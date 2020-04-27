# README 

This repository contains the code for the Wikidata enrichment pipeline.

## Files

There are three runnable scripts
1. `main.py`: This script extracts RDF triples from Freebase, BabelNet, Google KG, DBPedia 
and the Stanford Pizza Ontology and then performs entity and property disambiguation
using Sequence Matcher. The properties are written to a file called 'properties.tsv'
but they are only partially disambiguated. 

The properties.tsv file needs to be manually disambiguated after this step and saved
in a file called properties_validated.tsv. Then run `process_validated_properties.py`

2. `process_validated_properties.py`: Processes the validated properties and extracts labels from wikidata. Writes the final results to `results.tsv`

3. `extract_wikidata_entity.py`: Extracts all the RDF triples from a Wikidata entity 

An in-depth explanation of the process can be found in the [report](../Report.pdf)