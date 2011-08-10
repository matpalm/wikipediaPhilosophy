#!/usr/bin/env python
import fileinput, re, sys

redirects = {}
redirects_file = open('freebase-wex-2009-01-12-redirects.tsv', 'r')
line = redirects_file.readline()
sys.stderr.write(">read redirects\n")
while line:
    id, from_node, to_node = line.strip().split("\t")    
    # if from_node in redirects: some weird stuff going on with unicode chars, ignore for now
    #     raise Exception("already have from key ["+from_node+"]")
    redirects[from_node] = to_node
    line = redirects_file.readline()
redirects_file.close()
sys.stderr.write("<read redirects\n")

def follow_redirects(node, redirects, count):
    if node in redirects.keys():
        redirected = redirects[node]
        sys.stderr.write("redirecting from ["+node+"] to ["+redirected+"] (count="+`count`+")\n")
        return follow_redirects(redirected, redirects, count+1)
    else:
        sys.stderr.write("done redirecting node=["+node+"] count=["+`count`+"]\n")
        return node

for line in sys.stdin:
    from_node, to_node = line.strip().split("\t")
    sys.stderr.write("processing ["+from_node+"] -> ["+to_node+"]\n")
    redirected_to_node = follow_redirects(to_node, redirects, 0)
    print from_node + "\t" + redirected_to_node


