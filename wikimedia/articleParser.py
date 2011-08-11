#!/usr/bin/env python
import fileinput, re, sys, traceback
from BeautifulSoup import BeautifulStoneSoup
from xml.sax.saxutils import unescape

class LinkParser(BeautifulStoneSoup):
    NESTABLE_TAGS = {
        'link': ['link']
    }

def first_valid_link(links):
    for link in links:
        link_text = link.text
        if not ":" in link_text:
            return link_text
    return None

for line in fileinput.input():
    try:
        xml = BeautifulStoneSoup(line)

        title = xml.find('title').string
        print "START title", title.encode('utf-8')

        text = xml.find('text').string    
        print "text1 ", text[0:1000].encode('utf-8')

        # remove all (nested) { }s
        keep_replacing = True
        while keep_replacing:
            original = text
            text = re.sub(r'{[^{]*?}', ' ', text)
            print "text2a ", text[0:1000].encode('utf-8')
            keep_replacing = (original != text)
            print "keep_replacing a", keep_replacing

        # remove all (nested) ( )s
        keep_replacing = True
        while keep_replacing:
            original = text
            text = re.sub(r'\([^\(]*?\)', ' ', text)
            print "text2b ", text[0:1000].encode('utf-8')
            keep_replacing = (original != text)
            print "keep_replacing b", keep_replacing

        # remove all italicy, boldy things
        text = re.sub(r'\'\'[^\']*?\'\'', ' ', text)

        # unescape all XML 
        text = unescape(text, {"&apos;": "'", "&quot;": '"'}) 
        print "text3 ", text[0:1000].encode('utf-8')

        # remove all comments
        text = re.sub(r'<!--.*?-->', ' ', text)
        print "text4 ", text[0:1000].encode('utf-8')

        # we are now looking for the first [[link]]
        # a big problem is that links can be nested; 
        #   [[Image:foo.jpg|thumbnail|here is some [[link]] text]] But here is the [[proper]] link
        # and in this case we want to ignore both the Image:foo.jpg _and_ the [[link]] since it's nested in the image one
        # we do this by converting [[blah]] to <link>blah</link> so we can do it with soup
        text = re.sub('\[\[','<link>', re.sub('\]\]','</link>', text))
        print "text5 ", text[0:1000].encode('utf-8')
    
        # parse for <link> (being sure to handle recursive case) 
        # and pick first one
        parsedLinks = LinkParser(text)
        links = parsedLinks.findAll('link',recursive=False)
        link = first_valid_link(links)            
        if not link:
            sys.stderr.write("ERROR can't find valid link for ["+title.encode('utf-8')+"] :(\n")
            break
        print "link", link.encode('utf-8')

        # clean link up; anchors, _s, etc
        link = re.sub(r'[\#\|].*','', link)
        print "link sans anchor", link.encode('utf-8')
        link = re.sub('_',' ', link)
        print "link sans _", link.encode('utf-8')
        link = link[0].upper() + link[1:] # make sure it's first letter capital
        print "link upper", link.encode('utf-8')
        
        # done
        print ("FINAL\t"+title+"\t"+link).encode('utf-8')

#    output = title + "\t" + first_link
#    output_unescaped = unescape(output, {"&apos;": "'", "&quot;": '"'})        
#    print output_unescaped.encode('utf-8')
    except:
        sys.stderr.write("ERROR problem processing article for ["+title.encode('utf-8')+"] "+str(sys.exc_info()[0])+"\n")
        traceback.print_exc(file=sys.stderr)
