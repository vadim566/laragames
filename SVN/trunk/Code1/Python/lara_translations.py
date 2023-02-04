
import lara
import lara_split_and_clean
import lara_audio
import lara_config
import lara_mwe
import lara_chinese
import lara_utils
import lara_replace_chars
import lara_parse_utils
import copy

def init_translation_tables(Params):
    global translations_for_segments, translations_for_word_tokens
    ( translations_for_segments, translations_for_word_tokens ) = ( {}, {} )
    lara_chinese.maybe_add_hanzi_to_pinyin_dict_to_params(Params)

def count_translations(Params):
    return { 'segments': count_segment_translations(Params),
             'words': count_word_translations(Params)
             }

def make_translation_spreadsheet(SplitFile, Spreadsheet, Params):
    if Params.word_translations_on == 'surface_word_token':
        make_translation_spreadsheet_tokens(SplitFile, Spreadsheet, Params)
    else:
        make_translation_spreadsheet_types(SplitFile, Spreadsheet, Params)

def make_note_spreadsheet(SplitFile, Spreadsheet, Params):
    Params1 = copy.copy(Params)
    Params1.word_translations_on = 'lemma_notes'
    make_translation_spreadsheet_types(SplitFile, Spreadsheet, Params1)

def make_image_dict_spreadsheet(SplitFile, Spreadsheet, Params):
    Params1 = copy.copy(Params)
    Params1.word_translations_on = 'lemma_image_dict'
    make_translation_spreadsheet_types(SplitFile, Spreadsheet, Params1)

def make_translation_spreadsheet_tokens(SplitFile, Spreadsheet, Params):
    global translations_for_segments, translations_for_word_tokens, translations_for_words
    ( translations_for_segments, translations_for_word_tokens, translations_for_words ) = ( {}, {}, {} )
    if not process_segment_spreadsheet_files('local_files', all_segment_translation_spreadsheets(Params)):
        return False
    if Params.ignore_existing_word_token_data != 'yes' and \
       not process_word_token_spreadsheet_files('local_files', all_word_token_translation_spreadsheets(Params)):
        return False
    # We are going to load the word_translation_surface spreadsheet, if there is one, to get type translations for words
    Params1 = copy.copy(Params)
    Params1.word_translations_on = 'surface_word_type'
    if not process_word_spreadsheet_files('local_files', all_word_translation_surface_spreadsheets(Params1), Params1):
        return False
    #InList = [ Chunk for ( PageInfo, Chunks ) in lara_split_and_clean.read_split_file(SplitFile, Params1) for Chunk in Chunks ]
    InList = [ Chunk for ( PageInfo, Chunks ) in lara_mwe.read_split_file_applying_mwes_if_possible(Params1) for Chunk in Chunks ]
    Triples = [ token_spreadsheet_triple_for_chunk(Chunk, Params1) for Chunk in InList
                if not (Chunk[1]).isspace() and not Chunk[1] == '' ]
    NMissing = missing_translations_in_tokens_triples(Triples)
    ( CSVLines, NFilled, NEmpty ) = token_triples_to_csv_lines(Triples, Params1)
    lara_utils.write_lara_csv(CSVLines, Spreadsheet)
    JSONFile = lara_utils.change_extension(Spreadsheet, 'json')
    word_translation_csv_to_json(Spreadsheet, JSONFile)
    lara_utils.print_and_flush(f'--- Written word token translation files (CSV: {Spreadsheet}, JSON: {JSONFile}')
    lara_utils.print_and_flush(f'--- ({NFilled} filled entries, {NEmpty} empty entries, {NMissing} missing segment translations )')
    return True

def tmp_word_token_spreadsheet_to_tmp_word_type_spreadsheet(Spreadsheet):
    ( BaseName, Extension ) = lara_utils.file_to_base_file_and_extension(Spreadsheet)
    return f'{BaseName}_surface_type.{Extension}'

# We use translation_spreadsheet for all word translation spreadsheets, irrespective of type
def all_word_token_translation_spreadsheets(Params):
    OwnTranslationSpreadsheets = [] if Params.translation_spreadsheet_tokens == '' else [ Params.translation_spreadsheet_tokens ]
    return OwnTranslationSpreadsheets

def process_word_token_spreadsheet_files(CorpusId, Files):
    for File in Files:
        if not process_word_token_spreadsheet_file(CorpusId, File):
            return False
    return True

def store_downloaded_word_token_translations(CorpusId, File):
    process_word_token_spreadsheet_file(CorpusId, File)
            
def process_word_token_spreadsheet_file(CorpusId, File):
    Records = read_word_token_spreadsheet_file(File, 'remove_mwe_markings')
    if Records != False:
        store_word_token_spreadsheet_data(CorpusId, Records)
        lara_utils.print_and_flush(f'--- Loaded word token translation spreadsheet ({len(Records)} records) {File}')
        return True
    else:
        return False

def read_word_token_spreadsheet_file(WordCSV, RemoveMWEMarkings):
    if not lara_utils.file_exists(WordCSV):
        lara_utils.print_and_flush(f'*** Warning: translation spreadsheet not found {WordCSV}')
        return []
    DataFromCSV = lara_utils.read_lara_csv(WordCSV)
    if not DataFromCSV:
        lara_utils.print_and_flush(f'*** Error: unable to read translation spreadsheet {WordCSV}')
        return False
    Records = DataFromCSV
    Records1 = group_word_token_spreadsheet_lines_into_records(Records, RemoveMWEMarkings)
    if not Records1:
        lara_utils.print_and_flush(f'*** Error: unable to read translation spreadsheet {WordCSV}')
    return Records1

