import spacy

nlp = spacy.load('en')
# doc = nlp('Man acts as though he were the shaper and master of language while, in fact, language \
# remains the master of man.')
doc = nlp('Bob wants that house, but Eve wants the other. Linda likes both houses.')
sentences = list(doc.sents)
for s in sentences:
    print(s)
    print(s.root)

print(list(sentences[0].root.children))
root_token = sentences[1].root
subj = None
obj = None
for child in root_token.children:
    print(child)
    if child.dep_ is "nsubj":
        subj = child
    if child.dep_ is "dobj":
        obj = child

print((subj, root_token, obj))
