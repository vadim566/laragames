
import lara_top
import lara_transform_tagged_file
import lara_config
import lara_audio
import lara_parse_utils
import lara_utils
import copy

def test(Id):
    if Id == 'tina_signed':
        ConfigFile = '$LARA/Content/tina_signed/corpus/local_config.json'
        SegmentSpreadsheet = '$LARA/Content/tina_signed/corpus/tina_signed_icelandic_to_ítm_segments.csv'
        WordSpreadsheet = '$LARA/Content/tina_signed/corpus/tina_signed_icelandic_to_ítm_words.csv'
        NewId = 'tina_ítm'
        SignerId = 'siggi'
        SignLang = 'ítm'
        TargetLang = 'english'
        NewProjectDir = '$LARA/Content/tina_ítm'
    elif Id == 'tina_signed_v2':
        ConfigFile = '$LARA/Content/tina_signed/corpus/local_config.json'
        SegmentSpreadsheet = '$LARA/Content/tina_signed/corpus/tina_signed_icelandic_to_ítm_segments_v2.csv'
        WordSpreadsheet = '$LARA/Content/tina_signed/corpus/tina_signed_icelandic_to_ítm_words.csv'
        NewId = 'tina_ítm_v2'
        SignerId = 'siggi'
        SignLang = 'ítm'
        TargetLang = 'english'
        NewProjectDir = '$LARA/Content/tina_ítm'
    elif Id == 'tina_signed_v3':
        ConfigFile = '$LARA/Content/tina_signed/corpus/local_config_30.json'
        SegmentSpreadsheet = '$LARA/Content/tina_signed/corpus/tina_signed_icelandic_to_ítm_segments_v3.csv'
        WordSpreadsheet = '$LARA/Content/tina_signed/corpus/tina_signed_icelandic_to_ítm_words.csv'
        NewId = 'tina_ítm_v3'
        SignerId = 'siggi'
        SignLang = 'ítm'
        TargetLang = 'english'
        NewProjectDir = '$LARA/Content/tina_ítm'
    else:
        lara_utils.print_and_flush('f*** Error: unknown ID "{Id}"')
        return False
    text_project_to_sign_project(ConfigFile, SegmentSpreadsheet, WordSpreadsheet,
                                 NewId, SignerId, SignLang, TargetLang,
                                 NewProjectDir)

def transfer_tina_word_videos():
    WordVideoDir = '$LARA/Content/icelandic/audio/siggi'
    SignVideoDir = '$LARA/Content/ítm/audio/siggi'
    RecordingFile = '$LARA/tmp_resources/tina_ítm_v3_record_words_full.json'
    text_word_videos_to_sign_videos(WordVideoDir, SignVideoDir, RecordingFile)

def text_project_to_sign_project(ConfigFile, SegmentSpreadsheet, WordSpreadsheet,
                                 NewId, SignerId, SignLang, TargetLang,
                                 NewProjectDir):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if not Params:
        lara_utils.print_and_flush(f'*** Error: unable to read config file {ConfigFile}')
        return False
    if not lara_top.compile_lara_local_resources(ConfigFile):
        lara_utils.print_and_flush(f'Error: unable make resources for {ConfigFile}')
        return False
    create_directory_and_subdirectories_for_new_project(NewProjectDir, SignerId, SignLang)
    SegmentDict = text_sign_spreadsheet_to_dict(SegmentSpreadsheet)
    WordDict = text_sign_spreadsheet_to_dict(WordSpreadsheet)
    NewCorpusFile = convert_corpus(Params, SegmentDict, NewProjectDir)
    NewSegmentVideoDir = convert_segment_video_dir(Params, SignerId, SegmentDict, NewProjectDir)
    NewSegmentTranslationCSV = convert_segment_translation_spreadsheet(Params, SignLang, TargetLang, SegmentDict, NewProjectDir)
    NewWordVideoDir = update_word_sign_dir(Params, SignerId, SignLang, WordDict)
    NewImageDir = copy_images(Params, NewProjectDir)
    NewWordTranslationCSV = update_word_translation_spreadsheet(Params, SignLang, TargetLang, WordDict)
    convert_config(Params, NewId, SignLang, NewProjectDir,
                   NewCorpusFile, NewSegmentVideoDir, NewSegmentTranslationCSV,
                   NewWordVideoDir, NewWordTranslationCSV, NewImageDir)

