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

    def unsupervised_predict(tweet):
    
        def get_good_chunks(chunks):
            good_chunks = []
            for subtree in chunks:
                if type(subtree) is nltk.Tree:
                    good_chunks.append(' '.join([leaves[0] for index, leaves in enumerate(subtree.leaves()) if index<2]))
            return good_chunks
        
        tokenized = nltk.word_tokenize(tweet)
        tagged = nltk.pos_tag(tokenized)

        chunk_gram = r"Chunk: {(<JJ><NNS?>)|(<RB\w?><VB[DNG]?>)|(<JJ><JJ><[^N]\w\w?|NNPS?>)" \
        "|(<RB\w?><JJ><[^N]\w\w?|NNPS?>)|(<NNS?><JJ><[^N]\w\w?|NNPS?>)}"

        chunk_parser = nltk.RegexpParser(chunk_gram)
        chunks = chunk_parser.parse(tagged)
        good_chunks = get_good_chunks(chunks)
        
        if not good_chunks:
            backup_chunk_gram = r"Chunk: {(<NN\w?\w?><VB\w?>)|(<RB\w?><JJ>)|(<N\w?\w?\w?|PR\w?><VB\w?>)}"
            chunk_parser = nltk.RegexpParser(backup_chunk_gram)
            chunks = chunk_parser.parse(tagged)
            good_chunks = get_good_chunks(chunks)

        print good_chunks
        SO = 0
        for chunk in good_chunks:
            close_good = hits("happy", chunk)
            close_bad = hits("sad", chunk)
            good = hits("good")
            bad = hits("bad")
            ratio1 = 1.0* close_good / close_bad
            ratio2 = 1.0* bad/good
            ratio = ratio1*ratio2
            SO += log(ratio)
        
        if SO=0:
            return 'Cannot predict'
        elif SO>0:
            return 'Positive'
        return 'Negative'

    
    def hits(word, phrase=None):
        query = "http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q={}"
        if not phrase:
            results = requests.get(query.format(word))
        else:
            results = requests.get(query.format(phrase+" AROUND(10) "+word))
        json_res = results.json()
        print json_res
        google_hits=int(json_res['responseData']['cursor']['estimatedResultCount'])
        return google_hits