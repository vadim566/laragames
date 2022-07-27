
import lara_top
import lara
import lara_treetagger
import lara_split_and_clean
import lara_mwe
import lara_audio
import lara_translations
import lara_config
import lara_old_norse
import lara_parse_utils
import lara_utils

# Takes a config file as input and returns a dict with all the LARA resources the flashcard code needs for this text.
def make_flashcard_resources(ConfigFile):
    try:
        Params = lara_config.read_lara_local_config_file(ConfigFile)
        if not Params:
            lara_utils.print_and_flush(f'Error: unable to read config file {ConfigFile}')
            return False
        ( WordPOSDict, LemmaPOSDict ) = get_word_pos_dict_and_lemma_pos_dict(ConfigFile, Params)
        ( WordFreqDict, LemmaFreqDict ) = make_word_and_lemma_frequency_dicts(Params)
        SegmentMultimediaDict = get_segment_multimedia_dict(Params)
        LemmaTranslationDict = get_lemma_translation_dict(Params)
        ( WordContextDict, LemmaContextDict ) = get_word_context_dict_and_lemma_context_dict(Params)
        TranslationLemmaDict = get_translations_lemma_dict(Params)
        TokenTranslationDict = get_token_translation_dict(Params)
        WordMultimediaDict = get_word_multimedia_dict(Params)
        SentenceAndWordPairsList = get_sentence_and_word_pairs_list(Params)
    except Exception as e:
        lara_utils.print_and_flush(f'*** Error: something went wrong when creating flashcard resources for config file {ConfigFile}')
        lara_utils.print_and_flush(str(e))
        return False
    return {
        # Config file settings for this text
        'params': Params,
        # Dict of form Word -> POS
        'word2POS_dict': WordPOSDict,
        # Dict of form Lemma -> POS
        'lemma2POS_dict': LemmaPOSDict,
        # Dict of form Word -> Freq
        'word2freq_dict': WordFreqDict,
        # Dict of form Lemma -> Freq
        'lemma2freq_dict': LemmaFreqDict,
        # Dict of form Lemma -> { 'translation': Translation, 'context', Context }
        'lemma2translation_and_context_dict': LemmaTranslationDict,
        # Dict of form word -> Context 
        'word2context_dict': WordContextDict,
        # Dict of form Lemma -> Context 
        'lemma2context_dict': LemmaContextDict,
        # Dict of form Lemma -> { 'translation': Translation, 'context', Context }
        'translation2lemma_and_context_dict': TranslationLemmaDict,
        # Dict of form Word -> { 'translation': Translation, 'context': Context, 'lemma': Lemma, 'is_mwe': IsMWE }
        'word2tokentranslation_and_context_dict': TokenTranslationDict,
        # Dict of form Word -> MultimediaFile
        'word2multimedia_dict': WordMultimediaDict,
        # Dict of form Segment -> MultimediaFile
        'segment2multimedia_dict': SegmentMultimediaDict,
        # List of [ Sentence, SurfaceWords ] pairs
        'sentences_and_word_pairs_list': SentenceAndWordPairsList
        }

def get_word_pos_dict_and_lemma_pos_dict(ConfigFile, Params):
    if not lara_treetagger.tagger_is_available_for_language(Params.language, Params) and not Params.language == 'oldnorse':
        return ( {}, {} )
    WordPosFile = lara_top.lara_tmp_file('word_pos_file', Params)
    make_word_pos_file_if_necessary(Params, ConfigFile, WordPosFile)
    if not lara_utils.file_exists(WordPosFile):
        return ( {}, {} )
    WordPOSData = lara_utils.read_json_file(WordPosFile)
    ( WordPosDict, LemmaPOSDict ) = ( {}, {} )
    for ( Word, Lemma, POS ) in WordPOSData:
        # This ignores the fact that a word may be associated with more than one POS
        WordPosDict[Word] = POS
        LemmaPOSDict[Lemma] = POS
    return ( WordPosDict, LemmaPOSDict )

