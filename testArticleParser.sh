cat article.egs/*eg | ./articleParser.py 2>/dev/null > egs_actual
diff egs_actual egs_expected
