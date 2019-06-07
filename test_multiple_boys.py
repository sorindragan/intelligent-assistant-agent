from sentence_processor import SentenceProcessor


def multiple_boys(phrase):
    sp = SentenceProcessor(phrase, 0)
    return sp.process()

def test_multiple_boys():
    output = [('boy0', 'outraced', 'charlie'),
              ('boy0', 'property', 'tall'),
              ('boy1', 'outraced', 'charlie'),
              ('boy1', 'property', 'ugly')
              ]
    assert multiple_boys("The tall boy and the ugly boy outraced Charlie.") == output
