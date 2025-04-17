

This demo application will create an SQLite database that can be used to include 
aiida archive files produced from several aiida plugins 
(aiida -gromacs and -amber presently). 

This database can be used to store and explore archive files and gives a 
taster for how biomolecular MD simulation data provenance can be stored for 
multiple research projects.

To install dependencies into a conda environment:

```console
user@computer:~$ conda create -n biosimdb-app
user@computer:~$ conda activate biosimdb-app
user@computer:~$ pip install .
```

To initate the database the first time you use the application, type the following:

```console
user@computer:~$ cd biosimdb-app
user@computer:~$ flask --app biosimdb_app init-db
```

This will create a biosimdb.sqlite file in the instance folder.

Then, the app can be run with:

```console
user@computer:~$ flask --app biosimdb_app run --debug -p 5001
```

And then visit http://127.0.0.1:5001/ in a local browser to explore the database.

Close the app with ctrl+c.
