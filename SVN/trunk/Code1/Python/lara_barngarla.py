import lara_translations
import lara_parse_utils
import lara_utils

#_raw_file = '$LARA/Content/barngarla_schürmann/corpus/Zuckermann_Barngarla_2020_Original-Barngarla-Sentences_edited.docx'
#_raw_file = '$LARA/Content/barngarla_schürmann/corpus/Zuckermann_Barngarla_2021_Original-Barngarla-Sentences_21-5-21_edited.docx'
_raw_file = '$LARA/Content/barngarla_schürmann/corpus/Zuckermann_Barngarla_2021_Original-Barngarla-Sentences_25-5-21.docx'
#_raw_file = '$LARA/Content/barngarla_schürmann/corpus/Zuckermann_Test3.docx'
_parsed_file = '$LARA/Content/barngarla_schürmann/corpus/parsed_sentences.json'
_lara_formatted_files = {'linguist': '$LARA/Content/barngarla_schürmann/corpus/schürmann_sentences.txt',
                         'layperson': '$LARA/Content/barngarla_schürmann/corpus/schürmann_sentences_layperson.txt',
                         'recording': '$LARA/Content/barngarla_schürmann/corpus/schürmann_sentences_recording.txt'}
_word_translation_spreadsheet = '$LARA/Content/barngarla_schürmann/translations/type_barngarla_english.csv'
_segment_translation_spreadsheet = '$LARA/Content/barngarla_schürmann/translations/barngarla_english.csv'
#_number_of_items_per_page_in_lara_formatted_text = 3
_number_of_items_per_page_in_lara_formatted_text = 1

def read_and_parse_schürmann_sentences():
    Lines = read_schürmann_sentences()
    if Lines == False:
        return
    SplitLines = [ split_line(Line) for Line in Lines ]
    Items = group_split_lines(SplitLines)
    lara_utils.write_json_to_file(Items, _parsed_file)

def format_schürmann_sentences(Version):
    lara_utils.print_and_flush(f'--- Formatting Schürmann sentences ("{Version}")')
    Content = lara_utils.read_json_file(_parsed_file)
    ( FormattedText, WordTranslationsDict, SegmentTranslationsDict ) = lara_format_schürmann_content(Content, Version)
    lara_utils.write_lara_text_file('\n'.join(FormattedText), _lara_formatted_files[Version])
    Header = [ 'Barngarla', 'English' ]
    WordTranslationsTriples = [ [ Word, '; '.join(WordTranslationsDict[Word]), 'current' ] for Word in WordTranslationsDict ]
    SegmentTranslationsTriples = [ [ Segment, '; '.join(SegmentTranslationsDict[Segment]), 'current' ] for Segment in SegmentTranslationsDict ]
    if Version != 'recording':
        lara_translations.write_translation_csv(Header, WordTranslationsTriples, _word_translation_spreadsheet)
        lara_translations.write_translation_csv(Header, SegmentTranslationsTriples, _segment_translation_spreadsheet)

# ---------------------------------------------------

def read_schürmann_sentences():
    lara_utils.print_and_flush(f'--- Reading from {_raw_file}')
    String = lara_utils.read_lara_text_file(_raw_file)
    if String == False:
        return False
    else:
        return String.split('\n')

##    '(2b)\tBakukku kaya yapurubidni \tparu ngarrinyuru, kaitya! ',
##     'Bagoogoo\tgaya\tyaboornbidni\tbaroo\tngarrrinyooroo,\t\t\tgadya!\t',
##     'bagoogoo\tgaya\tyabooroo-\tbidni\tbaroo\tngarrrinyoo-\t\troo\t\tgadya',
##     'behold\tspear\tinto-\t\tDER\tgame\tus two (PATR)-\tPOSS\t\tchild',
##     '‘Behold child! The game is ours, being hit by the spear.’',

def split_line(Line):
    return consolidate_tabs(Line).split('\t')

def consolidate_tabs(Line):
    if Line.find('\t\t') >= 0:
        return consolidate_tabs(Line.replace('\t\t', '\t'))
    else:
        return Line

# Test material
SplitLines1 = [['(1b)', 'Yadlanna bakkanbata'],
               ['yadlana', 'baganbadha'],
               ['yadlana', 'baganba-', 'dha'],
               ['root', 'dig round-', 'PRES'],
               ['‘to bare the root of a tree’']]

