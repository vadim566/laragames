
import lara_top
import lara_config
import lara_split_and_clean
import lara_audio
import lara_html
import lara_utils
import random

## External top-level call for creating the CSV files used to initialise the questionnaire database
##
##     make_human_tts_evaluation_forms(<MetadataFile>)
##
## where
##   
##   <MetadataFile> is a JSON-formatted file where the items are of the form
##
##    "<Language>": { 
##		"file": "<OutputFile>",
##		"data": [ 
##			    {   "id": "<Id>",
##				"human": "<HumanAudioConfigFile>",
##				"tts": "<TTSAudioConfigFile>",
##				"word_time": <MinutesOfWordAudio>,
##				"segment_time": <MinutesOfSegmentAudio>
##			    }
##			]
##	},
##
## where
##
## <Language> is the name of the language  
## <Id> is an ID
## <HumanAudioConfigFile> is the LARA config file for the human audio project
## <TTSAudioConfigFile> is the LARA config file for the TTS audio project, which must have the same text as the human audio config file    
## <MinutesOfWordAudio> is the approximate total number of minutes of word audio to select
## <MinutesOfSegmentAudio> is the approximate total number of minutes of segment audio to select, or "all" to use all segment audio
##
## Typical example:
##
##	"english": { 
##		"file": "$LARA/tmp/lrec_2022_english_shortened.csv",
##		"data": [   
##					{  "id": "lpp_english",
##						"human": "$LARA/Content/the_little_prince_lrec2022/corpus/local_config_shortened.json",
##						"tts": "$LARA/Content/the_little_prince_lrec2022/corpus/local_config_tts_shortened.json",
##						"word_time": 0.0,
##						"segment_time": "all"
##					}
##				]
##	},
    
def make_human_tts_evaluation_forms(MetadataFile):
    Metadata = lara_utils.read_json_file(MetadataFile)
    if Metadata == False:
        return
    if not isinstance(Metadata, dict):
        lara_utils.print_and_flush(f'*** Error: metadata file {MetadataFile} does not contain a dict')
    CorpusIds = Metadata.keys()
    Format = 'default'
    Mode = 'csv'
    DirOrId = 'dir_lrec_2022'
    make_eurocall_evaluation_forms1(Format, MetadataFile, CorpusIds, Mode, DirOrId)

## External top-level call for formatting questionnaire data downloaded from database:
##
##     format_human_tts_data(<SegmentFile>, <OverallFile>, <VoiceRatingFile>, <ResultsDir>)
##
## where
##
##   <SegmentFile> is a CSV file with format and example
##
##   Lang    UserID Sex  DoB  Education    Level      Teacher Hearing  Reading V1  Text     Score
##   English 26     male 1997 postgraduate nearNative yes     no       no      tts lettuces 4																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																				
##
##   <VoiceRatingFile> is a CSV file with format and example
##
##   Lang    UserID    Version  Question  Score
##   English 19        1        6         5
##
##   <OverallFile> is a CSV file with format and example
##
##   Lang    UserID Sex  DoB  Education    Level  T  H  R  VersionFirst V1Comment            V2Comment                              Comment StartTime             EndTime
##   English 45     male 1959 postgraduate native no no no tts	        "cold and monotone." "more natural, clearer pronunciation"  "NULL"  "2021-05-24 02:48:03" "2021-05-24 02:57:28"
##
##   <ResultsDir> is the directory in which to place results
																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																   
def format_human_tts_data(SegmentFile, OverallFile, VoiceRatingFile, ResultsDir):
    JSONFile = f'{ResultsDir}/Data.json'
    SentenceSummaryFile = f'{ResultsDir}/SentenceSummary.txt'
    VoiceSummaryFile = f'{ResultsDir}/VoiceSummary.txt'
    LanguageTableFile = f'{ResultsDir}/LanguageTable.html'
    VoiceTableFile = f'{ResultsDir}/VoiceTable.html'
    LanguageAndVoiceTableFile = f'{ResultsDir}/LanguageAndVoiceTable.html'
    FreeformCommentFile = f'{ResultsDir}/FreeformComments.html'
    lara_utils.create_directory_if_it_doesnt_exist(ResultsDir)
    lara_utils.delete_file_if_it_exists(JSONFile)
    organise_eurocall_data(SegmentFile, OverallFile, VoiceRatingFile, JSONFile)
    if not lara_utils.file_exists(JSONFile):
        return
    Format = 'default'
    summarise_eurocall_data(Format, JSONFile, SentenceSummaryFile, VoiceSummaryFile,
                            LanguageTableFile, VoiceTableFile, LanguageAndVoiceTableFile, FreeformCommentFile)
 
def make_all_eurocall_evaluation_forms():
    _all_corpus_ids = [ 'danish', 'english', 'farsi', 'french', 'icelandic',
                        'irish', 'italian', 'mandarin', 'spanish', 'swedish' ]
    make_eurocall_evaluation_forms(_all_corpus_ids, 'csv', 'id')

def make_all_lrec_2022_evaluation_forms():
    _all_corpus_ids = [ 'english', 'french', 'italian', 'polish',
                        'farsi', 'slovak', 'icelandic', 'irish',
                        'japanese' ]
    make_lrec_2022_evaluation_forms(_all_corpus_ids, 'csv', 'dir_lrec_2022')

def make_all_lrec_2022_evaluation_forms_shortened():
    _all_corpus_ids_shortened = [ 'english', 'french', 'italian', 'polish',
                                  'farsi', 'slovak', 'icelandic', 'irish',
                                  'japanese', 'mandarin' ]
    make_lrec_2022_evaluation_forms_shortened(_all_corpus_ids_shortened, 'csv', 'dir_lrec_2022')

##def make_eurocall_evaluation_form(MetadataFile, LanguageId):
##    make_eurocall_evaluation_forms1(MetadataFile, [ LanguageId ], 'csv', 'id')

def make_eurocall_evaluation_forms(CorpusIds, Mode, DirOrId):
    MetadataFile = '$LARA/Code/Python/eurocall_2021_eval_data.json'
    make_eurocall_evaluation_forms1('eurocall_2021', MetadataFile, CorpusIds, Mode, DirOrId)

def make_lrec_2022_evaluation_forms(CorpusIds, Mode, DirOrId):
    MetadataFile = '$LARA/Code/Python/lrec_2022_eval_data.json'
    make_eurocall_evaluation_forms1('lrec_2022', MetadataFile, CorpusIds, Mode, DirOrId)

def make_lrec_2022_evaluation_forms_shortened(CorpusIds, Mode, DirOrId):
    MetadataFile = '$LARA/Code/Python/lrec_2022_eval_data_shortened.json'
    make_eurocall_evaluation_forms1('lrec_2022', MetadataFile, CorpusIds, Mode, DirOrId)

_known_formats = ( 'default', 'eurocall_2021', 'lrec_2022' )

def make_eurocall_evaluation_forms1(Format, MetadataFile, CorpusIds, Mode, DirOrId):
    if not Format in _known_formats:
        lara_utils.print_and_flush(f'*** Error: bad 1st argument {Format} to make_eurocall_evaluation_forms1, needs to be in {_known_formats}')
        return False
    if not DirOrId in ( 'id', 'dir', 'dir_lrec_2022' ):
        lara_utils.print_and_flush(f'*** Error: bad 5th argument {DirOrId} to make_eurocall_evaluation_forms1, needs to be "id", "dir" or "dir_lrec_2022"')
        return False
    Metadata = lara_utils.read_json_file(MetadataFile)
    lara_utils.print_and_flush(f'Creating data for {CorpusIds}')
    for CorpusId in CorpusIds:
        lara_utils.print_and_flush(f'----------------- {CorpusId} --------------------------')
        if not CorpusId in Metadata:
            lara_utils.print_and_flush(f'*** Error: item "{CorpusId}" is not defined in {MetadataFile}')
            return False
        lara_utils.print_and_flush(f'--- CREATING DATA FOR "{CorpusId}"')
        Metadata1 = Metadata[CorpusId]
        Metadata2 = Metadata1['data']
        File0 = Metadata1['file']
        File = File0.replace('csv', 'json') if Mode == 'json' else File0
        Data = make_eurocall_evaluation_form_data(Metadata2, DirOrId)
        if Data != False:
            write_out_evaluation_form_data(Format, Data, Mode, DirOrId, CorpusId, File)

def make_eurocall_evaluation_form_data(MetadataList, DirOrId):
    Data = []
    for Item in MetadataList:
        Id = Item['id']
        HumanConfigFile = Item['human']
        TTSConfigFile = Item['tts']
        WordTime = Item['word_time']
        SegmentTime = Item['segment_time']
        lara_utils.print_and_flush(f'--- CREATING DATA FOR "{Id}"')
        NewData = make_random_evaluation_form_data(HumanConfigFile, TTSConfigFile, WordTime, SegmentTime)
        if NewData == False:
            lara_utils.print_and_flush('*** Error: something went wrong')
            return False
        else:
            Data += NewData
    return Data

##def make_random_evaluation_form(HumanConfigFile, TTSConfigFile, NWordItems, NSegmentItems, DirOrId, Mode, OutFileOrDir):
##    Data = make_random_evaluation_form_data(HumanConfigFile, TTSConfigFile, NWordItems, NSegmentItems)
##    write_out_evaluation_form_data(Data, Mode, DirOrId, OutFileOrDir)

def write_out_evaluation_form_data(Format, Data, Mode, DirOrId, CorpusId, OutFileOrDir):
    if not Mode in ( 'html', 'json', 'csv' ):
        lara_utils.print_and_flush(f'*** Error: unknown mode {Mode}')
        return
    if Mode == 'html':
        evaluation_form_data_to_dir(Data, OutFileOrDir)
    elif Mode == 'json':
        #lara_utils.write_json_to_file(Data, OutFileOrDir)
        lara_utils.write_json_to_file_plain_utf8(Data, OutFileOrDir)
    elif Mode == 'csv':
        CSVData = evaluation_data_to_csv_form(Format, Data, DirOrId, CorpusId)
        if DirOrId == 'dir_lrec_2022':
            lara_utils.write_lara_comma_csv(CSVData, OutFileOrDir)
        else:
            lara_utils.write_lara_csv(CSVData, OutFileOrDir)

def make_random_evaluation_form_data(HumanConfigFile, TTSConfigFile, NWordItems0, NSegmentItems0):
    NWordItems = coerce_to_number_or_all(NWordItems0)
    NSegmentItems = coerce_to_number_or_all(NSegmentItems0)
    if NWordItems == False and isinstance(NWordItems, bool):
        lara_utils.print_and_flush(f'*** Error: {NWordItems0} not a number')
        return False
    if NSegmentItems == False and isinstance(NWordItems, bool):
        lara_utils.print_and_flush(f'*** Error: {NSegmentItems0} not a number')
        return False
    WordItems = make_random_evaluation_form_data_words(HumanConfigFile, TTSConfigFile, NWordItems)
    SegmentItems = make_random_evaluation_form_data_segments(HumanConfigFile, TTSConfigFile, NSegmentItems)
    return WordItems + SegmentItems

def coerce_to_number_or_all(StrOrNumber):
    if StrOrNumber == 'all':
        return 'all'
    elif isinstance(StrOrNumber, int) or isinstance(StrOrNumber, float):
        return StrOrNumber
    elif isinstance(StrOrNumber, str):
        return lara_utils.safe_string_to_number(StrOrNumber)
    else:
        lara_utils.print_and_flush(f'*** Warning: {StrOrNumber} is not a string or a number')
        return False

def make_random_evaluation_form_data_words(HumanConfigFile, TTSConfigFile, NItems):
    if NItems == 0 or NItems == 0.0:
        return []
    OrderedWords = get_words_from_config(HumanConfigFile)
    ( HumanId, HumanWordDir, HumanMetadataDict ) = get_word_audio_data_from_config(HumanConfigFile)
    ( TTSId, TTSWordDir, TTSMetadataDict ) = get_word_audio_data_from_config(TTSConfigFile)
    if HumanMetadataDict == False or TTSMetadataDict == False:
        return []
    return make_random_evaluation_form_data1(OrderedWords, HumanId, HumanWordDir, HumanMetadataDict, TTSId, TTSWordDir, TTSMetadataDict, NItems, 'words')