# The format of the word token spreadsheet is a list of groups of four lines, as follows:
#
# Separator line (list of '--' entries)
# Source line
# Target line
# Reference target line (only for documentation)
#
# We convert this into a list of ( Source line, Target line ) pairs
def group_word_token_spreadsheet_lines_into_records(Records, RemoveMWEMarkings):
    ( N, OutRecords, I ) = ( len(Records), [], -1 )
    while True:
        if I >= N:
            return OutRecords
        if I == -1 and N > 0 and not separator_line(Records[0]) or \
           I >= 0 and separator_line(Records[I]):
            if I + 3 >= N:
                return OutRecords
            else:
                SourceLine = remove_trailing_nulls(Records[I + 1]) if RemoveMWEMarkings == 'dont_remove_mwe_markings' else \
                             remove_mwe_markings_in_list(remove_trailing_nulls(Records[I + 1]))                  
                OutRecords += [ ( SourceLine,
                                  remove_trailing_nulls(Records[I + 2]),
                                  remove_trailing_nulls(Records[I + 3])
                                  ) ]
                I += 4
        else:
            I += 1

_mwe_prefix = 'mwe__'

def remove_mwe_markings_in_list(List):
    if not isinstance(List, ( list, tuple )):
        lara_utils.print_and_flush(f'*** Error: bad call: remove_mwe_markings_in_list({List})')
        return False
    else:
        return [ remove_mwe_marking(X) for X in List ]

def remove_mwe_marking(Str):
    if not isinstance(Str, ( str )):
        lara_utils.print_and_flush(f'*** Error: bad call: remove_mwe_marking({Str})')
        return False
    elif Str.startswith(_mwe_prefix):
        return Str[len(_mwe_prefix):]
    else:
        return Str

def add_mwe_marking(Str):
    if not isinstance(Str, ( str )):
        lara_utils.print_and_flush(f'*** Error: bad call: add_mwe_marking({Str})')
        return False
    else:
        return _mwe_prefix + Str

def remove_trailing_nulls(List):
    return List[:start_index_of_trailing_nulls(List)]

def start_index_of_trailing_nulls(List):
    N = len(List)
    for I in range(0, N):
        if all_nulls(List[I:N]):
            return(I)
    return N

def all_nulls(List):
    for X in List:
        if X != '':
            return False
    return True           

# Separator line is just '--'
def separator_line(Record):
    for Item in Record:
        if Item != '--':
            return False
    return True

def store_word_token_spreadsheet_data(CorpusId, Records):
    global translations_for_word_tokens
    SubDict = translations_for_word_tokens[CorpusId] if CorpusId in translations_for_word_tokens else {}
    for ( Key0, Value, ReferenceTranslation ) in Records:
        if not all_null_line(Value):
            Key = tuple(Key0)
            SubDict[Key] = Value
    translations_for_word_tokens[CorpusId] = SubDict

def all_null_line(Line):
    for X in Line:
        if X != '' and not X.isspace():
            return False
    return True

def missing_translations_in_tokens_triples(Triples):
    Missing = 0
    for ( SourceSegment, SourceSurfaceWords, TargetSurfaceWords ) in Triples:
        if TargetSurfaceWords == []:
            #lara_utils.print_and_flush(f'*** Warning: no segment translation for "{SourceSegment}"')
            Missing += 1
    return Missing

def token_triples_to_csv_lines(Triples, Params):
    ( Lines, NFilled, NEmpty ) = ( [], 0, 0 )
    for ( SourceSegment, SourcePairs, TargetSurfaceWords ) in Triples:
        SourceSurfaceWords = [ Surface for ( Surface, Lemma ) in SourcePairs ]
        TranslationForSourceSurfaceWords = word_token_translation_or_null(SourceSurfaceWords, 'local_files')
        WordsAndIndices = lara_mwe.pairs_to_words_and_indices(SourcePairs, Params)
        IndexSourcePairs = { Index: maybe_add_mwe_marking(Indices, SourceSurfaceWords[Index]) for
                             ( Word, Indices, Lemma, MWE ) in WordsAndIndices for Index in Indices }
        SourceSurfaceWords1 = [ IndexSourcePairs[Index] for Index in range(0, len(SourceSurfaceWords)) ]
        if TranslationForSourceSurfaceWords == '':
            NEmpty += 1
            LanguageId = lara_utils.get_l1_from_params(Params)
            IndexTranslationPairs = { Index: type_translation_for_word_or_null(Word, LanguageId, Params) for
                                      ( Word, Indices, Lemma, MWE ) in WordsAndIndices for Index in Indices }
            TranslationForSourceSurfaceWords1 = [ IndexTranslationPairs[Index] for Index in range(0, len(SourceSurfaceWords)) ]
        else:
            NFilled += 1
            TranslationForSourceSurfaceWords1 = TranslationForSourceSurfaceWords
            warn_if_mwes_inconsistent_with_translations(WordsAndIndices, SourceSurfaceWords, TranslationForSourceSurfaceWords)
        Lines += [ 'separator_line', SourceSurfaceWords1, TranslationForSourceSurfaceWords1, TargetSurfaceWords ]
    Lines += [ 'separator_line' ]
    return ( expand_token_triple_lines(Lines), NFilled, NEmpty )

def warn_if_mwes_inconsistent_with_translations(WordsAndIndices, SourceSurfaceWords, TranslationForSourceSurfaceWords):
    for ( Word, Indices, Lemma, MWE ) in WordsAndIndices:
        Translations = [ TranslationForSourceSurfaceWords[I] for I in Indices ]
        if len(lara_utils.remove_duplicates(Translations)) > 1:
            lara_utils.print_and_flush(f'*** Warning: components of MWE "{Word}" translated differently ({Translations}) in')
            print_parallel_source_and_target(SourceSurfaceWords, TranslationForSourceSurfaceWords)

def print_parallel_source_and_target(Source, Target):
    ( Source1, Target1 ) = pad_words_in_lists_to_same_length(Source, Target)
    lara_utils.print_and_flush(f"Source: {'|'.join(Source1)}")
    lara_utils.print_and_flush(f"Target: {'|'.join(Target1)}")

