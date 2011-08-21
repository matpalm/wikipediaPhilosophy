#!/usr/bin/env bash
set -ex

cd ~/data

wget http://download.wikimedia.org/enwiki/20110722/enwiki-20110722-pages-articles.xml.bz2

bzcat enwiki-20110722-pages-articles.xml.bz2 | ~/wikipediaPhilosophy/flattenToOnePagePerLine.py > enwiki-20110722-pages-articles.pageperline.xml

cat enwiki-20110722-pages-articles.pageperline.xml | grep \<redirect\ \/\> > enwiki-20110722-pages-redirects.xml &
cat enwiki-20110722-pages-articles.pageperline.xml | grep -v \<redirect\ \/\> > enwiki-20110722-pages-articles.xml &

hadoop fs -mkdir /full/articles.xml
hadoop fs -mkdir /full/redirects.xml
hadoop fs -copyFromLocal enwiki-20110722-pages-articles.xml /full/articles.xml &
hadoop fs -copyFromLocal enwiki-20110722-pages-redirects.xml /full/redirects.xml &
wait

cd ~/wikipediaPhilosophy

hadoop jar ~/contrib/streaming/hadoop-streaming.jar \
 -input /full/redirects.xml -output /full/redirects \
 -mapper redirectParser.py -file redirectParser.py

pig -p INPUT=/full/redirects -p OUTPUT=/full/redirects.dereferenced1 -f dereference_redirects.pig
pig -p INPUT=/full/redirects.dereferenced1 -p OUTPUT=/full/redirects.dereferenced2 -f dereference_redirects.pig
pig -p INPUT=/full/redirects.dereferenced2 -p OUTPUT=/full/redirects.dereferenced3 -f dereference_redirects.pig
pig -p INPUT=/full/redirects.dereferenced3 -p OUTPUT=/full/redirects.dereferenced4 -f dereference_redirects.pig
hfs -mv /full/redirects /full/redirects.original
hfs -mv /full/redirects.dereferenced4 /full/redirects

hadoop jar ~/contrib/streaming/hadoop-streaming.jar \
 -input /full/articles.xml -output /full/edges \
 -mapper articleParser.py -file articleParser.py

pig -p INPUT=/full/edges -p OUTPUT=/full/edges.dereferenced -f dereference_redirects.pig
pig -p INPUT=/full/edges.dereferenced -p OUTPUT=/full/edges.dereferenced2 -f dereference_redirects.pig # sanity

hadoop fs -cat /full/edges.dereferenced/* > data/edges

java -Xmx8g -cp . DistanceToPhilosophy Philosophy data/edges >DistanceToPhilosophy.stdout 2>DistanceToPhilosophy.stderr

