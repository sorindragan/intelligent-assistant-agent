from utterance_branching import UtteranceBranching
from coref.coref import CorefSolver
from rdflib import Graph, URIRef, Namespace


def rdf_save(phrase, file_name):
    u = UtteranceBranching(CorefSolver(), file=file_name)
    u.process(phrase)

def rdf_query(file_name):
    g1 = Graph()
    g1.parse(file_name, format="xml")

    # who outraced the truck ?
    # outrac is the stem of outraced
    q = """PREFIX agent: <http://agent.org/>
    SELECT ?s
    WHERE {{
        ?s agent:{} agent:{} .
    }}""".format("outrac", "truck")
    print(q)
    responses = g1.query(q)

    string_responses = []
    for response in responses:
        for element in response:
            string_responses.append(element.split("/")[-1])
    return string_responses

def test_save_and_query():
    output = ["car"]
    file_name = "test1.rdf"
    phrase = "The red car outraced the yellow truck."

    rdf_save(phrase, file_name)
    assert rdf_query(file_name) == output
