
# Code to access the Irish tools for LARA tagging and lemmatisation. Used in lara_treetagger.py

import lara_utils
import os
import sys
import requests, json


_url = 'https://phoneticsrv3.lcs.tcd.ie/irishfst/api'
_max_chars_in_request = 15000

# Stuff for testing
def test_irish(Id):
    Files = { 'genesis1': '$LARA/Content/sample_irish/corpus/genesis1_plain.txt' }
    if not Id in Files:
        lara_utils.print_and_flush(f'Id {Id} not found')
        return False
    FileIn = Files[Id]
    FileOut = '$LARA/tmp/irish_out.json'
    import lara_config
    Params = lara_config.default_params()
    invoke_irish_pipeline_for_lara_tagging_and_lemmatisation(FileIn, FileOut, Params),
    lara_utils.prettyprint(lara_utils.read_json_file(FileOut))

def invoke_irish_pipeline_minimal(Str):
    uStr = Str.encode('utf8')
    FileOut = '/tmp/irish_output.json'
    #Call = f'curl -X POST -F "text={uStr}" -F "lemma=on" -F "utf8encoded=on" -F "expand_tag=on" {_url} > {FileOut}'
    #Result = os.system(Call)
    response = request.get("%s?text=%s" % (_url, uStr))
    data = response.json()
    with open(FileOut, "w") as out:
        out.write(data)
    
    if data == []:
        print(f'--- Sent "{Str}" for Irish tagging and lemmatisation, written {FileOut}')
    else:
        print(f'*** Error: something went wrong when sending "{Str}" for Irish tagging and lemmatisation')

# ----------------------------------------
 
def invoke_irish_pipeline_for_lara_tagging_and_lemmatisation(FileIn, FileOut, Params):
    try:
        return invoke_irish_pipeline_for_lara_tagging_and_lemmatisation1(FileIn, FileOut, Params)
    except Exception as e:
        lara_utils.print_and_flush(f'*** Error: something went wrong when sending {FileIn} for Irish tagging and lemmatisation')
        lara_utils.print_and_flush(str(e))
        return False
        
def invoke_irish_pipeline_for_lara_tagging_and_lemmatisation1(FileIn, FileOut, Params):
    lara_utils.delete_file_if_it_exists(FileOut)
    Str = lara_utils.read_lara_text_file(FileIn)
    #uStr = Str.encode('utf8')
    FileOut1 = lara_utils.absolute_file_name(FileOut)
    #Call = f'curl -X POST -F "text={uStr}" -F "lemma=on" -F "utf8encoded=on" -F "expand_tag=on" {_url} > {FileOut}'
    #Result = lara_utils.execute_lara_os_call(Call, Params)
    inSents = Str.split("\n")
    outSents = {"sentences":[]}
    for inSent in inSents:
        response = requests.get("%s?text=%s" % (_url, inSent))
        data = response.json()
        #print(json.dumps(data))
        outSents["sentences"].append(data)
        
    with open(FileOut1, "w") as out:
        out.write(json.dumps(outSents))
    #with open("/tmp/irishfst_out.json", "w") as out:
    #    out.write(json.dumps(outSents, indent=4))


    if response and lara_utils.file_exists(FileOut):
        if not looks_like_valid_irish_reply_file(FileOut):
            lara_utils.print_and_flush(f'*** Error: bad reply from Irish processing')
            try_to_print_start_of_reply_file(FileOut)
            return False
        lara_utils.print_and_flush(f'--- Sent {FileIn} for Irish tagging and lemmatisation, producing {FileOut1}')
        #return True
        return FileOut
    else:
        lara_utils.print_and_flush(f'*** Error: something went wrong when sending {FileIn} for Irish tagging and lemmatisation')
        return False

def looks_like_valid_irish_reply_file(File):
    try:
        Content = lara_utils.read_json_file(File)
        return isinstance(Content, dict) and 'sentences' in Content 
        #return isinstance(Content, list) 
    except:
        return False

def try_to_print_start_of_reply_file(File):
    try:
        Content = lara_utils.read_lara_text_file(File)
        Lines = Content.split('\n')
        lara_utils.print_and_flush('\n'.join(Lines[:5]))
    except:
        lara_utils.print_and_flush('(Not able to read file)')




def read_irish_tagger_output(File):
    try:
        Paragraph = lara_utils.read_json_file(File)
        return [ word_tag_and_lemma_for_irish_word_rec(WordRec) \
                 for Sent in Paragraph['sentences'] for WordRec in Sent ]
    except:
        lara_utils.print_and_flush(f'Unable to read read Irish result file {File}')
        return False

def word_tag_and_lemma_for_irish_word_rec(WordRec):
    Word = WordRec['word'] if 'word' in WordRec else '*unknown_word*'
    Tag = WordRec['tags'] if 'tags' in WordRec else '*unknown_tag*'
    Lemma = WordRec['lemma'] if 'lemma' in WordRec else '*unknown_lemma*'
    #print(f"{Word}\t{Lemma}\t{Tag}")
    return [ [ Word ], Tag, Lemma ]
    
## Typical TreeTagger output lines
##l'      DET:def il
##altre   ADJ     altro
##cose    NOM     cosa

## Convert a TreeTagger output line into a pair.
## We make the surface word into a one-element list
## to be compatible with the minimal-tagging interface, which can have a multiword as the surface word

def treetagger_output_line_to_tag_tuple(Line, Language):
    Components = Line.split()
    if len(Components) == 3:
        ( SurfaceWord, Tag, Lemmas ) = Components
        LemmaList = Lemmas.split('|')
        return [ [ SurfaceWord ], Tag, LemmaList[0] ]
    else:
        return False