def make_random_evaluation_form_data_segments(HumanConfigFile, TTSConfigFile, NItems):
    if NItems == 0 or NItems == 0.0:
        return []
    OrderedSegments = get_segments_from_config(HumanConfigFile)
    ( HumanId, HumanSegmentDir, HumanMetadataDict ) = get_segment_audio_data_from_config(HumanConfigFile)
    ( TTSId, TTSSegmentDir, TTSMetadataDict ) = get_segment_audio_data_from_config(TTSConfigFile)
    if HumanMetadataDict == False or TTSMetadataDict == False:
        return []
    return make_random_evaluation_form_data1(OrderedSegments, HumanId, HumanSegmentDir, HumanMetadataDict, TTSId, TTSSegmentDir, TTSMetadataDict, NItems, 'segments')

def get_words_from_config(ConfigFile):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    SplitFile = lara_top.lara_tmp_file('split', Params)
    Words = lara_audio.get_words_from_page_oriented_split_list(lara_split_and_clean.read_split_file(SplitFile, Params), Params)
    random.shuffle(Words)
    return Words

def get_segments_from_config(ConfigFile):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    SplitFile = lara_top.lara_tmp_file('split', Params)
    SplitFileData = lara_split_and_clean.read_split_file(SplitFile, Params)
    if SplitFileData == False:
        lara_utils.print_and_flush(f'*** Error: unable to create {SplitFile}')
        return False
    return [ MinimallyCleaned for ( PageInfo, Chunks) in SplitFileData for ( Raw, MinimallyCleaned, Pairs, Tag ) in Chunks
             if MinimallyCleaned != '' ]

def get_word_audio_data_from_config(ConfigFile):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    Id = Params.id
    WordDir = Params.word_audio_directory
    if WordDir == '':
        lara_utils.print_and_flush(f'*** Error: word audio directory not defined for {ConfigFile}')
        return ( False, False, False )
    if not lara_utils.directory_exists(WordDir):
        lara_utils.print_and_flush(f'*** Error: word audio directory {WordDir} not found for {ConfigFile}')
        return ( False, False, False )
    Metadata = lara_audio.read_ldt_metadata_file(WordDir)
    MetadataDict = { Item['text'] : Item['file'] for Item in Metadata }
    return ( Id, WordDir, MetadataDict )

def get_segment_audio_data_from_config(ConfigFile):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    Id = Params.id
    SegmentDir = Params.segment_audio_directory
    if SegmentDir == '':
        lara_utils.print_and_flush(f'*** Error: segment audio directory not defined for {ConfigFile}')
        return ( False, False, False )
    if not lara_utils.directory_exists(SegmentDir):
        lara_utils.print_and_flush(f'*** Error: segment audio directory {SegmentDir} not found for {ConfigFile}')
        return ( False, False, False )
    Metadata = lara_audio.read_ldt_metadata_file(SegmentDir)
    MetadataDict = { Item['text'] : Item['file'] for Item in Metadata }
    return ( Id, SegmentDir, MetadataDict )

def make_random_evaluation_form_data1(OrderedSegments, HumanId, HumanSegmentDir, HumanMetadataDict, TTSId, TTSSegmentDir, TTSMetadataDict, NItemsOrMaxTime, WordsOrSegments):
    if NItemsOrMaxTime == 'all':
        return make_random_evaluation_form_data_all(OrderedSegments, HumanId, HumanSegmentDir, HumanMetadataDict, TTSId, TTSSegmentDir, TTSMetadataDict, WordsOrSegments)
    elif isinstance(NItemsOrMaxTime, int):
        return make_random_evaluation_form_data_count(OrderedSegments, HumanId, HumanSegmentDir, HumanMetadataDict, TTSId, TTSSegmentDir, TTSMetadataDict, NItemsOrMaxTime, WordsOrSegments)
    elif isinstance(NItemsOrMaxTime, float):
        return make_random_evaluation_form_data_time(OrderedSegments, HumanId, HumanSegmentDir, HumanMetadataDict, TTSId, TTSSegmentDir, TTSMetadataDict, NItemsOrMaxTime, WordsOrSegments)
    else:
        lara_utils.print_and_flush(f'*** Error: eighth argument to make_random_evaluation_form_data1, "{NItemsOrMaxTime}" must be number.')
        return False

def make_random_evaluation_form_data_all(OrderedSegments, HumanId, HumanSegmentDir, HumanMetadataDict, TTSId, TTSSegmentDir, TTSMetadataDict, WordsOrSegments):
    AnnotatedOrderedSegments = [ annotate_segment(Segment, HumanId, HumanSegmentDir, HumanMetadataDict, TTSId, TTSSegmentDir, TTSMetadataDict)
                                 for Segment in OrderedSegments ]
    return [ AnnotatedSegment for AnnotatedSegment in AnnotatedOrderedSegments if AnnotatedSegment != False ]

def make_random_evaluation_form_data_count(OrderedSegments, HumanId, HumanSegmentDir, HumanMetadataDict, TTSId, TTSSegmentDir, TTSMetadataDict, NItems, WordsOrSegments):
    _max_attempts = 500
    N = len(OrderedSegments)
    if N < NItems:
        lara_utils.print_and_flush(f'*** Error: cannot create {NItems} examples, there are only {N} segments.')
    AnnotatedOrderedSegments = [ annotate_segment(Segment, HumanId, HumanSegmentDir, HumanMetadataDict, TTSId, TTSSegmentDir, TTSMetadataDict)
                                 for Segment in OrderedSegments ]
    NAttempts = 0
    random.seed()
    while True:
        I = random.randint(0, N - NItems)
        Data = AnnotatedOrderedSegments[I : I + NItems]
        if not False in Data:
            lara_utils.print_and_flush(f'--- Generated examples for {len(Data)} {WordsOrSegments}')
            return Data
        NAttempts += 1
        if NAttempts > _max_attempts:
            lara_utils.print_and_flush(f'*** Error: cannot create {NItems} examples after {_max_attempts} attempts.')
            return False

def make_random_evaluation_form_data_time(OrderedSegments, HumanId, HumanSegmentDir, HumanMetadataDict, TTSId, TTSSegmentDir, TTSMetadataDict, MaxTimeInMinutes, WordsOrSegments):
    _max_attempts = 500
    MaxTimeInSeconds = 60.0 * MaxTimeInMinutes
    N = len(OrderedSegments)
    AnnotatedOrderedSegments = [ annotate_segment(Segment, HumanId, HumanSegmentDir, HumanMetadataDict, TTSId, TTSSegmentDir, TTSMetadataDict)
                                 for Segment in OrderedSegments ]
    NAttempts = 0
    random.seed()
    while True:
        I = random.randint(0, N)
        ( TotalTime, Data ) = sequence_of_segments_starting_at_given_index_under_max_time(AnnotatedOrderedSegments, I, MaxTimeInSeconds)
        if Data != False:
            lara_utils.print_and_flush(f'--- Generated examples for {int(TotalTime)} seconds of {WordsOrSegments} ({len(Data)} items)')
            return Data
        NAttempts += 1
        if NAttempts > _max_attempts:
            lara_utils.print_and_flush(f'*** Error: cannot create examples after {_max_attempts} attempts.')
            return False

def sequence_of_segments_starting_at_given_index_under_max_time(AnnotatedOrderedSegments, I, MaxTimeInSeconds):
    ( TotalTime, Data, N ) = ( 0.0, [], len(AnnotatedOrderedSegments) )
    for J in range(I, N):
        Segment = AnnotatedOrderedSegments[J]
        if Segment == False:
            return ( False, False )
        NewTime = time_for_segment(Segment)
        if TotalTime + NewTime > MaxTimeInSeconds:
            return ( TotalTime, Data )
        else:
            TotalTime += time_for_segment(Segment)
            Data += [ Segment ]
    # Our combined segments probably weren't long enough
    return ( False, False )

def time_for_segment(Item):
    HumanAudioFile = Item['human_audio_file']
    HumanAudioDir = Item['human_audio_dir']
    TTSAudioFile = Item['tts_audio_file']
    TTSAudioDir = Item['tts_audio_dir']
    return length_of_mp3_file_in_seconds(f'{HumanAudioDir}/{HumanAudioFile}') + length_of_mp3_file_in_seconds(f'{TTSAudioDir}/{TTSAudioFile}')

def annotate_segment(Segment, HumanId, HumanSegmentDir, HumanMetadataDict, TTSId, TTSSegmentDir, TTSMetadataDict):
    if Segment in HumanMetadataDict and Segment in TTSMetadataDict:
        return { 'text': Segment,
                 'human_id': HumanId,
                 'human_audio_file': HumanMetadataDict[Segment],
                 'human_audio_dir': HumanSegmentDir,
                 'tts_id': TTSId,
                 'tts_audio_file': TTSMetadataDict[Segment],
                 'tts_audio_dir': TTSSegmentDir
                 }
    else:
        return False

def evaluation_data_to_csv_form(Format, Data, DirOrId, CorpusId):
    if DirOrId == 'dir':
        Header = [ 'text', 'human_audio_file', 'human_audio_dir', 'tts_audio_file', 'tts_audio_dir' ]
    elif DirOrId == 'dir_lrec_2022':
        if not CorpusId in lara_config._corpus_id_to_number:
            lara_utils.print_and_flush(f'*** Error: unknown corpus id "{CorpusId}"')
            return []
        else:
            CorpusNumber = lara_config._corpus_id_to_number[CorpusId]
        Header = [ 'QuestionnaireID', 'SegmentNumber', 'SegmentText', 'HumanAudioDir', 'HumanAudioFile', 'TtsAudioDir', 'TtsAudioFile' ]
    else:
        Header = [ 'text', 'human_audio_file', 'human_id', 'tts_audio_file', 'tts_id' ]
    return [ Header ] + [ evaluation_item_to_csv_line(Data[I], I, CorpusNumber, DirOrId) for I in range(0, len(Data))
                          if not fake_text_item(Data[I]['text'], Format) ]

# For LREC 2022, we aren't interested in the chapter titles
def fake_text_item(Text, Format):
    _chapter_titles = ( '2', '4', '8', '9' )
    return Format == 'lrec_2022' and Text.strip() in _chapter_titles

# QuestionnaireID   SegmentNumber   SegmentText	HumanAudioDir	            HumanAudioFile	    TtsAudioDir	                    TtsAudioFile
# 2	            3	            lettuces	prvocabpages/multimedia/    52275_190309121428.mp3  pr_ttsvocabpages/multimedia/    tts_2021-03-02_15-39-43_6208830123.mp3

def evaluation_item_to_csv_line(Item, Index, CorpusNumber, DirOrId):
    if DirOrId == 'dir':
        return [ Item['text'], Item['human_audio_file'], Item['human_audio_dir'], Item['tts_audio_file'], Item['tts_audio_dir'] ]
    if DirOrId == 'dir_lrec_2022':
        HumanAudioDirWeb = f"{Item['human_id']}vocabpages/multimedia/"
        TTSAudioDirWeb = f"{Item['tts_id']}vocabpages/multimedia/"
        return [ CorpusNumber, Index + 1, Item['text'], HumanAudioDirWeb, Item['human_audio_file'], TTSAudioDirWeb, Item['tts_audio_file'] ]
    else:
        return [ Item['text'], Item['human_audio_file'], Item['human_id'], Item['tts_audio_file'], Item['tts_id'] ]

def evaluation_form_data_to_dir(Data, Dir):
    if Data == False:
        return
    lara_utils.create_directory_deleting_old_if_necessary(Dir)
    AudioDir = f'{Dir}/audio'
    lara_utils.create_directory_deleting_old_if_necessary(AudioDir)
    FormFile = f'{Dir}/form.html'
    evaluation_form_data_to_form_file(Data, FormFile)
    write_script_file(Dir)
    for Item in Data:
        copy_audio_files_in_item(Item, AudioDir)
    lara_utils.print_and_flush(f'--- Created evaluation directory {Dir}')

def write_script_file(Dir):
    PlaysoundFunction = lara_html.playsound_scriptfunction([])
    lara_utils.write_lara_text_file(PlaysoundFunction, f'{Dir}/_script_.js')

def evaluation_form_data_to_form_file(Data, File):
    Header = evaluation_form_header()
    BodyLines = [ evaluation_form_line_for_item(Data[I], I) for I in range(0, len(Data)) ]
    Footer = evaluation_form_footer()
    AllLines = '\n'.join(Header + BodyLines + Footer)
    lara_utils.write_lara_text_file(AllLines, File)

def evaluation_form_header():
    return [f'<html>',  
	    f'<head>',
	    f'<title>Evaluation form</title>',
	    f'<meta http-equiv="Content-Type" content="text/html;charset=UTF-8">',
	    f'<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.0/jquery.min.js"></script>',
            f'<script src="_script_.js"></script>'
	    '</head>',
	    '<body>'
            ]

def evaluation_form_footer():
    return ['<div id="audio_container" style="width:0;height:0;overflow:hidden"></div>'
            '</div>',
            '</body>',
            '</html>'
            ]

