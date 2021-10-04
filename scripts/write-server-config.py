import json
import os
from os import listdir
from os.path import isfile, join
from pathlib import Path

from unidecode import unidecode

this_dir = Path(os.path.dirname(os.path.realpath(__file__)))

def make_base_config():

    return {
    "@context": "https://linkedsoftwaredependencies.org/bundles/npm/@ldf/server/^3.0.0/components/context.jsonld",
    "@id": "urn:ldf-server:my",
    "import": "preset-qpf:config-defaults.json",

    "title": f"Linked data fragment server",
    "datasources": []
    }


def define_data_source(title, dataset_id, description):
    return {
        "@id": f"urn:ldf-server:my:{dataset_id}",
        "@type": "HdtDatasource",
        "datasourceTitle": f"{title}",
        "description": f"{description}",
        "datasourcePath": f"{dataset_id}",
        "hdtFile": f"/usr/app/data/{dataset_id}.hdt"
        }


def write_server_config():
    """
    Write the server config such that it uses all hdt files in
    /hdt as the fragments data source.
    """

    rdf_dir = Path(this_dir.parent / "rdf")
    config = make_base_config()

    dataset_paths = [Path(rdf_dir / f) for f in listdir(rdf_dir) if not isfile(join(rdf_dir, f))]

    for dataset_dir in dataset_paths:

        try:
            with open(f'{str(dataset_dir.absolute()).replace("/hdt/", "rdf")}/simple-metadata.json') as f:
                metadata = json.load(f)
            config["datasources"].append(define_data_source(metadata["title"], metadata["dataset_id"], metadata["description"]))
        except FileNotFoundError:
            # No metadata means no data, pipeline has never succesfully run
            continue

    # json dumps what we've got
    with open(Path(this_dir.parent / "config.json"), "w") as f:
        json.dump(config, f, indent=2)
            
write_server_config()