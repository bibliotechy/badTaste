import re
from random import randrange
from nltk import tokenize
from nltk.corpus import cmudict
from redis import StrictRedis
import string

class BadTaste:

    def __init__(self):
        self.dish = self.get_dish()

    def get_dish(self):
        red = StrictRedis(db=0)
        self.dish = red.randomkey().decode('utf-8')
        self.dishwords = self.get_dish_words()
        return self.dish

    def get_dish_words(self):
        regex = re.compile('[^A-Za-z ]')
        return regex.sub('', self.dish).strip().split(" ")

    def get_bad_dish(self):
        def find_rhyme_in_words(dish, dishwords, redis, replaceCount=0):
            for word in sorted(dishwords):
                if word.lower() not in ["a", "an", "and", "of", "on", "the", "with",]:
                    pronunciations = cmudict.dict().get(word.lower(), [])
                    for pron in pronunciations:
                        badWord = find_best_rhyme(pron, redis)
                        if badWord:
                            dish = dish.replace(word, badWord.decode('utf-8'))
                            replaceCount += 1
                            break
                    if (replaceCount / len(dishwords)) < (1/3):
                        continue
                    else:
                        break
            return string.capwords(dish)

        def find_best_rhyme( pronunciation, redis):
            for i in range(len(pronunciation)-1,1,-1):
                badWord = redis.srandmember(bytes(":".join(pronunciation[-i:]).encode("utf-8")))
                if badWord:
                    return badWord
            else:
                return None

        if not  hasattr(self, "redis"):
            redis_url = "localhost"
            self.redis = StrictRedis(host=redis_url, db=1)
        newDish = find_rhyme_in_words(self.dish, self.dishwords,self.redis)
        if newDish and newDish.lower() != self.dish.lower():
            self.get_dish()
            return newDish
        else:
            self.get_dish()
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
                    self.redis.sadd(":".join(pron[-i:]), word)
        # Create multiple entry points for a word, form all but first sound matches to ony last two sounds match
        # For Example:
        # twiddle has a pronunciation: [u'T', u'W', u'IH1', u'D', u'AH0', u'L']
        # this creates entries for:
        # (u'AH0', u'L'),
        # (u'D', u'AH0', u'L'),
        # (u'IH1', u'D', u'AH0', u'L'),
        # (u'W', u'IH1', u'D', u'AH0', u'L')

def print_bad():
    try:
        bt = BadTaste()
        dish1 = bt.get_bad_dish()
        dish2 = bt.get_bad_dish()
        phrase = "Starter: " + dish1 + ", Main: " + dish2
        while len(phrase) > 140:
           phrase = " ".join(phrase.split()[:-1])
        print(phrase)
    except Exception as e:
        print(e)
        print_bad()

if __name__ == "__main__":
    print_bad()