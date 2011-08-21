set -ex

hadoop jar ~/contrib/streaming/hadoop-streaming.jar \
 -input /full/redirects.xml -output /full/redirects \
 -mapper redirectParser.py -file redirectParser.py

pig -p INPUT=/full/redirects -p OUTPUT=/full/redirects.dereferenced1 -f dereference_redirects.pig
pig -p INPUT=/full/redirects.dereferenced1 -p OUTPUT=/full/redirects.dereferenced2 -f dereference_redirects.pig
pig -p INPUT=/full/redirects.dereferenced2 -p OUTPUT=/full/redirects.dereferenced3 -f dereference_redirects.pig
pig -p INPUT=/full/redirects.dereferenced3 -p OUTPUT=/full/redirects.dereferenced4 -f dereference_redirects.pig
hfs -mv /full/redirects /full/redirects.original
hfs -mv /full/redirects.dereferenced4 /full/redirects
