from rdflib import Graph, Literal, URIRef
from rdflib import Namespace
from pprint import pprint

from sentence_processor import SentenceProcessor


class Conversation:

    def __init__(self, file="agent.rdf"):
        self.end_sentences = ["exit", "enough for now", "goodbye", "goodnight",
                              "bye", "that is all", "that's all for now"]
        self.greetings = ["hi", "hello", "hi there", "hello there",
                          "good morning", "good afternoon"]
        self.rdf_file = file
        self.g = Graph()
        self.n = Namespace("http://agent.org/")
        self.g.serialize(self.rdf_file)

    def listen(self, phrase):
        sentence_processor = SentenceProcessor(phrase)
        triplets = sentence_processor.process()
        g = Graph()
        n = self.n
        g.parse(self.rdf_file, format="xml")
        # uri_property = URIRef(n.property)

        for triplet in triplets:
            s, p, o = triplet
            subj, pred, obj = URIRef(n + s), URIRef(n + p), URIRef(n + o)
            # if pred == "property":
            #     pred = uri_property

            g.add((subj, pred, obj))

        g.serialize(self.rdf_file)

    def reply(self, phrase):
        pass

    def process(self, phrase):

        if phrase.lower().strip("!").strip(".") in self.end_sentences:
            return "Glad we talked!"
        elif phrase.lower().strip("!").strip(".") in self.greetings:
            return "Hello! What a wonderful day!"
        elif '?' in phrase:
            self.reply(phrase)
        else:
            self.listen(phrase)
