#!/usr/bin/env python
import fileinput, re

for line in fileinput.input():
    cols = line.split("\t")
    name, plain_text = cols[1], cols[3]
    print name + " | " + plain_text
    