SplitLines2 = [['(4a) ', 'Ngaitye pappi buntunni-narru nintye: Ngaitye kaitye winmannintyao warruwakkangalla'],
               ['Ngadyi', 'babi', 'boondooninarrroo', 'nindya:', 'ngadyi'],
               ['ngadyi', 'babi', 'boondooni-', 'na-', 'rrroo', 'nindya', 'ngadyi'],
               ['my', 'father', 'wonder-', 'PAST-', 'he (ERG)', 'thus', 'my'],
               ['', ''],
               ['gadya', 'winmanidhawoo'],
               ['gadya', 'winma-', 'ni-', 'dha-', 'woo'],
               ['child', 'be thin-', 'become-', 'PRES-', 'he/she'],
               [''],
               ['warrroowagangarla.'],
               ['warrroo-', 'waga-', 'ngarla'],
               ['kangaroo-', 'without-', 'plenty'],
               ['? translation needs to be checked']]

SplitLines3 = SplitLines1 + [ [''] ] + SplitLines2

def group_split_lines(SplitLines):
    Out = []
    State = 'outside_item'
    LastIdLine = 'no ID line yet'
    CurrentItem = {}
    while len(SplitLines) > 0:
        Line = [ Word.strip() for Word in SplitLines[0] ]
        SplitLines = SplitLines[1:]
        if is_id_line(Line) and State == 'outside_item':
            if CurrentItem != {}:
                Out += [ check_item(CurrentItem) ]
                CurrentItem = {}
            ( CurrentItem['id'], CurrentItem['original_sent'] ) = parse_id_line(Line)
            LastIdLine = Line
            State = 'expecting_plain_line'
        elif not null_line(Line) and ( State == 'expecting_plain_line' or State == 'expecting_plain_or_empty_line' ):
            add_plain_line(CurrentItem, parse_plain_line(Line))
            State = 'expecting_morphology_line'
        elif not null_line(Line) and State == 'expecting_morphology_line':
            add_morphology_line(CurrentItem, parse_morphology_line(Line))
            State = 'expecting_gloss_line'
        elif not null_line(Line) and State == 'expecting_gloss_line':
            add_gloss_line(CurrentItem, parse_gloss_line(Line))
            State = 'expecting_translation_or_empty_line'
        elif not null_line(Line) and ( State == 'expecting_translation_or_empty_line' or State == 'expecting_more_translation_or_empty_line' ):
            #CurrentItem['translation'] = parse_translation_line(Line)
            #State = 'outside_item'
            add_translation_line(CurrentItem, parse_translation_line(Line))
            State = 'expecting_more_translation_or_empty_line'
        elif null_line(Line) and State == 'expecting_translation_or_empty_line':
            State = 'expecting_plain_or_empty_line'
        elif null_line(Line) and State == 'expecting_more_translation_or_empty_line':
            State = 'outside_item'
        elif null_line(Line) and State == 'expecting_plain_or_empty_line':
            State = 'expecting_plain_or_empty_line'
        elif null_line(Line) and State == 'outside_item':
            State = 'outside_item'
        else:
            lara_utils.print_and_flush(f'*** Error: unable to interpret line {Line}, State = {State}')
            lara_utils.print_and_flush(f'*** Last ID line was {LastIdLine}')
            CurrentItem['unknown_component'] = Line
    if CurrentItem != {}:
        Out += [ check_item(CurrentItem) ]
    return Out

# ['(1b)', 'Yadlanna bakkanbata'],
def is_id_line(Line):
    if len(Line) == 0: return False
    First = Line[0]
    return len(First) >= 3 and First[0] == '(' and First[-1] == ')' and First[1].isdigit()

def parse_id_line(Line):
    Id = Line[0]
    OriginalSentence = ' '.join(Line[1:])
    return ( Id, OriginalSentence )

def null_line(Line):
    return max([ len(X) for X in Line ]) == 0

def parse_plain_line(Line):
    if len(Line[-1]) == 0:
        return lowercase_all_items_in_list(Line[:-1])
    else:
        return lowercase_all_items_in_list(Line)

def lowercase_all_items_in_list(List):
    return [ X.lower() for X in List ]

def add_plain_line(CurrentItem, Line):
    if not 'plain_line' in CurrentItem:
        CurrentItem['plain_line'] = Line
    else:
        CurrentItem['plain_line'] = CurrentItem['plain_line'] + Line

def parse_morphology_line(Line):
    if len(Line[-1]) == 0:
        return Line[:-1]
    else:
        return Line

def add_morphology_line(CurrentItem, Line):
    if not 'morphology_line' in CurrentItem:
        CurrentItem['morphology_line'] = Line
    else:
        CurrentItem['morphology_line'] = CurrentItem['morphology_line'] + Line