def pad_words_in_lists_to_same_length(List1, List2):
    if len(List1) != len(List2):
        lara_utils.print_and_flush(f'*** Error: bad call pad_words_in_lists_to_same_length({List1}, {List2})')
        lara_utils.print_and_flush(f'*** Error: lists have different lengths, {len(List1)} and {len(List2)}')
        return False
    ( OutList1, OutList2 ) = ( [], [] )
    for I in range(0, len(List1)):
        ( X1, X2 ) = pad_words_to_same_length(List1[I], List2[I])
        OutList1 += [ X1 ]
        OutList2 += [ X2 ]
    return ( OutList1, OutList2 )

def pad_words_to_same_length(Str1, Str2):
    ( L1, L2 ) = ( len(Str1), len(Str2) )
    return ( Str1, Str2 + ' ' * ( L1 - L2 ) ) if L1 > L2 else ( Str1 + ' ' * ( L2 - L1 ), Str2 )
    

def maybe_add_mwe_marking(Indices, Str):
    return add_mwe_marking(Str) if len(Indices) > 1 else Str

def expand_token_triple_lines(Lines):
    MaxLineLength = max([ len(Line) for Line in Lines if isinstance(Line, list) ]) if Lines != [] else 0
    SeparatorLine = MaxLineLength * [ '--' ]
    EmptyLine = MaxLineLength * [ '' ]
    return [ expand_token_triple_line(Line, SeparatorLine, EmptyLine, MaxLineLength ) for Line in Lines ]

def expand_token_triple_line(Line, SeparatorLine, EmptyLine, MaxLineLength ):
    if Line == 'separator_line':
        return SeparatorLine
    if Line == 'empty_line':
        return EmptyLine
    if isinstance(Line, list):
        return Line + ( MaxLineLength - len(Line) ) * [ '' ]
    lara_utils.print_and_flush(f'*** Error: unknown line when creating token transallation file: "{Line}"')
    return False

def word_token_translation_or_null(SourceSurfaceWords, CorpusId):
    global translations_for_word_tokens
    SubDict = translations_for_word_tokens[CorpusId] if CorpusId in translations_for_word_tokens else {}
    SourceSurfaceWordsTuple = tuple(SourceSurfaceWords)
    return SubDict[SourceSurfaceWordsTuple] if SourceSurfaceWordsTuple in SubDict else ''

def maybe_add_word_type_or_token_translations_to_params(Params, AnnotatedWords):
    if Params.word_translations_on == 'surface_word_type':
        add_word_type_translations_to_params(Params, AnnotatedWords)
    elif Params.word_translations_on == 'surface_word_token':
        add_word_token_translations_to_params(Params, AnnotatedWords)

def add_word_type_translations_to_params(Params, AnnotatedWords):
    # List of <Word, IndexList> pairs, where IndexList are the indices of the words associated with the possible MWE Word
    WordsAndIndices = lara_mwe.pairs_to_words_and_indices(AnnotatedWords, Params)
    LanguageId = lara_utils.get_l1_from_params(Params)
    IndexTranslationPairs = { Index: type_translation_for_word_or_null(Word, LanguageId, Params) for
                              ( Word, Indices, Lemma, MWE ) in WordsAndIndices for Index in Indices }
    Params.word_type_translations = IndexTranslationPairs
    #lara_utils.print_and_flush(f'{AnnotatedWords} -> Params.word_type_translations = {IndexTranslationPairs}')

def add_word_token_translations_to_params(Params, AnnotatedWords):
    CorpusId = lara_utils.get_corpus_id_from_params(Params)
    SourceSurfaceWords = [ regularise_word_for_word_token_translation(Pair[0]) for Pair in AnnotatedWords ]
    TargetSurfaceWords = word_token_translation_or_null(SourceSurfaceWords, CorpusId)
    if TargetSurfaceWords != '' and len(SourceSurfaceWords) == len(TargetSurfaceWords):
        Params.word_token_translations = TargetSurfaceWords
    elif len(SourceSurfaceWords) == 0:
        Params.word_token_translations = []
    else:
        Params.word_token_translations = [ '' for Word in TargetSurfaceWords ]
        if Params.translation_mouseover == 'yes':
            lara_utils.print_and_flush(f'*** Warning: no token translation found for {SourceSurfaceWords}')

def token_spreadsheet_triple_for_chunk(Chunk, Params):
    SourceSegment = Chunk[1]
    #SourcePairs = [ Pair for Pair in Chunk[2] if Pair[1] != '' ]
    #SourceSurfaceWords = [ regularise_word_for_word_token_translation(Pair[0]) for Pair in SourcePairs ]
    SourcePairs = [ ( regularise_word_for_word_token_translation(Surface), Lemma )
                    for ( Surface, Lemma ) in Chunk[2] if Lemma != '' ]
    TargetSegment = translation_for_segment_or_null(SourceSegment, 'local_files')
    TargetSurfaceWords = string_to_surface_words(TargetSegment, Params)
    #if len(TargetSurfaceWords) == 0:
    #    lara_utils.print_and_flush(f'*** Warning: null segment translation for "{SourceSegment}", "{TargetSegment}"')
    return ( SourceSegment, SourcePairs, TargetSurfaceWords )

def string_to_surface_words(Segment, Params):
    ( Chunk, Trace ) = lara_split_and_clean.string_to_text_chunk(Segment, Params)
    if len(Trace) > 0:
        lara_utils.print_and_flush(f'*** Warning: odd segment translation "{Segment}"')
        return Segment.split()
    else:
        return [ Pair[0] for Pair in Chunk[2] if Pair[1] != '' ]

def make_translation_spreadsheet_types(SplitFile, Spreadsheet, Params):
    global translations_for_words
    translations_for_words = {}
    if Params.word_translations_on == 'lemma':
        TranslationFilesToLoad = all_word_translation_spreadsheets(Params)
    elif Params.word_translations_on == 'lemma_notes':
        TranslationFilesToLoad = all_notes_spreadsheets(Params)
    elif Params.word_translations_on == 'lemma_image_dict':
        TranslationFilesToLoad = all_image_dict_spreadsheets(Params)
    else:
        TranslationFilesToLoad = all_word_translation_surface_spreadsheets(Params)
    if not process_word_spreadsheet_files('local_files', TranslationFilesToLoad, Params):
        return False
    make_translation_spreadsheet_types1(SplitFile, Spreadsheet, Params)

