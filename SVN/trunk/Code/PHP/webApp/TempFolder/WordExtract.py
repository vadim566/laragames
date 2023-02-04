import os
import sys
from hazm import *


words = word_tokenize('صبح‌ها دیر از خواب بیدار می‌شد')

tagger = POSTagger(model='resources/postagger.model')
taggedWords = tagger.tag(word_tokenize('ما بسیار کتاب می‌خوانیم'))
print(words)
print(taggedWords)
