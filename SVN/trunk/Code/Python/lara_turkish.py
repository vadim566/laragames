
# Code to invoke the Turkish NLP Pipeline for LARA tagging and lemmatisation. Used in lara_treetagger.py

# Sample command-line call:

# wget -O C:/tmp/turkish_out.txt "http://tools.nlp.itu.edu.tr/SimpleApi?tool=pipelineSSMorph&input=bir&token=4KhSDSXmAsWTbZrx915kjjuiD3icscVM"

import lara_utils
import urllib.parse

_url = 'http://tools.nlp.itu.edu.tr/SimpleApi'
_token = '4KhSDSXmAsWTbZrx915kjjuiD3icscVM'
_max_chars_in_request = 7500

def invoke_turkish_nlp_pipeline_for_lara_tagging_and_lemmatisation(FileIn, FileOut, Params):
    try:
        return invoke_turkish_nlp_pipeline_for_lara_tagging_and_lemmatisation1(FileIn, FileOut, Params)
    except Exception as e:
        lara_utils.print_and_flush(f'*** Error: something went wrong when sending {FileIn} for Turkish tagging and lemmatisation')
        lara_utils.print_and_flush(str(e))
        return False 
        
def invoke_turkish_nlp_pipeline_for_lara_tagging_and_lemmatisation1(FileIn, FileOut, Params):
    lara_utils.delete_file_if_it_exists(FileOut)
    Str = lara_utils.read_lara_text_file(FileIn)
    URLStr = urllib.parse.quote(Str)
    FileOut1 = lara_utils.absolute_file_name(FileOut)
    Call = f'wget -O {FileOut1} "{_url}?tool=pipelineSSMorph&input={URLStr}&token={_token}" >& /dev/null'
    Result = lara_utils.execute_lara_os_call(Call, Params)
    if Result == 0 and lara_utils.file_exists(FileOut):
        if not looks_like_valid_turkish_nlp_pipeline_reply_file(FileOut):
            lara_utils.print_and_flush(f'*** Error: bad reply from Turkish tagging and lemmatisation')
            try_to_print_start_of_reply_file(FileOut, 10)
            return False
        lara_utils.print_and_flush(f'--- Sent {FileIn} ({len(Str)} chars) for Turkish tagging and lemmatisation, producing {FileOut}')
        #try_to_print_start_of_reply_file(FileOut, 100)
        return FileOut
    else:
        lara_utils.print_and_flush(f'*** Error: something went wrong when sending {FileIn} for Turkish tagging and lemmatisation')
        return False

# It looks like a valid reply file if it mostly consists of lines of three elements separated by commas.
def looks_like_valid_turkish_nlp_pipeline_reply_file(File):
    try:
        Content = lara_utils.read_lara_text_file(File)
        Lines = Content.split('\n')
        SplitLineLengths = [ len(Line.split()) for Line in Lines ]
        NLines = len(SplitLineLengths)
        N3ElementLines = len( [ Len  for Len in SplitLineLengths if Len == 3 ])
        return NLines > 0 and N3ElementLines > 0 and N3ElementLines / NLines > 0.5
    except:
        return False

def try_to_print_start_of_reply_file(File, N):
    try:
        Content = lara_utils.read_lara_text_file(File)
        Lines = Content.split('\n')
        lara_utils.print_and_flush('\n'.join(Lines[:N]))
    except:
        lara_utils.print_and_flush('(Not able to read file)')


        
        
