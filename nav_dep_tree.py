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
        dependency_dict[element.text]["children"] = [child.text for child in element.children]
    return dependency_dict

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
    if "nsubjpass" in [sentence_dict[item]["dep"] for item in sentence_dict]:
        agents = [sentence_dict[item]["text"] for item in sentence_dict
                  if sentence_dict[item]["dep"] == "agent"
                 ]
        subject.append(find_object(agents[0], sentence_dict))
        predicate.append([sentence_dict[item]["text"] for item in sentence_dict
                          if sentence_dict[item]["dep"] == "ROOT"
                          ][0])
        object.append([sentence_dict[item]["text"] for item in sentence_dict
                       if sentence_dict[item]["dep"] == "nsubjpass"
                       ][0])
    return [(s, p, o) for (s, p, o) in zip(subject, predicate, object)]

# doc = nlp('Man acts as though he were the shaper and master of language while, in fact, language \
# remains the master of man.')
# doc = nlp('Bob wants that house, but Eve wants the other. Linda likes both houses.')
# doc = nlp('The old beggar ran after the rich man who was wearing a black coat')

def main():
    doc = nlp('The flat tire was not replaced by driver')
    # displacy.serve(doc, style='dep', page=True)

    triplets = []
    sentences = list(doc.sents)
    # split the phrase in sentences
    for s in sentences:
        print(s)
        print(s.root)
    print()

    deps_dict = tree_to_dict(sentences[0])
    pprint(deps_dict)

    root = sentences[0].root
    print(root)

    # test find_object
    obj = find_object('by', deps_dict)
    print("OBJ: ", obj)

    triplets = extract_triplet(deps_dict)

    print(triplets)
    print(findSVOs(doc))

    # print(spacy.explain('pobj'))

if __name__ == "__main__":
    main()
