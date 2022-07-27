
import lara_forced_alignment
import lara_images
import lara_audio
import lara_config
import lara_utils
import lara_parse_utils
import lara_replace_chars
import lara_mwe
import copy

##Turn a LARA file into internalised form, which can be written out as JSON.
##The internalised form consists of a list of triples, one per segment.
##Each triple is of the form
##
##[ RawString, MinimalCleaned, Cleaned ]
##
##where
##
##RawString is the original segment string, including all the LARA markup
##MinimalCleaned is the string with the formatting removed
##Cleaned is a list of [Word, Lemma] pairs

## Some test examples
def test_clean_lara_file(Id):
    if Id == 'peter':
        test_clean_lara_file1('$LARA/Content/peter_rabbit/corpus/peter_rabbit.txt',
                              '$LARA/Content/peter_rabbit/corpus/local_config.json',
                              '$LARA/tmp/peter_rabbit_split.json',
                              '$LARA/tmp/peter_rabbit_feedback.txt')
    elif Id == 'revivalistics':
        test_clean_lara_file1('$LARA/Content/revivalistics/corpus/revivalistics.txt',
                              '$LARA/Content/revivalistics/corpus/local_config.txt'
                              '$LARA/tmp/revivalistics_split.json',
                              '$LARA/tmp/revivalistics_feedback.txt')

def test_clean_lara_file1(CorpusFile, ConfigFile, SplitFile, FeedbackFile):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    clean_lara_file(CorpusFile, Params, SplitFile, FeedbackFile)

## Top-level function. Read the split file (output of clean_lara_file).
## Try to create it if it's not there and the corpus file is defined.
## If we are doing distributed, then the corpus file will be null.
def read_split_file(SplitFile, Params):
    if Params.corpus != '' and not lara_utils.file_exists(Params.corpus):
        lara_utils.print_and_flush(f'*** Error: unable to find corpus file {Params.corpus}, giving up')
        return False
    if not lara_utils.file_exists(SplitFile) or \
       Params.corpus != '' and not lara_utils.file_is_newer_than_file(SplitFile, Params.corpus):
        lara_utils.print_and_flush(f'--- Trying to remake split file {SplitFile} from corpus file {Params.corpus}')
        try:
            clean_lara_file(Params.corpus, Params, SplitFile, lara_utils.get_tmp_trace_file(Params))
        except:
            lara_utils.print_and_flush(f'*** Error: something went wrong when trying to create {SplitFile}, giving up')
            return False
    if lara_utils.file_exists(SplitFile):
        return lara_utils.read_json_file(SplitFile)
    else:
        lara_utils.print_and_flush(f'*** Error: unable to find {SplitFile} and unable to create it, giving up')
        return False

## Top-level function. Turn InFile into OutFile using the Params, which are a dictionary taken from the local_config parameters.
## Errors and other feedback are written out to TaggingFeedbackFile
def clean_lara_file(InFile, Params, OutFile, TaggingFeedbackFile):
    if not Params:
        lara_utils.print_and_flush(f'*** Error: unable to internalise config file, giving up')
        return False
    return clean_lara_file1(InFile, Params, OutFile, TaggingFeedbackFile)

def clean_lara_file1(InFile, Params, OutFile, TaggingFeedbackFile):
    Result = clean_lara_file_main(InFile, Params)
    if not Result:
        return False
    else:
        (Units, Trace) = Result
    ## Chunks are tagged by a fourth element which says where they have come from
    ## In "distributed LARA", this is the name of the resource, in the local version it's 'local_files'
    Units1 = add_tags_to_chunks(Units, 'local_files')
    lara_utils.write_json_to_file(Units1, OutFile)
    StatisticsTrace = print_split_file_statistics(Units)
    print_stored_trace_output_to_file(Trace + StatisticsTrace, TaggingFeedbackFile)
    return print_errors_from_trace(Trace)

def print_errors_from_trace(Trace):
    Errors = [ Line for Line in Trace if '*** Error' in Line ]
    if len(Errors) != 0:
        lara_utils.print_and_flush(f'\n{len(Errors)} ERRORS\n')
        for Line in Errors:
            lara_utils.print_and_flush(Line)
        return False
    else:
        return True

## Extract pages, img files and embedded audio files from a corpus file
def extract_css_img_and_audio_files(InFile, Params):
    ( PageOrientedSplitList, AudioTrackingData, Errors ) = clean_lara_file_main_minimal(InFile, Params)
    if not PageOrientedSplitList:
        return {}
    ( CSSFiles, Imgs, Audios ) = ( [], [], [] )
    for ( PageInfo, Units ) in PageOrientedSplitList:
        if 'css_file' in PageInfo:
            CSSFiles += [ PageInfo['css_file'] ]
        for Unit in Units:
            RawText = Unit[0]
            Imgs += lara_images.img_files_referenced_in_string(RawText)
            Audios += lara_audio.audio_files_referenced_in_string(RawText)
    return { 'css_files': lara_utils.remove_duplicates(CSSFiles),
             'img_files': lara_utils.remove_duplicates(Imgs),
             'audio_files': lara_utils.remove_duplicates(Audios) }

