from sklearn.feature_extraction.text import TfidfVectorizer


class TFIDF:


    """Class to provide text similarity using tf-idf.
    """

    def __init__(self, intents):

        """Initialization method of :class:`TFIDF` class.
        """
        self.intents = intents
        self.vect = TfidfVectorizer(min_df=1)
        self.tfidf = None
        self.sim_matrix = None
        self.idf =  None
        self.vocabulary = None


    def __string(self):
        return str(self.sim_matrix)

    def compute_similarity(self, utterance):
        self.tfidf = self.vect.fit_transform([utterance] + self.intents)
        self.sim_matrix = (self.tfidf * self.tfidf.T).A #similarities matrix of sentences
        self.idf = self.vect.idf_
        self.vocabulary = self.vect.vocabulary_
        return self.intents[(self.sim_matrix[0])[1:].argmax()]                                                                                                                                                                                                                                  


if __name__ == '__main__':


    sentences = [
        "Dogs are awesome.",
        "Some gorgeous creatures are felines.",
        "Dolphins are swimming mammals.",

    ]
 
    focus_sentence = "Cats are beautiful animals."

    w = TFIDF(sentences)
    print(w.compute_similarity(focus_sentence))
    print(w.sim_matrix)    


