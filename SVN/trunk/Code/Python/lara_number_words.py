import lara_utils

def spell_out_number_word(NumberWord, LaraLanguage):
    import num2words
    Number = lara_utils.safe_string_to_int(NumberWord)
    if Number == False:
        return False
    Language = lara_language_to_two_letter_language_code(LaraLanguage)
    if Language == False:
        return False
    if number_looks_like_year(Number):
        try:
            return num2words.num2words(Number, to = 'year', lang = Language)
        except:
            return False
    else:
        try:
            return num2words.num2words(Number, lang = Language)
        except:
            return False

def number_looks_like_year(Number):
    return 1200 <= Number and Number <= 2100

_lara_language_codes = { 'afrikaans': 'af',
                         'albanian': 'sq',
                         'arabic': 'ar',
                         'armenian': 'hy',
                         'bengali': 'bn',
                         'bosnian': 'bs',
                         'catalan': 'ca',
                         'cantonese': 'zh',
                         'mandarin': 'zh',
                         'taiwanese': 'zh',
                         'croatian': 'hr',
                         'czech': 'cs',
                         'danish': 'da',
                         'dutch': 'nl',
                         'english': 'en',
                         'esperanto': 'eo',
                         'estonian': 'et',
                         'filipino': 'tl',
                         'finnish': 'fi',
                         'french': 'fr',
                         'german': 'de',
                         'greek': 'el',
                         'gujarati': 'gu',
                         'hindi': 'hi',
                         'hungarian': 'hu',
                         'icelandic': 'is',
                         'indonesian': 'id',
                         'italian': 'it',
                         'japanese': 'ja',
                         'javanese': 'jw',
                         'kannada': 'kn',
                         'khmer': 'km',
                         'korean': 'ko',
                         'latin': 'la',
                         'latvian': 'lv',
                         'macedonian': 'mk',
                         'malayalam': 'ml',
                         'marathi': 'mr',
                         'burmese': 'my',
                         'nepali': 'ne',
                         'norwegian': 'no',
                         'polish': 'pl',
                         'portuguese': 'pt',
                         'romanian': 'ro',
                         'russian': 'ru',
                         'serbian': 'sr',
                         'sinhala': 'si',
                         'slovak': 'sk',
                         'spanish': 'es',
                         'sundanese': 'su',
                         'swahili': 'sw',
                         'swedish': 'sv',
                         'tamil': 'ta',
                         'telugu': 'te',
                         'thai': 'th',
                         'turkish': 'tr',
                         'ukrainian': 'uk',
                         'urdu': 'ur',
                         'vietnamese': 'vi',
                         'welsh': 'cy'
                         }

def lara_language_to_two_letter_language_code(Lang):
    return _lara_language_codes[Lang] if Lang in _lara_language_codes else False