## Minimal version that doesn't do any checking
def clean_lara_file_main_minimal(InFile, Params):
    InStr0 = lara_utils.read_lara_text_file(InFile)
    if not InStr0:
        return False
    ( InStr, AudioTrackingData, Trace0 ) = lara_audio.extract_audio_tracking_data_from_string(InStr0, Params)
##    if AudioTrackingData != {}:
##        lara_audio.write_audio_tracking_data_to_tmp_resources(AudioTrackingData, Params)
    ( Units, Trace1 ) = split_and_clean_lara_string(InStr, Params) 
    return ( split_list_to_page_oriented_split_list(Units), AudioTrackingData, Trace0 + Trace1 )

## The main processing: create the chunks and the trace output, but don't write things out
## Each part returns main output and trace, and we stick all the traces together at the end
def clean_lara_file_main(InFile, Params):
    InStr = lara_utils.read_lara_text_file(InFile)
    if not InStr:
        return False
    return clean_lara_string_main(InStr, Params)

def clean_lara_string_main(InStr0, Params):
    ( InStr, AudioTrackingData, Trace0 ) = lara_audio.extract_audio_tracking_data_from_string(InStr0, Params)
    if AudioTrackingData != {}:
        #Params.audio_tracking = { 'enabled': 'yes', 'element_to_trackingpoints': AudioTrackingData }
        lara_audio.write_audio_tracking_data_to_tmp_resources(AudioTrackingData, Params)
    Trace1 = check_image_and_audio_tags_in_lara_string(InStr, Params)
    ( Units, Trace2 ) = split_and_clean_lara_string(InStr, Params)
    NonNullUnits = [ Unit for Unit in Units if len(Unit[0]) > 0 ]
    PageOrientedSplitList = split_list_to_page_oriented_split_list(NonNullUnits)
    ## This produces warnings when the same word has been tagged in different ways
    Trace3 = inconsistent_tagging_messages(NonNullUnits)
    FullTrace = Trace0 + Trace1 + Trace2 + Trace3
    lara_utils.print_and_flush('\n'.join(FullTrace))
    return ( PageOrientedSplitList, FullTrace )

## Group segments by page, using the page tags
def split_list_to_page_oriented_split_list(SplitList):
    ( OutList, CurrentSplitList, CurrentPageInfo, PageNumber ) = ( [], [], '*start*', 1 )
    for Chunk in SplitList:
        if lara_utils.is_page_tag_chunk(Chunk):
            if CurrentPageInfo == '*start*' and len(CurrentSplitList) > 0:
                lara_utils.print_and_flush('*** Warning: material found before first <page> tag. Assuming extra <page> at start')
                OutList = [[{'page': PageNumber}, CurrentSplitList]]
                CurrentSplitList = []
                PageNumber = 2
            elif not CurrentPageInfo == '*start*':
                OutList += [[CurrentPageInfo, CurrentSplitList]]
                CurrentSplitList = []
            CurrentPageInfo = lara_utils.page_tag_chunk_page_info(Chunk)
            if not 'page' in CurrentPageInfo:
                CurrentPageInfo['page'] = PageNumber
                PageNumber += 1
        else:
            CurrentSplitList += [Chunk]
    if len(CurrentSplitList) > 0: 
        OutList += [[CurrentPageInfo, CurrentSplitList]]
    return remove_leading_linebreaks_in_pages(OutList)

def remove_leading_linebreaks_in_pages(PageOrientedSplitList):
    return [ ( PageInfo, remove_leading_linebreaks_in_page(Chunks) ) for ( PageInfo, Chunks ) in PageOrientedSplitList ]

def remove_leading_linebreaks_in_page(Chunks):
    if len(Chunks) > 0 and is_whitespace_chunk(Chunks[0]):
        return remove_leading_linebreaks_in_page(Chunks[1:])
    else:
        return Chunks

def remove_leading_linebreaks_in_chunk(Chunk):
    if len(Chunk) > 0:
        return [ remove_leading_linebreaks_in_string(Chunk[0]) ] + Chunk[1:]
    else:
        return Chunk

def remove_leading_linebreaks_in_string(Str):
    return remove_leading_linebreaks_in_string(Str[1:]) if Str[0] in "\n" else Str

def is_whitespace_chunk(Chunk):
    RawString = Chunk[0]
    return len(RawString) == 0 or RawString.isspace() 

