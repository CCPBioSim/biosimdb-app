#!/usr/bin/env python
from zipfile import ZipFile
from datetime import datetime
import pytz
import os
import sys
from flask import request, send_file, current_app, flash, redirect, url_for

import aiida
from aiida import orm, profile_context
from aiida.storage.sqlite_zip.backend import SqliteZipBackend

import MDAnalysis as mda

from biosimdb_app.data.simulationParser import extract_from_mda_universe, extract_from_aiida_archive #, get_protein_seq

def get_UC_time():
    """
    Get current datetime
    """
    tz = pytz.timezone('UTC')
    now = datetime.now(tz=tz)
    return now.strftime("%Y_%m_%d_%H_%M_%S")


def save_uploaded_files(db, cursor, project_ID):
    """
    Uploaded simulation data is zipped and saved in a zip file named by the
    current datetime. Append the current datetime onto the aiida file if
    it has been uploaded by user.
    """
    # Create a temporary folder to store uploaded files
    temp_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(temp_folder, exist_ok=True)
    # Create directories for simulation files
    main_folder = current_app.config['DATA_FOLDER']
    os.makedirs(main_folder, exist_ok=True)
    # Get the current date and time, will use it as folder name
    date = get_UC_time()


    for i in range(1,6):
        # print(i)
        top_file = request.files.getlist(f'topology_file{i}[]')
        traj_files = request.files.getlist(f'trajectory_file{i}[]')
        aiida_file = request.files.getlist(f'aiida_archive_file{i}[]')

        # print("AA", len(top_file), len(traj_files), len(aiida_file))

        entry_folder = os.path.join(main_folder, f"{date}_entry{i}")
        mda_u_dict, md_metadata_dict = None, None

        if (len(top_file) == 1 and top_file[0].filename != '' and 
            len(traj_files) > 0 and traj_files[0].filename != ''):
            #temp_folder2 = os.path.join(temp_folder, entry_folder)
            #os.makedirs(temp_folder2, exist_ok=True)
            top_file_paths, top_file_names = move_to_temp_folder(top_file, temp_folder)
            traj_file_paths, traj_file_names = move_to_temp_folder(traj_files, temp_folder)
            extension = os.path.splitext(top_file[0].filename)[1].replace('.', '')
            # u = mda.Universe(top_file_paths[0], traj_file_paths, topology_format=extension)
            try:
                u = mda.Universe(top_file_paths[0], traj_file_paths, topology_format=extension)
            except (ValueError, TypeError):
                flash(f"Topology: \"{', '.join(top_file_names)}\" and trajectory: \"{', '.join(traj_file_names)}\" for entry {i}, are unreadable, ensure they are readable in MDAnalysis before uploading.")
                return redirect(url_for("form.webform"))
            if u:
                # get_protein_seq(u)
                upload_top_traj(top_file, traj_files, entry_folder)
                mda_u_dict = extract_from_mda_universe(u)

            # Remove the temporary folder and its contents
            # for file_paths in top_file_paths+traj_file_paths:
                # os.remove(file_paths)
        if len(aiida_file) == 1 and aiida_file[0].filename != '':
            aiida_file_paths, aiida_file_names = move_to_temp_folder(aiida_file, temp_folder)
            # print("BBB", top_file, traj_files, aiida_file)
            try:
                archive_profile = SqliteZipBackend.create_profile(aiida_file_paths[0])
                with profile_context(archive_profile):
                    qb = orm.QueryBuilder()
            except aiida.common.exceptions.CorruptStorage:
                flash(f"AiiDA archive file: : \"{', '.join(aiida_file_names)}\" for entry {i}. is unreadable, ensure it is readable by AiiDA before uploading.")
                return redirect(url_for("form.webform"))
            if qb:
                # print("DDD", top_file, traj_files, aiida_file)
                upload_aiida_archive(aiida_file, entry_folder)
                md_metadata_dict = extract_from_aiida_archive(aiida_file_paths[0])
                # print("SSS", md_metadata_dict)

        # entry one always has file lengths as one, so have to treat it differently
        # to all other entries
        # skip entries that are empty, not sure if there is a better way to do this
        if i > 1:
            if len(top_file) == 0 and len(traj_files) == 0 and len(aiida_file) == 0:
                continue
                #flash(f"No files uploaded for entry {i}.")
                #return redirect(url_for("form.webform"))
        else:
            if top_file[0].filename == '' and traj_files[0].filename == '' and aiida_file[0].filename == '':
                continue

        software, thermostat, timestep, barostat, temperature, n_frames = None, None, None, None, None, None

        # print("XXX", mda_u_dict.keys())
        # print("YYY", md_metadata_dict.keys())
        if md_metadata_dict:
            software = md_metadata_dict["software"]
            thermostat = md_metadata_dict["thermostat"]
            timestep = md_metadata_dict["timestep"]
            barostat = md_metadata_dict["barostat"]
            temperature = md_metadata_dict["temperature"]
            n_frames = md_metadata_dict["n_frames"]

        query_sim = f"""INSERT INTO simulation 
        (`project_ID`, `software`, `thermostat`, `timestep`, `barostat`, `temperature`, `number of frames`, `simulation directory`) 
        VALUES (?,?,?,?,?,?,?,?)"""
        cursor.execute(query_sim, (project_ID, software, thermostat, timestep, barostat, temperature, n_frames, entry_folder))
        db.commit()

        simulation_ID = get_simulation_ID(cursor, project_ID)
        # print("sim_ID", simulation_ID, entry_folder, md_metadata_dict)

        if mda_u_dict:
            molecules_list = mda_u_dict["resnames"]
            atoms_list = mda_u_dict["atomnames"]
            masses_list = mda_u_dict["atom_masses"]
            n_atoms = mda_u_dict["n_atoms"]
            n_frames = mda_u_dict["n_frames"]
            single_frame_coordinates = mda_u_dict["single_frame_positions"]
            single_frame_dimensions = mda_u_dict["single_frame_dimensions"]
            simulation_time = mda_u_dict["simulation_time"]
            time_between_snapshots = mda_u_dict["time_between_snapshots"]
            charges_list = mda_u_dict["charges"]
            system_charge = mda_u_dict["system_charge"]

            query_top = f"""INSERT INTO topology 
            (`simulation_ID`, `atoms list`, `masses list`, `molecules list`, `charges list`, `system charge`) 
            VALUES (?,?,?,?,?,?)"""
            cursor.execute(query_top, (simulation_ID, atoms_list, masses_list, molecules_list, charges_list, system_charge))
            db.commit()

            query_top = f"""INSERT INTO trajectory 
            (`simulation_ID`, `number of atoms`, `number of frames`, `time between snapshots`, `single frame coordinates`, `single frame dimensions`) 
            VALUES (?,?,?,?,?,?)"""
            cursor.execute(query_top, (simulation_ID, n_atoms, n_frames, time_between_snapshots, single_frame_coordinates, single_frame_dimensions))
            db.commit()

    # db.close()



