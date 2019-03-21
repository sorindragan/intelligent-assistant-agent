import itertools
import re
import spacy
from spacy import displacy
from subject_object_extraction import findSVOs
from pprint import pprint


nlp = spacy.load('en')


def tree_to_dict(sentence):
    sentence = list(sentence)
    dependency_dict = {}
    for element in sentence:
        dependency_dict[element.text] = {}
        dependency_dict[element.text]["text"] = element.text
        dependency_dict[element.text]["pos"] = element.pos_
        dependency_dict[element.text]["dep"] = element.dep_
        dependency_dict[element.text]["children"] = [child.text
                                                     for child in element.children
                                                     ]
    return dependency_dict


def find_split_marker_advcl(document):
    markers = []
    for item in list(document):
        if item.dep_ == "mark":
            markers.append(item.text)
    return markers


def create_delimiters(markers_list):
    delimiters = ''
    for delimiter in markers_list:
        delimiters += delimiter + '|'
    return delimiters[:-1]


def find_object_passive_voice(agent, sentence_dict):
    agent = sentence_dict[agent]
    if "obj" in agent["dep"]:
        return agent["text"]
    elif agent["children"]:
        for child in agent["children"]:
            return find_object_passive_voice(child, sentence_dict)


def find_subject(root, sentence_dict):
    node = sentence_dict[root]
    if node["dep"] == "nsubj":
        return node["text"]
    elif node["children"]:
        for child in node["children"]:
            return find_subject(child, sentence_dict)


def find_direct_objects(root, sentence_dict, dobjects_list):
    node = sentence_dict[root]
    if node["dep"] == "dobj":
        dobjects_list.append(node["text"])
    if node["children"]:
        for child in node["children"]:
            if sentence_dict[child]["dep"] != "relcl":
                find_direct_objects(child, sentence_dict, dobjects_list)


def find_preposition_objects(root, sentence_dict, pobjects_list):
    node = sentence_dict[root]
    if node["dep"] == "pobj":
        pobjects_list.append(node["text"])
    if node["children"]:
        for child in node["children"]:
            if sentence_dict[child]["dep"] != "relcl":
                find_preposition_objects(child, sentence_dict, pobjects_list)


def find_relatice_clause_root(sentence_dict):
    relcl_list = [sentence_dict[item]["text"] for item in sentence_dict
                  if sentence_dict[item]["dep"] == "relcl"
                  ]
    if relcl_list:
        return relcl_list[0]


def find_all_conjuncts(sentence_dict, conjuncts_list):
    start = sentence_dict[conjuncts_list[-1]]
    if start["children"]:
        for child in start["children"]:
            if sentence_dict[child]["dep"] == "conj":
                conjuncts_list.append(sentence_dict[child]["text"])
                find_all_conjuncts(sentence_dict, conjuncts_list)


# TODO: handle negation?

def verify_compound(term, sentence_dict):
    term = sentence_dict[term]
    term_text = term["text"]
    if term["children"]:
        for child in term["children"]:
            if sentence_dict[child]["dep"] == "compound":
                term_text = sentence_dict[child]["text"] + " " + term_text
    return term_text