def create_directory_and_subdirectories_for_new_project(NewProjectDir, SignerId, SignLang):
    lara_utils.create_directory_if_it_doesnt_exist(NewProjectDir)
    lara_utils.create_directory_if_it_doesnt_exist(f'{NewProjectDir}/corpus')
    lara_utils.create_directory_if_it_doesnt_exist(f'{NewProjectDir}/audio')
    lara_utils.create_directory_if_it_doesnt_exist(f'{NewProjectDir}/audio/{SignerId}')
    lara_utils.create_directory_if_it_doesnt_exist(f'{NewProjectDir}/translations')
    lara_utils.create_directory_if_it_doesnt_exist(f'{NewProjectDir}/images')
    lara_utils.create_directory_if_it_doesnt_exist(f'$LARA/Content/{SignLang}')
    lara_utils.create_directory_if_it_doesnt_exist(f'$LARA/Content/{SignLang}/audio')
    lara_utils.create_directory_if_it_doesnt_exist(f'$LARA/Content/{SignLang}/audio/{SignerId}')
    lara_utils.create_directory_if_it_doesnt_exist(f'$LARA/Content/{SignLang}/translations')

def text_sign_spreadsheet_to_dict(Spreadsheet):
    Lines = lara_utils.read_lara_csv(Spreadsheet)
    Dict = {}
    for Line in Lines:
        ( Text, Sign ) = clean_up_text_sign_spreadsheet_line(Line)
        if not Sign == '' and not Sign.isspace():
            Dict[Text] = Sign
    return Dict

def clean_up_text_sign_spreadsheet_line(Line):
    if not isinstance(Line, list) or len(Line) < 2:
        lara_utils.print_and_flush(f'*** Error: bad line {Line}')
        return False
    return ( Line[0], clean_up_text_sign_spreadsheet_item(Line[1]) )

def clean_up_text_sign_spreadsheet_item(Item):
    Item1 = lara_parse_utils.remove_punctuation_marks_except_hyphen_and_underscore(Item)
    return ' '.join(Item1.split())

def convert_corpus(Params, SegmentDict, NewProjectDir):
    OldCorpusFileBase = Params.corpus.split('/')[-1]
    NewCorpusFile = f'{NewProjectDir}/corpus/{OldCorpusFileBase}'
    SplitFile = lara_top.lara_tmp_file('split', Params)
    SplitFileContent = lara_utils.read_json_file(SplitFile)
    SplitFileContent1 = convert_split_file_content(SplitFileContent, SegmentDict)
    lara_transform_tagged_file.split_file_content_to_text_file(SplitFileContent1, NewCorpusFile)
    return NewCorpusFile

def convert_split_file_content(SplitFileContent, SegmentDict):
    return [ convert_split_file_page(Page, SegmentDict) for Page in SplitFileContent ]

def convert_split_file_page(Page, SegmentDict):
    ( PageInfo, Segments ) = Page
    return ( PageInfo, [ convert_split_file_segment(Segment, SegmentDict) for Segment in Segments ] )

def convert_split_file_segment(Segment, SegmentDict):
    ( Raw, Clean, Pairs, Tag ) = Segment
    if not Clean in SegmentDict or SegmentDict[Clean] == '' or SegmentDict[Clean].isspace():
        if Clean != '':
            lara_utils.print_and_flush(f'*** Warning: no sign translation for "{Clean}"')
        return Segment
    SignedClean = SegmentDict[Clean]
    SignedWords = SignedClean.split()
    SignedPairs = convert_word_pairs(Pairs, SignedWords)
    SignedRaw = ''.join([ surface_form_for_pair(Pair) for Pair in SignedPairs ])
    return ( SignedRaw, SignedClean, SignedPairs, Tag )

