import spacy
import neuralcoref
#
# nlp = spacy.load('en')
#
# # Let's try before using the conversion dictionary:
# neuralcoref.add_to_pipe(nlp)
#
# # Here are three ways we can add the conversion dictionary
# # nlp.remove_pipe("neuralcoref")
# # neuralcoref.add_to_pipe(nlp, conv_dict={'Sudo': ['dog']})
# doc = nlp(u"On Monday, I am meeting Andreea. . She is my best friend.")
# #print(doc._.coref_scores)
# print(doc._.coref_resolved)

from coref import CorefSolver

c = CorefSolver()

response = c.solve("On Monday I am meeting Andreea.", previous=True, verbose=True)
response = c.solve("She is my best friend.", previous=True, verbose=True)
