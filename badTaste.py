__author__ = 'cbn'

from random import randrange
import csv
from nltk import tokenize
from nltk.corpus import cmudict

class BadTaste:

    def __init__(self, csvfile=None):
        if csvfile:
            self.load_dishes(csvfile)
            self.dish_count = len(self.dishes)
        if self.dishes:
            self.dish = self.get_dish()

    def load_dishes(self,csvfile):
        with open(csvfile) as dishes:
            self.dishes =  [dish['name'] for dish in csv.DictReader(dishes)]

    def get_dish(self):
        if self.dishes:
            self.dish = self.dishes[randrange(self.dish_count)]
            self.dishwords = self.get_dish_words()
            return self.dish
        else:
            raise ValueError("I don't know about no dishes")

    def get_dish_words(self):
        return self.dish.split(" ")

    def get_dish_word(self,dishwords):
        return dishwords[randrange(len(dishwords))]

    def get_random_dish(self):
        return self.get_dish_word(self.dishwords)

class BadWords:

    def __init__(self, filename):
        readed = open(filename)
        self.badwords = readed.read()
        readed.close()

        self.bad_word_tokens = self.tokenize_bad_words()

    def tokenize_bad_words(self):
        return tokenize.word_tokenize(self.badwords)

    #prondict = [{":".join(cmudict.dict().get(word, [[]])[0][-2:]): word} for word in bw.bad_word_tokens]
    # like this, but with betterer logic
    # add this shit in a redis, yo