def evaluation_form_line_for_item(Item, I):
    Text = Item['text']
    HumanAudioFile = Item['human_audio_file']
    HumanAudioDir = Item['human_audio_dir']
    TTSAudioFile = Item['tts_audio_file']
    TTSAudioDir = Item['tts_audio_dir']
    TextLine = f'<p>{Text}</p>'
    AudioLine = f"<p>{text_with_audio_file_link('Human audio', HumanAudioFile)}&nbsp;&nbsp;&nbsp;{text_with_audio_file_link('TTS audio', TTSAudioFile)}</p>"
    FeedbackLines = feedback_lines(I)
    return '\n'.join([ TextLine ] + [ AudioLine ] + FeedbackLines + [ '<hr>' ] )

def feedback_lines(I):
    Lines = ['<form>',
             '<input type="radio" id="both_good" name="feedback_{I}" value="both_good">',
             '<label for="both_good">Both acceptable and about equally good</label><br>',
             '<input type="radio" id="human_better" name="feedback_{I}" value="human_better">',
             '<label for="human_better">Both acceptable, but human audio is clearly better</label><br>',
             '<input type="radio" id="tts_better" name="feedback_{I}" value="tts_better">',
             '<label for="tts_better">Both acceptable, but TTS audio is clearly better</label><br>',
             '<input type="radio" id="human_only" name="feedback_{I}" value="human_only">',
             '<label for="human_only">Human audio is acceptable, TTS audio is not acceptable</label><br>',
             '<input type="radio" id="tts_only" name="feedback_{I}" value="tts_only">',
             '<label for="human_only">Human audio is not acceptable, TTS audio is acceptable</label><br>',
             '<input type="radio" id="both_bad" name="feedback_{I}" value="both_bad">',
             '<label for="both_bad">Neither one is acceptable</label><br>',
             '</form>']
    return Lines

def text_with_audio_file_link(Text, File):
    return f'<span class="sound" onclick="playSound(\'./audio/{File}\');"><u><i>{Text}</i></u></span>'

def copy_audio_files_in_item(Item, AudioDir):
    HumanAudioFile = Item['human_audio_file']
    HumanAudioDir = Item['human_audio_dir']
    TTSAudioFile = Item['tts_audio_file']
    TTSAudioDir = Item['tts_audio_dir']
    lara_utils.copy_file(f'{HumanAudioDir}/{HumanAudioFile}', f'{AudioDir}/{HumanAudioFile}')
    lara_utils.copy_file(f'{TTSAudioDir}/{TTSAudioFile}', f'{AudioDir}/{TTSAudioFile}')

# ----------------------------------

def average_length_of_mp3_dir_files_in_seconds(Dir):
    Files = lara_utils.directory_files(Dir)
    Lengths0 = [ length_of_mp3_file_in_seconds(f'{Dir}/{File}') for File in Files if lara_utils.extension_for_file(File) == 'mp3' ]
    Lengths = [ Length for Length in Lengths0 if Length != False ]
    return sum(Lengths) / len(Lengths)

def length_of_mp3_file_in_seconds(file):
    from mutagen.mp3 import MP3
    try:
        audio = MP3(lara_utils.absolute_file_name(file))
        return audio.info.length
    except:
        return False
    
# ----------------------------------

def make_farsi_tts_metadata_files():
    metadata_file_to_tts_form('$LARA/tmp_resources/Novin_Farsi_Learning-Book_three_record_segments_full.json',
                              '$LARA/tmp_resources/Novin_Farsi_Learning-Book_three_tts_record_segments_full.json')
    metadata_file_to_tts_form('$LARA/tmp_resources/Novin_Farsi_Learning-Book_four_record_segments_full.json',
                              '$LARA/tmp_resources/Novin_Farsi_Learning-Book_four_tts_record_segments_full.json')
    metadata_file_to_tts_form('$LARA/tmp/farsi_export/farsi/audio/elhamakhlaghi80@gmail.com/metadata_help.json',
                              '$LARA/tmp_resources/farsi_word_tts.json')

def metadata_file_to_tts_form(FileIn, FileOut):
    random.seed()
    Timestamp = lara_utils.timestamp()
    StartN = random.randint(1, 1000000000000)
    Index = 0
    DataIn = lara_utils.read_json_file(FileIn)
    DataOut = []
    for Item in DataIn:
        Text = Item['text']
        DataOut += [ { 'text': Text, 'file' : f'tts_{Timestamp}_{StartN + Index}.mp3' } ]
        Index += 1
    lara_utils.write_json_to_file_plain_utf8(DataOut, FileOut)
    
# ----------------------------------

def process_data(Operation):
    if Operation == 'convert_to_json_eurocall_2021':
        SegmentFile = '$LARA/Doc/EuroCALLTTSResults/EuroCallSegmentFinal.csv'
        VoiceRatingFile = '$LARA/Doc/EuroCALLTTSResults/EuroCallVoiceRatings.csv'
        OverallFile = '$LARA/Doc/EuroCALLTTSResults/EuroCallOverallFinal.csv'
        JSONFile = '$LARA/Doc/EuroCALLTTSResults/EuroCallFinal.json'
        organise_eurocall_data(SegmentFile, OverallFile, VoiceRatingFile, JSONFile)
    if Operation == 'summarise_eurocall_2021':
        Format = 'eurocall_2021'
        JSONFile = '$LARA/Doc/EuroCALLTTSResults/EuroCallFinal.json'
        SentenceSummaryFile = '$LARA/Doc/EuroCALLTTSResults/EuroCallSummary.txt'
        VoiceSummaryFile = '$LARA/Doc/EuroCALLTTSResults/EuroCallVoiceSummary.txt'
        LanguageTableFile = '$LARA/Doc/EuroCALLTTSResults/EuroCallLanguageTable.html'
        VoiceTableFile = '$LARA/Doc/EuroCALLTTSResults/EuroCallVoiceTable.html'
        LanguageAndVoiceTableFile = '$LARA/Doc/EuroCALLTTSResults/EuroCallLanguageAndVoiceTable.html'
        FreeformCommentFile = '$LARA/Doc/EuroCALLTTSResults/EuroCallFreeformComments.html'
        summarise_eurocall_data(Format, JSONFile, SentenceSummaryFile, VoiceSummaryFile,
                                LanguageTableFile, VoiceTableFile, LanguageAndVoiceTableFile, FreeformCommentFile)
    if Operation == 'convert_to_json_lrec_2022':
        SegmentFile = '$LARA/Doc/LREC2022TTS/Data/report_v2/EuroCallSegmentResponses.csv'
        VoiceRatingFile = '$LARA/Doc/LREC2022TTS/Data/report_v2/EuroCallVersionResponses.csv'
        OverallFile = '$LARA/Doc/LREC2022TTS/Data/report_v2/EuroCallVersionOverallResponses.csv'
        JSONFile = '$LARA/Doc/LREC2022TTS/Data/report_v2/LRECData.json'
        organise_eurocall_data(SegmentFile, OverallFile, VoiceRatingFile, JSONFile)
    if Operation == 'summarise_lrec_2022':
        Format = 'lrec_2022'
        JSONFile = '$LARA/Doc/LREC2022TTS/Data/report_v2/LRECData.json'
        SentenceSummaryFile = '$LARA/Doc/LREC2022TTS/Data/report_v2/LRECCallSummary.txt'
        VoiceSummaryFile = '$LARA/Doc/LREC2022TTS/Data/report_v2/LRECVoiceSummary.txt'
        LanguageTableFile = '$LARA/Doc/LREC2022TTS/Data/report_v2/LRECLanguageTable.html'
        VoiceTableFile = '$LARA/Doc/LREC2022TTS/Data/report_v2/LRECVoiceTable.html'
        LanguageAndVoiceTableFile = '$LARA/Doc/LREC2022TTS/Data/report_v2/LRECLanguageAndVoiceTable.html'
        FreeformCommentFile = '$LARA/Doc/LREC2022TTS/Data/report_v2/LRECFreeformComments.html'
        classify_lrec_2022_sentences_by_dialogue_and_humour()
        summarise_eurocall_data(Format, JSONFile, SentenceSummaryFile, VoiceSummaryFile,
                                LanguageTableFile, VoiceTableFile, LanguageAndVoiceTableFile, FreeformCommentFile)
    if Operation == 'convert_to_json_lrec_2022_v4':
        SegmentFile = '$LARA/Doc/LREC2022TTS/Data/report_v4/VQ_SegmentResponses_20220111_223428.csv'
        VoiceRatingFile = '$LARA/Doc/LREC2022TTS/Data/report_v4/VQ_VersionResponses_20220111_223512.csv'
        OverallFile = '$LARA/Doc/LREC2022TTS/Data/report_v4/VQ_VersionOverallResponses_20220111_223505.csv'
        JSONFile = '$LARA/Doc/LREC2022TTS/Data/report_v4/LRECData.json'
        organise_eurocall_data(SegmentFile, OverallFile, VoiceRatingFile, JSONFile)
    if Operation == 'summarise_lrec_2022_v4':
        Format = 'lrec_2022'
        JSONFile = '$LARA/Doc/LREC2022TTS/Data/report_v4/LRECData.json'
        SentenceSummaryFile = '$LARA/Doc/LREC2022TTS/Data/report_v4/LRECCallSummary.txt'
        VoiceSummaryFile = '$LARA/Doc/LREC2022TTS/Data/report_v4/LRECVoiceSummary.txt'
        LanguageTableFile = '$LARA/Doc/LREC2022TTS/Data/report_v4/LRECLanguageTable.html'
        VoiceTableFile = '$LARA/Doc/LREC2022TTS/Data/report_v4/LRECVoiceTable.html'
        LanguageAndVoiceTableFile = '$LARA/Doc/LREC2022TTS/Data/report_v4/LRECLanguageAndVoiceTable.html'
        FreeformCommentFile = '$LARA/Doc/LREC2022TTS/Data/report_v4/LRECFreeformComments.html'
        classify_lrec_2022_sentences_by_dialogue_and_humour()
        summarise_eurocall_data(Format, JSONFile, SentenceSummaryFile, VoiceSummaryFile,
                                LanguageTableFile, VoiceTableFile, LanguageAndVoiceTableFile, FreeformCommentFile)
    if Operation == 'convert_to_json_lrec_2022_final':
        SegmentFile = '$LARA/Doc/LREC2022TTS/Data/report_final/VQ_SegmentResponses_20220113_074508.csv'
        VoiceRatingFile = '$LARA/Doc/LREC2022TTS/Data/report_final/VQ_VersionResponses_20220113_074601.csv'
        OverallFile = '$LARA/Doc/LREC2022TTS/Data/report_final/VQ_VersionOverallResponses_20220113_074552.csv'
        JSONFile = '$LARA/Doc/LREC2022TTS/Data/report_final/LRECData.json'
        organise_eurocall_data(SegmentFile, OverallFile, VoiceRatingFile, JSONFile)
    if Operation == 'summarise_lrec_2022_final':
        Format = 'lrec_2022'
        JSONFile = '$LARA/Doc/LREC2022TTS/Data/report_final/LRECData.json'
        SentenceSummaryFile = '$LARA/Doc/LREC2022TTS/Data/report_final/LRECCallSummary.txt'
        VoiceSummaryFile = '$LARA/Doc/LREC2022TTS/Data/report_final/LRECVoiceSummary.txt'
        LanguageTableFile = '$LARA/Doc/LREC2022TTS/Data/report_final/LRECLanguageTable.html'
        VoiceTableFile = '$LARA/Doc/LREC2022TTS/Data/report_final/LRECVoiceTable.html'
        LanguageAndVoiceTableFile = '$LARA/Doc/LREC2022TTS/Data/report_final/LRECLanguageAndVoiceTable.html'
        FreeformCommentFile = '$LARA/Doc/LREC2022TTS/Data/report_final/LRECFreeformComments.html'
        classify_lrec_2022_sentences_by_dialogue_and_humour()
        summarise_eurocall_data(Format, JSONFile, SentenceSummaryFile, VoiceSummaryFile,
                                LanguageTableFile, VoiceTableFile, LanguageAndVoiceTableFile, FreeformCommentFile)
     
def organise_eurocall_data(SegmentFile, OverallFile, VoiceRatingFile, JSONFile):
    Dict = {}
    SegmentData = read_segment_data(SegmentFile)
    VoiceRatingData = read_voice_rating_data(VoiceRatingFile)
    OverallData = read_overall_data(OverallFile)
    internalise_segment_data(SegmentData, Dict)
    internalise_voice_rating_data(VoiceRatingData, Dict)
    internalise_overall_data(OverallData, Dict)
    lara_utils.write_json_to_file_plain_utf8(Dict, JSONFile)
    lara_utils.print_and_flush(f'--- Data for {len(Dict.keys())} subjects converted to JSON form')

