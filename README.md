[![Build Status](https://travis-ci.com/sorindragan/intelligent-assistant-agent.png)](https://travis-ci.com/sorindragan/intelligent-assistant-agent)
[![spaCy](https://img.shields.io/badge/made%20with-spaCy-blue.svg)](https://spacy.io)
[![neuralcoref](https://img.shields.io/badge/made%20with-neuralcoref-blueviolet.svg)](https://huggingface.co/coref)


## Intelligent Assistant Agent

Usage Examples:


1) Running the assistant
```python
> python assitant.py
```

2) Triplets extraction from affiramtions
```python
> from sentence_processor import SentenceProcessor
> phrase = "The tomato, which is one of the most popular salad ingredients, grows in many shapes and colors in greenhouses around the world."
> sp = SentenceProcessor(phrase)
> sp.process()
```

3) Triplets extraction from questions
```python
> from question_processor import QuestionProcessor
> q = QuestionProcessor("What is my bike code?")
> q.process()
```

4) Conversation and branching component
```python
> from utterance_branching import UtteranceBranching
> from coref.coref import NeuralCoref
> u =  UtteranceBranching(NeuralCoref())
> u.process("Mark is my best friend.")
> u.process("Who is Mark?")
```
