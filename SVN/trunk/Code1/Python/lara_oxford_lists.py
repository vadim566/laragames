
import lara_html
import lara_config
import lara_utils

def test(Id):
    if Id == 'read_3000':
        return read_oxford_list('$LARA/Content/oxford_3000/corpus/oxford_3000.docx')
    if Id == 'parse_3000':
        read_and_parse_oxford_list('$LARA/Content/oxford_3000/corpus/oxford_3000.docx',
                                   '$LARA/Content/oxford_3000/corpus/oxford_3000.json')
    if Id == 'parse_5000':
        read_and_parse_oxford_list('$LARA/Content/oxford_3000/corpus/oxford_5000.docx',
                                   '$LARA/Content/oxford_3000/corpus/oxford_5000.json')
    if Id == 'Alice in Wonderland':
        check_vocab('Alice in Wonderland (Oxford 5000)',
                    '$LARA/tmp_resources/alice_in_wonderland_count.json',
                    '$LARA/Content/oxford_3000/corpus/oxford_5000.json',
                    '$LARA/Content/oxford_3000/corpus/alice_in_wonderland.html')
    if Id == 'Animal Farm':
        check_vocab('Animal Farm (Oxford 5000)',
                    '$LARA/tmp_resources/animal_farm_count.json',
                    '$LARA/Content/oxford_3000/corpus/oxford_5000.json',
                    '$LARA/Content/oxford_3000/corpus/animal_farm.html')
    if Id == 'The Rime of the Ancient Mariner':
        check_vocab('The Rime of the Ancient Mariner (Oxford 5000)',
                    '$LARA/tmp_resources/the_rime_of_the_ancient_mariner_count.json',
                    '$LARA/Content/oxford_3000/corpus/oxford_5000.json',
                    '$LARA/Content/oxford_3000/corpus/the_rime_of_the_ancient_mariner.html')
    if Id == 'Animal Farm and Alice':
        check_vocab('Animal Farm and Alice in Wonderland (Oxford 5000)',
                    [ '$LARA/tmp_resources/animal_farm_count.json',
                      '$LARA/tmp_resources/alice_in_wonderland_count.json' ],
                    '$LARA/Content/oxford_3000/corpus/oxford_5000.json',
                    '$LARA/Content/oxford_3000/corpus/animal_farm_and_alice_in_wonderland.html')

def check_vocab(Caption, CountFiles, OxfordFile, HTMLFile):
    CountDict = count_files2dict(CountFiles)
    OxfordList = lara_utils.read_json_file(OxfordFile)
    Lines = annotate_oxford_list_from_count_dict(OxfordList, CountDict)
    TotalLines = make_total_lines(Lines)
    NonCERFTotalLine = make_non_cerf_total_line(OxfordFile, CountFiles)
    NonCERFLines = make_non_cerf_lines(OxfordFile, CountFiles)
    Header = ['Word', 'Level', 'Occurrences']
    Params = lara_config.default_params()
    EmptyLines = [ ['', '', ''] ]
    AllLines = [ Header ] + EmptyLines + TotalLines + [ NonCERFTotalLine ] + EmptyLines + Lines + NonCERFLines
    lara_html.write_out_html_table(Caption, AllLines, HTMLFile, Params)

def count_files2dict(CountFiles):
    return { Word: Count for ( Word, Count ) in read_count_files(CountFiles) }

def read_count_files(CountFiles):
    CountFiles1 = CountFiles if isinstance(CountFiles, list) else [ CountFiles ]
    return merge_count_contents( [ lara_utils.read_json_file(CountFile) for CountFile in CountFiles1 ] )

def merge_count_contents(ContentsList):
    Dict = {}
    for Content in ContentsList:
        for ( Word, Count ) in Content:
            Dict[Word] = Count if not Word in Dict else Dict[Word] + Count
    return sorted( [ ( Word, Dict[Word] ) for Word in Dict ], key=lambda x: x[1], reverse=True )

def annotate_oxford_list_from_count_dict(OxfordList, CountDict):
    return [ ( Word, Level, occurrences(Word, CountDict) ) for ( Word, Level ) in OxfordList ]

def make_non_cerf_total_line(OxfordFile, CountFiles):
    OxfordDict = { Item[0]: True for Item in lara_utils.read_json_file(OxfordFile) }
    TextWords = [ Item[0] for Item in read_count_files(CountFiles)
                  if not text_word_to_ignore(Item[0]) ]
    Count = len([ X for X in TextWords if not X in OxfordDict ])
    return [ 'Total', 'Other', Count ]

def make_non_cerf_lines(OxfordFile, CountFiles):
    OxfordDict = { Item[0]: True for Item in lara_utils.read_json_file(OxfordFile) }
    TextContent = read_count_files(CountFiles)
    return [ [ Word, 'Other', Count ] for ( Word, Count ) in TextContent
             if not Word in OxfordDict and not text_word_to_ignore(Word) ]

def text_word_to_ignore(Word):
    return Word in [ 'i', 's', 'mr', 'mrs' ] or space_apostrophe_or_digit_in_word(Word) or roman_number(Word)

def space_apostrophe_or_digit_in_word(Word):
    for Char in Word:
        if Char in " '’0123456789":
            return True
    return False

def roman_number(Word):
    return Word.lower() in [ 'i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x',
                             'xi', 'xii', 'xiii', 'xiv', 'xv', 'xvi', 'xvii', 'xviii', 'xix', 'xx',
                             'xxi', 'xxii', 'xxiii', 'xxiv', 'xxv', 'xxvi', 'xxvii', 'xxviii', 'xxix', 'xxx']

