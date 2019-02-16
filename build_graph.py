from rdflib import Graph
from rdflib import URIRef, BNode, Literal
from rdflib import Namespace
from rdflib.namespace import RDF, FOAF

bob = URIRef("http://example.org/people/Bob")
linda = BNode()  # a GUID is generated

name = Literal('Bob')  # passing a string
age = Literal(24)  # passing a python int
height = Literal(76.5)  # passing a python float
n = Namespace("http://example.org/people/")
print(n.bob)

g = Graph()

g.add((bob, RDF.type, FOAF.Person))
g.add((bob, FOAF.name, name))
g.add((bob, FOAF.knows, linda))
g.add((linda, RDF.type, FOAF.Person))
g.add((linda, FOAF.name, Literal('Linda')))

g.add((bob, FOAF.age, Literal(42)))
g.set((bob, FOAF.age, Literal(43)))
# g.remove((bob, None, None))  # remove all triples about bob

with open("graph.rdf", "wb") as f:
    f.write(g.serialize())  # example: format='turtle'
