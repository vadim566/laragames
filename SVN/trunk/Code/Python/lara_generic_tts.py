
import lara_config
import lara_audio
import lara_parse_utils
import lara_utils
import lara_tts
import random

def test_tts(Id):
    if Id == 'peter_rabbit_segments':
        JSONRecordingScript = '$LARA/tmp_resources/peter_rabbit_tts_record_segments_full.json'
        AudioZipfile = '$LARA/tmp_resources/peter_rabbit_segment_tts.zip'
        ConfigFile = '$LARA/Content/peter_rabbit/corpus/local_config_tts.json'
    elif Id == 'peter_rabbit_words':
        JSONRecordingScript = '$LARA/tmp_resources/peter_rabbit_tts_record_words_full.json'
        AudioZipfile = '$LARA/tmp_resources/peter_rabbit_word_tts.zip'
        ConfigFile = '$LARA/Content/peter_rabbit/corpus/local_config_tts.json'
    elif Id == 'le_bonheur_segments':
        JSONRecordingScript = '$LARA/tmp_resources/le_bonheur_tts_record_segments_full.json'
        AudioZipfile = '$LARA/tmp_resources/le_bonheur_segment_tts.zip'
        ConfigFile = '$LARA/Content/le_bonheur/corpus/local_config_tts.json'
    elif Id == 'le_bonheur_words':
        JSONRecordingScript = '$LARA/tmp_resources/le_bonheur_tts_record_words_full.json'
        AudioZipfile = '$LARA/tmp_resources/le_bonheur_word_tts.zip'
        ConfigFile = '$LARA/Content/le_bonheur/corpus/local_config_tts.json'
    elif Id == 'il_piccolo_principe_segments':
        JSONRecordingScript = '$LARA/tmp_resources/il_piccolo_principe_tts_record_segments_full.json'
        AudioZipfile = '$LARA/tmp_resources/il_piccolo_principe_segment_tts.zip'
        ConfigFile = '$LARA/Content/il_piccolo_principe/corpus/local_config_tts.json'
    elif Id == 'il_piccolo_principe_words':
        JSONRecordingScript = '$LARA/tmp_resources/il_piccolo_principe_tts_record_words_full.json'
        AudioZipfile = '$LARA/tmp_resources/il_piccolo_principe_word_tts.zip'
        ConfigFile = '$LARA/Content/il_piccolo_principe/corpus/local_config_tts.json'
    elif Id == 'sample_irish_segments':
        JSONRecordingScript = '$LARA/tmp_resources/sample_irish_tts_record_segments_full.json'
        AudioZipfile = '$LARA/tmp_resources/sample_irish_segment_tts.zip'
        ConfigFile = '$LARA/Content/sample_irish/corpus/local_config_tts.json'
    else:
        lara_utils.print_and_flush(f'*** Error: unknown ID {Id} in call to test_tts')
        return False
    return create_tts_audio(JSONRecordingScript, ConfigFile, AudioZipfile)

def test_tts_events(Id):
    if Id == 'english_1':
        RSLangId = 'en_uk'
        RSVoiceId = 'Alice-DNN'
        URL = 'https://tts.readspeaker.com/a/speak'
        Text = 'Hello. Goodbye.'
    elif Id == 'english_2':
        RSLangId = 'en_uk'
        RSVoiceId = 'Alice-DNN'
        URL = 'https://tts.readspeaker.com/a/speak'
        Text = 'Once upon a time there were four little rabbits.'
    else:
        lara_utils.print_and_flush(f'*** Error: unknown ID {Id} in call to test_tts_events')
        return False
    return lara_tts.get_events_using_readspeaker(RSLangId, RSVoiceId, URL, Text, 1, 1)

def get_tts_engines_for_language(Lang, ResultFile):
    Engines = lara_config.tts_engines_for_language(Lang)
    lara_utils.write_json_to_file(Engines, ResultFile)

# Create TTS files using a recording script. Put them in a zipfile together with metadata,
# so that they are in the same format as an LDT download file and can be installed in the same way.

def create_tts_audio(JSONRecordingScript, ConfigFile, AudioZipfile):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if not Params:
        return False
    ( TTSEngine, TTSLanguageId, TTSVoice, TTSURL ) = get_tts_parameters(Params, ConfigFile)
    if TTSEngine == False or TTSLanguageId == False or TTSVoice == False or TTSURL == False:
        return False
    RecordingData = lara_utils.read_json_file(JSONRecordingScript)
    if RecordingData == False:
        return False
    TTSSubstitutionRecordingData = load_tts_word_substitution_spreadsheet_if_necessary(Params)
    AudioDir = lara_utils.get_tmp_directory(Params)
    Timestamp = lara_utils.timestamp()
    StartN = random.randint(1, 10000000000)
    ( Language, NGood, NBad, NewMetadata, Count ) = ( Params['language'], 0, 0, [], 1 )
    Total = len(RecordingData + TTSSubstitutionRecordingData) 
    #for RecordingItem in remove_duplicated_recording_items(RecordingData + TTSSubstitutionRecordingData):
    for RecordingItem in RecordingData + TTSSubstitutionRecordingData:
        NewTTSFile = create_tts_audio_for_recording_item(RecordingItem,
                                                         TTSEngine, TTSLanguageId, TTSVoice, TTSURL,
                                                         AudioDir, Timestamp, StartN, NGood + 1, Count, Total)
        Count += 1
        if NewTTSFile == False:
            NBad += 1
        else:
            NGood += 1
            RecordingItem['file'] = NewTTSFile
            NewMetadata += [ RecordingItem ]
    lara_audio.write_ldt_metadata_file(NewMetadata, AudioDir)
    lara_utils.print_and_flush(f'--- Used {TTSEngine} TTS to create audio data in {AudioDir} ({NGood} succeeded, {NBad} failed)')
    lara_utils.delete_file_if_it_exists(AudioZipfile)
    Result = lara_utils.make_zipfile(AudioDir, AudioZipfile)
    if Result == True:
        lara_utils.delete_directory_if_it_exists(AudioDir)
        return True
    else:
        return False

