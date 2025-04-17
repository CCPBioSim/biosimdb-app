#!/usr/bin/env python
# from . import bp
from flask import current_app
import os
import json
import sys

import MDAnalysis as mda
import Bio.SeqIO
import aiida
from aiida import orm, profile_context
from aiida.storage.sqlite_zip.backend import SqliteZipBackend


def extract_from_mda_universe(u):
    """
    For the topology and trajectory uploaded, try to parse these and save 
    relevant information into the database

    https://userguide.mdanalysis.org/stable/topology_system.html
    """
    resnames = json.dumps(list(u.residues.resnames)) # convert numpy array
    atomnames = json.dumps(list(u.atoms.names))
    atom_masses = list(u.atoms.masses.flatten())
    atom_masses = json.dumps(" ".join(map(str, atom_masses)))
    n_atoms = len(u.atoms)
    n_frames = len(u.trajectory)
    # single_frame_positions = u.trajectory[0].positions # or use u.atoms.position
    single_frame_positions = list(u.trajectory[0].positions.flatten()) # or use u.atoms.position
    single_frame_positions = json.dumps(" ".join(map(str, single_frame_positions)))
    # single_frame_dimensions = u.trajectory[0].dimensions
    single_frame_dimensions = list(u.trajectory[0].dimensions.flatten())
    single_frame_dimensions = json.dumps(" ".join(map(str, single_frame_dimensions)))

    simulation_time = u.trajectory.time
    if simulation_time != 0.:
        time_between_snapshots = u.trajectory.ts.dt
    else:
        simulation_time = None
        time_between_snapshots = None
    try:
        charges = json.dumps(list(u.atoms.charges))
        system_charge = sum(charges)
    except mda.exceptions.NoDataError:
        charges = None
        system_charge = None

    # create a dictionary with all the results
    mda_u_dict = {
        "resnames": resnames,
        "atomnames": atomnames,
        "atom_masses": atom_masses,
        "n_atoms": n_atoms,
        "n_frames": n_frames,
        "single_frame_positions": single_frame_positions,
        "single_frame_dimensions": single_frame_dimensions,
        "simulation_time": simulation_time,
        "time_between_snapshots": time_between_snapshots,
        "charges": charges,
        "system_charge": system_charge,
    }

    return mda_u_dict


def extract_from_aiida_archive(aiida_file_path):
    """
    For a given aiida archive, extract relevant metadata.
    Also, try to find a toplogy and trajectory for the latest
    """
    # Create a temporary folder to store uploaded files
    temp_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(temp_folder, exist_ok=True)

    archive_profile = SqliteZipBackend.create_profile(aiida_file_path)

    md_metadata_dict = None
    with profile_context(archive_profile):
        qb = orm.QueryBuilder()
        # get all processes and order from newest to oldest
        qb.append(orm.ProcessNode, tag='process')
        qb.order_by({orm.ProcessNode: {"ctime": "desc"}})
        # print(dir(qb))
        top, traj, logfile_dict = None, None, None
        for i, entry in enumerate(qb.all(flat=True)):
            if logfile_dict != None:
                break
            # incoming = entry.get_incoming().all_nodes()
            outgoing = entry.get_outgoing().all_nodes()
            # print("$$$", entry.process_label)
            possible_top, possible_trajs = None, []
            for outputs in outgoing:
                # print(dir(outputs))
                if isinstance(outputs, orm.Dict) and entry.process_label == "MdrunCalculation":
                    # print("^^^", outputs.get_dict())
                    logfile_dict = outputs.get_dict()
                    break
                if isinstance(outputs, orm.SinglefileData):
                    # print("___", outputs.filename)
                    extension = os.path.splitext(outputs.filename)[1].replace('.', '')
                    if extension in ['psf', 'top', 'prmtop', 'parm7', 'pdb', 'ent', 'xpdb', 'pqr', 'gro', 'crd', 'pdbqt', 'dms', 'tpr', 'mol2', 'data', 'lammpsdump', 'xyz', 'txyz', 'arc', 'gms', 'config', 'history', 'xml', 'mmtf', 'gsd', 'minimal', 'itp', 'in', 'fhiaims', 'parmed', 'rdkit', 'openmmtopology', 'openmmapp']:
                        possible_top = outputs
                    if extension in ['chain', 'chemfiles', 'crd', 'dcd', 'config', 'history', 'dms', 'gms', 'gro', 'inpcrd', 'restrt', 'lammps', 'data', 'lammpsdump', 'mol2', 'pdb', 'ent', 'xpdb', 'pdbqt', 'pqr', 'trc', 'trj', 'mdcrd', 'crdbox', 'ncdf', 'nc', 'trr', 'h5md', 'trz', 'xtc', 'xyz', 'txyz', 'arc', 'memory', 'mmtf', 'gsd', 'coor', 'namdbin', 'in', 'fhiaims', 'tng', 'parmed', 'rdkit', 'openmmsimulation', 'openmmapp'] and outputs != possible_top:
                        possible_trajs.append(outputs)
            # if possible_top:
            #     print(">>", possible_top.filename)
            #     for traj in possible_trajs:
            #         print("\t>>", traj.filename)
            #         # with possible_top.open(mode='rb') as source:
            #         #     print(source)
            #         #     file_path = os.path.join(temp_folder, possible_top.filename)
            #         #     print(dir(source))
            #         with possible_top.as_path() as topfile:
            #             for traj in possible_trajs:
            #                 with traj.as_path() as trajfile:
            #                     # file_path = os.path.join(temp_folder, trajfile)
            #                     # trajfile.save(file_path)
            #                     # traj_paths.append(file_path)
            #                     try:
            #                         u = mda.Universe(topfile, trajfile, topology_format=extension)
            #                         # print("XXX", len(u.atoms), len(u.trajectory), topfile, trajfile)
            #                     except Exception as e:
            #                         #except (ValueError, TypeError, IndexError):
            #                         print(f"!!! {e}")
            #                         #pass

        if logfile_dict:
            if "GROMACS version" in logfile_dict:
                software = "GROMACS "+logfile_dict["GROMACS version"]
                timestep = float(logfile_dict["Input Parameters"]["dt"])
                # nsteps = float(logfile_dict["Input Parameters"]["nsteps"])
                thermostat = logfile_dict["Input Parameters"]["tcoupl"]
                barostat = logfile_dict["Input Parameters"]["pcoupl"]
                temperature = float(logfile_dict["Summary"]["Temperature"])
                # total_steps = float(logfile_dict["Summary"]["total-steps"])
                n_frames = float(logfile_dict["Summary"]["total-frames"])
                md_metadata_dict = {
                    "software": software,
                    "thermostat": thermostat,
                    "timestep": timestep,
                    "barostat": barostat,
                    "temperature": temperature,
                    "n_frames": n_frames
                }

    return md_metadata_dict



def visualise_simulation():
    """
    Display a single frame of the simulation
    """

