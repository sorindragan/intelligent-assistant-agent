import spacy
import neuralcoref

nlp = spacy.load('en')

# Let's try before using the conversion dictionary:
neuralcoref.add_to_pipe(nlp)

# Here are three ways we can add the conversion dictionary
nlp.remove_pipe("neuralcoref")
neuralcoref.add_to_pipe(nlp, conv_dict={'Sudo': ['dog']})
doc = nlp(u"I have a dog. My dog's name is Sudo. He has to be fed 2 times a day.")
#print(doc._.coref_scores)
print(doc._.coref_resolved)
