#!/usr/bin/env python
import fileinput, re, sys
from datetime import datetime

# slurp stdin
sys.stderr.write(str(datetime.now()) + " > read\n")
all_nodes = set()
outbound_edges = {}
for line in fileinput.input():
    to_node, from_node = line.strip().split("\t") # note! in other order!
    all_nodes.add(from_node)
    all_nodes.add(to_node)
    if from_node in outbound_edges.keys():
        outbound_edges[from_node].append(to_node)
    else:
        outbound_edges[from_node] = [to_node]
sys.stderr.write(str(datetime.now()) + " < read\n")

# breadth first walk from starting point
distance = 0
this_pass = ['Philosophy']
while len(this_pass) > 0:
    next_pass = []
    for node in this_pass:
        sys.stderr.write(str(datetime.now()) + " processing ["+node+"]")
        print node + "\t" + str(distance)
        all_nodes.remove(node)
        if node in outbound_edges.keys():
            next_pass += outbound_edges[node]
    distance += 1
    this_pass = next_pass

# emit all unvisited nodes
for unvisited_node in all_nodes:
    print unvisited_node + "\t-1"


