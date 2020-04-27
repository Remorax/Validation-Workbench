'''
This script extracts RDF triples from Freebase, BabelNet, Google KG, DBPedia 
and the Stanford Pizza Ontology and then performs entity and property disambiguation
using Sequence Matcher. The properties are written to a file called 'properties.tsv'
but they are only partially disambiguated. 

The properties.tsv file needs to be manually disambiguated after this step and saved
in a file called properties_validated.tsv. Then run `process_validated_properties.py`
'''

import urllib, json, requests, difflib, re
from difflib import SequenceMatcher
from SPARQLWrapper import SPARQLWrapper, JSON
from bs4 import BeautifulSoup
from collections import defaultdict
from pronto import Ontology

API_KEY = "AIzaSyD61I7wa6eDMTW-DU0hV3wWLXim85NbMHM" # Google API key

# Stage 1: RDF Triple extraction

def FreebaseExtractor(url):
    '''
        Extracts raw (property, entity) RDF triples from Freebase given url
    '''
    output = []
    # Relations to exclude from Freebase
    junkRelations = ["/type/object/permission", "/type/object/creator", "/type/object/attribution", "/common/topic/topic_equivalent_webpage", "/base/ontologies/ontology_instance/equivalent_instances"]
    r = requests.get(url)
    soup = BeautifulSoup(r.content)
    properties = soup.findAll("div", {"class": "property-section"})
    for prop in properties:
        data = [(prop["data-id"],el.text) for el in prop.findAll("a", {"class": "property-value"}) if prop["data-id"] not in junkRelations and (prop["data-id"]!="/type/object/key" or (prop["data-id"]=="/type/object/key" and "en" in el.text))]
        output.extend(data)
    return output

def babelNetExtractor(synset):
    '''
        Extracts raw (property, entity) RDF triples from BabelNet given synset ID
    '''

    service_url = 'https://babelnet.io/v5/getSynset'

    key  = 'ee9447b5-1903-4253-92a7-55526862de4f'

    params = {
        'id' : synset,
        'key'  : key
    }

    url = service_url + '?' + urllib.parse.urlencode(params)
    results = json.loads(requests.get(url).content.decode("utf-8"))
    '''
        dict that for each property contains:
        1. the key to choose from that property
        2. a machine-readable phrase for the property
    '''
    filteringDict = {
        "senses": ("simpleLemma", "related"),
        "glosses": ("gloss", "description"),
        "examples": ("example", "example"),
        "images": ("url", "images"),
        "categories": ("category", "category")
    }
    babelNet = []
    for key in results:
        ls = results[key]
        if key in filteringDict:
            for elem in ls:
                tup = filteringDict[key]
                if key=="senses":
                    babelNet.append((tup[1], elem["properties"][tup[0]]))
                elif key=="lnToOtherForm" or key=="lnToCompound":
                    [tup[1], key[tup[0]]]
                else:
                    babelNet.append((tup[1], elem[tup[0]]))
        elif key == "domains":
            babelNet.extend([("domain", el) for el in ls.keys()])
        elif key == "lnToCompound":
            babelNet.extend([("compounds", el) for el in ls["EN"]])
        elif key == "lnToOtherForm":
            babelNet.extend([("other forms", el) for el in ls["EN"]])
    return babelNet


def GoogleKGExtractor(entity):
    '''
        Extracts raw (property, entity) RDF triples from Google KG given entity name
    '''

    googleKGResults = []
    url = "https://kgsearch.googleapis.com/v1/entities:search?query=" + entity + "&key=" + API_KEY + "&limit=1&indent=True"
    response = json.loads(requests.get(url).content)
    results = response["itemListElement"][0]["result"]
    googleKGResults.append(("images", results["image"]["url"]))
    googleKGResults.append(("hypernym", results["description"]))
    googleKGResults.extend([("type", el) for el in results["@type"]])
    googleKGResults.append(("url", results["detailedDescription"]["url"]))
    googleKGResults.append(("description", results["detailedDescription"]["articleBody"]))
    return googleKGResults

def DBPediaExtractor(entity):
    '''
        Extracts raw (property, entity) RDF triples from DBPedia given entity name
    '''

    entity = "Pizza"
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    junkRelations = ["http://www.w3.org/2000/01/rdf-schema#label", "http://www.w3.org/2002/07/owl#sameAs", "http://dbpedia.org/ontology/wikiPageID", "http://dbpedia.org/ontology/wikiPageRevisionID", "http://xmlns.com/foaf/0.1/name", "http://purl.org/voc/vrank#hasRank"]
    sparql.setQuery("""SELECT * WHERE {<http://dbpedia.org/resource/"""+entity + """> ?relation ?object .}""")
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    allvals = results["results"]["bindings"]
    dbpedia = []
    for val in allvals:
        if ("xml:lang" not in val["object"] or val["object"]["xml:lang"]=="en") and val["relation"]["value"] not in junkRelations:
            dbpedia.append((val["relation"]["value"], val["object"]["value"]))
    return dbpedia