## Split the string for the whole text into segments, process each one separately
## into a chunk and a piece of trace, then stick everything together
def split_and_clean_lara_string(String, Params):
    Segments = add_segment_marks_around_page_tags(String).split('||')
    ChunksAndTraces = [ string_to_text_chunk(Segment, Params) for Segment in Segments ]
    ( AllChunks, AllTraces ) = ( [], [] )
    for ChunkAndTrace in ChunksAndTraces:
        ( Chunk, Trace ) = ChunkAndTrace
        AllChunks = AllChunks + [ Chunk ]
        AllTraces = AllTraces + Trace
    return ( AllChunks, AllTraces )

## Add segment marks around page tags, so that each one becomes a separate chunk

def add_segment_marks_around_page_tags(Str):
    page_tag_start = '<page'
    if Str.find(page_tag_start) < 0:
        return "<page>||" + Str
    (i, n, OutStr) = (0, len(Str), '')
    while True:
        if i >= n:
            return OutStr
        if Str[i:i+len(page_tag_start)] == page_tag_start:
            end_of_tag = Str.find(">", i + len(page_tag_start))
            if end_of_tag < 0:
                lara_utils.print_and_flush('*** Error: open <page> tag: {Str[i:i+50]}')
                return ''
            elif i == 0:
                OutStr += f'{Str[i:end_of_tag + 1]}||'
                i = end_of_tag + 1
            else:
                OutStr += f'||{Str[i:end_of_tag + 1]}||'
                i = end_of_tag + 1
        else:
            OutStr += Str[i]
            i += 1
    return OutStr

# Str = '‘It isn’t,’ said#say# the Caterpillar.'
# Params = lara_config.read_lara_local_config_file('$LARA/Content/alice_in_wonderland/corpus/local_config.json')

## Process a single segment into a chunk. Again, we return a piece of trace as part of every output
## and stick them together
def string_to_text_chunk(String0, Params):
    try:
        if String0.startswith("<page"):
            return page_tag_string_to_chunk(String0)
        String05 = lara_parse_utils.remove_weird_characters(String0)
        String = maybe_convert_inverted_comments(String05, Params)
        if String == False:
            Error = f'*** Error: unable to internalise segment "{String0[:200]}"'
            lara_utils.print_and_flush(Error)
            Chunk = [ String0, '', [] ]
            return ( Chunk, [ Error ] )
        # If we have comments_by_default set, then we've already checked things are balanced
        if Params.comments_by_default != 'yes':
            ( CommentBracketsOkay, CommentWarning ) = lara_parse_utils.brackets_properly_used_in_string(String, '/*', '*/') 
            if not CommentBracketsOkay:
                Error = f'*** Error: unable to internalise segment "{String0[:200]}"'
                lara_utils.print_and_flush(CommentWarning)
                lara_utils.print_and_flush(Error)
                Chunk = [ String0, '', [] ]
                return ( Chunk, [ Error ] )
        ( MinimalClean, Trace1) = minimal_clean_lara_string(String, Params)
        ( AnnotatedWords, Trace4 ) = string_to_annotated_words(String)
        try_to_balance_html_font_tags_in_annotated_words(AnnotatedWords)
        Chunk = [ String, MinimalClean, AnnotatedWords ]
        #Trace = Trace1 + Trace2 + Trace3 + Trace4
        Trace = Trace1 + Trace4
        return ( Chunk, Trace )
    except Exception as e:
        Error = f'*** Error: unable to internalise segment "{String0[:200]}"'
        lara_utils.print_and_flush(Error)
        lara_utils.print_and_flush(str(e))
        Chunk = [ String0, '', [] ]
        return ( Chunk, [ Error ] )

# It sometimes happens that a font tag (<b> or <i>) can end up in the preceding word, which can mess up formatting
# Try to adjust this

def try_to_balance_html_font_tags_in_annotated_words(AnnotatedWords):
    ( I, N ) = ( 0, len(AnnotatedWords) - 2 )
    while True:
        if I > N:
            return
        ( OpenTag, CloseTag ) = ends_in_html_open_font_tag(AnnotatedWords[I][0])
        if OpenTag != False:
            if not lara_parse_utils.brackets_properly_used_in_string(AnnotatedWords[I+1][0], OpenTag, CloseTag)[0]:
                # Move the <i> or <b> from the end of this item to the beginning of the next one
                AnnotatedWords[I][0] = AnnotatedWords[I][0][:-1*len(OpenTag)]
                AnnotatedWords[I+1][0] = OpenTag + AnnotatedWords[I+1][0]
        I += 1

_html_font_tag_pairs = ( ( '<i>', '</i>' ),
                         ( '<b>', '</b>' )
                         )

def ends_in_html_open_font_tag(String):
    for ( OpenTag, CloseTag ) in _html_font_tag_pairs:
        if String.endswith(OpenTag):
            return ( OpenTag, CloseTag )
    return ( False, False )
             
## Convert page tag string into a chunk, returning trace

def page_tag_string_to_chunk(Str):
    ( ParsedTag, Trace ) = parse_page_tag(Str)
    return ( [ '*page_tag*', Str, ParsedTag ], Trace )

