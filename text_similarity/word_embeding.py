import sys
from joblib import Memory
from gensim.models import KeyedVectors

mem = Memory("./mycache")

@mem.cache
def load_model(wordmodelfile):
    wordmodel = KeyedVectors.load_word2vec_format(wordmodelfile, binary=True, limit=500000)
    return wordmodel

class WordEmbed:

    def w2v(self, s1, s2, wordmodel):

        if s1 == s2:
                return 1.0

        s1words = s1.split()
        s2words = s2.split()
        s1wordsset = set(s1words)
        s2wordsset = set(s2words)
        vocab = wordmodel.vocab #the vocabulary considered in the word embeddings

        if len(s1wordsset & s2wordsset)==0:
                return 0.0
        for word in s1wordsset.copy(): #remove sentence words not found in the vocab
            if (word not in vocab):
                s1words.remove(word)

        for word in s2wordsset.copy(): #idem
            if (word not in vocab):
                s2words.remove(word)
        
        return wordmodel.n_similarity(s1words, s2words)

if __name__ == '__main__':
   
    wordmodelfile="../../GoogleNews-vectors-negative300.bin.gz"
    w = WordEmbed()
    wordmodel = load_model(wordmodelfile)
    s1="Dogs are awesome."
    print(s1)
    s2="Some gorgeous creatures are dogs.”"
    print("sim(s1,s2) = ", w.w2v(s1,s2,wordmodel),"/1.")
    s3="What is the meaning of life?"
    s4="What's the sense of life?"
    print("sim(s3,s4) = ", w.w2v(s3,s4,wordmodel),"/1.")