def make_translation_spreadsheet_types1(SplitFile, Spreadsheet, Params):
    #InList = [ Chunk for ( PageInfo, Chunks ) in lara_split_and_clean.read_split_file(SplitFile, Params) for Chunk in Chunks ]
    InList = [ Chunk for ( PageInfo, Chunks ) in lara_mwe.read_split_file_applying_mwes_if_possible(Params) for Chunk in Chunks ]
    # Assoc should associate each surface word with a structure of the form ( Freq, [ (Score1, Example1), ... ] )
    Assoc = lara.collect_word_page_info_simple(InList, Params)
    Tuples = [ [ Word,
                 translation_for_word_or_null(Word, 'local_files', Params),
                 Assoc[Word][0],
                 [ Example for ( Score, Example ) in Assoc[Word][1] ]
                 ]
               for Word in Assoc ]
    make_translation_spreadsheet_types_csv(Tuples, Spreadsheet, Params)
    make_translation_spreadsheet_types_json(Tuples, lara_utils.change_extension(Spreadsheet, 'json'), Params)

def make_translation_spreadsheet_types_json(Tuples, JSONFile, Params):
    #TuplesSorted = sorted(Tuples, key=lambda x: x[0])
    TuplesSorted = sorted(Tuples, key=lambda x: x[2], reverse=True)
    lara_utils.write_json_to_file(TuplesSorted, JSONFile)
    NEmpty = count_empty_translations_in_json_vocab_spreadsheet_list(Tuples)
    NFilled = len(Tuples) - NEmpty
    lara_utils.print_and_flush(f'--- Written JSON word translation file ({NFilled} filled entries, {NEmpty} blank entries) {JSONFile}')

def make_translation_spreadsheet_types_csv(Tuples, Spreadsheet, Params):
    #AllCurrent = all_translation_words_in_segments(InList, Params)
    AllCurrent = [ Tuple[0] for Tuple in Tuples ]
    CurrentPairs = [ [Word, 'current'] for Word in AllCurrent ]
    # Collect the current translations loaded by process_word_spreadsheet_files if there are any
    translations_dict = get_word_translations_dict(Params)
    if 'local_files' in translations_dict:
        NonCurrentPairs = [ [Word, ''] for Word in translations_dict['local_files'] if not Word in AllCurrent ]
    else:
        NonCurrentPairs = []
    AllPairs = CurrentPairs + NonCurrentPairs
    #lara_utils.print_and_flush(f'AllPairs = {AllPairs}')
    Triples0 = [ (lara_replace_chars.restore_reserved_chars(Word), translation_for_word_or_null(Word, 'local_files', Params), Current) \
                 for ( Word, Current ) in AllPairs ]
    Triples = sorted(lara_utils.remove_duplicates(Triples0), key=lambda x: x[0])
    Header = ['Head word', 'Translation', 'CurrentDomain']
    #lara_utils.write_lara_csv([ Header ] + Triples, Spreadsheet)
    write_translation_csv(Header, Triples, Spreadsheet)
    NEmpty = count_empty_translations_in_vocab_spreadsheet_list(Triples)
    NFilled = len(Triples) - NEmpty
    lara_utils.print_and_flush(f'--- Written word spreadsheet ({NFilled} filled entries, {NEmpty} blank entries) {Spreadsheet}')

def count_word_translations(Params):
    if Params.word_translations_on == 'surface_word_token':
        return count_word_token_translations(Params)
    global translations_for_words
    translations_for_words = {}
    if not process_word_spreadsheet_files('local_files', all_word_translation_spreadsheets(Params), Params):
        ( NEmpty, NFilled ) = ( 0, 0 )
    #InList = [ Chunk for ( PageInfo, Chunks ) in lara_split_and_clean.read_split_file(Params.split_file, Params) for Chunk in Chunks ]
    InList = [ Chunk for ( PageInfo, Chunks ) in lara_mwe.read_split_file_applying_mwes_if_possible(Params) for Chunk in Chunks ]
    AllCurrent = all_translation_words_in_segments(InList, Params)
    CurrentPairs = [ [Word, 'current'] for Word in AllCurrent ]
    Triples = [ (Word, translation_for_word_or_null(Word, 'local_files', Params), Current) for ( Word, Current ) in CurrentPairs ]
    NEmpty = count_empty_translations_in_vocab_spreadsheet_list(Triples)
    NFilled = len(Triples) - NEmpty
    return { 'translated': NFilled, 'not_translated': NEmpty }

def count_word_token_translations(Params):
    global translations_for_word_tokens
    translations_for_word_tokens = {}
    if not process_word_token_spreadsheet_files('local_files', all_word_token_translation_spreadsheets(Params)):
        return { 'translated': 0, 'not_translated': 0 }
    InList = [ Chunk for ( PageInfo, Chunks ) in lara_split_and_clean.read_split_file(Params.split_file, Params) for Chunk in Chunks ]
    ( NFilled, NEmpty ) = ( 0, 0 )
    for Chunk in InList:
        SurfaceWords = [ regularise_word_for_word_token_translation(WordPair[0]) for WordPair in Chunk[2] if WordPair[1] != '' ]
        NWords = len(SurfaceWords)
        Translation = word_token_translation_or_null(SurfaceWords, 'local_files')
        NTranslated = len([ Word for Word in Translation if Word != '' and not Word.isspace() ])
        if Translation == '':
            NEmpty += NWords
        else:
            NFilled += NTranslated
            NEmpty += ( NWords - NTranslated )
    return { 'translated': NFilled, 'not_translated': NEmpty }

def all_word_translation_spreadsheets(Params):
    OwnTranslationSpreadsheets = [] if Params.translation_spreadsheet == '' else [ Params.translation_spreadsheet ]
    return OwnTranslationSpreadsheets

def all_notes_spreadsheets(Params):
    OwnTranslationSpreadsheets = [] if Params.notes_spreadsheet == '' else [ Params.notes_spreadsheet ]
    return OwnTranslationSpreadsheets

