#!/usr/bin/env python
import fileinput, re, sys

for line in fileinput.input():
    cols = line.split("\t")

    # ignore "article" if plain text version very short, probably a meta article
    if len(cols[4].strip()) < 30: # plain text
        sys.stderr.write("reporter:counter:parse,plain_text_too_short,1\n")
        continue

    try:
        article_id, article_name, xml = cols[0], cols[1], cols[3]

        # ignore up to first sentence
        xml = re.sub(r'.*?<sentence', '', xml, 1) 

        next_target = None
        keep_searching = True
        while keep_searching:
            next_target_match = re.search(r'<target>(.*?)</target>', xml)        
            if next_target_match == None:
                keep_searching = False
            else:
                next_target = next_target_match.group(1)
                if (article_name != next_target) and (not ":" in next_target):
                    keep_searching = False
                else:
                    # get rid of this target and start on next
                    xml = re.sub(r'.*?'+re.escape(next_target_match.group(0)), '', xml, 1)
        
        if next_target:
            print "\t".join([article_name, next_target])

    except:
        sys.stderr.write("reporter:counter:parse,exception,1\n")
