
import lara_config
import lara_utils
from googletrans import Translator

def test(Id):
    if Id == 'le_chien_jaune_small':
        mt_translate_spreadsheet('$LARA/tmp_resources/le_chien_jaune_tmp_translations_small.csv',
                                 '$LARA/tmp_resources/le_chien_jaune_tmp_translations_small_filled_in.csv',
                                 '$LARA/Content/le_chien_jaune/corpus/local_config.json')
    elif Id == 'le_chien_jaune':
        mt_translate_spreadsheet('$LARA/tmp_resources/le_chien_jaune_tmp_translations.csv',
                                 '$LARA/tmp_resources/le_chien_jaune_tmp_translations_filled_in.csv',
                                 '$LARA/Content/le_chien_jaune/corpus/local_config.json')
    else:
        lara_utils.print_and_flush(f'*** Error: unknown argument: {Id}')

def mt_translate_spreadsheet(CSVIn, CSVOut, ConfigFile):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if not Params:
        return False
    ContentIn0 = lara_utils.read_lara_csv(CSVIn)
    if len(ContentIn0) == 0:
        lara_utils.print_and_flush(f'*** Error {CSVIn} is empty')
        return False
    ( Header, ContentIn ) = ( ContentIn0[0], ContentIn0[1:] )
    NontrivialSourceStrings = [ Line[0] for Line in ContentIn if len(Line) >= 2 and len(Line[0]) > 0 and trivial_string(Line[1]) ]
    N = len(NontrivialSourceStrings)
    lara_utils.print_and_flush(f'--- Submitting {N} lines for translation...')
    Translations = mt_translate_strings(NontrivialSourceStrings, Params)
    if not Translations:
        lara_utils.print_and_flush(f'... failed')
        return False
    else:
        lara_utils.print_and_flush(f'... succeeded')
    Substs = { NontrivialSourceStrings[I]: Translations[I] for I in range(len(NontrivialSourceStrings)) }
    ContentOut = [ Header ] + [ apply_substs_to_line(Substs, Line) for Line in ContentIn ]
    lara_utils.write_lara_csv(ContentOut, CSVOut)
    lara_utils.print_and_flush(f'--- Translated spreadsheet {CSVIn} to {CSVOut} ({N} lines translated)')
    return True

def trivial_string(Str):
    return Str.isspace() or len(Str) == 0

def apply_substs_to_line(Substs, Line):
    if len(Line) < 2:
        return Line
    Source = Line[0]
    Target = Substs[Source] if Source in Substs else Line[1]
    return [ Source, Target ] + Line[2:]    

def mt_translate_strings(Strs, Params):
    if Params.language == '':
        lara_utils.print_and_flush('*** Error: "language" not set, cannot call MT')
        return False
    if Params.l1 == '':
        lara_utils.print_and_flush('*** Error: "l1" not set, cannot call MT')
        return False
    if Params.mt_engine == 'google':
        return google_translate_string_list(Strs, Params.language, Params.l1)
    else:
        lara_utils.print_and_flush('*** Error: unknown MT engine "{Params.mt_engine}", cannot call MT')
        return False

def google_translate_string(Str, SourceLang, TargetLang):
    Result0 = google_translate_string_list([ Str ], SourceLang, TargetLang)
    return False if not Result0 else Result0[0]

def google_translate_string_list(StrList, SourceLang, TargetLang):
    try:
        SourceLang1 = lang_to_google_lang(SourceLang)
        TargetLang1 = lang_to_google_lang(TargetLang)
        if not SourceLang1 or not TargetLang1:
            return False
        translator = Translator()
        lara_utils.print_and_flush(f'--- Google translating {StrList} from {SourceLang} to {TargetLang}')
        translations = translator.translate(StrList, src=SourceLang1, dest=TargetLang1)
        return [ translation.text for translation in translations ]
    except Exception as e:
        lara_utils.print_and_flush(f'*** Error when trying to Google translate from {SourceLang} to {TargetLang}')
        lara_utils.print_and_flush(str(e))

_lara_lang2google_lang = {'amharic': 'am',
                          'arabic': 'ar',
                          'basque': 'eu',
                          'bengali': 'bn',
                          'bulgarian': 'bg',
                          'catalan': 'ca',
                          'cherokee': 'chr',
                          'chinese': 'zh',
                          'croatian': 'hr',
                          'czech': 'cs',
                          'danish': 'da',
                          'dutch': 'nl',
                          'english': 'en',
                          'estonian': 'et',
                          'filipino': 'fil',
                          'finnish': 'fi',
                          'french': 'fr',
                          'german': 'de',
                          'greek': 'el',
                          'gujarati': 'gu',
                          'hebrew': 'iw',
                          'hindi': 'hi',
                          'hungarian': 'hu',
                          'icelandic': 'is',
                          'indonesian': 'id',
                          'italian': 'it',
                          'japanese': 'ja',
                          'kannada': 'kn',
                          'korean': 'ko',
                          'latvian': 'lv',
                          'lithuanian': 'lt',
                          'malay': 'ms',
                          'malayalam': 'ml',
                          'marathi': 'mr',
                          'norwegian': 'no',
                          'polish': 'pl',
                          'portuguese (brazil)': 'pt-BR',
                          'portuguese': 'pt-PT',
                          'romanian': 'ro',
                          'russian': 'ru',
                          'serbian': 'sr',
                          'slovak': 'sk',
                          'slovenian': 'sl',
                          'spanish': 'es',
                          'swahili': 'sw',
                          'swedish': 'sv',
                          'tamil': 'ta',
                          'telugu': 'te',
                          'thai': 'th',
                          'turkish': 'tr',
                          'ukrainian': 'uk',
                          'urdu': 'ur',
                          'vietnamese': 'vi',
                          'welsh': 'cy'}

def lang_to_google_lang(Lang):
    if not Lang in _lara_lang2google_lang:
        lara_utils.print_and_flush(f'*** Error: language not supported by Google Translate: {Lang}')
        return False
    return _lara_lang2google_lang[Lang]

    

