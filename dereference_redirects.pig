-- pig -p INPUT=blah -p OUTPUT=blah2 -f dereference_redirects.pig
articles = load '$INPUT' as (from:chararray, to:chararray);
redirects = load '/full/redirects' as (from:chararray, to:chararray);
joined = join articles by to left outer, redirects by from;
redirected = foreach joined generate 
 articles::from as from,
 ((redirects::to is null) ? articles::to : redirects::to) as to;
store redirected into '$OUTPUT';