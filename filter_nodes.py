#!/usr/bin/env python
# filter nodes from edges 
import fileinput, re, sys

allowed_nodes = set()
for line in open(sys.argv[1],'r').readlines():
    node, freq = line.strip().split("\t")
    allowed_nodes.add(node)

for edge in sys.stdin:
    edge = edge.strip()
    from_node, to_node = edge.split("\t")
    if from_node in allowed_nodes and to_node in allowed_nodes:
        print edge



