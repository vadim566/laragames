
import lara_utils
import lara_top
# Remove circular import
#import lara_flashcards
import re
import copy

# --------------------------------------------------------

# Declarations

_language_ui_fallback = 'english'

# all fixed texts that are written to the HTML files should be routed through here
# (see function get_ui_text below)

ui_texts = {
    'english': {
        'toggle_translation_button' : 'toggle segment translations',
        'frequency_index': 'Frequency index',
        'alphabetical_index': 'Alphabetical index',
        'notes': 'Notes',
        'table_of_contents': 'Table of Contents',
        'index_heading_rank' : 'Rank', 
        'index_heading_word': 'Word',
        'index_heading_freq': 'Freq', 
        'index_heading_cumul': 'Cumul',
        'index_heading_note': 'Note',
        'next_page_title': 'next page',
        'prev_page_title': 'previous page',
        'first_page_title': 'first page',
        'set_bookmark': 'set bookmark',
        'goto_bookmark': 'go to bookmark',
        'unknown': '(unknown text id)'
    },
    'german': {
        'toggle_translation_button' : 'Übersetzungen umschalten',
        'frequency_index': 'Häufigkeitsindex',
        'alphabetical_index': 'Alphabetischer Index',
        'table_of_contents': 'Inhaltsverzeichnis',
        'index_heading_rank' : 'Rang', 
        'index_heading_word': 'Wort', 
        'index_heading_freq': 'Häufigk.', 
        'index_heading_cumul': 'kumuliert',
        'next_page_title': 'nächste Seite',
        'prev_page_title': 'vorherige Seite',
        'first_page_title': 'erste Seite',
        'set_bookmark': 'Lesez. setzen',
        'goto_bookmark': 'zu Lesez.',
        'unknown': '(unbekannte Textmarke)'
    },
    # TODO: same entries for other languages...
}

_permitted_bool_values = [ 'yes', 'no' ]
_permitted_word_translation_types = ['lemma', 'surface_word_type', 'surface_word_token']
_permitted_font_size_values = [ 'xx-small', 'x-small', 'small', 'medium', 'large', 'x-large', 'xx-large' ]
# Should allow uppercase and lowercase accented characters
_lara_id_pattern = '[A-Za-z\u00C0-\u017F][A-Za-z\u00C0-\u017F0-9_-]*'
_supported_mt_engines = [ 'google' ]
_supported_chinese_tokenisers = [ 'sharoff', 'jieba' ]
_permitted_retagging_strategies = [ '', 'replace_all', 'replace_lemma', 'replace_pos', 'remove_mwe' ]
# We may have more kinds of flashcards later, start with the following
_known_flashcard_types = [
    'lemma_translation_ask_l2',
    'lemma_translation_ask_l1',
    'lemma_translation_ask_l2_audio',
    'token_translation_ask_l2',
    'token_translation_ask_l2_audio',
    'signed_video_ask_l2',
    'sentence_with_gap'
    ]
_known_flashcard_levels = [ 'beginner', 'intermediate', 'advanced', 'multiword_expressions' ]
_html_styles = [ 'old', 'new', 'social_network' ]

# These colors are defined in lara_html.py
lara_html_colours = [
    'red',
    'light_red',
    'pink',
    'green',
    'light_green',
    'blue',
    'light_blue',
    'burgundy',
    'yellow',
    'orange',
    'purple',
    'violet',
    'brown',
    'gray',
    'black'
    ]

# Needed for LARA questionnaires, lara_tts_human_eval
_corpus_id_to_number = { 'french': 11,
                         'english': 12,
                         'italian': 13,
                         'polish': 14,
                         'japanese': 15,
                         'farsi': 16,
                         'icelandic': 17,
                         'slovak': 18,
                         'irish': 19,
                         'mandarin': 20
                         }


_explanations = { '[A-Za-z\u00C0-\u017F][A-Za-z\u00C0-\u017F0-9_-]*': 'A LARA ID can only include letters, numbers, - and _, and must start with a letter' }