def read_segment_data(File):
    return read_downloaded_questionnaire_data(File)

def read_voice_rating_data(File):
    return read_downloaded_questionnaire_data(File)

def read_overall_data(File):
    return read_downloaded_questionnaire_data(File)

def read_downloaded_questionnaire_data(File):
    Lines = read_lara_csv_comma_separated(File)
    #return maybe_remove_duplicate_columns(Lines)
    return Lines

##def maybe_remove_duplicate_columns(Lines):
##    if columns_appear_to_be_duplicated(Lines):
##        return remove_odd_numbered_columns(Lines)
##    else:
##        return Lines
##
##def columns_appear_to_be_duplicated(Lines):
##    if len(Lines) == 0:
##        return False
##    Len = len(FirstLine)
##    if Len % 2 != 0:
##        return False
##    for Line in Lines
##        for I in range(0, Len / 2):
##            if Line[ 2 * I ] != Line[ 2 * I + 1 ]:
##                return False
##    return True
##
##def remove_odd_numbered_columns(Lines):
##    LinesOut = []
##    for Line in Lines:
##        LinesOut += [ [ Line[ 2 * I ] for I in range(0, len(Line) / 2) ] ]
##    return LinesOut

def read_lara_csv_comma_separated(pathname):
    return read_lara_csv_custom_delimiter(pathname, ',')

def read_lara_csv_semicolon_separated(pathname):
    return read_lara_csv_custom_delimiter(pathname, ';')

def read_lara_csv_custom_delimiter(pathname, Delimiter):
    import csv
    abspathname = lara_utils.absolute_file_name(pathname)
    this_encoding = 'utf-8'
    try:
        with open(abspathname, 'r', encoding=this_encoding) as f:
            reader = csv.reader(f, delimiter=Delimiter, quotechar='"', quoting=csv.QUOTE_MINIMAL)
            List = list(reader)
        f.close()
        lara_utils.print_and_flush(f'--- Read CSV spreadsheet as {this_encoding} ({len(List)} lines) {abspathname}')
        return List
    except Exception as e:
        lara_utils.print_and_flush(f'*** Error: when trying to read CSV {abspathname} as {this_encoding}')
        lara_utils.print_and_flush(str(e))
        return False   
    
def internalise_segment_data(SegmentData, Dict):
    for Line in SegmentData:
        internalise_segment_data_line(Line, Dict)
    lara_utils.print_and_flush(f'--- Processed {len(SegmentData)} segment data lines')

def internalise_overall_data(OverallData, Dict):
    for Line in OverallData:
        internalise_overall_data_line(Line, Dict)
    lara_utils.print_and_flush(f'--- Processed {len(OverallData)} overall data lines')

def internalise_voice_rating_data(VoiceRatingData, Dict):
    for Line in VoiceRatingData:
        internalise_voice_rating_data_line(Line, Dict)
    lara_utils.print_and_flush(f'--- Processed {len(VoiceRatingData)} voice rating data lines')

# Typical segment data line
# Lang    ID Sex  DoB  Education    Level      Teacher Hearing  Reading V1  Text     Score
# English 26 male 1997 postgraduate nearNative yes     no       no      tts lettuces 4																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																				

def internalise_segment_data_line(Line, Dict):
    if len(Line) < 12:
        lara_utils.print_and_flush(f'*** Warning: skipping line {Line}')
    ( Lang, ID, Gender, DoB, Education, Level, Teacher, HearingIssues, ReadingIssues, VersionFirst, Text, Score ) = Line[:12]
    ( TTSAccepable, HumanAcceptable, Comparison ) = interpret_score(Score, VersionFirst)
    Entry = Dict[ID] if ID in Dict else {}
    Scores = Entry['scores'] if 'scores' in Entry else {}
    Entry['lang'] = Lang
    Entry['gender'] = Gender
    Entry['DoB'] = DoB
    Entry['education'] = Education
    Entry['level'] = Level
    Entry['teacher'] = Teacher
    Entry['hearing_issues'] = HearingIssues
    Entry['reading_issues'] = ReadingIssues
    Entry['version_first'] = VersionFirst
    Scores[Text] = { 'tts_acceptable': TTSAccepable, 'human_acceptable': HumanAcceptable, 'comparison': Comparison }
    Entry['scores'] = Scores
    Dict[ID] = Entry

# 1 = Both versions are acceptable and equally good
# 2 = Both versions are acceptable, but version 1 is clearly better
# 3 = Both versions are acceptable, but version 2 is clearly better
# 4 = Version 1 is acceptable, version 2 is not acceptable
# 5 = Version 1 is not acceptable, version 2 is acceptable
# 6 = Neither one is acceptable

_score_to_results_v1_is_tts = { '1': ( 'tts_acceptable', 'human_acceptable', 'equal' ),
                                '2': ( 'tts_acceptable', 'human_acceptable', 'tts_better' ),
                                '3': ( 'tts_acceptable', 'human_acceptable', 'human_better' ),
                                '4': ( 'tts_acceptable', 'human_not_acceptable', 'tts_better' ),
                                '5': ( 'tts_not_acceptable', 'human_acceptable', 'human_better' ),
                                '6': ( 'tts_not_acceptable', 'human_not_acceptable', 'equal' )
                                }

_score_to_results_v1_is_human = { '1': ( 'tts_acceptable', 'human_acceptable', 'equal' ),
                                  '2': ( 'tts_acceptable', 'human_acceptable', 'human_better' ),
                                  '3': ( 'tts_acceptable', 'human_acceptable', 'tts_better' ),
                                  '4': ( 'tts_not_acceptable', 'human_acceptable', 'human_better' ),
                                  '5': ( 'tts_acceptable', 'human_not_acceptable', 'tts_better' ),
                                  '6': ( 'tts_not_acceptable', 'human_not_acceptable', 'equal' )
                                  }

def interpret_score(Score, VersionFirst):
    if VersionFirst == 'tts':
        return _score_to_results_v1_is_tts[Score]
    elif VersionFirst == 'human':
        return _score_to_results_v1_is_human[Score]
    else:
        lara_utils.print_and_flush(f'*** Error: unknown value for "VersionFirst", {VersionFirst}')
        return False

# Typical record
# English 45 male 1959 postgraduate native no no no tts	         "cold and monotone." "more natural, clearer pronunciation"  "NULL"  "2021-05-24 02:48:03" "2021-05-24 02:57:28"
# Lang    ID Sex  DoB  Education    Level  T  H  R  VersionFirst V1Comment            V2Comment                              Comment StartTime             EndTime

def internalise_overall_data_line(Line, Dict):
    if len(Line) < 15:
        lara_utils.print_and_flush(f'*** Warning: skipping line {Line}')
    (Lang, ID, Sex, DoB, Education, Level, T, H, R, VersionFirst, V1Comment, V2Comment, Comment, StartTime, EndTime ) = Line[:15]
    if ID in Dict:
        Entry = Dict[ID]
        ( TTSComment, HumanComment ) = ( V1Comment, V2Comment ) if VersionFirst == 'tts' else ( V2Comment, V1Comment )
        if not 'voice_ratings_tts' in Entry:
            Entry['voice_ratings_tts'] = {}
        if not 'voice_ratings_human' in Entry:
            Entry['voice_ratings_human'] = {}
        Entry['voice_ratings_tts']['comment'] = TTSComment
        Entry['voice_ratings_human']['comment'] = HumanComment
        Entry['overall_comment'] = Comment
        Entry['time_start'] = StartTime
        Entry['time_end'] = EndTime
        Dict[ID] = Entry

# Typical record
# English 19 1        6   5																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																											
# Lang    ID Version  Q#  Score																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																			
																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																		
def internalise_voice_rating_data_line(Line, Dict):
    if len(Line) < 5:
        lara_utils.print_and_flush(f'*** Warning: skipping line {Line}')
    (Lang, ID, Version, QuestionNumber, LikertScore ) = Line[:5]
    if ID in Dict:
        Entry = Dict[ID]
        VersionFirst = Entry['version_first']
        VersionKey = 'voice_ratings_tts' if VersionFirst == 'tts' and Version == '1' or VersionFirst == 'human' and Version == '2' else 'voice_ratings_human'
        VoiceResponseQuestion = interpret_voice_response_question_number(QuestionNumber)
        SubEntry = Entry[VersionKey] if VersionKey in Entry else {}
        SubEntry[VoiceResponseQuestion] = LikertScore
        Entry[VersionKey] = SubEntry
        Dict[ID] = Entry

# 1 = Individual words were correctly pronounced. 
# 
# 2 = Each sentence as a whole was correctly pronounced. 
# 
# 3 = Speed of speech was appropriate. 
# 
# 4 = The voice sounded natural. 
# 
# 5 = The voice was pleasant to listen to. 
# 
# 6 = The voice would be acceptable for teaching purposes. 
# 
# 7 = I would recommend learners to use this voice as a model for imitating. 

def interpret_voice_response_question_number(QuestionNumber):
    if QuestionNumber == '1':
        return 'words_ok'
    elif QuestionNumber == '2':
        return 'sentences_ok'
    elif QuestionNumber == '3':
        return 'speed_ok'
    elif QuestionNumber == '4':
        return 'natural'
    elif QuestionNumber == '5':
        return 'pleasant'
    elif QuestionNumber == '6':
        return 'ok_for_teaching'
    elif QuestionNumber == '7':
        return 'ok_to_imitate'
    else:
        lara_utils.print_and_flush(f'*** Error: bad voice quality question number: {QuestionNumber}')

# ----------------------------------

def summarise_eurocall_data(Format, JSONFile, SentenceSummaryFile, VoiceSummaryFile,
                            LanguageTableFile, VoiceTableFile, LanguageAndVoiceTableFile, FreeformCommentFile):
    if check_for_known_format(Format) == False:
        return 
    ResultDict = summarise_eurocall_sentence_data(Format, JSONFile, SentenceSummaryFile)
    VoiceDict = summarise_eurocall_voice_data(Format, JSONFile, VoiceSummaryFile)
    make_language_table_file(Format, JSONFile, ResultDict, LanguageTableFile)
    make_language_table_file_csv(Format, JSONFile, ResultDict, LanguageTableFile.replace('html', 'csv'))
    make_voice_table_file(Format, JSONFile, VoiceDict, VoiceTableFile)
    make_language_and_voice_table_file(Format, JSONFile, ResultDict, VoiceDict, LanguageAndVoiceTableFile)
    make_voice_table_file_csv(Format, JSONFile, VoiceDict, VoiceTableFile.replace('html', 'csv'))
    make_freeform_comment_file(Format, JSONFile, FreeformCommentFile)

def check_for_known_format(Format):
    if not Format in _known_formats:
        lara_utils.print_and_flush(f'*** Unknown format "{Format}. Must be in {_known_formats}"')
        return False
    else:
        return True                
    
def summarise_eurocall_sentence_data(Format, JSONFile, SummaryFile):
    Content = lara_utils.read_json_file(JSONFile)
    SummaryConditions = get_summary_conditions(Format, Content)
    ResultDict = {}
    SummaryTexts = [ make_summary_text_for_condition(Condition, Content, ResultDict) for Condition in SummaryConditions ]
    AllSummaryText = '\n----------------------\n'.join(SummaryTexts)
    lara_utils.write_lara_text_file(AllSummaryText, SummaryFile)
    return ResultDict

def summarise_eurocall_voice_data(Format, JSONFile, SummaryFile):
    Content = lara_utils.read_json_file(JSONFile)
    SummaryConditions = get_voice_summary_conditions(Format, Content)
    VoiceDict = {}
    SummaryTexts = [ make_voice_summary_text_for_condition(Condition, Content, VoiceDict) for Condition in SummaryConditions ]
    AllSummaryText = '\n----------------------\n'.join(SummaryTexts)
    lara_utils.write_lara_text_file(AllSummaryText, SummaryFile)
    return VoiceDict

def get_summary_conditions(Format, Content):
    if Format == 'default':
        return get_default_summary_conditions(Content)
    elif Format == 'eurocall_2021':
        return get_eurocall_2021_summary_conditions(Content)
    elif Format == 'lrec_2022':
        return get_lrec_2022_summary_conditions(Content)

