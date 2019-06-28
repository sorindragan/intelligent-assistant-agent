from sentence_processor import SentenceProcessor


def passive_voice(phrase):
    sp = SentenceProcessor(phrase, 0)
    return sp.process()

def test_passive_voice():
    output = [('i', 'watching', 'them'),
              ('mechanic', 'property', 'old'),
              ('mechanic', 'replaced', 'truck'),
              ('mechanic', 'replaced', 'wheel'),
              ('wife', 'property', 'short'),
              ('wife', 'replaced', 'truck'),
              ('wife', 'replaced', 'wheel')
              ]

    assert all([triplet for triplet in output if
                triplet in passive_voice("The wheel and the truck were replaced by \
                the old mechanic and his short wife while I was watching them.")
                ])