# Relevant to conversion to phonetic text
_phonetically_spelled_languages = { 'barngarla': [ 'a', 'ai', 'aw',
                                                   'b', 'd',
                                                   'dy', 'dh', 'g', 'i',
                                                   'ii', 'l', 'ly', 'm',
                                                   'n', 'ng', 'nh', 'ny',
                                                   'oo', 'r', 'rr', 'rd',
                                                   'rl', 'rn', 'w', 'y'
                                                   ],
                                    'hebrew': [ 'א',
                                                'ב',
                                                'ג',
                                                'ד',
                                                'ה',
                                                'ו',
                                                'ז',
                                                'ח',
                                                'ט',
                                                'י',
                                                [ 'כ', 'ך' ],
                                                'ל',
                                                [ 'מ', 'ם' ],
                                                [ 'נ', 'ן' ],
                                                'ס',
                                                'ע',
                                                [ 'פ', 'ף' ],
                                                [ 'צ', 'ץ' ],
                                                'ק',
                                                'ר',
                                                'ש',
                                                'ת'
                                                ],
                                    'arabic': [ [ 'ا', 'ﺍ', 'ﺎ',
                                                  'آ', 'ﺁ', 'ﺂ',
                                                  'أ', 'إ' ],
                                                [ 'ب', 'ﺏ', 'ﺐ', 'ﺒ', 'ﺑ' ],
                                                [ 'ت', 'ﺕ', 'ﺖ', 'ﺘ', 'ﺗ' ],
                                                [ 'ث', 'ﺙ', 'ﺚ', 'ﺜ', 'ﺛ' ],
                                                [ 'ج', 'ﺝ', 'ﺞ', 'ﺠ', 'ﺟ' ],
                                                [ 'ح', 'ﺡ', 'ﺢ', 'ﺤ', 'ﺣ' ],
                                                [ 'خ', 'ﺥ', 'ﺦ', 'ﺨ', 'ﺧ' ],
                                                [ 'د', 'ﺩ', 'ﺪ' ],
                                                [ 'ذ', 'ﺫ', 'ﺬ' ],
                                                [ 'ر', 'ﺭ', 'ﺮ' ],
                                                [ 'ز', 'ﺯ', 'ﺰ' ],
                                                [ 'س', 'ﺱ', 'ﺲ', 'ﺴ', 'ﺳ' ],
                                                [ 'ش', 'ﺵ', 'ﺶ', 'ﺸ', 'ﺷ' ],
                                                [ 'ص', 'ﺹ', 'ﺺ', 'ﺼ', 'ﺻ' ],
                                                [ 'ض', 'ﺽ', 'ﺾ', 'ﻀ', 'ﺿ' ],
                                                [ 'ط', 'ﻁ', 'ﻂ', 'ﻄ', 'ﻃ' ],
                                                [ 'ظ', 'ﻅ', 'ﻆ', 'ﻈ', 'ﻇ' ],
                                                [ 'ع', 'ﻉ', 'ﻊ', 'ﻌ', 'ﻋ' ],
                                                [ 'غ', 'ﻍ', 'ﻎ', 'ﻐ', 'ﻏ' ],
                                                [ 'ف', 'ﻑ', 'ﻒ', 'ﻔ', 'ﻓ' ],
                                                [ 'ق', 'ﻕ', 'ﻖ', 'ﻘ', 'ﻗ' ],
                                                [ 'ك', 'ﻙ', 'ﻚ', 'ﻜ', 'ﻛ' ],
                                                [ 'ل', 'ﻝ', 'ﻞ', 'ﻠ', 'ﻟ' ],
                                                [ 'م', 'م', 'ﻢ', 'ﻤ', 'ﻣ' ],
                                                [ 'ن', 'ﻥ', 'ﻦ', 'ﻨ', 'ﻧ' ],
                                                [ 'ه', 'ﻩ', 'ﻪ', 'ﻬ', 'ﻫ' ],
                                                [ 'و', 'ﻭ', 'ﻮ' ],
                                                [ 'ي', 'ﻱ', 'ﻲ', 'ﻴ', 'ﻳ' ],
                                                [ 'ة', 'ﺓ', 'ﺔ' ],
                                                [ 'ى', 'ﻯ', 'ﻰ', 'ئ' ],
                                                [ 'ء' ]
                                                ],
                                    'farsi':  [ [ 'ا', 'ﺍ', 'ﺎ',
                                                  'آ', 'ﺁ', 'ﺂ',
                                                  'أ', 'إ' ],
                                                [ 'ب', 'ﺏ', 'ﺐ', 'ﺒ', 'ﺑ' ],
                                                [ 'پ' ],
                                                [ 'ت', 'ﺕ', 'ﺖ', 'ﺘ', 'ﺗ' ],
                                                [ 'ث', 'ﺙ', 'ﺚ', 'ﺜ', 'ﺛ' ],
                                                [ 'ج', 'ﺝ', 'ﺞ', 'ﺠ', 'ﺟ' ],
                                                [ 'چ' ],
                                                [ 'ح', 'ﺡ', 'ﺢ', 'ﺤ', 'ﺣ' ],
                                                [ 'خ', 'ﺥ', 'ﺦ', 'ﺨ', 'ﺧ' ],
                                                [ 'د', 'ﺩ', 'ﺪ' ],
                                                [ 'ذ', 'ﺫ', 'ﺬ' ],
                                                [ 'ر', 'ﺭ', 'ﺮ' ],
                                                [ 'ز', 'ﺯ', 'ﺰ' ],
                                                [ 'س', 'ﺱ', 'ﺲ', 'ﺴ', 'ﺳ' ],
                                                [ 'ش', 'ﺵ', 'ﺶ', 'ﺸ', 'ﺷ' ],
                                                [ 'ص', 'ﺹ', 'ﺺ', 'ﺼ', 'ﺻ' ],
                                                [ 'ض', 'ﺽ', 'ﺾ', 'ﻀ', 'ﺿ' ],
                                                [ 'ط', 'ﻁ', 'ﻂ', 'ﻄ', 'ﻃ' ],
                                                [ 'ظ', 'ﻅ', 'ﻆ', 'ﻈ', 'ﻇ' ],
                                                [ 'ع', 'ﻉ', 'ﻊ', 'ﻌ', 'ﻋ' ],
                                                [ 'غ', 'ﻍ', 'ﻎ', 'ﻐ', 'ﻏ' ],
                                                [ 'ف', 'ﻑ', 'ﻒ', 'ﻔ', 'ﻓ' ],
                                                [ 'ق', 'ﻕ', 'ﻖ', 'ﻘ', 'ﻗ' ],
                                                [ 'ك', 'ﻙ', 'ﻚ', 'ﻜ', 'ﻛ', 'ک' ],
                                                [ 'گ' ],
                                                [ 'ژ' ],
                                                [ 'ل', 'ﻝ', 'ﻞ', 'ﻠ', 'ﻟ' ],
                                                [ 'م', 'م', 'ﻢ', 'ﻤ', 'ﻣ' ],
                                                [ 'ن', 'ﻥ', 'ﻦ', 'ﻨ', 'ﻧ' ],
                                                [ 'ه', 'ﻩ', 'ﻪ', 'ﻬ', 'ﻫ' ],
                                                [ 'و', 'ﻭ', 'ﻮ' ],
                                                [ 'ي', 'ﻱ', 'ﻲ', 'ﻴ', 'ﻳ', 'ی' ],
                                                [ 'ة', 'ﺓ', 'ﺔ' ],
                                                [ 'ى', 'ﻯ', 'ﻰ', 'ئ' ],
                                                [ 'ء' ]
                                                ]
                                    }

_accent_chars = { 'arabic': [ chr(0x064B),
                              chr(0x064C),
                              chr(0x064D),
                              chr(0x064E),
                              chr(0x064F),
                              chr(0x0650),
                              chr(0x0651),
                              chr(0x0652),
                              chr(0x0653),
                              chr(0x0654),
                              chr(0x0655) ],
                  'farsi': [ chr(0x064B),
                              chr(0x064C),
                              chr(0x064D),
                              chr(0x064E),
                              chr(0x064F),
                              chr(0x0650),
                              chr(0x0651),
                              chr(0x0652),
                              chr(0x0653),
                              chr(0x0654),
                              chr(0x0655) ]
                  }

