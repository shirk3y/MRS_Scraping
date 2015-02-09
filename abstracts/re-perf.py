import string
import random
import time

def random_word():
    length = random.randint(2, 7)
    return ''.join(random.choice(string.ascii_uppercase + string.digits)
                   for _ in xrange(length))


def random_words(count):
    return [random_word() for x in xrange(count)]

tags = random_words(10000)
words = tags + random_words(90000)
random.shuffle(words)
text = ' '.join(words)

def test(re):
    tag_regexes = [re.compile(r'\b%s\b' % re.escape(tag)) for tag in tags]

    t = time.time()
    for regex in tag_regexes:
    	regex.search(text)
    print 'separate regexes:', time.time() - t

    tag_regex = re.compile(r'\b(%s)\b' % '|'.join([re.escape(tag) for tag in tags]))
    t = time.time()
    tag_regex.search(text)
    print 'combined regex:', time.time() - t

import re2 as _re2
print 'testing re2'
test(_re2)

import re as _re
print 'testing re'
test(_re)

