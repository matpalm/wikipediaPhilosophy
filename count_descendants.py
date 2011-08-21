#!/usr/bin/env python
import fileinput, re, sys

edges = {}
for line in open(sys.argv[1],'r').readlines():
    from_node, to_node = line.strip().split("\t")
    edges[from_node] = to_node

for node in sys.stdin:
    node = node.strip()
    last_node = node
    visited = set()

    while (node!=None):
        sys.stdout.write("LongValueSum:" + node + "\t1\n")
        if node == 'Philosophy':
            break
        
        node = edges.get(node)

        if node == None:
            sys.stderr.write("reporter:counter:path,unexpected_end_of_line,1\n")
            break
        elif node in visited:
            sys.stderr.write("reporter:counter:path,unexpected_cycle,1\n")
            break
        else:
            visited.add(node)
            last_node = node


