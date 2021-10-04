
import os
from pathlib import Path
import sys

import requests

this_dir = Path(os.path.dirname(os.path.realpath(__file__)))
datasets_list = Path(this_dir.parent / "datasets.txt")
if not datasets_list.exists():
    raise Exception('No datasets.txt file found in repo')

def populate_datasets_list(family):
    """
    Given a valiud family name from the jenkins server, create a ../datasets.txt
    file listing all the pipelines.
    """

    jobs_url = f'https://ci.floop.org.uk/job/GSS_data/job/beta.gss-data.org.uk/job/family/job/{family}/api/json'
    r = requests.get(jobs_url)
    if not r.ok:
        raise Exception(f'Failed to get Jenkins family jobs url of {jobs_url}, with status code {r.status_code}')

    job_urls = [x["url"] for x in r.json()["jobs"] if x["_class"] == "org.jenkinsci.plugins.workflow.job.WorkflowJob"]
    with open(datasets_list, 'w') as f:
        for job_url in job_urls:
            f.write(job_url + "\n")

populate_datasets_list(sys.argv[1])