def parse_page_tag(Str):
    ( Index, N, OutDict ) = ( Str.find("<page") + len("<page"), Str.find(">") - 1, {} )
    while True:
        Index = lara_parse_utils.skip_spaces(Str, Index)
        if Index >= N:
            return ( OutDict, [] )
        else:
            ( Key, Value, Index1, Errors ) = parse_page_tag_component(Str, Index)
            if len(Errors) > 0:
                return ( OutDict, Errors )
            elif Key:
                OutDict[Key] = Value
                Index = Index1
            elif lara_parse_utils.skip_spaces(Str, Index1) >= N:
                return ( OutDict, [] )
            else:
                return ( OutDict, [ f'*** Error: unknown text in page tag: "{Str[Index:]}"' ] )
                

def parse_page_tag_component(Str, Index):
    for Key in ( 'css_file', 'name' ):
        if lara_parse_utils.substring_found_at_index(Str, Index, Key + '="'):
            StartOfValueIndex = Index + len(Key) + 2
            EndOfValueIndex = Str.find('"', StartOfValueIndex)
            if EndOfValueIndex >= StartOfValueIndex:
                return ( Key, Str[StartOfValueIndex:EndOfValueIndex], EndOfValueIndex + 1, [] )
            else:
                return ( False, False, False, ['*** Error: malformed page tag "<page {Str}/>"' ] )
    # We didn't find any key/value pair
    return ( False, False, False, [] )
            

## This is in case we've used the 'comments_by_default' option in the parameters,
## where everything is a comment by default and we mark non-comments as {{ ... }}
##
## If we're doing this in the context of a linguistics paper or similar, we can
## in addition put things between the comments inside a @ ... @, so that the {{ ... }}
## mark items to record.
def maybe_convert_inverted_comments(String, Params):
    if not Params.comments_by_default == 'yes':
        return String
    ( BracketsProperlyUsed, BracketsWarning ) = lara_parse_utils.brackets_properly_used_in_string(String, '{{', '}}')
    if not BracketsProperlyUsed:
        lara_utils.print_and_flush(BracketsWarning)
        return False
    if Params.linguistics_article_comments == 'yes':
        String1 = String.replace('{{', '*/@')
        String2 = String1.replace('}}', '@/*')
        return '/*' + String2 + '*/'
    else:
        String1 = String.replace('{{', '*/')
        String2 = String1.replace('}}', '/*')
        return '/*' + String2 + '*/'

## Process the semgment into the 'minimally cleaned' form, regularising whitespaces etc
## and stripping out the LARA markup
def minimal_clean_lara_string(String, Params):
    String1 = clean_line_breaks_and_separators(String, Params)
    ( String2, Trace2 ) = lara_parse_utils.remove_img_and_audio_tags(String1)
    ( String3, Trace3 ) = lara_parse_utils.remove_hashtag_comment_and_html_annotations(String2, Params)
    String4 = lara_forced_alignment.remove_prosodic_phrase_boundaries_from_string(String3)
    return ( lara_parse_utils.regularise_spaces(String4), Trace2 + Trace3 )

## Turn newlines into spaces and remove vertical bars (used to mark multi-words)
## except if we're using this for treetagging, in which case we replace vertical bars with spaces
## and also replace double hyphens with spaces
def clean_line_breaks_and_separators(String, Params):
    String1 = String.replace('\n', ' ')
    if Params.for_treetagger == 'no':
        return String1.replace('|', '')
    else:
        String2 = String1.replace('|', ' ')
        return String2.replace('--', ' ')

## Convert a string into a list of [SurfaceWord, Lemma] pairs
## Return a list of pairs plus a trace list
def string_to_annotated_words(StrIn):
    I = 0
    N = len(StrIn)
    OutList = []
    while True:
        if I >= N:
            return ( OutList, [] )
        else:
            Result = read_next_annotated_word(StrIn, I, N)
            if Result == 'finished':
                if N > I:
                    FillerStr = StrIn[I:]
##                    Filler = regularise_filler_string(Filler0)
##                    OutList += [ [ Filler, '' ] ]
                    FillerPairs = filler_string_to_pairs(FillerStr)
                    OutList += FillerPairs
                return ( OutList, [] )
            elif Result == 'error':
                return ( [], [ f'*** Error in string_to_annotated_words: incorrect tagging in "{StrIn}"' ] )
            else:
                ( FillerStr, NextAnnotatedWord, NextI ) = Result
                #Filler = regularise_filler_string(Filler0)
                FillerPairs = filler_string_to_pairs(FillerStr)
                #( NextWord, NextLemma ) = NextAnnotatedWord
                NextAnnotatedWordPairs = [] if NextAnnotatedWord == '' else [ NextAnnotatedWord ]
                I = NextI
