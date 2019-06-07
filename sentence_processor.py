import re
import spacy
from spacy import displacy
from pprint import pprint

from triplet_extractor import TripletExtractor


class SentenceProcessor:

    def __init__(self, phrase, no):
        self.nlp = spacy.load('en')
        self.doc = self.nlp(phrase)
        self.sentences = list(self.doc.sents)
        self.triplets = []
        self.no = no

    def find_split_marker_advcl(self, document):
        """ Return markers in case of Adverbial Clause.
            Adverbial Clause Markers:
                  "after", "although", "as", "because", "before", "by the time",
                  "even if", "even though", "every time", "if", "in case",
                  "just in case", "like", "now that", "once", "only if",
                  "rather than", "since", "so that", "than", "that", "though",
                  "until", "when", "whenever", "where", "whereas", "wherever",
                  "whether", "whether or not", "while", "why".
        """
        markers = []
        for item in list(document):
            if item.dep_ == "mark":
                markers.append(item.text)
        return markers

    def create_delimiters(self, markers_list):
        """ Create delimiters that will go into the spilt function """
        delimiters = ''
        for delimiter in markers_list:
            delimiters += '(' + delimiter + ')( |,|;)|'
        return delimiters[:-1]

    def display_tree(self):
        """ Display the dependency tree at localhost:5000 """
        displacy.serve(self.doc, style='dep', page=True)

    def process(self):
        """ Extract all triplets from given phrase """
        extractor = TripletExtractor(self.no)

        for sentence in self.sentences:
            print("Sentence: ", sentence)
            print("ROOT: ", sentence.root)

            clauses = [sentence]
            # split a sentence in multiple sentences after adverbial clause modifiers
            if "advcl" in [elem.dep_ for elem in list(self.doc)]:
                split_markers = self.find_split_marker_advcl(self.doc)
                clauses = re.split(self.create_delimiters(split_markers), sentence.text)
                clauses = [self.nlp(c) for c in clauses
                           if c and c not in " ,;" and c not in split_markers
                           ]

            for clause in clauses:
                print("Clause: ", clause)
                if isinstance(clause, type(self.nlp(" "))):
                    clause = list(clause.sents)[0]

                clause_triplets = extractor.process(clause, "s")

                print(clause_triplets)
                self.triplets += clause_triplets

        final_triplets = list(set(self.triplets))
        final_triplets.sort()
        print("Sentence triplets: ", final_triplets)
        return final_triplets
