#!/usr/bin/env python
import fileinput, re, sys
from BeautifulSoup import BeautifulStoneSoup

def meta_article(name):
    match_before_colon = re.search(r'^(.*?):', name)
    if match_before_colon:
        prefix = match_before_colon.group(1)
        return prefix in ['File','Category','Template','Portal','Portal talk','File talk','Image']
    return False

def write_first_link(parsed, plain_text):
    for sentence in parsed.findAll('sentence'):
#        print "sentence", sentence
        for link in sentence.findAll('link'):
#            print "link", link
            if link.target:
                link_target = str(link.target.string)
                link_text   = str(link.part.string) if link.part else link_target
                if link_target!=article_name and not meta_article(link_target) and link_text in plain_text:
                    # huge hack but having lots of problems when article_name & target are
                    # unicode and combining with "\t"
                    sys.stdout.write(article_name.strip())
                    sys.stdout.write("\t")
                    sys.stdout.write(link_target.strip())
                    sys.stdout.write("\n")
                    return

for line in fileinput.input():
    article_id, article_name, dts, xml, plain_text = line.split("\t")

    # ignore "article" if it looks like a meta article name
    if meta_article(article_name):
        sys.stderr.write("reporter:counter:parse,metafile,1\n")
        continue

    try:
        # remove <space/> tags, they cause sentences in the write_first_link
        # to be truncated somehow ...
        xml = xml.replace('<space/>',' ')

        # remove all templates, they never seem to be visible main text
        # tried to do this the "right way" using beautiful soup findAll and extract()
        # but the parsing dies totally when xml contains non ascii (like the greek_languages.eg)
        xml = re.sub(r'<template.*?</template>', '', xml)

        # parse xml
        parsed = BeautifulStoneSoup(xml)
            
        # write the first link we see
        write_first_link(parsed, plain_text)

    except:
        sys.stderr.write("reporter:counter:parse,exception,1\n")
        sys.stderr.write("parsing ["+article_id+","+article_name+"] exception "+str(sys.exc_info()[0])+"\n")