def ontologyExtractor(ontName):
    '''
        Extracts raw (property, entity) RDF triples from ontology given entity name
    '''

    ont = Ontology(ontName)
    ontology = []
    for term in list(ont.terms()):
        subclasses = list(term.subclasses())
        ontology.extend([(subclass.name, "subclass_of", term.name) for subclass in subclasses])
    ontology = [tuple(el.split("\t")) for el in list(set(["\t".join(relation) for relation in ontology if relation[0]!=relation[-1]]))]
    ontology = [ont for ont in ontology if ont[0]=="Pizza" or ont[-1] == "Pizza"]
    ontology = [("hypernym", el[-1]) if el[0]=="Pizza" else ("hyponym", el[0] + " Pizza") for el in ontology ]
    return ontology

def camel_case_split(identifier):
    matches = re.finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
    return " ".join([m.group(0).lower() for m in matches])

url = "https://web.archive.org/web/20150720100504/http://www.freebase.com:80/m/0663v"
freebase = FreebaseExtractor(url)

synset = 'bn:00062694n'
babelNet = babelNetExtractor(synset)

entity = "pizza"
googleKG = GoogleKGExtractor(entity)

entity = "pizza"
dbpedia = DBPediaExtractor(entity)

ontName = "/Users/vivek/SIREN-Research/pizza.owl"
ontology = ontologyExtractor(ontName)

relations = freebase + babelNet + googleKG + ontology + dbpedia
open("relations.tsv", "w+").write("\n".join(["\t".join(l) for l in relations]))

# Stage 2: Entity Resolution 

threshold = 0.56 # Optimum threshold concluded from experiments (see similarity.py)

resolvedRelations = []

for elem in relations:
    relation = elem[0].split("/")[-1].split("#")[-1]
    item = elem[1]
    if ("https://" in item or "http://" in item) and "dbpedia" not in item and "#" not in item:
        resolvedRelations.append((relation, item))
        continue
    item = " ".join(item.split("/")[-1].split("#")[-1].split("_"))
    # Query Wikidata for each item
    url = "https://www.wikidata.org/w/index.php?search=" + "_".join(item.split(":")[-1].split(" "))
    r = requests.get(url)
    soup = BeautifulSoup(r.content)
    try:
        matches = soup.findAll("span", {"class": "wb-itemlink"})
        matches = [(match.find("span", {"class": "wb-itemlink-label"}), match.find("span", {"class": "wb-itemlink-id"})) for match in matches]
        top_results = [(el[0].text, el[1].text[1:-1]) for el in matches if el[0].text and el[1].text[1:-1][0]=="Q"][:5]
        
        # Return top matches above a certain threshold for difflib
        bestMatch = difflib.get_close_matches(item.lower(), [el[0].lower() for el in top_results], 1, threshold)[0]
        resolvedEntity = [el for el in top_results if el[0].lower()==bestMatch][0]
        s = SequenceMatcher(lambda x: x == " ", bestMatch, item.lower())
        resolvedRelations.append((relation, resolvedEntity[1]))
    except Exception as e:
        resolvedRelations.append((relation, item))
        pass


relationsDict = {}
for relation in resolvedRelations:
    if relation[0] in relationsDict:
        relationsDict[relation[0]].append(relation[1:])
    else:
        relationsDict[relation[0]] = [relation[1]]

# Stage 3: (Automated) Property Resolution 
# A preliminary stage to manual property resolution
# Similar to entity resolution

resolvedProperties = []
properties = list(allEntities.keys())
for prop in properties:
    item = camel_case_split(" ".join(prop.split("_")))
    url = "https://www.wikidata.org/w/index.php?search=" + "_".join(prop.split(" ")) + "&ns120=1"
    r = requests.get(url)
    soup = BeautifulSoup(r.content)
    try:
        matches = soup.findAll("span", {"class": "wb-itemlink"})
        matches = [(match.find("span", {"class": "wb-itemlink-label"}), match.find("span", {"class": "wb-itemlink-id"})) for match in matches]
        top_results = [(el[0].text, el[1].text[1:-1]) for el in matches if el[0].text and el[1].text[1:-1][0]=="P"][:5]
        bestMatch = difflib.get_close_matches(item.lower(), [el[0].lower() for el in top_results], len(top_results), 0)[0]
        resolvedEntity = [el for el in top_results if el[0].lower()==bestMatch][0]
        s = SequenceMatcher(lambda x: x == " ", bestMatch, item.lower())
        resolvedProperties.append((prop, resolvedEntity[1]))
    except Exception as e:
        resolvedProperties.append((prop, item))
        pass

open("properties.tsv", "w+").write("\n".join(["\t".join(el) for el in resolvedProperties]))