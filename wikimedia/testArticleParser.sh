cat article.egs/*eg | ./articleParser.py 2>/dev/null | grep FINAL > egs_actual
diff egs_actual egs_expected
