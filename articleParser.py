#!/usr/bin/env python
import fileinput, re, sys
from BeautifulSoup import BeautifulStoneSoup

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

def parse_link(link):
    target = link.target.string if link.target else None
    part   = link.part.string if link.part else target
    return [ target, part ]

for line in fileinput.input():
    cols = line.split("\t")    
    article_name, xml, plain_text = cols[1], cols[3], cols[4]

    # ignore "article" if it looks like a meta article name
    if meta_article(article_name):
        sys.stderr.write("reporter:counter:parse,metafile,1\n")
        continue

    # ignore "article" if it's plain text representation is very short
#    if len(plain_text) < 30:
#        sys.stderr.write("reporter:counter:parse,plain_text_too_short,1\n")
#        continue        

    try:
        parsed = BeautifulStoneSoup(xml)

        # remove all templates, they never seem to be visible main text
        for template in parsed.findAll('template'):
            template.extract()

        links = parsed.findAll('link')
        first_occurance_index  = None
        first_occurance_target = None
        first_occurance_text   = None
        links_to_examine = 10 # dont' go too deep in the document, for long articles you get false positives.
        for link in links:

            print "DEBUG next link", link

            target, text = parse_link(link)
            if not target:
                print "DEBUG ignore, no target"
                continue

            if target == article_name:
                print "DEBUG ignore, article name"
                continue
            
            if meta_article(target):
                print "DEBUG ignore, meta link"
                continue

            # look for word boundary match
            match = re.search(re.compile('\\b' + text + '\\b'), plain_text)
            if not match:
                print "DEBUG no match"
                continue
            index_in_plain_text = match.start()
            print "DEBUG [", target, "][", text, "][", index_in_plain_text, ']'

            if first_occurance_index == None:
                # bootstrap case of first one
                print "DEBUG bootstrap"
                first_occurance_index, first_occurance_target, first_occurance_text = index_in_plain_text, target, text
            else:                
                if index_in_plain_text <= first_occurance_index:
                    if first_occurance_text.startswith(text):
                        print "DEBUG less index, but substring"
                        continue                    
                    if len(text) < len(first_occurance_text):
                        print "DEBUG less index, but we got a longer match already"
                        continue
                    print "DEBUG less index and not subset"
                    # always choose one closer to fron
                    first_occurance_index, first_occurance_target, first_occurance_text = index_in_plain_text, target, text

#                elif index_in_plain_text == first_occurance_index \
#                        and len(text) > len(first_occurance_text):
#                    print "same index, longer matche"
                    # if the match has the same index favor the longer match
#                    first_occurance_index, first_occurance_text = index_in_plain_text, text

            links_to_examine -= 1
            if links_to_examine == 0:
                sys.stderr.write("reporter:counter:parse,10_links_examined_limit,1\n")
                break

            print "DEBUG fo index [", first_occurance_index, "] target [", first_occurance_target, \
                "] text [", first_occurance_text, ']'

        if first_occurance_target:
            print article_name, "\t", first_occurance_target
        else:
            sys.stderr.write("reporter:counter:parse,no_match,1\n")

        # ignore up to first paragraph
        #xml = re.sub(r'.*?<paragraph', '', xml, 1) 
        # remove all templates
        #xml = re.sub(r'<template.*?</template>', '', xml)
        # remove all synthetic links
        #xml = re.sub(r'<link synthetic="true".*?</link>', '', xml)

        # now look for first target that's...
        # - not some kind of meta article
        # - doesn't match article name
        #outbound_link = next_link(xml, article_name)
        #if outbound_link:
        #    print "\t".join([article_name, outbound_link])
        #else:
        #    sys.stderr.write("reporter:counter:parse,no_outbound_link_found,1\n")

    except:
        sys.stderr.write("parse exception "+str(sys.exc_info()[0])+"\n")
        sys.stderr.write("reporter:counter:parse,exception,1\n")
        raise
