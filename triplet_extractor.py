import itertools
import re
import spacy
from spacy import displacy
from pprint import pprint


class TripletExtractor:

    def __init__(self):
        self.triplets = []

    def find_all_conjuncts(self, node, conjuncts_list):
        if not node.children:
            for child in node.children:
                if child.dep_ != "conj":
                    continue
                conjuncts_list.append(child)
                self.find_all_conjuncts(child, conjuncts_list)

    def find_relatice_clause_root(self, clause):
        relcls = [node
                  for node in list(clause)
                  if node.dep_ == "relcl"
                  ]
        if relcls:
            return relcls[0]

    def find_subject(self, node):
        if node.dep_ == "nsubj":
            return node
        elif node.children:
            for child in node.children:
                return self.find_subject(child)

    def find_direct_objects(self, node, dobjects_list):
        if node.dep_ == "dobj":
            dobjects_list.append(node)
        if node.children:
            for child in node.children:
                if child.dep_ != "relcl":
                    self.find_direct_objects(child, dobjects_list)

    def find_preposition_objects(self, node, pobjects_list):
        if node.dep_ == "pobj":
            pobjects_list.append(node)
        if node.children:
            for child in node.children:
                if child.dep_ != "relcl":
                    self.find_preposition_objects(child, pobjects_list)

    def verify_compound(self, node):
        compound_text = node.text
        if node.children:
            for child in node.children:
                if child.dep_ == "compound":
                    compound_text = child.text + " " + node.text
        return compound_text

    def process(self, clause):
        tree_root = clause.root
        print("ROOT: ", tree_root)
        root_conjuncts = [tree_root]
        self.find_all_conjuncts(tree_root, root_conjuncts)
        relcl_root = self.find_relatice_clause_root(clause)
        if relcl_root:
            print("RELCL: ", relcl_root)
            root_conjuncts.append(relcl_root)

        print("ROOT_CONJUCTS: ", [node.text for node in root_conjuncts])

        old_subject = None
        for root in root_conjuncts:
            print("CURR ROOT: ", root)
            if "nsubj" in [item.dep_ for item in list(clause)]:
                nsubject = None
                nsubject = self.find_subject(root)
                if nsubject:
                    print("NSUBJ_FIRST: ", nsubject)
                    old_subject = nsubject
                if not nsubject and old_subject:
                    nsubject = old_subject

                nsubj_conjuncts = [nsubject]
                self.find_all_conjuncts(root, nsubj_conjuncts)
                print("NSUBJ_CONJUNCTS: ", nsubj_conjuncts)

                dobjects = []
                pobjects = []
                self.find_direct_objects(root, dobjects)
                self.find_preposition_objects(root, pobjects)
                print("DOBJS: ", dobjects)
                print("POBJS: ", pobjects)

                if dobjects:
                    for dobject in dobjects:
                        dobj_conjuncts = [dobject]
                        self.find_all_conjuncts(root, dobjects_list)
                        for subj, dobj in itertools.product(nsubj_conjuncts_text, dobj_conjuncts):
                            subj = self.verify_compound(subj)
                            dobj = self.verify_compound(dobj)
                            self.triplets.append((subj, root.text, dobj))
                if pobjects:
                    for pobject in pobjects:
                        pobj_conjuncts = [pobject]
                        self.find_all_conjuncts(root, pobj_conjuncts)
                        for subj, pobj in itertools.product(nsubj_conjuncts, pobj_conjuncts):
                            subj = self.verify_compound(subj)
                            pobj = self.verify_compound(pobj)
                            self.triplets.append((subj, root.text, pobj))

        return self.triplets