def surface_form_for_pair(Pair):
    ( Surface, Lemma ) = Pair
    # Non-content
    if Lemma == '':
        return Surface
    # No need for lemma tag (this should not happen if glosses are written normally, i.e. in uppercase
    elif Surface.lower() == Lemma:
        return Surface
    # Add lemma tag
    else:
        return f'{Surface}#{Lemma}#'

def convert_word_pairs(Pairs, SignedWords):
    # We've used up all the sign glosses, get rid of the rest of the words
    if len(SignedWords) == 0:
        return remove_content_words_from_pairs(Pairs)
    # We've used up all the words, add the sign glosses to the end with spaces in between
    elif not content_word_pair_in_pairs(Pairs):
        return signed_words_to_pairs(SignedWords)
    # Next pair is non-content, keep it and move on
    elif Pairs[0][1] == '':
        return [ Pairs[0] ] + convert_word_pairs(Pairs[:1], SignedWords)
    # Next pair is content, replace it with the next signed word
    else:
        SignedWord = SignedWords[0]
        Components = SignedWord.split('#')
        if len(Components) == 1:
            ( Sign, Lemma ) = ( SignedWord, SignedWord )
        elif len(Components) == 3 and Component[2] == '':
            ( Sign, Lemma ) = Components[:2]
        else:
            lara_utils.print_and_flush(f'*** Error: too many # in "{SignedWord}"')
            return False
        return [ ( Sign, Lemma ) ] + convert_word_pairs(Pairs[:1], SignedWords[:1])

def remove_content_words_from_pairs(Pairs):
    return [ Pair for Pair in Pairs if Pair[1] != '' ]

def content_word_pair_in_pairs(Pairs):
    return len( [ Pair for Pair in Pairs if Pair[1] != '' ] ) > 0

# Add a space after each signed word
def signed_words_to_pairs(SignedWords):
    Pairs = []
    for SignedWord in SignedWords:
        Pairs += [ [ SignedWord, SignedWord ], [ ' ', '' ] ]
    return Pairs      

def convert_segment_video_dir(Params, SignerId, SegmentDict, NewProjectDir):
    SegmentVideoDir = Params.segment_audio_directory
    if SegmentVideoDir == '':
        return ''
    NewSegmentVideoDir = f'{NewProjectDir}/audio/{SignerId}'
    Metadata = lara_audio.read_ldt_metadata_file(SegmentVideoDir)
    NewMetadata = convert_segment_video_metadata(Metadata, SegmentDict)
    lara_utils.copy_directory_one_file_at_a_time(SegmentVideoDir, NewSegmentVideoDir, [ 'webm' ])
    lara_audio.write_ldt_metadata_file(NewMetadata, NewSegmentVideoDir)
    return NewSegmentVideoDir

def convert_segment_video_metadata(Metadata, SegmentDict):
    return [ convert_segment_video_metadata_item(Item, SegmentDict) for Item in Metadata ]

"""
Metadata items look like this:

{
        "file": "705999_200612_190200665.webm",
        "source": null,
        "text": "T\u00edna fer \u00ed fr\u00ed"
    }
"""

def convert_segment_video_metadata_item(Item, SegmentDict):
    if Item['text'] in SegmentDict:
        Item1 = copy.copy(Item)
        Item1['text'] = SegmentDict[Item['text']]
        return Item1
    else:
        return Item

