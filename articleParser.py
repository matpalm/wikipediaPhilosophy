#!/usr/bin/env python
import fileinput, re, sys, traceback
from mwlib.parser.nodes import *
from mwlib.uparser import parseString, simpleparse
from BeautifulSoup import BeautifulStoneSoup
from xml.sax.saxutils import unescape

def replace_nested(regex, text):
    while True:
        original = text
        text = re.sub(regex, ' ', text)
        if original == text:
            return text

def unescape_full(text):
    return unescape(text, {"&apos;": "'", "&quot;": '"'})

def meta_article(link):    
    if not ":" in link:
        return False
    return link.startswith('File:') \
           or link.startswith('Category:') \
           or link.startswith('Wikipedia:') \
           or link.startswith('Template:') \
           or link.startswith('Portal:') \
           or link.startswith('Book:') \
           or link.startswith('MediaWiki:')

def internal_link(link):
    return link.startswith('#')

def valid_link(link, title):    
    link = re.sub(r'[\#\|].*','', link)
    link = re.sub('_',' ', link)
    if not link:
        return None
    link = link[0].upper() + link[1:] # make sure it's first letter capital
    if not (meta_article(link) or internal_link(link) or link==title):
        return link    

for line in fileinput.input():    
    try:
        xml = BeautifulStoneSoup(line)

        title = unescape_full(xml.find('title').string)
        if meta_article(title):
            sys.stderr.write("reporter:counter:parse,ignore_meta_title,1\n")
            continue

        text = unescape_full(xml.find('text').string)
        text = replace_nested('{[^{]*?}', text)    

        link = None
        parantheses_depth = 0

        nodes = [ parseString(title='', raw=text) ]
        while len(nodes) > 0:
#            print "nodes", nodes
            node = nodes.pop(0)
            node_type = type(node)

            if node_type in [Article, Paragraph, Node]:
                nodes = node.children + nodes
                continue

            if node_type is Text:
                text = str(node).encode('utf-8')
#                print "text", text
                for c in text:
                    if c == '(':
                        parantheses_depth += 1
                    elif c == ')':
                        parantheses_depth -= 1
                if parantheses_depth < 0:
                    sys.stderr.write("reporter:counter:parse,neg_parantheses_depth,1\n")
                    sys.stderr.write("warning! -ve parantheses_depth for ["+str(title).encode('utf-8')+"]\n")
                    parantheses_depth = 0

#            print "parantheses_depth", parantheses_depth
            if parantheses_depth > 0: 
                # we're still in brackets, ignore
                continue

            elif node_type is Style:
                if node.caption != "''": # ignore italics
                    nodes = node.children + nodes

            elif node_type is ArticleLink:
                target = node.target
                link = valid_link(target, title)
                if link:
                    break            

        if link:
            print (title+"\t"+link.strip()).encode('utf-8')

    except:
        sys.stderr.write("reporter:counter:parse,exception_parsing_article,1\n")
        sys.stderr.write("ERROR problem processing article for ["+title.encode('utf-8')+"] "+str(sys.exc_info()[0])+"\n")
        traceback.print_exc(file=sys.stderr)



