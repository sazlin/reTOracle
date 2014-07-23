from sklearn.datasets import load_files
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import numpy as np

with open('stopwords.txt') as stop_words:
        stop_words = [line.strip().lower() for line in stop_words if line!='\n']

train_small = load_files('./training_data/')
test_small = load_files('./test_data/')

# Turn the text documents into vectors of word frequencies
vectorizer = TfidfVectorizer(min_df=2, stop_words=stop_words)
X_train = vectorizer.fit_transform(train_small.data)
y_train = train_small.target

# Fit a classifier on the training set
classifier = MultinomialNB(alpha=1).fit(X_train, y_train)
print("Training score: {0:.1f}%".format(
    classifier.score(X_train, y_train) * 100))

# Evaluate the classifier on the testing set
X_test = vectorizer.transform(test_small.data)
y_test = test_small.target
print("Testing score: {0:.1f}%".format(
    classifier.score(X_test, y_test) * 100))


def predict(tweet):
    # classifier.predict
    # with open('stopwords.txt') as stop_words:
    #     stop_words = [line.strip().lower() for line in stop_words if line!='\n']

    # train_small = load_files('./training_data/')
    # vectorizer = TfidfVectorizer(min_df=2, stop_words=stop_words)
    # X_train = vectorizer.fit_transform(train_small.data)
    # y_train = train_small.target
    # classifier = MultinomialNB(alpha=0.5).fit(X_train, y_train)

    tweet = [tweet]
    matrix2 = vectorizer.transform(tweet).todense()
    predicted = classifier.predict(matrix2)

    if predicted == [0]:
        print 'negative'
    else:
        print 'positive'
