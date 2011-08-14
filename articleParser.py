#!/usr/bin/env python
import fileinput, re, sys, traceback
from BeautifulSoup import BeautifulStoneSoup
from xml.sax.saxutils import unescape

class LinkParser(BeautifulStoneSoup):
    NESTABLE_TAGS = {
        'link': ['link']
    }

def meta_article(link):
    return ':' in link

def internal_link(link):
    return link.startswith('#')

def first_valid_link(links, title):
    for link_node in links:
        link = link_node.text
#        print "raw link",link.encode('utf-8')
        link = re.sub(r'[\#\|].*','', link)
#        print "link sans anchor", link.encode('utf-8')
        link = re.sub('_',' ', link)
#        print "link sans _", link.encode('utf-8')
        if not link:
            continue
        link = link[0].upper() + link[1:] # make sure it's first letter capital
#        print "link upper", link.encode('utf-8')
        if not (meta_article(link) or internal_link(link) or link==title):
            return link
#        print "ignoring link", link.encode('utf-8')
    return None

def replace_nested(regex, text):
    while True:
        original = text
        text = regex.sub(' ', text)
#        print "text2 ", text[0:1000].encode('utf-8')
        if original == text:
            return text

def extract_links(text, remove_tags_and_content):
    # remove all (nested) { }s
    text = replace_nested(re.compile('{[^{]*?}'), text)
#    sys.stderr.write("text2 "+text[0:800].encode('utf-8')+"\n")

    # remove all (nested) ( )s
    # cant just remove all () since it removes () from links eg Letter_(Alphabet)
    # text = replace_nested(re.compile('\([^\(]*?\)'), text)

    # unescape all XML (this includes comments for the next section)
    text = unescape(text, {"&apos;": "'", "&quot;": '"'})
#    sys.stderr.write("text3 "+text[0:800].encode('utf-8')+"\n")

    # remove stray quotes (plays havok with italics and bold removal
    text = re.sub(r"[^']'[^']",' ',text)
#    sys.stderr.write("\ntext3a"+text[0:2500].encode('utf-8')+"\n")

    # sanitize italics and bold
    # depending on how aggressive we're trying to be either
    # remove _all_ the content or just the tags
    substitution = r" " if remove_tags_and_content else r"\1"
    text = re.sub(r"'''([^']*?)'''", substitution, text)
#    sys.stderr.write("\ntext3b"+text[0:2500].encode('utf-8')+"\n")
    text = re.sub(r"''([^']*?)''", substitution, text)
#    sys.stderr.write("\ntext3c"+text[0:2500].encode('utf-8')+"\n")

        # remove all comments (never nested)
    text = re.sub(r'<!--.*?-->', ' ', text)
#        print "text4 ", text[0:1000].encode('utf-8')

        # for some reason, no idea why, self closed tags, like ref in the following link
        #  <ref name="OED"/> is the first <link>Letter  |letter</link> and a <link>vowel</link> in the
        # cause parsedLinks.findAll recursive false to return nothing for links?
    text = re.sub('<[^<]*/>', ' ', text)
#        print "text7 ", text[0:1000].encode('utf-8')

        # refs cause no end of grief to beautiful soup (see physics.eg) ditch them all
        # (and i dont think they are ever nested)
    text = re.sub(r'<ref[\ >].*?</ref>', ' ', text)
#        print "text4b", text[0:1000].encode('utf-8')

        # and pres cause some problems too (see fidonet.eg)
    text = re.sub(r'<pre[\ >].*?</pre>', ' ', text)
#        print "text4c", text[0:1000].encode('utf-8')

        # we are now looking for the first [[link]]
        # a big problem is that links can be nested; 
        #   [[Image:foo.jpg|thumbnail|here is some [[link]] text]] But here is the [[proper]] link
        # and in this case we want to ignore both the Image:foo.jpg _and_ the [[link]] since it's nested in the image one
        # we do this by converting [[blah]] to <link>blah</link> so we can do it with soup
    text = re.sub('\[\[','<link>', re.sub('\]\]','</link>', text))
#    sys.stderr.write("text5 "+text[0:800].encode('utf-8')+"\n")

        # remove links in ( )s
        # primarily this is to address the common case of 
        #  foo (some other <link>bar</link) and then the <link>rest</link>...
        # where the first link in brackets (bar) is not a good choice
        # this re is a bit funky, needs some more examples me thinks.. (a.eg and allah.eg have been interesting cases)
    text = re.sub(r'\(([^\(\)]*?)<link>(.*?)</link>(.*?)\)', ' ', text)
#    sys.stderr.write("text6 "+text[0:800].encode('utf-8')+"\n")

        # occasionally some wikipedia articles are wrapped in <html><body>, or have bizarre stray br's or something.
        # non recursive findall fails on this
        # ( there's probably a way to config this to be allowed but more hacktastic to just remove them in this case )
        # ( perhaps even just trim away _all_ non link tags? down that path lies madness, really need to sort out the find... )
    for tag in ['html','body','noinclude','br','onlyinclude']:
        text = re.sub('<'+tag+'>',' ',text)
    
        # parse for <link> (being sure to handle recursive case) and pick first one
    links = LinkParser(text).findAll('link', recursive=False)
#        print "links", links
    return links


for line in fileinput.input():
    try:
        xml = BeautifulStoneSoup(line)

        title = xml.find('title').string
#        print "START title", title.encode('utf-8')

        if (meta_article(title)):
            sys.stderr.write("reporter:counter:parse,ignore_meta_article,1\n")
            sys.stderr.write("ignore meta article ["+title.encode('utf-8')+"]\n")
            continue

        text = xml.find('text').string    
#        sys.stderr.write("text1 "+text[0:800].encode('utf-8')+"\n")

        links = extract_links(text, True)
        link = first_valid_link(links, title)
        if not link:
            # try again, being less aggressive in the removal
            sys.stderr.write("reporter:counter:parse,more_aggresive_link_removal,1\n")
            links = extract_links(text, False)
            link = first_valid_link(links, title)
            if not link:
                sys.stderr.write("reporter:counter:parse,no_valid_links,1\n")
                sys.stderr.write("ERROR can't find valid link for ["+title.encode('utf-8')+"] :(\n")
                continue

        # done
        print (title+"\t"+link.strip()).encode('utf-8')

    except:
        sys.stderr.write("reporter:counter:parse,exception_parsing_article,1\n")
        sys.stderr.write("ERROR problem processing article for ["+title.encode('utf-8')+"] "+str(sys.exc_info()[0])+"\n")
        traceback.print_exc(file=sys.stderr)
