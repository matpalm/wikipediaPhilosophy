#!/usr/bin/env bash
set -x

hadoop fs -rmr /full/edges
hadoop jar ~/contrib/streaming/hadoop-streaming.jar \
  -input /full/articles.xml -output /full/edges \
  -mapper articleParser.py -file articleParser.py

hadoop fs -rmr /full/edges.dereferenced
pig -p INPUT=/full/edges -p OUTPUT=/full/edges.dereferenced -f dereference_redirects.pig

hadoop fs -cat /full/edges.dereferenced/* > data/edges

time java -Xmx8g -cp . DistanceToPhilosophy Philosophy data/edges >DistanceToPhilosophy.stdout 2>DistanceToPhilosophy.stderr

grep ^didnt DistanceToPhilosophy.stdout | sed -es/didnt\ visit\ // > didnt_visit
./walk_till_end.py < didnt_visit >walk_till_end.stdout 2>walk_till_end.stderr
grep end\ of\ line$ walk_till_end.stdout | cut -f2 | sort | uniq -c | sort -nr | head
