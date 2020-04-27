import requests, urllib, json
from bs4 import BeautifulSoup

entity = "Q177"
r = requests.get("https://www.wikidata.org/wiki/Q177")
soup = BeautifulSoup(r.content)
properties = soup.findAll("div", {"class": "wikibase-statementgrouplistview"})[0]
props = [p["id"] for p in properties.findAll("div", {"class": "wikibase-statementgroupview"}) if p["id"]]
entities = [[el["title"] for el in p.findAll("a", {"class": "wikibase-snakview-variation-valuesnak"}) if el.has_attr("title")] for p in properties.findAll("div", {"class": "wikibase-statementlistview-listview"}) if p.findAll("a")]

with urllib.request.urlopen("https://www.wikidata.org/w/api.php?action=wbgetentities&ids=Q177&format=json") as url:
    data = json.loads(url.read().decode())
    allClaims = data["entities"]["Q177"]["claims"]

original = []
for claim in allClaims:
    entts = allClaims[claim]
    for entt in entts:
        if entt["mainsnak"]["datatype"] == "wikibase-item":
            original.append((entt["mainsnak"]["property"], entt["mainsnak"]["datavalue"]["value"]["id"]))
        else:
            try:
                original.append((entt["mainsnak"]["property"], entt["mainsnak"]["datavalue"]["value"]))
            except:
                raise

open("original_entities.tsv", "w+").write("\n".join(["\t".join(el) for el in original]))