# Make a word POS file. This is a JSON file containing a list of lists, one per token, of the form
# [ Word, Lemma, POS ]
# We treat Old Norse specially.
def make_word_pos_file_if_necessary(Params, ConfigFile, WordPosFile):
    Language = Params.language
    CorpusFile = Params.corpus
    if lara_utils.file_exists(WordPosFile) and files_needed_for_word_pos_file_are_up_to_date(WordPosFile, CorpusFile):
        lara_utils.print_and_flush(f'--- POS file {WordPosFile} is more recent than corpus file {CorpusFile}, assuming up to date.')
    elif Language == 'oldnorse':
        make_old_norse_word_pos_file(Params, WordPosFile)
    elif lara_treetagger.tagger_is_available_for_language(Language, Params):
        lara_top.make_word_pos_file(ConfigFile)

def files_needed_for_word_pos_file_are_up_to_date(WordPosFile, CorpusFile):
    RelevantFiles = [ CorpusFile,
                      '$LARA/Code/Python/lara_flashcards_resources.py',
                      '$LARA/Code/Python/lara_old_norse.py',
                      '$LARA/Code/Python/lara_utils.py',
                      '$LARA/Code/Python/lara_parse_utils.py'
                      ]
    return lara_utils.file_is_newer_than_files(WordPosFile, RelevantFiles) 

def make_old_norse_word_pos_file(Params, WordPosFile):
    SplitFileData = get_split_file_contents(Params)
    WordLemmaPOSList = []
    for ( PageInfo, Segments ) in SplitFileData:
        for ( Raw, Clean, WordLemmaPairs, Tag ) in Segments:
            for ( Word, Lemma ) in WordLemmaPairs:
                if Lemma != '':
                    POS = lara_old_norse.old_norse_lemma_to_pos(Lemma)
                    ReducedPOS = lara_old_norse.reduced_form_of_old_norse_pos(POS)
                    WordLemmaPOSList += [ [ clean_up_word(Word), Lemma, ReducedPOS ] ]
    lara_utils.write_json_to_file(WordLemmaPOSList, WordPosFile)
    lara_utils.print_and_flush(f'--- Made Old Norse POS file {WordPosFile}')

# Get segment audio metadata and convert to dict
def get_segment_multimedia_dict(Params):
    Dir = Params.segment_audio_directory
    Dict = get_multimedia_dict(Dir)
    lara_utils.print_and_flush(f'--- Made segment multimedia dict ({len(Dict)} entries))')
    return Dict

# Get word audio metadata and convert to dict
def get_word_multimedia_dict(Params):
    Dir = Params.word_audio_directory
    Dict = get_multimedia_dict(Dir)
    lara_utils.print_and_flush(f'--- Made word multimedia dict ({len(Dict)} entries))')
    return Dict

def get_multimedia_dict(Dir):
    if Dir == '':
        return {}
    Metadata = lara_audio.read_ldt_metadata_file(Dir)
    Dict = {}
    for MetadataItem in Metadata:
        ( Text, BaseFile ) = ( MetadataItem['text'], MetadataItem['file'] )
        if BaseFile != '':
            Dict[Text] = BaseFile
    return Dict

# Get lemma translation spreadsheet and convert to dict
def get_lemma_translation_dict(Params):
    CSVFile = Params.translation_spreadsheet
    if CSVFile == '':
        return {}
    Data = lara_utils.read_lara_csv(CSVFile)[1:]
    Dict = {}
    for Line in Data:
        if len(Line) >= 2:
            ( Lemma, Translation ) = Line[:2]
            if Translation != '':
                Dict[Lemma] = Translation
    Dict1 = add_contexts_to_lemma_translation_dict(Params, Dict)
    lara_utils.print_and_flush(f'--- Made lemma to translation and context dict ({len(Dict1)} entries))')
    return Dict1

def add_contexts_to_lemma_translation_dict(Params, Dict):
    SplitFileData = get_split_file_contents(Params)
    Dict1 = {}
    for ( PageInfo, Segments ) in SplitFileData:
        for ( Raw, Clean, WordLemmaPairs, Tag ) in Segments:
            for ( Word, Lemma ) in WordLemmaPairs:
                if Lemma != '' and not Lemma in Dict1 and Lemma in Dict:
                    Dict1[Lemma] = { 'translation': Dict[Lemma], 'context': Clean }
    return Dict1

# Get two dicts that respectively associate words and lemmas with contexts
def get_word_context_dict_and_lemma_context_dict(Params):
    SplitFileData = get_split_file_contents(Params)
    ( WordDict, LemmaDict ) = ( {}, {} )
    for ( PageInfo, Segments ) in SplitFileData:
        for ( Raw, Clean, WordLemmaPairs, Tag ) in Segments:
            for ( Word, Lemma ) in WordLemmaPairs:
                #RegularisedWord = lara_translations.regularise_word(Word)
                if Word != '' and not Word in WordDict:
                    WordDict[Word] = Clean
                if Lemma != '' and not Lemma in LemmaDict:
                    LemmaDict[Lemma] = Clean
    return ( WordDict, LemmaDict )

