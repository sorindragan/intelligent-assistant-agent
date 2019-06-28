from text_similarity.wordnet import WordNetSimilarity
from random import choice
import json

class FailSafe:
    """
        FailSafe Mechanism
    """

    def __init__(self, treshold=0.7):
        self.questions = self.load_questions()
        self.treshold = treshold
        self.fail_answer = ["I didn't understand that. Could you rephrase that?", "Sory I don't understand"]

    def load_questions(self):
        """
        Loads the questions and answers for the FailSafe
        Mechanism
        """
        with open('text_similarity/questions.txt') as json_file:
            data = json.load(json_file)
            # print([*data])
            return data
        return None

    def answer_questions(self, to_answer, verbose=False):
        """

        """
        similarity_solver = WordNetSimilarity([*self.questions], to_answer)
        question, similarity = similarity_solver.compute_similarity()

        if similarity >= self.treshold:
            return question, choice(self.questions[question]), similarity
        else:
            return to_answer, choice(self.fail_answer), similarity

# if __name__ == '__main__':
#
#
#     sentences = [
#         "What's the purpose of life?",
#         "What's the meaning of life?",
#         "Describe yourself?"
#     ]
#
#
#     f = FailSafe ()
#     for sentence in sentences:
#         print()
#         print(f.answer_questions(sentence))