def all_image_dict_spreadsheets(Params):
    OwnTranslationSpreadsheets = [] if Params.image_dict_spreadsheet == '' else [ Params.image_dict_spreadsheet ]
    return OwnTranslationSpreadsheets

def all_word_translation_surface_spreadsheets(Params):
    OwnTranslationSpreadsheets = [] if Params.translation_spreadsheet_surface == '' else [ Params.translation_spreadsheet_surface ]
    return OwnTranslationSpreadsheets
                        
def all_translation_words_in_segments(InList, Params):
    LemmaOrSurface = 'lemma' if Params.word_translations_on in [ 'lemma', 'lemma_notes', 'lemma_img_dict' ] else 'surface'
    Words0 = [ regularise_lemma(Lemma) if LemmaOrSurface == 'lemma' else regularise_word(Surface) for Chunk in InList for ( Surface, Lemma ) in Chunk[2]
               if Lemma != '' and not lara_parse_utils.is_punctuation_string(Surface) and not not_real_headword(Surface) ]
    return lara_utils.remove_duplicates(Words0)

# Not yet sure how 'local_files' can get into this list, but discard it if it does.
def not_real_headword(Word):
    return Word in [ 'local_files' ]

def make_segment_translation_spreadsheet(SplitFile, Spreadsheet, Params):
    global translations_for_segments
    translations_for_segments = {}
    if not process_segment_spreadsheet_files('local_files', all_segment_translation_spreadsheets(Params)):
        return False
    InList = [ Chunk for ( PageInfo, Chunks ) in lara_split_and_clean.read_split_file(SplitFile, Params) for Chunk in Chunks ]
    Tuples = [ ( Chunk[1], translation_for_segment_or_null(Chunk[1], 'local_files') ) for Chunk in InList
                if not (Chunk[1]).isspace() and not Chunk[1] == '' ]
    Header = ['Segment', 'Translation']
    write_translation_csv(Header, Tuples, Spreadsheet)
    NEmpty = count_empty_translations_in_vocab_spreadsheet_list(Tuples)
    NFilled = len(Tuples) - NEmpty
    lara_utils.print_and_flush(f'--- Written segment spreadsheet ({NFilled} filled entries, {NEmpty} blank entries) {Spreadsheet}')
    JSONFile = lara_utils.change_extension(Spreadsheet, 'json')
    lara_utils.write_json_to_file(Tuples, JSONFile)
    lara_utils.print_and_flush(f'--- Written segment JSON file ({NFilled} filled entries, {NEmpty} blank entries) {JSONFile}')

def count_segment_translations(Params):
    global translations_for_segments
    translations_for_segments = {}
    if not process_segment_spreadsheet_files('local_files', all_segment_translation_spreadsheets(Params)):
        ( NEmpty, NFilled ) = ( 0, 0 )
    InList = [ Chunk for ( PageInfo, Chunks ) in lara_split_and_clean.read_split_file(Params.split_file, Params) for Chunk in Chunks ]
    Tuples = [ ( Chunk[1], translation_for_segment_or_null(Chunk[1], 'local_files') ) for Chunk in InList
                if not (Chunk[1]).isspace() and not Chunk[1] == '' ]
    NEmpty = count_empty_translations_in_vocab_spreadsheet_list(Tuples)
    NFilled = len(Tuples) - NEmpty
    return { 'translated': NFilled, 'not_translated': NEmpty }

def all_segment_translation_spreadsheets(Params):
    OwnTranslationSpreadsheets = [] if Params.segment_translation_spreadsheet == '' else [ Params.segment_translation_spreadsheet ]
    return OwnTranslationSpreadsheets

def write_translation_csv(Header, Tuples, Spreadsheet):
    Tuples1 = [ [ lara_replace_chars.restore_reserved_chars(Tuple[0]) ] + list(Tuple[1:]) for Tuple in Tuples ]
    lara_utils.write_lara_csv([ Header ] + Tuples1, Spreadsheet)

def init_stored_downloaded_translations_metadata():
    global translations_for_words, translations_for_segments
    translations_for_words = {}
    translations_for_segments = {}

def translation_for_word_or_lemma(Word, Lemma, Params):
    LanguageId = lara_utils.get_l1_from_params(Params)
    Source = regularise_lemma(Lemma) if Params.word_translations_on in [ 'lemma', 'lemma_notes', 'lemma_image_dict' ] else regularise_word(Word)
    return translation_for_word(Source, LanguageId, Params)

def all_notes_for_word(Word):
    translation_dict = get_word_translations_dict_for_word_translation_type('lemma_notes')
    Notes = []
    for CorpusId in translation_dict:
        SubDict = translation_dict[CorpusId]
        if Word in SubDict:
            Notes += [ SubDict[Word] ]
    return Notes

def all_images_for_word(Word):
    translation_dict = get_word_translations_dict_for_word_translation_type('lemma_image_dict')
    Notes = []
    for CorpusId in translation_dict:
        SubDict = translation_dict[CorpusId]
        if Word in SubDict:
            Notes += [ SubDict[Word] ]
    return Notes

def note_for_word(Word, CorpusId):
    translation_dict = get_word_translations_dict_for_word_translation_type('lemma_notes')
    if CorpusId in translation_dict:
        SubDict = translation_dict[CorpusId]
        if Word in SubDict:
            return SubDict[Word]
    return False

def image_for_word(Word, CorpusId):
    translation_dict = get_word_translations_dict_for_word_translation_type('lemma_image_dict')
    if CorpusId in translation_dict:
        SubDict = translation_dict[CorpusId]
        if Word in SubDict:
            return SubDict[Word]
    return False

def translation_for_word_or_null(Word, LanguageId, Params):
    Translation = translation_for_word(Word, LanguageId, Params)
    return Translation if Translation else ''

def type_translation_for_word_or_null(Word, LanguageId, Params):
    Translation = type_translation_for_word(Word, LanguageId, Params)
    return Translation if Translation else ''

