import sys

from conversation import Conversation


def main():
    c = Conversation()
    while True:
        print("You: ", end='', flush=True)
        utterance = str(sys.stdin.readline())
        response = c.process(utterance[:-1])
        if response:
            print("Bot: ",  response)
        if response == "Glad we talked!":
            break
        print()


if __name__ == "__main__":
    main()
