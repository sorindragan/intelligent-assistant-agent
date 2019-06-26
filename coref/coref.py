"""
.. module:: coref
    :synopsis: the top-level submodule of Intelligent Assistant that aims to create corefference based dialogs.
.. moduleauthor:: Dana-Maria Nica 314C4
"""

import itertools
import spacy
import neuralcoref
# import en_coref_sm  # Small English model for NeuralCoref: a pipeline extension for spaCy 2.0

# Printing Lists as Tabular Data
from tabulate import tabulate

def tabulate_output(rows, headers):
    print(tabulate(rows, headers))
    print("\n \n")

# TO_IGNORE = ['I', 'i', 'me', 'Me', 'you', 'You']

class CorefSolver():

    """Class to provide corefference based dialogs.
    """

    def __init__(self):

        """Initialization method of :class:`NeuralCoref` class.
        """

        # Load your usual SpaCy model (one of SpaCy English models)
        self.nlp  = spacy.load('en')
        # neuralcoref.add_to_pipe(self.nlp, blacklist=True)

        # Add neural coref to SpaCy's pipe
        neuralcoref.add_to_pipe(self.nlp)

        # previous conversations for iterative coreffrence solver
        self.prev = []

        #a container for accessing linguistic annotations for current
        self.doc = None



    def reset_prev(self):
        """
            Resets the previuous conversations list

        """
        self.prev.clear()


    def reset_doc(self):
        """
            Resets the doc container

        """
        self.doc = None

    def add_to_prev(self, conv):
        self.prev.append(conv)

    def unsolved_coref(self):
        """
            param to_solve: the string containing coreffrences
            type to_solve: String
            return: False if no coreffrences
                    a list of unsolved pronoun coreffrences otherwise
        """

        # no coref clusters return all the pronoun in doc
        if self.doc._.coref_clusters is None:
            unsolved_pron_coref = [pron for pron in self.doc if pron.pos_ == 'PRON']

        # get a list of unsolved pronoun coreffrences
        else :
            unsolved_pron_coref = [pron for pron in self.doc if pron.pos_ == 'PRON' and not pron._.in_coref]

        return False if (unsolved_pron_coref == []) else unsolved_pron_coref


    def solve(self, to_solve, previous=False, depth=None, verbose=False):
        """
            param to_solve: the string containig coreffrences
            type to_solve: String
            return: a pair containing string in which each corefering mention is replaced
                    by the main mention in the associated cluster and a list of unsolved
                    pronoun coreffrences
        """

        self.doc = self.nlp(to_solve)
        n_of_sents = len(list(self.doc.sents))
        unsolv_coref = self.unsolved_coref()
        solved_coref = self.doc._.coref_resolved

        if previous is False or self.prev == []:

            if solved_coref == "":
                self.prev.append(to_solve)
            else:
                self.prev.append(solved_coref)

            # if doc._.coref_cluesters is None doc._.coref_resolved
            # is an empty string
            return (solved_coref, unsolv_coref)

        else :

            current_depth = 0
            total_n_of_sents = 1
            iterative_solver = to_solve

            if depth is None:
                depth = len(self.prev)
            else:
                depth = min(depth, len(self.prev))

            while (unsolv_coref != [] and (current_depth != depth)):
                iterative_solver = self.prev[depth - 1 - current_depth] + " . " + iterative_solver
                self.doc = self.nlp(iterative_solver)
                # print(iterative_solver.replace('^', ''))
                unsolv_coref = self.unsolved_coref()
                solved_coref = self.doc._.coref_resolved

                if verbose:
                    tabulate_output([[self.prev[depth - 1 - current_depth]], [iterative_solver], [unsolv_coref]], [current_depth])

                current_depth += 1
                total_n_of_sents += 1

            if solved_coref == "":
                self.prev.append(to_solve)
            else:

#                 print(total_n_of_sents, n_of_sents)
                solved_coref = solved_coref.split('.')[total_n_of_sents - n_of_sents :]
                solved_coref = ' '.join(map(str, solved_coref))
                self.prev.append(solved_coref)
            if verbose:
                tabulate_output([[solved_coref], [unsolv_coref]], ["RESULT"])

            return (solved_coref, unsolv_coref)
