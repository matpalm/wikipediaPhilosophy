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
    target = str(link.target.string) if link.target else None
    part   = str(link.part.string) if link.part else target
    return [ target, part ]

for line in fileinput.input():
    cols = line.split("\t")    
    article_id, article_name, xml, plain_text = cols[0], cols[1], cols[3], cols[4]

    # ignore "article" if it looks like a meta article name
    if meta_article(article_name):
        sys.stderr.write("reporter:counter:parse,metafile,1\n")
        continue

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

            target, text = parse_link(link)
            if not target:
                continue

            if target == article_name:
                continue
            
            if meta_article(target):
                continue

            # look for word boundary match
            match = re.search(re.compile('\\b' + re.escape(text) + '\\b'), plain_text)
            if not match:
                continue
            index_in_plain_text = match.start()

            if first_occurance_index == None:
                # bootstrap case of first one
                first_occurance_index, first_occurance_target, first_occurance_text = index_in_plain_text, target, text
            else:                
                if index_in_plain_text <= first_occurance_index:
                    if first_occurance_text.startswith(text):
                        continue                    
                    if len(text) < len(first_occurance_text):
                        continue
                    # always choose one closer to fron
                    first_occurance_index, first_occurance_target, first_occurance_text = index_in_plain_text, target, text

            links_to_examine -= 1
            if links_to_examine == 0:
                sys.stderr.write("reporter:counter:parse,10_links_examined_limit,1\n")
                break

        if first_occurance_target:
            print article_name, "\t", first_occurance_target
        else:
            sys.stderr.write("reporter:counter:parse,no_match,1\n")

    except:
        sys.stderr.write("reporter:counter:parse,exception,1\n")
        sys.stderr.write("parsing ["+article_id+","+article_name+"] exception "+str(sys.exc_info()[0])+"\n")
