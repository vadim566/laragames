
import lara_utils
import lara_replace_chars
import unicodedata

## Simple utility functions for parsing LARA strings.

## Remove hashtags and HTML annotations, but keep the comments if we have 'keep_comments':'yes' in the parameters
## Returns a (Str, Trace) pair
def remove_hashtag_comment_and_html_annotations(StrIn, Params):
    KeepComments = 'keep_comments' if 'keep_comments' in Params and Params['keep_comments'] == 'yes' else 'delete_comments'
    return remove_hashtag_comment_and_html_annotations1(StrIn, KeepComments)

def remove_hashtag_comment_and_html_annotations1(StrIn, KeepComments):
    I = 0
    N = len(StrIn)
    State = 'outside_annotation'
    StrOut = ''
    while True:
        if I >= N and State == 'outside_annotation':
            return ( StrOut, [] )
        if I >= N:
            return ( '', [ f'*** Error in remove_hashtag_comment_and_html_annotations: incorrect tagging in "{StrIn}"' ] )
        c1 = StrIn[I]
        c2 = StrIn[I:I+2]
        if c2 == "&#":
            StrOut += c2
            I += 2
        elif lara_replace_chars.is_escaped_reserved_char_sequence(c2) and \
             State in ( 'outside_annotation', 'inside_phrase', 'inside_comment' ):
            StrOut += c2
            I += 2
        elif lara_replace_chars.is_escaped_reserved_char_sequence(c2):
            I += 2
        elif c1 == "#" and State == 'outside_annotation':
            State = 'inside_hash'
            I += 1
        elif c1 == "@" and State == 'outside_annotation':
            State = 'inside_phrase'
            I += 1
        elif c1 == "<" and State == 'inside_phrase':
            State = 'inside_phrase_and_html'
            I += 1         
        elif c1 == "<" and State == 'inside_comment':
            State = 'inside_comment_and_html'
            I += 1         
        elif c1 == "<" and State == 'outside_annotation':
            State = 'inside_html'
            I += 1   
        elif c2 == "/*" and State == 'outside_annotation':
            State = 'inside_comment'
            I += 2  
        elif c1 == "#" and State == 'inside_hash':
            State = 'outside_annotation'
            I += 1  
        elif c1 == "@" and State == 'inside_phrase':
            State = 'outside_annotation'
            I += 1 
        elif c1 == ">" and State == 'inside_phrase_and_html':
            State = 'inside_phrase'
            I += 1 
        elif c1 == ">" and State == 'inside_comment_and_html':
            State = 'inside_comment'
            I += 1 
        elif c1 == ">" and State == 'inside_html':
            State = 'outside_annotation'
            I += 1
        elif c2 == "*/" and State == 'inside_comment':
            State = 'outside_annotation'
            I += 2
        elif State == 'inside_hash':
            I += 1
        elif State == 'inside_html':
            I += 1
        elif State == 'inside_phrase_and_html':
            I += 1
        elif State == 'inside_comment_and_html':
            I += 1
        elif State == 'inside_comment' and KeepComments == 'delete_comments':
            I += 1
        elif State == 'inside_comment' and KeepComments == 'keep_comments':
            StrOut += c1
            I += 1
        elif State == 'outside_annotation':
            StrOut += c1
            I += 1
        elif State == 'inside_phrase':
            StrOut += c1
            I += 1
        else:
            return ( '', [ f'*** Error in remove_hashtag_comment_and_html_annotations: incorrect tagging in "{StrIn}"' ] )

## Remove all HTML tags.
## Return a string/trace pair
def remove_html_annotations_from_string(StrIn):
    I = 0
    N = len(StrIn)
    State = 'outside_annotation'
    StrOut = ''
    while True:
        if I >= N and State == 'outside_annotation':
            return ( StrOut, [] )
        if I >= N:
            return ( '', [ f'*** Error in remove_html_annotations_from_string: incorrect tagging in "{StrIn}"' ] )
        c1 = StrIn[I]
        c2 = StrIn[I:I+2]
        if c2 == '\\<':
            StrOut += c2
            I += 2
        elif c1 == "<" and State == 'outside_annotation':
            State = 'inside_html'
            I += 1   
        elif c1 == ">" and State == 'inside_html':
            State = 'outside_annotation'
            I += 1
        elif State == 'inside_html':
            I += 1
        elif State == 'outside_annotation':
            StrOut += StrIn[I]
            I += 1
        else:
            return ( '', [ f'*** Error in remove_html_annotations_from_string: incorrect tagging in "{StrIn}"' ] )

