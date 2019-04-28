from sentence_processor import SentenceProcessor


def multiple_cars(phrase):
    sp = SentenceProcessor(phrase)
    return sp.process()

def test_multiple_cars():
    output = [('boy0', 'outraced', 'Charlie'),
              ('boy0', 'property', 'tall'),
              ('boy1', 'outraced', 'Charlie'),
              ('boy1', 'property', 'ugly')
              ]
    assert multiple_cars("The tall boy and the ugly boy outraced Charlie.") == output
