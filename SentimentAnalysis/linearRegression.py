from sklearn.feature_extraction.text import CountVectorizer
from sklearn.cross_validation import train_test_split
from sklearn.linear_model import LogisticRegression as LR
import pandas as pd
import numpy as np
import re
from string import maketrans


def import_data(csv_file):
    """
    takes csv files, parses with panda and returns result
    """
    # skips bad lines
    data = pd.read_csv(csv_file, error_bad_lines=False)
    return data


def cleanData(s):
    """
    cleans data by lowers cases and removing accentuated chars
    then extracts word tokens of at least 2 chars
    """

    # extract only word tokens of at least 2 chars
    re.compile(r"\b\w\w + \b", re.U).findall(s)

    xml_dict = {';': '', '&lt': '<', '&amp': '&', '&gt': '>', '&quot': '"',
                '&apos': '\''}
    for key, value in xml_dict.iteritems():
        s = s.replace(key, value)
    s.translate(maketrans('?!,.', '    '))

    return s


def build_vocab(training_samples=10000, vocab=None):

    training_data = import_data('data_set.csv')

    if not vocab:
        vocab = []
    with open('stopwords.txt') as stop_words:
        stop_words = {line.strip().lower() for line in stop_words if line!='\n'} 
    words = {}
    tweets = []
    for tweet in training_data['SentimentText'][0:training_samples]:
        clean_tweet = cleanData(tweet)
        clean_tweet = clean_tweet.split(' ')
        tweets.extend(clean_tweet)
    for word in tweets:
        if word not in stop_words:
            if word.isalnum() and len(word) > 2:
                if words.get(word, False):
                    words[word] += 1
                else:
                    words[word] = 1

    vocab = sorted(words.iteritems(), key=lambda x: x[1], reverse=True)
    vocab = [tup[0] for tup in vocab]
    return vocab


def vectorize(vocab, tweet):
    vector = np.zeros(len(vocab))
    word_list = []
    clean_tweet = tweet.translate(maketrans('?!,.', '    '))
    word_list.extend(clean_tweet.strip().lower().split())

    for word in word_list:
        try:
            vector[vocab.index(word)] += 1
        except ValueError:
            pass
    return vector