## Remove all hashtags and phrase markings.
## Return a string
def remove_hashtag_annotations_from_string(StrIn):
    if StrIn.find('#') < 0 and StrIn.find('@') < 0:
        return StrIn
    I = 0
    N = len(StrIn)
    State = 'outside_annotation'
    StrOut = ''
    while True:
        if I >= N and State == 'outside_annotation':
            return StrOut
        if I >= N:
            lara_utils.print_and_flush(f'*** Error in remove_hashtag_annotations_from_string: incorrect tagging in "{StrIn}"')
            return False
        c1 = StrIn[I]
        c2 = StrIn[I:I+2]
        if c2 == "&#":
            StrOut += c2
            I += 2
        elif lara_replace_chars.is_escaped_reserved_char_sequence(c2) and \
             State in ( 'outside_annotation', 'inside_phrase' ):
            StrOut += c2
            I += 2
        elif lara_replace_chars.is_escaped_reserved_char_sequence(c2):
            I += 2
        elif c1 == "#" and State == 'outside_annotation':
            State = 'inside_hash'
            I += 1   
        elif c1 == "#" and State == 'inside_hash':
            State = 'outside_annotation'
            I += 1
        elif c1 == "@" and State == 'outside_annotation':
            State = 'inside_phrase'
            I += 1   
        elif c1 == "@" and State == 'inside_phrase':
            State = 'outside_annotation'
            I += 1
        elif State == 'inside_hash':
            I += 1
        elif State == 'outside_annotation' or State == 'inside_phrase':
            StrOut += StrIn[I]
            I += 1
        else:
            return ( '', [ f'*** Error in remove_hashtag_annotations_from_string: incorrect tagging in "{StrIn}"' ] )   

## Remove top-level tags (i.e. not things like </i>) and comments.
## Return a string/trace pair
def remove_top_level_tags_and_comments(StrIn):
    I = 0
    N = len(StrIn)
    StrOut = ''
    while True:
        if I >= N:
            return ( StrOut, [] )
        c1 = StrIn[I]
        c2 = StrIn[I:I+2]
        if c2 == '\\<':
            StrOut += c2
            I += 2
        elif substring_found_at_index(StrIn, I, "<"):
            End = StrIn.find(">", I+1)
            if End > I and is_top_level_tag(StrIn[I:End+len('>')]):
                I = End + len('>')
            elif End > I:
                StrOut += StrIn[I:End+len('>')]
                I = End + len('>')
            else:
                return ( '', [ f'*** Error in remove_top_level_tags_and_comments: incorrect tagging in "{StrIn}"' ] )
        elif substring_found_at_index(StrIn, I, "/*"):
            End = StrIn.find("*/", I+len("*/"))
            if End > I:
                I = End + len("*/")
                # Shorten comments to minimal comments
                StrOut += '/**/'
            else:
                return ( '', [ f'*** Error in remove_top_level_tags_and_comments: incorrect tagging in "{StrIn}"' ] )
        else:
            StrOut += StrIn[I]
            I += 1

def is_top_level_tag(Str):
    if Str in ['<h1>', '</h1>',
               '<h2>', '</h2>',
               '<table>', '</table>',
               '<tr>', '</tr>',
               '<td>', '</td>']:
        return True
    elif substring_found_at_index(Str, 0, '<img '):
        return True
    elif substring_found_at_index(Str, 0, '<video '):
        return True
    elif substring_found_at_index(Str, 0, '<audio '):
        return True
    else:
        return False

