#!/usr/bin/env python
import os
import requests
from . import form_bp
from ..invenio import invenio_bp
from flask import render_template, jsonify, redirect, request, session, current_app, flash
import json
import tempfile
from werkzeug.utils import secure_filename
from MDAnalysis import Universe

from collections.abc import Iterable
from pathlib import Path
import glob
import re
import copy
from datetime import datetime


from data_collections_api.dumpers import Formats, get_loader
from data_collections_api.invenio import InvenioRepository
from data_collections_api.metadata import validate_metadata

from biosimdb_app.metadata.form_metadata import WEBFORM_SCHEMA, DSMD_AUTO_EXTRACT, INVENIO_FORM_EMPTY, DSMD_EMPTY




def create_files_dict(all_files: Iterable[Path | str]) -> dict[str, Path]:
    """
    Save file paths into a dictionary to a format e.g.

    Parameters
    ----------
    all_files : Iterable[Path | str]
        Files to load into dict.

    Returns
    -------
    dict[str, Path]
        Dictionary of file names and file paths.

    Examples
    --------
    .. code-block:: Python

       files_dict = create_files_dict(["my_dir/*.file", "my_dir/example/*.cif"])
       # files_dict = {
       #    "name1.file": "my_dir/name1.file",
       #    "name2.file": "my_dir/name2.file",
       #    "name1.cif": "my_dir/example/name1.cif",
       # }
    """
    files_dict = {}
    for file_str in all_files:
        # expand file_str if using wildcards
        files = glob.glob(file_str)  # noqa: PTH207
        for file in files:
            file_path = Path(file)
            files_dict[file_path.name] = file_path
    return files_dict


def run_record_upload(
    api_url: str,
    api_key: str,
    metadata_path: Path,
    metadata_format: Formats,
    files: Iterable[Path | str],
    community: str,
) -> None:
    """
    Run the uploading of metadata and associated files to an Invenio repository.

    Parameters
    ----------
    api_url : str
        URL of repository.
    api_key : str
        Repository API key.
    metadata_path : Path
        Path to metadata file.
    metadata_format : Formats
        Format of metadata file (json or yaml).
    files : list[Path | str]
        Files to upload.
    community : str
        Community to which files will be uploaded.
    """
    # create repo object
    repository = InvenioRepository(url=api_url, api_key=api_key)

    # open metadata record
    loader = get_loader(metadata_format)
    data = loader(metadata_path)

    draft_id = None

    #validate_metadata(data)

    # convert list of file paths to a dictionary
    files_dict = create_files_dict(files)

    # create an empty draft record in Invenio and retrieve its id
    draft = repository.depositions.create()
    draft_id = draft.get()["id"]

    # add metadata to draft
    repository.depositions.draft(draft_id).update(data)

    # add files to draft
    repository.depositions.draft(draft_id).files.upload(files_dict)

    # bind draft to a community
    repository.depositions.draft(draft_id).bind(community)

    # submit draft for review
    # repository.depositions.draft(draft_id).submit_review()

    return repository, draft_id

def data_collections_upload(metadata_path, files_path):
    """
    Docstring for data_collections_upload
    
    :param metadata_path: Path to data-collections record metadata
    :param files_path: Path to files being uploaded with record
    :param token: token used to access data-collection app
    """
    token = session.get("access_token")
    API_BASE = current_app.config['API_BASE']
    repository, draft_id = run_record_upload(
        api_url=API_BASE, api_key=token, metadata_path=metadata_path, metadata_format="json", files=files_path, community="biosimdb",
    )
    return repository, draft_id


