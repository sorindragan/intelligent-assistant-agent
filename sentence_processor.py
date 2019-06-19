import re
import spacy
from spacy import displacy
from pprint import pprint

from triplet_extractor import TripletExtractor


class SentenceProcessor:

    def __init__(self, phrase, no, verbose=False):
        self.nlp = spacy.load('en')
        self.doc = self.nlp(phrase)
        self.sentences = list(self.doc.sents)
        self.triplets = []
        self.verbose = verbose
        self.debug_dict = {}
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
        extractor = TripletExtractor(no=self.no, verbose=self.verbose)

        for sentence in self.sentences:
            self.debug_dict["sentence"] = sentence
            self.debug_dict["ROOT"] = sentence.root

            clauses = [sentence]
            # split a sentence in multiple sentences after adverbial clause modifiers
            if "advcl" in [elem.dep_ for elem in list(self.doc)]:
                split_markers = self.find_split_marker_advcl(self.doc)
                if split_markers:        
                    clauses = re.split(self.create_delimiters(split_markers), sentence.text)
                    clauses = [self.nlp(c) for c in clauses
                               if c and c not in " ,;" and c not in split_markers
                               ]

            for clause in clauses:
                self.debug_dict["Clause"] = clause
                if isinstance(clause, type(self.nlp(" "))):
                    clause = list(clause.sents)[0]

                clause_triplets = extractor.process(clause, "s")

                self.debug_dict["clause_triplets"] = clause_triplets
                self.triplets += clause_triplets

        final_triplets = list(set(self.triplets))
        final_triplets.sort()
        self.debug_dict["Sentence triplets"] = final_triplets

        if self.verbose:
            pprint(self.debug_dict)

        return final_triplets