## Remove img and audio tags only
## Return a string/trace pair
def remove_img_and_audio_tags(StrIn):
    I = 0
    N = len(StrIn)
    StrOut = ''
    while True:
        if I >= N:
            return ( StrOut, [] )
        c1 = StrIn[I]
        c2 = StrIn[I:I+2]
        if c2 == '\\<':
            StrOut += c2
            I += 2
        elif c1 == '<':
            End = StrIn.find(">", I+1)
            if End > I and is_img_or_audio_tag(StrIn[I:End]):
                I = End + 1
            elif End > I:
                StrOut += StrIn[I:End+1]
                I = End + 1
            else:
                return ( '', [ f'*** Error in remove_img_and_audio_tags: incorrect tagging in "{StrIn}"' ] )
        else:
            StrOut += StrIn[I]
            I += 1

def is_img_or_audio_tag(Str):
    if substring_found_at_index(Str, 0, '<img '):
        return True
    elif substring_found_at_index(Str, 0, '<video '):
        return True
    elif substring_found_at_index(Str, 0, '<audio '):
        return True
    else:
        return False


#### Clean up string by adding spaces before and after various
#### punctuation marks. This is ad hoc and not robust. We need a better way
##clean_substitutions = [ [ "|", "| " ],
##                        [ " M.", " M." ],
##                        [ " Mr.", " Mr." ],
##                        [ " Mrs.", " Mrs." ],
##                        [ "\n", " " ],
##                        [ " M.", " M." ],
##                        [ "...", " ... " ],
##                        [ "…", " ... " ],
##                        [ ".»", " . » " ],
##                        [ "?»", " ? » " ],
##                        [ "!»", " ! » " ],
##                        [ ".", " . " ],
##                        [ "?", " ? " ],
##                        [ "؟", " ؟ " ],
##                        [ "!", " ! " ],
##                        [ ";", " ; " ],
##                        [ "؛", " ؛ " ],
##                        [ ":", " : " ],
##                        [ "--", " - " ],
##                        [ "—", " — " ],
##                        [ "«", "« " ],
##                        [ "»", " » " ],
##                        [ "“", "“ " ],
##                        [ "”", " ” " ],
##                        [ "\"", "" ],
##                        [ ",", " ," ],
##                        [ "،", " ،" ],
##                        [ "'", "' " ],
##                        [ "‘", " ‘ " ],
##                        [ "’", " ’ " ],
##                        [ "(", "( " ],
##                        [ ")", " )" ],
##                        #[ "_", "" ],
##                        [ "　", " " ],
##                        [ "。", " 。" ],
##                        [ "、", " 、" ],
##                        [ "！", " ！" ],
##                        [ "「", "「 " ],
##                        [ "」", " 」 " ]
##                        ]
##
##def clean_lara_string(StrIn):
##    N = len(StrIn)
##    State = 'top_level'
##    StrOut = ''
##    I = 0
##    while True:
##        if I >= N and State == 'top_level':
##            return ( StrOut, [] )
##        if I >= N:
##            return ( StrIn, [f'*** Error in clean_lara_string: incorrect tagging in "{StrIn}"'] )
##        c1 = StrIn[I]
##        c2 = StrIn[I:I+2]
##        if c2 == '\\@':
##            StrOut += c2
##            I += 2
##        elif c1 == "@" and State == 'top_level':
##            State = 'inside_phrase_brackets'
##            StrOut += StrIn[I]
##            I += 1
##        elif c1 == "@" and State == 'inside_phrase_brackets':
##            State = 'top_level'
##            StrOut += StrIn[I]
##            I += 1
##        elif State == 'inside_phrase_brackets':
##            StrOut += StrIn[I]
##            I += 1
##        # Special handling of single quote/apostrophe surrounded by letters and possibly vertical bars or hashtags
##        elif I + 2 < N and State == 'top_level' and StrIn[I] == '|' and is_apostrophe_char(StrIn[I + 1]) and StrIn[I+2].isalpha():
##            StrOut += f'| {StrIn[I+1]}{StrIn[I+2]}'
##            I += 3
##        elif I + 2 < N and State == 'top_level' and StrIn[I].isalpha() and is_apostrophe_char(StrIn[I + 1]) and StrIn[I] == '|':
##            StrOut += f'{StrIn[I]}{StrIn[I+1]}| '
##            I += 3
##        elif I + 2 < N and State == 'top_level' and StrIn[I].isalpha() and is_apostrophe_char(StrIn[I + 1]) and \
##             ( StrIn[I+2].isalpha() or ( StrIn[I+2] == '#' and not StrIn[I+2:I+3] == '##' ) ):
##            StrOut += f'{StrIn[I]}{StrIn[I+1]}{StrIn[I+2]}'
##            I += 3                                                                                   
##        else:
##            MatchResult = match_against_substitutions_table(StrIn, I, clean_substitutions)
##            if MatchResult:
##                ( From, To ) = MatchResult
##                StrOut += To
##                I += len(From)
##            else:
##                StrOut += StrIn[I]
##                I += 1
##
##def match_against_substitutions_table(Str, Index, Table):
##    for Line in Table:
##        ( From, To ) = Line
##        if substring_found_at_index(Str, Index, From):
##            return ( From, To )
##    return False