##_tts_info = { 'readspeaker':
##              {   'url': 'https://tts.readspeaker.com/a/speak',
##                  'languages':
##                  { 'english':
##                    {  'language_id': 'en_uk',
##                       'voices': [ 'Alice-DNN' ]
##                       },
##               ...

## Return 4-tuple ( TTSEngine, TTSLanguageId, TTSVoice, TTSURL)
def get_tts_parameters(Params, ConfigFile):
    if Params.language == '':
        lara_utils.print_and_flush(f'*** Error: "language" not defined in config file: {ConfigFile}')
        return ( False, False, False, False )
    else:
        Language = Params.language
    if Params.tts_engine in ( 'None', None, '' ):
        lara_utils.print_and_flush(f'*** Error: "tts_engine" not defined in config file: {ConfigFile}')
        return ( False, False, False, False )
    else:
        TTSEngine = Params.tts_engine
        if not TTSEngine in lara_config._tts_info:
            lara_utils.print_and_flush(f'*** Error: unknown TTS engine "{TTSEngine}" defined in config file: {ConfigFile}')
            return ( False, False, False, False )
        if not Language in lara_config._tts_info[TTSEngine]['languages']:
            lara_utils.print_and_flush(f'*** Error: TTS engine "{TTSEngine}" does not support language "{Language}"')
            return ( False, False, False, False )                                          
    RelevantTTSInfo = lara_config._tts_info[TTSEngine]['languages'][Language]
    TTSLanguageId = RelevantTTSInfo['language_id']
    if Params.tts_voice != '':
        TTSVoice = Params.tts_voice
        if not TTSVoice in RelevantTTSInfo['voices']:
            lara_utils.print_and_flush(f'*** Error: TTS engine "{TTSEngine}" does not support voice "{TTSVoice}"')
            return ( False, False, False, False )
    else:
        # Take first voice if none is explicitly specified
        TTSVoice = RelevantTTSInfo['voices'][0]
    TTSURL = Params.tts_url if Params.tts_url != '' else lara_config._tts_info[TTSEngine]['url']
    return ( TTSEngine, TTSLanguageId, TTSVoice, TTSURL)

def remove_duplicated_recording_items(RecordingItems):
    ( Dict, OutList ) = ( {}, [] )
    for Item in RecordingItems:
        Key = Item['annotated_text'] if 'annotated_text' in Item else Item['text']
        if not Key in Dict:
            OutList += Item
            Dict[Key] = True
    return OutList
    
def create_tts_audio_for_recording_item(RecordingItem,
                                        TTSEngine, TTSLanguageId, TTSVoice, TTSURL,
                                        AudioDir, Timestamp, StartN, Index, Count, Total):
    if not isinstance(RecordingItem, dict) or \
       not 'text' in RecordingItem and not 'annotated_text' in RecordingItem:
        lara_utils.print_and_flush(f'*** Error: bad item in TTS recording script: {RecordingItem}')
        return False
    AnnotatedText = RecordingItem['annotated_text'] if 'annotated_text' in RecordingItem else RecordingItem['text']
    AnnotatedText1 = tts_word_substitutions[AnnotatedText] if AnnotatedText in tts_word_substitutions else AnnotatedText
    ShortFile = f'tts_{Timestamp}_{StartN + Index}.mp3'
    LongFile = f'{AudioDir}/{ShortFile}'
    Result = lara_tts.call_tts_engine(TTSEngine, TTSLanguageId, TTSVoice, TTSURL, AnnotatedText1, LongFile, Count, Total)
    return False if Result == False else ShortFile

# Sometimes we want TTS to pronounce a word as though it were a different word.
# For example in French we want to pronounce "j'" as though it were "je" with ReadSpeaker,
# since the default ReadSpeaker pronunciation of "j'" is to treat it as the letter J.

tts_word_substitutions = {}

def get_tts_substitute_words():
    return lara_utils.remove_duplicates([ tts_word_substitutions[Word] for Word in tts_word_substitutions ])

def load_tts_word_substitution_spreadsheet_if_necessary(Params):
    WordSubstitutionSpreadsheet = Params.tts_word_substitution_spreadsheet
    if WordSubstitutionSpreadsheet == '':
        return []
    WordSubstitutions = lara_utils.read_lara_csv(WordSubstitutionSpreadsheet)
    if WordSubstitutions == False:
        lara_utils.print_and_flush(f'*** Error: unable to read {WordSubstitutionSpreadsheet}')
        return []
    SubstitutionsProcessed = 0
    for Record in WordSubstitutions:
        if len(Record) >= 2 and not null_field(Record[0]) and not null_field(Record[1]):
            Word = normalise_word(Record[0])
            SubstitutedWord = normalise_word(Record[1])
            tts_word_substitutions[Word] = SubstitutedWord
            SubstitutionsProcessed += 1
    lara_utils.print_and_flush(f'--- Loaded {SubstitutionsProcessed} TTS word substitutions from {WordSubstitutionSpreadsheet}')
    # We need to record both the words that are substituted and the words they substitute to.
    return [ { 'text': Word } for Word in get_tts_substitute_words() ] + \
           [ { 'text': Word } for Word in tts_word_substitutions ]
    
def null_field(Str):
    return Str == '' or Str.isspace()

def normalise_word(Word):
    return lara_audio.make_word_canonical_for_word_recording(Word.strip())

