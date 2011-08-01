#!/usr/bin/env python
import fileinput, re, sys

def meta_article(name):
    match_before_colon = re.search(r'^(.*?):', name)
    if match_before_colon:
        prefix = match_before_colon.group(1)
        return prefix in ['File','Category','Template','Portal','Portal talk','File talk']
    return False

def next_link(xml, article_name):
    while True:
        next_target_match = re.search(r'<target>(.*?)</target>', xml)        
        if next_target_match == None:
            return None
        else:
            next_target = next_target_match.group(1)
            if (article_name != next_target) and (not ":" in next_target):
                return next_target
            else:
                # get rid of this target and start on next
                xml = re.sub(r'.*?'+re.escape(next_target_match.group(0)), '', xml, 1)

for line in fileinput.input():
    cols = line.split("\t")
    article_name, xml, plain_text = cols[1], cols[3], cols[4]

    # ignore "article" if it looks like a meta article name
    if meta_article(article_name):
        sys.stderr.write("reporter:counter:parse,metafile,1\n")
        continue

    # ignore "article" if it's plain text representation is very short
    if len(plain_text) < 30:
        sys.stderr.write("reporter:counter:parse,plain_text_too_short,1\n")
        continue        

    try:
        # ignore up to first paragraph
        xml = re.sub(r'.*?<paragraph', '', xml, 1) 
        # remove all templates
        xml = re.sub(r'<template.*?</template>', '', xml)
        # remove all synthetic links
        xml = re.sub(r'<link synthetic="true".*?</link>', '', xml)

        # now look for first target that's...
        # - not some kind of meta article
        # - doesn't match article name
        outbound_link = next_link(xml, article_name)
        if outbound_link:
            print "\t".join([article_name, outbound_link])
        else:
            sys.stderr.write("reporter:counter:parse,no_outbound_link_found,1\n")

    except:
        sys.stderr.write("reporter:counter:parse,exception,1\n")