# AudioOutput help any_speaker MISSING_FILE all# (no trace info)
def parse_ldt_recording_script_line(Line):
    start_string = "MISSING_FILE "
    end_string = "#"
    Start = Line.find(start_string)
    if Start < 0:
        return False
    End = Line.find(end_string, Start + len(start_string))
    if End < 0:
        return False
    return Line[Start + len(start_string):End]

def parse_ldt_metadata_file_line(Line):
    if Line.find("AudioOutput") >= 0:
        return parse_ldt_metadata_file_ldt_line(Line)
    elif Line.find("NonLDTAudioFile") >= 0:
        return parse_ldt_metadata_file_non_ldt_line(Line)
    else:
        return False

# AudioOutput help any_speaker help/50771_181219201652.wav 'Now run along, and don't get into mischief. I am going out.'# |
def parse_ldt_metadata_file_ldt_line(Line):
    HelpIndex = Line.find("help/")
    if HelpIndex > 0:
        StartFileIndex = HelpIndex + len("help/")
    else:
        return False
    if Line.find(".wav") > 0:
        EndFileIndex = Line.find(".wav") + len(".wav")
    elif Line.find(".mp3") > 0:
        EndFileIndex = Line.find(".mp3") + len(".mp3")
    else:
        return False
    File = Line[StartFileIndex:EndFileIndex]
    FirstNonSpaceInTextIndex = skip_spaces(Line, EndFileIndex)
    HashIndex = Line.find("#")
    if HashIndex > EndFileIndex:
        Text = Line[FirstNonSpaceInTextIndex:HashIndex]
        return ( File, Text )
    else:
        return File

# NonLDTAudioFile Inferno_I_1-12.mp3
def parse_ldt_metadata_file_non_ldt_line(Line):
    TagIndex = Line.find("NonLDTAudioFile")
    if TagIndex >= 0:
        EndTagIndex = TagIndex + len("NonLDTAudioFile")
    else:
        return False
    FirstNonSpaceInTextIndex = skip_spaces(Line, EndTagIndex)
    File = remove_final_spaces(Line[FirstNonSpaceInTextIndex:])
    if len(File) > 0:
        return ( File, 'NonLDTAudioFile' )
    else:
        return False

mwe_lemma_marking_chars = '*'

def mwe_def_word_to_lemma(Word):
    if Word.isupper():
        return Word.lower()
    elif len(Word) > 2 and \
         Word[0] in mwe_lemma_marking_chars and \
         Word[-1] in mwe_lemma_marking_chars and \
         Word[0] == Word[-1]:
        return Word[1:-1]
    else:
        return False

def word_marked_as_mwe_lemma(Word):
    return True if mwe_def_word_to_lemma(Word) else False

mwe_classes = {}

def init_parse_mwe_file():
    global mwe_classes
    mwe_classes = {}

def mark_as_mwe_class(ClassName):
    mwe_classes[ClassName] = True

def is_mwe_class(ClassName):
    return ClassName in mwe_classes
 
def parse_mwe_def(Line):
    if Line.startswith('transform:'):
        return parse_mwe_transform(Line)
    elif Line.startswith('class:'):
        return parse_mwe_class(Line)
    else:
        return parse_mwe_normal_def(Line)

