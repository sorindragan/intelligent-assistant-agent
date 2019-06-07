import sys
from gtts import gTTS
import os

from conversation import Conversation
from speech_to_text import SpeechToText


def main():
    c = Conversation()
    speech_to_text = SpeechToText()
    while True:
        # say
        utterance = speech_to_text.process()
        response = c.process(utterance)

        # type
        # utterance = str(sys.stdin.readline())
        # response = c.process(utterance[:-1])

        if response:

            tts = gTTS(text=response, lang='en')
            tts.save("response.mp3")
            os.system("mpg123 response.mp3")

            print("Bot: ",  response)
        if response == "Glad we talked!":
            break
        print()


if __name__ == "__main__":
    main()