def word_has_translation(Word, Lemma, Params):
    LanguageId = lara_utils.get_l1_from_params(Params)
    WordOrLemma = Lemma if Params.word_translations_on == 'lemma' else Word
    Translation = translation_for_word(WordOrLemma, LanguageId, Params)
    Translation1 = False if null_translation(Translation) else Translation
    #lara_utils.print_and_flush(f'--- WordOrLemma = {WordOrLemma}, Translation = {Translation}, Translation1 = {Translation1}')
    return Translation1

def translation_for_word(Word, LanguageId, Params):
    Translation = translation_for_word1(Word, LanguageId, Params)
    return lara_chinese.maybe_add_pinyin_to_translation(Word, Translation, Params)

def translation_for_word1(Word, LanguageId, Params):
    if Params.word_translations_on == 'surface_word_token':
        return word_token_translation_for_word(Params)
    if stored_word_type_translation_available(Params):
        return stored_word_type_translation_for_word(Params)
    return type_translation_for_word(Word, LanguageId, Params)

def type_translation_for_word(Word0, LanguageId, Params):
    Word = regularise_word(Word0) if Params.word_translations_on == 'surface_word_type' else Word0
    translation_dict = get_word_translations_dict(Params)
    if LanguageId in translation_dict:
        SubDict = translation_dict[LanguageId]
        if Word in SubDict:
            return SubDict[Word]
        LemmaParts = Word.split('/')
        if len(LemmaParts) > 1 and LemmaParts[0] in SubDict:
            return SubDict[LemmaParts[0]]
    #lara_utils.print_and_flush(f'*** Warning: no translation for {Word0}: word_translations_on = {Params.word_translations_on}, LanguageId = {LanguageId}')
    return False

def word_token_translation_for_word(Params):
    ( TokenIndex, TokenTranslations ) = ( Params.word_token_index, Params.word_token_translations )
    if isinstance(TokenIndex, int) and isinstance(TokenTranslations, list) and 0 <= TokenIndex and TokenIndex < len(TokenTranslations):
        return TokenTranslations[TokenIndex]
    else:
        return False

def stored_word_type_translation_available(Params):
    return Params.word_translations_on == 'surface_word_type' and \
           isinstance(Params.word_type_translations, dict) and \
           isinstance(Params.word_token_index, int) and \
           Params.word_token_index in Params.word_type_translations

def stored_word_type_translation_for_word(Params):
    ( Index, StoredTranslations ) = ( Params.word_token_index, Params.word_type_translations )
    if isinstance(Index, int) and isinstance(StoredTranslations, dict) and Index in StoredTranslations:
        return StoredTranslations[Index]
    else:
        return False

def translation_for_segment(Segment, CorpusId):
    global translations_for_segments
    CanonicalSegment = regularise_segment(Segment)
    if CorpusId in translations_for_segments:
        SubDict = translations_for_segments[CorpusId]
        if CanonicalSegment in SubDict:
            return SubDict[CanonicalSegment]
        else:
            return False
    else:
        return False

def no_segment_translations(CorpusId):
    global translations_for_segments
    return not CorpusId in translations_for_segments 
    
def translation_for_segment_or_null(Segment, CorpusId):
    Translation = translation_for_segment(Segment, CorpusId)
    if Translation:
        return Translation
    else:
        return ''

##def store_downloaded_word_translations(LanguageId, File, Params):
##    return process_word_spreadsheet_file(LanguageId, File, Params)
def store_downloaded_word_translations(LanguageId, UserId, LemmaOrSurface, File):
    L1Key = LanguageId if UserId == 'public' else ( LanguageId, UserId )
    return store_word_translation_file(File, LemmaOrSurface, L1Key)

def process_word_spreadsheet_files(LanguageId, Files, Params):
    for File in Files:
        if not process_word_spreadsheet_file(LanguageId, File, Params):
            return False
    return True

def store_downloaded_notes(LanguageId, File):
    return store_word_translation_file(File, 'lemma_notes', LanguageId)

def store_downloaded_image_dict(LanguageId, File):
    return store_word_translation_file(File, 'lemma_image_dict', LanguageId)

def process_note_file(LanguageId, File, Params):
    Params1 = copy.copy(Params)
    Params1.word_translations_on = 'lemma_notes'
    process_word_spreadsheet_file(LanguageId, File, Params1)     

def process_image_dict_file(LanguageId, File, Params):
    Params1 = copy.copy(Params)
    Params1.word_translations_on = 'lemma_image_dict'
    process_word_spreadsheet_file(LanguageId, File, Params1)     

def process_word_spreadsheet_file(LanguageId, File, Params):
    LemmaOrSurface = Params.word_translations_on
    L1Key = LanguageId
    return store_word_translation_file(File, LemmaOrSurface, L1Key)

def store_word_translation_file(File, LemmaOrSurface, L1Key):
    if lara_utils.file_exists(File):
        DataFromCSV = lara_utils.read_lara_csv(File)
        if DataFromCSV:
            Records = DataFromCSV[1:]
            store_word_spreadsheet_data(Records, LemmaOrSurface, L1Key)
            lara_utils.print_and_flush(f'--- Loaded word translation spreadsheet {File}')
            return True
        else:
            lara_utils.print_and_flush(f'*** Error: unable to load word translation spreadsheet {File}')
            return False
    else:
        lara_utils.print_and_flush(f'*** Warning: word translation spreadsheet not found: {File}')
        return True

def store_word_spreadsheet_data(Records, LemmaOrSurface, L1Key):
    translations_dict = get_word_translations_dict_for_word_translation_type(LemmaOrSurface)
    SubDict = translations_dict[L1Key] if L1Key in translations_dict else {}
    for Record in Records:
        # Ignore lines where the translation hasn't been filled in.
        if len(Record) >= 2 and not Record[1].isspace() and not Record[1] == '':
            ( Word, Translation ) = ( lara_replace_chars.replace_reserved_chars(Record[0]), Record[1] )
            SubDict[Word] = Translation
    translations_dict[L1Key] = SubDict