# transform: se VERB -> VERB toi
def parse_mwe_transform(Line):
    Line1 = Line[len('transform:'):]
    TopComponents = Line1.split('->')
    if len(TopComponents) != 2:
        return False
    ( LHSString, RHSString ) = TopComponents
    ( LHSList, RHSList ) = ( LHSString.split(), RHSString.split() )
    LHS = mark_mwe_constants_and_vars(LHSList, RHSList)
    RHS = mark_mwe_constants_and_vars(RHSList, LHSList)
    if not LHS or not RHS:
        lara_utils.print_and_flush(f'*** Error: bad transform: "{Line}"')
        return False
    return { 'type': 'transform',
             'lhs': LHS,
             'rhs': RHS
             }

def mark_mwe_constants_and_vars(List, OtherList):
    MarkedList = [ mark_constants_and_vars_on_element(X, OtherList) for X in List ]
    return MarkedList if not False in MarkedList else False

def mark_constants_and_vars_on_element(X, OtherList):
    if not syntactically_marked_as_mwe_tranform_var(X):
        return [ 'const', X ]
    elif X in OtherList:
        return [ 'var', X ]
    else:
        lara_utils.print_and_flush(f'*** Error: variable "{X}" only on one side of transform')
        return False

def syntactically_marked_as_mwe_tranform_var(X):
    return len(X) >= 3 and X.startswith('*') and X.endswith('*')

# class: se me m te t se s nous vous
def parse_mwe_class(Line):
    Components = Line.split()
    if len(Components) < 3:
        return False
    else:
        ( ClassName, ClassMembers ) = ( Components[1], Components[2:] )
        mark_as_mwe_class(ClassName)
        return { 'type': 'class',
                 'name': ClassName,
                 'body': ClassMembers
                 }

# se éloigner | name:s'éloigner POS:V
def parse_mwe_normal_def(Line):
    TopComponents = [ Component.strip() for Component in Line.split('|') ]
    if len(TopComponents) == 2:
        ( Main, Annotation ) = ( TopComponents[0], TopComponents[1] )
        ParsedAnnotation = parse_mwe_annotation( TopComponents[1], Line)
        for Key in ParsedAnnotation:
            if not Key in [ 'name', 'pos' ]:
                lara_utils.print_and_flush(f'*** Error: unknown keyword "{Key}" in MWE def line "{Line}"')
                return False
        Name = ParsedAnnotation['name'] if 'name' in ParsedAnnotation else default_name_for_mwe_words(Main)
        POS = ParsedAnnotation['pos'] if 'pos' in ParsedAnnotation else ''
    elif len(TopComponents) == 1:
        ( Main, Name, POS ) = ( Line, default_name_for_mwe_words(TopComponents[0]), '' )
    else:
        return False
    Components = Main.split()
    ListOfLists = [ mwe_expand_word(Component) for Component in Components ]
    Body = [ Element for List in ListOfLists for Element in List ]
    return { 'type': 'mwe_def',
             'name': Name,
             'pos': POS,
             'body': Body
             }

def default_name_for_mwe_words(Str):
    #return ' '.join(Str.lower().split())
    return ' '.join([ mwe_component_to_name_form(Component) for Component in Str.split() ])

def mwe_component_to_name_form(Component):
    if word_marked_as_mwe_lemma(Component):
        return mwe_def_word_to_lemma(Component)
    else:
        return Component.lower()

# se AGIR de | POS:V NAME:s'agir de

def parse_mwe_annotation( Annotation, Line):
    Components0 = Annotation.split()
    Components1 = [ mwe_annotation_component_classify(Component.split(':')) for Component in Components0 ]
    Components2 = [ Component for Group in Components1 for Component in Group ]
    return combine_mwe_annotation_components(Components2, Line) 

def mwe_annotation_component_classify(List):
    if len(List) == 1:
        return [ [ List[0], 'value_component' ] ]
    elif len(List) == 2 and List[1] == '':
        return [ [ List[0], 'key' ] ]
    elif len(List) == 2:
        return [ [ List[0], 'key' ], [ List[1], 'value_component' ] ]
    else:
        return False

