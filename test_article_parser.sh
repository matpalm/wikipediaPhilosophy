cat article.egs/*eg | ./articleParser.py > egs_actual
sdiff egs_actual egs_expected
