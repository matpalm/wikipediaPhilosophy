#!/usr/bin/env python
from mwlib.uparser import parseString, simpleparse
from BeautifulSoup import BeautifulStoneSoup
from xml.sax.saxutils import unescape
from mwlib.parser.nodes import *
import fileinput
import re

def replace_nested(regex, text):
    while True:
        original = text
        text = re.sub(regex, ' ', text)
#        print "text2 ", text[0:1000].encode('utf-8')
        if original == text:
            return text

for line in fileinput.input():
    xml = BeautifulStoneSoup(line)
    text = xml.find('text').string
    text = unescape(text, {"&apos;": "'", "&quot;": '"'})
    text = replace_nested('{[^{]*?}', text)    
    simpleparse(text)
    




