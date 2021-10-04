
# Triple Pattern Fragment Server

Server and helper scripts to get one or more of our current datasets deployed as/on a triple pattern fragment server.

The basic gist is:

* We convert rdf formatted file(s) into HDT format of **one hdt per dataset** (the various rdf formats that represent "a" dataset get munged into one).
* Build a triple pattern fragment container using the HDT file(s) as the data source(s).
* (Optionally) deploy said container on google cloud.

The makefile will do all the actual work, just be aware of whats its doing.

Note: this is first pass and not productionised in any sense (it won't be fast, don't just dump 40 datasets in).

### Setup

This is **all related to deploying the fragment server to google cloud**. If you're just running one locally for development purposes (or playing) you can ignore this section.

Install gcloud cli, [https://cloud.google.com/sdk/docs/install](https://cloud.google.com/sdk/docs/install)

* Authenticate your machine via `gcloud auth login` (assuming you have sufficiant google cloud permissions to deploy things, if not and you think you should bug Alex/Mike).
* Authenticate your docker client via `gcloud auth configure-docker`

You'll also need to export the following environment variables.

| variable               | description              |
| --------               | ------------------------ |
| GOOGLE_PROJECT_ID      | identifes our google account for want of a better term (ask in slack for this)                         |
| GOOGLE_PROJECT_REGION  | ask in slack for this                         |

### Usage

Check the datasets you want (in the form of jenkins job urls) are in `datasets.txt` then `make`, that'll build and deploy a linked data fragment server with that data.

The last line of output from `make` will give you the url.

**Important:** we're currently using a default image name (will change this at some point) so a naked make will overwrite whatevers currently deployed with whatever you've specified, so use a bit of care and don't do a naked `make` unless that's what your after - for developing/playing see **Local Usage** below.

### Local Usage

You'll need to `make local` then hop over to [http:/localhost:5000/](http:/localhost:5000/) to see your dataset(s) as browsable fragments.

Note: docker will run the server detached (in the background) and will output a big id when you run it. To stop the container when you're done do `docker kill <that big id>`.

If you forget/lose the id then do `docker ps`, copy the id from the start of the line and docker kill that instead.

### Changing Data Sources

If you want to use different datasets then either:

* (a) change the list in `./datasets.txt` and `make` or `make local`
* (b) do `make job=<URL TO JENKINS JOB>`

The latter is more for quickly playing around with a new source but they do the same things under the hood, it's just _1-n_ datasets vs _a_ dataset.

Note 1 - `make job=<job url>` will start up a local container with that data.

Note 2 - only the last successful job will be used, if there's no last succesful job that job url will be ignored.

### Things to know

Still working through this, but at time of writing I'm switching out the base url `http://gss-data.org.uk/data/gss_data/` for `http://gss-data.org.uk/data/gss_fragment_data/`.

Not wedded to it, but doing it for now as a fragment query still needs to make reference to pmd (for reference data) and it'll get really confusing/slow if your pulling identical obs data from multiple places.

If you do want to run queries against your fragment server you'll need a linked data fragment client, see [https://comunica.dev/docs/](https://comunica.dev/docs/).

If you do deploy more datasets as fragments, the first time you hit a dataset will be slow, caching will take care of that on subsequent requests.