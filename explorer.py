#!/usr/bin/env python
import fileinput, re, sys

edges = {}
print "reading..."
for line in open('edges','r').readlines():
    from_node, to_node = line.strip().split("\t")
    edges[from_node] = to_node

dot_file = open('graph.dot','w')
dot_file.write("digraph {\n")

while True:
    node = raw_input("node? ")
    last_node = node

    if node=='':
        break

    while not(node == 'Philosophy' or node == None):
        print node,"->",
        node = edges.get(node)
        if node:
            dot_file.write('"'+last_node+'"->"'+node+'\"\n')
        last_node = node

    if (node=='Philosophy'):
        print node
    else:
        print "DONE"

dot_file.write("}\n")
dot_file.close()

