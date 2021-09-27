import json
import os
from pathlib import Path

from os import getcwd, listdir
from os.path import isfile, join

this_dir = Path(os.path.dirname(os.path.realpath(__file__)))

def make_base_config(title):
    return {
    "@context": "https://linkedsoftwaredependencies.org/bundles/npm/@ldf/server/^3.0.0/components/context.jsonld",
    "@id": "urn:ldf-server:my",
    "import": "preset-qpf:config-defaults.json",

    "title": f"{title}",

    "datasources": []
    }

def make_datasource(title, filename):
    return {
        "@id": f"urn:ldf-server:my:{filename.replace('.', '')}",
        "@type": "HdtDatasource",
        "datasourceTitle": f"{title}",
        "description": f"{filename[:-4]} with an HDT back-end",
        "datasourcePath": "data",
        "hdtFile": f"/data/{filename}"
        }
        

def write_server_config():
    """
    Write the server config such that it uses all hdt files in
    /hdt as the fragments data source.
    """

    hdt_dir = Path(this_dir.parent / "hdt")
    rdf_dir = Path(this_dir.parent / "rdf")

    with open(Path(rdf_dir / "simple-metadata.json")) as f:
        metadata = json.load(f)

    # make base config
    config = make_base_config(metadata["title"])

    hdt_files = [Path(hdt_dir / f) for f in listdir(hdt_dir) if isfile(join(hdt_dir, f))]
    for hdt_file in hdt_files:
        config["datasources"].append(make_datasource(metadata["title"], hdt_file.name))
    
    # json dumps what we've got
    with open(Path(this_dir.parent / "config.json"), "w") as f:
        json.dump(config, f, indent=2)
        
write_server_config()