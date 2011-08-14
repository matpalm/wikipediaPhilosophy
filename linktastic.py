#!/usr/bin/env python
import fileinput, re

for line in fileinput.input():
    x,a,b = line.split("\t")
    a = re.sub(' ', '_', a)
    print "http://en.wikipedia.org/wiki/" + a + "\t" + b.strip()