def parse_gloss_line(Line):
    if len(Line[-1]) == 0:
        return Line[:-1]
    else:
        return Line

def add_gloss_line(CurrentItem, Line):
    if not 'gloss_line' in CurrentItem:
        CurrentItem['gloss_line'] = Line
    else:
        CurrentItem['gloss_line'] = CurrentItem['gloss_line'] + Line

def parse_translation_line(Line):
    return ' '.join(Line)

def add_translation_line(CurrentItem, Line):
    if not 'translation' in CurrentItem:
        CurrentItem['translation'] = [ Line ]
    else:
        CurrentItem['translation'] = CurrentItem['translation'] + [ Line ]

def check_item(Item):
    if not 'id' in Item or not 'original_sent' in Item or not 'plain_line' in Item or \
       not 'morphology_line' in Item or not 'gloss_line' in Item:
        Item['malformed'] = 'missing_field'
        return Item
    if len(Item['morphology_line']) != len(Item['gloss_line']):
        Item['malformed'] = f"morphology length = {len(Item['morphology_line'])}, gloss length = {len(Item['gloss_line'])}"
        return Item
    if len(Item['plain_line']) != len( [ X for X in Item['morphology_line'] if len(X) > 0 and ( X == '-' or  X[-1] != '-' ) ] ):
        Item['malformed'] = f"mismatch between plain line {Item['plain_line']} and morphology line {Item['morphology_line']}"
        return Item
    return Item

# ---------------------------------------------------

def lara_format_schürmann_content(Content, Version):
    ( WordTranslationsDict, SegmentTranslationsDict ) = ( {}, {} ) 
    FormattedItems = [ lara_format_schürmann_item(Item, WordTranslationsDict, SegmentTranslationsDict, Version) for Item in Content ]
    return ( combine_lara_formatted_schürmann_items(FormattedItems, Version), WordTranslationsDict, SegmentTranslationsDict )

def lara_format_schürmann_item(Item, WordTranslationsDict, SegmentTranslationsDict, Version):
    if Version == 'linguist':
        return lara_format_schürmann_item_linguist(Item, WordTranslationsDict, SegmentTranslationsDict)
    if Version == 'layperson':
        return lara_format_schürmann_item_layperson(Item, WordTranslationsDict, SegmentTranslationsDict)
    if Version == 'recording':
        return lara_format_schürmann_item_recording(Item, WordTranslationsDict, SegmentTranslationsDict)

##{
##        "gloss_line": [
##            "nose",
##            "sneeze-",
##            "PRES"
##        ],
##        "id": "(1a)",
##        "morphology_line": [
##            "moodhla",
##            "babmababma-",
##            "dha"
##        ],
##        "original_sent": "Mudla babmababmata",
##        "plain_line": [
##            "moodhla",
##            "babmababmadha"
##        ],
##        "translation": [
##            "\u2018to sneeze\u2019"
##        ]

def lara_format_schürmann_item_linguist(Item, WordTranslationsDict, SegmentTranslationsDict):
    Header = lara_format_id_and_plain_line(Item['id'], Item['plain_line'])
    TableStartLine = [ '<table>' ]
    PlainLine = lara_format_plain_line(Item['plain_line'], Item['morphology_line'])
    MorphologyLine = lara_format_morphology_line(Item['morphology_line'])
    GlossLine = lara_format_gloss_line(Item['gloss_line'])
    TableEndLine = [ '</table>' ]
    TranslationLine = lara_format_translation_line(Item['translation'])
    OriginalSentLine = lara_format_original_sent(Item['original_sent'])
    add_word_translations_for_plain_line(Item['plain_line'], Item['gloss_line'], WordTranslationsDict)
    add_word_translations_for_morphology_line(Item['morphology_line'], Item['gloss_line'], WordTranslationsDict)
    add_segment_translations_for_plain_line(Item['plain_line'], Item['gloss_line'], Item['translation'], SegmentTranslationsDict)
    add_segment_translations_for_morphology_line(Item['morphology_line'], Item['gloss_line'], Item['translation'], SegmentTranslationsDict)
    FormattedItems = Header + TableStartLine + PlainLine + MorphologyLine + GlossLine + TableEndLine + TranslationLine + OriginalSentLine
    return FormattedItems

