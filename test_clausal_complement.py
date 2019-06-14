from sentence_processor import SentenceProcessor


def clausal_complement(phrase):
    sp = SentenceProcessor(phrase, 0)
    return sp.process()

def test_clausal_complement():
    output = [('i', 'expect', 'call'),
              ('john', 'call', 'in morning'),
              ('john', 'call', 'me'),
              ('morning', 'property', 'busy'),
              ('morning', 'property', 'next')
              ]

    assert clausal_complement("I expect John to call me in the next busy morning") == output
