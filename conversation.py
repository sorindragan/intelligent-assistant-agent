from nltk.stem import PorterStemmer, WordNetLemmatizer
from pprint import pprint
from rdflib import Graph, Literal, URIRef
from rdflib import Namespace
from string import digits
import random


from sentence_processor import SentenceProcessor
from question_processor import QuestionProcessor


class Conversation:

    def __init__(self, file="agent.rdf"):
        self.end_sentences = ["exit", "enough for now", "goodbye", "goodnight",
                              "bye", "that is all", "that's all for now"]
        self.greetings = ["hi", "hello", "hi there", "hello there",
                          "good morning", "good afternoon", "hey"]
        self.rdf_file = file
        self.g = Graph()
        self.n = Namespace("http://agent.org/")
        self.g.serialize(self.rdf_file)
        self.stemmer = PorterStemmer()
        self.lemm = WordNetLemmatizer()
        self.no = 1
        self.wh_list = ["who", "what", "where", "why", "when", "which", "how"]

    def listen(self, phrase):
        """ Construct and update the RDF Graph based on triplets extracted
            during a conversation
        """
        sentence_processor = SentenceProcessor(phrase, self.no)
        self.no += 1
        triplets = sentence_processor.process()
        g = Graph()
        n = self.n
        g.parse(self.rdf_file, format="xml")

        for triplet in triplets:
            s, p, o = triplet
            st_s, st_p, st_o = self.stemmer.stem(s), self.stemmer.stem(self.lemm.lemmatize(p, 'v')), self.stemmer.stem(o)
            # s, p, o = self.lemm.lemmatize(s), self.lemm.lemmatize(p), self.lemm.lemmatize(o)
            s, p, o = s.replace(" ", "_"), p.replace(" ", "_"), o.replace(" ", "_")
            st_s, st_p, st_o = st_s.replace(" ", "_"), st_p.replace(" ", "_"), st_o.replace(" ", "_")
            print((s, p, o), (st_s, st_p, st_o))
            subj, pred, obj = URIRef(n + st_s), URIRef(n + st_p), URIRef(n + st_o)
            g.add((subj, pred, obj))
            g.add((subj, URIRef(n + "reference"), URIRef(n + s)))
            g.add((pred, URIRef(n + "reference"), URIRef(n + p)))
            g.add((obj, URIRef(n + "reference"), URIRef(n + o)))

        g.serialize(self.rdf_file)

    def yes_no_query(self, triplets, g):
        lose_digits = str.maketrans('', '', digits)
        query_triplets = []
        n = self.n
        for triplet in triplets:
            s, p, o = triplet
            s, p, o = self.stemmer.stem(s), self.stemmer.stem(self.lemm.lemmatize(p, 'v')), self.stemmer.stem(o)
            # s, p, o = self.lemm.lemmatize(s), self.lemm.lemmatize(p), self.lemm.lemmatize(o)
            s, p, o = s.replace(" ", "_"), p.replace(" ", "_"), o.replace(" ", "_")
            print(s, p, o)
            subj, pred, obj = URIRef(n + s), URIRef(n + p), URIRef(n + o)
            query_triplets.append((subj, pred, obj))

        if all([True if triplet in g else False
                for triplet in query_triplets
                ]):
            bot_response = "Yes."
        else:
            print(query_triplets)
            bot_response = "Yes."
            for triplet in query_triplets:
                s, p, o = triplet
                s, p, o = s.split("/")[-1], p.split("/")[-1], o.split("/")[-1]
                if o.translate(lose_digits) == "at":
                    query_responses = []
                    q = """PREFIX agent: <http://agent.org/>
                    SELECT ?o
                    WHERE {{
                        agent:{} agent:{} ?o.
                    }}""".format(s, p)
                    print(q)
                    query_responses.append(g.query(q))

                    string_responses = []
                    for response in query_responses:
                        for element in response:
                            for triplet in element:
                                word = triplet.split("/")[-1]
                                string_responses.append(word.translate(lose_digits))

                    print(string_responses)
                    if "at" not in string_responses:
                        bot_response = "No."
                        break

                if s.translate(lose_digits) == "at":
                    query_responses = []
                    q = """PREFIX agent: <http://agent.org/>
                    SELECT ?s
                    WHERE {{
                        ?s agent:{} agent:{}.
                    }}""".format(p, o)
                    print(q)
                    query_responses.append(g.query(q))

                    string_responses = []
                    for response in query_responses:
                        for element in response:
                            for triplet in element:
                                word = triplet.split("/")[-1]
                                string_responses.append(word.translate(lose_digits))

                    print(string_responses)
                    if "at" not in string_responses:
                        bot_response = "No."
                        break

        return bot_response

    def who_what_query(self, triplets, g):
        # TODO extract properties for objects that are not abstract
        query_properties = {}
        query_responses = []
        n = self.n
        for triplet in triplets:
            s, p, o = triplet
            if any([s == "what" and p == "is_a", o == "what" and p == "is_a",
                    s == "who" and p == "is_a", o == "who" and p == "is_a"
                    ]):
                continue
            s, p, o = self.stemmer.stem(s), self.stemmer.stem(self.lemm.lemmatize(p, 'v')), self.stemmer.stem(o)
            # s, p, o = self.lemm.lemmatize(s), self.lemm.lemmatize(p), self.lemm.lemmatize(o)
            s, p, o = s.replace(" ", "_"), p.replace(" ", "_"), o.replace(" ", "_")
            print(s, p, o)
            subj, pred, obj = URIRef(n + s), URIRef(n + p), URIRef(n + o)

            q = """PREFIX agent: <http://agent.org/>
            SELECT ?o
            WHERE {{
                agent:{} agent:{} ?o.
            }}""".format(s, p)
            print(q)
            query_responses.append(g.query(q))

        string_responses = []
        for response in query_responses:
            for element in response:
                for triplet in element:
                    word = triplet.split("/")[-1]
                    if word == "null":
                        continue
                    string_responses.append(word)
                    query_properties[word] = []

        print(string_responses)
        stem_response = []
        for word in string_responses:
            if word[:2] == "at":
                q_p = """PREFIX agent: <http://agent.org/>
                SELECT ?p ?o
                WHERE {{
                    agent:{} ?p ?o.
                    FILTER (?p != agent:reference) .
                }}""".format(word)
                print(q_p)
                query_properties[word].append(g.query(q_p))
            else:
                q_s = """PREFIX agent: <http://agent.org/>
                SELECT ?o
                WHERE {{
                    agent:{} agent:properti ?o.
                }}""".format(word)
                simple_properties = g.query(q_s)
                for prop in simple_properties:
                    for tuple in prop:
                        stem = tuple.split("/")[-1]
                        stem_response.append(stem)
                stem_response.append(word)


        object_type = None
        for key in query_properties:
            for result in query_properties[key]:
                for element in result:
                    print(element)
                    if element[-2].split("/")[-1] == "is_a":
                        object_type = element[-1].split("/")[-1]
                        continue

                    property = element[-1].split("/")[-1]

                    if property == "null":
                        continue
                    print(property)
                    stem_response.append(property)
            stem_response.append(object_type)

        lexical_responses = []
        for stem in stem_response:
            q_s = """PREFIX agent: <http://agent.org/>
            SELECT ?o
            WHERE {{
                agent:{} agent:reference ?o.
            }}""".format(stem)
            print(q_s)
            lexical_responses.append(g.query(q_s))

        string_response = ""
        for response in lexical_responses:
            for element in response:
                for triplet in element:
                    word = triplet.split("/")[-1]
                    word = word.replace("_", " ")
                    string_response += word + " "

        return string_response[:-1]

    def where_when_query(self, triplets, g):
        query_responses = []
        n = self.n
        for triplet in triplets:
            s, p, o = triplet
            s, p, o = self.stemmer.stem(s), self.stemmer.stem(self.lemm.lemmatize(p, 'v')), self.stemmer.stem(o)
            # s, p, o = self.lemm.lemmatize(s), self.lemm.lemmatize(p), self.lemm.lemmatize(o)
            s, p, o = s.replace(" ", "_"), p.replace(" ", "_"), o.replace(" ", "_")
            print(s, p, o)
            subj, pred, obj = URIRef(n + s), URIRef(n + p), URIRef(n + o)

            q = """PREFIX agent: <http://agent.org/>
            SELECT ?o
            WHERE {{
                agent:{} agent:{} ?o.
            }}""".format(s, p)
            print(q)
            query_responses.append(g.query(q))
        stem_responses = []
        for response in query_responses:
            for element in response:
                for triplet in element:
                    word = triplet.split("/")[-1]
                    stem_responses.append(word)

        lose_digits = str.maketrans('', '', digits)
        stem_responses = filter(lambda x: x.translate(lose_digits) != "at", stem_responses)
        print(stem_responses)

        lexical_responses = []
        for stem in stem_responses:
            q_s = """PREFIX agent: <http://agent.org/>
            SELECT ?o
            WHERE {{
                agent:{} agent:reference ?o.
            }}""".format(stem)
            print(q_s)
            lexical_responses.append(g.query(q_s))

        string_response = ""
        for response in lexical_responses:
            for element in response:
                for triplet in element:
                    word = triplet.split("/")[-1]
                    word = word.replace("_", " ")
                    string_response += word + " "

        return string_response[:-1]


    def reply(self, phrase):
        """ Construct query and interogate RDF Graph based on triplets extracted
            during a conversation
        """
        g = Graph()
        g.parse(self.rdf_file, format="xml")

        response = ""

        question_processor = QuestionProcessor(phrase)
        triplets = question_processor.process()
        wh_list = self.wh_list
        # TODO: costruct queries

        # yes/no questions
        if phrase.split()[0].lower() not in wh_list:
            response = self.yes_no_query(triplets, g)
        elif phrase.split()[0].lower() in ["who", "what"]:
            response = self.who_what_query(triplets, g)
        elif phrase.split()[0].lower() in ["where", "when"]:
            response = self.where_when_query(triplets, g)

        return response

    def process(self, phrase):
        bot_reply = ""
        if phrase.lower().strip("!").strip(".") in self.end_sentences:
            bot_reply = random.choice(["Glad we talked!", "Happy to help!", "Gooodbye!"])
        elif phrase.lower().strip("!").strip(".") in self.greetings:
            bot_reply = random.choice(["Hello! What a wonderful day!", "At your disposal!", "Hi there!"])
        elif ('?' in phrase)  or (phrase.split()[0] in self.wh_list):
            bot_reply = self.reply(phrase + "?")
        else:
            self.listen(phrase)
            bot_reply = "Roger that!"

        return bot_reply
