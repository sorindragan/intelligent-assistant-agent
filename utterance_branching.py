import random

from conversation import Conversation

class UtteranceBranching:

    def __init__(self, verbose=False):
        self.end_sentences = ["exit", "enough for now", "goodbye", "goodnight",
                              "bye", "that is all", "that's all for now"]
        self.greetings = ["hi", "hello", "hi there", "hello there",
                          "good morning", "good afternoon", "hey"]
        self.wh_list = ["who", "what", "where", "why", "when", "which", "how"]
        self.yes_no_list = ["is", "are", "am", "will", "could", "would", "may",
                            "can", "have", "has", "had", "did", "do", "does",
                            ]
        self.end_replies = ["Glad we talked!", "Happy to help!", "Gooodbye!"]
        self.greetings_replies = ["Hello! What a wonderful day!", "At your disposal!", "Hi there!"]
        self.verbose = verbose
        self.c = Conversation()

    def process(self, phrase):
        bot_reply = ""

        if phrase.lower().strip("!").strip(".") in self.end_sentences:
            bot_reply = random.choice(self.end_replies)
        elif phrase.lower().strip("!").strip(".") in self.greetings:
            bot_reply = random.choice(self.greetings_replies)
        elif ('?' in phrase)  or (phrase.split()[0] in self.wh_list + self.yes_no_list):
            bot_reply = self.c.reply(phrase + "?")
        else:
            self.c.listen(phrase + ".")
            bot_reply = "Roger that!"

        if self.verbose:
            pprint(c.debug())

        return bot_reply