def update_word_sign_dir(Params, SignerId, SignLang, WordDict):
    WordVideoDir = Params.word_audio_directory
    if WordVideoDir == '':
        return ''
    NewWordVideoDir = f'$LARA/Content/{SignLang}/audio/{SignerId}'
    OldMetadata = lara_audio.read_ldt_metadata_file(WordVideoDir)
    lara_utils.print_and_flush(f'--- Read {len(OldMetadata)} metadata items from {WordVideoDir}')
    SignMetadata = lara_audio.read_ldt_metadata_file(NewWordVideoDir)
    lara_utils.print_and_flush(f'--- Read {len(SignMetadata)} metadata items from {NewWordVideoDir}')
    WordsSignsFiles = [ ( Word, WordDict[Word], find_word_in_word_metadata(Word, OldMetadata) )
                        for Word in WordDict
                        if WordDict[Word] != '' and find_word_in_word_metadata(Word, OldMetadata) != False ]
    lara_utils.print_and_flush(f'--- Found {len(WordsSignsFiles)} words with sign translation and associated sign file')
    for ( Word, Sign, File) in WordsSignsFiles:
        SourceFile = f'{WordVideoDir}/{File}'
        TargetFile = f'{NewWordVideoDir}/{File}'
        if lara_utils.file_exists(SourceFile):
            lara_utils.copy_file(SourceFile, TargetFile)
            if not find_word_in_word_metadata(Word, SignMetadata):
                SignMetadata += [ { 'file': File, 'text': lara_audio.make_word_canonical_for_word_recording(Sign) } ]
        else:
            lara_utils.print_and_flush(f'*** Warning: file not found: {SourceFile}')
    lara_audio.write_ldt_metadata_file(SignMetadata, NewWordVideoDir)
    return NewWordVideoDir

def find_word_in_word_metadata(Word, Metadata):
    for Record in Metadata:
        if isinstance(Record, dict) and 'text' in Record and \
           Record['text'] == Word or Record['text'] == f'að {Word}':
            return Record['file']
    return False

def convert_segment_translation_spreadsheet(Params, SignLang, TargetLang, SegmentDict, NewProjectDir):
    if Params.segment_translation_spreadsheet == '':
        return ''
    SegmentTranslationCSV = Params.segment_translation_spreadsheet
    NewSegmentTranslationCSV = f'{NewProjectDir}/translations/{SignLang}_{TargetLang}.csv'
    Content = lara_utils.read_lara_csv(SegmentTranslationCSV)
    NewContent = [ convert_segment_translation_spreadsheet_line(Line, SegmentDict) for Line in Content ]
    lara_utils.write_lara_csv(NewContent, NewSegmentTranslationCSV)
    return NewSegmentTranslationCSV

def convert_segment_translation_spreadsheet_line(Line, SegmentDict):
    ( Source, Target ) = Line[:2]
    Source1 = SegmentDict[Source] if Source in SegmentDict else Source
    return ( Source1, Target )

def update_word_translation_spreadsheet(Params, SignLang, TargetLang, WordDict):
    if Params.translation_spreadsheet == '':
        return ''
    WordTranslationCSV = Params.translation_spreadsheet
    Content = lara_utils.read_lara_csv(WordTranslationCSV) if lara_utils.file_exists(WordTranslationCSV) else []
    NewWordTranslationCSV = f'$LARA/Content/{SignLang}/translations/{SignLang}_{TargetLang}.csv'
    SignContent = lara_utils.read_lara_csv(NewWordTranslationCSV) if lara_utils.file_exists(NewWordTranslationCSV) else []
    NNew = 0
    for Record in Content:
        ( Word, Translation ) = Record[:2]
        Sign = look_up_word_in_word_dict(Word, WordDict)
        if Sign != False:
            Sign = WordDict[Word]
            Updated = False
            for SignRecord in SignContent:
                if SignRecord[0] == Sign:
                    SignRecord[1] = Translation
                    Updated = True
            if not Updated:
               SignContent += [ [ Sign, Translation ] ]
               NNew += 1
    if NNew > 0:
        lara_utils.write_lara_csv(SignContent, NewWordTranslationCSV)
        lara_utils.print_and_flush(f'--- {NNew} new translations added to {NewWordTranslationCSV}')
    else:
        lara_utils.print_and_flush(f'--- No new translations found, {NewWordTranslationCSV} not updated')
    return NewWordTranslationCSV

def look_up_word_in_word_dict(Word, WordDict):
    Word1 = remove_verb_prefix_if_necessary(Word)
    return WordDict[Word1] if Word1 in WordDict else False

