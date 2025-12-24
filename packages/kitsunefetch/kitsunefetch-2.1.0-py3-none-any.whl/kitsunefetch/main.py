#!/usr/bin/env python3
"""
KitsuneFetch v2.1.0 - OPTIMIZED VERSION
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import concurrent.futures
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

VERSION = "v2.1.0"

# Path to DATA folder
import importlib.resources
DATA_DIR = os.path.join(os.path.dirname(__file__), "DATA")

SEARCH_API = "https://search.rcsb.org/rcsbsearch/v2/query"
GRAPHQL_API = "https://data.rcsb.org/graphql"

REQUEST_DELAY = 0.1
DEFAULT_BATCH_SIZE = 50
MAX_RETRIES = 3
MAX_WORKERS_DOWNLOAD = 10
MAX_WORKERS_GRAPHQL = 3

DB_PDB, DB_ALPHAFOLD, DB_MODELARCHIVE, DB_ALL = "pdb", "alphafold", "modelarchive", "all"

def get_search_terms(protein_name: str) -> list:
    terms = [protein_name]
    key = protein_name.lower().strip()
    if key in PROTEIN_NAME_MAPPINGS:
        terms.extend(PROTEIN_NAME_MAPPINGS[key])
    return terms

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

GRAPHQL_QUERY_PDB = """
query ($ids: [String!]!) {
  entries(entry_ids: $ids) {
    rcsb_id
    struct { title }
    rcsb_accession_info { initial_release_date }
    rcsb_primary_citation { pdbx_database_id_DOI pdbx_database_id_PubMed }
    rcsb_entry_info { molecular_weight deposited_unmodeled_polymer_monomer_count }
    exptl { method }
    polymer_entities { rcsb_polymer_entity { pdbx_mutation } rcsb_entity_source_organism { scientific_name } }
    nonpolymer_entities { pdbx_entity_nonpoly { comp_id } }
    assemblies { rcsb_assembly_info { polymer_entity_instance_count } pdbx_struct_assembly { oligomeric_details } }
  }
}
"""

GRAPHQL_QUERY_CSM = """
query ($ids: [String!]!) {
  entries(entry_ids: $ids) {
    rcsb_id
    struct { title }
    rcsb_accession_info { initial_release_date }
    rcsb_entry_info { molecular_weight }
    polymer_entities { rcsb_entity_source_organism { scientific_name } }
    rcsb_ma_qa_metric_global { ma_qa_metric_global { type value } }
  }
}
"""

def create_session():
    session = requests.Session()
    retry = Retry(total=MAX_RETRIES, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry, pool_connections=20, pool_maxsize=20)
    session.mount("https://", adapter)
    return session

SESSION = create_session()

def format_duration(s):
    if s < 60: return f"{s:.2f}s"
    return f"{int(s // 60)}m {s % 60:.1f}s"

def safe_request(url, method="get", json_data=None, timeout=30):
    try:
        time.sleep(REQUEST_DELAY)
        resp = SESSION.post(url, json=json_data, timeout=timeout) if method == "post" else SESSION.get(url, timeout=timeout)
        resp.raise_for_status()
        return resp
    except:
        return None

def get_species_name(species):
    return SPECIES_MAPPINGS.get(species.lower().strip(), species) if species else None

def get_search_terms(protein_name):
    terms = [protein_name]
    if protein_name.lower() in PROTEIN_NAME_MAPPINGS:
        terms.extend(PROTEIN_NAME_MAPPINGS[protein_name.lower()])
    return terms

def capitalize_title(text):
    if not text or text == "NA": return text
    return text[0].upper() + text[1:].lower() if len(text) > 1 else text.upper()

def filter_by_source(struct_ids, database):
    if database == DB_ALL: return struct_ids
    elif database == DB_PDB: return [i for i in struct_ids if not i.startswith("AF_") and not i.startswith("MA_")]
    elif database == DB_ALPHAFOLD: return [i for i in struct_ids if i.startswith("AF_")]
    elif database == DB_MODELARCHIVE: return [i for i in struct_ids if i.startswith("MA_")]
    return struct_ids

def convert_rcsb_id_to_native(rcsb_id):
    if rcsb_id.startswith("AF_"):
        match = re.match(r'AF_AF([A-Z0-9]+)F(\d+)', rcsb_id)
        if not match:
            match = re.match(r'AF_([A-Z0-9]+)F(\d+)', rcsb_id)
        if match:
            uniprot, frag = match.group(1), match.group(2)
            return {"native_id": f"AF-{uniprot}-F{frag}", "source": "AlphaFold", 
                    "uniprot_id": uniprot, "url": f"https://alphafold.ebi.ac.uk/entry/{uniprot}"}
    
    elif rcsb_id.startswith("MA_"):
        inner = rcsb_id[5:] if rcsb_id.startswith("MA_MA") else rcsb_id[3:]
        
        known = [
            ("T3VR3", "t3vr3"),
            ("BAKCEPC", "bak-cepc"),
            ("COFFESLAC", "coffe-slac"),
            ("ASFVASFVG", "asfv-asfvg"),
            ("ORNLSPHDIV", "ornl-sphdiv"),
            ("JDVIRAL", "jd-viral"),
        ]
        
        for prefix, dataset in known:
            if inner.upper().startswith(prefix):
                num = inner[len(prefix):]
                if num.isdigit():
                    native = f"ma-{dataset}-{num}"
                    return {"native_id": native, "source": "ModelArchive",
                            "url": f"https://www.modelarchive.org/doi/10.5452/{native}"}
        
        match = re.match(r'^([A-Za-z]+)(\d+)$', inner)
        if match:
            dataset_raw, num = match.group(1).lower(), match.group(2)
            native = f"ma-{dataset_raw}-{num}"
            return {"native_id": rcsb_id, "source": "ModelArchive",
                    "url": f"https://www.rcsb.org/structure/{rcsb_id}"}
        
        return {"native_id": rcsb_id, "source": "PDB", "url": f"https://www.rcsb.org/structure/{rcsb_id}"}
    
    return {"native_id": rcsb_id, "source": "PDB", "url": f"https://www.rcsb.org/structure/{rcsb_id}"}

def search_database(protein_name, database=DB_ALL, species=None, date_start=None, date_end=None):
    all_ids = set()
    scientific_species = get_species_name(species)
    content_type = ["experimental", "computational"] if database in [DB_ALL, DB_ALPHAFOLD, DB_MODELARCHIVE] else ["experimental"]
    
    for term in get_search_terms(protein_name):
        nodes = [{"type": "terminal", "service": "text", 
                  "parameters": {"attribute": "struct.title", "operator": "contains_phrase", "value": term}}]
        if scientific_species:
            nodes.append({"type": "terminal", "service": "text", 
                         "parameters": {"attribute": "rcsb_entity_source_organism.scientific_name", 
                                       "operator": "exact_match", "value": scientific_species}})
        if date_start or date_end:
            nodes.append({"type": "terminal", "service": "text", 
                         "parameters": {"attribute": "rcsb_accession_info.initial_release_date", "operator": "range",
                                       "value": {"from": f"{date_start or '1900'}-01-01", 
                                                "to": f"{date_end or '2099'}-12-31",
                                                "include_lower": True, "include_upper": True}}})
        
        query = {"type": "group", "logical_operator": "and", "nodes": nodes} if len(nodes) > 1 else nodes[0]
        body = {"query": query, "return_type": "entry", 
                "request_options": {"paginate": {"start": 0, "rows": 1000}, "results_content_type": content_type}}
        
        resp = safe_request(SEARCH_API, method="post", json_data=body)
        if resp and resp.text.strip():
            try:
                all_ids.update([hit["identifier"] for hit in resp.json().get("result_set", [])])
            except:
                pass
    return list(all_ids)

def fetch_single_batch(batch_ids, query):
    resp = safe_request(GRAPHQL_API, method="post", json_data={"query": query, "variables": {"ids": batch_ids}}, timeout=60)
    if resp:
        try:
            return [e for e in resp.json().get("data", {}).get("entries", []) if e]
        except:
            pass
    return []

def fetch_entries_graphql_parallel(struct_ids, batch_size=DEFAULT_BATCH_SIZE):
    pdb_ids = [i for i in struct_ids if not i.startswith("AF_") and not i.startswith("MA_")]
    csm_ids = [i for i in struct_ids if i.startswith("AF_") or i.startswith("MA_")]
    
    def fetch_all(ids, query):
        batches = [ids[i:i + batch_size] for i in range(0, len(ids), batch_size)]
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS_GRAPHQL) as ex:
            for r in ex.map(lambda b: fetch_single_batch(b, query), batches):
                results.extend(r)
        return results
    
    pdb_entries = fetch_all(pdb_ids, GRAPHQL_QUERY_PDB) if pdb_ids else []
    csm_entries = fetch_all(csm_ids, GRAPHQL_QUERY_CSM) if csm_ids else []
    print(f"  Fetched {len(pdb_entries)} PDB + {len(csm_entries)} CSM entries")
    return pdb_entries, csm_entries

def parse_pdb_entry(entry):
    pdb_id = entry.get("rcsb_id", "NA")
    title = capitalize_title((entry.get("struct") or {}).get("title", "NA"))
    release = ((entry.get("rcsb_accession_info") or {}).get("initial_release_date", "NA") or "NA")[:10]
    
    doi = "NA"
    cit = entry.get("rcsb_primary_citation")
    if cit:
        doi = cit.get("pdbx_database_id_DOI") or (f"PMID:{cit['pdbx_database_id_PubMed']}" if cit.get("pdbx_database_id_PubMed") else "NA")
    
    exp = "; ".join([e.get("method") for e in (entry.get("exptl") or []) if e and e.get("method")]) or "NA"
    mw = f"{(entry.get('rcsb_entry_info') or {}).get('molecular_weight', 0):.2f} kDa" if (entry.get('rcsb_entry_info') or {}).get('molecular_weight') else "NA"
    
    species_set, mutation = set(), "No"
    for pe in (entry.get("polymer_entities") or []):
        if not pe: continue
        for org in (pe.get("rcsb_entity_source_organism") or []):
            if org and org.get("scientific_name"): 
                species_set.add(org["scientific_name"])
        if mutation == "No":
            m = ((pe.get("rcsb_polymer_entity") or {}).get("pdbx_mutation") or "")
            if m and m.strip().lower() not in ["", "none", "null", "?", "n/a", "wild type", "wt"]: 
                mutation = "Yes"
    
    missing = (entry.get("rcsb_entry_info") or {}).get("deposited_unmodeled_polymer_monomer_count", 0) or 0
    
    oligo = "NA"
    if entry.get("assemblies"):
        details = ((entry["assemblies"][0] or {}).get("pdbx_struct_assembly") or {}).get("oligomeric_details", "").lower()
        for n, name in [(1, "monomer"), (2, "dimer"), (3, "trimer"), (4, "tetramer")]:
            if name in details: 
                oligo = str(n)
                break
        if oligo == "NA": 
            oligo = str((entry["assemblies"][0].get("rcsb_assembly_info") or {}).get("polymer_entity_instance_count", "NA"))
    
    ligands = [((npe or {}).get("pdbx_entity_nonpoly") or {}).get("comp_id") for npe in (entry.get("nonpolymer_entities") or [])]
    ligands = [l for l in ligands if l and l.upper() not in SKIP_LIGANDS]
    
    return {
        "Structure_ID": pdb_id, "Source": "PDB", "Title": title, "DOI": doi, "Release_Date": release,
        "Species": "; ".join(sorted([s.capitalize() for s in species_set])) or "NA", "Mutation": mutation,
        "Exp_Technique": exp, "Oligomeric_State": oligo, "Mol_Weight": mw, "Missing_Residues": missing,
        "Ligands": "; ".join(ligands) if ligands else "No", "pLDDT": "NA", 
        "URL": f"https://www.rcsb.org/structure/{pdb_id}"
    }

def parse_csm_entry(entry):
    rcsb_id = entry.get("rcsb_id", "NA")
    info = convert_rcsb_id_to_native(rcsb_id)
    
    title = capitalize_title((entry.get("struct") or {}).get("title", "NA"))
    release = ((entry.get("rcsb_accession_info") or {}).get("initial_release_date", "NA") or "NA")[:10]
    mw = f"{(entry.get('rcsb_entry_info') or {}).get('molecular_weight', 0):.2f} kDa" if (entry.get('rcsb_entry_info') or {}).get('molecular_weight') else "NA"
    
    species_set = set()
    for pe in (entry.get("polymer_entities") or []):
        for org in (pe.get("rcsb_entity_source_organism") or []):
            if org and org.get("scientific_name"): 
                species_set.add(org["scientific_name"])

    plddt = "NA"
    for metric_container in (entry.get("rcsb_ma_qa_metric_global") or []):
        if not metric_container:
            continue
        ma_list = metric_container.get("ma_qa_metric_global")
        if isinstance(ma_list, list):
            for ma in ma_list:
                if ma and isinstance(ma, dict) and ma.get("type") == "pLDDT" and ma.get("value") is not None:
                    plddt = f"{ma['value']:.2f}"
                    break
        if plddt != "NA":
            break
    
    result = {
        "Structure_ID": info["native_id"], "Source": info["source"], "Title": title, "DOI": "NA",
        "Release_Date": release, "Species": "; ".join(sorted([s.capitalize() for s in species_set])) or "NA",
        "Mutation": "NA", "Exp_Technique": f"AI Prediction ({info['source']})", "Oligomeric_State": "1",
        "Mol_Weight": mw, "Missing_Residues": 0, "Ligands": "No", "pLDDT API": plddt, "URL": info["url"]
    }
    if "uniprot_id" in info: 
        result["UniProt_ID"] = info["uniprot_id"]
    return result

def sort_results(results):
    def get_date(r): 
        return r.get("Release_Date", "") if r.get("Release_Date", "") != "NA" else "0000-00-00"
    pdb = sorted([r for r in results if r.get("Source") == "PDB"], key=get_date, reverse=True)
    af = sorted([r for r in results if r.get("Source") == "AlphaFold"], key=get_date, reverse=True)
    ma = sorted([r for r in results if r.get("Source") == "ModelArchive"], key=get_date, reverse=True)
    return pdb + af + ma

def download_single_pdb(pdb_id, output_dir):
    for ext in ["cif", "pdb"]:
        try:
            resp = SESSION.get(f"https://files.rcsb.org/download/{pdb_id.lower()}.{ext}", timeout=30)
            if resp.status_code == 200:
                with open(os.path.join(output_dir, f"{pdb_id}.{ext}"), 'w') as f: 
                    f.write(resp.text)
                return True
        except: 
            pass
    return False

def download_single_alphafold(native_id, output_dir):
    match = re.match(r'AF-([A-Z0-9]+)-F(\d+)', native_id)
    if not match:
        return False
    uniprot = match.group(1)
    
    # Utiliser l'API AlphaFold pour obtenir l'URL correcte
    try:
        time.sleep(REQUEST_DELAY)
        api_url = f"https://alphafold.ebi.ac.uk/api/prediction/{uniprot}"
        resp = SESSION.get(api_url, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list) and len(data) > 0:
                cif_url = data[0].get("cifUrl")
                if cif_url:
                    time.sleep(REQUEST_DELAY)
                    cif_resp = SESSION.get(cif_url, timeout=60)
                    if cif_resp.status_code == 200 and len(cif_resp.text) > 1000:
                        filepath = os.path.join(output_dir, f"{native_id}.cif")
                        with open(filepath, 'w') as f:
                            f.write(cif_resp.text)
                        return True
    except:
        pass
    return False

def download_single_modelarchive(native_id, output_dir):
    """
    Download structure from ModelArchive.
    Native IDs are like: ma-dataset-123 or MA_MADATA123
    
    ModelArchive API format:
    https://www.modelarchive.org/api/projects/{id}?type=basic__model_file_name
    """
    try:
        # Try different ID formats
        ids_to_try = [native_id]
        
        # If native_id is like "ma-xxx-123", also try without prefix formatting
        if native_id.startswith("ma-"):
            # Keep as-is for API
            pass
        elif native_id.startswith("MA_"):
            # Convert MA_MADATA123 to ma-data-123 format
            inner = native_id[3:]  # Remove MA_
            if inner.startswith("MA"):
                inner = inner[2:]  # Remove second MA if present
            # Try to find where numbers start
            match = re.match(r'^([A-Za-z]+)(\d+)$', inner)
            if match:
                dataset = match.group(1).lower()
                num = match.group(2)
                ids_to_try.append(f"ma-{dataset}-{num}")
        
        for model_id in ids_to_try:
            time.sleep(REQUEST_DELAY)
            
            # ModelArchive API endpoint
            api_url = f"https://www.modelarchive.org/api/projects/{model_id}?type=basic__model_file_name"
            
            resp = SESSION.get(api_url, timeout=60, headers={
                'Accept': 'text/plain, application/octet-stream, */*',
                'User-Agent': 'KitsuneFetch/2.1.0'
            })
            
            if resp.status_code == 200:
                content = resp.text
                # Check if it's a valid CIF file (should contain data_ at start)
                if content and len(content) > 500 and ('data_' in content[:100] or '_entry.id' in content):
                    filepath = os.path.join(output_dir, f"{native_id}.cif")
                    with open(filepath, 'w') as f:
                        f.write(content)
                    return True
        
        # Fallback: try RCSB direct download
        # The RCSB ID format for ModelArchive is like MA_MAxxxxxx
        rcsb_variants = []
        if native_id.startswith("ma-"):
            # Convert ma-dataset-123 to MA_MAdataset123
            parts = native_id.split("-")
            if len(parts) >= 3:
                dataset = parts[1]
                num = "-".join(parts[2:])
                rcsb_variants.append(f"MA_MA{dataset.upper()}{num}")
                rcsb_variants.append(f"MA_{dataset.upper()}{num}")
        else:
            rcsb_variants.append(native_id)
            if not native_id.startswith("MA_"):
                rcsb_variants.append(f"MA_{native_id}")
        
        for rcsb_id in rcsb_variants:
            for ext in ["cif", "pdb"]:
                try:
                    time.sleep(REQUEST_DELAY)
                    url = f"https://files.rcsb.org/download/{rcsb_id}.{ext}"
                    resp = SESSION.get(url, timeout=30)
                    if resp.status_code == 200 and len(resp.text) > 500:
                        # Verify it's actual structure data
                        if 'ATOM' in resp.text or 'data_' in resp.text:
                            filepath = os.path.join(output_dir, f"{native_id}.{ext}")
                            with open(filepath, 'w') as f:
                                f.write(resp.text)
                            return True
                except:
                    pass
        
    except Exception as e:
        pass
    
    return False

def download_structures_parallel(results, output_dir):
    pdb = [r["Structure_ID"] for r in results if r.get("Source") == "PDB"]
    af = [r["Structure_ID"] for r in results if r.get("Source") == "AlphaFold"]
    ma = [r["Structure_ID"] for r in results if r.get("Source") == "ModelArchive"]
    total = 0
    
    if pdb:
        d = os.path.join(output_dir, "PDB_structures")
        os.makedirs(d, exist_ok=True)
        print(f"\nDownloading {len(pdb)} PDB...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS_DOWNLOAD) as ex:
            total += sum(1 for f in concurrent.futures.as_completed([ex.submit(download_single_pdb, i, d) for i in pdb]) if f.result())
    if af:
        d = os.path.join(output_dir, "AlphaFold_structures")
        os.makedirs(d, exist_ok=True)
        print(f"Downloading {len(af)} AlphaFold...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS_DOWNLOAD) as ex:
            total += sum(1 for f in concurrent.futures.as_completed([ex.submit(download_single_alphafold, i, d) for i in af]) if f.result())
    if ma:
        d = os.path.join(output_dir, "ModelArchive_structures")
        os.makedirs(d, exist_ok=True)
        print(f"Downloading {len(ma)} ModelArchive...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS_DOWNLOAD) as ex:
            results_ma = list(concurrent.futures.as_completed([ex.submit(download_single_modelarchive, i, d) for i in ma]))
            success = sum(1 for f in results_ma if f.result())
            total += success
            if len(ma) - success > 0:
                print(f"  Note: {len(ma) - success} ModelArchive structures could not be downloaded")
    return total

def apply_filters(results, no_mutation=False, no_ligand=False, with_ligand=None, 
                  oligomeric_state=None, technique=None, max_missing=None, min_plddt=None):
    kept, filtered_out = [], []
    
    for r in results:
        source = r.get("Source", "PDB")
        reason = None
        
        if no_mutation and source == "PDB" and r.get("Mutation", "").startswith("Yes"):
            reason = "has mutation"
        if not reason and no_ligand and source == "PDB" and r.get("Ligands", "No") != "No":
            reason = "has ligand"
        if not reason and with_ligand and source == "PDB":
            if with_ligand.upper() not in r.get("Ligands", "").upper():
                reason = f"no {with_ligand} ligand"
        if not reason and oligomeric_state and r.get("Oligomeric_State") != oligomeric_state:
            reason = f"oligomer != {oligomeric_state}"
        if not reason and technique:
            exp = r.get("Exp_Technique", "").lower()
            match = (technique == "xray" and "x-ray" in exp) or \
                    (technique == "nmr" and "nmr" in exp) or \
                    (technique == "em" and ("microscopy" in exp or "cryo" in exp)) or \
                    (technique == "predicted" and "ai prediction" in exp)
            if not match:
                reason = f"technique != {technique}"
        if not reason and max_missing is not None and source == "PDB":
            if r.get("Missing_Residues", 0) > max_missing:
                reason = f"missing > {max_missing}"
        if not reason and min_plddt is not None and source in ["AlphaFold", "ModelArchive"]:
            plddt = r.get("pLDDT API", r.get("pLDDT", "NA"))
            if plddt != "NA":
                try:
                    if float(plddt) < min_plddt:
                        reason = f"pLDDT < {min_plddt}"
                except:
                    pass
        
        if reason:
            r["Filter_Reason"] = reason
            filtered_out.append(r)
        else:
            kept.append(r)
    
    return kept, filtered_out

def save_results_by_source(results, filtered_out, output_dir):
    sources = {}
    for r in results:
        src = r.get("Source", "PDB").lower()
        prefix = "pdb" if src == "pdb" else "af" if src == "alphafold" else "ma"
        if prefix not in sources:
            sources[prefix] = []
        sources[prefix].append(r)
    
    filtered_sources = {}
    for r in filtered_out:
        src = r.get("Source", "PDB").lower()
        prefix = "pdb" if src == "pdb" else "af" if src == "alphafold" else "ma"
        if prefix not in filtered_sources:
            filtered_sources[prefix] = []
        filtered_sources[prefix].append(r)
    
    # Columns to exclude: Source and URL for all, pLDDT for PDB only
    exclude_all = {"Source", "URL"}
    exclude_pdb = {"Source", "URL", "pLDDT"}
    
    for prefix, data in sources.items():
        if not data:
            continue
        exclude = exclude_pdb if prefix == "pdb" else exclude_all
        fieldnames = [k for k in data[0].keys() if k not in exclude]
        filepath = os.path.join(output_dir, f"{prefix}_results.csv")
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t', extrasaction='ignore')
            w.writeheader()
            w.writerows(data)
        print(f"  -> {prefix}_results.csv ({len(data)} entries)")
    
    for prefix, data in filtered_sources.items():
        if not data:
            continue
        exclude = exclude_pdb if prefix == "pdb" else exclude_all
        fieldnames = [k for k in data[0].keys() if k not in exclude]
        if "Filter_Reason" not in fieldnames:
            fieldnames.append("Filter_Reason")
        filepath = os.path.join(output_dir, f"{prefix}_filtered_out.csv")
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t', extrasaction='ignore')
            w.writeheader()
            w.writerows(data)
        print(f"  -> {prefix}_filtered_out.csv ({len(data)} entries)")

def generate_statistics(results, output_dir, database, command_line, execution_time):
    if not results: 
        return
    
    pdb = [r for r in results if r.get("Source") == "PDB"]
    af = [r for r in results if r.get("Source") == "AlphaFold"]
    ma = [r for r in results if r.get("Source") == "ModelArchive"]
    
    with open(os.path.join(output_dir, "KitsuneFetch.log"), 'w') as f:
        f.write(f"{'='*60}\n")
        f.write(f"KitsuneFetch {VERSION} - SUMMARY\n")
        f.write(f"{'='*60}\n\n")
        f.write(f"Command: {command_line}\n")
        f.write(f"Execution time: {execution_time}\n\n")
        f.write(f"Database filter: {database.upper()}\n")
        f.write(f"Total results: {len(results)}\n\n")
        if pdb: f.write(f"  - PDB: {len(pdb)}\n")
        if af: f.write(f"  - AlphaFold: {len(af)}\n")
        if ma: f.write(f"  - ModelArchive: {len(ma)}\n")
    print(f"  -> KitsuneFetch.log")
    
    if pdb and database in [DB_PDB, DB_ALL]: 
        _gen_pdb_stats(pdb, output_dir)
    if af and database in [DB_ALPHAFOLD, DB_ALL]: 
        _gen_csm_stats(af, "af", "AlphaFold", output_dir)
    if ma and database in [DB_MODELARCHIVE, DB_ALL]: 
        _gen_csm_stats(ma, "ma", "ModelArchive", output_dir)

def _gen_pdb_stats(results, output_dir):
    total = len(results)
    tech_counts, oligo_counts, species_counts, ligand_counts = {}, {}, {}, {}
    
    for r in results:
        tech = r.get("Exp_Technique", "Unknown")
        tech_counts[tech] = tech_counts.get(tech, 0) + 1
        
        oligo = r.get("Oligomeric_State", "NA")
        oligo_counts[oligo] = oligo_counts.get(oligo, 0) + 1
        
        for s in r.get("Species", "Unknown").split(";"):
            s = s.strip()
            if s and s != "NA":
                species_counts[s] = species_counts.get(s, 0) + 1
        
        lig = r.get("Ligands", "No")
        if lig == "No":
            ligand_counts["No ligand"] = ligand_counts.get("No ligand", 0) + 1
        else:
            for l in lig.split(";"):
                l = l.strip()
                if l:
                    ligand_counts[l] = ligand_counts.get(l, 0) + 1
    
    with open(os.path.join(output_dir, "pdb_statistics.txt"), 'w') as f:
        f.write(f"{'='*60}\n")
        f.write(f"PDB STATISTICS ({total} structures)\n")
        f.write(f"{'='*60}\n\n")
        
        f.write("EXPERIMENTAL TECHNIQUES:\n")
        for k, v in sorted(tech_counts.items(), key=lambda x: -x[1]):
            f.write(f"  {k}: {v} ({v/total*100:.1f}%)\n")
        
        f.write("\nOLIGOMERIC STATE DISTRIBUTION:\n")
        for k, v in sorted(oligo_counts.items()):
            label = f"{k}-mer" if k.isdigit() else k
            f.write(f"  {label}: {v} ({v/total*100:.1f}%)\n")
        
        f.write("\nSPECIES:\n")
        for k, v in sorted(species_counts.items(), key=lambda x: -x[1])[:15]:
            f.write(f"  {k}: {v} ({v/total*100:.1f}%)\n")
        
        f.write("\nLIGANDS:\n")
        has_ligand = total - ligand_counts.get("No ligand", 0)
        f.write(f"  With ligand: {has_ligand} ({has_ligand/total*100:.1f}%)\n")
        f.write(f"  Without ligand: {ligand_counts.get('No ligand', 0)}\n")
        f.write("\n  Top ligands:\n")
        for k, v in sorted([(k,v) for k,v in ligand_counts.items() if k != "No ligand"], key=lambda x: -x[1])[:10]:
            f.write(f"    {k}: {v}\n")
    
    print(f"  -> pdb_statistics.txt")
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    fig.suptitle(f'PDB Statistics ({total} structures)', fontsize=16, fontweight='bold')
    
    _make_pie(axes[0, 0], tech_counts, 'Experimental Techniques')
    oligo_display = {(f"{k}-mer" if k.isdigit() else k): v for k, v in oligo_counts.items()}
    _make_pie(axes[0, 1], oligo_display, 'Oligomeric State Distribution')
    _make_pie(axes[1, 0], species_counts, 'Species', max_items=8)
    ligand_summary = {"With ligand": total - ligand_counts.get("No ligand", 0), "No ligand": ligand_counts.get("No ligand", 0)}
    _make_pie(axes[1, 1], ligand_summary, 'Ligand Presence')
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(os.path.join(output_dir, "pdb_statistics_figures.png"), dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  -> pdb_statistics_figures.png")

def _gen_csm_stats(results, prefix, source_name, output_dir):
    total = len(results)
    species_counts = {}
    plddt_values = []
    plddt_ranges = {"Very High (>90)": 0, "High (70-90)": 0, "Low (50-70)": 0, "Very Low (<50)": 0}
    
    for r in results:
        for s in r.get("Species", "Unknown").split(";"):
            s = s.strip()
            if s and s != "NA":
                species_counts[s] = species_counts.get(s, 0) + 1
        
        plddt = r.get("pLDDT API", "NA")
        if plddt != "NA":
            try:
                v = float(plddt)
                plddt_values.append(v)
                if v > 90: plddt_ranges["Very High (>90)"] += 1
                elif v > 70: plddt_ranges["High (70-90)"] += 1
                elif v > 50: plddt_ranges["Low (50-70)"] += 1
                else: plddt_ranges["Very Low (<50)"] += 1
            except:
                pass
    
    with open(os.path.join(output_dir, f"{prefix}_statistics.txt"), 'w') as f:
        f.write(f"{'='*60}\n")
        f.write(f"{source_name.upper()} STATISTICS ({total} structures)\n")
        f.write(f"{'='*60}\n\n")
        
        f.write("pLDDT CONFIDENCE DISTRIBUTION:\n")
        for k, v in plddt_ranges.items():
            if v > 0:
                f.write(f"  {k}: {v} ({v/total*100:.1f}%)\n")
        if plddt_values:
            f.write(f"\n  Mean pLDDT: {np.mean(plddt_values):.1f}\n")
            f.write(f"  Median pLDDT: {np.median(plddt_values):.1f}\n")
        
        f.write("\nSPECIES:\n")
        for k, v in sorted(species_counts.items(), key=lambda x: -x[1])[:15]:
            f.write(f"  {k}: {v} ({v/total*100:.1f}%)\n")
    
    print(f"  -> {prefix}_statistics.txt")
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(f'{source_name} Statistics ({total} structures)', fontsize=14, fontweight='bold')
    
    if plddt_values:
        colors = {'Very High (>90)': '#2ecc71', 'High (70-90)': '#3498db', 'Low (50-70)': '#f39c12', 'Very Low (<50)': '#e74c3c'}
        plddt_data = {k: v for k, v in plddt_ranges.items() if v > 0}
        if plddt_data:
            wedges, _, _ = axes[0].pie(plddt_data.values(), autopct=lambda p: f'{p:.1f}%' if p > 5 else '',
                                       colors=[colors.get(k, '#95a5a6') for k in plddt_data.keys()])
            axes[0].legend(wedges, [f"{k} ({v})" for k, v in plddt_data.items()], loc="upper left", bbox_to_anchor=(-0.2, 1.0), fontsize=9)
        axes[0].set_title('pLDDT Confidence Distribution')
    else:
        axes[0].text(0.5, 0.5, 'No pLDDT data', ha='center', va='center', fontsize=12)
        axes[0].axis('off')
    
    _make_pie(axes[1], species_counts, 'Species', max_items=8)
    
    plt.tight_layout(rect=[0, 0, 1, 0.93])
    plt.savefig(os.path.join(output_dir, f"{prefix}_statistics_figures.png"), dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  -> {prefix}_statistics_figures.png")

def _make_pie(ax, data, title, max_items=8):
    if not data or all(v == 0 for v in data.values()):
        ax.text(0.5, 0.5, 'No data', ha='center', va='center', fontsize=12)
        ax.set_title(title, fontweight='bold')
        ax.axis('off')
        return
    
    data = {k: v for k, v in data.items() if v > 0}
    sorted_data = sorted(data.items(), key=lambda x: -x[1])
    
    if len(sorted_data) > max_items:
        top = dict(sorted_data[:max_items-1])
        top["Others"] = sum(v for _, v in sorted_data[max_items-1:])
    else:
        top = dict(sorted_data)
    
    wedges, _, _ = ax.pie(top.values(), autopct=lambda p: f'{p:.0f}%' if p > 5 else '', colors=plt.cm.Set3.colors[:len(top)])
    ax.legend(wedges, [f"{k} ({v})" for k, v in top.items()], loc="upper left", bbox_to_anchor=(-0.3, 1.0), fontsize=8)
    ax.set_title(title, fontweight='bold')

def create_output_directory(protein_name, database, species):
    now = datetime.now()
    prefix = {"pdb": "PDB", "alphafold": "AlphaFold", "modelarchive": "ModelArchive", "all": "ALL"}.get(database, "ALL")
    parts = [prefix, protein_name] + ([species] if species else []) + [now.strftime("%d-%m-%Y_%H-%M-%S")]
    name = re.sub(r'[^\w\-]', '_', "_".join(parts))
    os.makedirs(name, exist_ok=True)
    return name

def query_protein(protein_name, database=DB_ALL, species=None, date_start=None, date_end=None,
                 download_flag=False, batch_size=DEFAULT_BATCH_SIZE, no_mutation=False, 
                 no_ligand=False, with_ligand=None, oligomeric_state=None, technique=None, 
                 max_missing=None, min_plddt=None, command_line=None):
    start = time.time()
    print(f"\n{'='*60}\nKitsuneFetch {VERSION}\n{'='*60}")
    print(f"Protein: {protein_name}\nDatabase: {database.upper()}")
    if species: print(f"Species: {species}")
    print(f"{'='*60}\n")
    
    print("Searching databases...")
    struct_ids = search_database(protein_name, database, species, date_start, date_end)
    if not struct_ids: 
        print("No structures found.")
        return
    
    struct_ids = filter_by_source(struct_ids, database)
    if not struct_ids: 
        print(f"No structures for {database}")
        return
    
    counts = {"PDB": len([i for i in struct_ids if not i.startswith(("AF_", "MA_"))]),
              "AlphaFold": len([i for i in struct_ids if i.startswith("AF_")]),
              "ModelArchive": len([i for i in struct_ids if i.startswith("MA_")])}
    print(f"\nFound {len(struct_ids)}: " + ", ".join(f"{k}={v}" for k, v in counts.items() if v))
    
    print("\nFetching details...")
    pdb_entries, csm_entries = fetch_entries_graphql_parallel(struct_ids, batch_size)
    if not pdb_entries and not csm_entries: 
        print("No data retrieved.")
        return
    
    print("Parsing...")
    results = [parse_pdb_entry(e) for e in pdb_entries] + [parse_csm_entry(e) for e in csm_entries]
    if not results: 
        print("No results.")
        return
    
    filtered_out = []
    has_filters = any([no_mutation, no_ligand, with_ligand, oligomeric_state, technique, max_missing is not None, min_plddt is not None])
    if has_filters:
        results, filtered_out = apply_filters(results, no_mutation, no_ligand, with_ligand, oligomeric_state, technique, max_missing, min_plddt)
        if filtered_out:
            print(f"  Filtered: {len(filtered_out)} removed, {len(results)} remaining")
    
    if not results: 
        print("No structures match filter criteria.")
        return
    
    results = sort_results(results)
    if filtered_out:
        filtered_out = sort_results(filtered_out)
    
    output_dir = create_output_directory(protein_name, database, species)
    print(f"\nOutput: {output_dir}/")
    
    save_results_by_source(results, filtered_out, output_dir)
    
    execution_time = format_duration(time.time() - start)
    generate_statistics(results, output_dir, database, command_line or " ".join(sys.argv), execution_time)
    
    if download_flag: 
        download_structures_parallel(results, output_dir)
    
    print(f"\n{'='*60}\nDONE! {len(results)} entries in {execution_time}\n{'='*60}")

def main():
    if len(sys.argv) < 2: 
        print("Usage: python KitsuneFetch.py <protein> [species] [--database=X] [--download] [filters]")
        print("\nFilters:")
        print("  --no-mutation      Exclude structures with mutations")
        print("  --no-ligand        Exclude structures with ligands")
        print("  --ligand=XXX       Only structures with specific ligand")
        print("  --oligomer=N       Only specific oligomeric state")
        print("  --technique=X      xray, nmr, em, or predicted")
        print("  --max-missing=N    Max missing residues (PDB)")
        print("  --min-plddt=N      Min pLDDT score (AlphaFold/ModelArchive)")
        sys.exit(0)
    
    # Store the full command line
    command_line = " ".join(sys.argv)
    
    protein, database, species, download, batch = sys.argv[1], DB_ALL, None, False, DEFAULT_BATCH_SIZE
    no_mutation, no_ligand, with_ligand = False, False, None
    oligomeric_state, technique, max_missing, min_plddt = None, None, None, None
    
    positional = []
    for arg in sys.argv[2:]:
        if arg.startswith("--database="): database = arg.split("=", 1)[1].lower()
        elif arg.startswith("--batch-size="): batch = int(arg.split("=", 1)[1])
        elif arg == "--download": download = True
        elif arg == "--no-mutation": no_mutation = True
        elif arg == "--no-ligand": no_ligand = True
        elif arg.startswith("--ligand="): with_ligand = arg.split("=", 1)[1]
        elif arg.startswith("--oligomer="): oligomeric_state = arg.split("=", 1)[1]
        elif arg.startswith("--technique="): technique = arg.split("=", 1)[1].lower()
        elif arg.startswith("--max-missing="): max_missing = int(arg.split("=", 1)[1])
        elif arg.startswith("--min-plddt="): min_plddt = float(arg.split("=", 1)[1])
        elif not arg.startswith("--"): positional.append(arg)
    
    if positional: species = positional[0]
    
    query_protein(protein, database, species, download_flag=download, batch_size=batch,
                  no_mutation=no_mutation, no_ligand=no_ligand, with_ligand=with_ligand,
                  oligomeric_state=oligomeric_state, technique=technique,
                  max_missing=max_missing, min_plddt=min_plddt, command_line=command_line)

if __name__ == "__main__":
    main()
