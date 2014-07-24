import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression as LR
from string import maketrans
import pandas as pd
from pandas import DataFrame, read_csv, read_excel, concat

class ML_builder(object):
    def __init__(self):
        self.vocab = []
        self.classifier = None
        self.train_df = None
    
    def build_vocab(self, n, training_samples):
        vocab = []
        with open('stopwords.txt') as stop_words:
            stop_words = {line.strip().lower() for line in stop_words if line!='\n'} 
        words = {}    
        tweets = []
        for tweet in self.train_df['SentimentText'][0:training_samples]:
            clean_tweet = self.tweet_cleaner(tweet)
            tweets.extend(clean_tweet.split())
        for word in tweets:
            if word not in stop_words:
                if word.isalnum() and len(word)>1:    
                    if words.get(word, False):
                        words[word] += 1
                    else:
                        words[word] = 1

        vocab = sorted(words.iteritems(), key=lambda x: x[1], reverse=True)
        vocab = [tup[0] for tup in vocab]
        self.vocab = vocab[:n]
        
    def tweet_cleaner(self, tweet):
        words = []
        tweet = tweet.translate(maketrans('?!,.', '    '))
        words.extend(tweet.strip().lower().split())
        for index, word in enumerate(words):
            for happy in happyface:
                if happy in word:
                    words[index]='happyface'
                    break
            for sad in sadface:
                if sad in word:
                    words[index]='sadface'
                    break
        return " ".join(words)
            
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
        output = self.train_df['Sentiment'][0:training_samples]
        clf = SVC(kernel='linear', probability=True)
        clf.fit(tweet_array, np.asarray(output))
        self.classifier = clf

    def test_classifier(self, training_samples, test_samples):
        test_array = np.zeros((test_samples, len(self.vocab)))
        for index, tweet in enumerate(self.train_df['SentimentText'][training_samples:test_samples]):
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
        
    def ML_build(self):
        with open('happyface.txt') as happyface:
            happyface = [line.strip() for line in happyface if line!='\n']
            sadface = [line.strip()[::-1] for line in happyface if line!='\n']

        self.train_df = read_csv('Sentiment Analysis Dataset.csv')
        self.train_df = self.train_df.ix[:,['Sentiment','SentimentText']]
        positive = self.train_df[self.train_df['Sentiment']==0]
        negative = self.train_df[self.train_df['Sentiment']==1]
        positive = positive[:10000]
        negative = negative[:10000]
        self.train_df = positive+negative

        self.build_vocab(n = 5000, training_samples = 2500)
        self.make_classifier(training_samples = 2500)
        self.test_classifier(training_samples = 2500, test_samples = 400)

    def Predict(self, tweet):
        if self.vocab == []:
            self.ML_build()
        return (self.classifier.predict(self.vectorize(tweet))[0],
                self.classifier.predict_proba(self.vectorize(tweet))[0])

                
                