_tts_info = { 'readspeaker':
              {   'url': 'https://tts.readspeaker.com/a/speak',
                  'languages':
                  { 'english':
                    {  'language_id': 'en_uk',
                       'voices': [ 'Alice-DNN' ]
                       },
                    'french':
                    {  'language_id': 'fr_fr',
                       'voices': [ 'Elise-DNN' ]
                       },
                    'italian':
                    {  'language_id': 'it_it',
                       'voices': [ 'Gina-DNN' ]
                       },
                    'german':
                    {  'language_id': 'de_de',
                       'voices': [ 'Max-DNN' ]
                       },
                    'danish':
                    {  'language_id': 'da_dk',
                       'voices': [ 'Lene' ]
                       },
                    'spanish':
                    {  'language_id': 'es_es',
                       'voices': [ 'Pilar-DNN' ]
                       },
                    'icelandic':
                    {  'language_id': 'is_is',
                       'voices': [ 'Female01' ]
                       },
                    'swedish':
                    {  'language_id': 'sv_se',
                       'voices': [ 'Maja-DNN' ]
                       },
                    'farsi':
                    {  'language_id': 'fa_ir',
                       'voices': [ 'Female01' ]
                       },
                    'mandarin':
                    {  'language_id': 'zh_cn',
                       'voices': [ 'Hui' ]
                       },
                    'dutch':
                    {  'language_id': 'nl_nl',
                       'voices': [ 'Ilse-DNN' ]
                       },
                    'japanese':
                    {  'language_id': 'ja_jp',
                       'voices': [ 'Sayaka-DNN' ]
                       },
                    'polish':
                    {  'language_id': 'pl_pl',
                       'voices': [ 'Aneta-DNN' ]
                       },
                    'slovak':
                    {  'language_id': 'sk_sk',
                       'voices': [ 'Jakub' ]
                       }
                  }
                },
              'google_tts':
              {   'url': 'not_required',
                  'languages':
                  {'afrikaans': {'language_id': 'af', 'voices': ['default']},
                   'albanian': {'language_id': 'sq', 'voices': ['default']},
                   'arabic': {'language_id': 'ar', 'voices': ['default']},
                   'armenian': {'language_id': 'hy', 'voices': ['default']},
                   'bengali': {'language_id': 'bn', 'voices': ['default']},
                   'bosnian': {'language_id': 'bs', 'voices': ['default']},
                   'catalan': {'language_id': 'ca', 'voices': ['default']},
                   'cantonese': {'language_id': 'zh-CN', 'voices': ['default']},
                   'mandarin': {'language_id': 'zh', 'voices': ['default']},
                   'taiwanese': {'language_id': 'zh-TW', 'voices': ['default']},
                   'croatian': {'language_id': 'hr', 'voices': ['default']},
                   'czech': {'language_id': 'cs', 'voices': ['default']},
                   'danish': {'language_id': 'da', 'voices': ['default']},
                   'dutch': {'language_id': 'nl', 'voices': ['default']},
                   'english': {'language_id': 'en', 'voices': ['default']},
                   'esperanto': {'language_id': 'eo', 'voices': ['default']},
                   'estonian': {'language_id': 'et', 'voices': ['default']},
                   'filipino': {'language_id': 'tl', 'voices': ['default']},
                   'finnish': {'language_id': 'fi', 'voices': ['default']},
                   'french': {'language_id': 'fr', 'voices': ['default']},
                   'german': {'language_id': 'de', 'voices': ['default']},
                   'greek': {'language_id': 'el', 'voices': ['default']},
                   'gujarati': {'language_id': 'gu', 'voices': ['default']},
                   'hindi': {'language_id': 'hi', 'voices': ['default']},
                   'hungarian': {'language_id': 'hu', 'voices': ['default']},
                   'icelandic': {'language_id': 'is', 'voices': ['default']},
                   'indonesian': {'language_id': 'id', 'voices': ['default']},
                   'italian': {'language_id': 'it', 'voices': ['default']},
                   'japanese': {'language_id': 'ja', 'voices': ['default']},
                   'javanese': {'language_id': 'jw', 'voices': ['default']},
                   'kannada': {'language_id': 'kn', 'voices': ['default']},
                   'khmer': {'language_id': 'km', 'voices': ['default']},
                   'korean': {'language_id': 'ko', 'voices': ['default']},
                   'latin': {'language_id': 'la', 'voices': ['default']},
                   'latvian': {'language_id': 'lv', 'voices': ['default']},
                   'macedonian': {'language_id': 'mk', 'voices': ['default']},
                   'malayalam': {'language_id': 'ml', 'voices': ['default']},
                   'marathi': {'language_id': 'mr', 'voices': ['default']},
                   'burmese': {'language_id': 'my', 'voices': ['default']},
                   'nepali': {'language_id': 'ne', 'voices': ['default']},
                   'norwegian': {'language_id': 'no', 'voices': ['default']},
                   'polish': {'language_id': 'pl', 'voices': ['default']},
                   'portuguese': {'language_id': 'pt', 'voices': ['default']},
                   'romanian': {'language_id': 'ro', 'voices': ['default']},
                   'russian': {'language_id': 'ru', 'voices': ['default']},
                   'serbian': {'language_id': 'sr', 'voices': ['default']},
                   'sinhala': {'language_id': 'si', 'voices': ['default']},
                   'slovak': {'language_id': 'sk', 'voices': ['default']},
                   'spanish': {'language_id': 'es', 'voices': ['default']},
                   'sundanese': {'language_id': 'su', 'voices': ['default']},
                   'swahili': {'language_id': 'sw', 'voices': ['default']},
                   'swedish': {'language_id': 'sv', 'voices': ['default']},
                   'tamil': {'language_id': 'ta', 'voices': ['default']},
                   'telugu': {'language_id': 'te', 'voices': ['default']},
                   'thai': {'language_id': 'th', 'voices': ['default']},
                   'turkish': {'language_id': 'tr', 'voices': ['default']},
                   'ukrainian': {'language_id': 'uk', 'voices': ['default']},
                   'urdu': {'language_id': 'ur', 'voices': ['default']},
                   'vietnamese': {'language_id': 'vi', 'voices': ['default']},
                   'welsh': {'language_id': 'cy', 'voices': ['default']}
                   }
                  },
              'abair':
              {   'url': 'https://www.abair.ie/api2/synthesise',
                  'languages':
                  { 'irish':
                    {  'language_id': 'ga-IE',
                       'voices': [
                           'ga_UL_anb_nnmnkwii',
                           'ga_MU_nnc_nnmnkwii',
                           'ga_MU_cmg_nnmnkwii'                           
                       ]
                       }
                  }
                }
              }

_supported_tts_engines = list(_tts_info.keys())

_supported_tts_voices = lara_utils.remove_duplicates([ Voice
                                                       for Engine in _tts_info
                                                       for Language in _tts_info[Engine]['languages']
                                                       for Voice in _tts_info[Engine]['languages'][Language]['voices']
                                                       ])
_abstract_html_values = [ 'plain_html_only', 'abstract_html_only', 'plain_and_abstract_html', 'plain_via_abstract_html'  ]

