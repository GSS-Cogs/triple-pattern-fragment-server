import os
from pathlib import Path

import json

from os import getcwd, listdir
from os.path import isfile, join
import shutil

import gzip

from rdflib import Dataset, Graph

this_dir = Path(os.path.dirname(os.path.realpath(__file__)))


def unpack_rdf_artifacts():
    """
    As it says, unzip where ttl is gzipped, copy over where its not.
    """

    # Get a list of the artifacts
    this_dir = Path(os.path.dirname(os.path.realpath(__file__)))
    input_dir = Path(this_dir.parent / "inputs")
    rdf_dir = Path(this_dir.parent / "rdf")
    artifacts = [Path(input_dir / f) for f in listdir(input_dir) if isfile(join(input_dir, f))]

    # Make sure ./{parent}/rdf dir exists
    rdf_dir.mkdir(exist_ok=True)

    for artifact in artifacts:

        # Case 1: It's already ttl, just move it over
        if artifact.name.endswith(".ttl"):
            shutil.copyfile(artifact, Path(rdf_dir / artifact.name))

        # Case 2: It's zipped up tll, unzip it over
        elif artifact.name.endswith(".ttl.gz"):
            with gzip.open(artifact, 'rb') as f_in:
                # note: the [:-3] is just clipping the .gz off the artifact filename
                with open(Path(rdf_dir, artifact.name[:-3]), 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

        # Case 3: It's a trig, dump it over to ttl in keeping with everything else
        elif artifact.name.endswith(".trig"):
            """
            A trig file is a Dataset (thing of multiple graphs) that just so happens
            to contain 1 graph - the metadata graph.

            So we're gonna pull out g (graph) from d (dataset) then serialize g.

            While we're in here, we'll also make a simple metadata json to
            fill out the server config later without having to reparse the input
            files.
            """
            d = Dataset()
            g = Graph()
            d.parse(artifact)

            metadata = {}
            fields_wanted = [
                'http://purl.org/dc/terms/title'
                ]
            for s, p, o, _ in d.quads((None, None, None, None)):
                g.add((s, p, o)) # add every triple from d to g
                if str(p) in fields_wanted:
                    fieldname = str(p).split("#")[1] if "#" in str(p) else str(p).split("/")[-1]
                    metadata[fieldname] = o
                    break # we only want the first occurance
            with open(f"{rdf_dir}/simple-metadata.json", "w") as f:
                json.dump(metadata, f)
            g.serialize(destination=f"{rdf_dir}/{artifact.name}.ttl")

        # Case 3: rogue input
        else:
            raise ValueError(f'No handling for file {artifact}, should this be here?')

unpack_rdf_artifacts()