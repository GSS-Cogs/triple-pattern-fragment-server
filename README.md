
# Triple Pattern Fragments

Server and helper scripts to get one of our current datasets depoyed as/on a triple pattern fragment server.

The basic gist is:

* We convert things of an rdf like format (csvw for now, though whatever should work) into HDT format.
* Build a triple pattern fragment container using that HDT file as its data source.
* Deploy said container to a serverless endpoint on google cloud.

### Usage

Depends on how you're getting the data in. The initial scenario is take if from the jenkins arifacts so 

`make job=https://ci.floop.org.uk/job/GSS_data/job/beta.gss-data.org.uk/job/family/job/climate-change/job/BEIS-2005-to-2019-local-authority-carbon-dioxide-CO2-emissions/`

Will build and deploy a linked data fragment endpoint/server for the dataset `BEIS-2005-to-2019-local-authority-carbon-dioxide-CO2-emissions` using whatever csvw arifacts make up the last successful job.

From here I'll touch on what the different stages of the makefile do.

### Stage: Create a HDT file.

Lots of different ways you could do this so I'm expecting these options to grow.

Regardless of the flavour you pick they'll all do the same thing anyway - dump a `data.hdt` file into `./hdt` so the
fragment server can build on/around it.


#### 1.) From the artifacts of an existing data pipeline.

The mvp "just get it working" option.

`make job=<url to jenkins job> hdt-from-jenkins`

Example:

`make job=https://ci.floop.org.uk/job/GSS_data/job/beta.gss-data.org.uk/job/family/job/climate-change/job/BEIS-2005-to-2019-local-authority-carbon-dioxide-CO2-emissions/ hdt-from-jenkins`