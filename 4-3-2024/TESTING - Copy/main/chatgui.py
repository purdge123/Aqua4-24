from kivymd.app import MDApp
import nltk
from nltk.stem import WordNetLemmatizer
from keras.models import load_model
import json
import random
import numpy as np
import pickle
from home import Home_Screen
nltk.download('punkt')
nltk.download('wordnet')

lemmatizer = WordNetLemmatizer()

model = load_model('chatbot_model.h5')
intents = json.loads(open('main\intents.json').read())
words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))


class ChatBotApp(MDApp):
    response = ''
    def send_message(self,chat_input):     
        user_message = chat_input.text
        chat_input.text = ""

        if user_message:
            bot_response = self.chatbot_response(user_message)
            return bot_response    
    # Update chat log
        '''
            chat_log = self.root.chat_log
            chat_log.text += f"[b]You:[/b] {user_message}\n"
            chat_log.text += f"[b]Bot:[/b] {bot_response}\n"
            chat_log.height = chat_log.texture_size[1]
        '''
    def chatbot_response(self, msg):
        p = self.bow(msg, words)
        res = model.predict(np.array([p]))[0]
        ERROR_THRESHOLD = 0.25
        results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
        results.sort(key=lambda x: x[1], reverse=True)
        return_list = []

        for r in results:
            return_list.append({"intent": classes[r[0]], "probability": str(r[1])})

        tag = return_list[0]['intent']
        list_of_intents = intents['intents']
        for i in list_of_intents:
            if i['tag'] == tag:
                result = random.choice(i['responses'])
                break

        return result

    def bow(self, sentence, words):
        sentence_words = self.clean_up_sentence(sentence)
        bag = [0] * len(words)

        for s in sentence_words:
            for i, w in enumerate(words):
                if w == s:
                    bag[i] = 1

        return np.array(bag)

    def clean_up_sentence(self, sentence):
        sentence_words = nltk.word_tokenize(sentence)
        sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
        return sentence_words
