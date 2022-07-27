import os

def invoke_icelandic_pipeline_test(Str):
    uStr = Str.encode('utf8')
    _url = 'malvinnsla.arnastofnun.is'
    FileOut = 'C:/tmp/icelandic_output.json'
    #Call = f'curl -X POST -F "text={uStr}" -F "lemma=on" -F "utf8encoded=on" -F "expand_tag=on" {_url} > {FileOut}'
    #Call = f'curl -X POST -F "text={uStr}" -F "lemma=on" -F "expand_tag=on" {_url} > {FileOut}'
    Call = f'curl -X POST -F "text={Str}" -F "lemma=on" -F "expand_tag=on" {_url} > {FileOut}'
    Result = os.system(Call)
    if Result == 0:
        print(f'--- Sent "{Str}" for Icelandic tagging and lemmatisation, written {FileOut}')
    else:
        print(f'*** Error: something went wrong when sending "{Str}" for Icelandic tagging and lemmatisation')

# Typical call
#invoke_icelandic_pipeline_test('Hei')
