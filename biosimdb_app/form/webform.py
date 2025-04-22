#!/usr/bin/env python
from . import form_bp
from flask import render_template, request, flash
from biosimdb_app.utils.db import get_db
import json

from biosimdb_app.data.dataUploader import save_uploaded_files

@form_bp.route('/webform', methods=['GET', 'POST'])
def webform():
    """
    Get data from webform and add it to the sqlite database
    """
    if request.method == "POST":
        user_name = request.form["creator_name"]
        user_email = request.form["creator_email"]
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
