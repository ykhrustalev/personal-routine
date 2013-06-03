#!/usr/bin/env python
import sys

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "usage: <raw memo export text> <month>"
        exit(1)

    text = sys.argv[1]
    month = sys.argv[2]

    for l in text.split("|"):
        if l[4:6] != month:
            continue
        print "{},8,\"{}\"".format(*l.strip().split(";"))