@form_bp.route("/extract_metadata", methods=["POST"])
def extract_metadata():

    i = request.form.get("index")
    if not i:
        return jsonify({"error": "No simulation index provided"}), 400

    topology = request.files.get(f"topology[{i}]")
    trajectories = request.files.getlist(f"trajectory[{i}][]")
    aiida = request.files.get(f"aiida[{i}]")

    result = {}

    if not topology or not trajectories:
        return jsonify({"error": "Simulation files are missing. Please upload files to automatically extract metadata and fill in missing metadata fields manually."}), 400
    
    # Save topology to temporary file
    topo_ext = os.path.splitext(topology.filename)[1]
    topo_file = tempfile.NamedTemporaryFile(delete=False, suffix=topo_ext)
    topology.save(topo_file.name)
    
    # Save all trajectory files to temporary files
    traj_files = []
    for traj in trajectories:
        traj_ext = os.path.splitext(traj.filename)[1]
        temp_traj = tempfile.NamedTemporaryFile(delete=False, suffix=traj_ext)
        traj.save(temp_traj.name)
        traj_files.append(temp_traj.name)

    try:
        # Pass the list of trajectories to MDAnalysis
        u = Universe(topo_file.name, traj_files)

        for field, func in DSMD_AUTO_EXTRACT.items():
            key = f"dsmd[{i}][{field}]"
            if callable(func):
                result[key] = func(u)
            else:
                result[key] = func

        # Clean up temporary files (topology + trajectories)
        topo_file.close()
        for path in traj_files:
            os.unlink(path)
        os.unlink(topo_file.name)

        return jsonify(result)

    except Exception as e:
        # Cleanup in case of error
        topo_file.close()
        for path in traj_files:
            os.unlink(path)
        os.unlink(topo_file.name)
        return jsonify({'error': str(e)}), 500




def submit_form():
    """
    Docstring for submit_form
    """
    token = session.get("access_token")
    API_BASE = current_app.config['API_BASE']
    BASE_URL = current_app.config['BASE_URL']

    ##################################
    # try to submit test data via the data-collections-API as a test
    files = [os.path.join(invenio_bp.root_path, 'test_data/csa.*')]

    # metadata_path = os.path.join(invenio_bp.root_path, 'test_data/record.yaml')
    # run_record_upload(
    #     api_url=API_BASE, api_key=token, metadata_path=metadata_path, metadata_format="yaml", files=files, community="biosimdb",
    # )

    metadata_path = os.path.join(invenio_bp.root_path, 'test_data/record.json')
    run_record_upload(
        api_url=API_BASE, api_key=token, metadata_path=metadata_path, metadata_format="json", files=files, community="biosimdb",
    )
    ##################################


    
    if not token:
        flash(f"Error: {r.status_code} — {r.json()['message']}<br>Please log in before submitting a record.", "danger")
        # FAILURE → return filled form
        return render_template("form/webform2.html",
                                fields=WEBFORM_SCHEMA,
                                form_data=request.form)
    

    # repository, draft_id = data_collections_upload(metadata_path, files_path)

    # if r.status_code == 201:
    #     record_id = r.json()["id"]
    #     record_url = f"{BASE_URL}/uploads/{record_id}"
    #     flash(
    #         f'Record created successfully! '
    #         f'<a href="{record_url}" target="_blank" class="btn btn-sm btn-success ms-2">View Record</a>', "success"
    #     )
    #     # SUCCESS → return blank form
    #     return render_template("form/webform2.html",
    #                             fields=WEBFORM_SCHEMA,
    #                             form_data={})

    # else:
    #     flash(f"Upload failed: {r.status_code} — {r.json()['message']}", "danger")
    #     # FAILURE → return filled form
    #     return render_template("form/webform2.html",
    #                             fields=WEBFORM_SCHEMA,
    #                             form_data=request.form)


def form_to_json(form):
    """
    Convert html form data into json form
    
    :param form: Description
    """
    data = {}
    for key, value in form.items():
        # Split "author[1][given_name]" -> ["author","1","given_name"]
        parts = re.findall(r'\w+', key)

        root = parts[0]
        idx = int(parts[1]) - 1 if len(parts) > 1 else None
        field = parts[2] if len(parts) > 2 else None

        if idx is None:
            data[root] = value
            continue

        data.setdefault(root, [])

        while len(data[root]) <= idx:
            data[root].append({})

        if field:
            data[root][idx][field] = value
        else:
            data[root][idx] = value

    return data

