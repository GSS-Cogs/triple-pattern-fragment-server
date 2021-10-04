"""
Client scipt that takes an argument - a url to jenkins job - and dumps all the rdf
files (.trig, .ttl, .ttl.gz) into an ../inputs/{dataset_name_path_segment} directory.
"""

import os
from pathlib import Path
import sys

import requests

this_dir = Path(os.path.dirname(os.path.realpath(__file__)))

class JenkinsClient:
    """
    Simple client for getting stuff from Jenkins
    """

    def __init__(self, output_path: Path = Path(this_dir.parent / "inputs")):

        api_token = os.environ.get("JENKINS_API_TOKEN", None)
        assert api_token, 'Aborting. You need to have exported the env var JENKINS_API_TOKEN'

        username = os.environ.get("JENKINS_USER", None)
        assert username, 'Aborting. You need to have exported the env var JENKINS_USER'

        self.api_token = api_token
        self.username = username
        self.output_path = output_path

        self.output_path.mkdir(exist_ok=True)


    def _ensure_dataset_path(self, job_url):
        """
        Given the wanted dataset path (typically the pathified name of the dataset),
        (a) store it on self.
        (b) make sure an {self.output_path}/{dataset_path} sub directory exists

        Note: self.output_path by default is ../inputs
        """
        dataset_path = job_url.rstrip("/").split("/")[-1]
        self.dataset_path = Path(self.output_path / dataset_path)
        self.dataset_path.mkdir(exist_ok=True)


    def dump_artifacts_locally(self, job_url: str):
        """
        artifacts from jenkins job api, example:
        https://ci.floop.org.uk/job/GSS_data/job/beta.gss-data.org.uk/job/family/job/climate-change/job/BEIS-2005-to-2019-local-authority-carbon-dioxide-CO2-emissions/lastStableBuild/api/json?
        """
        self._ensure_dataset_path(job_url)
        rest_url = f'{job_url}lastStableBuild/api/json?'

        r = requests.get(rest_url)
        if not r.ok:

            # If its a 404, there's typically no last successful build
            if r.status_code == 404:
                print(f'404 for url {rest_url}, ignoring probable never built.')
                return
            raise Exception(f'Failed to get {rest_url} with status code {r.status_code}')

        job_dict = r.json()

        self._ensure_dataset_path(job_url)

        # Download the artifacts
        for artifact in job_dict["artifacts"]:
            filename = artifact["fileName"]
            if not filename.endswith((".ttl.gz", ".ttl", ".trig")):
                continue
            url = f'{job_url}/lastStableBuild/artifact/{artifact["relativePath"]}'
            self._download_artifact(filename, url)

    def _download_artifact(self, filename, url):
        """
        Download a single artifact to the specified output directory.
        Always treat as a stream in case of larger source data files.
        """
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(Path(self.dataset_path / filename), 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    f.write(chunk)

client = JenkinsClient()
client.dump_artifacts_locally(sys.argv[1])  # sys.argv[1] == "job" arg, typically from the makefile
