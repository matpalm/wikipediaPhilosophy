#!/usr/bin/env python
import fileinput, re, sys

seen_first_page = False

for line in fileinput.input():

    line = line.strip()

    # ignore last line
    if line == '</mediawiki>': 
        continue

    # ignore up to first page
    if not seen_first_page: 
        if line != '<page>':
            continue   
        else:
            seen_first_page = True
    
    sys.stdout.write(line)
    if line == '</page>':
        sys.stdout.write("\n")