def remove_verb_prefix_if_necessary(Word):
    verb_prefix = 'að '
    return Word[len(verb_prefix):] if Word.startswith(verb_prefix) else Word

def copy_images(Params, NewProjectDir):
    OldImageDir = Params.image_directory
    if OldImageDir == '':
        return
    NewImageDir = f'{NewProjectDir}/images'
    lara_utils.copy_directory_one_file_at_a_time(OldImageDir, NewImageDir, 'all')
    return NewImageDir

"""

A signed doc config file will look something like this:

{
    "audio_mouseover": "yes",
    "corpus": "*CORPUS_DIR*/corpus/ImportedTaggedFile.docx",
    "id": "ítm_small",
    "language": "ítm",
    "segment_audio_directory": "*CORPUS_DIR*/audio/siggi",
    "segment_translation_mouseover": "yes",
    "segment_translation_spreadsheet": "*CORPUS_DIR*/translations/ítm_english.csv",
    "translation_mouseover": "yes",
    "translation_spreadsheet": "*LANGUAGE_DIR*/translations/ítm_english.csv",
    "video_annotations": "yes",
    "word_audio_directory": "*LANGUAGE_DIR*/audio/siggi",
    "word_translations_on": "lemma"
}

"""

def convert_config(Params, NewId, SignLang, NewProjectDir,
                   NewCorpusFile, NewSegmentVideoDir, NewSegmentTranslationCSV,
                   NewWordVideoDir, NewWordTranslationCSV, NewImageDir):
    ChangeParams = { 'id': NewId,
                     'language': SignLang,
                     'corpus': NewCorpusFile,
                     'segment_audio_directory': NewSegmentVideoDir,
                     'segment_translation_spreadsheet': NewSegmentTranslationCSV,
                     'word_audio_directory': NewWordVideoDir, 
                     'translation_spreadsheet': NewWordTranslationCSV,
                     'image_directory': NewImageDir
                     }
    NewParams = lara_utils.merge_dicts(Params, ChangeParams)
    NewConfigFile = f'{NewProjectDir}/corpus/local_config.json'
    lara_utils.write_json_to_file(non_default_params(NewParams), NewConfigFile)
    return NewConfigFile

def non_default_params(Params):
    FeatDict = lara_config.items_in_lara_local_config_data
    return { Key: Params[Key] for Key in Params
             if Key in FeatDict and Params[Key] != FeatDict[Key]['default'] }

# -----------------------------------------

def text_word_videos_to_sign_videos(WordVideoDir, SignVideoDir, RecordingFile):
    lara_utils.create_directory_deleting_old_if_necessary(SignVideoDir)
    WordMetadata = lara_audio.read_ldt_metadata_file(WordVideoDir)
    WordMetadataDict = index_metadata_by_canonical_form_of_word(WordMetadata)
    RecordingData = lara_utils.read_json_file(RecordingFile)
    SignMetadata = process_recording_data_for_word_to_sign(RecordingData, WordMetadataDict, WordVideoDir, SignVideoDir)
    lara_audio.write_ldt_metadata_file(SignMetadata, SignVideoDir)

##    Typical metadata item
##
##    {
##        "file": "849730_200821_165308277.webm",
##        "source": null,
##        "text": "að fara"
##    },

def index_metadata_by_canonical_form_of_word(WordMetadata):
    Dict = {}
    for Item in WordMetadata:
        if isinstance(Item, dict) and ( 'text' in Item or 'source' in Item ) \
           and 'file' in Item and Item['file'] != '':
           #and not blue_shirt_video(Item['file'])
            if 'source' in Item and Item['source'] != '' and Item['source'] != None:
                Text = Item['source']
            else:
                Text = Item['text']
            Canonical = canonical_form_of_icelandic_lemma(Text)
            Dict[Canonical] = Item
    lara_utils.print_and_flush(f'--- Found {len(Dict.keys())} usable word videos')
    return Dict

def canonical_form_of_icelandic_lemma(Lemma):
    Components = Lemma.split()
    if len(Components) == 2 and Components[0] == 'að':
        return Components[1]
    else:
        return Lemma

