import os
import sys
from gtts import gTTS

from utterance_branching import UtteranceBranching
from coref.coref import *
from speech_to_text import SpeechToText
from text_similarity.fail_safe import FailSafe

def main():
    coref_solver = CorefSolver()
    fail_safe = FailSafe()
    verbose = False
    if "--verbose" in sys.argv:
        verbose = True
        u = UtteranceBranching(verbose=True)
    else:
        u = UtteranceBranching()

    kb_file_name = None
    if "--kb" in sys.argv:
        pos = sys.argv.index("--kb")
        kb_file_name = sys.argv[pos + 1]

    q_file_name = None
    if "--q" in sys.argv:
        pos = sys.argv.index("--q")
        q_file_name = sys.argv[pos + 1]

    if kb_file_name:
        with open(kb_file_name, "r") as f:
            utterances = list(f)
            for u in utterances:
                print("##################################################")
                print(u)
                solved_coref, unsolved_coref = coref_solver.solve(u[:-1], previous=True, depth=10, verbose=verbose)
                if solved_coref == "":
                    solved_coref = u[:-1]
                print("***********")
                print(solved_coref)
                print("***********")
                response = u.process(solved_coref.strip())
                print(response)

    if q_file_name:
        with open(q_file_name, "r") as f:
            questions = list(f)
            for q in questions:
                print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
                print(q)
                response = u.process(q)
                if not response:
                    question, response, similarity =  fail_safe.answer_questions(solved_coref)
                print("Bot: ",  response)
            return

    speech_to_text = SpeechToText()

    while True:

        # type or say
        print("Write Something or press V for voice input: ", end='', flush=True)
        utterance = str(sys.stdin.readline())

        if utterance[:-1].lower() == "v":
            utterance = speech_to_text.process()
            print(utterance)
        else:
            utterance = utterance[:-1]

        solved_coref, unsolved_coref = coref_solver.solve(utterance, previous=True, depth=5, verbose=True)
        if solved_coref == "":
            solved_coref = utterance
        response = u.process(solved_coref.strip())

        # response = c.process(utterance[:-1])

        if response:

            tts = gTTS(text=response, lang='en')
            tts.save("response.mp3")
            os.system("mpg123 response.mp3")

            print("Bot: ",  response)

            if response in ["Glad we talked!", "Happy to help!", "Gooodbye!"]:
                break

        else:
            question, response, similarity =  fail_safe.answer_questions(solved_coref)
            print("Bot: ",  response)

            tts = gTTS(text=response, lang='en')
            tts.save("response.mp3")
            os.system("mpg123 response.mp3")

        print()


if __name__ == "__main__":
    main()