def extract_triplet(sentence_dict):
    triplets = []
    tree_root = [sentence_dict[item] for item in sentence_dict
                 if sentence_dict[item]["dep"] == "ROOT"
                 ][0]

    root_conjuncts = [tree_root["text"]]
    find_all_conjuncts(sentence_dict, root_conjuncts)
    relcl_root = find_relatice_clause_root(sentence_dict)
    if relcl_root:
        root_conjuncts.append(relcl_root)

    # passive voice base case
    if "nsubjpass" in [sentence_dict[item]["dep"] for item in sentence_dict]:
        agents = [sentence_dict[item]["text"] for item in sentence_dict
                  if sentence_dict[item]["dep"] == "agent"
                  ]
        pass_subject = find_object_passive_voice(agents[0], sentence_dict)
        pass_subject_conjuncts = [pass_subject]
        find_all_conjuncts(sentence_dict, pass_subject_conjuncts)
        pass_object = [sentence_dict[item]["text"] for item in sentence_dict
                       if sentence_dict[item]["dep"] == "nsubjpass"
                       ][0]
        pass_object_conjuncts = [pass_object]
        find_all_conjuncts(sentence_dict, pass_object_conjuncts)

        for pass_subj, pass_obj in itertools.product(pass_subject_conjuncts, pass_object_conjuncts):
            pass_subj = verify_compound(pass_subj, sentence_dict)
            pass_obj = verify_compound(pass_obj, sentence_dict)
            triplets.append((pass_subj, tree_root["text"], pass_obj))

    # normal
    old_subject = None
    for root in root_conjuncts:
        print("RRRR: ", root)
        if "nsubj" in [sentence_dict[item]["dep"] for item in sentence_dict]:
            nsubject = None
            nsubject = find_subject(root, sentence_dict)
            if nsubject:
                old_subject = nsubject
            if not nsubject and old_subject:
                nsubject = old_subject

            nsubj_conjuncts = [nsubject]
            find_all_conjuncts(sentence_dict, nsubj_conjuncts)

            dobjects = []
            pobjects = []
            find_direct_objects(root, sentence_dict, dobjects)
            find_preposition_objects(root, sentence_dict, pobjects)

            if dobjects:
                dobj_conjuncts = [dobjects[0]]
                find_all_conjuncts(sentence_dict, dobj_conjuncts)
                for subj, dobj in itertools.product(nsubj_conjuncts, dobj_conjuncts):
                    subj = verify_compound(subj, sentence_dict)
                    dobj = verify_compound(dobj, sentence_dict)
                    triplets.append((subj, root, dobj))
            if pobjects:
                pobj_conjuncts = [pobjects[0]]
                find_all_conjuncts(sentence_dict, pobj_conjuncts)
                for subj, pobj in itertools.product(nsubj_conjuncts, pobj_conjuncts):
                    subj = verify_compound(subj, sentence_dict)
                    pobj = verify_compound(pobj, sentence_dict)
                    triplets.append((subj, root, pobj))
            if not (dobjects or pobjects):
                object = [sentence_dict[item]["text"] for item in sentence_dict
                          if (sentence_dict[item]["dep"] == "ccomp"
                              or sentence_dict[item]["dep"] == "xcomp")
                          ][0]
                for subj in nsubj_conjuncts:
                    subj = verify_compound(subj, sentence_dict)
                    object = verify_compound(object, sentence_dict)
                    triplets.append((subj, root, object))

    return triplets


doc_examples = ['Man acts as though he were the shaper and master of language while, in fact, \
                language remains the master of man.',
                'Take two of these and call me in the morning.',
                'I love Maya and hate Sonya.',
                'All you need is love!',
                ]


def main():
    # doc = nlp(phrase)
    # phrase = input("Write text:\n")

    phrase = "The tomato, which is one of the most popular salad ingredients, grows in many shapes and varieties in greenhouses around the world."
    # OK
    # phrase = 'The old beggar ran after the rich man who was wearing a black coat'
    # OK
    # phrase = 'I love Maya and hate Sonya'
    # OK
    # phrase = 'Bob wants the red car, although Eve likes the yellow car. Linda likes both cars.'
    # OK
    # phrase = 'Maia loves Matt, Tim, and John while Jimmy and little Bob really like their funny firends, Sheldon and Chelsea'
    # OK
    # phrase = "Gregory and Tim ordered pepperoni pizza, orange juice, and fresh blueberry ice cream for tonight."
    # OK
    # phrase = 'The flat tire and the bearing were not replaced by driver and his wife'
    doc = nlp(phrase)

    displacy.serve(doc, style='dep', page=True)

    triplets = []
    sentences = list(doc.sents)
    # split the phrase in sentences
    for s in sentences:
        print("Sentence: ", s)
        print("ROOT: ", s.root)
        print()

        clauses = [s]
        # split proposition after the marker when there is an adverbial clause
        if "advcl" in [elem.dep_ for elem in list(doc)]:
            split_markers = find_split_marker_advcl(doc)

            clauses = re.split(create_delimiters(split_markers), s.text)
            clauses = [nlp(c) for c in clauses]

        for c in clauses:
            print("Clause: ", c)
            print()
            displacy.serve(c, style='dep', page=True)
            deps_dict = tree_to_dict(c)
            pprint(deps_dict)

            # # test
            # conj_test = ['cream']
            # print("BEFORE: ", conj_test)
            # find_all_conjuncts(deps_dict, conj_test)
            # print()
            # print("AFTER: ", conj_test)
            #
            # # test2
            # word = 'pizza'
            # print("BEFORE2: ", word)
            # word = verify_compound(word, deps_dict)
            # print()
            # print("AFTER2: ", word)

            triplets = extract_triplet(deps_dict)

            print(triplets)
            print(findSVOs(doc))


if __name__ == "__main__":
    main()