_abstract_html_format_values = [ 'pickle_only', 'json_only', 'pickle_and_json' ]

_jquery_source_values = [ 'google', 'cloudflare' ]

def tts_engines_for_language(Lang):
    return [ { 'engine': Engine, 'voices':_tts_info[Engine]['languages'][Lang]['voices'] }
               for Engine in _tts_info
               if Lang in _tts_info[Engine]['languages'] ]

# Required = 'l'/'d' means for local/distributed
items_in_lara_local_config_data = {
        # ----- required items -----
		'id'                                : { 'required' : True,  'default' : '',    'pattern': _lara_id_pattern },
		'corpus'                            : { 'required' : False, 'default' : '',    'file_or_directory': True },
                'resource_file'                     : { 'required' : 'd',   'default' : '',    'file_or_directory': True },
                'reading_history'                   : { 'required' : 'd',   'default' : '',    },
        # ----- optional items -----
		'add_postags_to_lemma'              : { 'required' : False, 'default' : 'no',  'permitted' : _permitted_bool_values },
                #'abstract_html'                     : { 'required' : False, 'default' : 'plain_and_abstract_html',  'permitted' : _abstract_html_values },
                #'abstract_html'                     : { 'required' : False, 'default' : 'plain_html_only',  'permitted' : _abstract_html_values },
                #'abstract_html'                     : { 'required' : False, 'default' : 'abstract_html_only',  'permitted' : _abstract_html_values },
                'abstract_html'                     : { 'required' : False, 'default' : 'plain_via_abstract_html',  'permitted' : _abstract_html_values },
                'abstract_html_file'                : { 'required' : False, 'default' : '',    'file_or_directory': True },
                #'abstract_html_format'              : { 'required' : False, 'default' : 'pickle_and_json',  'permitted' : _abstract_html_format_values },
                'abstract_html_format'              : { 'required' : False, 'default' : 'json_only',  'permitted' : _abstract_html_format_values },
                'alphabetical_list_link_in_nav_bar' : { 'required' : False, 'default' : 'no',  'permitted' : _permitted_bool_values },
                'alphabetical_list_only_pictures'   : { 'required' : False, 'default' : 'no',  'permitted' : _permitted_bool_values },
                'aligned_phonetic_annotations_file' : { 'required' : False, 'default' : '',    'file_or_directory': True },
                'aligned_segments_file'             : { 'required' : False, 'default' : '',    'file_or_directory': True },
                'aligned_segments_file_evaluate'    : { 'required' : False, 'default' : '',    'file_or_directory': True },
                'alignment_postprocessing'          : { 'required' : False, 'default' : 'yes',  'permitted' : _permitted_bool_values },
                'alignment_postediting_file'        : { 'required' : False, 'default' : '',    'file_or_directory': True },
                'allow_bookmark'                    : { 'required' : False, 'default' : 'no',  'permitted' : _permitted_bool_values },
                'allow_table_of_contents'           : { 'required' : False, 'default' : 'no',  'permitted' : _permitted_bool_values },
                'audio_alignment_beam_width'        : { 'required' : False, 'default' : 40,    'integer' : True },
                'audio_alignment_corpus'            : { 'required' : False, 'default' : '',    'file_or_directory': True },
                'audio_alignment_match_function'    : { 'required' : False, 'default' : 'binary'},
                'audio_cutting_up_parameters'       : { 'required' : False, 'default' : None    }, 
		'audio_mouseover'                   : { 'required' : False, 'default' : 'no',  'permitted' : [ 'yes', 'both', 'no'] },
                'audio_on_click'                    : { 'required' : False, 'default' : 'yes',  'permitted' : _permitted_bool_values },
                'audio_segments'                    : { 'required' : False, 'default' : 'yes',  'permitted' : [ 'yes', 'no'] },
		'audio_tracking'                    : { 'required' : False, 'default' : None    }, # this is a dict by itself!
                'audio_tracking_file'               : { 'required' : False, 'default' : '',    'file_or_directory': True },
		'audio_words_in_colour'             : { 'required' : False, 'default' : 'no',  'permitted' : ['no', 'red'] },
		'author_name'                       : { 'required' : False, 'default' : '',    },
		'author_url'                        : { 'required' : False, 'default' : '',    },
		'author_email'                      : { 'required' : False, 'default' : '',    },
                'chinese_tokeniser'                 : { 'required' : False, 'default' : 'jieba', 'permitted' : _supported_chinese_tokenisers },
		'coloured_words'                    : { 'required' : False, 'default' : 'yes', 'permitted' : _permitted_bool_values },
                'compiled_directory'                : { 'required' : False, 'default' : '$LARA/compiled' },
		'comments_by_default'               : { 'required' : False, 'default' : 'no',  'permitted' : _permitted_bool_values },
		'css_file'                          : { 'required' : False, 'default' : '',    'file_or_directory': True },
		'script_file'                       : { 'required' : False, 'default' : '',    'file_or_directory': True },
                'double_segmented_corpus'           : { 'required' : False, 'default' : '',    'file_or_directory': True },
                'external_sign_video_height'        : { 'required' : False, 'default' : ''      },
                'external_sign_video_width'         : { 'required' : False, 'default' : ''      },
		'extra_page_info'                   : { 'required' : False, 'default' : 'yes'      },
                'flashcard_type'                    : { 'required' : False, 'default' : '', 'permitted' : _known_flashcard_types },
		'font'                              : { 'required' : False, 'default' : 'serif', 'permitted' : ['serif', 'sans-serif', 'monospace'] },
                'font_size'                         : { 'required' : False, 'default' : 'medium',  'permitted' : _permitted_font_size_values  },
                'frequency_list_link_in_nav_bar'    : { 'required' : False, 'default' : 'no',  'permitted' : _permitted_bool_values },
                'frequency_lists_hidden'            : { 'required' : False, 'default' : 'no',  'permitted' : _permitted_bool_values },
		'frequency_lists_in_main_text_page' : { 'required' : False, 'default' : 'no',  'permitted' : _permitted_bool_values },
                'frequency_list_only_images'        : { 'required' : False, 'default' : 'no',  'permitted' : _permitted_bool_values },
                'google_asr_language_code'          : { 'required' : False, 'default' : ''      },
		'hide_images'                       : { 'required' : False, 'default' : 'no',  'permitted' : _permitted_bool_values },
                'html_style'                        : { 'required' : False, 'default' : 'old',  'permitted' : _html_styles },
                'id_on_examples'                    : { 'required' : False, 'default' : 'no',  'permitted' : _permitted_bool_values },
                'id_printform'                      : { 'required' : False, 'default' : ''     },
                'image_dict_spreadsheet'            : { 'required' : False, 'default' : '',    'file_or_directory': True },
                'image_dict_words_in_colour'        : { 'required' : False, 'default' : 'no',  'permitted' : _permitted_bool_values },
		'image_directory'                   : { 'required' : False, 'default' : '',    'file_or_directory': True},
                'image_width_in_concordance_pages'  : { 'required' : False, 'default' : 400,   'integer' : True},
                'jquery_downloaded_from'            : { 'required' : False, 'default' : 'google',  'permitted' : _jquery_source_values},
		'keep_comments'                     : { 'required' : False, 'default' : 'no',  'permitted' : _permitted_bool_values },
                'l1'                                : { 'required' : False, 'default' : ''     },
                'labelled_source_corpus'            : { 'required' : False, 'default' : '',    'file_or_directory': True },
                'labelled_target_corpus'            : { 'required' : False, 'default' : '',    'file_or_directory': True },
		'language'                          : { 'required' : False, 'default' : ''     },
		'language_ui'                       : { 'required' : False, 'default' : _language_ui_fallback },
                'lara_tmp_directory'                : { 'required' : False, 'default' : '$LARA/tmp_resources' },
		'linguistics_article_comments'      : { 'required' : False, 'default' : 'no',  'permitted' : _permitted_bool_values },
                'lemma_dictionary_spreadsheet'      : { 'required' : False, 'default' : '',    'file_or_directory': True },
		'max_examples_per_word_page'        : { 'required' : False, 'default' : 10,   'integer' : True},
                'mt_engine'                         : { 'required' : False, 'default' : 'google',  'permitted' : _supported_mt_engines },
                'mwe_annotations_file'              : { 'required' : False, 'default' : '',    'file_or_directory': True },
                'mwe_file'                          : { 'required' : False, 'default' : '',    'file_or_directory': True },
                'mwe_max_gaps'                      : { 'required' : False, 'default' : 4,   'integer' : True},
                'mwe_words_in_colour'               : { 'required' : False, 'default' : 'no',  'permitted' : _permitted_bool_values },
                'notes_spreadsheet'                 : { 'required' : False, 'default' : '',    'file_or_directory': True },
                'note_words_in_colour'              : { 'required' : False, 'default' : 'no',  'permitted' : _permitted_bool_values },
                'parallel_version_id'               : { 'required' : False,  'default' : '',    'pattern': _lara_id_pattern    },
                'parallel_version_id2'              : { 'required' : False,  'default' : '',    'pattern': _lara_id_pattern    },
                'parallel_version_id3'              : { 'required' : False,  'default' : '',    'pattern': _lara_id_pattern    },
                'parallel_version_label'            : { 'required' : False,  'default' : '' },
                'parallel_version_label2'           : { 'required' : False,  'default' : '' },
                'parallel_version_label3'           : { 'required' : False,  'default' : '' },
                'phonetic_headings_are_comments'    : { 'required' : False, 'default' : 'yes',  'permitted' : _permitted_bool_values },
                'phonetic_lexicon_aligned'          : { 'required' : False, 'default' : '',    'file_or_directory': True },
                'phonetic_lexicon_plain'            : { 'required' : False, 'default' : '',    'file_or_directory': True },
                'phonetic_text'                     : { 'required' : False, 'default' : 'no',  'permitted' : _permitted_bool_values },
                'picturebook'                       : { 'required' : False, 'default' : 'no',  'permitted' : _permitted_bool_values },
                'picturebook_word_locations_file'   : { 'required' : False, 'default' : '',    'file_or_directory': True },
                'picture_words'                     : { 'required' : False, 'default' : 'no',  'permitted' : _permitted_bool_values },
                'pinyin_corpus'                     : { 'required' : False, 'default' : '',    'file_or_directory': True },
                'plain_text'                        : { 'required' : False, 'default' : 'no',  'permitted' : _permitted_bool_values },
                'play_combine_parts'                : { 'required' : False, 'default' : False, 'dict' : True },
                'play_parts'                        : { 'required' : False, 'default' : [],    'list_of_strings' : True },
 		'postags_file'                      : { 'required' : False, 'default' : '',    'file_or_directory': True },
                'postags_colours_file'              : { 'required' : False, 'default' : '',    'file_or_directory': True },
                'preceding_context_window'          : { 'required' : False, 'default' : 10,   'integer' : True},
                'preferred_translator'              : { 'required' : False, 'default' : '',    },
                'preferred_voice'                   : { 'required' : False, 'default' : '',    },
                'relative_compiled_directory'       : { 'required' : False, 'default' : '.',    },
                'retagging_strategy'                : { 'required' : False, 'default' : '',  'permitted' : _permitted_retagging_strategies },
                'reversed_corpus_file'              : { 'required' : False, 'default' : '',    'file_or_directory': True },
                'reversed_segment_translation_file' : { 'required' : False, 'default' : '',    'file_or_directory': True },
                'segment_audio_exact_context_match' : { 'required' : False, 'default' : 'no',  'permitted' : _permitted_bool_values },
		'segment_audio_directory'           : { 'required' : False, 'default' : '',    'file_or_directory': True },
                'segment_audio_keep_duplicates'     : { 'required' : False, 'default' : 'no',  'permitted' : _permitted_bool_values },
                'segment_audio_word_breakpoint_csv' : { 'required' : False, 'default' : '',    'file_or_directory': True },
                'segment_audio_word_offset'         : { 'required' : False, 'default' : 0.0,   'number': True },
                'segment_audio_word_window_left'    : { 'required' : False, 'default' : 0,     'integer_or_prosodic_phrase': True },
                'segment_audio_word_window_right'   : { 'required' : False, 'default' : 0,     'integer_or_prosodic_phrase': True },
                'segment_translation_as_popup'      : { 'required' : False, 'default' : 'yes', 'permitted' : _permitted_bool_values + ['not_popup_translation_only'] },
                'segment_translation_character'     : { 'required' : False, 'default' : '✎',    'character' : True },
                'segment_translation_mouseover'     : { 'required' : False, 'default' : 'yes', 'permitted' : _permitted_bool_values },
		'segment_translation_spreadsheet'   : { 'required' : False, 'default' : '',    'file_or_directory': True },
                'source_file'                       : { 'required' : False, 'default' : '',    'file_or_directory': True },
                'tagged_corpus'                     : { 'required' : False, 'default' : '',    'file_or_directory': True },
                'tag_using_google_cloud'            : { 'required' : False, 'default' : 'no',  'permitted' : _permitted_bool_values },
                'target_file'                       : { 'required' : False, 'default' : '',    'file_or_directory': True },
		'text_direction'                    : { 'required' : False, 'default' : 'ltr', 'permitted': ['rtl', 'ltr'] },
		'title'                             : { 'required' : False, 'default' : ''     },
                'tmx_files'                         : { 'required' : False, 'default' : False, 'dict' : True },
                'tmx_source_lang'                   : { 'required' : False, 'default' : ''     },
                'tmx_target_lang'                   : { 'required' : False, 'default' : ''     },
		'toggle_translation_button'         : { 'required' : False, 'default' : 'no',  'permitted' : _permitted_bool_values },
                'translated_words_in_colour'        : { 'required' : False, 'default' : 'no',  'permitted' : _permitted_bool_values },
                'translated_words_not_in_colour'    : { 'required' : False, 'default' : 'no',  'permitted' : _permitted_bool_values },
                'translation_alignment_corpus'      : { 'required' : False, 'default' : '',    'file_or_directory': True },
                'translation_includes_transcription': { 'required' : False, 'default' : 'no',  'permitted' : _permitted_bool_values },
		'translation_mouseover'             : { 'required' : False, 'default' : 'no',  'permitted' : _permitted_bool_values },
		'translation_spreadsheet'           : { 'required' : False, 'default' : '',    'file_or_directory': True },
                'translation_spreadsheet_surface'   : { 'required' : False, 'default' : '',    'file_or_directory': True },
                'translation_spreadsheet_tokens'    : { 'required' : False, 'default' : '',    'file_or_directory': True },
                'trimming_db_threshold'             : { 'required' : False, 'default' : 25,   'number': True },
                'trimming_start_offset'             : { 'required' : False, 'default' : 0.0,   'number': True },
                'tts_engine'                        : { 'required' : False, 'default' : 'None','permitted': [ 'None', None ] + _supported_tts_engines },
                'tts_voice'                         : { 'required' : False, 'default' : '' },
                'tts_url'                           : { 'required' : False, 'default' : '' },
                'tts_word_substitution_spreadsheet' : { 'required' : False, 'default' : '',    'file_or_directory': True },
                'ui_texts'                          : { 'required' : False,  'default' : {} },
                'unsegmented_corpus'                : { 'required' : False, 'default' : '',    'file_or_directory': True },
		'untagged_corpus'                   : { 'required' : False, 'default' : '',    'file_or_directory': True },
                'untagged_raw_corpus'               : { 'required' : False, 'default' : '',    'file_or_directory': True },
                'video_annotations'                 : { 'required' : False, 'default' : '',    'permitted' : _permitted_bool_values },
                'video_annotations_from_translation': { 'required' : False, 'default' : '',    'permitted' : _permitted_bool_values },
                'web_multimedia_url'                : { 'required' : False, 'default' : '' },
                'word_alignment_file'               : { 'required' : False, 'default' : '',    'file_or_directory': True },
		'word_audio_directory'              : { 'required' : False, 'default' : '',    'file_or_directory': True },
                #'word_audio_voice'                 : { 'required' : False, 'default' : '' },
                'word_translation_file_in_json'     : { 'required' : False, 'default' : 'no',  'permitted' : _permitted_bool_values },
                'word_translations_on'              : { 'required' : False, 'default' : 'lemma', 'permitted': _permitted_word_translation_types },
                'working_tmp_directory'             : { 'required' : False, 'default' : '$LARA/tmp' },
        # ----- for internal use -----
                'corpus_id'                         : { 'required' : False, 'default' : '', 'internal': True     },
                'component_params'                  : { 'required' : False, 'default' : {}, 'internal': True     },
                'postag_colours'                    : { 'required' : False, 'default' : {}, 'internal': True     },
		'local_files'                       : { 'required' : False, 'default' : 'no',  'permitted' : _permitted_bool_values, 'internal': True },
                'for_reading_portal'                : { 'required' : False, 'default' : 'no',  'permitted' : _permitted_bool_values, 'internal': True },
                'for_treetagger'                    : { 'required' : False, 'default' : 'no',  'permitted' : _permitted_bool_values, 'internal': True },
                'page_name'                         : { 'required' : False, 'default' : '', 'internal': True     },
                'make_word_pos_file_in_treetagging' : { 'required' : False, 'default' : 'no',  'permitted' : _permitted_bool_values, 'internal': True },
                'word_token_translations'           : { 'required' : False, 'default' : [], 'internal': True },
                'word_token_index'                  : { 'required' : False, 'default' : '', 'internal': True },
                'word_type_translations'            : { 'required' : False, 'default' : {}, 'internal': True },
                'segment_audio_for_word_audio'      : { 'required' : False, 'default' : False, 'internal': True },
                'hanzi_to_pinyin_dict'              : { 'required' : False, 'default' : {}, 'internal': True },
                'audio_segment_warnings'            : { 'required' : False, 'default' : 'yes', 'internal': True },
                'word_audio_breakpoints'            : { 'required' : False, 'default' : False, 'internal': True},
                'word_audio_prosodic_boundaries'    : { 'required' : False, 'default' : [], 'internal': True},
                'ignore_existing_word_token_data'   : { 'required' : False, 'default' : '', 'internal': True },
                'split_file'                        : { 'required' : False, 'default' : '',    'file_or_directory': True, 'internal': True },
                'count_file'                        : { 'required' : False, 'default' : '',    'file_or_directory': True, 'internal': True },
                'surface_count_file'                : { 'required' : False, 'default' : '',    'file_or_directory': True, 'internal': True },
                'compile_cache_file'                : { 'required' : False, 'default' : '',    'file_or_directory': True, 'internal': True },
                'word_pages_directory'              : { 'required' : False, 'default' : '',    'file_or_directory': True, 'internal': True },
                'metadata_directory'                : { 'required' : False, 'default' : '',    'file_or_directory': True, 'internal': True },
		'css_file_for_page'                 : { 'required' : False, 'default' : '',    'file_or_directory': True, 'internal': True },
                'script_file_for_page'              : { 'required' : False, 'default' : '',    'file_or_directory': True, 'internal': True },
                'recompile'                         : { 'required' : False, 'default' : '', 'internal': True     },
                'write_word_pages_to_file'          : { 'required' : False, 'default' : 'yes', 'permitted' : _permitted_bool_values, 'internal': True },
                'switch_off_caching'                : { 'required' : False, 'default' : 'no', 'permitted' : _permitted_bool_values, 'internal': True },
                'selector_tool_id'                  : { 'required' : False, 'default' : '', 'integer' : True, 'internal': True },
        }

