import os
from pathlib import Path

from os import getcwd, listdir
from os.path import isfile, join

import docker
from docker import DockerClient
from docker.models.containers import Container


this_dir = Path(os.path.dirname(os.path.realpath(__file__)))

def convert_rdf_to_hdt():
    """
    Convert each rdf file to a hdt file
    """

    hdt_dir = Path(this_dir.parent / "hdt")
    hdt_dir.mkdir(exist_ok=True)

    rdf_dir = Path(this_dir.parent / "rdf")

    client: DockerClient = docker.from_env()

    # Scoop up the rdf files
    rdf_files = [Path(rdf_dir / f) for f in listdir(rdf_dir) if isfile(join(rdf_dir, f)) and not f.endswith(".json")]

    for rdf_file in rdf_files:
        container: Container = client.containers.run(
            "rfdhdt/hdt-cpp",
            command = f"rdf2hdt -f turtle -p -v ./data/rdf/{rdf_file.name} ./data/hdt/{rdf_file.name}.hdt",
            volumes = {this_dir.parent: {"bind": "/data", "mode": "rw"}},
        )

    #docker run -it --rm -v "$(pwd)":/data rfdhdt/hdt-cpp rdf2hdt -f turtle -p ./data/rdf/local-authority-code.ttl ./data/out.hdt

convert_rdf_to_hdt()