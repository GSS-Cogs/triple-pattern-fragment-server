
# All the things
.PHONY: build hdt-from-jenkins check-hdt-from-jenkins-env
everything: hdt-from-jenkins build

# Build the docker file using the current local resourcves
.PHONY: build
build:
	docker build .
	
# Take some csvw andtrig jenkins artifacts, dump all the resulting rdf into a hdt file.
.PHONY: hdt-from-jenkins check-hdt-from-jenkins-env
hdt-from-jenkins: check-hdt-from-jenkins-env
	@# Confirm we've been given a url to a jenkins job
	@if [ -z "$(job)" ]; then \
		echo "Aborting. You need to provide a url to a jenkins job we can get artifcts from, eg: "; \
		echo "https://ci.floop.org.uk/job/GSS_data/job/beta.gss-data.org.uk/job/family/job/climate-change/job/BEIS-2005-to-2019-local-authority-carbon-dioxide-CO2-emissions/"; \
		exit 1; \
	fi
	rm -rf ./inputs/*
	rm -rf ./rdf/*
	rm -rf ./hdt/*
	pipenv run python3 scripts/download-artifacts-from-jenkins-job.py $(job)
	pipenv run python3 scripts/unpack-rdf-artifacts.py
	pipenv run python3 scripts/convert-rdf-to-hdt.py
	pipenv run python3 scripts/write-server-config.py
	rm -rf ./inputs/*
	rm -rf ./rdf/*

# If we're calling to jenkins make sure the user has exported what they need to.
.PHONY: check-hdt-from-jenkins-env
check-hdt-from-jenkins-env:
ifndef JENKINS_API_TOKEN
	$(error JENKINS_API_TOKEN is undefined)
endif
ifndef JENKINS_USER
	$(error JENKINS_USER is undefined)
endif