##                if NextWord != '' and Filler != '' and Filler != '|':
##                    OutList += [ [ Filler, '' ], NextAnnotatedWord ]
##                elif NextWord != '':
##                    OutList += [ NextAnnotatedWord ]
##                elif NextWord == '' and Filler != '' and Filler != '|':
##                    OutList += [ [ Filler, '' ] ]
                OutList += FillerPairs + NextAnnotatedWordPairs

## Read one "annotated word" (word plus optional hashtag) from StrIn, starting at position I
## N is the length of StrIn.
## Return a [ Word, Lemma ] pair plus the new position in StrIn
def read_next_annotated_word(StrIn, I, N):
    I1 = next_word_initial_char_index(StrIn, I, N)
    if I1 >= I:
        Filler = StrIn[I:I1]
        ( Word, PhraseBracketed, I2 ) = read_possibly_phrase_bracketed_word(StrIn, I1, N)
        if I2 < 0:
            return 'error'
        else:
            Result = read_lemma_annotation(StrIn, I2, N, Word, PhraseBracketed)
            if Result == 'error':
                return 'error'
            else:
                ( Lemma, I3 ) = Result
                return ( Filler, [ Word, Lemma ], I3 )
    else:
        return 'finished'

## Remove intra-word separators, we no longer need to know about them
##def regularise_filler_string(Str):
##    return Str.replace('|', '')

def filler_string_to_pairs(FillerStr):
    FillerStr1 = FillerStr.replace('|', '')
    return filler_string_to_pairs1(FillerStr1)

## We want to break out img and audio tags as separate components.
def filler_string_to_pairs1(FillerStr):
    if FillerStr == '':
        return []
    elif not '<img' in FillerStr and not '<audio' in FillerStr and not '<video' in FillerStr:
        return [ [ FillerStr, '' ] ]
    elif FillerStr.startswith('<img') or FillerStr.startswith('<audio') or FillerStr.startswith('<video'):
        EndIndex = FillerStr.find('>')
        # There is no closing >, so we have a malformed tag. Return it anyway and handle it later.
        if EndIndex < 0:
            return [ [ FillerStr, '' ] ]
        else:
            NextIndex = EndIndex + len('>')
            return [ [ FillerStr[:NextIndex], '' ] ] + filler_string_to_pairs1(FillerStr[NextIndex:])
    else:
        NextIndex = next_img_or_audio_tag_index_in_string(FillerStr)
        # This should not happen but just in case.
        if NextIndex == False:
            return False
        else:
            return [ [ FillerStr[:NextIndex], '' ] ] + filler_string_to_pairs1(FillerStr[NextIndex:])

def next_img_or_audio_tag_index_in_string(Str):
    NextTagLocations = [ Str.find(Tag) for Tag in ( '<img', '<audio', '<video' ) ]
    RealNextTagLocations = [ Location for Location in NextTagLocations if Location >= 0 ]
    if len(RealNextTagLocations) == 0 :
        lara_utils.print_and_flush(f'*** Error: expected to find <img>, <audio> or <video> tag in {Str}')
        return False
    else:
        return min(RealNextTagLocations)

## Read the 'Word' part of an annotated word. This might by phrase-bracketed, i.e. enclosed in @ ... @
## Return a triple: ( <Word>, <whether or not it's phrase-bracketed>, <new position> )
## Note that we don't call clean_up_word_keeping_case_and_whitespace if we have a phrase-bracketed string
def read_possibly_phrase_bracketed_word(Str, I, N):
    if I >= N:
        return ( False, False, -1 )
    if Str[I] == '@':
        #NextPhraseBracketIndex = Str.find('@', I+1)
        NextPhraseBracketIndex = lara_parse_utils.find_next_non_escaped_at_sign_index(Str, I+1)
        if NextPhraseBracketIndex > I+1:
            Word = Str[I+1:NextPhraseBracketIndex]
            return ( Word, 'phrase_bracketed', NextPhraseBracketIndex+1 )
        else:
            return ( False, False, -1 )
    else:
        NextBoundaryIndex = next_word_separator_char(Str, I, N)
        if NextBoundaryIndex > I:
            Word0 = Str[I:NextBoundaryIndex]
            Word = clean_up_word_keeping_case_and_whitespace(Word0)
            return ( Word, 'not_phrase_bracketed', NextBoundaryIndex )
        else:
            return ( False, False, -1 )

## Now read the 'Lemma' part, which might be a hashtag or null
def read_lemma_annotation(Str, I, N, Word, PhraseBracketed):
    if I < N and Str[I] == '#':
        #NextHashtagIndex = Str.find('#', I+1)
        NextHashtagIndex = lara_parse_utils.find_next_non_escaped_hash_index(Str, I)
        if NextHashtagIndex > I+1:
##          In fact not at all clear why we should clean up a lemma tag that's inside #...# - remove this.
##            Lemma0 = Str[I+1:NextHashtagIndex]
##            ( Lemma, Trace ) = lara_parse_utils.remove_hashtag_comment_and_html_annotations(Lemma0, {})
##            if len(Trace) > 0:
##                return 'error'
##            else:
##                return ( clean_up_word_keeping_case(Lemma), NextHashtagIndex+1 )
            Lemma = Str[I+1:NextHashtagIndex]
            return ( Lemma, NextHashtagIndex+1 )
        else:
            return 'error'
    else:
        ( Word1, Trace ) = lara_parse_utils.remove_hashtag_comment_and_html_annotations(Word, {})
        if len(Trace) > 0:
            return ( '', I )
        elif PhraseBracketed == 'phrase_bracketed':
            return ( clean_up_word_keeping_punctuation(Word1), I )
        else:
            return ( clean_up_word(Word1), I )

## Look ahead in the string to find the next character that could start a word -
## not whitespace or punctuation mark, except for @ which has a special meaning as the start of a multiword.
## Skip HTML tags.
def next_word_initial_char_index(Str, Start, N):
    I = Start
    while True:
        if I >= N:
            return -1
        c1 = Str[I]
        if c1 == '<' and ( I == 0 or Str[I - 1] != '\\' ):
            NextCloseBracketPosition = Str.find(">", I+1)
            if NextCloseBracketPosition > I:
                I = NextCloseBracketPosition + len('>')
            else:
                return I
        elif lara_replace_chars.is_escaped_reserved_char_sequence(Str[I:I+2]):
            return I
        elif Str[I:I+2] == '/*':
            EndCommentIndex = Str.find('*/', I + len('/*'))
            I = EndCommentIndex + len('*/') if EndCommentIndex > 0 else -1
        elif c1.isspace() or c1 == '|' or lara_parse_utils.is_punctuation_char(c1) and c1 != '@':
            I += 1
        else:
            return I

## Look ahead to find the next separator: end of string, space, punctuation mark, hashtag, phrase bracket, vertical bar,
## double hyphen (= dash), hyphen followed by space or vertical bar, or start of comment.
##
## For French and Italian, we need to keep final apostrophes in words like d', l'. But we need to be careful not
## to do this in contexts where the ' is a quote mark.
def next_word_separator_char(Str, Start, N):
    I = Start
    while True:
        if I >= N:
            return N
        c1 = Str[I]
        c2 = Str[I+1:I+2]
        c12 = Str[I:I+2]
        c23 = Str[I+1:I+3]
        if lara_replace_chars.is_escaped_reserved_char_sequence(c12):
            I += 2
        elif c1.isspace() or is_splitting_punctuation_char(c1) \
             or c1 in "@#|" or c12 in ( '--', '- ', '-|', '/*' ) \
             or ( lara_parse_utils.is_apostrophe_char(c1) and not c2 in '#|' and \
                  ( c2.isspace() or is_splitting_punctuation_char(c2) or c23 in ( '--', '- ', '-|', '/*' ) ) ):
            return I
        else:
            I += 1

## Most punctuation marks can't occur word-internally, but hyphens, slashes and apostrophes can
def is_splitting_punctuation_char(Char):
    return lara_parse_utils.is_punctuation_char(Char) and \
           not Char in "-/" and \
           not lara_parse_utils.is_apostrophe_char(Char)

## Cleaning up the word in various ways
## For French and Italian, we need to keep final apostrophes in words like d', l'.
def clean_up_word_keeping_case_and_whitespace(Str):
    if lara_parse_utils.is_punctuation_string(Str):
        return Str
    else:
        return lara_parse_utils.remove_initial_and_final_punctuation_marks_but_not_final_hyphen_or_apostrophe(Str)
        #return lara_parse_utils.remove_initial_and_final_punctuation_marks_but_not_final_hyphen(Str)

def clean_up_word_keeping_punctuation(Str):
    return lara_parse_utils.regularise_spaces(Str.lower())

def clean_up_word(Str):
    if lara_parse_utils.is_punctuation_string(Str):
        return Str
    else:
        return lara_parse_utils.regularise_spaces(lara_parse_utils.remove_initial_and_final_punctuation_marks(Str.lower()))

def clean_up_word_keeping_case(Str):
    if lara_parse_utils.is_punctuation_string(Str):
        return Str
    else:
        return lara_parse_utils.regularise_spaces(lara_parse_utils.remove_initial_and_final_punctuation_marks(Str))

## Clean up a string so that it is a legal file name
    
cached_clean_up_word_for_files = {}