def lara_format_schürmann_item_layperson(Item, WordTranslationsDict, SegmentTranslationsDict):
    Header = lara_format_id_and_plain_line(Item['id'], Item['plain_line'])
    TableStartLine = [ '<table>' ]
    PlainLine = lara_format_plain_line(Item['plain_line'], Item['morphology_line'])
    MorphologyLine = lara_format_morphology_line(Item['morphology_line'])
    GlossLine = lara_format_gloss_line(Item['gloss_line'])
    TableEndLine = [ '</table>' ]
    TranslationLine = lara_format_translation_line(Item['translation'])
    add_word_translations_for_plain_line(Item['plain_line'], Item['gloss_line'], WordTranslationsDict)
    add_word_translations_for_morphology_line(Item['morphology_line'], Item['gloss_line'], WordTranslationsDict)
    add_segment_translations_for_plain_line(Item['plain_line'], Item['gloss_line'], Item['translation'], SegmentTranslationsDict)
    add_segment_translations_for_morphology_line(Item['morphology_line'], Item['gloss_line'], Item['translation'], SegmentTranslationsDict)
    FormattedItems = Header + TableStartLine + PlainLine + MorphologyLine + GlossLine + TableEndLine + TranslationLine 
    return FormattedItems

def lara_format_schürmann_item_recording(Item, WordTranslationsDict, SegmentTranslationsDict):
    TableStartLine = [ '<table>' ]
    PlainLine = lara_format_plain_line(Item['plain_line'], Item['morphology_line'])
    MorphologyLine = lara_format_morphology_line(Item['morphology_line'])
    TableEndLine = [ '</table>' ]
    FormattedItems = TableStartLine + PlainLine + MorphologyLine + TableEndLine 
    return FormattedItems

def combine_lara_formatted_schürmann_items(FormattedItems, Version):
    ( I, OutLines ) = ( 0, [] )
    if Version != 'recording':
        OutLines += lara_formatted_schürmann_header()
    for FormattedItem in FormattedItems:
        if I % _number_of_items_per_page_in_lara_formatted_text == 0:
            OutLines += [ f'<page css_file="normal_page.css">' ]
        OutLines += FormattedItem
        I += 1
    return OutLines

def lara_formatted_schürmann_header():
    return [ '<page>',
             '<h1>/*Sentences and Phrases from Schürmann’s Vocabulary*/||</h1>',
             '<b>/*Professor Ghil‘ad Zuckermann, 2020*/||</b>',
             '',
             '<img src="Schürmann_ca1890.jpg" width="372" height="480"/>'
             ]

def lara_format_id_and_plain_line(Id, PlainLine):
    PlainSent = ' '.join(PlainLine).capitalize()
    return [ f'<h2>{Id} {PlainSent}||</h2>' ]

def lara_format_id_and_original_sent(Id, OriginalSent):
    return [ f'<h2>{Id} {OriginalSent}||</h2>' ]
    #return [ '',
    #         f'<b>{Id} {OriginalSent}||</b>' ]

def lara_format_original_sent(OriginalSent):
    return [ f'/*Original Schürmann orthography: {OriginalSent}*/||' ]

##        "morphology_line": [
##            "ila",
##            "widi-",
##            "dha"
##        ],
##        "plain_line": [
##            "ila",
##            "wididhi"
##        ],

_left_lara_bracket = '{{'
_right_lara_bracket = '}}'
            
def lara_format_plain_line(PlainLine, MorphologyLine):
    ( I, J, FormattedRowItems ) = ( 0, 0, [] )
    while I < len(PlainLine):
        J1 = J
        while J1 < len(MorphologyLine) and ( len(MorphologyLine[J1]) > 0 and MorphologyLine[J1] != '-' and MorphologyLine[J1][-1] == '-' ):
            J1 += 1
        if J >= len(MorphologyLine):
            Error = f'*** Error: unable to format plain line = {PlainLine}, morphology line = {MorphologyLine}'
            lara_utils.print_and_flush(Error)
            return Error
        J1 += 1
        Length = J1 - J
        EndSegment = '||' if I == len(PlainLine) - 1 else ''
        if Length == 1:
            FormattedRowItem = f'<td>{_left_lara_bracket}{PlainLine[I]}{_right_lara_bracket}{EndSegment}</td>'
        else:
            # We have a plain text item matching several morphology line items, remove the terminal hyphen from the first one
            Word = PlainLine[I]
            ( WordNoPunct, Punct ) = split_off_terminal_punctuation(Word)
            Lemma = MorphologyLine[J][:-1]
            FormattedRowItem = f'<td colspan="{Length}">{_left_lara_bracket}{WordNoPunct}#{Lemma}#{Punct}{_right_lara_bracket}{EndSegment}</td>'
        J = J1
        I += 1
        FormattedRowItems += [ FormattedRowItem ]
    return format_table_row(FormattedRowItems)

