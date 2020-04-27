from collections import defaultdict

props = [l.split("\t") for l in open("properties_validated.tsv", "r").read().split("\n")]
propEntities = defaultdict(list)
for prop in props:
    ls = allEntities[prop[0]]
    ls2 = [el.split(" [")[0] for el in propEntities[prop[-1]]]
    for elem in ls:
        if elem[1] not in ls2:
            if type(elem) !=str:
                propEntities[prop[-1]].append(elem[::-1][0] + " [" + elem[::-1][1] + "]")
            else:
                propEntities[prop[-1]].append(elem)

open("results.tsv", "w+").write("\n".join(["\t".join(el) for el in result]))