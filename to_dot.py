#!/usr/bin/env python
import sys

edges_file = sys.argv[1]
descendants_file = sys.argv[2]

weights = {}
for node_weight in open(descendants_file,'r').readlines():
    node, weight = node_weight.strip().split("\t")
    weights[node] = int(weight)

minw = min(weights.values())
delta = max(weights.values()) - minw
penwidths = {}
#print "weights", weights
for node in weights.keys():
    normalised = float(weights[node] - minw) / delta
    weights[node] = (normalised * 10000) + 1
    penwidths[node] = (normalised * 30) + 1
#print "weights", weights

print "digraph {"
print 'rankdir="LR"'
print 'graph [ truecolor bgcolor="#00000000" ];'
print 'node [ style=filled ];'
for edge in open(edges_file,'r').readlines():
    from_node, to_node = edge.strip().split("\t")
#    print '"' + from_node + '" -> "' + to_node + '" [ penwidth= ' + str(penwidths[from_node])+ '];'
    print '"' + from_node + '" -> "' + to_node + '" [ weight = ' + str(weights[from_node]) + ', penwidth= ' + str(penwidths[from_node])+ '];'
print "}"