def get_default_summary_conditions(Content):
    Languages = lara_utils.remove_duplicates([ Content[Id]['lang'] for Id in Content ])
    SentencesAndLanguages = lara_utils.remove_duplicates([ ( Sentence, Lang )
                                                           for Lang in Languages
                                                           for Id in Content
                                                           for Sentence in Content[Id]['scores']
                                                           if Lang == Content[Id]['lang']
                                                           ])
                                             
    Everything = [ 'Everything',
                   'Only sentences', 'Only words',
                   'Teacher', 'Not teacher',
                   ( 'Teacher', 'Only sentences' ), ( 'Teacher', 'Only words' ),
                   ( 'Not teacher', 'Only sentences' ), ( 'Not teacher', 'Only words' ),
                   'Native/near-native', 'Not native/near-native',
                   ( 'Native/near-native', 'Only sentences' ), ( 'Native/near-native', 'Only words' ),
                   ( 'Not native/near-native', 'Only sentences' ), ( 'Not native/near-native', 'Only words' )
                   ]
    LangConditions = [ ( 'Language:', Lang ) + Condition 
                       for Lang in Languages
                       for Condition in ( ( 'Everything', ),
                                          ( 'Teacher', ), ( 'Not teacher', ),
                                          ( 'Native/near-native', ), ( 'Not native/near-native', ),
                                          ( 'Only sentences', ), ( 'Only words', ),
                                          ( 'Teacher', 'Only sentences' ), ( 'Teacher', 'Only words' ),
                                          ( 'Not teacher', 'Only sentences' ), ( 'Not teacher', 'Only words' ),
                                          ( 'Native/near-native', 'Only sentences' ), ( 'Native/near-native', 'Only words' ),
                                          ( 'Not native/near-native', 'Only sentences' ), ( 'Not native/near-native', 'Only words' )
                                          )
                       ]
    SentConditions = [ ( 'Sentence:', Lang, Sent ) for ( Sent, Lang ) in SentencesAndLanguages ]

    return Everything + LangConditions + SentConditions

def get_eurocall_2021_summary_conditions(Content):
    Languages = lara_utils.remove_duplicates([ Content[Id]['lang'] for Id in Content ])
    SentencesAndLanguages = lara_utils.remove_duplicates([ ( Sentence, Lang )
                                                           for Lang in Languages
                                                           for Id in Content
                                                           for Sentence in Content[Id]['scores']
                                                           if Lang == Content[Id]['lang']
                                                           ])
                                             
    Everything = [ 'Everything',
                   'Only sentences', 'Only words',
                   'ReadSpeaker', 'not ReadSpeaker',
                   ( 'ReadSpeaker', 'Only sentences' ), ( 'ReadSpeaker', 'Only words' ),
                   ( 'not ReadSpeaker', 'Only sentences' ), ( 'not ReadSpeaker', 'Only words' ),
                   'Teacher', 'Not teacher',
                   ( 'Teacher', 'Only sentences' ), ( 'Teacher', 'Only words' ),
                   ( 'Not teacher', 'Only sentences' ), ( 'Not teacher', 'Only words' ),
                   'Native/near-native', 'Not native/near-native',
                   ( 'Native/near-native', 'Only sentences' ), ( 'Native/near-native', 'Only words' ),
                   ( 'Not native/near-native', 'Only sentences' ), ( 'Not native/near-native', 'Only words' )
                   ]
    LangConditions = [ ( 'Language:', Lang ) + Condition 
                       for Lang in Languages
                       for Condition in ( ( 'Everything', ),
                                          ( 'Teacher', ), ( 'Not teacher', ),
                                          ( 'Native/near-native', ), ( 'Not native/near-native', ),
                                          ( 'Only sentences', ), ( 'Only words', ),
                                          ( 'Teacher', 'Only sentences' ), ( 'Teacher', 'Only words' ),
                                          ( 'Not teacher', 'Only sentences' ), ( 'Not teacher', 'Only words' ),
                                          ( 'Native/near-native', 'Only sentences' ), ( 'Native/near-native', 'Only words' ),
                                          ( 'Not native/near-native', 'Only sentences' ), ( 'Not native/near-native', 'Only words' )
                                          )
                       ]
    SentConditions = [ ( 'Sentence:', Lang, Sent ) for ( Sent, Lang ) in SentencesAndLanguages ]

    return Everything + LangConditions + SentConditions

def get_lrec_2022_summary_conditions(Content):
    Languages = lara_utils.remove_duplicates([ Content[Id]['lang'] for Id in Content ])
    SentencesAndLanguages = lara_utils.remove_duplicates([ ( Sentence, Lang )
                                                           for Lang in Languages
                                                           for Id in Content
                                                           for Sentence in Content[Id]['scores']
                                                           if Lang == Content[Id]['lang']
                                                           ])
                                             
    Everything = [ 'Everything',
                   #'Only sentences', 'Only words',
                   'Humour', 'Not humour', 'Dialogue', 'Not dialogue',
                   'ReadSpeaker', 'not ReadSpeaker',
                   #( 'ReadSpeaker', 'Only sentences' ), ( 'ReadSpeaker', 'Only words' ),
                   #( 'not ReadSpeaker', 'Only sentences' ), ( 'not ReadSpeaker', 'Only words' ),
                   'Teacher', 'Not teacher',
                   #( 'Teacher', 'Only sentences' ), ( 'Teacher', 'Only words' ),
                   #( 'Not teacher', 'Only sentences' ), ( 'Not teacher', 'Only words' ),
                   'Native/near-native', 'Not native/near-native',
                   ( 'Native/near-native', 'Humour' ), ( 'Native/near-native', 'Not humour' ),
                   ( 'Native/near-native', 'Dialogue' ), ( 'Native/near-native', 'Not dialogue' )
                   #( 'Native/near-native', 'Only sentences' ), ( 'Native/near-native', 'Only words' ),
                   #( 'Not native/near-native', 'Only sentences' ), ( 'Not native/near-native', 'Only words' )
                   ]
    LangConditions = [ ( 'Language:', Lang ) + Condition 
                       for Lang in Languages
                       for Condition in ( ( 'Everything', ),
                                          ( 'Teacher', ), ( 'Not teacher', ),
                                          ( 'Native/near-native', ), ( 'Not native/near-native', ),
                                          #( 'Only sentences', ), ( 'Only words', ),
                                          ( 'Humour', ), ( 'Not humour', ), ( 'Dialogue', ), ( 'Not dialogue', ),
                                          #( 'Teacher', 'Only sentences' ), ( 'Teacher', 'Only words' ),
                                          #( 'Not teacher', 'Only sentences' ), ( 'Not teacher', 'Only words' ),
                                          #( 'Native/near-native', 'Only sentences' ), ( 'Native/near-native', 'Only words' ),
                                          #( 'Not native/near-native', 'Only sentences' ), ( 'Not native/near-native', 'Only words'
                                          ( 'Native/near-native', 'Humour' ), ( 'Native/near-native', 'Not humour' ),
                                          ( 'Native/near-native', 'Dialogue' ), ( 'Native/near-native', 'Not dialogue' ) )
                       ]
    SentConditions = [ ( 'Sentence:', Lang, Sent ) for ( Sent, Lang ) in SentencesAndLanguages ]

    return Everything + LangConditions + SentConditions

def get_voice_summary_conditions(Format, Content):
    if Format == 'default':
        return get_voice_summary_conditions_default(Content)
    elif Format == 'eurocall_2021':
        return get_voice_summary_conditions_eurocall_2021(Content)
    elif Format == 'lrec_2022':
        return get_voice_summary_conditions_lrec_2022(Content)
    else:
        return []

def get_voice_summary_conditions_default(Content):
    Languages = lara_utils.remove_duplicates([ Content[Id]['lang'] for Id in Content ])
    
    Everything = [ 'Everything', 
                   'Teacher', 'Not teacher',
                   'Native/near-native', 'Not native/near-native']
    LangConditions = [ ( 'Language:', Lang, SubCondition )
                       for Lang in Languages
                       for SubCondition in ( 'Everything', 'Teacher', 'Not teacher', 'Native/near-native', 'Not native/near-native') ]

    return Everything + LangConditions 
                                                
def get_voice_summary_conditions_eurocall_2021(Content):
    Languages = lara_utils.remove_duplicates([ Content[Id]['lang'] for Id in Content ])
    
    Everything = [ 'Everything',
                   'ReadSpeaker', 'not ReadSpeaker',
                   'Teacher', 'Not teacher',
                   'Native/near-native', 'Not native/near-native']
    LangConditions = [ ( 'Language:', Lang, SubCondition )
                       for Lang in Languages
                       for SubCondition in ( 'Everything', 'Teacher', 'Not teacher', 'Native/near-native', 'Not native/near-native') ]

    return Everything + LangConditions 

def get_voice_summary_conditions_lrec_2022(Content):
    Languages = lara_utils.remove_duplicates([ Content[Id]['lang'] for Id in Content ])
    
    Everything = [ 'Everything',
                   'ReadSpeaker', 'not ReadSpeaker',
                   'Teacher', 'Not teacher',
                   'Native/near-native', 'Not native/near-native']
    LangConditions = [ ( 'Language:', Lang, SubCondition )
                       for Lang in Languages
                       for SubCondition in ( 'Everything', 'Teacher', 'Not teacher', 'Native/near-native', 'Not native/near-native') ]

    return Everything + LangConditions 

def make_summary_text_for_condition(Condition, Content, ResultDict):
    Scores = get_scores_matching_condition(Content, Condition)
    NMatches = len(Scores)
    if NMatches == 0:
        return f'Condition: {Condition} does not match anything'
    NRaters = get_number_of_raters_for_condition(Content, Condition)
    ProportionHumanAcceptable = proportion_of_scores_with_value_for_feature(Scores, 'human_acceptable', 'human_acceptable')
    ProportionTTSAcceptable = proportion_of_scores_with_value_for_feature(Scores, 'tts_acceptable', 'tts_acceptable')
    ProportionHumanBetter = proportion_of_scores_with_value_for_feature(Scores, 'comparison', 'human_better')
    ProportionTTSBetter = proportion_of_scores_with_value_for_feature(Scores, 'comparison', 'tts_better')
    ProportionEqual = proportion_of_scores_with_value_for_feature(Scores, 'comparison', 'equal')
    Lines = [ f'Condition: {Condition} ({NMatches} examples)',
              f'Human voice is acceptable: {ProportionHumanAcceptable}%',
              f'TTS voice is acceptable:   {ProportionTTSAcceptable}%',
              f'Human voice is better:     {ProportionHumanBetter}%',
              f'About the same:            {ProportionEqual}%',
              f'TTS voice is better:       {ProportionTTSBetter}%'
              ]
    ResultDict[(Condition, 'n_matches')] = NMatches
    ResultDict[(Condition, 'n_raters')] = NRaters
    ResultDict[(Condition, 'human_acceptable')] = ProportionHumanAcceptable
    ResultDict[(Condition, 'tts_acceptable')] = ProportionTTSAcceptable
    ResultDict[(Condition, 'human_better')] = ProportionHumanBetter
    ResultDict[(Condition, 'same')] = ProportionEqual
    ResultDict[(Condition, 'tts_better')] = ProportionTTSBetter
    return '\n'.join(Lines)

def get_number_of_raters_for_condition(Content, Condition):
    SimplifiedCondition = remove_sentence_oriented_parts_of_condition(Condition)
    Records = get_records_matching_condition(Content, Condition)
    return len(Records)

def remove_sentence_oriented_parts_of_condition(Condition):
    if Condition in ( 'Only sentences', 'Only words', ( 'Only sentences', ),  ( 'Only words', ) ):
        return 'Everything'
    elif isinstance(Condition, str):
        return Condition
    elif isinstance(Condition, tuple):
        return tuple([ remove_sentence_oriented_parts_of_condition(Elt) for Elt in Condition ])

def make_voice_summary_text_for_condition(Condition, Content, VoiceDict):
    Records = get_records_matching_condition(Content, Condition)
    NMatches = len(Records)
    if NMatches == 0:
        return f'Condition: {Condition} does not match anything'
    VoiceDict[(Condition, 'n_matches')] = NMatches
    RatingLines = []
    for SubKey in ( 'words_ok', 'sentences_ok', 'speed_ok', 'natural', 'pleasant', 'ok_for_teaching', 'ok_to_imitate' ):
        RatingLines += [ voice_summary_line(SubKey, Records, Condition, VoiceDict) ]
    Lines = [ f'Condition: {Condition} ({NMatches} examples)' ] + RatingLines
    return '\n'.join(Lines)

