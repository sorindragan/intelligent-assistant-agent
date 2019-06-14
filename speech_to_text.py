import speech_recognition as sr

class SpeechToText:

    def __init__(self):
        self.sample_rate = 48000
        self.chunk_size = 2048
        self.r = sr.Recognizer()

    def list_michrophones(self):
        mic_list = sr.Microphone.list_microphone_names()

    def process(self):

        text = ""
        with sr.Microphone(sample_rate = self.sample_rate,
        				   chunk_size = self.chunk_size
                           ) as source:

        	self.r.adjust_for_ambient_noise(source)
        	print("Say Something: ", end='', flush=True)
        	audio = self.r.listen(source)

        	try:
        		text = self.r.recognize_google(audio)
        		print("You: ", text)

        	except sr.UnknownValueError:
        		print("Google Speech Recognition could not understand what you said")

        	except sr.RequestError as e:
        		print("Could not request results from Google Speech Recognition service; {0}".format(e))
        return text