right_to_left_languages = ['arabic',
                           'farsi',
                           'hebrew',
                           'uyghur']

def default_value_for_param(ParamName):
    return items_in_lara_local_config_data[ParamName]['default']

def is_internal_param(ParamName):
    Entry = items_in_lara_local_config_data[ParamName]
    return 'internal' in Entry and Entry['internal'] == True

# --------------------------------------------------------

# Wrapper for dict() so that instead of Params["key"] you can now write Params.key
class LARAConfigDict(dict):
    def __init__(self, initialDict):
        super().__init__()
        setattr(self, 'itemlist', initialDict.keys())
        for k,v in initialDict.items():
            self[k] = v 
            setattr(self, k, v)
    def __setitem__(self, k, v):
        setattr(self, k, v)
    def __getitem__(self, k): 
        return getattr(self, k)
    def __iter__(self):
        return iter(self.itemlist)
    def __len__(self):
        return len(self.itemlist)
    def keys(self):
        return self.itemlist
    def values(self):
        return [ self[k] for k in self ]
    def keys_and_values(self):
        return { k: self[k] for k in self }
    def __repr__(self):
        return str({ k: self[k] for k in self })
    def __str__(self):
        return str({ k: self[k] for k in self })
    def __contains__(self, k):
        return k in self.itemlist

