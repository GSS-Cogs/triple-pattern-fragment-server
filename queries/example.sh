docker run --env-file ./env --rm comunica/actor-init-sparql:dev \
https://ldf-trial1-no4vxskx7a-nw.a.run.app/BEIS-Final-UK-greenhouse-gas-emissions-national-statistics-1990-to-2019 \
https://staging.gss-data.org.uk/sparql?query=PREFIX%20rdfs%3A%20%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23%3E%0APREFIX%20skos%3A%20%3Chttp%3A%2F%2Fwww.w3.org%2F2004%2F02%2Fskos%2Fcore%23%3E%0A%0ACONSTRUCT%20%7B%20%3Fmeasure%20rdfs%3Alabel%20%3Flabel%20%7D%20%0AWHERE%20%7B%20%3Fmeasure%20skos%3AinScheme%09%3Chttp%3A%2F%2Fgss-data.org.uk%2Fdef%2Fconcept-scheme%2Fmeasurement-units%3E%20%3B%0A%09rdfs%3Alabel%20%3Flabel%20%7D \
https://staging.gss-data.org.uk/sparql?query=PREFIX%20rdfs%3A%20%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23%3E%0APREFIX%20xsd%3A%20%3Chttp%3A%2F%2Fwww.w3.org%2F2001%2FXMLSchema%23%3E%0A%0ACONSTRUCT%20%7B%20%3Fdateurl%20rdfs%3Alabel%20%3Fdate%20%7D%0AWHERE%20%7B%20%0A%20%20%3Fdateurl%20%3Chttp%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23type%3E%20%3Chttp%3A%2F%2Freference.data.gov.uk%2Fdef%2Fintervals%2FCalendarYear%3E%20%3B%0A%09%09rdfs%3Alabel%20%3Fdate%0A%7D \
"
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX sdmxa: <http://purl.org/linked-data/sdmx/2009/attribute#>
PREFIX dim: <http://gss-data.org.uk/data/gss_fragment_data/energy/beis-final-uk-greenhouse-gas-emissions-national-statistics-1990-to-2019#dimension/>

SELECT *
WHERE {

    # Get wanted observation and dimension urls from the fragments server
    ?obs <http://purl.org/linked-data/cube#dataSet> <http://gss-data.org.uk/data/gss_fragment_data/energy/beis-final-uk-greenhouse-gas-emissions-national-statistics-1990-to-2019#dataset> ;
        dim:gas [ rdfs:label ?gastype] ;  # For a locally defined dimension, we can get the label straight from the fragment server
        dim:period ?dateurl ;
        sdmxa:unitMeasure ?measuretypeurl ;
        <http://gss-data.org.uk/def/measure/gas-emissions> ?emission ;
        FILTER(?gastype NOT IN (\"All\", \"Net CO2 Emissions - Minus Removals\")) .

    # Get labels for dateurls
    ?dateurl rdfs:label ?date .
    FILTER regex(?date, \"(^199[0-9]{1}$)|(^2[0-9]{3}$)\")

    # Get labels for measures
    ?measuretypeurl rdfs:label ?measuretype .
}
"