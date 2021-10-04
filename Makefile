
# Build a LDF server using the dataset sources as defined in ./datasets.txt
# deploy it to google cloud run
.PHONY: build-deploy
batch-build-deploy: preclean batch build push-container deploy

# Build a LDF server using the dataset sources as defined in ./datasets.txt
# runs the container locally but does NOT push anything to the cloud
.PHONY: local
local: preclean batch postclean build
	docker run -d -p 5000:5000 data:latest

# Helper to write the ./datasets.txt with the full contents of
# a family as defined by its completed jenkins jobs
.PHONY: datalist
datalist:
	@if [ -z "$(family)" ]; then \
		echo "Aborting. You need to provide a family as defined on jenkins, eg 'make family=ClimateChange datalist'"; \
	exit 1; \
	fi
	pipenv run python3 scripts/populate-datasets-list.py $(family)

# Convert every dataset listed in datasets.txt to hdt
# and write an appropriate ldf server config.
.PHONY: batch
batch: preclean
	rm -f ./config.json
	@for id in $$(cat datasets.txt); do  \
		pipenv run python3 scripts/download-artifacts-from-jenkins-job.py "$$id"; \
	done
	pipenv run python3 scripts/unpack-rdf-artifacts.py
	pipenv run python3 scripts/convert-rdf-to-hdt.py
	pipenv run python3 scripts/write-server-config.py

# Build LDF server image (with the data in it) using the dataset sources as defined in ./datasets.txt
.PHONY: build
build: check-google-project-id
	docker build -t gcr.io/$(GOOGLE_PROJECT_ID)/data:latest -f Dockerfile .

# Push your data:latest image to google cloud run
.PHONY: push-container
push-container:
	docker push gcr.io/$(GOOGLE_PROJECT_ID)/data:latest

# Deploy image as defined on google cloud via cloud run
.PHONY: deploy
deploy: push-container
	gcloud run deploy ldf-trial1 \
 	--image gcr.io/$(GOOGLE_PROJECT_ID)/data:latest \
 	--region $(GOOGLE_PROJECT_REGION) \
	--port 5000 \
 	--platform managed \
 	--memory 4Gi \
	--cpu 4

# Cleanup any lingering resources before processing
.PHONY: preclean
preclean:
	rm -rf ./inputs/*
	rm -rf ./rdf/*
	rm -rf ./hdt/*

# Cleanup any lingering (and not needed to serve) resources after processing
.PHONY: postclean
	rm -rf ./inputs/*
	rm -rf ./rdf/*

# Build server with ONE dataset as provided by job= kwarg and write a server config
.PHONY: hdt-from-jenkins check-hdt-from-jenkins-env check-job-arg check-id-arg
hdt-from-jenkins: check-job-arg check-hdt-from-jenkins-env preclean
	rm -f ./config.json
	pipenv run python3 scripts/download-artifacts-from-jenkins-job.py $(job)
	pipenv run python3 scripts/unpack-rdf-artifacts.py
	pipenv run python3 scripts/convert-rdf-to-hdt.py
	pipenv run python3 scripts/write-server-config.py
	rm -rf ./inputs/*
	rm -rf ./rdf/*
	docker build -t gcr.io/$(GOOGLE_PROJECT_ID)/data:latest -f Dockerfile .

# Make sure the user has provided a job= kwarg to the makefile
.PHONY: check-job-arg
check-job-arg:
	@# Confirm we've been given a url to a jenkins job
	@if [ -z "$(job)" ]; then \
		echo "Aborting. You need to provide a url to a jenkins job we can get artifcts from, eg: "; \
		echo "https://ci.floop.org.uk/job/GSS_data/job/beta.gss-data.org.uk/job/family/job/climate-change/job/BEIS-2005-to-2019-local-authority-carbon-dioxide-CO2-emissions/"; \
		exit 1; \
	fi

# Make sure the user has exported relevant env vars for google cloud
.PHONY: check-google-project-id
check-google-project-id:
ifndef MY_PROJECT_ID
	$(error GOOGLE_PROJECT_ID is undefined)
endif
ifndef GOOGLE_PROJECT_REGION
	$(error GOOGLE_PROJECT_REGION is undefined)
endif

# Make sure jenkins environment variables have been exported
.PHONY: check-hdt-from-jenkins-env
check-hdt-from-jenkins-env:
ifndef JENKINS_API_TOKEN
	$(error JENKINS_API_TOKEN is undefined)
endif
ifndef JENKINS_USER
	$(error JENKINS_USER is undefined)
endif