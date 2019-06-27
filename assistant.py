import os
import sys
from gtts import gTTS

from utterance_branching import UtteranceBranching
from speech_to_text import SpeechToText
from text_similarity.fail_safe import FailSafe
from coref.coref import *

def main():

    fail_safe = FailSafe()
    coref_solver = CorefSolver()

    verbose = False
    if "--verbose" in sys.argv:
        verbose = True
        u = UtteranceBranching(coref_solver, verbose=True)
    else:
        u = UtteranceBranching(coref_solver)

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
            for utterance in utterances:
                print("##################################################")
                print(utterance)
                response = u.process(utterance[:-1])
                print(response)

    if q_file_name:
        with open(q_file_name, "r") as f:
            questions = list(f)
            for q in questions:
                print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
                print(q)
                response = u.process(q[:-1])
                if not response:
                    question, response, similarity =  fail_safe.answer_questions(q)
                    coref_solver.prev.pop()

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

        response = u.process(utterance)

        if response:

            tts = gTTS(text=response, lang='en')
            tts.save("response.mp3")
            os.system("mpg123 response.mp3")

            print("Bot: ",  response)

            if response in ["Glad we talked!", "Happy to help!", "Gooodbye!"]:
                break

        else:
            question, response, similarity = fail_safe.answer_questions(utterance)
            coref_solver.prev.pop()
            print("Bot: ",  response)

            tts = gTTS(text=response, lang='en')
            tts.save("response.mp3")
            os.system("mpg123 response.mp3")

        print()


if __name__ == "__main__":
    main()
