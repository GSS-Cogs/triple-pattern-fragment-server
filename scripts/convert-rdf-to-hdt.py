import os
from os import listdir
from os.path import isfile, join
from pathlib import Path

import docker
from docker import DockerClient
from docker.models.containers import Container


this_dir = Path(os.path.dirname(os.path.realpath(__file__)))

def convert_rdf_to_hdt():
    """
    For each dataset:
    * write all individual nt files to a single nt file
    * convert that single nt file to a hdt file
    """

    hdt_dir = Path(this_dir.parent / "hdt")
    hdt_dir.mkdir(exist_ok=True)

    rdf_dir = Path(this_dir.parent / "rdf")

    client: DockerClient = docker.from_env()

    dataset_paths = [Path(rdf_dir / f) for f in listdir(rdf_dir) if not isfile(join(rdf_dir, f))]

    for dataset_dir in dataset_paths:

        # Scoop up the rdf files
        rdf_files = [Path(dataset_dir / f) for f in listdir(dataset_dir) if isfile(join(dataset_dir, f)) and not f.endswith(".json")]

        dataset_nt_out = Path(dataset_dir / "data.nt")

         # Create file as blank
        with open(dataset_nt_out, "w") as f:
                f.write("")

        # Write append all nt files to a single nt file
        # update the data url so we can distinguish from the obs on PMD
        # (as we have to include it to get the reference data)
        with open(dataset_nt_out, "a") as f:
            for rdf_file in rdf_files:
                with open(rdf_file) as f2:
                    f.write(f2.read())

        # Convert the nt file to a hdt file
        for rdf_file in rdf_files:
            container: Container = client.containers.run(
                "rfdhdt/hdt-cpp",
                command = f"rdf2hdt -p -v ./data/rdf/{dataset_dir.name}/data.nt ./data/hdt/{dataset_dir.name}.hdt",
                volumes = {this_dir.parent: {"bind": "/data", "mode": "rw"}},
            )

convert_rdf_to_hdt()