def get_simulation_ID(cursor, project_ID):
    """
    Find if email is already in the database
    """
    query = f'SELECT `simulation_ID` FROM `simulation` WHERE `project_ID`="{project_ID}"'
    cursor.execute(query)
    result = cursor.fetchone()
    simulation_ID = result["simulation_ID"]
    return simulation_ID


def move_to_temp_folder(uploaded_files, temp_folder):
    """
    Move uploaded files to a temporary folder first
    """
    file_paths, file_names = [], []
    for file in uploaded_files:
        if file:
            file_path = os.path.join(temp_folder, file.filename)
            file.save(file_path)
            # size = os.stat(file_path).st_size
            # print("size", size)
            if file_path not in file_paths:
                file_paths.append(file_path)  
                file_names.append(file.filename)  
    return file_paths, file_names

def zip_multiple_trajectories(file_paths, entry_folder):
    """
    If multiple trajectory files are uploaded for a given simulation entry, 
    then zip all these files together
    """
    zip_filename = f"trajectory.zip"
    zip_path_traj = os.path.join(entry_folder, zip_filename)
    with ZipFile(zip_path_traj, 'w') as zip:
        for file_path in file_paths:
            zip.write(file_path, os.path.basename(file_path))
    send_file(zip_path_traj, as_attachment=True)


def upload_top_traj(top_file, traj_files, entry_folder):
    """
    Upload the topology and trajectory to database dir
    """
    os.makedirs(entry_folder, exist_ok=True)
    if len(traj_files) > 1:
        zip_multiple_trajectories(traj_files, entry_folder)
    if len(traj_files) == 1:
        upload_single_file(traj_files[0], "trajectory", traj_files[0].filename, entry_folder)
    if len(top_file) == 1:
        upload_single_file(top_file[0], "topology", top_file[0].filename, entry_folder)


def upload_aiida_archive(aiida_file, entry_folder):
    """
    Upload aiida file
    """
    upload_single_file(aiida_file[0], "aiida_archive", aiida_file[0].filename, entry_folder)


def upload_single_file(file, new_file_name, current_file_name, destination_folder):
    """
    Upload single file to relevant folder
    """
    # Determine file length (optional, for logging)
    file.seek(0, os.SEEK_END)
    file_length = file.tell()
    print("XXXX", file.filename, file_length)

    # Reset cursor before saving
    file.seek(0)

    # Make sure destination exists
    os.makedirs(destination_folder, exist_ok=True)

    # Build final file name
    dotextension = os.path.splitext(current_file_name)[1]
    new_file_name = new_file_name + dotextension
    new_file_path = os.path.join(destination_folder, new_file_name)

    # Save file
    file.save(new_file_path)

    # Check saved size
    size = os.stat(new_file_path).st_size
    print("XXXX2", file.filename, size)

    return None, None, None