def make_total_lines(Lines):
    AllLevels = lara_utils.remove_duplicates(Level for ( Word, Level, Occurrences ) in Lines)
    return [ ( 'Total', Level, total_for_level(Level, Lines) ) for Level in AllLevels ]

def total_for_level(Level, Lines):
    TotalForLevel = len( [ Line for Line in Lines if Line[1] == Level ] )
    FilledForLevel = len( [ Line for Line in Lines if Line[1] == Level and Line[2] != '' ] )
    return f'{FilledForLevel}/{TotalForLevel}'
             
def occurrences(Word, CountDict):
    return CountDict[Word.lower()] if Word.lower() in CountDict else ''

def read_and_parse_oxford_list(FileIn, FileOut):
    Tokens = read_oxford_list(FileIn)
    Content = parse_oxford_list(Tokens)
    Content1 = clean_content(Content)
    lara_utils.write_json_to_file(Content1, FileOut)

def clean_content(Content):
    Cleaned = []
    for ( Words, Level ) in Content:
        Words1 = clean_words(Words)
        for Word in Words1:
            Cleaned += [ ( Word, Level ) ]
    return lara_utils.remove_duplicates( sorted(Cleaned, key=lambda x: x[1]) )

def clean_words(Words):
    Out = []
    for Word in Words:
        if '(' in Word:
            return Out
        else:
            Out += [ clean_word(Word) ]
    return Out

def clean_word(Word):
    Out = ''
    for Char in Word:
        if not Char in '0123456789':
            Out += Char
    return Out

def read_oxford_list(File):
    InStr = lara_utils.read_lara_text_file(File)
    InStr = InStr.replace(',', '')
    InStr = InStr.replace('.', '. ')
    Tokens = InStr.split()
    N = len(Tokens)
    lara_utils.print_and_flush(f'--- Read {File} ({N} tokens)')
    return Tokens

# a, an indefinite article A1
# abandon v. B2 ability n. A2
# able adj. A2
# about prep., adv. A1
# above prep., adv. A1
# abroad adv. A2
# absolute adj. B2
# absolutely adv. B1
# academic adj.B1, n. B2
# accept v. A2
# acceptable adj. B2
# access n., v. B1
# accident n. A2

def parse_oxford_list(Tokens):
    ( I, Out ) = ( 0, [] )
    while True:
        try:
            ( Next, I1 ) = read_next_entry(Tokens, I)
        except:
            lara_utils.print_and_flush(f'Failed at {Tokens[I:I+20]}')
            return Out
        if not Next:
            return Out
        Out += [ Next ]
        I = I1

def read_next_entry(Tokens, I):
    if len(Tokens[I:]) == 0:
        return ( False, I )
    ( HeadWords, I1 ) = read_head_words(Tokens, I)
    if not HeadWords:
        return ( False, I )
    ( FirstLevel, I2 ) = read_pos_and_levels(Tokens, I1)
    if not FirstLevel:
        return ( False, I )
    return ( ( HeadWords, FirstLevel ), I2 )

def read_head_words(Tokens, I):
    if len(Tokens[I:]) == 0:
        return ( False, I )
    ( I1, HeadWords ) = ( I, [] )
    while is_head_word(Tokens[I1]):
        HeadWords += [ Tokens[I1] ]
        I1 += 1
    if len(HeadWords) == 0:
        return ( False, I )
    return ( HeadWords, I1 )

def read_pos_and_levels(Tokens, I):
    if len(Tokens[I:]) == 0:
        return ( False, I )
    ( Level, I1 ) = read_single_pos_and_level(Tokens, I)
    if not Level:
        return ( False, I )
    while True:
        ( OtherLevel, I2 ) = read_single_pos_and_level(Tokens, I1)
        if not OtherLevel:
            return ( Level, I1 )
        I1 = I2

def read_single_pos_and_level(Tokens, I):
    if len(Tokens[I:]) == 0:
        return ( False, I )
    I1 = read_pos_list(Tokens, I)
    if not I1:
        return ( False, I)
    return read_level(Tokens, I1)

def read_pos_list(Tokens, I):
    if len(Tokens[I:]) == 0:
        return False
    I1 = read_pos(Tokens, I)
    if not I1:
        return False
    while True:
        I2 = read_pos(Tokens, I1)
        if not I2:
            return I1
        I1 = I2

def read_pos(Tokens, I):
    if len(Tokens[I:]) == 0:
        return False
    Word = Tokens[I]
    if is_pos_word(Word):
        return I + 1
    else:
        return False

def read_level(Tokens, I):
    if len(Tokens[I:]) == 0:
        return False
    Word = Tokens[I]
    if is_level_word(Word):
        return ( Word, I + 1 )
    else:
        return False

def is_head_word(Word):
    return not is_pos_word(Word) and not is_level_word(Word)

_pos_words = [ 'indefinite', 'article',
               'v.', 'n.', 'adj.', 'adv.', 'pron.', 'det.',
               'adj/adv.', '/adv.', 
               'det./pron.', '/pron.',
               'det./adj.', '/adj.',
               'det./number.', '/number', 'number/det.',
               'exclam./n.', '/n.',
               '/prep.', '/det.',
               'modal', 'auxiliary',
               'prep.', 'exclam.', 'conj.', 'number', 'noun.',
               '/',
               'infinitive', 'marker'
               ]

def is_pos_word(Word):
    return Word in _pos_words

_level_words = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2' ]

def is_level_word(Word):
    return Word in _level_words


                
        
            
    
    
    
