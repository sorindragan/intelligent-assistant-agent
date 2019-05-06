from sentence_processor import SentenceProcessor


def multiple_boys(phrase):
    sp = SentenceProcessor(phrase)
    return sp.process()

def test_multiple_boys():
    output = [('boy0', 'outraced', 'Charlie'),
              ('boy0', 'property', 'tall'),
              ('boy1', 'outraced', 'Charlie'),
              ('boy1', 'property', 'ugly')
              ]
    assert multiple_boys("The tall boy and the ugly boy outraced Charlie.") == output