def voice_summary_line(SubKey, Records, Condition, VoiceDict):
    AvScoreHuman = average_voice_rating_score('voice_ratings_human', SubKey, Records)
    AvScoreTTS = average_voice_rating_score('voice_ratings_tts', SubKey, Records)
    AvDifference = number_to_2_dp(lara_utils.safe_string_to_number(AvScoreHuman) - lara_utils.safe_string_to_number(AvScoreTTS))
    VoiceDict[(Condition, SubKey, 'human')] = AvScoreHuman
    VoiceDict[(Condition, SubKey, 'tts')] = AvScoreTTS
    return f'{SubKey:16}: human = {AvScoreHuman}, TTS = {AvScoreTTS}, difference = {AvDifference} '

def average_voice_rating_score(Key, SubKey, Records):
    Scores = [ lara_utils.safe_string_to_number(Record[Key][SubKey]) for Record in Records ]
    return number_to_2_dp( sum(Scores) / len(Scores) )
               

def get_scores_matching_condition(Content, Condition):
    return [ Content[Id]['scores'][Sentence]
             for Id in Content
             for Sentence in Content[Id]['scores']
             if matches_condition(Condition, { 'record': Content[Id], 'sentence': Sentence })
             ]

def get_records_matching_condition(Content, Condition):
    return [ Content[Id]
             for Id in Content
             if matches_condition(Condition, { 'record': Content[Id], 'sentence': 'any_sentence' })
             ]
                             
def matches_condition(Condition, RecordAndSentence):
    Record = RecordAndSentence['record']
    Sentence = RecordAndSentence['sentence']
    Words = Sentence.split()
    Language = Record['lang']
    if Condition == 'Everything':
        return True
    elif Condition == 'ReadSpeaker':
        return not Record['lang'] in ( 'Mandarin', 'Farsi', 'Irish' )
    elif Condition == 'not ReadSpeaker':
        return Record['lang'] in ( 'Mandarin', 'Farsi', 'Irish' )
    elif Condition == 'Teacher':
        return Record['teacher'] == 'yes'
    elif Condition == 'Not teacher':
        return Record['teacher'] != 'yes'
    elif Condition == 'Native/near-native':
        return Record['level'] in ( 'native', 'nearNative' )
    elif Condition == 'Not native/near-native':
        return not Record['level'] in ( 'native', 'nearNative' )
    elif Condition == 'Only sentences':
        return not looks_like_a_single_word(Sentence, Words, Language) or Sentence == 'any_sentence'
    elif Condition == 'Only words':
        return looks_like_a_single_word(Sentence, Words, Language) or Sentence == 'any_sentence'
    elif Condition == 'Humour':
        HumourAndDialogue = language_and_sentence_to_humour_and_dialogue(Language, Sentence)
        return HumourAndDialogue != False and HumourAndDialogue[0] == 'humour' or Sentence == 'any_sentence'
    elif Condition == 'Not humour':
        HumourAndDialogue = language_and_sentence_to_humour_and_dialogue(Language, Sentence)
        return HumourAndDialogue != False and HumourAndDialogue[0] == 'not_humour' or Sentence == 'any_sentence'
    elif Condition == 'Dialogue':
        HumourAndDialogue = language_and_sentence_to_humour_and_dialogue(Language, Sentence)
        return HumourAndDialogue != False and HumourAndDialogue[1] == 'dialogue' or Sentence == 'any_sentence'
    elif Condition == 'Not dialogue':
        HumourAndDialogue = language_and_sentence_to_humour_and_dialogue(Language, Sentence)
        return HumourAndDialogue != False and HumourAndDialogue[1] == 'not_dialogue' or Sentence == 'any_sentence'
    elif isinstance(Condition, tuple) and len(Condition) == 2 and not Condition[0] in ( 'Language:', 'Sentence:' ):
        return matches_condition(Condition[0], RecordAndSentence) and matches_condition(Condition[1], RecordAndSentence)
    elif isinstance(Condition, tuple) and len(Condition) == 2 and Condition[0] == 'Language:':
        return Condition[1] == Record['lang']
    elif isinstance(Condition, tuple) and len(Condition) == 3 and Condition[0] == 'Sentence:':
        return Condition[2] == Sentence
    elif isinstance(Condition, tuple) and len(Condition) == 3 and Condition[0] == 'Language:':
        return Condition[1] == Record['lang'] and matches_condition(Condition[2], RecordAndSentence)
    elif isinstance(Condition, tuple) and len(Condition) == 4 and Condition[0] == 'Language:' :
        return Condition[1] == Record['lang'] and \
               matches_condition(Condition[2], RecordAndSentence) and matches_condition(Condition[3], RecordAndSentence)
    else:
        return False

def looks_like_a_single_word(Sentence, Words, Language):
    if Language == 'Mandarin' or Language == 'Japanese':
        return len(Sentence) <= 4
    else:
        return len(Words) == 1

def proportion_of_scores_with_value_for_feature(Scores, Key, Value):
    NScores = len(Scores)
    NSelected = len([ Score for Score in Scores if Score[Key] == Value ])
    return percentage_to_1_dp( NSelected / NScores )

# --------------------------------

def make_language_and_voice_table_file(Format, JSONFile, ResultDict, VoiceDict, LanguageAndVoiceTableFile):
    LanguageTableLines = make_all_language_table_lines(Format, JSONFile, ResultDict)
    VoiceTableLines = make_all_voice_table_lines(Format, JSONFile, VoiceDict)
    AllLines = [ [ '<b>Results for individual utterances' ] ] + \
               LanguageTableLines + \
               [ [ '<b>Overall impressions of voices' ] ] + \
               VoiceTableLines
    write_out_language_and_voice_table(AllLines, LanguageAndVoiceTableFile)

def write_out_language_and_voice_table(Lines, File):
    Header = [ 'Condition' ] 
    Caption = 'LREC 2022 combined human/TTS results. Yellow = TTS not worse, orange = TTS within 10%.'
    Params = lara_config.default_params()
    print_html_table(Caption, Header, Lines, File, Params)

# --------------------------------

def make_language_table_file(Format, JSONFile, ResultDict, LanguageTableFile):
    LanguageTableLines = make_all_language_table_lines(Format, JSONFile, ResultDict)
    write_out_language_table(LanguageTableLines, LanguageTableFile)

def make_all_language_table_lines(Format, JSONFile, ResultDict):
    Content = lara_utils.read_json_file(JSONFile)
    AllConditions = get_summary_conditions(Format, Content)
    LangConditions = [ Condition for Condition in AllConditions
                       if isinstance(Condition, tuple) and Condition[0] == 'Language:' ]
    Languages = sorted(lara_utils.remove_duplicates([ Condition[1] for Condition in LangConditions ]))
    LangConditionTypes = lara_utils.remove_duplicates([ Condition[2:] for Condition in LangConditions ])
    return make_language_table_lines(Languages, LangConditionTypes, ResultDict)

_info_types = ( 'human_acceptable', 'tts_acceptable', 'human_better', 'tts_better', 'same' )

def make_language_table_lines(Languages, LangConditionTypes, ResultDict):
    Lines = []
    for LangConditionType in LangConditionTypes:
        Lines += make_language_table_lines_for_condition_type(Languages, LangConditionType, ResultDict)
    return Lines

def make_language_table_lines_for_condition_type(Languages, LangConditionType, ResultDict):
    ConditionName = ' + '.join(LangConditionType)
    ConditionElement = { 'value': ConditionName, 'rowspan': 9 }
    HeaderLine = [ ConditionElement, 'language' ] + Languages
    RatersLine = raters_line(Languages, LangConditionType, ResultDict)
    ItemsLine = items_line(Languages, LangConditionType, ResultDict)
    AnnotationsLine = annotations_line(Languages, LangConditionType, ResultDict)
    BodyLines = make_language_table_body_lines(Languages, LangConditionType, ResultDict) 
    
    return [ HeaderLine, RatersLine, ItemsLine, AnnotationsLine ] + BodyLines

##    ResultDict[(Condition, 'human_acceptable')] = ProportionHumanAcceptable
##    ResultDict[(Condition, 'tts_acceptable')] = ProportionTTSAcceptable
##    ResultDict[(Condition, 'human_better')] = ProportionHumanBetter
##    ResultDict[(Condition, 'same')] = ProportionEqual
##    ResultDict[(Condition, 'tts_better')] = ProportionTTSBetter

def raters_line(Languages, LangConditionType, ResultDict):
    Body = []
    for Language in Languages:
        Condition = ( 'Language:', Language ) + LangConditionType
        NRaters = ResultDict[(Condition, 'n_raters')] if (Condition, 'n_raters') in ResultDict else '*'
        Body += [ add_italics_and_parens(NRaters) ]
    return [ '<i>(#raters)</i>' ] + Body

def annotations_line(Languages, LangConditionType, ResultDict):
    Body = []
    for Language in Languages:
        Condition = ( 'Language:', Language ) + LangConditionType
        NMatches = ResultDict[(Condition, 'n_matches')] if (Condition, 'n_matches') in ResultDict else '*'
        Body += [ add_italics_and_parens(NMatches) ]
    return [ '<i>(#annotations)</i>' ] + Body

def items_line(Languages, LangConditionType, ResultDict):
    Body = []
    for Language in Languages:
        Condition = ( 'Language:', Language ) + LangConditionType
        NRaters = ResultDict[(Condition, 'n_raters')] if (Condition, 'n_raters') in ResultDict else '*'
        NMatches = ResultDict[(Condition, 'n_matches')] if (Condition, 'n_matches') in ResultDict else '*'
        NItems = int( NMatches / NRaters ) if NMatches != '*' and NRaters != '*' and NRaters != 0 else '*'
        Body += [ add_italics_and_parens(NItems) ]
    return [ '<i>(#items)</i>' ] + Body

def make_language_table_body_lines(Languages, LangConditionType, ResultDict):
    Lines = []
    Dict = {}
    for Language in Languages:
        Parts = [ make_language_table_element_part(Language, LangConditionType, ResultDict, InfoType)
                  for InfoType in _info_types ]
        PartsWithMarkings = mark_numbers_in_language_table_element_parts(Parts)
        for InfoTypeIndex in range(0, len(_info_types)):
            InfoType = _info_types[InfoTypeIndex]
            PartWithMarkings = PartsWithMarkings[InfoTypeIndex]
            Dict[( Language, InfoType )] = PartWithMarkings
    for InfoType in _info_types:
        Line = [ f'({InfoType})' if InfoType == 'same' else InfoType ] + [ Dict[( Language, InfoType )] for Language in Languages ]
        Lines += [ Line ]
    return Lines
            
##def make_language_table_element(Language, LangConditionType, ResultDict):
##    Parts = [ make_language_table_element_part(Language, LangConditionType, ResultDict, InfoType)
##              for InfoType in _info_types ]
##    Condition = ( 'Language:', Language ) + LangConditionType
##    NRaters = ResultDict[(Condition, 'n_raters')] if (Condition, 'n_raters') in ResultDict else '*'
##    NMatches = ResultDict[(Condition, 'n_matches')] if (Condition, 'n_matches') in ResultDict else '*'
##    NItems = int( NMatches / NRaters ) if NMatches != '*' and NRaters != '*' and NRaters != 0 else '*'
##    PartsWithMarkings = mark_numbers_in_language_table_element_parts(Parts)
##    return '<br>'.join([ Language, str(NRaters), str(NItems), str(NMatches) ] + PartsWithMarkings)

def mark_numbers_in_language_table_element_parts(Parts):
    if '*' in Parts:
        return Parts
    PartsAsNumbers = [ lara_utils.safe_string_to_number(Str) for Str in Parts ]
    ( HumanAcceptable, TTSAcceptable, HumanBetter, TTSBetter, Same ) = Parts
    SameParens = f'({Same})'
    ( HumanAcceptableNum, TTSAcceptableNum, HumanBetterNum, TTSBetterNum, SameNum ) = PartsAsNumbers
    if TTSAcceptableNum >= HumanAcceptableNum:
        ( HumanAcceptableMarked, TTSAcceptableMarked ) = ( mark(HumanAcceptable, 'better'), mark(TTSAcceptable, 'better') )
    elif TTSAcceptableNum >= HumanAcceptableNum - 10.0:
        ( HumanAcceptableMarked, TTSAcceptableMarked ) = ( mark(HumanAcceptable, 'nearly'), mark(TTSAcceptable, 'nearly') )
    else:
        ( HumanAcceptableMarked, TTSAcceptableMarked ) = ( HumanAcceptable, TTSAcceptable )
    if TTSBetterNum >= HumanBetterNum:
        ( HumanBetterMarked, SameMarked, TTSBetterMarked ) = ( mark(HumanBetter, 'better'), SameParens, mark(TTSBetter, 'better') )
    elif TTSBetterNum >= HumanBetterNum - 10.0:
        ( HumanBetterMarked, SameMarked, TTSBetterMarked ) = ( mark(HumanBetter, 'nearly'), SameParens, mark(TTSBetter, 'nearly') )
    else:
        ( HumanBetterMarked, SameMarked, TTSBetterMarked ) = ( HumanBetter, SameParens, TTSBetter )
    return [ HumanAcceptableMarked, TTSAcceptableMarked, HumanBetterMarked, TTSBetterMarked, SameMarked ]

