import os
import sys
from gtts import gTTS

from conversation import Conversation
from speech_to_text import SpeechToText


def main():

    if "--verbose" in sys.argv:
        c = Conversation(verbose=True)
    else:
        c = Conversation()

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
                print(c.process(str(u)[:-1]))

    if q_file_name:
        with open(q_file_name, "r") as f:
            questions = list(f)
            for q in questions:
                print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
                print(q)
                print(c.process(str(q)[:-1]))
            return

    speech_to_text = SpeechToText()

    while True:
        # say
        # utterance = speech_to_text.process()
        # response = c.process(utterance)

        # type
        utterance = str(sys.stdin.readline())
        response = c.process(utterance[:-1])

        if response:

            tts = gTTS(text=response, lang='en')
            tts.save("response.mp3")
            os.system("mpg123 response.mp3")

            print("Bot: ",  response)
        if response in ["Glad we talked!", "Happy to help!", "Gooodbye!"]:
            break
        print()


if __name__ == "__main__":
    main()
