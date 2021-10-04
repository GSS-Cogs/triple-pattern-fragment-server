import json
import os
from os import listdir
from os.path import isfile, join
from pathlib import Path
import re
import shutil

import gzip
from rdflib import Dataset, Graph
from unidecode import unidecode

this_dir = Path(os.path.dirname(os.path.realpath(__file__)))

# lifted from: https://github.com/GSS-Cogs/gss-utils/blob/d1d6ec63644968087a9cb631a66763bf390a5c7d/gssutils/utils.py#L12
def pathify(label):
    """
      Convert a label into something that can be used in a URI path segment.
    """
    return re.sub(r'-$', '',
                  re.sub(r'-+', '-',
                         re.sub(r'[^\w/]', '-', unidecode(label).lower())))

def unpack_rdf_artifacts():
    """
    Dump all the rdf artifacts in whatever format out as ntriples.

    This is purely so we can mash it all into a single file (and convert to hdt) 
    later without having to worry about eg mangling ttl prefixes.
    """

    # Get a list of the artifacts
    this_dir = Path(os.path.dirname(os.path.realpath(__file__)))
    input_dir = Path(this_dir.parent / "inputs")
    rdf_dir = Path(this_dir.parent / "rdf")
    rdf_dir.mkdir(exist_ok=True)

    # Each sub directory in inputs, represents a single rdf dataset

    dataset_paths = [Path(input_dir / f) for f in listdir(input_dir) if not isfile(join(input_dir, f))]

    for dataset_in_dir in dataset_paths:

        dataset_out_dir = Path(rdf_dir / dataset_in_dir.name)
        dataset_out_dir.mkdir()

        artifacts = [Path(dataset_in_dir / f) for f in listdir(dataset_in_dir) if isfile(join(dataset_in_dir, f))]

        # Trig first, we need the title of the dataset for the path
        for artifact in artifacts:

            if artifact.name.endswith(".trig"):
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
                    'http://purl.org/dc/terms/title',
                    'http://purl.org/dc/terms/description'
                    ]

                # We're just after the title of the dataset
                # You could take it from the jenkins job url but im not sure I trust it.
                title_found = False
                for s, p, o, _ in d.quads((None, None, None, None)):
                    g.add((s, p, o)) # add every triple from d to g
                    if str(p) in fields_wanted and not title_found:
                        fieldname = str(p).split("#")[1] if "#" in str(p) else str(p).split("/")[-1]
                        
                        # Only take first example of each
                        if fieldname not in metadata:
                            metadata[fieldname] = o

                metadata["dataset_id"] = dataset_in_dir.name
                with open(f"{dataset_out_dir}/simple-metadata.json", "w") as f:
                    json.dump(metadata, f)
                g.serialize(destination=f"{dataset_out_dir}/{artifact.name}.nt", format="nt")

            # If it's already ttl, just serialise it as n triples
            elif artifact.name.endswith(".ttl"):

                # then write it as n-triples
                g = Graph()
                g.parse(artifact)
                g.serialize(destination=f"{dataset_out_dir}/{artifact.name}.nt", format="nt")

            # Case 2: It's zipped up tll, unzip it then serialise to ntriples
            elif artifact.name.endswith(".ttl.gz"):
                with gzip.open(artifact, 'rb') as f_in:
                    with open(Path(dataset_in_dir / artifact.name[:-3]), 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)

                # then write it as n-triples
                g = Graph()
                g.parse(Path(dataset_in_dir / artifact.name[:-3]))
                g.serialize(destination=f"{dataset_out_dir}/{artifact.name}.nt", format="nt")

            # Case 3: rogue input
            else:
                raise ValueError(f'No handling for file {artifact}, should this be here?')

unpack_rdf_artifacts()