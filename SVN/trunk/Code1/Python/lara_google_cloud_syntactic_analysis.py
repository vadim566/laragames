
from google.cloud import language_v1
import lara_japanese
import lara_utils

def invoke_pipeline_for_lara_tagging_and_lemmatisation(PlainFile, OutputFile, Params):
    Str = lara_utils.read_lara_text_file(PlainFile)
    Lang = Params.language
    TaggingTuples = string_to_tagging_triples(Str, Lang)
    if TaggingTuples == False:
        return False
    else:
        TaggingTuples1 = maybe_consolidate_tagging_tuples(TaggingTuples, Lang)
        write_tagging_triples_to_file(TaggingTuples1, OutputFile)
        return OutputFile

# A tagging triple is a triple of the form [ Surface, Tag, Lemma ]

def string_to_tagging_triples(Str, Lang):
    GoogleLangId = lara_lang_id_to_google_lang_id(Lang)
    if GoogleLangId == False:
        lara_utils.print_and_flush('*** Error: "{Lang}" not supported by Google Cloud syntax analysis')
        return False
    client = language_v1.LanguageServiceClient()
    type_ = language_v1.Document.Type.PLAIN_TEXT
    encoding_type = language_v1.EncodingType.UTF8
    document = {"content": Str,
                "type_": type_,
                "language": GoogleLangId}
    try:
        lara_utils.print_and_flush(f'--- Sending {Lang} text ({len(Str)} chars) for Google Cloud syntactic analysis')
        response = client.analyze_syntax(request = {'document': document,
                                                    'encoding_type': encoding_type})
        Tuples = [ [ token.text.content, token.part_of_speech.tag.name, token.lemma.lower() ]
                   for token in response.tokens ]
        lara_utils.print_and_flush(f'--- Done ({len(Tuples)} tokens found)')
        return Tuples
    except Exception as e:
        lara_utils.print_and_flush(f'*** Warning: something went wrong during call to Google Cloud')
        lara_utils.print_and_flush(str(e))
        return False

def write_tagging_triples_to_file(TaggingTuples, OutputFile):
    lara_utils.write_lara_text_file('\n'.join( [ tagging_tuple_to_text_line(Tuple) for Tuple in TaggingTuples ]),
                                    OutputFile)

def tagging_tuple_to_text_line(Tuple):
    return '\t'.join(Tuple)                              

_lara_lang_to_google_lang = { 'mandarin': 'zh',
                              'english': 'en',
                              'french': 'fr',
                              'german': 'de',
                              'italian': 'it',
                              'japanese': 'ja',
                              'korean': 'ko',
                              'portuguese': 'pt',
                              'russian': 'ru',
                              'spanish': 'es' }

def is_language_supported_by_google_cloud_tagging(Lang):
    return Lang in _lara_lang_to_google_lang

def lara_lang_id_to_google_lang_id(Lang):
    return _lara_lang_to_google_lang[Lang] if Lang in _lara_lang_to_google_lang else False

def maybe_consolidate_tagging_tuples(TaggingTuples, Lang):
    if Lang == 'japanese':
        return lara_japanese.consolidate_google_tagging_tuples(TaggingTuples)
    else:
        return TaggingTuples
    
