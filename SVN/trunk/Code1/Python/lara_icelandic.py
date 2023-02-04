
# Code to access the Icelandic tools for LARA tagging and lemmatisation. Used in lara_treetagger.py

import lara_utils
import os
import sys

_url = 'malvinnsla.arnastofnun.is'
#_url = '130.208.178.108:5003'
_max_chars_in_request = 15000

# ----------------------------------------
 
def invoke_icelandic_pipeline_for_lara_tagging_and_lemmatisation(FileIn, FileOut, Params):
    try:
        return invoke_icelandic_pipeline_for_lara_tagging_and_lemmatisation1(FileIn, FileOut, Params)
    except Exception as e:
        lara_utils.print_and_flush(f'*** Error: something went wrong when sending {FileIn} for Icelandic tagging and lemmatisation')
        lara_utils.print_and_flush(str(e))
        return False
        
def invoke_icelandic_pipeline_for_lara_tagging_and_lemmatisation1(FileIn, FileOut, Params):
    lara_utils.delete_file_if_it_exists(FileOut)
    Str = lara_utils.read_lara_text_file(FileIn)
    uStr = remove_characters_that_curl_doesnt_like(Str).encode('utf8')
    FileOut1 = lara_utils.absolute_file_name(FileOut)
    Call = f'curl -X POST -F "text={uStr}" -F "lemma=on" -F "utf8encoded=on" -F "expand_tag=on" {_url} > {FileOut1}'
    Result = lara_utils.execute_lara_os_call(Call, Params)
    #Result = lara_utils.execute_lara_os_call_direct(Call)
    if Result == 0 and lara_utils.file_exists(FileOut):
        if not looks_like_valid_icelandic_reply_file(FileOut):
            lara_utils.print_and_flush(f'*** Error: bad reply from Icelandic processing. Expecting JSON file containing a dict with "paragraphs" at top level')
            try_to_print_start_of_reply_file(FileOut)
            return False
        lara_utils.print_and_flush(f'--- Sent {FileIn} ({len(Str)} chars) for Icelandic tagging and lemmatisation, producing {FileOut}')
        #return True
        return FileOut
    else:
        lara_utils.print_and_flush(f'*** Error: something went wrong when sending {FileIn} for Icelandic tagging and lemmatisation')
        return False

# Remove quotes and parentheses because they mess up the curl invocation - haven't yet found a way to escape them.
def remove_characters_that_curl_doesnt_like(Str):
    for Char in '"()':
        Str = Str.replace(Char, '')
    Str = Str.replace('\'', '’')
    return Str

def looks_like_valid_icelandic_reply_file(File):
    try:
        Content = lara_utils.read_json_file(File)
        #lara_utils.write_json_to_file(Content, '$LARA/tmp/tmp_icelandic_tagging.json')
        #return isinstance(Content, dict) and 'sentences' in Content
        return isinstance(Content, dict) and 'paragraphs' in Content 
    except:
        return False

def try_to_print_start_of_reply_file(File):
    try:
        Content = lara_utils.read_lara_text_file(File)
        Lines = Content.split('\n')
        lara_utils.print_and_flush('\n'.join(Lines[:5]))
    except:
        lara_utils.print_and_flush('(Not able to read file)')

# ----------------------------------------

# Temporary stuff for testing
def test_icelandic(Id):
    Files = { 'genesis1': '$LARA/Content/sample_icelandic/corpus/genesis1_plain.txt' }
    if not Id in Files:
        lara_utils.print_and_flush(f'Id {Id} not found')
        return False
    FileIn = Files[Id]
    FileOut = '$LARA/tmp/icelandic_out.json'
    import lara_config
    Params = lara_config.default_params()
    invoke_icelandic_pipeline_for_lara_tagging_and_lemmatisation(FileIn, FileOut, Params),
    lara_utils.prettyprint(lara_utils.read_json_file(FileOut))

def invoke_icelandic_pipeline_minimal(Str):
    uStr = Str.encode('utf8')
    FileOut = 'C:/tmp/icelandic_output.json'
    Call = f'curl -X POST -F "text={uStr}" -F "lemma=on" -F "utf8encoded=on" -F "expand_tag=on" {_url} > {FileOut}'
    Result = os.system(Call)
    if Result == 0:
        print(f'--- Sent "{Str}" for Icelandic tagging and lemmatisation, written {FileOut}')
    else:
        print(f'*** Error: something went wrong when sending "{Str}" for Icelandic tagging and lemmatisation')

