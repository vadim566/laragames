
import lara_generic_tagging
import lara_split_and_clean
import lara_utils
import lara_parse_utils
import lara_postags
import lara_audio

# Making blank lemma spreadsheets

def make_lemma_dictionary_file(UntaggedFile, LemmaFile, Params):
    CurrentSpreadsheetLines = read_and_store_current_lemma_dictionary(Params)
    if CurrentSpreadsheetLines == False:
        return False
    InList = [ Chunk for ( PageInfo, Chunks ) in lara_split_and_clean.clean_lara_file_main(UntaggedFile, Params)[0] for Chunk in Chunks ]
    Words = lara_audio.get_words_from_split_file_contents(InList)
    OutList = make_lemma_dictionary_file_contents(CurrentSpreadsheetLines, Words)
    if not OutList:
        return False
    NEmpty = len([ Line for Line in OutList if Line[1] == '' ])    
    NFilled = len(OutList) - NEmpty
    Header = ['Word', 'Lemma', 'POS']
    write_lemma_dictionary_file(Header, OutList, LemmaFile)
    lara_utils.print_and_flush(f'--- Written lemma lexicon spreadsheet ({NFilled} filled entries, {NEmpty} blank entries) {LemmaFile}')
    return True

def make_lemma_dictionary_file_contents(CurrentSpreadsheetLines, Words):
    LinesFromWords = [ (Word, '', '') for Word in Words if not Word in lemmas_for_surface_words ]
    CurrentSpreadsheetLinesAsTuples = [ tuple(Item) for Item in CurrentSpreadsheetLines ]
    AllEntries = lara_utils.remove_duplicates( CurrentSpreadsheetLinesAsTuples + LinesFromWords )
    return sorted(AllEntries, key=lambda x: x[0])

def write_lemma_dictionary_file(Header, OutList, LemmaFile):
    lara_utils.write_lara_csv([ Header ] + OutList, LemmaFile)

def read_and_store_current_lemma_dictionary(Params):
    (File, SpreadsheetLines) = read_current_lemma_dictionary(Params)
    if SpreadsheetLines:
        store_lemma_lexicon_spreadsheet_data(SpreadsheetLines)
        lara_utils.print_and_flush(f'--- Loaded lemma lexicon spreadsheet {File}')
        return SpreadsheetLines
    else:
        return False

def read_current_lemma_dictionary(Params):
    if Params.lemma_dictionary_spreadsheet == '':
        lara_utils.print_and_flush(f'*** Error: unable to do lemma lexicon processing, lemma lexicon not found in config')
        return (False, False)
    File = Params.lemma_dictionary_spreadsheet
    if lara_utils.file_exists(File):
        DataFromCSV = lara_utils.read_lara_csv(File)
        if DataFromCSV and len(DataFromCSV) > 0:
            return (File, DataFromCSV[1:])
        else:
            lara_utils.print_and_flush(f'*** Error: unable to read lemma lexicon spreadsheet {File}')
            return (File, False)
    else:
        lara_utils.print_and_flush(f'*** Warning: lemma lexicon spreadsheet not found: {File}')
        return (File, [])
    
lemmas_for_surface_words = {}

def store_lemma_lexicon_spreadsheet_data(Records):
    global lemmas_for_surface_words
    lemmas_for_surface_words = {}
    for Record in Records:
        # Ignore empty lines and lines where the lemma hasn't been filled in.
        if len(Record) >= 2 and \
           not Record[0].isspace() and not Record[0] == '' and \
           not Record[1].isspace() and not Record[1].isspace() == '':
            SurfaceWord = Record[0]
            Lemma = SurfaceWord if Record[1] == '*' else Record[1]
            POS = Record[2] if len(Record) >= 3 and not Record[2].isspace() else ''
            SurfaceWordComponents = [ make_word_canonical(Word) for Word in SurfaceWord.split() ]
            ( FirstSurfaceWord, RestSurfaceWords ) = ( SurfaceWordComponents[0], SurfaceWordComponents[1:] )
            Entry = lemmas_for_surface_words[FirstSurfaceWord] if FirstSurfaceWord in lemmas_for_surface_words else []
            Entry += [( RestSurfaceWords, Lemma, POS )]
            lemmas_for_surface_words[FirstSurfaceWord] = Entry

