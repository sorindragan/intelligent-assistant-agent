import re
import spacy
from spacy import displacy
from subject_object_extraction import findSVOs
from pprint import pprint


nlp = spacy.load('en')
ADV_CL_MARKERS = ["after", "although", "as", "because", "before", "by the time",
                  "even if", "even though", "every time", "if", "in case",
                  "just in case", "like", "now that", "once", "only if",
                  "rather than", "since", "so that", "than", "that", "though",
                  "until", "when", "whenever", "where", "whereas", "wherever",
                  "whether", "whether or not", "while", "why",
                  ]


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

# TODO: implement this
def search_conjuncts():
    return None

def find_object(agent, sentence_dict):
    agent = sentence_dict[agent]
    # print(agent["text"], agent["dep"], agent["children"])
    if "obj" in agent["dep"]:
        return agent["text"]
    elif agent["children"]:
        for child in agent["children"]:
            return find_object(child, sentence_dict)

def extract_triplet(sentence_dict):
    subject = []
    predicate = []
    object = []
    root = [sentence_dict[item]["text"] for item in sentence_dict
            if sentence_dict[item]["dep"] == "ROOT"
            ][0]
    # passive
    if "nsubjpass" in [sentence_dict[item]["dep"] for item in sentence_dict]:
        agents = [sentence_dict[item]["text"] for item in sentence_dict
                  if sentence_dict[item]["dep"] == "agent"
                 ]
        subject.append(find_object(agents[0], sentence_dict))
        predicate.append(root)
        object.append([sentence_dict[item]["text"] for item in sentence_dict
                       if sentence_dict[item]["dep"] == "nsubjpass"
                       ][0])
    # normal
    if "nsubj" in [sentence_dict[item]["dep"] for item in sentence_dict]:
        nsubject = [sentence_dict[item]["text"] for item in sentence_dict
                    if sentence_dict[item]["dep"] == "nsubj"
                    ][0]
        dobjects = [sentence_dict[item]["text"] for item in sentence_dict
                    if sentence_dict[item]["dep"] == "dobj"
                    ]
        pobjects = [sentence_dict[item]["text"] for item in sentence_dict
                    if sentence_dict[item]["dep"] == "pobj"
                    ]
        if dobjects:
            for dobj in dobjects:
                subject.append(nsubject)
                predicate.append(root)
                object.append(dobj)
        elif pobjects:
            for pobj in pobjects:
                subject.append(nsubject)
                predicate.append(root)
                object.append(pobj)
        else:
            subject.append(nsubject)
            predicate.append(root)
            object.append([sentence_dict[item]["text"] for item in sentence_dict
                           if sentence_dict[item]["dep"] == "xcomp"
                           ][0])

    return [(s, p, o) for (s, p, o) in zip(subject, predicate, object)]

doc_examples = ['Man acts as though he were the shaper and master of language while, in fact, \
                language remains the master of man.', 'Bob wants that house, but Eve wants the other. \
                Linda likes both houses.', 'The old beggar ran after the rich man who was wearing \
                a black coat', 'The flat tire and the bearing was not replaced by driver',
                'Take two of these and call me in the morning.',
                ]

def main():
    # phrase = input("Write text:\n")
    # doc = nlp(phrase)

    phrase = 'Maia loves Matt, Tim, and John while Jimmy and little Bob really like their gay firends Sheldon and Chelsea'
    doc = nlp(phrase)

    # displacy.serve(doc, style='dep', page=True)


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

            clauses = re.split(create_delimiters(split_markers), phrase)
            clauses = [nlp(c) for c in clauses]

        for c in clauses:
            displacy.serve(c, style='dep', page=True)
            deps_dict = tree_to_dict(c)
            pprint(deps_dict)

            triplets = extract_triplet(deps_dict)

            print(triplets)
            print(findSVOs(doc))


if __name__ == "__main__":
    main()
