
import lara_parse_utils
import lara_utils

_replace_chars_enabled = True
#_replace_chars_enabled = False

##_replacements = { '#': '☩',
##                  '<': '☾'
##                  }
_replacements = { '#': '\\#',
                  '<': '\\<',
                  '@': '\\@'
                  }

_inverse_replacements = { _replacements[Char]: Char for Char in _replacements }

_replacement_regex = lara_utils.make_multiple_replacement_regex(_replacements)

_restore_regex = lara_utils.make_multiple_replacement_regex(_inverse_replacements)

def is_escaped_reserved_char_sequence(Str):
    return Str in _inverse_replacements

def replace_reserved_chars(Str):
    if not isinstance(Str, str):
        lara_utils.print_and_flush(f'*** Error: bad call: replace_reserved_chars({Str})')
        return False
    if not _replace_chars_enabled:
        return Str
    return lara_utils.apply_multiple_replacement_regex(_replacements, _replacement_regex, Str)

def restore_reserved_chars(Str):
    if not isinstance(Str, str):
        lara_utils.print_and_flush(f'*** Error: bad call: restore_reserved_chars({Str})')
        return False
    if not _replace_chars_enabled:
        return Str
    return lara_utils.apply_multiple_replacement_regex(_inverse_replacements, _restore_regex, Str)
##def restore_reserved_chars(Str):
##    return Str


# Usually we won't have HTML in the string - but if we do, try to correct replacements of '<'
def try_to_correct_replaced_html(Str):
    try:
        return try_to_correct_replaced_html1(Str)
    except Exception as e:
        lara_utils.print_and_flush(f'*** Warning: error when trying to correct replaced HTML in {Str[:100]}')
        lara_utils.print_and_flush(str(e))
        return Str

def try_to_correct_replaced_html1(Str):
    if Str.find('\\<') < 0:
        return Str
    ( I, N, OutStr ) = ( 0, len(Str), '' )
    while True:
        if I >= N:
            return OutStr
        NextLT = Str.find('\\<', I)
        if NextLT < 0:
            OutStr += Str[I:]
            return OutStr
        OutStr += Str[I:NextLT]
        NextGT = Str.find('>', NextLT)
        # There's a nearby >, so probably it's an HTML tag
        if NextGT - NextLT < 100:
            OutStr += Str[( NextLT + len('\\') ) : ( NextGT + len('>') )]
            I = NextGT + len('>')
        else:
            OutStr += Str[NextLT : ( NextLT + len('\\<') )]
            I = NextLT + len('\\<')
    return OutStr

_hyphen_char = '-'
_minus_char = chr(0x2212)
_en_dash_char = chr(0x2013)

def try_to_replace_nonstandard_hyphen(Str):
    HyphenCharUsed = best_guess_at_hyphen_char(Str)
    if HyphenCharUsed != _hyphen_char:
        lara_utils.print_and_flush(f'--- Replacing with normal hyphen')
        return Str.replace(HyphenCharUsed, _hyphen_char)
    else:
        return Str

def best_guess_at_hyphen_char(Str):
    Dict = { _hyphen_char: 0, _minus_char: 0, _en_dash_char: 0 }
    for Index in range(1, len(Str) - 2):
        if is_hyphen(Str[Index]) and \
           not is_hyphen_or_space_or_punctuation(Str[ Index - 1 ]) and \
           not is_hyphen_or_space_or_punctuation(Str[ Index + 1 ]):
            Dict[Str[Index]] += 1
    if Dict[_minus_char] > Dict[_hyphen_char] and Dict[_minus_char] >= 10:
        lara_utils.print_and_flush(f'--- Minus character (0x2212) apparently used as hyphen')
        return _minus_char
    elif Dict[_en_dash_char] > Dict[_hyphen_char] and Dict[_en_dash_char] >= 10:
        lara_utils.print_and_flush(f'--- En-dash character (0x2013) apparently used as hyphen')
        return _en_dash_char
    else:
        return _hyphen_char

def is_hyphen_or_space_or_punctuation(Char):
    return is_hyphen(Char) or Char.isspace() or lara_parse_utils.is_punctuation_char(Char)
            
def is_hyphen(Char):
    return Char in ( _hyphen_char, _minus_char, _en_dash_char )
                                                 
    
