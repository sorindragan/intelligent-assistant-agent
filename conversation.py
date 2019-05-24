from rdflib import Graph, Literal, URIRef
from rdflib import Namespace
from pprint import pprint

from sentence_processor import SentenceProcessor
from question_processor import QuestionProcessor


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
        """ Construct and update the RDF Graph based on triplets extracted
            during a conversation
        """
        sentence_processor = SentenceProcessor(phrase)
        triplets = sentence_processor.process()
        g = Graph()
        n = self.n
        g.parse(self.rdf_file, format="xml")
        # uri_property = URIRef(n.property)

        for triplet in triplets:
            s, p, o = triplet
            s, p, o = s.replace(" ", "_"), p.replace(" ", "_"), o.replace(" ", "_")
            subj, pred, obj = URIRef(n + s), URIRef(n + p), URIRef(n + o)

            # if pred == "property":
            #     pred = uri_property

            g.add((subj, pred, obj))

        g.serialize(self.rdf_file)

    def yes_no_query(self, triplets, g):
        query_triplets = []
        n = self.n
        for triplet in triplets:
            s, p, o = triplet
            s, p, o = s.replace(" ", "_"), p.replace(" ", "_"), o.replace(" ", "_")
            subj, pred, obj = URIRef(n + s), URIRef(n + p), URIRef(n + o)
            query_triplets.append((subj, pred, obj))

        if all([True if triplet in g else False
                for triplet in query_triplets
                ]):
            response = "Yes."
        else:
            response = "No."
        return response


    def reply(self, phrase):
        """ Construct query and interogate RDF Graph based on triplets extracted
            during a conversation
        """
        g = Graph()
        g.parse(self.rdf_file, format="xml")

        question_processor = QuestionProcessor(phrase)
        triplets = question_processor.process()
        # TODO: costruct queries
        wh_list = ["who", "what", "where", "why", "when", "which", "how"]

        # yes/no questions
        if phrase.split()[0].lower() not in wh_list:
            response = self.yes_no_query(triplets, g)

        # return response

        return response

    def process(self, phrase):

        if phrase.lower().strip("!").strip(".") in self.end_sentences:
            return "Glad we talked!"
        elif phrase.lower().strip("!").strip(".") in self.greetings:
            return "Hello! What a wonderful day!"
        elif '?' in phrase:
            return self.reply(phrase)
        else:
            self.listen(phrase)