def fill_invenio_metadata(form_data):
    """
    Take the dictionary generated from the webform and populate a blank copy of the invenio dictionary.
    """
    invenio_data = copy.deepcopy(INVENIO_FORM_EMPTY)
    creators = []
    for creator in form_data["creator"]:
        creators.append({
            "affiliations": [{"name": creator["affiliation"]}],
            "identifiers": [{"identifier": creator["identifier"]}],
            "person_or_org": {
                "family_name": creator["family_name"],
                "given_name": creator["given_name"],
                "type": "personal"
            }
        })
    invenio_data["metadata"]["creators"] = creators
    invenio_data["metadata"]["description"] = form_data["simulation"][0]["description"]
    invenio_data["metadata"]["title"] = form_data["simulation"][0]["title"]
    invenio_data["metadata"]["publication_date"] = datetime.today().strftime('%Y-%m-%d')
    invenio_data["custom_fields"]["dsmd"] = form_data["dsmd"]
    # add generated keywords
    # add generated subjects

    return invenio_data


@form_bp.route("/webform2", methods=["GET", "POST"])
def webform2():
    token = session.get("access_token")

    if request.method == "POST":

        errors = {}
        # add function to catch errors in filled out fields here
        # errors = {
        # # "author[1][email]": "Invalid email address",
        # "creator[1][affiliation]": "Invalid affiliation"
        # }
        # print("errors", errors)

        if errors:
            print("ERRORS")
            return render_template("form/webform2.html",
                                    schema=WEBFORM_SCHEMA,
                                    form_data=request.form,
                                    errors=errors)

        if not token:
            print("token")
            print(request.form)
            flash(f"Error: Please log in before submitting a record.", "danger")
            # FAILURE → return filled form
            return render_template("form/webform2.html",
                                    schema=WEBFORM_SCHEMA,
                                    form_data=request.form,
                                    errors=errors)

        json_form = form_to_json(request.form)
        print("******json_form******")
        print(json_form)
        invenio_data = fill_invenio_metadata(json_form)
        # invenio_data = TEST_INVENIO_DATA
        print("******invenio_data******")
        print(invenio_data)


        files = request.files
        # print(files)

        with tempfile.TemporaryDirectory(prefix="biosimdb_") as tmpdir:
            paths = []
            for field in request.files:
                files = request.files.getlist(field)
                for file in files:
                    if file.filename == "":
                        continue
                    filename = secure_filename(file.filename)
                    path = os.path.join(tmpdir, filename)
                    file.save(path)
                    paths.append(path)
                # uploaded_paths[field] = paths

            metadata_path = os.path.join(tmpdir, "metadata.json")

            with open(metadata_path, "w") as f:
                json.dump(invenio_data, f, indent=2)

            print(metadata_path, paths)

            repository, draft_id = data_collections_upload(metadata_path, paths)
            print("repository", repository)
            print("draft_id", draft_id)


        # submit_form() # this works

        # make compatible with what invenio expects
        # submit data via API
        # check responce from API
        if draft_id:
            BASE_URL = current_app.config['BASE_URL']
            record_url = f"{BASE_URL}/uploads/{draft_id}"
            flash(
                f'Record created successfully! '
                f'<a href="{record_url}" target="_blank" class="btn btn-sm btn-success ms-2">View Record</a>', "success"
            )
            return render_template(
                "form/webform2.html",
                schema=WEBFORM_SCHEMA,
                form_data={},
                errors={},
            )
        
        else:
            return render_template("form/webform2.html", schema=WEBFORM_SCHEMA,
            form_data={}, errors=errors)

    return render_template(
        "form/webform2.html",
        schema=WEBFORM_SCHEMA,
        form_data={},
        errors={},
    )