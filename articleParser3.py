#!/usr/bin/env python
import fileinput, re
from mwlib.parser.nodes import *
from mwlib.uparser import parseString, simpleparse
from BeautifulSoup import BeautifulStoneSoup
from xml.sax.saxutils import unescape

def replace_nested(regex, text):
    while True:
        original = text
        text = re.sub(regex, ' ', text)
#        print "text2 ", text[0:1000].encode('utf-8')
        if original == text:
            return text

def unescape_full(text):
    return unescape(text, {"&apos;": "'", "&quot;": '"'})

def meta_article(link):
    return ':' in link

def internal_link(link):
    return link.startswith('#')

def valid_link(link, title):    
    link = re.sub(r'[\#\|].*','', link)
    print "link sans anchor", link.encode('utf-8')
    link = re.sub('_',' ', link)
    print "link sans _", link.encode('utf-8')
    if not link:
        return None
    link = link[0].upper() + link[1:] # make sure it's first letter capital
    print "link upper", link.encode('utf-8')
    if not (meta_article(link) or internal_link(link) or link==title):
        return link
    

for line in fileinput.input():    
    xml = BeautifulStoneSoup(line)

    title = unescape_full(xml.find('title').string)
    text = unescape_full(xml.find('text').string)

    text = replace_nested('{[^{]*?}', text)    

    link = None
    nodes = [ parseString(title='', raw=text) ]
    while len(nodes) > 0:
        print "NODES ", nodes
        node = nodes.pop(0)
        node_type = type(node)

        if node_type in [Article, Paragraph, Node]:
            print "push children", node_type
            nodes = node.children + nodes
        elif node_type is Text:
            print "text![",node,"]"
        elif node_type is Style:
            if node.caption == "''":
                print "ignore italics"
            elif node.caption == "'''":
                print "push children", node_type
                nodes = node.children + nodes
            else:
                print "dont know what to do with style", node_type
        elif node_type is ArticleLink:
            target = node.target
            link = valid_link(target, title)
            if link:
                break
        elif node_type is ImageLink:
            pass        
        else:
            print "dont know what to do with", node_type
    
    print (title+"\t"+link.strip()).encode('utf-8')