def add_word_translations_for_plain_line(PlainLine, GlossLine, WordTranslationsDict):
    ( I, J ) = ( 0, 0 )
    while I < len(PlainLine):
        J1 = J
        while J1 < len(GlossLine) and ( len(GlossLine[J1]) > 0 and GlossLine[J1] != '-' and GlossLine[J1][-1] == '-' ):
            J1 += 1
        J1 += 1
        Word = split_off_terminal_punctuation(PlainLine[I])[0]
        Translation = split_off_terminal_punctuation(connect_hyphens(' '.join([ GlossLine[K] for K in range(J, J1) ])))[0]
        add_to_translations_dict(lara_translations.regularise_word(Word), Translation, WordTranslationsDict)
        J = J1
        I += 1

def add_word_translations_for_morphology_line(MorphologyLine, GlossLine, WordTranslationsDict):
    for I in range(0, len(MorphologyLine)):
        Translation = split_off_terminal_punctuation(GlossLine[I])[0]
        add_to_translations_dict(lara_translations.regularise_word(MorphologyLine[I]), Translation, WordTranslationsDict)

def add_segment_translations_for_plain_line(PlainLine, GlossLine, TranslationLine, SegmentTranslationsDict):
    PlainSegment = ' '.join(PlainLine)
    GlossTranslation = connect_hyphens(' '.join(GlossLine))
    FreeTranslation = '\n'.join(TranslationLine)
    FullTranslation = f'{GlossTranslation} ({FreeTranslation})' if GlossTranslation != FreeTranslation else GlossTranslation
    add_to_translations_dict(lara_translations.regularise_segment(PlainSegment), FullTranslation, SegmentTranslationsDict)

def add_segment_translations_for_morphology_line(MorphologyLine, GlossLine, TranslationLine, SegmentTranslationsDict):
    MorphologySegment = ' '.join(MorphologyLine)
    GlossTranslation = ' '.join(GlossLine)
    FreeTranslation = '\n'.join(TranslationLine)
    FullTranslation = f'{GlossTranslation} ({FreeTranslation})' if GlossTranslation != FreeTranslation else GlossTranslation
    add_to_translations_dict(lara_translations.regularise_segment(MorphologySegment), FullTranslation, SegmentTranslationsDict)

def add_to_translations_dict(WordOrSegment, Translation0, Dict):
    Translation = Translation0[1:] if len(Translation0) > 0 and Translation0[0] == '?' else Translation0
    if len(Translation) == 0:
        return
    if not WordOrSegment in Dict:
        Dict[WordOrSegment] = [ Translation ]
    elif not Translation in Dict[WordOrSegment]:
        Dict[WordOrSegment] += [ Translation ]

def connect_hyphens(Str):
    return Str.replace(' - ', ' *dash* ').replace('- ', '-').replace(' *dash* ', ' - ')

def split_off_terminal_punctuation(Word):
    if len(Word) == 0:
        return ( '', '')
    if not lara_parse_utils.is_punctuation_char(Word[-1]) or Word[-1] == ')':
        return ( Word, '' )
    ( Word1, Punct1 ) = split_off_terminal_punctuation(Word[:-1])
    return ( Word1, Punct1 + Word[-1] )

##        "morphology_line": [
##            "ila",
##            "widi-",
##            "dha"
##        ],

def lara_format_morphology_line(MorphologyLine):
    List = []
    for I in range(0, len(MorphologyLine)):
        EndSegment = '||' if I == len(MorphologyLine) - 1 else ''
        List += [ f'<td><i>{_left_lara_bracket}{MorphologyLine[I]}{_right_lara_bracket}</i>{EndSegment}</td>' ]
    return format_table_row(List)

##        "gloss_line": [
##            "nose",
##            "sneeze-",
##            "PRES"
##        ],

def lara_format_gloss_line(GlossLine):
    List = []
    for I in range(0, len(GlossLine)):
        EndSegment = '||' if I == len(GlossLine) - 1 else ''
        List += [ f'<td>/*{GlossLine[I]}*/{EndSegment}</td>' ]
    return format_table_row(List)

##        "translation": [
##            "\u2018to sneeze\u2019"

def lara_format_translation_line(TranslationLine):
    return [ '/*' + TranslationLineItem + '*/||' for TranslationLineItem in TranslationLine ]

def format_table_row(FormattedRowItems):
    Intro = [ '  <tr>' ]
    Body = [ f'      {X}' for X in FormattedRowItems ]
    Coda = [ '  </tr>' ]
    return Intro + Body + Coda