def store_downloaded_segment_translations(CorpusId, File):
    return process_segment_spreadsheet_file(CorpusId, File)

def process_segment_spreadsheet_files(CorpusId, Files):
    for File in Files:
        if not process_segment_spreadsheet_file(CorpusId, File):
            return False
    return True
            
def process_segment_spreadsheet_file(CorpusId, File):
    if lara_utils.file_exists(File):
        DataFromCSV = lara_utils.read_lara_csv(File)
        if DataFromCSV:
            Records = DataFromCSV[1:]
            store_segment_spreadsheet_data(CorpusId, Records)
            lara_utils.print_and_flush(f'--- Loaded segment translation spreadsheet ({len(Records)} records) {File}')
            return True
        else:
            lara_utils.print_and_flush(f'*** Error: unable to load segment translation spreadsheet {File}')
            return False
    else:
        lara_utils.print_and_flush(f'*** Warning: segment translation spreadsheet not found: {File}')
        return True

def store_segment_spreadsheet_data(CorpusId, Records):
    global translations_for_segments
    SubDict = translations_for_segments[CorpusId] if CorpusId in translations_for_segments else {}
    for Record in Records:
        # Ignore lines where the translation hasn't been filled in.
        if len(Record) >= 2 and not Record[1].isspace() and not Record[1] == '':
            Key = internalise_text_from_segment_spreadsheet(Record[0])
            SubDict[Key] = Record[1]
    translations_for_segments[CorpusId] = SubDict

def regularise_word(Word):
    #return lara_audio.make_word_canonical_for_word_recording(Word)
    return lara_audio.make_word_canonical_for_word_recording_dont_restore_chars(Word)

def regularise_word_for_word_token_translation(Word):
    ( WordMinusHTML, Trace ) = lara_parse_utils.remove_html_annotations_from_string(Word)
    if len(Trace) == 0:
        WordMinusHTML1 = WordMinusHTML.replace('\n', '')
        WordMinusHTML2 = lara_replace_chars.restore_reserved_chars(WordMinusHTML1)
        return lara_parse_utils.remove_initial_and_final_spaces(lara_parse_utils.remove_weird_characters(WordMinusHTML2))
    else:
        lara_utils.print_and_flush(f'*** Error in lara_translations.regularise_word_for_word_token_translation')
        lara_utils.print_and_flush('\n'.join(Trace))
        return False   

def regularise_lemma(Lemma):
    return lara_mwe.strip_off_mwe_part_tag(Lemma)

def regularise_segment(Str):
    Str1 = lara_parse_utils.remove_weird_characters(Str)
    Str1 = lara_parse_utils.remove_initial_and_final_spaces(Str1.replace('"', '').replace('\'', ''))
    return lara_parse_utils.remove_audio_prefix( Str1 )
    
def internalise_text_from_segment_spreadsheet(Str):
    Str1 =  lara_replace_chars.replace_reserved_chars(Str)
    return lara_parse_utils.remove_initial_and_final_spaces(Str1.replace('"', '').replace('\'', ''))

def count_empty_translations_in_vocab_spreadsheet_list(Tuples):
    Empty = [ Tuple for Tuple in Tuples if Tuple[1] == '' ]
    return len(Empty)

def count_empty_translations_in_json_vocab_spreadsheet_list(Tuples):
    Empty = [ Word for ( Word, Translation, Freq, Examples ) in Tuples if Translation == '' ]
    return len(Empty)

# ------------------------------------------------

# Dicts for caching translation information
translations_for_words = {}
translations_for_segments = {}
translations_for_word_tokens = {}

def get_word_translations_dict(Params):
    WordTranslationType = Params.word_translations_on
    return get_word_translations_dict_for_word_translation_type(WordTranslationType)

def get_word_translations_dict_for_word_translation_type(WordTranslationType):
    global translations_for_words
    if not WordTranslationType in lara_config._permitted_word_translation_types + [ 'lemma_notes', 'lemma_image_dict' ]:
        lara_utils.print_and_flush(f'*** Error: unknown word translation_type: {WordTranslationType}')
        return False
    if not WordTranslationType in translations_for_words:
        translations_for_words[WordTranslationType] = {}
    return translations_for_words[WordTranslationType]

def notes_are_defined():
    subdict = get_word_translations_dict_for_word_translation_type('lemma_notes')
    return subdict and isinstance(subdict, dict) and len(list(subdict.keys())) > 0

def image_dict_entries_are_defined():
    subdict = get_word_translations_dict_for_word_translation_type('lemma_image_dict')
    return subdict and isinstance(subdict, dict) and len(list(subdict.keys())) > 0

def lemma_and_notes_list():
    if not notes_are_defined():
        return []
    Assoc = {}
    subdict = get_word_translations_dict_for_word_translation_type('lemma_notes')
    for CorpusId in subdict:
        subsubdict = subdict[CorpusId]
        if isinstance(subsubdict, dict):
            for Word in subsubdict:
                List = Assoc[Word] if Word in Assoc else []
                List += [ subsubdict[Word] ]
                Assoc[Word] = List
    return [ [ Word, Assoc[Word] ] for Word in Assoc ]

def lemma_and_image_list_for_representation(Params):
    return [ lemma_and_images_list_item_to_representation(Item, Params) for Item in lemma_and_images_list() ]

def lemma_and_images_list_item_to_representation(Item, Params):
    ( Lemma, Files ) = ( Item[0], Item[1] )
    return { 'lemma': Lemma,
             'images': [ { 'corpus_name': Params.id,
                           'file': File }
                         for File in Files ]
             }

def lemma_and_images_list():
    if not image_dict_entries_are_defined():
        return []
    Assoc = {}
    subdict = get_word_translations_dict_for_word_translation_type('lemma_image_dict')
    for CorpusId in subdict:
        subsubdict = subdict[CorpusId]
        if isinstance(subsubdict, dict):
            for Word in subsubdict:
                List = Assoc[Word] if Word in Assoc else []
                List += [ subsubdict[Word] ]
                Assoc[Word] = List
    return [ [ Word, Assoc[Word] ] for Word in Assoc ]                                                             

