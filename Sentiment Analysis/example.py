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

    # xml_dict = {';': '', '&lt': '<', '&amp': '&', '&gt': '>', '&quot': '"',
    #             '&apos': '\''}
    # for key, value in xml_dict.iteritems():
    #     s = s.replace(key, value)
    s.translate(maketrans('?!,.', '    '))

    with open('stopwords.txt') as stop_words:
        stop_words = {line.strip().lower() for line in stop_words if line!='\n'}

    return s


def move_to_file():
    training_data = import_data('data_set.csv')
    negative_index = 1
    positive_index = 1
    for i in range(60000, 65000):
        if training_data['Sentiment'][i] == 0:
            with open("./test_data/negative/text" + str(negative_index) + '.txt', 'w') as f:
                f.write(training_data['SentimentText'][i])
                f.close()
                negative_index += 1
        else:
            with open("./test_data/positive/text" + str(positive_index) + '.txt', 'w') as f:
                f.write(training_data['SentimentText'][i])
                f.close()
                positive_index += 1
