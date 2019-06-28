from nltk.stem import PorterStemmer, WordNetLemmatizer
from pprint import pprint
from rdflib import Graph, Literal, Namespace, URIRef
from string import digits
import itertools
import functools

from sentence_processor import SentenceProcessor
from question_processor import QuestionProcessor


class Conversation:

    def __init__(self, file="agent.rdf", verbose=False):
        self.rdf_file = file
        self.g = Graph()
        self.n = Namespace("http://agent.org/")
        self.g.serialize(self.rdf_file)
        self.stemmer = PorterStemmer()
        self.lemm = WordNetLemmatizer()
        self.wh_list = ["who", "what", "where", "why", "when", "which", "how"]
        self.yes_no_list = ["is", "are", "am", "will", "could", "would", "may",
                            "can", "have", "has", "had", "did", "do", "does",
                            ]
        self.verbose = verbose
        self.no = 1
        self.lose_digits = str.maketrans('', '', digits)
        self.debug_dict = {}


    def words_to_URIs(self, triplet):
        n = self.n
        s, p, o = triplet
        s, p, o = self.stemmer.stem(s), self.stemmer.stem(self.lemm.lemmatize(p, 'v')), self.stemmer.stem(o)
        s, p, o = s.replace(" ", "_"), p.replace(" ", "_"), o.replace(" ", "_")
        subj, pred, obj = URIRef(n + s), URIRef(n + p), URIRef(n + o)
        return (subj, pred, obj)

    def URIs_to_words(self, responses):
        strings = [word.split("/")[-1]
                   for response in responses
                   for element in response
                   for word in element
                   if word.split("/")[-1] != "null"
                   ]
        return strings

    def listen(self, phrase):
        """ Construct and update the RDF Graph based on triplets extracted
            during a conversation
        """
        sentence_processor = SentenceProcessor(phrase, no=self.no, verbose=self.verbose)
        self.no += 1
        triplets = sentence_processor.process()
        g = Graph()
        n = self.n
        g.parse(self.rdf_file, format="xml")

        self.debug_dict["listen_triplets"] = triplets
        additional_triplets = []
        for triplet in triplets:
            s, p, o = triplet
            if s[-1] in digits:
                new_triplet = self.words_to_URIs((s, "type", s.translate(self.lose_digits)))
                additional_triplets.append(new_triplet)
                g.add(new_triplet)
            if o[-1] in digits:
                new_triplet = self.words_to_URIs((o, "type", o.translate(self.lose_digits)))
                additional_triplets.append(new_triplet)
                g.add(new_triplet)

            subj, pred, obj = self.words_to_URIs(triplet)
            g.add((subj, pred, obj))
            s, p, o = s.replace(" ", "_"), p.replace(" ", "_"), o.replace(" ", "_")
            additional_triplets.append((subj, URIRef(n + "reference"), URIRef(n + s)))
            additional_triplets.append((pred, URIRef(n + "reference"), URIRef(n + p)))
            additional_triplets.append((obj, URIRef(n + "reference"), URIRef(n + o)))
            g.add((subj, URIRef(n + "reference"), URIRef(n + s)))
            g.add((pred, URIRef(n + "reference"), URIRef(n + p)))
            g.add((obj, URIRef(n + "reference"), URIRef(n + o)))

        self.debug_dict["additional_triplets"] = additional_triplets

        g.serialize(self.rdf_file)

    def yes_no_query(self, triplets, g):
        query_triplets = []
        n = self.n
        self.debug_dict["yes_no_query"] = triplets
        if not triplets:
            return "Spacy could not create the dependency tree correctly for this question."

        for triplet in triplets:
            query_triplets.append(self.words_to_URIs(triplet))

        if all([True if triplet in g else False
                for triplet in query_triplets
                ]):
            bot_response = "Yes."
        else:
            bot_response = "Yes."
            for triplet in query_triplets:
                s, p, o = triplet
                s, p, o = s.split("/")[-1], p.split("/")[-1], o.split("/")[-1]
                if o.translate(self.lose_digits) == "at":
                    query_responses = []
                    q = """PREFIX agent: <http://agent.org/>
                    SELECT ?o
                    WHERE {{
                        agent:{} agent:{} ?o.
                    }}""".format(s, p)
                    query_responses.append(g.query(q))

                    self.debug_dict["yes_no_q1"] = q

                    string_responses = self.URIs_to_words(query_responses)

                    self.debug_dict["yes_no_string_responses_object"] = string_responses

                    if "at" not in string_responses:
                        bot_response = "No, or I don't know that yet.+"
                        break

                if s.translate(self.lose_digits) == "at":
                    query_responses = []
                    q = """PREFIX agent: <http://agent.org/>
                    SELECT ?s
                    WHERE {{
                        ?s agent:{} agent:{}.
                    }}""".format(p, o)
                    query_responses.append(g.query(q))
                    self.debug_dict["yes_no_q2"] = q

                    string_responses = self.URIs_to_words(query_responses)

                    self.debug_dict["yes_no_string_responses_subject"] = string_responses
                    if "at" not in string_responses:
                        bot_response = "No, or I don't know that yet.+"
                        break

                if s.translate(self.lose_digits) != "at" and o.translate(self.lose_digits) != "at":
                    bot_response = "No, or I don't know that yet.+"

        return bot_response

    def reference_query(self, word):
        g = Graph()
        g.parse(self.rdf_file, format="xml")
        q_ = """PREFIX agent: <http://agent.org/>
        SELECT ?o
        WHERE {{
            agent:{} agent:reference ?o.
        }}""".format(word)
        res = g.query(q_)
        return self.URIs_to_words([res])[0]

    def stem_to_reference(self, obj_prop_tuple):
        key, values = obj_prop_tuple
        new_key = self.reference_query(key)
        new_values = list(map(self.reference_query, values))
        return (new_key, new_values)

    def who_what_query(self, triplets, g):
        query_properties = {}
        query_responses = []
        n = self.n
        self.debug_dict["WHO_WHAT_triplets"] = triplets
        for triplet in triplets:
            s, p, o = triplet
            if any([s == "what" and p == "is_a", o == "what" and p == "is_a",
                    s == "who" and p == "is_a", o == "who" and p == "is_a"
                    ]):
                continue
            s, p, o = self.stemmer.stem(s), self.stemmer.stem(self.lemm.lemmatize(p, 'v')), self.stemmer.stem(o)
            s, p, o = s.replace(" ", "_"), p.replace(" ", "_"), o.replace(" ", "_")

            q = """PREFIX agent: <http://agent.org/>
            SELECT ?o
            WHERE {{
                agent:{} agent:{} ?o.
            }}""".format(s, p)
            query_responses.append(g.query(q))
            self.debug_dict["who_what_q1"] = q

        string_responses = self.URIs_to_words(query_responses)

        for word in string_responses:
            if "at" == word[:2] and word[-1] in digits:
                continue
            query_properties[word] = []

        self.debug_dict["who_what_string_responses"] = string_responses

        at_reponses = []
        for word in list(set(string_responses)):
            if word[:2] == "at":
                q_p = """PREFIX agent: <http://agent.org/>
                SELECT ?o
                WHERE {{
                    agent:{} agent:is_a ?o.
                }}""".format(word)
                at_reponses.append(g.query(q_p))
                self.debug_dict["who_what_q2"] = q_p

                type = at_reponses[-1]
                type = self.URIs_to_words([type])[0]

                q_s = """PREFIX agent: <http://agent.org/>
                SELECT ?o
                WHERE {{
                    agent:{} agent:properti ?o.
                }}""".format(word)
                if type not in query_properties:
                    query_properties[type] = []
                query_properties[type].append(g.query(q_s))
            else:
                q_s = """PREFIX agent: <http://agent.org/>
                SELECT ?o
                WHERE {{
                    agent:{} agent:properti ?o.
                }}""".format(word)
                query_properties[word].append(g.query(q_s))


        for key in query_properties:
            query_properties[key] = self.URIs_to_words(query_properties[key])

        object_properties = list(query_properties.items())
        object_properties = [element for element in object_properties
                             if "_" not in element[0]
                             ]
        print(object_properties)
        results = list(map(self.stem_to_reference, object_properties))
        print(results)

        final_response = functools.reduce(lambda acc, elem:
                                          acc + ", ".join(map(str, elem[1])) + " " + str(elem[0]) + " and ",
                                          results, ""
                                          )
        return final_response[:-4]

    def where_when_query(self, triplets, g):
        query_responses = []
        n = self.n
        for triplet in triplets:
            s, p, o = triplet
            s, p, o = self.stemmer.stem(s), self.stemmer.stem(self.lemm.lemmatize(p, 'v')), self.stemmer.stem(o)
            s, p, o = s.replace(" ", "_"), p.replace(" ", "_"), o.replace(" ", "_")

            q = """PREFIX agent: <http://agent.org/>
            SELECT ?o
            WHERE {{
                agent:{} agent:{} ?o.
            }}""".format(s, p)
            query_responses.append(g.query(q))
            self.debug_dict["where_when_q1"] = q

        stem_responses = self.URIs_to_words(query_responses)
        stem_responses = filter(lambda w: w.translate(self.lose_digits) != "at" or "_" in w, stem_responses)
        self.debug_dict["where_when_stem_responses"] = stem_responses

        lexical_responses = []
        for stem in list(set(stem_responses)):
            q_s = """PREFIX agent: <http://agent.org/>
            SELECT ?o
            WHERE {{
                agent:{} agent:reference ?o.
            }}""".format(stem)
            self.debug_dict["where_when_q2"] = q
            lexical_responses.append(g.query(q_s))

        string_responses = self.URIs_to_words(lexical_responses)

        final_response = functools.reduce(lambda acc, elem:
                                          acc + elem.replace("_", " ") + " ",
                                          string_responses, ""
                                          )
        return final_response[:-1]


    def which_query(self, triplets, g):
        n = self.n
        final_response = ""
        type_responses = []
        original_word = None
        for triplet in triplets:
            s, p, o = triplet
            s, p, o = self.stemmer.stem(s), self.stemmer.stem(self.lemm.lemmatize(p, 'v')), self.stemmer.stem(o)
            s, p, o = s.replace(" ", "_"), p.replace(" ", "_"), o.replace(" ", "_")

            q = """PREFIX agent: <http://agent.org/>
            SELECT ?s
            WHERE {{
                ?s agent:type agent:{}.
            }}""".format(s)
            self.debug_dict["which_q1"] = q
            type_responses.append(g.query(q))

        type_responses = self.URIs_to_words(type_responses)

        word_response = None
        for word in type_responses:
            q_o = """PREFIX agent: <http://agent.org/>
            SELECT ?o
            WHERE {{
                agent:{} agent:{} ?o.
            }}""".format(word, p)
            res = g.query(q_o)
            if res:
                word_response = word

        if word_response:
            q_r = """PREFIX agent: <http://agent.org/>
            SELECT ?o
            WHERE {{
                agent:{} agent:reference ?o.
            }}""".format(word_response)
            org = g.query(q_r)
            original_word = self.URIs_to_words([org])[0]

            q_p = """PREFIX agent: <http://agent.org/>
            SELECT ?o
            WHERE {{
                agent:{} agent:properti ?o.
            }}""".format(word_response)
            stem_properties = g.query(q_p)
            stem_properties = self.URIs_to_words([stem_properties])
            print(stem_properties)
            org_properties = list(map(self.reference_query, stem_properties))

            final_response = functools.reduce(lambda acc, elem:
                                              acc + elem + " ",
                                              org_properties, ""
                                              )
            final_response += original_word.translate(self.lose_digits)
        return final_response

    def reply(self, phrase):
        """ Construct query and interogate RDF Graph based on triplets extracted
            during a conversation
        """
        g = Graph()
        g.parse(self.rdf_file, format="xml")

        response = ""

        question_processor = QuestionProcessor(phrase, verbose=self.verbose)
        triplets = question_processor.process()

        # yes/no questions
        if phrase.split()[0].lower() in self.yes_no_list:
            response = self.yes_no_query(triplets, g)
        # wh quesrions
        elif phrase.split()[0].lower() in ["who", "what"]:
            response = self.who_what_query(triplets, g)
        elif phrase.split()[0].lower() in ["where", "when"]:
            response = self.where_when_query(triplets, g)
        elif phrase.split()[0].lower() == "which":
            response = self.which_query(triplets, g)

        return response

    def debug(self):
        return self.debug_dict

    def internal_state(self):
        internal_triplets = []
        g = Graph()
        g.parse(self.rdf_file, format="xml")
        for triplet in g:
            internal_triplets.append(tuple([element.n3().split("/")[-1][:-1]
                                            for element in triplet
                                            ])
                                    )
        internal_triplets = list(filter(lambda t: t[1] != "reference", internal_triplets))
        print(internal_triplets)
