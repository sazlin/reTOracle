
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.svm import SVC
import pandas as pd
from pandas import read_csv, read_excel, concat
import nltk
import re
import requests
import json
from math import log, exp
import os
from os.path import isfile

class SVM_builder(object):
    def __init__(self):
        self.vocab = []
        self.happyface = []
        self.sadface = []
        self.classifier = None
        self.train_df = None
    
    def build_vocab(self, n, training_samples):
        with open('stopwords.txt') as stop_words:
            stop_words = {line.strip().lower() for line in stop_words if line!='\n'} 
   
        tweets = []
        for tweet in self.train_df['SentimentText'][0:training_samples]:
            clean_tweet = self.tweet_cleaner(tweet)
            tweets.extend(clean_tweet.split())
        
        word_df = pd.DataFrame(tweets, columns=['word'])
        
        df_filter = pd.Series([word not in stop_words for word in word_df['word']], index = word_df.index)
        word_df = word_df[df_filter]
        result = word_df.groupby('word').size().order(ascending=False)[:n]
        self.vocab = list(result.index)
        print 'Vocab Complete'
        
    def tweet_cleaner(self, tweet):
        words = []
        tweet = tweet.replace('"@#?!,.0123456789-&*', '                    ')
        words.extend(tweet.strip().lower().split())
        for index, word in enumerate(words):
            for happy in self.happyface:
                if happy in word:
                    words[index]='happyface'
                    break
            for sad in self.sadface:
                if sad in word:
                    words[index]='sadface'
                    break
        cleaner = " ".join([word for word in words if len(word)>1])
        return cleaner.replace(':)(;][\/=', '         ')
            
    def vectorize(self, tweet):
        vector = np.zeros(len(self.vocab))
        clean_tweet = self.tweet_cleaner(tweet)

        for word in clean_tweet.split():
            try:
                vector[self.vocab.index(word)] += 1
            except ValueError:
                pass
        return vector

    def make_classifier(self, training_samples):
        tweet_array = np.zeros((training_samples, len(self.vocab)))
        for index, tweet in enumerate(self.train_df['SentimentText'][0:training_samples]):
            tweet_array[index] = self.vectorize(tweet)
        print 'Vectorization Complete'
        output = self.train_df['Sentiment'][0:training_samples]
        clf = SVC(kernel='linear', probability=True)
        #X_csr = sparse.csr_matrix(tweet_array)
        X_csr = tweet_array
        clf.fit(X_csr, np.asarray(output))
        self.classifier = clf
        print 'Classifier Created'

    def test_classifier(self, training_samples, test_samples):
        test_array = np.zeros((test_samples, len(self.vocab)))
        for index, tweet in enumerate(self.train_df['SentimentText'][training_samples:training_samples+test_samples]):
            test_array[index] = self.vectorize(tweet)
        predictions = self.classifier.predict(test_array)
        correct, wrong = 0,0
        for index, predict in enumerate(predictions):
            if predict == self.train_df['Sentiment'][index+training_samples]:
                correct += 1
            else:
                wrong += 1
        print (correct, wrong)
        print 'Percentage {}'.format(1.0*correct/(correct+wrong))

    def PCA_analysis(self, training_samples = 1000):
        tweet_array = np.zeros((training_samples, len(self.vocab)))
        for index, tweet in enumerate(self.train_df['SentimentText'][0:training_samples]):
            tweet_array[index] = self.vectorize(tweet)
        pca = PCA(n_components=2)
        pca.fit(tweet_array)
        print(pca.explained_variance_ratio_)
        print(pca.components_)
        
    def SVM_build(self):
        curr_dir = os.getcwd()
        if isfile('SVM_algo.txt'):
            self.classifier = load_pickle('SVM_algo.txt')
            self.vocab = load_pickle('vocab.txt')
        else:
            with open('happyface.txt') as happyface:
                self.happyface = [line.strip() for line in happyface if line!='\n']
                self.sadface = [line.strip()[::-1] for line in happyface if line!='\n']

            self.train_df = read_csv('Sentiment Analysis Dataset.csv')
            self.train_df = self.train_df.ix[:,['Sentiment','SentimentText']]
            positive = self.train_df[self.train_df['Sentiment']==0]
            negative = self.train_df[self.train_df['Sentiment']==1]
            sample_size = 10000
            training_ratio = .9
            positive_train = positive[:int(training_ratio*sample_size)]
            negative_train = negative[:int(training_ratio*sample_size)]
            positive_test = positive[int(training_ratio*sample_size):sample_size]
            negative_test = negative[int(training_ratio*sample_size):sample_size]
            self.train_df = concat([positive_train,negative_train, positive_test, negative_test])
            self.train_df = self.train_df.reset_index()

            self.build_vocab(n = 5000, training_samples = int(sample_size*training_ratio*2))
            self.make_classifier(training_samples = int(sample_size*training_ratio*2))
            self.test_classifier(training_samples = int(sample_size*training_ratio*2),
                                 test_samples = int((1-training_ratio)*sample_size*2))
            print 'Classifier Ready'
            export_pickle('SVM_algo.txt', self.classifier)
            export_pickle('vocab.txt', self.vocab)

    def Predict(self, tweet):
        Decider = self.classifier.predict_proba(self.vectorize(tweet))[0][0]
        if Decider<.475:
            return (1, self.classifier.predict_proba(self.vectorize(tweet))[0])
        elif Decider>.525:
            return (-1, self.classifier.predict_proba(self.vectorize(tweet))[0])
        return (0, self.classifier.predict_proba(self.vectorize(tweet))[0])
        