def process_recording_data_for_word_to_sign(RecordingData, WordMetadataDict, WordVideoDir, SignVideoDir):
    ( NewMetadata, NTransferredRecords ) = ( [], 0 )
    for Item in RecordingData:
        if isinstance(Item, dict) and 'text' in Item:
            Text = Item['text']
            if Text in WordMetadataDict:
                OriginalRecord = WordMetadataDict[Text]
                VideoFile = OriginalRecord['file']
                NewRecord = copy.copy(OriginalRecord)
                NewRecord['text'] = Text
                NewMetadata += [ NewRecord ]
                NTransferredRecords += 1
                lara_utils.copy_file(f'{WordVideoDir}/{VideoFile}', f'{SignVideoDir}/{VideoFile}')
    lara_utils.print_and_flush(f'--- Transferred {NTransferredRecords} records')
    return NewMetadata

# Last blue shirt video is 706038_200612_174735813.webm
    
def blue_shirt_video(VideoFile):
    Components = VideoFile.split('_')
    return lara_utils.safe_string_to_int(Components[0]) <= 706038

# -----------------------------------------

_recycled_sign_spreadsheet = '$LARA/Content/tina_ítm/MissingSigns/missing_signs.csv'

_tsw_dir = '$LARA/Content/tina_ítm/MissingSigns/tina_signed_words_staging'

_pstw_dir = '$LARA/Content/tina_ítm/MissingSigns/tina_pure_signed_text_words'

_recycled_sign_dir = '$LARA/Content/tina_ítm/MissingSigns/recycled_signs'

def recycle_extra_sign_videos():
    lara_utils.create_directory_deleting_old_if_necessary(_recycled_sign_dir)
    RecycledSignData = lara_utils.read_lara_csv(_recycled_sign_spreadsheet)
    TSWMetadata = lara_audio.read_ldt_metadata_file(_tsw_dir)
    PSTWMetadata = lara_audio.read_ldt_metadata_file(_pstw_dir)
    TSWMetadataDict = index_metadata_by_canonical_form_of_word(TSWMetadata)
    PSTWMetadataDict = index_metadata_by_canonical_form_of_word(PSTWMetadata)
    copy_recycled_sign_data(RecycledSignData, TSWMetadataDict, PSTWMetadataDict)

def copy_recycled_sign_data(RecycledSignData, TSWMetadataDict, PSTWMetadataDict):
    ( Good, Bad, Metadata ) = ( 0, 0, [] )
    for Line in RecycledSignData:
        if len(Line) >= 3 and Line[1] in ( 'tsw', 'pstw' ):
            ( OldWord, Type, NewWord ) = ( Line[0].strip(), Line[1], Line[2].strip().lower() )
            File = get_file_for_recycled_sign_data_line(OldWord, Type, TSWMetadataDict, PSTWMetadataDict)
            if File == False:
                Bad += 1
            else:
                Good += 1
                Metadata += [ { 'text': NewWord, 'file': File, 'source': '' } ]
                copy_recycled_file(Type, File)
    lara_utils.print_and_flush(f'--- Good = {Good}, Bad = {Bad} ')
    lara_audio.write_ldt_metadata_file(Metadata, _recycled_sign_dir)

def get_file_for_recycled_sign_data_line(OldWord, Type, TSWMetadataDict, PSTWMetadataDict):
    Dict = TSWMetadataDict if Type == 'tsw' else PSTWMetadataDict
    CanonicalOldWord = canonical_form_of_icelandic_lemma(OldWord)
    if not CanonicalOldWord in Dict:
        lara_utils.print_and_flush(f'*** Warning: cannot find "{OldWord}" in "{Type}"')
        return False
    else:
        return Dict[CanonicalOldWord]['file']
        
def copy_recycled_file(Type, File):
    FromDir = _tsw_dir if Type == 'tsw' else _pstw_dir
    ToDir = _recycled_sign_dir
    lara_utils.copy_file(f'{FromDir}/{File}', f'{ToDir}/{File}')
