
# Example Query

We'll go into how this works and what I've done in detail below, first though, to run the query:

* `chmod +x ./example.sh` (only once)
* `./example/sh`

It's running the linked data fragments client [https://github.com/comunica/comunica/](https://github.com/comunica/comunica/) via docker, so (as long as you've got docker installed) no other setup should be needed.

_Note: won't be particularly fast, this is art of the possible stuff, speed/performance/caching etc is a whole different area of investigation._

_Note 2: there's a few different ways/tools for querying linked data fragments, communica from the command line is just the most convenient place to start rather than any sort of long term choice._

### General Principles

The premises of working with linked data fragments is to:

- (a) Start with targetted subsets of the triples you want, so you can...
- (b) Do your filtering/querying/combining on the client side.

**IMPORTANT** - while the "client" in this context is your laptop, for a productionised approach that may well not be the case. The "client" could just as easily be a web server or search portal. The point is the "client" pulls in and combines the data via a federated query, where that data is availible across multiple urls of a distributed data layer, as opposed to a whole bunch of triples in one big triple store dump.


### Why a shell script?

While using the comunica command line client the pattern is `<command> <list data source> <sparql query>`. It's just convenient to put that in a shell script and tweak it as needed.

### Breaking Down The Query

Going to split this into the three obvious component parts metioned above `<command> <list data source> <sparql query>`.

## 1. Command

I'm running this via docker, with some caveats:

1. Comunica uses nodejs, nodejs has finite memory so we're using the `../env` file to make sure its set to a healthy amount. You might not need it but it won't hurt, you can also set it via a direct flag to docker if you prefer.

2. I'm pointing at the dev branch, there's a fix related to RAM that's not in master yet, again just keeping an eye on performance. It's entirely possible to kill nodejs by overloading the RAM it has availible, the more care you take with it the more complex the queries you can successfully execute.

As a general steer, write your queries with performance in mind.

## 2.List Data Sources

The premis of this is to start from finite data sources to minimise the processing burden on the client side.

In the case of this query, we're after three things:

1.) Triples from the specififc dataset `BEIS-Final-UK-greenhouse-gas-emissions-national-statistics-1990-to-2019` - the triple pattern fragment holding these triples is represented by the first url passed into the query.

2.) The labels for the measure type urls as used in the fragment (this information is on PMD).

3.) The labels for the date urls as used in the fragment (this information is on PMD).

To get the pmd information we are url encoding a SPARQL CONSTRUCT query to use as a data source.

For example, a CONSTRUCT query to get the label for each measure type url is shown below:

```
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

CONSTRUCT { ?measure rdfs:label ?label } 
WHERE { ?measure skos:inScheme	<http://gss-data.org.uk/def/concept-scheme/measurement-units> ;
	rdfs:label ?label }
```

If you url encode this query (you can use this: https://meyerweb.com/eric/tools/dencoder/) and pass it to the relevant PMD endpoint `https://staging.gss-data.org.uk/sparql?query=`: you get the url:

```
https://staging.gss-data.org.uk/sparql?query=PREFIX%20rdfs%3A%20%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23%3E%0APREFIX%20skos%3A%20%3Chttp%3A%2F%2Fwww.w3.org%2F2004%2F02%2Fskos%2Fcore%23%3E%0A%0ACONSTRUCT%20%7B%20%3Fmeasure%20rdfs%3Alabel%20%3Flabel%20%7D%20%0AWHERE%20%7B%20%3Fmeasure%20skos%3AinScheme%09%3Chttp%3A%2F%2Fgss-data.org.uk%2Fdef%2Fconcept-scheme%2Fmeasurement-units%3E%20%3B%0A%09rdfs%3Alabel%20%3Flabel%20%7D \
```

Which results in an RDF data source _equal to the exact data we need_.

So sources 2 and 3 in the query are just url encoded CONSTRUCT queries to pmd, getting the specific data the query needs to lookup reference data labels.

## 3. SPARQL Query

This is very similar to a typicsl SPARQL query and supports the same conventions and functionality you'd expect.

Things worth noting though:

- Local dimensions will be defined in/on the fragment, so you can get eg label without bringing PMD into it.
- Filter earlier than you otherwise would (as soon as you can basically), it's more performant as (I think, thought not 100%) it'll garbage collect the unwanted triples and help you avoid resources constraints.
- The basic approach is: get what you need from the fragment(s) you're using, then where needed supplement that data with targetted calls to PMD via url encoded CONSTRUCT queries.



