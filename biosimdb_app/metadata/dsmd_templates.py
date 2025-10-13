"""
Grouped BioSimDB metadata can be played around with, invenio metadata needs to be approved before changed
"""

grouped_metadata_template = {
    "1_system_details": {
        "title": "",
        "description": "",
        "atom_count": "",
        "molecule_count": "",
        "frame_count": "",
        "protein_sequences": [""],
        "membrane": "",
        "ligands": [""],
        "solvent": "",
        "solution_acidity": ""
    },
    "2_simulation_settings": {
        "timestep": "",
        "framestep": "",
        "total_time": "",
        "temperature": "",
        "temperature_coupling": "",
        "pressure": "",
        "pressure_coupling": "",
        "ensemble": "",
        "thermostat": "",
        "barostat": "",
        "wall_time": ""
    },
    "3_methods": {
        "simulation_method": "",
        "electrostatics_method": "",
        "constraint_algorithm": "",
        "minimisation_algorithm": "",
        "long_range_cutoff": ""
    },
    "4_box_properties": {
        "box_type": "",
        "box_dimensions": "",
        "box_angles": "",
        "periodic_boundary_conditions": ""
    },
    "5_files_and_formats": {
        "software": "",
        "software_version": "",
        "molecular_model": "",
        "force_fields": [""],
        "experimental_structures": [""],
        "topology_size": "",
        "trajectories": [""],
        "trajectory_sizes": [""]
    },
    "6_simulation_metrics": {
        "average_kinetic_energy": "",
        "average_potential_energy": "",
        "average_temperature": "",
        "average_pressure": "",
        "average_volume": "",
    }
}


invenio_metadata_template = {
                "software": "",
                "software_version": "",
                "molecular_model": "",
                "simulation_method": "",
                "timestep": "",
                "framestep": "",
                "length": "",
                "temperature": "",
                "pressure": "",
                "ensemble": "",
                "box_type": "",
                "trajectories": "",
                "force_fields": "",
                "experimental_structures": "",
                "pH": "",
                "membrane": "",
                "ligands": "",
                "sequences": "",
                "average_energy": "",
                "box_dimensions": "",
                "long_range_cutoff": "",
                "thermostat": "",
                "barostat": "",
                "atom_count": "",
                "wall_time": ""
            }