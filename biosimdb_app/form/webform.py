#!/usr/bin/env python
import os
import copy
from . import form_bp
from flask import render_template, request, flash, jsonify
from biosimdb_app.utils.db import get_db
import json
import tempfile
from MDAnalysis import Universe

from biosimdb_app.data.dataUploader import save_uploaded_files
from biosimdb_app.metadata.dsmd_templates import grouped_metadata_template
from biosimdb_app.data.simulationInspector import get_protein_seq

@form_bp.route('/webform', methods=['GET', 'POST'])
def webform():
    """
    Get data from webform and add it to the sqlite database
    """
    if request.method == "POST":
        user_name = request.form["creator_name"]
        user_email = request.form["creator_email"]
        # TO-DO: add institution to database
        user_institution = request.form["creator_institution"]
        # TO-DO: add other authors institution into webform and db
        sim_authors1 = request.form.getlist('author_name[]')
        sim_authors = json.dumps([user_name]+sim_authors1) # sqlite does not accept lists as inputs
        sim_system = request.form["sim_title"]
        sim_description = request.form["sim_description"]
        sim_refs1 = request.form.getlist("citation_name[]")
        sim_refs = json.dumps(sim_refs1) # sqlite does not accept lists as inputs

        # get the sqlite database
        db = get_db()
        cursor = db.cursor()

        # check if email already exists
        creator_ID = check_email_existence(cursor, user_email)
        if creator_ID:
            # If user already exists
            query = f"""INSERT INTO project 
            (`creator_ID`, `title`, `abstract`, `authors`, `citations`) 
            VALUES 
            (?,?,?,?,?)"""
            cursor.execute(query, (creator_ID, sim_system, 
                    sim_description, sim_authors, sim_refs))
        else:
            # create a new user if email address not in database
            query_email = f"""INSERT INTO creator 
            (`creator`, `email`) VALUES(?,?)"""
            cursor.execute(query_email, (user_name, user_email))
            db.commit()

            query = f"""INSERT INTO project 
            (`creator_ID`, `title`, `abstract`, `authors`, `citations`) 
            VALUES (LAST_INSERT_ROWID(),?,?,?,?)"""
            cursor.execute(query, (sim_system, 
                    sim_description, sim_authors, sim_refs))
        
        db.commit()

        # get the creator_ID, this time it should be created
        creator_ID = check_email_existence(cursor, user_email)
        # find the last uploaded project for the creator
        project_ID = get_project_ID(cursor, creator_ID)

        # Save the uploaded files to the sqlite database
        save_uploaded_files(db, cursor, project_ID) #save uploaded files

        # Close the database connection
        db.close()

        # Notify uploader the project has been added to the database
        flash(f"Submission entered into database.")

    return render_template('form/webform.html')


def check_email_existence(cursor, email):
    """
    Find if email is already in the database
    """
    # get the email for a given creator
    query = f'SELECT `creator_ID` FROM `creator` WHERE `email`="{email}"'
    cursor.execute(query)
    result = cursor.fetchone()
    creator_ID = None
    if result != None:
        creator_ID = result["creator_ID"]
    return creator_ID


def get_project_ID(cursor, creator_ID):
    """
    Find the project ID belonging to a given creator ID
    """
    # get last entry in project table
    query = f'SELECT `project_ID` FROM `project` WHERE `creator_ID`="{creator_ID}" ORDER BY `project_ID` DESC LIMIT 1'
    cursor.execute(query)
    result = cursor.fetchone()
    project_ID = result["project_ID"]
    return project_ID


@form_bp.route('/parse-metadata', methods=['POST'])
def parse_metadata():
    topo = request.files.get('topology')
    traj = request.files.get('trajectory')

    # biosimdb_metadata_template_empty = biosimdb_metadata_template.copy()
    biosimdb_metadata_template_empty = copy.deepcopy(grouped_metadata_template)

    # Just return the empty metadata fields if no files are uploaded
    if not topo or not traj:
        biosimdb_metadata_template_empty["alert"] = "Simulation files are missing. Please upload files to automatically extract metadata or fill in metadata fields manually."
        return jsonify(biosimdb_metadata_template_empty)
    
    topo_ext = os.path.splitext(topo.filename)[1]
    traj_ext = os.path.splitext(traj.filename)[1]

    with tempfile.NamedTemporaryFile(delete=False, suffix=topo_ext) as topo_file, \
         tempfile.NamedTemporaryFile(delete=False, suffix=traj_ext) as traj_file:

        topo.save(topo_file.name)
        traj.save(traj_file.name)

        try:
            u = Universe(topo_file.name, traj_file.name)
            biosimdb_metadata_template = extract_simulation_metadata(u, 
                                    biosimdb_metadata_template_empty)


            return jsonify(biosimdb_metadata_template)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        

def extract_simulation_metadata(u, biosimdb_metadata_template):
    """
    Extract simulation metadata from MDAnalysis universe and fill in the 
    associated metadata dictionary
    """
    atoms = u.atoms
    trajectory = u.trajectory

    n_atoms = len(atoms)
    n_residues = len(u.residues)
    n_frames = len(trajectory)
    time_step = trajectory.dt if hasattr(trajectory, 'dt') else None
    total_time = time_step * n_frames if time_step else None

    box = trajectory.ts.dimensions if hasattr(trajectory.ts, 'dimensions') else None
    box_str = f"{box[0]:.1f} x {box[1]:.1f} x {box[2]:.1f} Å" if box is not None else ""
    box_str_angles = f"alpha: {box[3]:.1f}, beta: {box[4]:.1f}, gamma: {box[5]:.1f} degrees" if box is not None and len(box) == 6 else ""
    
    # get the sequence of the proteins in the system
    sequence = get_protein_seq(u)
    sequence = str(sequence.seq) if sequence else ""

    # populate the metadata template
    biosimdb_metadata_template["1_system_details"]["title"] = f"Simulation with {n_atoms} atoms"
    biosimdb_metadata_template["1_system_details"]["description"] = f"Trajectory has {n_frames} frames and {n_residues} residues."
    biosimdb_metadata_template["2_simulation_settings"]["framestep"] = f"{time_step:.2f} ps" if time_step else ""
    biosimdb_metadata_template["2_simulation_settings"]["total_time"] = f"{total_time:.2f} ps" if total_time else ""
    biosimdb_metadata_template["4_box_properties"]["box_dimensions"] = box_str
    biosimdb_metadata_template["4_box_properties"]["box_angles"] = box_str_angles
    biosimdb_metadata_template["1_system_details"]["atom_count"] = n_atoms
    biosimdb_metadata_template["1_system_details"]["molecule_count"] = n_residues
    biosimdb_metadata_template["1_system_details"]["frame_count"] = n_frames
    biosimdb_metadata_template["1_system_details"]["protein_sequences"] = sequence

    return biosimdb_metadata_template