#!/usr/bin/env python3
"""
KitsuneFetch
PDB Protein Query Tool - GraphQL Version
Retrieves structural information from RCSB PDB database using GraphQL API.
Reads configuration from DATA/ folder.
"""

import requests
import json
import csv
import sys
import time
import os
import re
from datetime import datetime
from typing import Optional, Tuple
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import numpy as np

# Version
VERSION = "v1.0.2"

# API endpoints
SEARCH_API = "https://search.rcsb.org/rcsbsearch/v2/query"
GRAPHQL_API = "https://data.rcsb.org/graphql"

# Rate limiting settings
REQUEST_DELAY = 0.5
DEFAULT_BATCH_SIZE = 5
BATCH_DELAY = 1.5
MAX_RETRIES = 3
RETRY_DELAY = 3.0

# Path to DATA folder
import importlib.resources
DATA_DIR = os.path.join(os.path.dirname(__file__), "DATA")

# GraphQL query
GRAPHQL_QUERY = """
query ($ids: [String!]!) {
  entries(entry_ids: $ids) {
    rcsb_id
    struct { title }
    rcsb_accession_info { initial_release_date }
    rcsb_primary_citation {
      pdbx_database_id_DOI
      pdbx_database_id_PubMed
      rcsb_journal_abbrev
      title
    }
    rcsb_entry_info {
      molecular_weight
      deposited_polymer_entity_instance_count
      deposited_unmodeled_polymer_monomer_count
    }
    exptl { method }
    polymer_entities {
      rcsb_polymer_entity { pdbx_mutation }
      rcsb_entity_source_organism { scientific_name }
    }
    nonpolymer_entities { pdbx_entity_nonpoly { comp_id } }
    assemblies {
      rcsb_assembly_info { polymer_entity_instance_count }
      pdbx_struct_assembly { oligomeric_details }
    }
  }
}
"""


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format."""
    if seconds < 60:
        return f"{seconds:.2f} seconds"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes} min {secs:.2f} sec"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours}h {minutes}min {secs:.2f}sec"


def log_command(args: list, output_dir: str, start_time: float = None, end_time: float = None):
    """Log the command line and execution time to KitsuneFetch.log in the output directory"""
    log_file = os.path.join(output_dir, "KitsuneFetch.log")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    command = " ".join(args)
    
    log_entry = f"🦊 KitsuneFetch {VERSION}\n"
    log_entry += f"{'='*50}\n"
    log_entry += f"Timestamp: {timestamp}\n"
    log_entry += f"Command: {command}\n"
    
    if start_time is not None and end_time is not None:
        duration = end_time - start_time
        log_entry += f"{'='*50}\n"
        log_entry += f"Execution time: {format_duration(duration)}\n"
        log_entry += f"  (Raw: {duration:.4f} seconds)\n"
    
    log_entry += f"{'='*50}\n"
    
    try:
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(log_entry)
        print(f"  -> KitsuneFetch.log")
    except Exception as e:
        print(f"Warning: Could not write to log file: {e}")


def capitalize_title(text: str) -> str:
    """Capitalize first letter, lowercase the rest."""
    if not text or text == "NA":
        return text
    return text[0].upper() + text[1:].lower() if len(text) > 1 else text.upper()


def format_species_name(species: str) -> str:
    """Format species name with first letter uppercase, rest lowercase."""
    if not species or species == "NA":
        return species
    parts = [s.strip() for s in species.split(";")]
    formatted = []
    for part in parts:
        if part:
            formatted.append(part[0].upper() + part[1:].lower() if len(part) > 1 else part.upper())
    return "; ".join(formatted)


def load_species_mappings() -> dict:
    mapping_file = os.path.join(DATA_DIR, "SPECIES_MAPPINGS.txt")
    mappings = {}
    try:
        with open(mapping_file, 'r', encoding='utf-8') as f:
            content = f.read()
            pattern = r'"([^"]+)"\s*:\s*"([^"]+)"'
            matches = re.findall(pattern, content)
            for key, value in matches:
                mappings[key.lower().strip()] = value.strip()
        print(f"Loaded {len(mappings)} species mappings from {mapping_file}")
    except FileNotFoundError:
        print(f"Warning: {mapping_file} not found. Using default mappings.")
        mappings = {"human": "Homo sapiens", "mouse": "Mus musculus", "yeast": "Saccharomyces cerevisiae", "ecoli": "Escherichia coli", "e. coli": "Escherichia coli"}
    except Exception as e:
        print(f"Error loading species mappings: {e}. Using defaults.")
        mappings = {"human": "Homo sapiens"}
    return mappings


def get_species_name(species: str) -> str:
    if not species:
        return None
    species_lower = species.lower().strip()
    if species_lower in SPECIES_MAPPINGS:
        return SPECIES_MAPPINGS[species_lower]
    return species


def load_skip_ligands() -> set:
    skip_file = os.path.join(DATA_DIR, "SKIP_LIGANDS.txt")
    ligands = set()
    try:
        with open(skip_file, 'r', encoding='utf-8') as f:
            content = f.read()
            matches = re.findall(r'"([^"]+)"', content)
            ligands = {m.strip().upper() for m in matches if m.strip()}
        print(f"Loaded {len(ligands)} skip ligands from {skip_file}")
    except FileNotFoundError:
        print(f"Warning: {skip_file} not found. Using default skip ligands.")
        ligands = {"HOH", "WAT", "DOD", "H2O", "D2O", "SO4", "PO4", "CL", "NA", "K", "MG", "CA", "ZN", "FE",
                   "GOL", "EDO", "PEG", "MPD", "DMS", "ACT", "FMT", "TRS", "BME", "DTT", "MES", "EPE",
                   "PG4", "PE4", "1PE", "2PE", "P6G", "NO3", "SCN", "BR", "IOD", "F", "NH4", "CIT", "TAR"}
    return ligands


def load_protein_mappings() -> dict:
    mapping_file = os.path.join(DATA_DIR, "PROTEIN_NAME_MAPPINGS.txt")
    mappings = {}
    try:
        with open(mapping_file, 'r', encoding='utf-8') as f:
            content = f.read()
            pattern = r'"([^"]+)"\s*:\s*\[([^\]]+)\]'
            matches = re.findall(pattern, content)
            for key, values_str in matches:
                values = re.findall(r'"([^"]+)"', values_str)
                if values:
                    mappings[key.lower().strip()] = [v.strip() for v in values]
        print(f"Loaded {len(mappings)} protein mappings from {mapping_file}")
    except FileNotFoundError:
        print(f"Warning: {mapping_file} not found. Using default mappings.")
        mappings = {"hsp90": ["Heat shock protein 90", "HSP90AA1", "HSP90AB1"], "hsp70": ["Heat shock protein 70", "HSPA1A", "HSPA8"],
                    "p53": ["Tumor protein p53", "TP53"], "ubiquitin": ["Ubiquitin", "Polyubiquitin", "UBB", "UBC"]}
    return mappings


print("Loading configuration files...")
SPECIES_MAPPINGS = load_species_mappings()
SKIP_LIGANDS = load_skip_ligands()
PROTEIN_NAME_MAPPINGS = load_protein_mappings()
print()


def get_search_terms(protein_name: str) -> list:
    terms = [protein_name]
    key = protein_name.lower().strip()
    if key in PROTEIN_NAME_MAPPINGS:
        terms.extend(PROTEIN_NAME_MAPPINGS[key])
    return terms


def safe_request(url: str, method: str = "get", json_data: dict = None, timeout: int = 30) -> Optional[requests.Response]:
    for attempt in range(MAX_RETRIES):
        try:
            time.sleep(REQUEST_DELAY)
            if method == "post":
                response = requests.post(url, json=json_data, timeout=timeout)
            else:
                response = requests.get(url, timeout=timeout)
            if response.status_code == 429:
                wait_time = RETRY_DELAY * (attempt + 2)
                print(f"    Rate limited (429). Waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
            if response.status_code >= 400:
                print(f"    HTTP Error {response.status_code}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                return None
            return response
        except requests.exceptions.Timeout:
            if attempt < MAX_RETRIES - 1:
                print(f"    Timeout, retry {attempt + 1}/{MAX_RETRIES}...")
                time.sleep(RETRY_DELAY)
            else:
                return None
        except requests.exceptions.RequestException as e:
            if attempt < MAX_RETRIES - 1:
                print(f"    Error: {type(e).__name__}, retry {attempt + 1}/{MAX_RETRIES}...")
                time.sleep(RETRY_DELAY)
            else:
                return None
    return None


def parse_date_range(date_range: str) -> Tuple[Optional[str], Optional[str]]:
    if not date_range:
        return None, None
    date_range = date_range.strip()
    if '-' in date_range:
        parts = date_range.split('-', 1)
        start = parts[0].strip() if parts[0].strip() else None
        end = parts[1].strip() if len(parts) > 1 and parts[1].strip() else None
        return start, end
    return date_range, date_range


def search_pdb(protein_name: str, species: Optional[str] = None,
               date_start: Optional[str] = None, date_end: Optional[str] = None) -> list:
    search_terms = get_search_terms(protein_name)
    all_pdb_ids = set()
    scientific_species = get_species_name(species) if species else None
    
    for term in search_terms:
        query_nodes = [{"type": "terminal", "service": "text", "parameters": {"attribute": "struct.title", "operator": "contains_phrase", "value": term}}]
        if scientific_species:
            query_nodes.append({"type": "terminal", "service": "text", "parameters": {"attribute": "rcsb_entity_source_organism.scientific_name", "operator": "exact_match", "value": scientific_species}})
        if date_start or date_end:
            query_nodes.append({"type": "terminal", "service": "text", "parameters": {"attribute": "rcsb_accession_info.initial_release_date", "operator": "range",
                "value": {"from": f"{date_start}-01-01" if date_start else "1900-01-01", "to": f"{date_end}-12-31" if date_end else "2099-12-31", "include_lower": True, "include_upper": True}}})
        query = {"type": "group", "logical_operator": "and", "nodes": query_nodes} if len(query_nodes) > 1 else query_nodes[0]
        request_body = {"query": query, "return_type": "entry", "request_options": {"paginate": {"start": 0, "rows": 1000}, "results_content_type": ["experimental"]}}
        response = safe_request(SEARCH_API, method="post", json_data=request_body)
        if response and response.text.strip():
            try:
                data = response.json()
                ids = [hit["identifier"] for hit in data.get("result_set", [])]
                all_pdb_ids.update(ids)
            except (json.JSONDecodeError, ValueError):
                print(f"    Warning: Could not parse response for term '{term}'")
    
    print(f"Search terms used: {search_terms}")
    if scientific_species and scientific_species != species:
        print(f"Species '{species}' converted to '{scientific_species}'")
    return list(all_pdb_ids)


def fetch_entries_graphql(pdb_ids: list, batch_size: int = DEFAULT_BATCH_SIZE) -> list:
    all_entries = []
    total = len(pdb_ids)
    failed_batches = 0
    
    for i in range(0, total, batch_size):
        batch = pdb_ids[i:i + batch_size]
        batch_num = i // batch_size + 1
        total_batches = (total + batch_size - 1) // batch_size
        print(f"  Fetching batch {batch_num}/{total_batches} ({len(batch)} structures)...")
        
        response = safe_request(GRAPHQL_API, method="post", json_data={"query": GRAPHQL_QUERY, "variables": {"ids": batch}}, timeout=60)
        if response:
            try:
                data = response.json()
                if data is None:
                    print(f"    Warning: Empty response for batch {batch_num}")
                    failed_batches += 1
                    continue
                if "errors" in data:
                    err_msg = data["errors"][0].get("message", "Unknown error") if data["errors"] else "Unknown"
                    print(f"    Warning: GraphQL error: {err_msg[:100]}")
                    failed_batches += 1
                entries = data.get("data")
                if entries:
                    entry_list = entries.get("entries", [])
                    if entry_list:
                        valid_entries = [e for e in entry_list if e is not None]
                        all_entries.extend(valid_entries)
            except json.JSONDecodeError as e:
                print(f"    Warning: JSON decode error in batch {batch_num}: {e}")
                failed_batches += 1
        else:
            print(f"    Warning: No response for batch {batch_num}")
            failed_batches += 1
        if i + batch_size < total:
            time.sleep(BATCH_DELAY)
    
    if failed_batches > 0:
        print(f"\n  Note: {failed_batches} batch(es) had issues.")
    return all_entries


def detect_mutation_in_title(title: str) -> bool:
    if not title or title == "NA":
        return False
    title_lower = title.lower()
    mutation_keywords = ["mutant", "mutation", "mutations", "mutated", "mutagenesis", "variant", "substitution", "replacement",
                         "point mutation", "single mutation", "double mutation", "triple mutation", "deletion", "truncat", "insert"]
    if any(kw in title_lower for kw in mutation_keywords):
        return True
    if re.search(r'\b[A-Z]\d+[A-Z]\b', title):
        return True
    if re.search(r'\([A-Z]\d+[A-Z]', title):
        return True
    return False


def parse_entry(entry: dict) -> dict:
    pdb_id = entry.get("rcsb_id", "NA")
    title = "NA"
    struct = entry.get("struct")
    if struct and struct.get("title"):
        title = capitalize_title(struct["title"])
    
    release_date = "NA"
    acc_info = entry.get("rcsb_accession_info")
    if acc_info and acc_info.get("initial_release_date"):
        release_date = acc_info["initial_release_date"][:10]
    
    doi = "NA"
    citation = entry.get("rcsb_primary_citation")
    if citation:
        journal = citation.get("rcsb_journal_abbrev") or ""
        cit_title = citation.get("title") or ""
        unpublished = ["to be published", "tobepublished", "in preparation", "in press", "submitted", "unpublished"]
        is_unpublished = any(ind in journal.lower() or ind in cit_title.lower() for ind in unpublished)
        if not is_unpublished and journal.strip():
            if citation.get("pdbx_database_id_DOI"):
                doi = citation["pdbx_database_id_DOI"]
            elif citation.get("pdbx_database_id_PubMed"):
                doi = f"PMID:{citation['pdbx_database_id_PubMed']}"
    
    exp_method = "NA"
    exptl = entry.get("exptl") or []
    if exptl:
        methods = [e.get("method") for e in exptl if e and e.get("method")]
        exp_method = "; ".join(methods) if methods else "NA"
    
    mol_weight = "NA"
    entry_info = entry.get("rcsb_entry_info")
    if entry_info:
        weight = entry_info.get("molecular_weight")
        if weight:
            mol_weight = f"{weight:.2f} kDa"
    
    species_set = set()
    has_mutation = "No"
    polymer_entities = entry.get("polymer_entities") or []
    for pe in polymer_entities:
        if pe is None:
            continue
        organisms = pe.get("rcsb_entity_source_organism") or []
        for org in organisms:
            if org:
                name = org.get("scientific_name")
                if name:
                    species_set.add(name)
        if has_mutation == "No":
            rcsb_pe = pe.get("rcsb_polymer_entity")
            if rcsb_pe:
                mutation = rcsb_pe.get("pdbx_mutation")
                if mutation and str(mutation).strip().lower() not in ["", "none", "null", "?", "n/a", "wild type", "wild-type", "wt"]:
                    has_mutation = "Yes"
    species_formatted = [s[0].upper() + s[1:].lower() if len(s) > 1 else s.upper() for s in sorted(species_set)]
    species = "; ".join(species_formatted) if species_formatted else "NA"
    
    missing_residues = 0
    entry_info = entry.get("rcsb_entry_info")
    if entry_info:
        unmodeled = entry_info.get("deposited_unmodeled_polymer_monomer_count")
        if unmodeled:
            missing_residues = unmodeled
    
    if has_mutation == "No":
        if detect_mutation_in_title(title):
            has_mutation = "Yes (title)"
    
    oligo_state = "NA"
    assemblies = entry.get("assemblies") or []
    if assemblies:
        first_assembly = assemblies[0]
        if first_assembly:
            pdbx_assembly = first_assembly.get("pdbx_struct_assembly")
            if pdbx_assembly:
                oligo_details = pdbx_assembly.get("oligomeric_details")
                if oligo_details:
                    oligo_details_lower = oligo_details.lower()
                    match = re.search(r'(\d+)-mer', oligo_details_lower)
                    if match:
                        oligo_state = match.group(1)
                    elif "monomer" in oligo_details_lower:
                        oligo_state = "1"
                    elif "dimer" in oligo_details_lower:
                        oligo_state = "2"
                    elif "trimer" in oligo_details_lower:
                        oligo_state = "3"
                    elif "tetramer" in oligo_details_lower:
                        oligo_state = "4"
                    elif "pentamer" in oligo_details_lower:
                        oligo_state = "5"
                    elif "hexamer" in oligo_details_lower:
                        oligo_state = "6"
                    elif "heptamer" in oligo_details_lower:
                        oligo_state = "7"
                    elif "octamer" in oligo_details_lower:
                        oligo_state = "8"
                    elif "nonamer" in oligo_details_lower:
                        oligo_state = "9"
                    elif "decamer" in oligo_details_lower:
                        oligo_state = "10"
                    elif "dodecamer" in oligo_details_lower:
                        oligo_state = "12"
            if oligo_state == "NA":
                assembly_info = first_assembly.get("rcsb_assembly_info")
                if assembly_info:
                    count = assembly_info.get("polymer_entity_instance_count")
                    if count:
                        oligo_state = str(count)
    if oligo_state == "NA" and not assemblies:
        entry_info = entry.get("rcsb_entry_info")
        if entry_info:
            count = entry_info.get("deposited_polymer_entity_instance_count")
            if count:
                oligo_state = str(count)
    
    ligands = []
    has_ligand = False
    nonpolymer_entities = entry.get("nonpolymer_entities") or []
    for npe in nonpolymer_entities:
        if npe is None:
            continue
        entity_nonpoly = npe.get("pdbx_entity_nonpoly")
        if entity_nonpoly:
            comp_id = entity_nonpoly.get("comp_id")
            if comp_id:
                if comp_id.upper() not in SKIP_LIGANDS:
                    has_ligand = True
                    if comp_id not in ligands:
                        ligands.append(comp_id)
    ligands_str = "; ".join(ligands) if ligands else ("Yes" if has_ligand else "No")
    
    return {"PDB_Code": pdb_id, "Title": title, "DOI": doi, "Release_Date": release_date, "Species": species,
            "Mutation": has_mutation, "Exp_Technique": exp_method, "Oligomeric_State": oligo_state,
            "Mol_Weight": mol_weight, "Missing_Residues": missing_residues, "Ligands": ligands_str}


def is_complex_with_other_proteins(title: str, protein_name: str) -> bool:
    if not title or title == "NA":
        return False
    title_lower = title.lower()
    complex_keywords = ["complex", "bound to", "in complex with", "associated with", "interacting with"]
    return any(kw in title_lower for kw in complex_keywords)


def title_contains_partner(title: str, partner_name: str) -> bool:
    if not title or title == "NA" or not partner_name:
        return False
    return partner_name.lower() in title.lower()


def filter_by_technique(exp_technique: str, technique_filter: str) -> bool:
    if not exp_technique or exp_technique == "NA":
        return False
    exp_lower = exp_technique.lower()
    if technique_filter == "xray":
        return "x-ray" in exp_lower or "xray" in exp_lower or "diffraction" in exp_lower
    elif technique_filter == "nmr":
        return "nmr" in exp_lower or "nuclear magnetic" in exp_lower
    elif technique_filter == "em":
        return "microscopy" in exp_lower or "electron" in exp_lower or "cryo" in exp_lower
    elif technique_filter == "other":
        is_xray = "x-ray" in exp_lower or "xray" in exp_lower or "diffraction" in exp_lower
        is_nmr = "nmr" in exp_lower or "nuclear magnetic" in exp_lower
        is_em = "microscopy" in exp_lower or "electron" in exp_lower or "cryo" in exp_lower
        return not (is_xray or is_nmr or is_em)
    return True


def is_integrative_structure(exp_technique: str, title: str = "") -> bool:
    exp_lower = (exp_technique or "").lower()
    title_lower = (title or "").lower()
    integrative_keywords = ["integrative", "hybrid model", "multi-method", "theoretical model", "computational model",
                            "deep learning", "machine learning", "alphafold", "predicted structure", "predicted model"]
    modeling_patterns = ["modeled structure", "modelled structure", "modeled by", "modelled by",
                         "modeling of", "modelling of", "computational modeling", "computational modelling"]
    if exp_technique and exp_technique != "NA":
        if any(kw in exp_lower for kw in integrative_keywords):
            return True
        if any(mp in exp_lower for mp in modeling_patterns):
            return True
    if title and title != "NA":
        if any(kw in title_lower for kw in integrative_keywords):
            return True
        if any(mp in title_lower for mp in modeling_patterns):
            return True
    return False


def download_pdb_structures(pdb_ids: list, output_dir: str) -> int:
    """Download PDB structure files."""
    pdb_dir = os.path.join(output_dir, "PDB")
    os.makedirs(pdb_dir, exist_ok=True)
    
    print(f"\nDownloading {len(pdb_ids)} PDB structures...")
    downloaded = 0
    failed = []
    
    for i, pdb_id in enumerate(pdb_ids, 1):
        pdb_id_lower = pdb_id.lower()
        
        if i % 10 == 0 or i == len(pdb_ids):
            print(f"  Progress: {i}/{len(pdb_ids)} ({downloaded} downloaded)")
        
        url_cif = f"https://files.rcsb.org/download/{pdb_id_lower}.cif"
        response_cif = safe_request(url_cif, method="get", timeout=30)
        if response_cif and response_cif.status_code == 200:
            output_file_cif = os.path.join(pdb_dir, f"{pdb_id}.cif")
            with open(output_file_cif, 'w', encoding='utf-8') as f:
                f.write(response_cif.text)
            downloaded += 1
            continue
        
        url_pdb = f"https://files.rcsb.org/download/{pdb_id_lower}.pdb"
        response_pdb = safe_request(url_pdb, method="get", timeout=30)
        if response_pdb and response_pdb.status_code == 200:
            output_file_pdb = os.path.join(pdb_dir, f"{pdb_id}.pdb")
            with open(output_file_pdb, 'w', encoding='utf-8') as f:
                f.write(response_pdb.text)
            downloaded += 1
            continue
        
        failed.append(pdb_id)
    
    print(f"  Downloaded: {downloaded}/{len(pdb_ids)} structures")
    if failed:
        print(f"  Failed: {len(failed)} - {', '.join(failed[:10])}{'...' if len(failed) > 10 else ''}")
    print(f"  -> PDB/")
    
    return downloaded


def apply_filters(results: list, protein_name: str, no_complex: bool = False,
                  only_complex: bool = False, complex_partner: str = None,
                  no_mutation: bool = False, oligomeric_state: str = None,
                  technique: str = None, no_ligand: bool = False,
                  with_ligand: str = None, no_integrative: bool = False,
                  max_missing: int = None) -> Tuple[list, list]:
    kept = []
    filtered = []
    
    for r in results:
        title = r.get("Title", "")
        dominated = False
        
        if no_complex and not dominated:
            if is_complex_with_other_proteins(title, protein_name):
                dominated = True
                r["Filter_Reason"] = "complex"
        
        if only_complex and not dominated:
            if not is_complex_with_other_proteins(title, protein_name):
                dominated = True
                r["Filter_Reason"] = "not complex"
        
        if complex_partner and not dominated:
            if not title_contains_partner(title, complex_partner):
                dominated = True
                r["Filter_Reason"] = f"no partner {complex_partner}"
        
        if no_mutation and not dominated:
            mutation_value = r.get("Mutation", "")
            if mutation_value == "Yes" or mutation_value == "Yes (title)":
                dominated = True
                r["Filter_Reason"] = "mutation"
        
        if oligomeric_state and not dominated:
            if r.get("Oligomeric_State") != oligomeric_state:
                dominated = True
                r["Filter_Reason"] = f"oligomer != {oligomeric_state}"
        
        if technique and not dominated:
            if not filter_by_technique(r.get("Exp_Technique", ""), technique):
                dominated = True
                r["Filter_Reason"] = f"technique != {technique}"
        
        if no_ligand and not dominated:
            ligands_value = r.get("Ligands", "")
            if ligands_value != "No":
                dominated = True
                r["Filter_Reason"] = "has ligand"
        
        if with_ligand and not dominated:
            ligands_value = r.get("Ligands", "").upper()
            if with_ligand.upper() not in ligands_value:
                dominated = True
                r["Filter_Reason"] = f"no ligand {with_ligand}"
        
        if no_integrative and not dominated:
            if is_integrative_structure(r.get("Exp_Technique", ""), r.get("Title", "")):
                dominated = True
                r["Filter_Reason"] = "integrative"
        
        if max_missing is not None and not dominated:
            missing = r.get("Missing_Residues", 0)
            if missing > max_missing:
                dominated = True
                r["Filter_Reason"] = f"missing residues ({missing}) > {max_missing}"
        
        if dominated:
            filtered.append(r)
        else:
            kept.append(r)
    
    return kept, filtered


def sort_by_release_date(results: list) -> list:
    """Sort results by release date (reverse chronological order, most recent first)."""
    def get_date_key(r):
        date_str = r.get("Release_Date", "NA")
        if date_str == "NA" or not date_str:
            return "0000-00-00"
        return date_str
    return sorted(results, key=get_date_key, reverse=True)


def create_output_directory(protein_name: str, species: Optional[str]) -> str:
    now = datetime.now()
    parts = [protein_name]
    if species:
        parts.append(species)
    parts.extend([now.strftime("%d-%m-%Y"), now.strftime("%H-%M-%S")])
    dir_name = "_".join(parts)
    dir_name = "".join(c if c.isalnum() or c in ['_', '-'] else '_' for c in dir_name)
    os.makedirs(dir_name, exist_ok=True)
    print(f"\nCreated output directory: {dir_name}/")
    return dir_name


def generate_statistics(results: list, protein_name: str, species: Optional[str],
                        date_start: Optional[str], date_end: Optional[str], output_dir: str,
                        technique_filter: str = None, oligomer_filter: str = None,
                        no_ligand: bool = False, with_ligand: str = None):
    total = len(results)
    if total == 0:
        return
    stats_file = os.path.join(output_dir, "statistics.txt")
    oligo_counts, species_counts, technique_counts, ligand_counts = {}, {}, {}, {}
    for r in results:
        state = r["Oligomeric_State"] if r["Oligomeric_State"] != "NA" else "Unknown"
        oligo_counts[state] = oligo_counts.get(state, 0) + 1
        if not species:
            sp = r["Species"] if r["Species"] != "NA" else "Unknown"
            for s in [x.strip() for x in sp.split(";") if x.strip()]:
                species_counts[s] = species_counts.get(s, 0) + 1
        tech = r["Exp_Technique"] if r["Exp_Technique"] != "NA" else "Unknown"
        technique_counts[tech] = technique_counts.get(tech, 0) + 1
        lig = r["Ligands"]
        if lig == "No":
            ligand_counts["None"] = ligand_counts.get("None", 0) + 1
        else:
            for l in [x.strip() for x in lig.split(";") if x.strip()]:
                ligand_counts[l] = ligand_counts.get(l, 0) + 1
    
    with open(stats_file, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n🦊 KitsuneFetch 🦊")
        f.write("\nFetch me if you can !\n" + "=" * 60 + "\n\n")
        f.write("=" * 60 + "\nPDB QUERY STATISTICS\n" + "=" * 60 + "\n\n")
        f.write("QUERY INFORMATION\n" + "-" * 40 + "\n")
        f.write(f"Protein name: {protein_name}\n")
        f.write(f"Species filter: {species if species else 'Not specified'}\n")
        f.write(f"Date range: {date_start or 'any'} to {date_end or 'any'}\n")
        f.write(f"Total unique structures: {total}\n\n")
        
        f.write("OLIGOMERIC STATE DISTRIBUTION\n" + "-" * 40 + "\n")
        if oligomer_filter:
            f.write(f"Filter applied: oligomer={oligomer_filter}\n")
        for state, count in sorted(oligo_counts.items(), key=lambda x: (0, int(x[0])) if x[0].isdigit() else (1, x[0])):
            label = f"{state}-mer" if state != "Unknown" else state
            f.write(f"{label}: {count} ({count/total*100:.1f}%)\n")
        f.write("\n")
        
        if not species and species_counts:
            f.write("SPECIES DISTRIBUTION\n" + "-" * 40 + "\n")
            for sp, count in sorted(species_counts.items(), key=lambda x: -x[1]):
                f.write(f"{sp}: {count} ({count/total*100:.1f}%)\n")
            f.write("\n")
        
        f.write("EXPERIMENTAL TECHNIQUES\n" + "-" * 40 + "\n")
        if technique_filter:
            f.write(f"Filter applied: technique={technique_filter}\n")
        for tech, count in sorted(technique_counts.items(), key=lambda x: -x[1]):
            f.write(f"{tech}: {count} ({count/total*100:.1f}%)\n")
        f.write("\n")
        
        f.write("LIGAND DISTRIBUTION\n" + "-" * 40 + "\n")
        if no_ligand:
            f.write(f"Filter applied: no-ligand (apo structures only)\n")
        elif with_ligand:
            f.write(f"Filter applied: ligand={with_ligand}\n")
        without = ligand_counts.get("None", 0)
        f.write(f"With ligand(s): {total - without} ({(total - without)/total*100:.1f}%)\n")
        f.write(f"Without ligand: {without} ({without/total*100:.1f}%)\n\nBreakdown:\n")
        for lig, count in sorted(ligand_counts.items(), key=lambda x: -x[1]):
            f.write(f"  {lig}: {count} ({count/total*100:.1f}%)\n")
        f.write("\n" + "=" * 60 + "\n")
    print(f"  -> statistics.txt")
    generate_pie_charts(oligo_counts, species_counts, technique_counts, ligand_counts, total, species, output_dir,
                        technique_filter, oligomer_filter, no_ligand, with_ligand)


def generate_pie_charts(oligo_counts, species_counts, technique_counts, ligand_counts, total, species_filter, output_dir,
                        technique_filter=None, oligomer_filter=None, no_ligand=False, with_ligand=None):
    fig, axes = plt.subplots(2, 2, figsize=(16, 14))
    fig.suptitle('PDB Query Statistics', fontsize=18, fontweight='bold', y=0.98)
    colors = plt.cm.Set3.colors
    
    def make_pie(ax, data, title, filter_msg=None, max_items=8):
        if filter_msg:
            ax.text(0.5, 0.5, f'Filter applied:\n{filter_msg}', ha='center', va='center', fontsize=12,
                    bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
            ax.set_title(title, fontweight='bold', fontsize=12)
            ax.axis('off')
            return
        if not data:
            ax.text(0.5, 0.5, 'No data', ha='center', va='center', fontsize=12)
            ax.set_title(title, fontweight='bold', fontsize=12)
            ax.axis('off')
            return
        sorted_data = sorted(data.items(), key=lambda x: -x[1])
        if len(sorted_data) > max_items:
            top_data = dict(sorted_data[:max_items-1])
            top_data["Others"] = sum(c for _, c in sorted_data[max_items-1:])
        else:
            top_data = dict(sorted_data)
        labels = list(top_data.keys())
        sizes = list(top_data.values())
        wedges, texts, autotexts = ax.pie(sizes, autopct=lambda pct: f'{pct:.1f}%' if pct > 5 else '', colors=colors[:len(sizes)], startangle=90, pctdistance=0.75)
        for autotext in autotexts:
            autotext.set_fontsize(9)
            autotext.set_fontweight('bold')
        legend_labels = [f'{l} ({top_data[l]})' for l in labels]
        ax.legend(wedges, legend_labels, title="Categories", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), fontsize=9)
        ax.set_title(title, fontweight='bold', fontsize=12, pad=10)
    
    oligo_labels = {(f"{k}-mer" if k != "Unknown" else k): v for k, v in oligo_counts.items()}
    oligo_filter_msg = f"oligomer={oligomer_filter}" if oligomer_filter else None
    make_pie(axes[0, 0], oligo_labels, 'Oligomeric State Distribution', oligo_filter_msg)
    
    tech_labels = {k.replace('DIFFRACTION', 'DIFF.').replace('MICROSCOPY', 'MICRO.').replace('SOLUTION ', ''): v for k, v in technique_counts.items()}
    tech_filter_msg = f"technique={technique_filter}" if technique_filter else None
    make_pie(axes[0, 1], tech_labels, 'Experimental Techniques', tech_filter_msg)
    
    if not species_filter and species_counts:
        make_pie(axes[1, 0], species_counts, 'Species Distribution')
    else:
        axes[1, 0].text(0.5, 0.5, f'Filter applied:\nspecies={species_filter}', ha='center', va='center', fontsize=12,
                        bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
        axes[1, 0].set_title('Species Distribution', fontweight='bold', fontsize=12)
        axes[1, 0].axis('off')
    
    ligand_filter_msg = None
    if no_ligand:
        ligand_filter_msg = "no-ligand (apo only)"
    elif with_ligand:
        ligand_filter_msg = f"ligand={with_ligand}"
    make_pie(axes[1, 1], ligand_counts, 'Ligand Distribution', ligand_filter_msg, max_items=10)
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    fig_path = os.path.join(output_dir, "statistics_figures.png")
    plt.savefig(fig_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  -> statistics_figures.png")


def query_protein(protein_name: str, species: Optional[str] = None, date_start: Optional[str] = None,
                  date_end: Optional[str] = None, no_complex: bool = False, only_complex: bool = False,
                  complex_partner: str = None, no_mutation: bool = False,
                  oligomeric_state: str = None, technique: str = None, no_ligand: bool = False,
                  with_ligand: str = None, no_integrative: bool = False, max_missing: int = None,
                  download_pdb: bool = False, batch_size: int = DEFAULT_BATCH_SIZE):
    
    # Start timing
    start_time = time.time()
    
    print(f"\n{'='*60}")
    print(f"🦊 KitsuneFetch {VERSION} : PDB QUERY TOOL")
    print(f"{'='*60}")
    print(f"Protein: {protein_name}")
    if species:
        print(f"Species: {species}")
    if date_start or date_end:
        print(f"Date range: {date_start or 'any'} to {date_end or 'any'}")
    
    filters_active = []
    if no_complex:
        filters_active.append("no-complex")
    if only_complex:
        filters_active.append("only-complex")
    if complex_partner:
        filters_active.append(f"complex-with={complex_partner}")
    if no_mutation:
        filters_active.append("no-mutation")
    if oligomeric_state:
        filters_active.append(f"oligomer={oligomeric_state}")
    if technique:
        filters_active.append(f"technique={technique}")
    if no_ligand:
        filters_active.append("no-ligand")
    if with_ligand:
        filters_active.append(f"ligand={with_ligand}")
    if no_integrative:
        filters_active.append("no-integrative")
    if max_missing is not None:
        filters_active.append(f"max-missing={max_missing}")
    if filters_active:
        print(f"Filters: {', '.join(filters_active)}")
    if download_pdb:
        print(f"Download: PDB files")
    if batch_size != DEFAULT_BATCH_SIZE:
        print(f"Batch size: {batch_size}")
    
    print(f"{'='*60}\n")
    
    print("Searching PDB database...")
    pdb_ids = search_pdb(protein_name, species, date_start, date_end)
    
    if not pdb_ids:
        print(f"\nNo structures found for your request.")
        end_time = time.time()
        print(f"\nExecution time: {format_duration(end_time - start_time)}")
        return
    
    print(f"\nFound {len(pdb_ids)} structures. Fetching details via GraphQL...\n")
    entries = fetch_entries_graphql(pdb_ids, batch_size)
    
    if not entries:
        print("Failed to retrieve data.")
        end_time = time.time()
        print(f"\nExecution time: {format_duration(end_time - start_time)}")
        return
    
    print(f"\nParsing {len(entries)} entries...")
    results = [parse_entry(entry) for entry in entries if entry]
    
    if results:
        original_count = len(results)
        
        after_filter_count = original_count
        filtered_out = []
        if no_complex or only_complex or complex_partner or no_mutation or oligomeric_state or technique or no_ligand or with_ligand or no_integrative or max_missing is not None:
            results, filtered_out = apply_filters(results, protein_name, no_complex, only_complex, complex_partner,
                                                  no_mutation, oligomeric_state, technique, no_ligand, with_ligand, no_integrative, max_missing)
            after_filter_count = len(results)
            filtered_count = original_count - after_filter_count
            if filtered_count > 0:
                print(f"  Filtered out {filtered_count} entries based on options ({after_filter_count} remaining)")
        
        if not results:
            print(f"\nNo structures match your filter criteria.")
            end_time = time.time()
            print(f"\nExecution time: {format_duration(end_time - start_time)}")
            return
        
        results = sort_by_release_date(results)
        if filtered_out:
            filtered_out = sort_by_release_date(filtered_out)
        
        output_dir = create_output_directory(protein_name, species)
        
        csv_path = os.path.join(output_dir, "results.csv")
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys(), delimiter='\t')
            writer.writeheader()
            writer.writerows(results)
        print(f"  -> results.csv")
        
        if filtered_out:
            filtered_path = os.path.join(output_dir, "filtered_out.csv")
            fieldnames = list(results[0].keys()) + ["Filter_Reason"]
            with open(filtered_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
                writer.writeheader()
                writer.writerows(filtered_out)
            print(f"  -> filtered_out.csv ({len(filtered_out)} entries)")
        
        generate_statistics(results, protein_name, species, date_start, date_end, output_dir,
                            technique, oligomeric_state, no_ligand, with_ligand)
        
        if download_pdb:
            pdb_codes = [r["PDB_Code"] for r in results]
            download_pdb_structures(pdb_codes, output_dir)
        
        # End timing
        end_time = time.time()
        
        # Log command with timing info
        log_command(sys.argv, output_dir, start_time, end_time)
        
        print(f"\n{'='*60}")
        print("DONE!")
        print(f"  Fetched: {original_count} structures")
        if after_filter_count != original_count:
            print(f"  After filters: {after_filter_count} structures")
        print(f"  Final output: {len(results)} entries")
        print(f"  Execution time: {format_duration(end_time - start_time)}")
        print(f"Output directory: {output_dir}/")
        print(f"{'='*60}\n")
        print(f"\n")
        print(f" 🦊 KitsuneFetch 🦊    Fetch me if you can !")
    else:
        end_time = time.time()
        print("No data retrieved.")
        print(f"\nExecution time: {format_duration(end_time - start_time)}")
        print(f"\n")
        print(f" 🦊 KitsuneFetch 🦊    Fetch me if you can !")


def print_usage():
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                      KitsuneFetch {VERSION}                     ║
║              PDB PROTEIN QUERY TOOL (GraphQL)                ║
╚══════════════════════════════════════════════════════════════╝

            🦊 KitsuneFetch 🦊    Fetch me if you can !

DESCRIPTION:
    Query the RCSB Protein Data Bank for protein structures.
    Uses GraphQL API for efficient data retrieval.
    Generates csv data, statistics, and pie charts.

USAGE:
    python KitsuneFetch.py <protein_name> [species] [date_range] [options]

ARGUMENTS:
    protein_name  : Required. Protein name, nickname, or gene symbol.
    species       : Optional. Filter by organism (use 'None' to skip).
    date_range    : Optional. Filter by release date (use 'None' to skip).
                    Format: YYYY-YYYY  (e.g., 2000-2010)
                            YYYY-      (e.g., 2015- for 2015 onwards)
                            -YYYY      (e.g., -2010 for up to 2010)
                            YYYY       (e.g., 2020 for that year only)

OPTIONS (can be combined):
    --no-complex      : Exclude structures in complex with other proteins
    --only-complex    : Keep only structures in complex with other proteins
    --complex-with=X  : Keep only complexes with a specific partner (e.g., CDC37, p23)
    --no-mutation     : Exclude structures with mutations (wild-type only)
    --no-ligand       : Exclude structures with ligands (apo structures only)
    --ligand=X        : Keep only structures with a specific ligand (e.g., ADP, ATP)
    --no-integrative  : Exclude integrative/hybrid structures (multi-method)
    --max-missing=N   : Exclude structures with more than N missing residues
    --oligomer=N      : Keep only structures with specific oligomeric state
                        (1=monomer, 2=dimer, 3=trimer, 4=tetramer, etc.)
    --technique=X     : Filter by experimental technique:
                        xray  - X-ray diffraction (all types)
                        nmr   - NMR (solution, solid-state, etc.)
                        em    - Electron microscopy (cryo-EM, etc.)
                        other - Other techniques (neutron, fiber, etc.)
    --download-pdb    : Download PDB/mmCIF files for matching structures
    --batch-size=N    : Number of structures to fetch per batch (default: 5)
                        Higher values = faster but may cause rate limiting

EXAMPLES:
    python KitsuneFetch.py HSP90
    python KitsuneFetch.py HSP90 human
    python KitsuneFetch.py HSP90 human 2010-2020
    python KitsuneFetch.py HSP90 human None --no-complex
    python KitsuneFetch.py HSP90 human None --only-complex
    python KitsuneFetch.py HSP90 human None --complex-with=CDC37
    python KitsuneFetch.py HSP90 human None --no-mutation --oligomer=2
    python KitsuneFetch.py HSP90 None None --oligomer=1 --technique=nmr
    python KitsuneFetch.py HSP90 human None --no-ligand
    python KitsuneFetch.py HSP90 human None --ligand=ADP
    python KitsuneFetch.py HSP90 human None --max-missing=10
    python KitsuneFetch.py HSP90 human None --download-pdb
    python KitsuneFetch.py HSP90 human None --batch-size=20
    python KitsuneFetch.py p53 human None --no-complex --oligomer=4 --technique=xray

OUTPUT:
    Creates directory: <protein>_[species]_<dd-mm-yyyy>_<hh-mm-ss>/
        - KitsuneFetch.log        : Version, command, and execution time
        - results.csv             : Data table (sorted by date, most recent first)
        - filtered_out.csv        : Filtered structures (if any)
        - statistics.txt          : Summary statistics
        - statistics_figures.png  : Pie charts
        - PDB/                    : Downloaded structures (if --download-pdb)

CONFIGURATION:
    Place these files in DATA/ folder (next to the script):
        - SKIP_LIGANDS.txt        : Ligands to exclude
        - PROTEIN_NAME_MAPPINGS.txt : Protein name aliases
        - SPECIES_MAPPINGS.txt    : Species name mappings

REQUIREMENTS:
    pip install requests matplotlib numpy
""")


