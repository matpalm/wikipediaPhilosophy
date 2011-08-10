cut -f4 $1 | perl -plne's/\\n/ /g'|xmllint --format - | less
