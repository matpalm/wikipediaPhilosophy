#!/usr/bin/env python
import fileinput, re, sys
from BeautifulSoup import BeautifulStoneSoup
from xml.sax.saxutils import unescape

for line in fileinput.input():
    try:
        xml = BeautifulStoneSoup(line)

        title = xml.find('title').string

        text = xml.find('text').string
        redirect_match = re.search('\[\[(.*?)\]\]', text)
        redirect = redirect_match.group(1)
        redirect = re.sub(r'\#.*', '', redirect) # drop any anchors
        redirect = re.sub('_',' ', redirect) # sometimes redirects include _s instead of ' 's (?)

        output = title + "\t" + redirect
        output_unescaped = unescape(output, {"&apos;": "'", "&quot;": '"'})        
        print output_unescaped.encode('utf-8')
    except:
        sys.stderr.write("problem processing line ["+line+"] "+str(sys.exc_info()[0])+"\n")
