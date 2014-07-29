import pytest
import rheTOracle
from flask.ext.testing import

def test_say_hello():
    from rheTOracle import say_hello
    assert say_hello() == u'RheTOracly speaking, how awesome are we?'


def test_update_redis():
    pass

def test_q1_query():
    pass


def test_q2_query():
    pass


def test_map_q2_results_to_language():
    pass


def test_map_q1_results_to_language():
    pass