import cPickle
def load_pickle(filename):
    pickled = open(filename, 'rb')
    data = cPickle.load(pickled)
    return data
def export_pickle(filename, the_object):
    pickle_file = open(filename, 'wb')
    cPickle.dump(the_object, pickle_file)
    pickle_file.close()


def unsupervised_predict(tweet):
    
    def get_good_chunks(chunks):
        good_chunks = []
        for subtree in chunks:
            if type(subtree) is nltk.Tree:
                good_chunks.append(' '.join([leaves[0] for index, leaves in enumerate(subtree.leaves()) if index<2]))
        return good_chunks
    
    tokenized = nltk.word_tokenize(tweet)
    tagged = nltk.pos_tag(tokenized)

    chunk_gram = r"Chunk: {(<JJ><NNS?>)|(<RB\w?><VB[DNG]?>)|(<JJ><JJ><[^N]\w\w?|NNPS?>)"     "|(<RB\w?><JJ><[^N]\w\w?|NNPS?>)|(<NNS?><JJ><[^N]\w\w?|NNPS?>)}"

    chunk_parser = nltk.RegexpParser(chunk_gram)
    chunks = chunk_parser.parse(tagged)
    good_chunks = get_good_chunks(chunks)
    
    if not good_chunks:
        backup_chunk_gram = r"Chunk: {(<NN\w?\w?><VB\w?>)|(<RB\w?><JJ>)|(<N\w?\w?\w?|PR\w?><VB\w?>)"         "|(<VB\w?><RB\w?>)|(<VB\w?><JJ>)}"
        chunk_parser = nltk.RegexpParser(backup_chunk_gram)
        chunks = chunk_parser.parse(tagged)
        good_chunks = get_good_chunks(chunks)

    print good_chunks
    SO = 0
    for chunk in good_chunks:
        close_good = hits("happy", chunk)
        close_bad = hits("sad", chunk)
        good = hits("happy")
        bad = hits("sad")
        ratio1 = 1.0* close_good / close_bad
        ratio2 = 1.0* bad/good
        ratio = ratio1*ratio2
        SO += log(ratio)
    
    if sigmoid(SO)>.025:
        return (1, 1-sigmoid(SO), sigmoid(SO))
    elif sigmoid(SO)<-.025:
        return (-1, 1-sigmoid(SO), sigmoid(SO))
    return (0, 1-sigmoid(SO), sigmoid(SO))

def sigmoid(x):
  return 1 / (1 + exp(-x))

def hits(word, phrase=None):
    query = "http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q={}"
    if not phrase:
        results = requests.get(query.format(word))
    else:
        results = requests.get(query.format(phrase+" AROUND(10) "+word))
    json_res = results.json()
    google_hits=int(json_res['responseData']['cursor']['estimatedResultCount'])
    return google_hits
                
                