def clean_up_word_for_files(Word):
    global cached_clean_up_word_for_files
    if Word in cached_clean_up_word_for_files:
        return cached_clean_up_word_for_files[Word]
    else:
        Word1 = Word.lower()
        Word2 = lara_parse_utils.regularise_spaces(Word1)
        Word3 = lara_replace_chars.restore_reserved_chars(Word2)
        Word4 = replace_non_file_characters(Word3)
        #Word5 = f'capitalised_{Word4}' if len(Word) > 0 and Word[0].isupper() else Word4
        if len(Word) > 0 and all_letters_are_caps(Word):
            Word5 = f'all_capitalised_{Word4}'
        elif len(Word) > 0 and Word[0].isupper():
            Word5 = f'capitalised_{Word4}'
        else:
            Word5 = Word4
        WordOut = Word5[:50]
        cached_clean_up_word_for_files[Word] = WordOut
        return WordOut

def all_letters_are_caps(Word):
    for Letter in Word:
        if not Letter.isupper() and not lara_parse_utils.is_punctuation_char(Letter):
            return False
    return True
	
def replace_non_file_characters(Word):
    Out = ''
    for Char in Word:
        Replacement = replacement_for_non_file_char(Char)
        if Replacement:
            Out += Replacement
        else:
            Out += Char
    return Out

replacements_for_non_file_char = {"|": "",
                                  "‘": "_apostrophe",
                                  "’": "_apostrophe",
                                  "\'": "_apostrophe",
                                  "\"": "_quote",
                                  ",": "_comma",
                                  "،": "_comma",
                                  ".": "_period",
                                  "«": "_lquote",
                                  "“": "_lquote",
                                  "»": "_rquote",
                                  "”": "_rquote",
                                  "!": "_exclam",
                                  "?": "_question_mark",
                                  "؟": "_question_mark",
                                  "(": "_lparen",
                                  ")": "_rparen",
                                  "[": "_lsquare",
                                  "]": "_rsquare",
                                  "{": "_lcurly",
                                  "}": "_rcurly",
                                  "&": "_ampersand",
                                  "*": "_asterisk",
                                  ":": "_colon",
                                  ";": "_semicolon",
                                  "؛": "_semicolon",
                                  "/": "_slash",
                                  "\\": "_backslash",
                                  "—": "_dash",
                                  "–": "_dash",
                                  "•": "_bullet",
                                  "#": "_hash",
                                  "%": "_percent",
                                  "<": "_lt",
                                  ">": "_gt",
                                  "@": "_at",
                                  "œ": "oe"}

def replacement_for_non_file_char(Char):
    global replacements_for_non_file_char
    if Char in replacements_for_non_file_char:
        return replacements_for_non_file_char[Char]
    else:
        return False               

## Adding the tag as a fourth element in the chunk, also in the page info
def add_tags_to_chunks(PageOrientedSplitList, Tag):
    return [ ( add_tag_to_page_info(PageInfo, Tag), add_tags_to_chunks1(Units, Tag) )
               for ( PageInfo, Units ) in PageOrientedSplitList ]

def add_tag_to_page_info(PageInfo, Tag):
    PageInfo1 = copy.copy(PageInfo)
    PageInfo1['corpus'] = Tag
    return PageInfo1

def add_tags_to_chunks1(Units, Tag):
    return [ Unit + [ Tag ] for Unit in Units ]

## Check that the image and audio tags in the string are okay
def check_image_and_audio_tags_in_lara_string(InStr, Params):
    Params1 = lara_utils.add_corpus_id_tag_to_params(Params, 'local_files')
    Params1.local_files = 'yes'
    ( DummyStr, Trace1 ) = lara_images.process_img_tags_in_string(InStr, Params1)
    ( DummyStr, Trace2, ThisPageAudioFileUsed ) = lara_audio.process_audio_tags_in_string(InStr, '*no_clean_text*', Params1)
    return Trace1 + Trace2

## Produce messages for inconsistent tagging.
## Find [Surface, Tag, MinimallyCleaned] triples and then sort them appropriately
def inconsistent_tagging_messages(Units):
    Triples0 = [ (Surface.lower(), Tag, MinimallyCleaned) for
                 [Raw, MinimallyCleaned, Cleaned] in Units if
                 Raw != '*page_tag*' for
                 [Surface, Tag] in Cleaned if
                 not lara_parse_utils.is_punctuation_string(Tag) and not lara_mwe.is_mwe_lemma(Tag) ]
    Triples = sorted(Triples0, key=lambda x: x[0])
    #print(f'Triples: {Triples}')
    GroupedList = group_chunk_triples_by_word(Triples)
    #print(f'GroupledList: {GroupedList}')
    return inconsistent_tagging_messages1(GroupedList)

def group_chunk_triples_by_word(Triples):
    CurrentWord = '*no_word*'
    CurrentList = []
    GroupedList = []
    for [Word, Tag, MinimallyCleaned] in Triples:
        if CurrentWord == '*no_word*':
            CurrentWord = Word
            CurrentList = [[Tag, MinimallyCleaned]]
        elif Word == CurrentWord:
            CurrentList += [[Tag, MinimallyCleaned]]
        else:
            GroupedList += [[CurrentWord, CurrentList]]
            CurrentWord = Word
            CurrentList = [[Tag, MinimallyCleaned]]          
    if len(CurrentList) > 0:
        GroupedList += [[CurrentWord, CurrentList]]
    return GroupedList