def default_params():
    Dict = {}
    fill_in_missing_keys_and_values(Dict)
    return LARAConfigDict(Dict)

# Read the config data, check that it is consistent, and check/create env vars and directories

def read_lara_local_config_file_dont_check_directories(ConfigFile):
    return read_lara_config_file(ConfigFile, 'l', 'dont_check')

def read_lara_local_config_file(ConfigFile):
    return read_lara_config_file(ConfigFile, 'l', 'check')

def read_lara_distributed_config_file(ConfigFile):
    return read_lara_config_file(ConfigFile, 'd', 'check')

def read_lara_config_file(ConfigFile, LorD, CheckP):
    if not lara_utils.file_exists(ConfigFile):
        lara_utils.print_and_flush(f'*** Error: unable to find config file {ConfigFile}')
        return False
    if not lara_utils.extension_for_file(ConfigFile) == 'json':
        lara_utils.print_and_flush(f'*** Error: extension of config file {ConfigFile} has to be ".json"')
        return False
    Data = lara_utils.read_json_file(ConfigFile)
    if not Data:
        lara_utils.print_and_flush(f'*** Error: cannot internalise config file {ConfigFile}')
    OrigData = copy.copy(Data)
    if check_minimal_requirements_for_lara_local_config_data(Data, LorD):
        fill_in_missing_keys_and_values(Data)
        Params = LARAConfigDict(Data)
        if CheckP == 'dont_check' or check_environment_variables_and_working_directories(Params):
            return Params
        else:
            lara_utils.print_and_flush(f'*** Error: cannot internalise config file {ConfigFile}')
            lara_utils.print_and_flush(f'*** Error: contents {OrigData}')
            return False
    else:
        return False