def main():
    if len(sys.argv) < 2 or sys.argv[1].lower() in ["-h", "--help", "help", "?"]:
        print_usage()
        sys.exit(0)
    
    protein_name = sys.argv[1]
    species = None
    date_range = None
    no_complex = False
    only_complex = False
    complex_partner = None
    no_mutation = False
    oligomeric_state = None
    technique = None
    no_ligand = False
    with_ligand = None
    no_integrative = False
    max_missing = None
    download_pdb = False
    batch_size = DEFAULT_BATCH_SIZE
    
    positional_args = []
    for arg in sys.argv[2:]:
        if arg.startswith("--"):
            if arg == "--no-complex":
                no_complex = True
            elif arg == "--only-complex":
                only_complex = True
            elif arg.startswith("--complex-with="):
                complex_partner = arg.split("=", 1)[1]
                only_complex = True
            elif arg == "--no-mutation":
                no_mutation = True
            elif arg == "--no-ligand":
                no_ligand = True
            elif arg.startswith("--ligand="):
                with_ligand = arg.split("=", 1)[1]
            elif arg == "--no-integrative":
                no_integrative = True
            elif arg.startswith("--max-missing="):
                try:
                    max_missing = int(arg.split("=", 1)[1])
                except ValueError:
                    print(f"Error: Invalid max-missing value. Must be a number.")
                    sys.exit(1)
            elif arg == "--download-pdb":
                download_pdb = True
            elif arg.startswith("--batch-size="):
                try:
                    batch_size = int(arg.split("=", 1)[1])
                    if batch_size < 1:
                        print(f"Error: Batch size must be at least 1.")
                        sys.exit(1)
                    if batch_size > 50:
                        print(f"Warning: Large batch sizes (>{50}) may cause rate limiting.")
                except ValueError:
                    print(f"Error: Invalid batch-size value. Must be a number.")
                    sys.exit(1)
            elif arg.startswith("--oligomer="):
                oligomeric_state = arg.split("=", 1)[1]
                if not oligomeric_state.isdigit():
                    print(f"Error: Invalid oligomer value '{oligomeric_state}'. Must be a number (1, 2, 3, etc.)")
                    sys.exit(1)
            elif arg.startswith("--technique="):
                technique = arg.split("=", 1)[1].lower()
                if technique not in ["xray", "nmr", "em", "other"]:
                    print(f"Error: Invalid technique '{technique}'. Use: xray, nmr, em, or other")
                    sys.exit(1)
            else:
                print(f"Warning: Unknown option '{arg}'")
        else:
            positional_args.append(arg)
    
    if no_complex and (only_complex or complex_partner):
        print("Error: Cannot use --no-complex with --only-complex or --complex-with")
        sys.exit(1)
    
    if no_ligand and with_ligand:
        print("Error: Cannot use --no-ligand with --ligand")
        sys.exit(1)
    
    if len(positional_args) > 0:
        species = positional_args[0]
    if len(positional_args) > 1:
        date_range = positional_args[1]
    
    if species and species.lower() in ["none", ""]:
        species = None
    if date_range and date_range.lower() in ["none", ""]:
        date_range = None
    
    date_start, date_end = parse_date_range(date_range)
    query_protein(protein_name, species, date_start, date_end, no_complex, only_complex,
                  complex_partner, no_mutation, oligomeric_state, technique, no_ligand,
                  with_ligand, no_integrative, max_missing, download_pdb, batch_size)


if __name__ == "__main__":
    main()