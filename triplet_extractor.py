import itertools
import spacy
from collections import Counter
from pprint import pprint


class TripletExtractor:

    def __init__(self, no, verbose=False):
        self.triplets = []
        self.concept_object_no = no
        self.verbose = verbose
        self.debug_dict = {}

    def find_particle(self, root):
        """ In case of phrasal verbs, return the particle
            Example: "blow up" instead of "blow"
        """
        particle = ""
        if root.children:
            for child in root.children:
                if child.dep_ == "prt":
                    particle = child.text
        return particle

    def check_attr(self, root, concept_objects_props):
        """ Find the attribute introduced by the root in case it exists
            and use it to introduce a concept object and a property
            Example: "pizza is italian"
            will result in (pizza, is, @1) and (@1, "property", "italian")
        """
        if root.children:
            for child in root.children:
                if child.dep_ == "attr":
                    concept_objects_props.append(("at" + str(self.concept_object_no), child))
                    self.concept_object_no += 1

    def check_predicative_adjectives(self, root):
        """ In case of a nominal predicate
            replace the root with the adjectival complement
            Example: "faster" instead of "is" in the "is faster" construction
        """
        new_root = root.text
        if root.children:
            for child in root.children:
                if child.dep_ == "acomp":
                    new_root = child.text
        return new_root

    def find_property(self, node, descriptions):
        """ Return properties of a subject/object <Name>
            that will be forming a (<Name>, "property", property) triplet
        """
        if node.children:
            for child in node.children:
                if child.dep_ == "amod":
                    descriptions.append(child)

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

    def find_subject(self, node, nsubj_list, next_root):
        """ Return the Nominal Subject. """
        if node.dep_ == "nsubj":
            nsubj_list.append(node)
        if node.children:
            for child in node.children:
                if next_root and child.dep_ == "conj" and child == next_root:
                   continue
                self.find_subject(child, nsubj_list, next_root)

    def find_direct_objects(self, node, dobjects_list, next_root):
        """ Return the Direct Objects. """
        if node.dep_ == "dobj":
            dobjects_list.append(node)
        if node.children:
            for child in node.children:
                if next_root and child.dep_ == "conj" and child == next_root:
                   continue
                if child.dep_ != "relcl":
                    self.find_direct_objects(child, dobjects_list, next_root)

    def find_preposition_objects(self, node, pobjects_list, next_root):
        """ Return the Prepositional Objects. """
        if node.dep_ == "pobj":
            pobjects_list.append(node)
        if node.children:
            for child in node.children:
                if next_root and child.dep_ == "conj" and child == next_root:
                   continue
                if child.dep_ != "relcl":
                    self.find_preposition_objects(child, pobjects_list, next_root)

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

    def process(self, clause, type):
        """ Extract triplets from a clause """
        tree_root = clause.root
        self.debug_dict["ROOT"] = tree_root
        # initial sentence root
        root_conjuncts = [tree_root]
        # all predicates in the sentence
        self.find_all_conjuncts(tree_root, root_conjuncts)
        relcl_root = self.find_relative_clause_root(clause)

        if relcl_root:
            self.debug_dict["RELCL"] = relcl_root
            root_conjuncts.append(relcl_root)

        self.debug_dict["ROOT_CONJUCTS"] = [node.text for node in root_conjuncts]

        # simple passive voice case
        pv_subjects = []
        if "nsubjpass" in [item.dep_
                           for item in list(clause)
                           ]:
            agent = [item
                     for item in list(clause)
                     if item.dep_ == "agent"
                     ][0]

            self.find_passive_voice_object(agent, pv_subjects)
            pv_subject = pv_subjects[0]
            pv_subject_conjuncts = [pv_subject]
            self.find_all_conjuncts(pv_subject, pv_subject_conjuncts)

            pv_object = [item
                         for item in list(clause)
                         if item.dep_ == "nsubjpass"
                         ][0]
            pv_object_conjnucts = [pv_object]
            self.find_all_conjuncts(pv_object, pv_object_conjnucts)

            for pv_subj, pv_obj in itertools.product(pv_subject_conjuncts, pv_object_conjnucts):
                subj_properties = []
                obj_properties = []

                self.find_property(pv_subj, subj_properties)
                self.find_property(pv_obj, obj_properties)

                pv_subj = self.verify_compound(pv_subj)
                pv_obj = self.verify_compound(pv_obj)

                if subj_properties:
                    for prop in subj_properties:
                        self.triplets.append((pv_subj, "property", prop.text))

                if obj_properties:
                    for prop in obj_properties:
                        self.triplets.append((pv_obj, "property", prop.text))

                self.triplets.append((pv_subj, tree_root.text, pv_obj))

        # active voice case
        old_subject = None
        for no, root in enumerate(root_conjuncts):
            # consider each subtree of every predicate independetly
            if no + 1 < len(root_conjuncts):
                next_root = root_conjuncts[no + 1]
            else:
                next_root = None

            particle = self.find_particle(root)
            self.debug_dict["CURR_ROOT"] = root
            self.debug_dict["Deps"] = [(item.text, item.dep_) for item in list(clause)]

            nsubj_conjuncts = []
            if "nsubj" in [item.dep_ for item in list(clause)]:
                subjects = []
                self.find_subject(root, subjects, next_root)
                nsubject = subjects[0] if subjects else None

                # check if there is a new subject
                # or the same subject does another action
                if nsubject:
                    self.debug_dict["FIRST_NSUBJ"] = nsubject
                    old_subject = nsubject
                if not nsubject and old_subject:
                    nsubject = old_subject

                nsubj_conjuncts = [nsubject]
                self.find_all_conjuncts(nsubject, nsubj_conjuncts)
                self.debug_dict["NSUBJ_CONJUNCTS"] = nsubj_conjuncts

            elif not pv_subjects:
                if type == "q":
                    nsubj_conjuncts = [item for item in list(clause)
                                       if item.dep_ == "npadvmod"
                                       ]
                    nsubj_conjuncts+= [item for item in list(clause)
                                       if item.text.lower() == "who"
                                       ]
                    self.debug_dict["NSUBJ_CONJUNCTS_Q"] = nsubj_conjuncts
                # imperative sentences (no subject)
                else:
                    nsubj_conjuncts = [spacy.load('en')("null")[0]]
                    self.debug_dict["NSUBJ_CONJUNCTS_ELSE"] =  nsubj_conjuncts

            dobjects = []
            pobjects = []
            self.find_direct_objects(root, dobjects, next_root)
            self.find_preposition_objects(root, pobjects, next_root)

            # clausal components
            cobjects = [item
                      for item in list(clause)
                      if (item.dep_ == "ccomp" or item.dep_ == "xcomp")
                      ]

            self.debug_dict["DOBJS"] = dobjects
            self.debug_dict["POBJS"] = pobjects
            self.debug_dict["COBJS"] = cobjects

            if dobjects and not cobjects:
                for dobject in dobjects:
                    dobj_conjuncts = [dobject]
                    self.find_all_conjuncts(dobject, dobj_conjuncts)
                    self.debug_dict["DOBJ_CONJUNCTS"] = dobj_conjuncts
                    # number instances of objects if they are of the same type
                    counter_subj = Counter([subj.text for subj in nsubj_conjuncts]) \
                                    if nsubj_conjuncts else 0
                    counter_dobj = Counter([dobj.text for dobj in dobj_conjuncts]) \
                                    if dobj_conjuncts else 0

                    # handle multiple identical words
                    for i, subj in enumerate(nsubj_conjuncts):
                        for j, dobj in enumerate(dobj_conjuncts):
                            subj_idx = ""
                            dobj_idx = ""
                            if subj.text == dobj.text:
                                subj_idx = str(i)
                                dobj_idx = str(j + len(nsubj_conjuncts))
                            if counter_subj[subj.text] > 1:
                                subj_idx = str(i)
                            if counter_dobj[dobj.text] > 1:
                                dobj_idx = str(j + len(nsubj_conjuncts))

                            subj_properties = []
                            dobj_properties = []
                            self.find_property(subj, subj_properties)
                            self.find_property(dobj, dobj_properties)

                            subj_c = self.verify_compound(subj)
                            dobj_c = self.verify_compound(dobj)

                            if subj_properties:
                                for prop in subj_properties:
                                    self.triplets.append((subj_c + subj_idx, "property", prop.text))
                            if dobj_properties:
                                for prop in dobj_properties:
                                    self.triplets.append((dobj_c + dobj_idx, "property", prop.text))

                            pred = self.check_predicative_adjectives(root)
                            if particle:
                                particle = " " + particle

                            attr_tuples = []
                            self.check_attr(root, attr_tuples)
                            if attr_tuples:
                                for tuple in attr_tuples:
                                    abstract_obj, prop = tuple[0], tuple[1]
                                    properties = []
                                    self.find_property(prop, properties)
                                    prop_c = self.verify_compound(prop)
                                    for p in properties:
                                        self.triplets.append((abstract_obj, "property", p.text))
                                    self.triplets.append((abstract_obj, "is_a", prop_c))
                                    self.triplets.append((subj_c + subj_idx, pred + particle, abstract_obj))

                            self.triplets.append((subj_c + subj_idx, pred + particle, dobj_c + dobj_idx))
            if pobjects and not cobjects:
                for pobject in pobjects:
                    pobj_conjuncts = [pobject]
                    preposition = pobject.head.text + " "
                    self.find_all_conjuncts(pobject, pobj_conjuncts)
                    self.debug_dict["POBJ_CONJUNCTS"] = pobj_conjuncts
                    # number instances of objects if they are of the same type
                    counter_subj = Counter([subj.text for subj in nsubj_conjuncts]) \
                                    if nsubj_conjuncts else 0
                    counter_pobj = Counter([pobj.text for pobj in pobj_conjuncts]) \
                                    if pobj_conjuncts else 0

                    # handle multiple identical words
                    for i, subj in enumerate(nsubj_conjuncts):
                        for j, pobj in enumerate(pobj_conjuncts):
                            subj_idx = ""
                            pobj_idx = ""
                            if subj.text == pobj.text:
                                subj_idx = str(i)
                                pobj_idx = str(j + len(nsubj_conjuncts))
                            if counter_subj[subj.text] > 1:
                                subj_idx = str(i)
                            if counter_pobj[pobj.text] > 1:
                                pobj_idx = str(j + len(nsubj_conjuncts))

                            subj_properties = []
                            pobj_properties = []
                            self.find_property(subj, subj_properties)
                            self.find_property(pobj, pobj_properties)

                            subj_c = self.verify_compound(subj)
                            pobj_c = self.verify_compound(pobj)

                            if subj_properties:
                                for prop in subj_properties:
                                    self.triplets.append((subj_c + subj_idx, "property", prop.text))
                            if pobj_properties:
                                for prop in pobj_properties:
                                    self.triplets.append((pobj_c + pobj_idx, "property", prop.text))

                            pred = self.check_predicative_adjectives(root)
                            if particle:
                                particle = " " + particle

                            attr_tuples = []
                            self.check_attr(root, attr_tuples)
                            if attr_tuples:
                                for tuple in attr_tuples:
                                    abstract_obj, prop = tuple[0], tuple[1]
                                    properties = []
                                    self.find_property(prop, properties)
                                    prop_c = self.verify_compound(prop)
                                    for p in properties:
                                        self.triplets.append((abstract_obj, "property", p.text))
                                    self.triplets.append((abstract_obj, "is_a", prop_c))
                                    self.triplets.append((subj_c + subj_idx, pred + particle, abstract_obj))

                            self.triplets.append((subj_c + subj_idx, pred + particle, preposition + pobj_c + pobj_idx))

            # number subjects in sentence
            counter_subj = Counter([subj.text for subj in nsubj_conjuncts]) \
                                    if nsubj_conjuncts else 0

            if cobjects:
                self.debug_dict["IC"] = "INSIDE CLAUSAL"
                object = cobjects[0]

                # handle multiple identical subjects
                for i, subj in enumerate(nsubj_conjuncts):
                    subj_idx = ""
                    if counter_subj[subj.text] > 1:
                        subj_idx = str(i)

                    subj_properties = []
                    self.find_property(subj, subj_properties)
                    subj_c = self.verify_compound(subj)

                    if subj_properties:
                        for prop in subj_properties:
                            self.triplets.append((subj_c + subj_idx, "property", prop.text))

                    pred = self.check_predicative_adjectives(root)
                    if particle:
                        particle = " " + particle

                    attr_tuples = []
                    self.check_attr(root, attr_tuples)
                    if attr_tuples:
                        for tuple in attr_tuples:
                            abstract_obj, prop = tuple[0], tuple[1]
                            properties = []
                            self.find_property(prop, properties)
                            prop_c = self.verify_compound(prop)
                            for p in properties:
                                self.triplets.append((abstract_obj, "property", p.text))
                            self.triplets.append((abstract_obj, "is_a", prop_c))
                            self.triplets.append((subj_c + subj_idx, pred + particle, abstract_obj))

                    self.triplets.append((subj_c + subj_idx, pred + particle, object.text))

                clausal_subj = subjects[-1] if subjects else "null"
                clausal_pred = object.text
                c_subj_c = self.verify_compound(clausal_subj)
                c_subj_properties = []
                self.find_property(clausal_subj, c_subj_properties)
                for prop in c_subj_properties:
                    self.triplets.append((c_subj_c, "property", prop.text))

                if pobjects:
                    self.debug_dict["CWP"] = "Clausal with pobject"
                    for pobj in pobjects:
                        preposition = pobj.head.text + " "
                        c_pobj_properties = []
                        self.find_property(pobj, c_pobj_properties)
                        for prop in c_pobj_properties:
                            self.triplets.append((pobj.text, "property", prop.text))
                        self.triplets.append((c_subj_c, clausal_pred, preposition + pobj.text))

                if dobjects:
                    self.debug_dict["CWD"] = "Clausal with dobject"
                    for dobj in dobjects:
                        c_dobj_properties = []
                        self.find_property(dobj, c_dobj_properties)
                        for prop in c_dobj_properties:
                            self.triplets.append((dobj.text, "property", prop.text))
                        self.triplets.append((c_subj_c, clausal_pred, dobj.text))

            elif not pobjects and not dobjects:
                self.debug_dict["CWW"] = "Clausal with other objects"
                for i, subj in enumerate(nsubj_conjuncts):
                    subj_idx = ""
                    if counter_subj[subj.text] > 1:
                        subj_idx = str(i)

                    subj_properties = []
                    self.find_property(subj, subj_properties)
                    subj_c = self.verify_compound(subj)

                    if subj_properties:
                        for prop in subj_properties:
                            self.triplets.append((subj_c + subj_idx, "property", prop.text))

                    pred = self.check_predicative_adjectives(root)
                    if particle:
                        particle = " " + particle

                    attr_tuples = []
                    self.check_attr(root, attr_tuples)
                    if "who" in [item.text.lower() for item in nsubj_conjuncts]:
                        attr_tuples = filter(lambda t: t[1].text.lower() != "who", attr_tuples)
                    self.debug_dict["attrs"] = attr_tuples
                    if attr_tuples:
                        for tuple in attr_tuples:
                            abstract_obj, prop = tuple[0], tuple[1]
                            properties = []
                            self.find_property(prop, properties)
                            prop_c = self.verify_compound(prop)
                            for p in properties:
                                self.triplets.append((abstract_obj, "property", p.text))
                            self.triplets.append((abstract_obj, "is_a", prop_c))
                            self.triplets.append((subj_c + subj_idx, pred + particle, abstract_obj))

            if not (dobjects or pobjects or cobjects or [item for item in list(clause) if item.dep_ == "attr"]):
                self.debug_dict["WO"] = "Without objects"
                for i, subj in enumerate(nsubj_conjuncts):
                    subj_idx = ""
                    if counter_subj[subj.text] > 1:
                        subj_idx = str(i)

                    subj_properties = []
                    self.find_property(subj, subj_properties)
                    subj_c = self.verify_compound(subj)

                    if subj_properties:
                        for prop in subj_properties:
                            self.triplets.append((subj_c + subj_idx, "property", prop.text))

                    pred = self.check_predicative_adjectives(root)
                    if particle:
                        particle = " " + particle

                    self.triplets.append((subj_c + subj_idx, pred + particle, "null"))

        self.triplets = [(t[0].lower(), t[1].lower(), t[2].lower())
                         for t in self.triplets
                         ]

        if self.verbose:
            pprint(self.debug_dict)

        return self.triplets
