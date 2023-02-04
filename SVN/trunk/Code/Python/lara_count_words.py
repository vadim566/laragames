
import lara_split_and_clean
import lara_utils

def check_text_file(File):
    ( Str, Pairs, Words ) = file_to_string_pairs_and_words(File)
    if Str == False: return
    lara_utils.print_and_flush(f'---  Chars: {len(Str)}')
    lara_utils.print_and_flush(f'--  Tokens: {len(Pairs)}')
    lara_utils.print_and_flush(f'--   Words: {len(Words)}')

def compare_text_file_words(File1, File2):
    ( Str1, Pairs1, Words1 ) = file_to_string_pairs_and_words(File1)
    ( Str2, Pairs2, Words2 ) = file_to_string_pairs_and_words(File2)
    if Str1 == False or Str2 == False:
        return
    if Words1 == Words2:
        lara_utils.print_and_flush(f'--- Words in files are the same')
        return
    else:
        report_difference_between_word_lists(Words1, Words2, File1, File2)

def file_to_string_pairs_and_words(File):
    Str = lara_utils.read_lara_text_file(File)
    if Str == False:
        return ( False, False, False )
    Str1 = make_string_canonical_for_counting_words(Str)
    Pairs = lara_split_and_clean.string_to_annotated_words(Str1)[0]
    Words = [ Pair[0] for Pair in Pairs if Pair[1] != '' ]
    return ( Str1, Pairs, Words )

def make_string_canonical_for_counting_words(Str):
    Substitutions = { '//': '',
                      '||': '',
                      '’': "'" }
    Regex = lara_utils.make_multiple_replacement_regex(Substitutions)
    return lara_utils.apply_multiple_replacement_regex(Substitutions, Regex, Str)

def report_difference_between_word_lists(Words1, Words2, File1, File2):
    ( NWords1, NWords2 ) = ( len(Words1), len(Words2) )
    for I in range(0, NWords1):
        if I > NWords2:
            lara_utils.print_and_flush(f'--- Extra words at end of {File1}: {possibly_truncated_list(Words1[NWords2:])}')
            return
        elif Words1[I] != Words2[I]:
            Context = Words1[max(0, I-10):I]
            lara_utils.print_and_flush(f'--- Words differ at position {I} after {Context}: {Words1[I]}/{Words2[I]}')
            return
    lara_utils.print_and_flush(f'--- Extra words at end of {File2}: {possibly_truncated_list(Words2[NWords1:])}')
    return

def possibly_truncated_list(List):
    return List[:10] + [ '...' ] if len(List) > 10 else List

    
