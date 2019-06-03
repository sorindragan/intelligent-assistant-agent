import sys

from conversation import Conversation
from coref.coref import *

def main():
    c = Conversation()
    coref_solver = CorefSolver()
    while True:
        print("You: ", end='', flush=True)
        utterance = str(sys.stdin.readline())
        solved_coref = coref_solver.solve(utterance)
        print(solved_coref)
        response = c.process(utterance[:-1])
        if response:
            print("Bot: ",  response)
        if response == "Glad we talked!":
            break
        print()


if __name__ == "__main__":
    main()
