"""
Not used yet, but can be used to parse simulation files after they've been 
uploaded to the databases
"""
import os
import glob
import requests

import MDAnalysis as mda
# from rcsbsearchapi.search import SequenceQuery

def get_protein_seq(u):
    """
    Get the sequence of proteins in an mda universe
    """
    protein = u.select_atoms("protein").residues

    # Bio.SeqIO library used by MDAnalysis doesn't recognise HIP histidine residue name
    if "HIP" in protein.resnames:
        # Select all residues with the resname "HIP"
        selection_string = "resname HIP"
        residues = u.select_atoms(selection_string).residues

        # Change the resname of the selected residues to "HIS"
        new_resnames = ["HIS"] * len(residues)
        residues.resnames = new_resnames
        protein = u.select_atoms("protein").residues

    sequence = protein.sequence(id="sequence1", name="protein1")
    return sequence

def search_rcsb(query_sequence):
    """
    Use the rcsb API to get PDB entries that are most likely to match the
    simulated system
    """
    # # 1. Use the search API first to get the relevant entry
    # # Use SequenceQuery class and add parameters
    # results = SequenceQuery(str(query_sequence.seq), 1, 0.95)
    # # results("polymer_entity") produces an iterator of IDs with return type - polymer entities
    # print(len(list(results("polymer_entity"))))

    # 2. Get entries via web API

    # API endpoint
    url = "https://search.rcsb.org/rcsbsearch/v2/query"

    # Payload with your sequence query
    payload = {
        "query": {
            "type": "terminal",
            "service": "sequence",
            "parameters": {
                "evalue_cutoff": 1,
                "identity_cutoff": 0.95,
                "target": "pdb_protein_sequence",
                "value": str(query_sequence.seq)
            }
        },
        "return_type": "entry",
        "request_options": {
            "paginate": {"start": 0, "rows": 5}, # get top 5 entries
            "scoring_strategy": "sequence",
            "sort": [
                # {"sort_by": "score", "direction": "desc"}  # sort by score
                {"sort_by": "rcsb_entry_info.resolution_combined", "direction": "asc"} # sort by resolution
            ]
        }
    }

    # Send the POST request with JSON body
    response = requests.post(url, json=payload)

    identifiers = []
    # Handle response
    if response.status_code == 200:
        data = response.json()
        for result in data.get("result_set", []):
            identifier = result["identifier"]
            identifiers.append(identifier)
            # score = result.get("score", "N/A")
            # print(f"ID: {identifier}, Score: {score}")
            # print(json.dumps(result, indent=2))
    else:
        print("Search failed:", response.status_code, response.text)

    return identifiers


def fetch_top_traj_files(sim_records):
    """
    For a given simulation project in the database, iterate over each simulation 
    entry in the project and and load as an MDA universe.
    """
    for i, entry in enumerate(sim_records):
        # get the name of the directory the simulation is in
        sim_dir = entry["simulation directory"]
        # get the file paths for the topology and trajectory in the entry
        top = glob.glob(sim_dir+"/topology.*")
        traj = glob.glob(sim_dir+"/trajectory.*")
        if top and traj:
            # if a topology and trajectory is found, get the topology extension
            # and load as an MDAnalysis universe
            extension = os.path.splitext(top[0])[1].replace('.', '')
            u = mda.Universe(top[0], traj, topology_format=extension)
            # do things with the universe...
            # sequence = get_protein_seq(u)
            # identifiers = search_rcsb(sequence)