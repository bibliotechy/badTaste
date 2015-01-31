__author__ = 'cbn'

import re
from random import randrange
import csv
from nltk import tokenize
from nltk.corpus import cmudict
from redis import StrictRedis

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
        regex = re.compile('[^A-Za-z ]')
        return regex.sub('', self.dish).strip().split(" ")

    def get_dish_word(self):
        return self.dishwords[randrange(len(self.dishwords))]

    def get_random_dish(self):
        return self.get_dish_word(self.dishwords)

    def get_bad_dish(self):
        def find_rhyme_in_words(dish, dishwords, redis, replaceCount=0):
            for word in sorted(dishwords):
                if word.lower() not in ["a", "an", "and", "of", "the", "with",]:
                    pronunciations = cmudict.dict().get(word.lower(), [])
                    for pron in pronunciations:
                        badWord = find_best_rhyme(pron, redis)
                        if badWord:
                            dish = dish.replace(word, badWord.decode('utf-8')).title()
                            replaceCount += 1
                            break
                    if replaceCount / len(dishwords) < (1/3):
                        continue
                    else:
                        break
            return dish

        def find_best_rhyme( pronunciation, redis):
            for i in range(len(pronunciation)-1,1,-1):
                badWord = redis.srandmember(tuple(pronunciation[-i:]))
                if badWord:
                    return badWord
            else:
                return None

        if not  hasattr(self, "redis"):
            redis_url = "localhost"
            self.redis = StrictRedis(host=redis_url, db=1)
        newDish = find_rhyme_in_words(self.dish, self.dishwords,self.redis)
        self.get_dish()
        if newDish != self.dish:
            return newDish
        else:
            self.get_bad_dish()



class BadWords:

    def __init__(self, filename):
        redis_url = "localhost"
        self.redis = StrictRedis(host=redis_url, db=1)

        readed = open(filename)
        self.badwords = readed.read()
        readed.close()

        self.bad_word_tokens = self.tokenize_bad_words()

    def tokenize_bad_words(self):
        return tokenize.word_tokenize(self.badwords)

    def badWordsInRedis(self):
        for word in self.bad_word_tokens:
            pronunciations = cmudict.dict().get(word,[])
            for pron in pronunciations:
                for i in range(2,len(pron)):
                    self.redis.sadd(tuple(pron[-i:]), word)
        # Create multiple entry points for a word, form all but first sound matches to ony last two sounds match
        # For Example:
        # twiddle has a pronunciation: [u'T', u'W', u'IH1', u'D', u'AH0', u'L']
        # this creates entries for:
        # (u'AH0', u'L'),
        # (u'D', u'AH0', u'L'),
        # (u'IH1', u'D', u'AH0', u'L'),
        # (u'W', u'IH1', u'D', u'AH0', u'L')
