cat article.egs/*eg | ./articleParser.py 2>/dev/null > egs_actual
sdiff egs_actual egs_expected