def check_environment_variables_and_working_directories(Params):
    if not lara_utils.check_environment_variable_directory('LARA'):
        lara_utils.print_and_flush(f'*** Error: environment variable LARA not set')
        return False
    if not lara_utils.create_directory_if_it_doesnt_exist(Params.lara_tmp_directory):
        lara_utils.print_and_flush(f'*** Error: cannot create lara_tmp_directory {Params.lara_tmp_directory}')
        return False
    if not lara_utils.create_directory_if_it_doesnt_exist(Params.working_tmp_directory):
        lara_utils.print_and_flush(f'*** Error: cannot create working_tmp_directory {Params.working_tmp_directory}')
        return False
    if not lara_utils.create_directory_if_it_doesnt_exist(Params.compiled_directory):
        lara_utils.print_and_flush(f'*** Error: cannot create compiled_directory {Params.compiled_directory}')
        return False
    lara_utils.print_and_flush('--- Environment variables and working directories look okay')
    return True

def fill_in_missing_keys_and_values(Data):
    for key in items_in_lara_local_config_data.keys():
        if key in Data: continue
        Data[key] = items_in_lara_local_config_data[key]['default']

def check_minimal_requirements_for_lara_local_config_data(Data, LocalOrDistributed):
    return check_required_items(Data, LocalOrDistributed) and check_keys(Data) and check_values(Data)

def check_required_items(Data, LocalOrDistributed):
    MissingItems = [ Item for Item in items_in_lara_local_config_data if
                     items_in_lara_local_config_data[Item]['required'] in ( True, LocalOrDistributed ) and not Item in Data ]
    if len(MissingItems) == 0:
        return True
    else:
        lara_utils.print_and_flush(f'*** Error: config file does not define following keys: "{" ".join(MissingItems)}"')
        return False   

# Use this in lara_import_export to check whether there are any bad values in the data
def bad_values_in_config_data(Data):
    BadValuesFound = False
    UnknownKeys = [ Item for Item in Data if unknown_key(Item) ]
    if len(UnknownKeys) > 0:
        lara_utils.print_and_flush(f'*** Error: config file contains unknown or deprecated keys: "{" ".join(UnknownKeys)}"')
        BadValuesFound = True
    InvalidKeyValues = [ [Item, Data[Item] ] for Item in Data if invalid_value_for_key(Item, Data[Item]) ]
    if len(InvalidKeyValues) > 0:
        BadValuesFound = True
    return BadValuesFound

# Version for top-level call
def check_config_file_and_print(ConfigFile, LocalOrDistributed0, ReplyFile):
    try:
        Data = check_config_file(ConfigFile, LocalOrDistributed0)
    except:
        Data = { 'internal_error': 'yes' }
    lara_utils.write_json_to_file(Data, ReplyFile)

