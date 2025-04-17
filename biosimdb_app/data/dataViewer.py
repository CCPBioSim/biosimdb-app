#!/usr/bin/env python
from . import bp
from flask import render_template, request, send_file, current_app
# from extensions import mysql
import os
from .inspect_aiida_db import aiida_attributes
from biosimdb_app.utils.db import get_db
import json

from .simulationInspector import fetch_top_traj_files

@bp.route('/BioSimDB', methods=['GET'])
def display_data():
    """
    Display X number of database entries
    """
    # get all the "projects" in the database and render
    query = 'SELECT * FROM `project`'
    records, page, total_pages, sort_column, sort_direction = get_data(query)
    return render_template('data/showdata.html', page_name="/BioSimDB", 
            records=records, page=page, 
            total_pages=total_pages, sort_column=sort_column, 
            sort_direction=sort_direction)

def get_data(query):
    """
    """
    page = request.args.get('page', 1, type=int)
    sort_column = request.args.get('sort_column', '`datetime added`', type=str)
    sort_direction = request.args.get('sort_direction', 'desc', type=str)
    per_page = 10 # number of records per page
    

    # Calculate total count
    # cursor = mysql.connection.cursor()
    db = get_db()
    cursor = db.cursor()
    #query = 'SELECT COUNT(*) AS total_count FROM simulation_details'
    cursor.execute(query)
    #result = cursor.fetchone()
    #total_count = result['total_count'] if result else 0
    result = cursor.fetchall()
    total_count = len(result)

    # Calculate total number of pages
    total_pages = (total_count // per_page) + (1 if total_count % per_page > 0 else 0)

    # Calculate OFFSET
    offset = (page - 1) * per_page
    limit = per_page

    # Retrieve records for the current page
    cursor.execute(f'{query} ORDER BY {sort_column} {sort_direction} LIMIT {offset}, {limit}')
    records = cursor.fetchall()

    # Close the database connection
    db.close()
    return records, page, total_pages, sort_column, sort_direction
   


@bp.route('/search_results/entry/<project_ID>')
def entry_info(project_ID):
    """
    If a particular entry is selected by user, then open entry and provide all 
    info from database for said entry.
    """
    query_projects = f'SELECT * FROM `project` WHERE `project_ID`="{project_ID}"'
    query_sim = f'SELECT * FROM `simulation` WHERE `project_ID`="{project_ID}"'

    db = get_db()
    cursor = db.cursor()
    # cursor.execute(query1)
    # result = cursor.fetchone()
    # simulation_folder_name = result["simulation_folder_name"]

    cursor.execute(query_projects)
    project_records = cursor.fetchall()
    # for k in project_records[0].keys():
    #     if k in ["authors", "citations"]:
    #         print(k, project_records[0][k], json.loads(project_records[0][k]))

    cursor.execute(query_sim)
    sim_records = cursor.fetchall()
    # print(sim_records, len(sim_records))
    if len(sim_records) > 0:
        simulation_ID = sim_records[0]["simulation_ID"]

        # print(sim_records[0]["simulation_folder_name"])
        # for t in sim_records[0].keys():
        #     print("___", t, sim_records[0][t])

        query_top = f'SELECT * FROM topology WHERE simulation_ID="{simulation_ID}"'
        query_traj = f'SELECT * FROM trajectory WHERE simulation_ID="{simulation_ID}"'

        cursor.execute(query_top)
        top_records = cursor.fetchall()

        cursor.execute(query_traj)
        traj_records = cursor.fetchall()
        # print("&&&", json.load(traj_records[0]["single frame coordinates"]))

        m = max(len(sim_records), len(top_records), len(traj_records))
        if len(top_records) < m:
            top_records = (top_records + m * [{}])[:m]
        if len(traj_records) < m:
            traj_records = (traj_records + m * [{}])[:m]

        # get the mda universe from the top and traj files for each record entry
        fetch_top_traj_files(sim_records)

        return render_template('data/entry.html', project_records=project_records, 
                sim_records=sim_records, top_records=top_records, 
                traj_records=traj_records, zip=zip, json=json, enumerate=enumerate,
                #trajectory_name=trajectory_name_db, traj_info=traj_info, 
                #aiida_info=aiida_info
                )

    else:
        return render_template('data/entry.html', project_records=project_records)




    #if len(records) == 1:
    #    records = records[0]

    # aiida_info = ""
    # traj_info = ""
    # trajectories_path = ""
    # for row in records:
    #     simulation_path = os.path.join(current_app.instance_path, simulation_folder_name, "/")
    #     archives_path = os.path.join(current_app.instance_path, "aiida_archives/")
    #     trajectories_path = os.path.join(current_app.instance_path, "simulations/")
    #     # trajectories_path = '/trajectories/'
    #     aiida_archive_name = row['aiida_archive_file']
    #     trajectory_name_db = row['topology_file']
    #     traj_name = trajectory_name_db
    #     # Need to remove forward slashes from traj_name to be arg for flask func
    #     if "/" in trajectory_name_db:
    #         traj_name = traj_name.replace("/", " ")
    #     if aiida_archive_name not in (None, "") and os.path.exists(archives_path+aiida_archive_name):
    #         aiida_info +=f"""
    #         <div class="row">
    #             <div class="col text-end">
    #                 <b>AiiDA</b>
    #             </div>
    #             <div class="col-8">
    #                 <a href="/aiida-archive/{aiida_archive_name}">Explore</a> or
    #                 <a href="/download_archive/{aiida_archive_name}">Download</a>
    #             </div>
    #         </div>
    #         """
    #     if trajectory_name_db and os.path.exists(trajectories_path+trajectory_name_db):
    #         traj_info +=f"""
    #         <div class="row">
    #             <div class="col text-end">
    #                 <b>Simulation Topology & trajectory</b>
    #             </div>
    #             <div class="col-8">
    #                 <a href="/download/{traj_name}">Download</a>
    #             </div>
    #         </div>
    #         """

    db.close()

    # return render_template('data/entry.html', project_records=project_records, 
    #             sim_records=sim_records, top_records=top_records, 
    #             traj_records=traj_records
    #             #trajectory_name=trajectory_name_db, traj_info=traj_info, 
    #             #aiida_info=aiida_info
    #             )


@bp.route('/aiida-archive/<filename>')
def view_aiida_archive(filename):
    """
    If an aiida archive file is included in an entry, then show the data
    provenance graph.
    """
    start = request.args.get('start', 0)
    end = request.args.get('end', 1)
    archives_path = os.path.join(current_app.instance_path, "aiida_archives/")
    start, end = int(start), int(end)
    content, graph, html_content, options, n_processes = aiida_attributes(
        archives_path+filename, start, end
    )
    if end > n_processes:
        end = n_processes-1
    return render_template('data/attributes.html', data=content, #[start:end], 
                    graph=graph, pyvis=html_content, options=options)
    #return html_content


@bp.route('/download/<trajectory_name>')
def download(trajectory_name):
    """
    """
    traj_path1 = os.path.join(current_app.instance_path, "simulations/")
    traj_path = traj_path1+trajectory_name.replace(" ", "/")
    return send_file(traj_path, as_attachment=True)

@bp.route('/download_archive/<archive_name>')
def download_archive(archive_name):
    """
    """
    archive_path1 = os.path.join(current_app.instance_path, "aiida_archives/")
    archive_path = archive_path1+archive_name.replace(" ", "/")
    return send_file(archive_path, as_attachment=True)