# Get lemma translation spreadsheet and convert to reverse dict
def get_translations_lemma_dict(Params):
    Dict = get_lemma_translation_dict(Params)
    Dict1 = {}
    for Lemma in Dict.keys():
        Entry = Dict[Lemma]
        Translation = Entry['translation']
        Context = Entry['context']
        Dict1[Translation] = { 'lemma': Lemma, 'context': Context }
    lara_utils.print_and_flush(f'--- Made translation to lemma and context dict ({len(Dict1)} entries))')
    return Dict1

# Get token translation dict
def get_token_translation_dict(Params):
    TokenFileCSV = Params.translation_spreadsheet_tokens
    if TokenFileCSV == '' or not lara_utils.file_exists(TokenFileCSV):
        return {}
    TokenFileJSON = lara_utils.get_tmp_json_file(Params)
    lara_translations.word_translation_csv_to_json(TokenFileCSV, TokenFileJSON)
    TranslationTriples = lara_mwe.split_file_and_token_translation_file_to_translation_context_tuples_taking_account_of_mwes(Params, TokenFileJSON)
    Dict = {}
    for ( Word, Translation, Context, Lemma, IsMWE ) in TranslationTriples:
        if not null_translation(Translation) and not Word in Dict:
            Dict[Word] = { 'translation': Translation, 'context': Context, 'lemma': Lemma, 'is_mwe': IsMWE }
    lara_utils.delete_file_if_it_exists(TokenFileJSON)
    lara_utils.print_and_flush(f'--- Made word to token translation and context dict ({len(Dict)} entries))')
    return Dict

def null_translation(Translation):
    return Translation in ( '', '-', '(-)' )
 
# Get list of [ Sentence, SurfaceWord ] pairs
def get_sentence_and_word_pairs_list(Params):
    SplitFileData = get_split_file_contents(Params)
    List = []
    for ( PageInfo, Segments ) in SplitFileData:
        for ( Raw, Clean, WordLemmaPairs, Tag ) in Segments:
            if Clean != '':
                Pairs = [ ( clean_up_word(Word), Lemma ) for ( Word, Lemma ) in WordLemmaPairs ]
                List += [ [ Clean, Pairs ] ]
    lara_utils.print_and_flush(f'--- Made sentence and word-pairs list({len(List)} entries))')
    return List

def make_word_and_lemma_frequency_dicts(Params):
    CountFile = lara_top.lara_tmp_file('count', Params)
    SurfaceCountFile = lara_top.lara_tmp_file('surface_count', Params)
    WordCountPairs = lara.read_count_file(SurfaceCountFile, Params)
    LemmaCountPairs = lara.read_surface_count_file(CountFile, Params)
    WordCountDict = word_count_pairs_to_dict(WordCountPairs)
    LemmaCountDict = lemma_count_pairs_to_dict(LemmaCountPairs)
    lara_utils.print_and_flush(f'--- Made word frequency dict, {len(WordCountDict)} entries')
    lara_utils.print_and_flush(f'--- Made lemma frequency dict, {len(LemmaCountDict)} entries')
    return (WordCountDict, LemmaCountDict  )

def word_count_pairs_to_dict(WordCountPairs):
    Dict = {}
    for ( Word, Count ) in WordCountPairs:
        CleanWord = clean_up_word(Word).lower()
        Dict[CleanWord] = Count if not CleanWord in Dict else Dict[CleanWord] + Count
    return Dict

def lemma_count_pairs_to_dict(LemmaCountPairs):
    Dict = {}
    for ( Lemma, Count ) in LemmaCountPairs:
        Dict[Lemma] = Count if not Lemma in Dict else Dict[Lemma] + Count
    return Dict

def get_split_file_contents(Params):
    SplitFile = lara_top.lara_tmp_file('split', Params)
    # This remakes the split file if it's out of date
    return lara_split_and_clean.read_split_file(SplitFile, Params)

def clean_up_word(Word):
    return lara_parse_utils.remove_hashtag_comment_and_html_annotations1(Word, 'delete_comments')[0]
