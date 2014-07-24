from LR import predict
from pickleMe import load_pickle


classifier_global = load_pickle('LRclassifier.txt')
vectorizer_global = load_pickle('LRvectorizer.txt')


def testPredict():
    assert predict('I love Python')[0] == 'positive'