def make_language_table_element_part(Language, LangConditionType, ResultDict, InfoType):
    Condition = ( 'Language:', Language ) + LangConditionType 
    Key = ( Condition, InfoType)
    Value = ResultDict[Key] if Key in ResultDict else '*'
    return Value

def write_out_language_table(Lines, File):
    Header = [ 'Condition' ] 
    Caption = 'LREC 2022 human/TTS results by language and condition. Yellow = TTS not worse, orange = TTS within 10%.'
    Params = lara_config.default_params()
    print_html_table(Caption, Header, Lines, File, Params)

# --------------------------------

def make_language_table_file_csv(Format, JSONFile, ResultDict, LanguageTableFile):
    Content = lara_utils.read_json_file(JSONFile)
    AllConditions = get_summary_conditions(Format, Content)
    LangConditions = [ Condition for Condition in AllConditions
                       if isinstance(Condition, tuple) and Condition[0] == 'Language:' ]
    Languages = sorted(lara_utils.remove_duplicates([ Condition[1] for Condition in LangConditions ]))
    LangConditionTypes = lara_utils.remove_duplicates([ Condition[2:] for Condition in LangConditions ])
    LanguageTableLines = make_language_table_lines_csv(Languages, LangConditionTypes, ResultDict)
    write_out_language_table_csv(Languages, LanguageTableLines, LanguageTableFile)

def make_language_table_lines_csv(Languages, LangConditionTypes, ResultDict):
    Lines = []
    for LangConditionType in LangConditionTypes:
        Lines += make_language_table_lines_for_condition_type_csv(Languages, LangConditionType, ResultDict)
    return Lines

#_info_types = ( 'human_acceptable', 'tts_acceptable', 'human_better', 'same', 'tts_better' )

def make_language_table_lines_for_condition_type_csv(Languages, LangConditionType, ResultDict):
    LangConditionTypeFormatted = ' + '.join(LangConditionType)
    LanguageLine = [ LangConditionTypeFormatted, 'language' ] + Languages
    RatersLine = [ LangConditionTypeFormatted, '(#raters)' ] + \
                 [ lookup_or_asterisk(ResultDict, ( ( 'Language:', Language ) + LangConditionType, 'n_raters' ) ) for Language in Languages ]
    MatchesLine = [ LangConditionTypeFormatted, '(#annotations)' ] + \
                  [ lookup_or_asterisk(ResultDict, ( ( 'Language:', Language ) + LangConditionType, 'n_matches') ) for Language in Languages ]
    BodyLines = [ [ LangConditionTypeFormatted, InfoType ] + \
                  [ make_language_table_element_part(Language, LangConditionType, ResultDict, InfoType)
                    for Language in Languages ]
                  for InfoType in _info_types ]
    return [ LanguageLine, RatersLine, MatchesLine ] + BodyLines

def lookup_or_asterisk(Dict, Key):
    return Dict[Key] if Key in Dict else '*'

def write_out_language_table_csv(Languages, Lines, File):
    lara_utils.write_lara_csv(Lines, File)

# --------------------------------

def make_voice_table_file(Format, JSONFile, VoiceDict, VoiceTableFile):
    VoiceTableLines = make_all_voice_table_lines(Format, JSONFile, VoiceDict)
    write_out_voice_table(VoiceTableLines, VoiceTableFile)

def make_all_voice_table_lines(Format, JSONFile, VoiceDict):
    Content = lara_utils.read_json_file(JSONFile)
    AllConditions = get_voice_summary_conditions(Format, Content)
    LangConditions = [ Condition for Condition in AllConditions
                       if isinstance(Condition, tuple) and Condition[0] == 'Language:' ]
    Languages = sorted(lara_utils.remove_duplicates([ Condition[1] for Condition in LangConditions ]))
    LangConditionTypes = lara_utils.remove_duplicates([ Condition[2:] for Condition in LangConditions ])
    return make_voice_table_lines(Languages, LangConditionTypes, VoiceDict)

def make_voice_table_lines(Languages, LangConditionTypes, VoiceDict):
    Lines = []
    for LangConditionType in LangConditionTypes:
        Lines += make_voice_table_lines_for_condition_type(Languages, LangConditionType, VoiceDict)
    return Lines

def make_voice_table_lines_for_condition_type(Languages, LangConditionType, VoiceDict):
    ConditionName = ' + '.join(LangConditionType)
    ConditionElement = { 'value': ConditionName, 'rowspan': 9 }
    HeaderLine = [ ConditionElement, 'language' ] + Languages
    RatersLine = voice_raters_line(Languages, LangConditionType, VoiceDict)
    BodyLines = make_voice_table_body_lines(Languages, LangConditionType, VoiceDict) 
    
    return [ HeaderLine, RatersLine ] + BodyLines

_voice_info_types = ( 'words_ok', 'sentences_ok', 'speed_ok', 'natural', 'pleasant', 'ok_for_teaching', 'ok_to_imitate' )

_voice_info_subtypes = ( 'human', 'tts' )

def voice_raters_line(Languages, LangConditionType, VoiceDict):
    Body = []
    for Language in Languages:
        Condition = ( 'Language:', Language ) + LangConditionType
        NRaters = VoiceDict[(Condition, 'n_matches')] if (Condition, 'n_matches') in VoiceDict else '*'
        Body += [ add_italics_and_parens(NRaters) ]
    return [ '<i>(#raters)</i>' ] + Body

def make_voice_table_body_lines(Languages, LangConditionType, VoiceDict):
    Lines = []
    Dict = {}
    for Language in Languages:
        Parts = [ make_voice_table_element_part(Language, LangConditionType, VoiceDict, InfoType)
                  for InfoType in _voice_info_types ]
        PartsWithMarkings = mark_numbers_in_voice_table_element_parts(Parts)
        for InfoTypeIndex in range(0, len(_voice_info_types)):
            InfoType = _voice_info_types[InfoTypeIndex]
            PartWithMarkings = PartsWithMarkings[InfoTypeIndex]
            Dict[( Language, InfoType )] = PartWithMarkings
    for InfoType in _voice_info_types:
        Line = [ InfoType ] + [ Dict[( Language, InfoType )] for Language in Languages ]
        Lines += [ Line ]
    return Lines

##def make_voice_table_line(Languages, LangConditionType, VoiceDict):
##    Body = [ make_voice_table_element(Language, LangConditionType, VoiceDict) for Language in Languages ]
##    Gloss = '<br>'.join(( 'language', '(#raters)' ) + _voice_info_types)
##    RowLabel = ' + '.join(LangConditionType)
##    return [ RowLabel , Gloss ] + Body
##
##def make_voice_table_element(Language, LangConditionType, VoiceDict):
##    Parts = [ make_voice_table_element_part(Language, LangConditionType, VoiceDict, InfoType)
##              for InfoType in _voice_info_types ]
##    Condition = ( 'Language:', Language ) + LangConditionType
##    NMatches = f"({VoiceDict[(Condition, 'n_matches')]})" if (Condition, 'n_matches') in VoiceDict else '*'
##    PartsWithMarkings = mark_numbers_in_voice_table_element_parts(Parts)
##    return '<br>'.join([ Language, NMatches ] + PartsWithMarkings)

def mark_numbers_in_voice_table_element_parts(Parts):
    return [ mark_numbers_in_voice_table_element_part(Part) for Part in Parts ]

def mark_numbers_in_voice_table_element_part(Part):
    if Part == '*':
        return '*'
    ( Human, TTS) = Part
    ( HumanNum, TTSNum ) = [ lara_utils.safe_string_to_number(Str) for Str in Part ]
    FormattedPart = f'{HumanNum}/{TTSNum}'
    if TTSNum >= HumanNum:
        MarkedPart = mark(FormattedPart, 'better')
    elif TTSNum >= HumanNum - 0.5:
        MarkedPart = mark(FormattedPart, 'nearly')
    else:
        MarkedPart = FormattedPart
    return MarkedPart

##    VoiceDict[(Condition, SubKey, 'human')] = AvScoreHuman
##    VoiceDict[(Condition, SubKey, 'tts')] = AvScoreTTS

def make_voice_table_element_part(Language, LangConditionType, VoiceDict, InfoType):
    Condition = ( 'Language:', Language ) + LangConditionType 
    HumanKey = ( Condition, InfoType, 'human')
    TTSKey = ( Condition, InfoType, 'tts')
    if not HumanKey in VoiceDict or not TTSKey in VoiceDict:
        return '*'
    else:
        return ( VoiceDict[HumanKey], VoiceDict[TTSKey] )

def write_out_voice_table(Lines, File):
    Header = [ 'Condition' ] 
    Caption = 'LREC 2022 human/TTS voice ratings by language and condition. Entries in form (average human rating/average TTS rating). Yellow = TTS not worse, orange = TTS within 0.5.'
    Params = lara_config.default_params()
    print_html_table(Caption, Header, Lines, File, Params)

# --------------------------------

def make_voice_table_file_csv(Format, JSONFile, VoiceDict, VoiceTableFile):
    Content = lara_utils.read_json_file(JSONFile)
    AllConditions = get_voice_summary_conditions(Format, Content)
    LangConditions = [ Condition for Condition in AllConditions
                       if isinstance(Condition, tuple) and Condition[0] == 'Language:' ]
    Languages = sorted(lara_utils.remove_duplicates([ Condition[1] for Condition in LangConditions ]))
    LangConditionTypes = lara_utils.remove_duplicates([ Condition[2:] for Condition in LangConditions ])
    VoiceTableLines = make_voice_table_lines_csv(Languages, LangConditionTypes, VoiceDict)
    write_out_voice_table_csv(Languages, VoiceTableLines, VoiceTableFile)

def make_voice_table_lines_csv(Languages, LangConditionTypes, VoiceDict):
    Lines = []
    for LangConditionType in LangConditionTypes:
        Lines += make_voice_table_lines_for_condition_csv(Languages, LangConditionType, VoiceDict)
    return Lines

#_voice_info_types = ( 'words_ok', 'sentences_ok', 'speed_ok', 'natural', 'pleasant', 'ok_for_teaching', 'ok_to_imitate' )

#_voice_info_subtypes = ( 'human', 'tts' )

def make_voice_table_lines_for_condition_csv(Languages, LangConditionType, VoiceDict):
    LangConditionTypeFormatted = ' + '.join(LangConditionType)
    ( LanguagesTwice, HumanTTSList, RatersList ) = ( [], [], [] )
    for Language in Languages:
        LanguagesTwice += [ Language, Language ]
        HumanTTSList += [ 'Human', 'TTS' ]
        RaterInfo = lookup_or_asterisk(VoiceDict, ( ( 'Language:', Language ) + LangConditionType, 'n_matches' ) ) 
        RatersList += [ RaterInfo, RaterInfo ]
    LanguageLine = [ LangConditionTypeFormatted, 'language' ] + LanguagesTwice
    HumanTTSLineLine = [ LangConditionTypeFormatted, 'Human/TTS' ] + HumanTTSList
    RatersLine = [ LangConditionTypeFormatted, '(#raters)' ] + RatersList
    Body = [ make_voice_table_body_line_csv(InfoType, Languages, LangConditionType, VoiceDict) for InfoType in _voice_info_types ]
    return [ LanguageLine, HumanTTSLineLine, RatersLine ] + Body

def make_voice_table_body_line_csv(InfoType, Languages, LangConditionType, VoiceDict):
    LangConditionTypeFormatted = ' + '.join(LangConditionType)
    List = []
    for Language in Languages:
        List += make_voice_table_element_part_csv(Language, LangConditionType, VoiceDict, InfoType)
    return [ LangConditionTypeFormatted, InfoType ] + List

##    VoiceDict[(Condition, SubKey, 'human')] = AvScoreHuman
##    VoiceDict[(Condition, SubKey, 'tts')] = AvScoreTTS

def make_voice_table_element_part_csv(Language, LangConditionType, VoiceDict, InfoType):
    Condition = ( 'Language:', Language ) + LangConditionType 
    HumanKey = ( Condition, InfoType, 'human')
    TTSKey = ( Condition, InfoType, 'tts')
    if not HumanKey in VoiceDict or not TTSKey in VoiceDict:
        return ( '*', '*' )
    else:
        return ( VoiceDict[HumanKey], VoiceDict[TTSKey] )

