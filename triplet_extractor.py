import itertools
import spacy
from pprint import pprint


class TripletExtractor:

    def __init__(self):
        self.triplets = []

    def find_all_conjuncts(self, node, conjuncts_list):
        """ Return list of conjuncts of given node.
            Example: "Ana and Bob went home."
            Bob is a conjunct of Ana.
        """
        if node.children:
            for child in node.children:
                if child.dep_ != "conj":
                    continue
                conjuncts_list.append(child)
                self.find_all_conjuncts(child, conjuncts_list)

    def find_relative_clause_root(self, clause):
        """ Return Relative Clause root if a Relative Cluase exists. """
        relcls = [node
                  for node in list(clause)
                  if node.dep_ == "relcl"
                  ]
        if relcls:
            return relcls[0]

    def find_subject(self, node, nsubj_list):
        """ Return the Nominal Subject. """
        if node.dep_ == "nsubj":
            nsubj_list.append(node)
        if node.children:
            for child in node.children:
                self.find_subject(child, nsubj_list)

    def find_direct_objects(self, node, dobjects_list):
        """ Return the Direct Objects. """
        if node.dep_ == "dobj":
            dobjects_list.append(node)
        if node.children:
            for child in node.children:
                if child.dep_ != "relcl":
                    self.find_direct_objects(child, dobjects_list)

    def find_preposition_objects(self, node, pobjects_list):
        """ Return the Prepositional Objects. """
        if node.dep_ == "pobj":
            pobjects_list.append(node)
        if node.children:
            for child in node.children:
                if child.dep_ != "relcl":
                    self.find_preposition_objects(child, pobjects_list)

    def find_passive_voice_object(self, agent, agent_list):
        """ Return the Passive Voice Object,
            that is the Subject being acted upon.
        """
        if "obj" in agent.dep_:
            agent_list.append(agent)
        if agent.children:
            for child in agent.children:
                self.find_passive_voice_object(child, agent_list)

    def verify_compound(self, node):
        """ Return the Compound in case it exists.
            Example: "orange juice" instead of "juice".
        """
        compound_text = node.text
        if node.children:
            for child in node.children:
                if child.dep_ == "compound":
                    compound_text = child.text + " " + node.text
        return compound_text

    def process(self, clause):
        """ Extract triplets from a simple clause """
        tree_root = clause.root
        print("ROOT: ", tree_root)
        root_conjuncts = [tree_root]
        self.find_all_conjuncts(tree_root, root_conjuncts)
        relcl_root = self.find_relative_clause_root(clause)
        if relcl_root:
            print("RELCL: ", relcl_root)
            root_conjuncts.append(relcl_root)

        print("ROOT_CONJUCTS: ", [node.text for node in root_conjuncts])

        # passive voice case
        if "nsubjpass" in [item.dep_
                           for item in list(clause)
                           ]:
            agent = [item
                     for item in list(clause)
                     if item.dep_ == "agent"
                     ][0]
            pv_subjects = []
            self.find_passive_voice_object(agent, pv_subjects)
            pv_subject_conjuncts = [pv_subjects[0]]
            self.find_all_conjuncts(pv_subject, pv_subject_conjuncts)
            pv_object = [item
                         for item in list(clause)
                         if item.dep_ == "nsubjpass"
                         ][0]
            pv_object_conjnucts = [pv_object]
            self.find_all_conjuncts(pv_object, pv_object_conjnucts)

            for pv_subj, pv_obj in itertools.product(pv_subject_conjuncts, pv_object_conjnucts):
                pv_subj = self.verify_compound(pv_subj)
                pv_obj = self.verify_compound(pv_obj)
                self.triplets.append((pv_subj, tree_root.text, pv_obj))

        # active voice case
        old_subject = None
        for root in root_conjuncts:
            print("CURR ROOT: ", root)
            print([(item.text, item.dep_) for item in list(clause)])
            if "nsubj" in [item.dep_ for item in list(clause)]:
                subjects = []
                self.find_subject(root, subjects)
                nsubject = subjects[0] if subjects else None
                if nsubject:
                    print("FIRST_NSUBJ: ", nsubject)
                    old_subject = nsubject
                if not nsubject and old_subject:
                    nsubject = old_subject

                nsubj_conjuncts = [nsubject]
                print(nsubj_conjuncts)
                self.find_all_conjuncts(nsubject, nsubj_conjuncts)
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
                        self.find_all_conjuncts(dobject, dobj_conjuncts)
                        print("DOBJ_CONJUNCTS ", dobj_conjuncts)
                        for subj, dobj in itertools.product(nsubj_conjuncts, dobj_conjuncts):
                            subj = self.verify_compound(subj)
                            dobj = self.verify_compound(dobj)
                            self.triplets.append((subj, root.text, dobj))
                if pobjects:
                    for pobject in pobjects:
                        pobj_conjuncts = [pobject]
                        self.find_all_conjuncts(pobject, pobj_conjuncts)
                        print("POBJ_CONJUNCTS ", pobj_conjuncts)
                        for subj, pobj in itertools.product(nsubj_conjuncts, pobj_conjuncts):
                            subj = self.verify_compound(subj)
                            pobj = self.verify_compound(pobj)
                            self.triplets.append((subj, root.text, pobj))

                if not (dobjects or pobjects):
                    objects = [item
                              for item in list(clause)
                              if (item.dep_ == "ccomp" or item.dep_ == "xcomp")
                              ]
                    object = "null"
                    if objects:
                        object = objects[0]

                    for subj in nsubj_conjuncts:
                        subj = self.verify_compound(subj)
                        if object != "null":
                            object = self.verify_compound(object)
                        self.triplets.append((subj, root.text, object))

        return self.triplets
