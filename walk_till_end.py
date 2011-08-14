#!/usr/bin/env python
import fileinput, re, sys

#sys.stderr.write("parsing edges\n")
edges = {}
for line in open('edges'):
    a,b = line.strip().split("\t")
    edges[a] = b
#sys.stderr.write("done\n")

for node in fileinput.input():
    node = node.strip()
#    sys.stderr.write("parsing ["+node+"]\n")

    if not edges.has_key(node):
        sys.stdout.write(node + "\tNA\t0\tno node\n")
        continue

    starting_node = node
    num_hops = 0
    visited = set()
    visited.add(starting_node)
    exit_reason = None
    while True:
#        sys.stderr.write("["+node+"] -> ")
        node = edges[node]
#        sys.stderr.write("["+node+"]\n")
        num_hops += 1

        if not edges.has_key(node):
            exit_reason = "end of line"
        if num_hops > 1000:
            exit_reason = "hop limit"
        if node in visited:
            exit_reason = "cycle"

        if exit_reason:
            break

        visited.add(node)

    sys.stdout.write(starting_node + "\t" + node + "\t" + str(num_hops) + "\t" + exit_reason + "\n")


