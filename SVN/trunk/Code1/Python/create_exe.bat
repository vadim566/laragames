pyinstaller -y -F ^
    --add-data ./lara_newcontent_template.zip;. ^
    --add-data ./lara_postags.json;. ^
    --add-data ./lara_utf8-tokenize.perl;. ^
    lara_run.py

