import sys

from conversation import Conversation
from coref.coref import *

def main():
    c = Conversation()
    coref_solver = CorefSolver()
    while True:
        print("You: ", end='', flush=True)
        utterance = str(sys.stdin.readline())
        solved_coref, unsolved_coref = coref_solver.solve(utterance[:-1], previous=True, depth=10)
        if solved_coref == "":
            solved_coref = utterance[:-1]
        
        response = c.process(solved_coref)
        if response:
            print("Bot: ",  response)
        if response == "Glad we talked!":
            break
        print()


if __name__ == "__main__":
    main()
