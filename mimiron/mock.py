# coding: utf-8

import sys
import random

def mock_test_condition():
    rint = random.randint(0, 100)
    print >> sys.stderr, '%d got' % rint
    return rint < 15

