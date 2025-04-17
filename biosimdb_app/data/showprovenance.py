#!/usr/bin/env python
import os
import sys

# from app import app
from . import bp

from flask import render_template, request, current_app, send_file, redirect, url_for, flash
# from extensions import mysql

import aiida
from aiida import orm, profile_context
from aiida.storage.sqlite_zip.backend import SqliteZipBackend

from werkzeug.utils import secure_filename

# from .inspect_aiida_db import get_qb

import MDAnalysis as mda

@bp.route('/showprovenance', methods=['GET', 'POST'])
def show_provenance_results():
    """
    Read in aiida archive file and return the commands, code, inputs and 
    outputs in string html format.
    """
    file_info = None
    if request.method == "POST":
        #pass
        uploaded_file = request.files.getlist('archive_file')
        # Create a temporary folder to store uploaded files
        temp_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(temp_folder, exist_ok=True)
        for file in uploaded_file:
            if file:
                uploaded_file_name = secure_filename(file.filename)
                file_path = os.path.join(temp_folder, uploaded_file_name)
                file.save(file_path)
                size = os.stat(file_path).st_size
                # file_info = f"{file_path} {round(size/1e+6, 2)} MB"
                # file_info = mimetypes.guess_all_extensions(file_path)

                try:
                    archive_profile = SqliteZipBackend.create_profile(file_path)
                    with profile_context(archive_profile):
                        qb = orm.QueryBuilder()

                except aiida.common.exceptions.CorruptStorage:
                    flash(f"AiiDA archive file: : \"{file_path}\" is unreadable, ensure it is readable by AiiDA before uploading.")
                    return redirect(url_for("data.show_provenance_results"))

                if qb:
                    file_info = show_provenance_text(file_path)
                # Remove the temporary folder and its contents
                os.remove(file_path)
    return render_template('data/showprovenance.html', 
                           page_name="/showprovenance", file_name=file_info)


def show_provenance_text(archive_filepath):
    """For a given loaded aiida profile, get the provenance and convert it 
    into html format string. 

    https://www.w3schools.com/bootstrap5/bootstrap_collapse.php
    """

    #  create a profile instance from the archive path
    archive_profile = SqliteZipBackend.create_profile(archive_filepath)
    all_outputs = f"""
        <br />
        <button class="btn btn-outline-secondary" type="button" data-bs-toggle="collapse" data-bs-target=".multi-collapse" aria-expanded="false" aria-controls="">Toggle All Steps</button>
        <br />
        <br />
        """

    with profile_context(archive_profile):
        qb = orm.QueryBuilder()
        # get all processes and order from oldest to newest
        qb.append(orm.ProcessNode, tag='process')
        qb.order_by({orm.ProcessNode: {"ctime": "asc"}})

        output_pks = {} # save PK of output files and step no.
        for i, entry in enumerate(qb.all(flat=True)):
            # print(i, entry)
            # print(list(entry.inputs))
            # print(list(entry.outputs))
            # print(dir(entry))
            # print(entry.label)
            command = ""
            executable = ""
            for link_triple in entry.get_incoming().all():
                # print("A", link_triple.node)
                # print("B", link_triple.link_type)
                # print("C", link_triple.link_label)
                # print("D", type(link_triple.node))
                if link_triple.link_label == "command":
                    command = link_triple.node.value

            incoming = entry.get_incoming().all_nodes()
            outgoing = entry.get_outgoing().all_nodes()
            input_files = []
            output_files = []
            executable, filepath = None, None
            for inputs in incoming:
                if isinstance(inputs, orm.InstalledCode):
                    executable = inputs.label
                if isinstance(inputs, orm.SinglefileData):
                    # file = open_file(inputs)
                    input_str = inputs.filename
                    # print("* INPUT FILE:", input_str)
                    # print(dir(inputs)) # check attributes for inputs
                    # content = inputs.get_content()
                    chunk = "None"
                    with inputs.open(mode='rb') as source:
                        chunk = source.read(1024)
                        with inputs.as_path() as filepath:
                            filepath = filepath
                            extension = os.path.splitext(inputs.filename)[1].replace('.', '')
                            if extension in ['psf', 'top', 'prmtop', 'parm7', 'pdb', 'ent', 'xpdb', 'pqr', 'gro', 'crd', 'pdbqt', 'dms', 'tpr', 'mol2', 'data', 'lammpsdump', 'xyz', 'txyz', 'arc', 'gms', 'config', 'history', 'xml', 'mmtf', 'gsd', 'minimal', 'itp', 'in', 'fhiaims', 'parmed', 'rdkit', 'openmmtopology', 'openmmapp']:
                                # print("\t*** FILE:", inputs.filename)
                                u = None
                                try:
                                    u = mda.Universe(filepath, topology_format=extension)
                                except:
                                    pass
                                # if u:
                                #     #print(dir(u))
                                #     #print(u.residues, u.atoms)
                                #     try:
                                #         print(u.atoms.positions)
                                #     except:
                                #         pass
                        try:
                            chunk = chunk.decode("utf-8")
                        except:
                            chunk = "None"
                        # lines = source.readlines()
                        # content = lines
                        # size = sys.getsizeof(source)
                    # with inputs.as_path() as filepath:
                    #     with filepath.open(mode='rb') as source:
                    #         content = source
                    if inputs.pk in output_pks:
                        input_str = f"""<div>{inputs.filename, filepath} <-- from <b><a class="text-decoration-none link-dark" href="#STEP{output_pks[inputs.pk]}"><span style = "background-color:#fff6aa">Step {output_pks[inputs.pk]}.</span></a></b></div>
                        <p>{chunk}</p>
                        <div class="col-8">
                        <a class="btn btn-outline-primary" href="/download_node" role="button">Download</a>
                        </div>
                        
                        """
                    input_files.append(input_str)
            for outputs in outgoing:
                if outputs.pk not in output_pks:
                    output_pks[outputs.pk] = i+1 
                if isinstance(outputs, orm.SinglefileData):
                    output_files.append(outputs.filename)

            inputs_str = ""
            for inp in input_files:
                inputs_str+=f'<div style="font-family:\'Courier New\'">{inp}</div>'

            outputs_str = ""
            for out in output_files:
                outputs_str+=f'<div style="font-family:\'Courier New\'">{out}</div>'

            output = f"""
            <ul>
            <a id="STEP{i+1}" class="link-dark text-decoration-none" data-bs-toggle="collapse" href="#step{i+1}" aria-expanded="false" aria-controls="step{i+1}"><b><span style = "background-color:#fff6aa">Step {i+1}.</b></a> <p style="font-family:'Courier New'">{command}</p>
                <ul class="multi-collapse collapse" id="step{i+1}">
                    <!--<div>command:</div>
                    <ul>
                        <div>{command}</div>
                    </ul>-->
                    <div><span style = "background-color:#ffd4aa">code:</div>
                    <ul>
                        <div style="font-family:'Courier New'">{executable}</div>
                    </ul>
                    <div><span style = "background-color:#9effc9">input files:</div>
                    <ul>
                        {inputs_str}
                    </ul>
                    <div><span style = "background-color:#c9f5ff">output files:</div>
                    <ul>
                        {outputs_str}
                    </ul>
                </ul>
            </ul>
            """
            all_outputs += output

    return all_outputs


@bp.route('/download_node')
def download_node():
    """
    """
    file_path = None
    # with input_node.as_path() as filepath:
    #     file_path = filepath
    return send_file(file_path, as_attachment=True)