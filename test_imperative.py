from sentence_processor import SentenceProcessor


def imperative(phrase):
    sp = SentenceProcessor(phrase, 0)
    return sp.process()

def test_imperative():
    output = [('null', 'write', 'book')]

    assert imperative("Write the book!") == output