def write_out_voice_table_csv(Languages, Lines, File):
   lara_utils.write_lara_csv(Lines, File)

# --------------------------------

def make_freeform_comment_file(Format, JSONFile, FreeformCommentFile):
    Content = lara_utils.read_json_file(JSONFile)
    AllConditions = get_voice_summary_conditions(Format, Content)
    LangConditions = [ Condition for Condition in AllConditions
                       if isinstance(Condition, tuple) and Condition[0] == 'Language:' ]
    Languages = sorted(lara_utils.remove_duplicates([ Condition[1] for Condition in LangConditions ]))
    CommentDict = {}
    for Key in Content:
        extract_freeform_comments_from_record(Content[Key], CommentDict)
    CommentLines = lara_utils.concatenate_lists([ freeform_comment_lines_for_lang(Language, CommentDict)
                                                  for Language in Languages ])
    write_out_freeform_comment_file(CommentLines, FreeformCommentFile)

def extract_freeform_comments_from_record(Record, CommentDict):
    Lang = Record['lang']
    if 'voice_ratings_human' in Record and 'comment' in Record['voice_ratings_human'] and non_null_comment(Record['voice_ratings_human']['comment']):
        HumanComment = Record['voice_ratings_human']['comment']
        HumanKey = ( Lang, 'human' )
        HumanData = CommentDict[HumanKey] if HumanKey in CommentDict else { 'list': [], 'total': 0, 'native': 0, 'teacher': 0 }
        HumanData['total'] += 1
        HumanAnnotation = []
        if Record['level'] in ( 'native', 'nearNative' ):
            HumanData['native'] += 1
            HumanAnnotation += [ f'native/near-native' ]
        if Record['teacher'] in ( 'yes' ):
            HumanData['teacher'] += 1
            HumanAnnotation += [ f'teacher' ]
        HumanComment1 = HumanComment if len(HumanAnnotation) == 0 else f'{HumanComment} <b>[{", ".join(HumanAnnotation)}]</b>'
        HumanData['list'] += [ HumanComment1 ]
        CommentDict[HumanKey] = HumanData
    if 'voice_ratings_tts' in Record and 'comment' in Record['voice_ratings_tts'] and non_null_comment(Record['voice_ratings_tts']['comment']):
        TTSComment = Record['voice_ratings_tts']['comment']
        TTSKey = ( Lang, 'tts' )
        TTSData = CommentDict[TTSKey] if TTSKey in CommentDict else { 'list': [], 'total': 0, 'native': 0, 'teacher': 0 }
        TTSAnnotation = []
        TTSData['total'] += 1
        if Record['level'] in ( 'native', 'nearNative' ):
            TTSData['native'] += 1
            TTSAnnotation += [ f'native/near-native' ]
        if Record['teacher'] in ( 'yes' ):
            TTSData['teacher'] += 1
            TTSAnnotation += [ f'teacher' ]
        TTSComment1 = TTSComment if len(TTSAnnotation) == 0 else f'{TTSComment} <b>[{", ".join(TTSAnnotation)}]</b>'
        TTSData['list'] += [ TTSComment1 ]
        CommentDict[TTSKey] = TTSData

def non_null_comment(Str):
    return Str != '' and not Str.isspace()

def freeform_comment_lines_for_lang(Lang, CommentDict):
    HumanKey = ( Lang, 'human' )
    HumanData = CommentDict[HumanKey] if HumanKey in CommentDict else { 'list': [], 'total': 0, 'native': 0, 'teacher': 0 }
    TTSKey = ( Lang, 'tts' )
    TTSData = CommentDict[TTSKey] if TTSKey in CommentDict else { 'list': [], 'total': 0, 'native': 0, 'teacher': 0 }
    MainHeading = f'<h2>{Lang}</h2>'
    HumanHeading = f"<h3>Comments for human voice ({HumanData['total']} comments, {HumanData['native']} native/near-native, {HumanData['teacher']} teachers)</h3>"
    TTSHeading = f"<h3>Comments for TTS voice ({TTSData['total']} comments, {TTSData['native']} native/near-native, {TTSData['teacher']} teachers)</h3>"
    HumanLines = [ f'<p>{Comment}</p>' for Comment in HumanData['list'] ]
    TTSLines = [ f'<p>{Comment}</p>' for Comment in TTSData['list'] ]
    return [ MainHeading ] + [ HumanHeading ] + HumanLines + [ TTSHeading ] + TTSLines

def write_out_freeform_comment_file(CommentLines, File):
    Caption = 'LREC 2022 human/TTS freeform comments by language and type.'
    Intro = freeform_comment_file_intro(Caption)
    Closing = freeform_comment_file_closing()
    AllLines = Intro + CommentLines + Closing
    lara_utils.write_unicode_text_file('\n'.join(AllLines), File)
    lara_utils.print_and_flush(f'--- Written freeform comment file ({len(CommentLines)} lines) to {File}')

def freeform_comment_file_intro(Caption):
    return ['<head>',
	    '<meta http-equiv="Content-Type" content="text/html;charset=UTF-8">',
	    '<style>',
	    '</style>',
	    '</head>',
	    '<body>',
            f'<h1>{Caption}</h1>']

def freeform_comment_file_closing():
    return ['</body>',
	    '</html>']

# --------------------------------

_language_and_sentence_to_humour_and_dialogue = {}

def language_and_sentence_to_humour_and_dialogue(Language0, Sentence):
    Language = Language0.strip().lower()
    if not Language in _language_and_sentence_to_humour_and_dialogue:
        #lara_utils.print_and_flush(f'--- No data for "{Language}"')
        return False
    LanguageDict = _language_and_sentence_to_humour_and_dialogue[Language]
    if not Sentence in LanguageDict:
        #lara_utils.print_and_flush(f'--- No data for "{Sentence}"')
        return False
    return LanguageDict[Sentence]

def classify_lrec_2022_sentences_by_dialogue_and_humour():
    global _language_and_sentence_to_humour_and_dialogue
    classify_sentences_by_dialogue_and_humour('$LARA/Code/Python/lrec_2022_eval_data_shortened.json',
                                              _lrec_2022_sentence_classification_file)
    _language_and_sentence_to_humour_and_dialogue = lara_utils.read_json_file(_lrec_2022_sentence_classification_file)
    lara_utils.print_and_flush(f'--- Stored dialogue and humour classification')

def classify_sentences_by_dialogue_and_humour(MetadataFile, ClassificationFile):
    Dict = {}
    Metadata = lara_utils.read_json_file(MetadataFile)
    if Metadata == False:
        return
    for Language in Metadata:
        classify_sentences_by_dialogue_and_humour_single_language(Language, Metadata[Language], Dict)
    lara_utils.write_json_to_file_plain_utf8(Dict, ClassificationFile)
    lara_utils.print_and_flush(f'--- Written classified sentences to {ClassificationFile}')

##    "english": { 
##		"file": "$LARA/tmp/lrec_2022_english_shortened.csv",
##		"data": [   
##					{  "id": "lpp_english",
##						"human": "$LARA/Content/the_little_prince_lrec2022/corpus/local_config_shortened.json",
##						"tts": "$LARA/Content/the_little_prince_lrec2022/corpus/local_config_tts_shortened.json",
##						"word_time": 0.0,
##						"segment_time": "all"
##					}
##				]
##	},

_lrec_2022_sentence_classification_file = '$LARA/tmp_resources/lrec_2022_sentence_classifications.json'

_chapter_classifications = { '2': ( 'humour', 'dialogue' ),
                             '4': ( 'humour', 'not_dialogue' ),
                             '8': ( 'not_humour', 'not_dialogue' ),
                             '9': ( 'not_humour', 'dialogue' )
                             }

_chapters = list(_chapter_classifications.keys())

def classify_sentences_by_dialogue_and_humour_single_language(Language, MetadataItem, Dict):
    lara_utils.print_and_flush(f'--- Classifying sentences for "{Language}"')
    ConfigFile = MetadataItem['data'][0]['human']
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    SegmentsRecordingFile = lara_top.lara_tmp_file('ldt_segment_recording_file_full_json', Params)
    SegmentData = lara_utils.read_json_file(SegmentsRecordingFile)
    if not check_that_texts_are_in_segment_data(_chapters, SegmentData):
        lara_utils.print_and_flush(f'*** Error: not all chapters found in data for "{Language}"')
        return
    CurrentChapter = False
    SubDict = {}
    for SegmentDataItem in SegmentData:
        Text = SegmentDataItem['text']
        if Text in _chapters:
            CurrentChapter = Text
        elif CurrentChapter != False:
            Classification = _chapter_classifications[CurrentChapter]
            SubDict[Text] = Classification
    Dict[Language] = SubDict

def check_that_texts_are_in_segment_data(Texts, SegmentData):
    for Text in Texts:
        if not check_that_text_is_in_segment_data(Text, SegmentData):
            return False
    return True

def check_that_text_is_in_segment_data(Text, SegmentData):
    for SegmentDataItem in SegmentData:
        if Text == SegmentDataItem['text']:
            return True
    lara_utils.print_and_flush(f'*** Error: "{Text}" not found')
    return False

# --------------------------------

def mark(Str, Type):
    if Type == 'better':
        BackgroundColour = 'yellow'
    elif Type == 'nearly':
        BackgroundColour = 'orange'
    else:
        lara_utils.print_and_flush(f'*** Warning: unknown second argument to "mark", "{Type}"')
        return Str
    return { 'value': Str, 'background_colour': BackgroundColour }

def add_italics_and_parens(Elt):
    return f'<i>({Elt})</i>' if Elt != '*' else Elt

def percentage_to_1_dp(Number):
    return "%.1f" % ( 100.0 * Number )

def number_to_2_dp(Number):
    return "%.2f" % Number 

# --------------------------------------------------------

def print_html_table(Caption, Header, List, File, Params):
    List1 = [ Header ] + List 
    write_out_html_table(Caption, List1, File, Params)

def write_out_html_table(Caption, Lines, File, Params):
    HTMLLines = table_lines_to_html_lines(Caption, Lines, Params)
    lara_utils.write_unicode_text_file('\n'.join(HTMLLines), File)
    lara_utils.print_and_flush(f'--- Written file ({len(Lines)} lines) to {File}')

def table_lines_to_html_lines(Caption, Lines, Params):
    Intro = table_lines_intro(Caption, Params)
    Body = table_lines_to_html_lines1(Lines)
    Closing = table_lines_closing()
    return Intro + Body + Closing

def table_lines_intro(Caption, Params):
    return ['<head>',
	    '<meta http-equiv="Content-Type" content="text/html;charset=UTF-8">',
	    '<style>',
	    'table, th, td {'
            'border: 1px solid black;',
            'border-collapse: collapse;',
            'padding: 5px;',
	    '</style>',
	    '</head>',
	    '<body>',
            f'<h2>{Caption}</h2>', 
	    '<table>']

def table_lines_to_html_lines1(TableLines):
    ListsOfLines = [ table_line_to_html_lines(TableLine) for TableLine in TableLines ]
    return [ HTMLLine for HTMLLines in ListsOfLines for HTMLLine in HTMLLines ]

def table_line_to_html_lines(TableLine):
    Opening = line_opening()
    Body = [ table_line_item_to_html_line(Item) for Item in TableLine ]
    Closing = line_closing()
    return Opening + Body + Closing

def line_opening():
    return ['<tr>']

_html_table_height = '10px'

def table_line_item_to_html_line(Element):
    if isinstance(Element, dict) and 'value' in Element and 'background_colour' in Element:
        Value = Element['value']
        BackgroundColour = Element['background_colour']
        ColourCode = colour_to_code(BackgroundColour)
        return f'<td style="height:{_html_table_height}; text-align:center; background-color:{ColourCode}">{Value}</td>'
    elif isinstance(Element, dict) and 'value' in Element and 'rowspan' in Element:
        Value = Element['value']
        Rowspan = Element['rowspan']
        return f'<td style="height:{_html_table_height}; text-align:center" rowspan="{Rowspan}">{Value}</td>'
    else:
        return f'<td style="height:{_html_table_height}; text-align:center">{Element}</td>'

def colour_to_code(Colour):
    if Colour == 'yellow':
        return '#ffff00'
    if Colour == 'orange':
        return '#ff9900'
    else:
        lara_utils.print_and_flush(f'*** Error: unknown colour "{Colour}"')
        return False

def line_closing():
    return ['</tr>']

def table_lines_closing():
    return ['</table>',
	    '</body>',
	    '</html>']