# ------------------------------------------------

# Keep only the first two columns (i.e. remove the 'current' markings)
def make_current_only_csv(FullCSV, CurrentOnlyCSV):
    if lara_utils.file_exists(FullCSV):
        DataFromCSV = lara_utils.read_lara_csv(FullCSV)
        if DataFromCSV and len(DataFromCSV) >= 1:
            lara_utils.print_and_flush(f'--- Read full translation spreadsheet, {len(DataFromCSV)-1} records')
            CurrentOnlyRecords = [ Record[:2] for Record in DataFromCSV[1:] if len(Record) >= 2 and Record[2] == 'current' ]
            AllCurrentOnlyRecords = [ DataFromCSV[0][:2] ] + CurrentOnlyRecords
            lara_utils.write_lara_csv(AllCurrentOnlyRecords, CurrentOnlyCSV)
            lara_utils.print_and_flush(f'--- Written current-only translation spreadsheet, {len(CurrentOnlyRecords)} records to {CurrentOnlyCSV}')
            return True
        else:
            lara_utils.print_and_flush(f'*** Warning: unable to read translation spreadsheet {FullCSV}')
            return False
    else:
        lara_utils.print_and_flush(f'*** Warning: word translation spreadsheet not found: {FullCSV}')
        return True

def word_translation_csv_to_json(WordCSV, WordJSON):
    Records = read_word_token_spreadsheet_file(WordCSV, 'dont_remove_mwe_markings')
    if not Records:
        lara_utils.print_and_flush(f'*** Error: unable to read translation spreadsheet {WordCSV}')
        return False
    return lara_utils.write_json_to_file(Records, WordJSON)

def word_translation_json_to_csv(WordJSON, WordCSV):
    try:
        word_translation_json_to_csv1(WordJSON, WordCSV)
    except Exception as e:
        lara_utils.print_and_flush(f'*** Error: something went wrong when trying to convert word token JSON into CSV')
        lara_utils.print_and_flush(str(e))

def word_translation_json_to_csv1(WordJSON, WordCSV):
    Records = lara_utils.read_json_file(WordJSON)
    if not Records:
        lara_utils.print_and_flush(f'*** Error: unable to read translation JSON file {WordJSON}')
        return False
    if not check_for_word_token_translation_content(Records):
        lara_utils.print_and_flush(f'*** Error: {WordJSON} does not appear to be a word token JSON file')
        return False
    Lines = []
    for ( SourceWords, TranslatedWords, ReferenceWords ) in Records:
        Lines += [ 'separator_line', SourceWords, TranslatedWords, ReferenceWords ]
    ExpandedLines = expand_token_triple_lines(Lines)
    lara_utils.write_lara_csv(ExpandedLines, WordCSV)

def check_for_word_token_translation_content(Records):
    if not isinstance(Records, list):
        lara_utils.print_and_flush(f'*** Error: contents of file are not a list')
    #( Length, Example ) = ( False, False )
    for Record in Records:
        if not isinstance(Record, list) or not len(Record) == 3:
            lara_utils.print_and_flush(f'*** Error: item {Record} is not a three-element list')
        for SubRecord in Record:
            if not is_list_of_strings(SubRecord):
                lara_utils.print_and_flush(f'*** Error: component of item {SubRecord} is not a list of strings')
                return False
##            if not Length:
##                (Example, Length ) = ( SubRecord, len(SubRecord) )
##            elif not len(SubRecord) == Length:
##                lara_utils.print_and_flush(f'*** Error: lines are not all the same length')
##                lara_utils.print_and_flush(f'*** Error: {Example} has {Length} items, and {SubRecord} has {len(SubRecord)} items')
##                return False
    return True

def word_type_or_lemma_json_to_csv(WordJSON, WordCSV):
    try:
        word_type_or_lemma_json_to_csv1(WordJSON, WordCSV)
    except Exception as e:
        lara_utils.print_and_flush(f'*** Error: something went wrong when trying to convert word type or lemma JSON into CSV')
        lara_utils.print_and_flush(str(e))

def word_type_or_lemma_json_to_csv1(WordJSON, WordCSV):
    Records = lara_utils.read_json_file(WordJSON)
    if not Records:
        lara_utils.print_and_flush(f'*** Error: unable to read translation JSON file {WordJSON}')
        return False
    if not check_for_word_type_or_lemma_translation_content(Records):
        lara_utils.print_and_flush(f'*** Error: {WordJSON} does not appear to be a word type or lemma JSON file')
        return False
    #SortedRecords = sorted(Records, key=lambda x: x[0].lower())
    Lines = []
    #for ( SourceWord, TranslatedWord, Freq, Examples ) in SortedRecords:
    for ( SourceWord, TranslatedWord, Freq, Examples ) in Records:
        Lines += [ [ SourceWord, TranslatedWord ] ]
    Header = [ 'Source', 'Target' ]
    lara_utils.write_lara_csv([ Header ] + Lines, WordCSV)

def check_for_word_type_or_lemma_translation_content(Records):
    if not isinstance(Records, list):
        lara_utils.print_and_flush(f'*** Error: contents of file are not a list')
        return False
    for Record in Records:
        if not isinstance(Record, list) or not len(Record) == 4:
            lara_utils.print_and_flush(f'*** Error: item {Record} is not a four-element list')
            return False
        if not isinstance(Record[0], str):
            lara_utils.print_and_flush(f'*** Error: first element of {Record} is not a string')
            return False
        if not isinstance(Record[1], str):
            lara_utils.print_and_flush(f'*** Error: second element of {Record} is not a string')
            return False
    return True
            
def is_list_of_strings(List):
    if not isinstance(List, list):
        return False
    for X in List:
        if not isinstance(X, str):
            return False
    return True

def null_translation(Translation):
    if not isinstance(Translation, str):
        return True
    else:
        for Char in Translation:
            if not lara_parse_utils.is_punctuation_char(Char) and not Char.isspace():
                return False
        return True