def combine_mwe_annotation_components(Components, Line):
    #lara_utils.print_and_flush(f'--- Components = {Components}')
    ( CurrentKey, Out, CurrentValueList ) = ( False, [], [] )
    while True:
        if len(Components) == 0:
            if len(CurrentValueList) == 0:
                lara_utils.print_and_flush(f'*** Error: bad MWE annotation in {Line}')
                return False
            else:
                Out += [ [ CurrentKey, ' '.join(CurrentValueList) ] ]
                Dict = { Element[0] : Element[1] for Element in Out }
                #lara_utils.print_and_flush(f'--- Combined components = {Dict}')
                return Dict
        ( CurrentValue, CurrentType ) = Components[0]
        Components = Components[1:]
        if CurrentType == 'key':
            if CurrentKey:
                if len(CurrentValueList) == 0:
                    lara_utils.print_and_flush(f'*** Error: bad MWE annotation in {Line}')
                    return False
                else:
                    Out += [ [ CurrentKey, ' '.join(CurrentValueList) ] ]
            ( CurrentKey, CurrentValueList ) = ( CurrentValue.lower(), [] )
        else:
            CurrentValueList += [ CurrentValue ]
                           
def mwe_expand_word(Word):
    Lemma = mwe_def_word_to_lemma(Word)
    if Lemma:
        return [ [ 'lemma', Lemma ] ]
    elif is_mwe_class(Word):
        return [ [ 'surface', Word ] ]
    else:
        return [ [ 'surface', Component ] for Component in split_mwe_def_word(Word.lower()) ]

def split_mwe_def_word(Word):
    return lara_utils.split_on_multiple_delimiters([ '\'', '’', '-' ], Word)

def skip_spaces(Str, Start):
    Index = Start
    N = len(Str)
    while True:
        if Index >= N:
            return N
        elif Str[Index].isspace():
            Index += 1
        else:
            return Index

def brackets_properly_used_in_string(String, OpenBracket, CloseBracket):
    if String.find(OpenBracket) < 0 and String.find(CloseBracket) < 0:
        return ( True, '' )
    ( I, N, LookingFor ) = ( 0, len(String), OpenBracket )
    while True:
        if I >= N:
            if LookingFor == OpenBracket:
                return ( True, '' )
            else:
                return ( False,  f'*** Warning: unmatched {OpenBracket} in {String[:200]}' )
        if String[I:].startswith(OpenBracket):
            if LookingFor == OpenBracket:
                I += len(OpenBracket)
                LookingFor = CloseBracket
            else:
                return ( False, f'*** Warning: nested {OpenBracket} in {String[:200]}' )
        elif String[I:].startswith(CloseBracket):
            if LookingFor == CloseBracket:
                I += len(CloseBracket)
                LookingFor = OpenBracket
            else:
                return ( False, f'*** Warning: unmatched {CloseBracket} in {String[:200]}' )
        else:
            I += 1

def find_next_non_escaped_hash_index(Str, Start):
    return find_next_non_escaped_char_index(Str, '#', Start)

def find_next_non_escaped_at_sign_index(Str, Start):
    return find_next_non_escaped_char_index(Str, '@', Start)

def find_next_non_escaped_char_index(Str, Char, Start):
    I = Start + 1
    N = len(Str)
    while True:
        # Gone past the end of the string
        if I >= N:
            return -1
        NextCharIndex = Str.find(Char, I)
        # There was no char
        if NextCharIndex < 0:
            return NextCharIndex
        # We found a non-escaped char
        elif Str[NextCharIndex - 1] != '\\':
            return NextCharIndex
        # It was an escaped char. Skip both characters and try again
        else:
            I = NextCharIndex + 1

def substring_found_at_index(Str, Index, Substr):
    return Str[Index:Index + len(Substr)] == Substr 
    # return Str.find(Substr, Index, Index + len(Substr)) >= 0

def regularise_spaces(Str):
    return ' '.join(Str.split())

def replace_nonbreaking_spaces_with_spaces_in_string(Str):
    return Str.replace('\xa0', ' ')

def remove_weird_characters(Str):
    # Odd things in Japanese
    #Str1 = Str.replace('　', '')
    Str1 = Str
    return Str1.replace('\ufeff', '')

def remove_initial_and_final_spaces(Str):
    return remove_final_spaces(remove_initial_spaces(Str))

def remove_audio_prefix(Str):
    import re
    Str1 = re.sub( r"^_[^:]+_:", "", Str)
    return Str1

def remove_initial_spaces(Str):
    I = 0
    N = len(Str)
    while True:
        if I >= N:
            return ''
        elif Str[I].isspace():
            I += 1
        else:
            return Str[I:]

