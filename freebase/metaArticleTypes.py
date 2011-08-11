#!/usr/bin/env python
import fileinput, re

for line in fileinput.input():
    cols = line.split("\t")
    name = cols[1]
    meta_type_match = re.search(r'(.*):', name)
    meta_type = meta_type_match.group(1) if meta_type_match else 'normal file'
    print "LongValueSum:" + meta_type + "\t1"