def check_config_file(ConfigFile, LocalOrDistributed0):
    if LocalOrDistributed0 == 'local':
        LocalOrDistributed = 'l'
    elif LocalOrDistributed0 == 'distributed':
        LocalOrDistributed = 'd'
    else:
        lara_utils.print_and_flush('*** Error: bad second argument {LocalOrDistributed0} to check_config_file. Needs to be "local" or "distributed"')
        return False                 
    if not lara_utils.file_exists(ConfigFile):
        return { 'status': 'bad', 'config_file_missing': 'yes' }
    Data = lara_utils.read_json_file(ConfigFile)
    if not Data:
        return { 'status': 'bad', 'config_file_unable_to_read': 'yes' }
    Feedback = { 'status': 'good' }
    UnknownKeys = [ Item for Item in Data if unknown_key(Item) ]
    if len(UnknownKeys) > 0:
        Feedback['unknown_keys'] = UnknownKeys
        Feedback['status'] = 'bad'
    InvalidKeyValues = [ [Item, Data[Item] ] for Item in Data if invalid_value_for_key(Item, Data[Item]) ]
    if len(InvalidKeyValues) > 0:
        Feedback['invalid_key_values'] = InvalidKeyValues
        Feedback['status'] = 'bad'
    MissingItems = [ Item for Item in items_in_lara_local_config_data if
                     items_in_lara_local_config_data[Item]['required'] in ( True, LocalOrDistributed ) and not Item in Data ]
    if len(MissingItems) > 0:
        Feedback['missing_items'] = MissingItems
        Feedback['status'] = 'bad'
    return Feedback

def check_keys(Data):
    UnknownKeys = [ Item for Item in Data if unknown_key(Item) ]
    if len(UnknownKeys) == 0:
        return True
    else:
        lara_utils.print_and_flush(f'*** Warning: config file contains unknown or deprecated keys: "{" ".join(UnknownKeys)}"')
        return True

def unknown_key(Key):
    return not Key in items_in_lara_local_config_data

def check_values(Data):
    InvalidKeyValues = [ [Item, Data[Item] ] for Item in Data if invalid_value_for_key(Item, Data[Item]) ]
    return len(InvalidKeyValues) == 0

def invalid_value_for_key(Key, Value):
    if not Key in items_in_lara_local_config_data: return False # allow unknown keys at this point!
    ConfigItem = items_in_lara_local_config_data[Key] 
    # check permitted values
    if 'permitted' in ConfigItem and not Value in ConfigItem['permitted']:
        lara_utils.print_and_flush(f'*** Error: invalid value "{Value}" for config file item "{Key}". Permitted values are {items_in_lara_local_config_data[Key]["permitted"]}')
        return True
    # match against pattern
    if 'pattern' in ConfigItem and not re.search(f'^({ConfigItem["pattern"]})$', str(Value)):
        Explanation = f' ({_explanations[ConfigItem["pattern"]]})' if ConfigItem["pattern"] in _explanations else ''
        lara_utils.print_and_flush(f'*** Error: invalid value "{Value}" for config file item "{Key}". Value must match this pattern: {ConfigItem["pattern"]}{Explanation}')
        return True
    # Check integer if required
    if 'integer' in ConfigItem and ConfigItem['integer'] and not isinstance(Value, int):
        lara_utils.print_and_flush(f'*** Error: invalid value "{Value}" for config file item "{Key}". Value must be an integer')
        return True
    # Check integer if required
    if 'integer_or_prosodic_phrase' in ConfigItem and ConfigItem['integer_or_prosodic_phrase'] and not isinstance(Value, int) and \
       Value != 'prosodic_phrase':
        lara_utils.print_and_flush(f'*** Error: invalid value "{Value}" for config file item "{Key}". Value must be an integer or "prosodic_phrase"')
        return True
    # Check number if required
    if 'number' in ConfigItem and ConfigItem['number'] and not isinstance(Value, ( int, float )):
        lara_utils.print_and_flush(f'*** Error: invalid value "{Value}" for config file item "{Key}". Value must be a number')
        return True
    # Check character if required
    if 'character' in ConfigItem and ConfigItem['character'] and ( not isinstance(Value, str) or not len(Value) == 1 ):
        lara_utils.print_and_flush(f'*** Error: invalid value "{Value}" for config file item "{Key}". Value must be a character')
        return True
    # Check list of strings if required
    if 'list_of_strings' in ConfigItem and ConfigItem['list_of_strings'] and not lara_utils.is_list_of_strings(Value):
        lara_utils.print_and_flush(f'*** Error: invalid value "{Value}" for config file item "{Key}". Value must be a list of strings')
        return True
    # Check dict if required
    if 'dict' in ConfigItem and ConfigItem['dict'] and not isinstance(Value, dict):
        lara_utils.print_and_flush(f'*** Error: invalid value "{Value}" for config file item "{Key}". Value must be a dict')
        return True
    # directory or file entries must not be empty            
    if not Value and 'file_or_directory' in ConfigItem and ConfigItem['file_or_directory']:
        lara_utils.print_and_flush(f'*** Error: unknown value "{Value}" for config file item "{Key}". Files or directories must not be empty')
        return True
    return False

def check_lara_id(Id):
    Pattern = _lara_id_pattern
    if re.search(f'^({Pattern})$', str(Id)):
        return True
    elif Pattern in _explanations:
        return f'Incorrect LARA ID "{Id}". {_explanations[Pattern]}'
    else:
        return f'Incorrect LARA ID "{Id}". A LARA ID must match this pattern: {Pattern}'

# Version for top-level call
def check_lara_id_and_print(Id, ReplyFile):
    try:
        Data = check_lara_id(Id)
    except:
        Data = 'internal_error'
    lara_utils.write_json_to_file(Data, ReplyFile)

# Need to omit default values in general otherwise checking doesn't work
def save_params_as_config_file(Params, ConfigFile):
    Dict = dict(Params)
    Dict1 = {}
    for Key in Dict:
        if Dict[Key] != default_value_for_config_file_key(Key):
            Dict1[Key] = Dict[Key]
    lara_utils.write_json_to_file_plain_utf8(Dict1, ConfigFile)

def default_value_for_config_file_key(Key):
    Data = items_in_lara_local_config_data[Key]
    return Data['default'] if 'default' in Data else None
                  
# --------------------------------------------------------

def right_to_left_language(L2):
    global right_to_left_languages
    return L2 in right_to_left_languages

def get_ui_text( id, Params ):
    if id in Params.ui_texts:
        return Params.ui_texts[id]
    Language = Params.language_ui
    if Language not in ui_texts or id not in ui_texts[Language]:
        Language = _language_ui_fallback
    if id not in ui_texts[Language]:
        lara_utils.print_and_flush( f'*** warning: no translation found for {id} in UI texts' );
        return get_ui_text( 'unknown', Params )
    return ui_texts[Language][id]