## Get all the inconsistent tagging messages
def inconsistent_tagging_messages1(GroupledList):
    ListOfLists = [ inconsistent_tagging_message(Word, TagSegmentPairs) for [Word, TagSegmentPairs] in GroupledList if
                    inconsistent_tags_in_list(TagSegmentPairs) ]
    return [ Element for List in ListOfLists for Element in List ]

## It's an inconsistent tag if there are multiple tags for the word
def inconsistent_tags_in_list(TagSegmentPairs):
    Tags = [ TagSegmentPair[0] for TagSegmentPair in TagSegmentPairs ]
    return len(lara_utils.remove_duplicates(Tags)) > 1

## Generates the message
def inconsistent_tagging_message(Word, TagSegmentPairs):
    Tags = [ TagSegmentPair[0] for TagSegmentPair in TagSegmentPairs ]
    Intro = f'\n*** Warning: Inconsistent tags for "{Word}":'
    Examples = [ f'{Tag:<20}{Segment}' for [ Tag, Segment ] in TagSegmentPairs ]
    Examples.sort()
    return [ Intro ] + Examples

## Returns a list of lines giving stats for the string, including longest segments
## (these are useful for spotting when you've missed a separator)
def print_split_file_statistics(PageOrientedSplitList):
    Units = [ Unit for ( PageInfo, PageUnits ) in PageOrientedSplitList for Unit in PageUnits ]
    Statistics = get_statistics_for_page_oriented_split_list(PageOrientedSplitList)
    if not Statistics:
        return [ 'Error: unable to extract statistics from split file' ]
    NPages = Statistics['pages']
    NSegments = Statistics['segments']
    NWords = Statistics['words']
    NWordsIncludingComments = Statistics['words_including_comments']
    NUniqueWords = Statistics['unique_words']
    PagesMessage = f'--- {NPages} pages'
    SegmentsMessage = f'--- {NSegments} segments'
    WordsMessage = f'--- {NWords} words'
    WordsMessageNWordsIncludingComments = f'--- {NWordsIncludingComments} words including comments'
    UniqueWordsMessage = f'--- {NUniqueWords} different tags'    
    LongestSegments = longest_segments(Units)
    
    AllMessages = ['\n' + PagesMessage, SegmentsMessage, WordsMessage, WordsMessageNWordsIncludingComments, UniqueWordsMessage] + \
                  ['\nLongest segments:'] + LongestSegments + [ '\n' ]
    lara_utils.print_and_flush('\n'.join(AllMessages))
    return AllMessages

def get_statistics_for_page_oriented_split_list(PageOrientedSplitList):
    try:
        Units = [ Unit for ( PageInfo, PageUnits ) in PageOrientedSplitList for Unit in PageUnits ]
        return {
            'pages': count_pages_in_split_file_contents(PageOrientedSplitList),
            'segments': count_segments_in_split_file_contents(Units),
            'words': count_words_in_split_file_contents(Units),
            'words_including_comments': count_words_including_comments_in_split_file_contents(Units),
            'unique_words': count_unique_tags_in_split_file_contents(Units)
            }
    except:
        return False        

def count_pages_in_split_file_contents(PageOrientedSplitList):
    return len(PageOrientedSplitList)

def count_segments_in_split_file_contents(Units):
    return len(Units)

def count_words_in_split_file_contents(Units):
    return len([ WordTagPair[0] for Chunk in Units for WordTagPair in Chunk[2]
                 if not lara_parse_utils.is_punctuation_string(WordTagPair[0]) ])

def count_words_including_comments_in_split_file_contents(Units):
    return sum([ len(Chunk[1].split()) for Chunk in Units ])

def count_unique_tags_in_split_file_contents(Units):
    Tags = [ WordTagPair[1] for Chunk in Units for WordTagPair in Chunk[2]
             if not lara_parse_utils.is_punctuation_string(WordTagPair[0]) ]
    return len(lara_utils.remove_duplicates(Tags))

def longest_segments(Units):
    SegmentsAndLengths = [ [ Chunk[1], count_non_punctuation_word_items_in_cleaned(Chunk[2]) ] for Chunk in Units ]
    SortedSegmentsAndLengths = sorted(SegmentsAndLengths, key=lambda x: x[1], reverse=True)
    return [ Item[0] for Item in SortedSegmentsAndLengths ][:5]

def count_non_punctuation_word_items_in_cleaned(Cleaned):
    return len([ Item for Item in Cleaned if not lara_parse_utils.is_punctuation_string(Item[0]) ])

def print_stored_trace_output_to_file(Trace, TaggingFeedbackFile):
    lara_utils.write_lara_text_file('\n'.join(Trace), TaggingFeedbackFile)

    

