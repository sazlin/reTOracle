#!/usr/bin/python
import sys
#identity reducer
for line in sys.stdin:
    # line = line.strip()
    # arg = line.split('\t')
    # print "[{0}, {1}]".format(arg[0], arg[1])
    if line == "\n":
        pass
    else:
        print line
