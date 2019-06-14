import re
import spacy
from spacy import displacy
from pprint import pprint

from triplet_extractor import TripletExtractor


class QuestionProcessor:

    def __init__(self, phrase, verbose=False):
        self.nlp = spacy.load('en')
        self.doc = self.nlp(phrase)
        self.sentences = list(self.doc.sents)
        self.triplets = []
        self.verbose = verbose
        self.debug_dict = {}

    def display_tree(self):
        """ Display the dependency tree at localhost:5000 """
        displacy.serve(self.doc, style='dep', page=True)

    def process(self):
        """ Extract all triplets from given phrase """
        extractor = TripletExtractor(no = 0, verbose=self.verbose)

        for sentence in self.sentences:
            self.debug_dict["Sentence"] = sentence
            self.debug_dict["ROOT"] = sentence.root

            question_triplets = extractor.process(sentence, "q")
            self.debug_dict["question_triplets"] = question_triplets
            self.triplets += question_triplets

        self.triplets = list(set(self.triplets))
        self.triplets.sort()
        self.debug_dict["Question_Triplets"] = self.triplets
        if self.verbose:
            pprint(self.debug_dict)
        return self.triplets