# ------------------------------------------------------------

## Do minimal tagging, add the tags.
def minimal_tag_lara_file_main(InFile, Params, OutFile):
    if not read_and_store_current_lemma_dictionary(Params):
        lara_utils.print_and_flush('*** Error: unable to load lemma dictionary')
        return False
    Triples = minimal_tag_triples_for_file(InFile, Params)
    if Triples:
        if annotate_lara_file_from_minimal_tagger_output(InFile, Triples, OutFile, Params):
            lara_utils.print_and_flush(f'--- Call to minimal tagging successfully completed')
        else:
            lara_utils.print_and_flush('*** Error: unable to do minimal tagging')
            return False
    else:
        lara_utils.print_and_flush(f'*** Error: unable to get minimal tag triples (lang = {Language})')
        return False

def minimal_tag_triples_for_file(File, Params):
    ( PageOrientedSplitList, Trace ) = lara_split_and_clean.clean_lara_file_main(File, Params)
    SurfaceWords = [ Pair[0] for ( PageInfo, Chunks ) in PageOrientedSplitList for Chunk in Chunks for Pair in Chunk[2] ]
    return minimal_tag_triples_for_surface_words(SurfaceWords)

##def tag_triple_for_surface_word(Word):
##    CanonicalWord = lara_audio.make_word_canonical_for_word_recording(Word)
##    if CanonicalWord in lemmas_for_surface_words and not lemmas_for_surface_words[CanonicalWord][0] in ( '', '-' ):
##        ( Lemma, POS ) = lemmas_for_surface_words[CanonicalWord]
##    else:
##        ( Lemma, POS ) = ( CanonicalWord, '' )
##    return ( Word, POS, Lemma)

def minimal_tag_triples_for_surface_words(SurfaceWords):
    ( I, N, Out ) = (0, len(SurfaceWords), [] )
    while True:
        if I >= N:
            return Out
        Current = SurfaceWords[I]
        CurrentCanonical = make_word_canonical(Current)
        if CurrentCanonical in lemmas_for_surface_words:
            Matches = [ match_surface_words(Item, SurfaceWords, Current, I+1) for Item in lemmas_for_surface_words[CurrentCanonical] ]
            Matches = lara_utils.non_false_members(Matches)
            LexiconMatch = best_match(Matches)
            BestMatch = LexiconMatch if LexiconMatch else ( [ Current ], '', make_word_canonical(Current) )
        else:
            BestMatch = ( [ Current ], '', make_word_canonical(Current) )
        ( Matched, POS, Lemma ) = BestMatch
        Out += [ BestMatch ]
        I += len(Matched)

def match_surface_words(MinimalTagItem, SurfaceWords, FirstWord, I):
    ( RestSurfaceWords, Lemma, POS ) = MinimalTagItem
    ( N, Matched ) = ( len(SurfaceWords), [FirstWord] )
    for Word in RestSurfaceWords:
        if I>= N or Word != make_word_canonical(SurfaceWords[I]):
            return False
        Matched += [ SurfaceWords[I] ]
        I += 1
    return ( Matched, POS, Lemma )

def best_match(Matches):
    return sorted(Matches, key=lambda x: len(x[0]), reverse=True)[0] if len(Matches) > 0 else False

def annotate_lara_file_from_minimal_tagger_output(LARAFile, TagTuples, TaggedFile, Params):
    InString = lara_utils.read_lara_text_file(LARAFile)
    RawOutString = lara_generic_tagging.annotate_lara_string_from_tagging_triples(TagTuples, InString, Params)
    if not RawOutString:
        lara_utils.print_and_flush(f'*** Error: unable to update LARA file from minimal tagging output')
        return False
    OutString = lara_generic_tagging.remove_hashtags_and_separators_inside_multiwords(RawOutString)
    if OutString:
        lara_utils.write_lara_text_file(OutString, TaggedFile)
        return True
    else:
        lara_utils.print_and_flush(f'*** Error: unable to update LARA file from minimal tagging output')
        return False

def make_word_canonical(Word):
    return lara_audio.make_word_canonical_for_word_recording(Word)
