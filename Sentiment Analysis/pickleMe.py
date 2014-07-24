import cPickle


def load_pickle(filename):

    pickled = open(filename, 'rb')
    data = cPickle.load(pickled)
    return data


def export_pickle(filename, the_object):
    pickle_file = open(filename, 'w')
    cPickle.dump(the_object, pickle_file)
    pickle_file.close()