def remove_final_spaces(Str):
    I = 0
    N = len(Str)
    while True:
        if I >= N:
            return Str
        elif (Str[I:]).isspace():
            return Str[:I]
        else:
            I += 1


def remove_initial_and_final_punctuation_marks(Str):
    return remove_final_punctuation_marks(remove_initial_punctuation_marks(Str))

def remove_initial_and_final_punctuation_marks_but_not_final_hyphen_or_apostrophe(Str):
    return remove_final_punctuation_marks_but_not_final_hyphen_or_apostrophe(remove_initial_punctuation_marks(Str))
##def remove_initial_and_final_punctuation_marks_but_not_final_hyphen(Str):
##    return remove_final_punctuation_marks_but_not_final_hyphen(remove_initial_punctuation_marks(Str))

def remove_final_hyphen(Str):
    if Str[-1:] == '-':
        return Str[:-1]
    else:
        return Str

def remove_punctuation_marks(Str):
    ( I, N, Str1 ) = ( 0, len(Str), '')
    while True:
        if I >= N:
            return Str1
        c1 = Str[I]
        c2 = Str[I:I+2]
        if lara_replace_chars.is_escaped_reserved_char_sequence(c2):
            Str1 += c2
            I += 2
        elif not is_punctuation_char(c1):
            Str1 += c1
            I += 1
        else:
            I += 1

def remove_punctuation_marks_except_hyphen_and_underscore(Str):
    ( I, N, Str1 ) = ( 0, len(Str), '')
    while True:
        if I >= N:
            return Str1
        c1 = Str[I]
        c2 = Str[I:I+2]
        if lara_replace_chars.is_escaped_reserved_char_sequence(c2):
            Str1 += c2
            I += 2
        elif not is_punctuation_char(c1) or c1 in "-_":
            Str1 += c1
            I += 1
        else:
            I += 1

def remove_initial_punctuation_marks(Str):
    I = 0
    N = len(Str)
    while True:
        if I >= N:
            return ''
        c1 = Str[I]
        c2 = Str[I:I+2]
        if lara_replace_chars.is_escaped_reserved_char_sequence(c2):
            return Str[I:]
        elif is_punctuation_char(c1):
            I += 1
        else:
            return Str[I:]

def remove_final_punctuation_marks(Str):
    I = 0
    N = len(Str)
    while True:
        if I >= N:
            return Str
        elif lara_replace_chars.is_escaped_reserved_char_sequence(Str[I:I+2]):
            I += 2
        elif is_punctuation_or_vertical_bar_string(Str[I:]):
            return Str[:I]
        else:
            I += 1

def remove_final_punctuation_marks_but_not_final_hyphen_or_apostrophe(Str):
#def remove_final_punctuation_marks_but_not_final_hyphen(Str):
    I = 0
    N = len(Str)
    # If it ends with a hyphen or apostrophe, don't remove anything
    Lastchar = Str[-1]
    if Lastchar == '-' or is_apostrophe_char(Lastchar):
    #if Lastchar == '-':
        return Str
    while True:
        if I >= N:
            return Str
        elif lara_replace_chars.is_escaped_reserved_char_sequence(Str[I:I+2]):
            I += 2
        elif is_punctuation_or_vertical_bar_string(Str[I:]):
            return Str[:I]
        else:
            I += 1

def is_punctuation_or_vertical_bar_string(Str):
    for I in range(0, len(Str)):
        if lara_replace_chars.is_escaped_reserved_char_sequence(Str[I:I+2]):
            return False
        if not is_punctuation_or_vertical_bar_char(Str[I]):
            return False
    return True

def is_punctuation_string(Str):
    if not isinstance(Str, str):
        return False
    for I in range(0, len(Str)):
        if lara_replace_chars.is_escaped_reserved_char_sequence(Str[I:I+2]):
            return False
        if not is_punctuation_char(Str[I]):
            return False
    return True

def is_punctuation_or_vertical_bar_char(Char):
    return Char == '|' or is_punctuation_char(Char)

def is_punctuation_char(Char):
    return unicodedata.category(Char)[0] == 'P' or Char in '¦−'

def is_apostrophe_char(X):
    return X in "'’"







   
