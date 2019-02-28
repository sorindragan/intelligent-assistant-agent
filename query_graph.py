import rdflib

g = rdflib.Graph()

g.parse("graph.rdf")

qres = g.query(
    """SELECT DISTINCT ?aname ?bname
    WHERE {
       ?a ns1:knows ?b .
       ?a ns1:name ?aname .
       ?b ns1:name ?bname .
    }""")

for row in qres:
    print(row)

g2 = rdflib.Graph()

g2.parse("spiderman.rdf")

qres2 = g2.query(
    """SELECT DISTINCT ?aname ?bname
    WHERE {
       ?a rel:enemyOf ?b .
       ?a foaf:name ?aname .
       ?b foaf:name ?bname .
    }""")

for row in qres2:
    print(row)
