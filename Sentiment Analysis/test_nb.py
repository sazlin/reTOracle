from NB import predict
from pickleMe import load_pickle


classifier_global = load_pickle('classifier.txt')
vectorizer_global = load_pickle('vectorizer.txt')


def testPredict():
    assert predict('I love Python') == 'positive'
