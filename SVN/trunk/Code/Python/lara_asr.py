##
import lara_audio
import lara_split_and_clean
import lara_config
import lara_picturebook
import lara_utils
##from google.cloud import speech_v1p1beta1 as speech
##import io
##import base64
##import sys
##import requests
    
def test(Id):
    if Id == 'candide1':
        Files = [ '$LARA/Content/candide/audio/litteratureaudio/extracted_file_ch1_2.mp3',
                  '$LARA/Content/candide/audio/litteratureaudio/extracted_file_ch1_5.mp3'
##                  '$LARA/Content/candide/audio/litteratureaudio/extracted_file_ch1_6.mp3',
##                  '$LARA/Content/candide/audio/litteratureaudio/extracted_file_ch1_7.mp3',
##                  '$LARA/Content/candide/audio/litteratureaudio/extracted_file_ch1_8.mp3',
##                  '$LARA/Content/candide/audio/litteratureaudio/extracted_file_ch1_9.mp3',
##                  '$LARA/Content/candide/audio/litteratureaudio/extracted_file_ch1_10.mp3'
                  ]
        for File in Files:
            lara_utils.print_and_flush(f'--- Processing: {File}')
            Result = mp3_to_rec_responses(File, 'fr-FR')
            lara_utils.prettyprint(Result)
    elif Id == 'candide2':
        Files = [ '$LARA/Content/candide/audio/litteratureaudio/extracted_file_ch1_5.mp3'
##                  '$LARA/Content/candide/audio/litteratureaudio/extracted_file_ch1_6.mp3',
##                  '$LARA/Content/candide/audio/litteratureaudio/extracted_file_ch1_7.mp3',
##                  '$LARA/Content/candide/audio/litteratureaudio/extracted_file_ch1_8.mp3',
##                  '$LARA/Content/candide/audio/litteratureaudio/extracted_file_ch1_9.mp3',
##                  '$LARA/Content/candide/audio/litteratureaudio/extracted_file_ch1_10.mp3'
                  ]
        OutFile = '$LARA/Content/candide/audio/litteratureaudio/recognition_results1.json'
        LanguageCode = 'fr-FR'
        Timeout = 0
        recognise_mp3s_and_store_results(Files, LanguageCode, Timeout, OutFile)
    elif Id == 'candide3':
        Files = [ 'gs://candide/extracted_file_ch1_5.mp3'
                  ]
        OutFile = '$LARA/Content/candide/audio/litteratureaudio/recognition_results_long1.json'
        LanguageCode = 'fr-FR'
        Timeout = 20
        recognise_mp3s_and_store_results(Files, LanguageCode, Timeout, OutFile)
    elif Id == 'candide_ch1':
        Files = [ 'gs://candide/litteratureaudio_src/Voltaire_-_Candide_Chap01.mp3'
                  ]
        OutFile = '$LARA/Content/candide/audio/litteratureaudio/recognition_results_ch1.json'
        LanguageCode = 'fr-FR'
        Timeout = 300
        recognise_mp3s_and_store_results(Files, LanguageCode, Timeout, OutFile)
    elif Id == 'candide_ch1_separate':
        Files = [ f'$LARA/Content/candide/audio/litteratureaudio/extracted_file_ch1_{I}.mp3' for I in range(1, 32) ]
        OutFile = '$LARA/Content/candide/audio/litteratureaudio/recognition_results_ch1_separate.json'
        LanguageCode = 'fr-FR'
        Timeout = 0
        recognise_mp3s_and_store_results(Files, LanguageCode, Timeout, OutFile)
    elif Id == 'candide_ch1_fix':
        File1 = '$LARA/Content/candide/audio/litteratureaudio/recognition_results_ch1_separate.json'
        File2 = '$LARA/Content/candide/audio/litteratureaudio/recognition_results_ch1_separate_fixed.json'
        LanguageCode = 'fr-FR'
        Timeout = 0
        try_to_fix_cutoffs_in_rec_results(File1, LanguageCode, Timeout, File2)    
    elif Id == 'candide_ch2_separate':
        Files = [ f'$LARA/Content/candide/audio/litteratureaudio/extracted_file_ch2_{I}.mp3' for I in range(33, 85) ]
        OutFile = '$LARA/Content/candide/audio/litteratureaudio/recognition_results_ch2_separate.json'
        LanguageCode = 'fr-FR'
        Timeout = 0
        recognise_mp3s_and_store_results(Files, LanguageCode, Timeout, OutFile)
    elif Id == 'candide_ch2_fix':
        File1 = '$LARA/Content/candide/audio/litteratureaudio/recognition_results_ch2_separate.json'
        File2 = '$LARA/Content/candide/audio/litteratureaudio/recognition_results_ch2_separate_fixed.json'
        LanguageCode = 'fr-FR'
        Timeout = 0
        try_to_fix_cutoffs_in_rec_results(File1, LanguageCode, Timeout, File2)    
    elif Id == 'combray_overture':
        Files = [ f'$LARA/Content/combray/audio/MoniqueVincens_overture/extracted_file_ch1_{I}.mp3' for I in range(1, 79) ]
        OutFile = '$LARA/Content/combray/audio/MoniqueVincens_overture/recognition_results_overture.json'
        LanguageCode = 'fr-FR'
        Timeout = 0
        recognise_mp3s_and_store_results(Files, LanguageCode, Timeout, OutFile)
    elif Id == 'combray_overture_fix':
        File1 = '$LARA/Content/combray/audio/MoniqueVincens_overture/recognition_results_overture.json'
        File2 = '$LARA/Content/combray/audio/MoniqueVincens_overture/recognition_results_overture_fixed.json'
        LanguageCode = 'fr-FR'
        Timeout = 0
        try_to_fix_cutoffs_in_rec_results(File1, LanguageCode, Timeout, File2)
    elif Id == 'combray_ch1_all':
        Files = [ f'$LARA/Content/combray/audio/MoniqueVincens_full/extracted_file_ch1_{I}.mp3' for I in range(1, 543) ]
        #Files = [ f'$LARA/Content/combray/audio/MoniqueVincens_full/extracted_file_ch1_{I}.mp3' for I in range(1, 10) ]
        OutFile = '$LARA/Content/combray/audio/MoniqueVincens_full/recognition_results_ch1_all.json'
        LanguageCode = 'fr-FR'
        Timeout = 0
        recognise_mp3s_and_store_results(Files, LanguageCode, Timeout, OutFile)
    elif Id == 'recueillement_tmp':
        Files = [ f'$LARA/Content/recueillement_tmp/audio/litteratureaudio/extracted_file__{I}.mp3' for I in range(2, 18) ]
        OutFile = '$LARA/Content/recueillement_tmp/audio/litteratureaudio/recognition_results.json'
        LanguageCode = 'fr-FR'
        Timeout = 0
        recognise_mp3s_and_store_results(Files, LanguageCode, Timeout, OutFile)
    elif Id == 'recueillement_tmp_from_config':
        ConfigFile = '$LARA/Content/recueillement_tmp/corpus/local_config.json'
        #MaxFilesToRecogniseOrAll = 'all'
        MaxFilesToRecogniseOrAll = 5
        recognise_and_store_in_segment_audio_dir(ConfigFile, MaxFilesToRecogniseOrAll)
    elif Id == 'irish1':
        SpeechFile = '$LARA/Content/an-prionsa-beag-lrec2022/audio/human/attempt1_humorous_ch2_norm_01.mp3'
        LanguageCode = 'ga-GA'
        Result = mp3_to_rec_responses(SpeechFile, LanguageCode)
        lara_utils.prettyprint(Result)
    elif Id == 'irish2':
        ConfigFile = '$LARA/Content/an-prionsa-beag-lrec2022/corpus/local_config_human.json'
        #MaxFilesToRecogniseOrAll = 'all'
        MaxFilesToRecogniseOrAll = 5
        recognise_and_store_in_segment_audio_dir(ConfigFile, MaxFilesToRecogniseOrAll)
    else:
        lara_utils.print_and_flush(f'*** Error: unknown ID: {Id}')

# -------------------------------------------------------------------------------

# Send previously unprocessed files in Params.segment_audio_directory for recognition
# and stores results in its recognition_results.json file

_recognition_batch_size = 20

def recognise_and_store_in_segment_audio_dir(ConfigFile, MaxFilesToRecogniseOrAll0):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if Params == False:
        return
    MaxFilesToRecogniseOrAll = interpret_second_arg_to_recognise_and_store(MaxFilesToRecogniseOrAll0)
    if MaxFilesToRecogniseOrAll != 'all' and not isinstance(MaxFilesToRecogniseOrAll, ( int )):
        return
    ( LanguageCode, AudioDir ) = ( Params.google_asr_language_code, Params.segment_audio_directory )
    if LanguageCode == '':
        lara_utils.print_and_flush(f'*** Error: google_asr_language_code not set in config file')
        return
    if AudioDir == '':
        lara_utils.print_and_flush(f'*** Error: segment_audio_directory not set in config file')
        return
    FilesToRecognise = get_segment_audio_files_to_recognise(AudioDir, MaxFilesToRecogniseOrAll)
    RecognitionResultFile = lara_utils.get_tmp_json_file(Params)
    # Use "plain" as opposed to "large" recognition
    Timeout = 0
    while True:
        NFilesLeft = len(FilesToRecognise)
        if NFilesLeft == 0:
            return
        elif NFilesLeft <= _recognition_batch_size:
            FilesToRecogniseBatch = FilesToRecognise
            FilesToRecognise = []
        else:
            FilesToRecogniseBatch = FilesToRecognise[:_recognition_batch_size]
            FilesToRecognise = FilesToRecognise[_recognition_batch_size:]
        recognise_mp3s_and_store_results(FilesToRecogniseBatch, LanguageCode, Timeout, RecognitionResultFile)
        store_recognition_results_in_segment_audio_dir(RecognitionResultFile, AudioDir)

def interpret_second_arg_to_recognise_and_store(MaxFilesToRecogniseOrAll0):
    if MaxFilesToRecogniseOrAll0 == 'all' or isinstance(MaxFilesToRecogniseOrAll0, ( int )):
        return MaxFilesToRecogniseOrAll0
    elif isinstance(MaxFilesToRecogniseOrAll0, ( str )):
        return lara_utils.safe_string_to_int(MaxFilesToRecogniseOrAll0)
    else:
        return False

# Segment audio dir has a file called recognition_results.json
# which keeps the results in the same format as recognise_mp3s_and_store_results
# except that file names are relative to the audio dir

def get_segment_audio_files_to_recognise(AudioDir, MaxFilesToRecogniseOrAll):
    AudioMetadata = lara_audio.read_ldt_metadata_file(AudioDir)
    if AudioMetadata == False:
        return
    RecResults = read_rec_results_file(AudioDir)
    RecognisedFilesDict = { RecResult['file']: True for RecResult in RecResults }
    UnrecognisedFiles = [ f"{AudioDir}/{Item['file']}" for Item in AudioMetadata
                          if not Item['file'] in RecognisedFilesDict
                          # Don't recognise the merged files
                          and not 'merged' in Item['file'] ]
    return UnrecognisedFiles if MaxFilesToRecogniseOrAll == 'all' else UnrecognisedFiles[:MaxFilesToRecogniseOrAll]

def store_recognition_results_in_segment_audio_dir(RecognitionResultFile, AudioDir):
    NewRecResults0 = lara_utils.read_json_file(RecognitionResultFile)
    if NewRecResults0 == False:
        return
    NewRecResults = [ make_file_relative_in_rec_result(RecResult) for RecResult in NewRecResults0 ]
    RecResults = read_rec_results_file(AudioDir)
    RecResultsDict = { RecResult['file']: RecResult for RecResult in RecResults }
    for RecResult in NewRecResults:
        RecResult1 = make_file_relative_in_rec_result(RecResult)
        RecResultsDict[RecResult1['file']] = RecResult1
    UpdatedRecResults = list(RecResultsDict.values())
    write_rec_results_file(UpdatedRecResults, AudioDir)
    lara_utils.print_and_flush(f'--- Written rec results file ({len(UpdatedRecResults)} items)')

def make_file_relative_in_rec_result(RecResult):
    return { 'file': lara_utils.base_name_for_pathname(RecResult['file']),
             'result': RecResult['result'] }

def read_rec_results_file(AudioDir):
    RecResultsFile = f'{AudioDir}/recognition_results.json'
    return [] if not lara_utils.file_exists(RecResultsFile) else lara_utils.read_json_file(RecResultsFile)

def write_rec_results_file(RecResults, AudioDir):
    RecResultsFile = f'{AudioDir}/recognition_results.json'
    lara_utils.write_json_to_file_plain_utf8(RecResults, RecResultsFile)

def write_ordered_rec_results_file(RecResults, AudioDir):
    RecResultsFile = f'{AudioDir}/recognition_results_ordered.json'
    lara_utils.write_json_to_file_plain_utf8(RecResults, RecResultsFile)

def make_plain_rec_results_file(AudioDir):
    RecResults = read_rec_results_file(AudioDir)
    PlainRecResultFile = f'{AudioDir}/recognition_results_plain.json'
    TextRecResults = [ Item['result']['transcript'] for Item in RecResults
                       if isinstance(Item, dict) and 'result' in Item and isinstance(Item['result'], dict) and 'transcript' in Item['result'] and Item['result']['transcript'] != False ]
    lara_utils.write_json_to_file_plain_utf8(TextRecResults, PlainRecResultFile)

# -------------------------------------------------------------------------------

def recognise_mp3s_and_store_results(Files, LanguageCode, Timeout, OutFile):
    AllResults = []
    if not check_all_files_exist(Files):
        return
    NFixed = 0
    for File in Files:
        lara_utils.print_and_flush(f'--- Processing: {File}')
        if Timeout == 0:
            Result = mp3_to_rec_responses(File, LanguageCode)
        elif LanguageCode == 'ga-GA':
            lara_utils.print_and_flush(f'*** Error: no offline recognition yet for Irish')
            return { 'transcript': False }
        else:
            import lara_google_cloud_asr
            Result = lara_google_cloud_asr.large_mp3_to_rec_responses_google(File, LanguageCode, Timeout)
        lara_utils.print_and_flush(f'--- Recognised: {Result["transcript"]}')
        FileAndResult = { 'file': File, 'result': Result }
        ( FileAndResultPossiblyFixed, NeededToFix ) = try_to_fix_cutoffs_in_single_rec_result(FileAndResult, LanguageCode, Timeout)
        AllResults += [ FileAndResultPossiblyFixed ]
        NFixed += 1 if NeededToFix == True else 0
    lara_utils.write_json_to_file_plain_utf8(AllResults, OutFile)
    lara_utils.print_and_flush(f'--- Written {len(AllResults)} recognition results ({NFixed} fixed) to file: {OutFile}')

def check_all_files_exist(Files):
    Okay = True
    for File in Files:
        if not lara_utils.file_exists(File):
            lara_utils.print_and_flush(f'*** Error: file not found {File}')
            Okay = False
    return Okay

def mp3_to_rec_responses(SpeechFile, LanguageCode):
    if not lara_utils.file_exists(SpeechFile):
        lara_utils.print_and_flush(f'*** Warning: file not found: {SpeechFile}')
        return { 'transcript': False }
    AbsSpeechFile = lara_utils.absolute_file_name(SpeechFile)
    if LanguageCode == 'ga-GA':
        import lara_asr_irish
        return mp3_to_rec_responses_irish(AbsSpeechFile)
    else:
        import lara_google_cloud_asr
        return lara_google_cloud_asr.mp3_to_rec_responses_google(AbsSpeechFile, LanguageCode)

#-------------------------------------

def try_to_fix_cutoffs_in_rec_results(RecResultsFile, LanguageCode, Timeout, RecResultsFile1):
    Results = lara_utils.read_json_file(RecResultsFile)
    if Results == False:
        return
    ( OutResults, NFixed ) = ( [], 0 )
    for Result in Results:
        ( NewResult, TriedToFix ) = try_to_fix_cutoffs_in_single_rec_result(Result, LanguageCode, Timeout)
        OutResults += [ NewResult ]
        if TriedToFix:
            NFixed += 1
    lara_utils.write_json_to_file_plain_utf8(OutResults, RecResultsFile1)
    lara_utils.print_and_flush(f'--- Written {len(OutResults)} results ({NFixed} fixed) to {RecResultsFile1}')

# times in seconds
_cutoff_for_fixing = 1.5 
_time_to_skip_when_fixing = 0.1
   
def try_to_fix_cutoffs_in_single_rec_result(RecResult, LanguageCode, Timeout):
    File = RecResult['file']
    LengthInSeconds = lara_utils.length_of_mp3(File)
    RecTranscript = RecResult['result']['transcript']
    Params = lara_config.default_params()
    if RecTranscript == False:
        return ( RecResult, False )
    if 'word_info' in RecResult['result'] and len(RecResult['result']['word_info']) != 0:
        LastRecWordTime = RecResult['result']['word_info'][-1]['start_end'][1]
    else:
        return ( RecResult, False )
    if LengthInSeconds - LastRecWordTime < _cutoff_for_fixing:
        return ( RecResult, False )
    ( FromTime, ToTime ) = ( LastRecWordTime + _time_to_skip_when_fixing, LengthInSeconds )
    ExtractedFile = extract_part_of_mp3(File, FromTime, ToTime, 'part2', Params)
    if ExtractedFile == False:
        return ( RecResult, False )
    lara_utils.print_and_flush(f'--- Retrying recognition on part of {File} {FromTime:.2f}-{ToTime:.2f}s')
    RecResult2 = mp3_to_rec_responses(ExtractedFile, LanguageCode)
    RecTranscript2 = RecResult2['transcript']
    if RecTranscript2 == False:
        lara_utils.print_and_flush(f'--- Retried recognition failed')
        return ( RecResult, False )
    lara_utils.print_and_flush(f'--- Retried recognition succeeded ("{RecTranscript2}"), combining results')
    CombinedResult = { 'file': File,
                       'result': { 'transcript': f'{RecTranscript} {RecTranscript2}',
                                   'confidence': 0.5 * ( RecResult['result']['confidence'] + RecResult2['confidence'] ),
                                   'word_info': RecResult['result']['word_info'] + add_offset_to_word_info(RecResult2['word_info'], FromTime) }
                       }
    return ( try_to_fix_cutoffs_in_single_rec_result(CombinedResult, LanguageCode, Timeout)[0], True )

def add_offset_to_word_info(WordInfo, Offset):
    return [ add_offset_to_word_info_item(Item, Offset) for Item in WordInfo ]

def add_offset_to_word_info_item(Item, Offset):
    Word = Item['word']
    ( Start, End ) = Item['start_end']
    return { 'word': Word, 'start_end':[ Start + Offset, End + Offset ] }


def extract_part_of_mp3(AudioFile, FromTime, ToTime, Label, Params):
    ( BaseFile, Extension ) = lara_utils.file_to_base_file_and_extension(AudioFile)
    ExtractedFile = f'{BaseFile}_{Label}.{Extension}'
    AbsExtractedFile = lara_utils.absolute_file_name(ExtractedFile)
    AbsAudioFile = lara_utils.absolute_file_name(AudioFile)
    Command = f'ffmpeg -i {AbsAudioFile} -ss {FromTime:.2f} -to {ToTime:.2f} -c copy {AbsExtractedFile}'
    lara_utils.print_and_flush(f'--- Extracting audio from {FromTime:.2f}s to {ToTime:.2f}s ({AudioFile})')
    Result = execute_ffmpeg_command(Command, AbsExtractedFile, Params)
    if Result:
        return ExtractedFile
    else:
        lara_utils.print_and_flush(f'\n*** Warning: unable to extract audio')
        lara_utils.print_and_flush(f'*** with command {Command}')
        return False
    
def execute_ffmpeg_command(Command, OutFile, Params):
    lara_utils.delete_file_if_it_exists(OutFile)
    Status = lara_utils.execute_lara_os_call(Command, Params)
    if Status == 0:
        return True
    else:
        return False

#-------------------------------------

def reorder_recognition_results_file(ConfigFile):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if Params == False:
        return
    AudioDir = Params.segment_audio_directory
    if AudioDir == '':
        lara_utils.print_and_flush(f'*** Error: segment_audio_directory not set in config file')
        return
    RecResults = read_rec_results_file(AudioDir)
    if RecResults == []:
        return
    OrderedSegmentAudioFiles = get_ordered_segment_audio_files(Params, AudioDir)
    OrderedRecResults = order_recognition_results(OrderedSegmentAudioFiles, RecResults)
    write_ordered_rec_results_file(OrderedRecResults, AudioDir)
    lara_utils.print_and_flush(f'--- Written ordered rec results file ({len(OrderedRecResults)} files)')
    return

def get_ordered_segment_audio_files(Params, AudioDir):
    lara_utils.add_corpus_id_tag_to_params(Params, 'local_files')
    lara_audio.init_stored_downloaded_audio_metadata()
    lara_audio.read_and_store_ldt_metadata_files([ AudioDir ], 'segments', Params)
    PageOrientedSplitList = lara_split_and_clean.read_split_file('', Params)
    ( Files, TextSoFar ) = ( [], [] )
    for ( PageInfo, Segments ) in PageOrientedSplitList:
        for Segment in Segments:
            if lara_picturebook.is_annotated_image_segment(Segment):
                InnerSegmentList = lara_picturebook.annotated_image_segments(Segment)
                for Segment1 in InnerSegmentList:
                    MinimallyCleaned = Segment1[1]
                    Context = lara_audio.text_so_far_to_context(TextSoFar, Params)
                    File = lara_audio.get_audio_url_for_chunk_or_word(MinimallyCleaned, Context, 'segments', Params)
                    Files += [ File ]
                    TextSoFar += MinimallyCleaned.split()
            else:
                MinimallyCleaned = Segment[1]
                Context = lara_audio.text_so_far_to_context(TextSoFar, Params)
                File = lara_audio.get_audio_url_for_chunk_or_word(MinimallyCleaned, Context, 'segments', Params)
                Files += [ File ]
                TextSoFar += MinimallyCleaned.split()
    return [ lara_utils.base_name_for_pathname(File) for File in Files
             if File != '*no_audio_url*' and File != False ]

def order_recognition_results(OrderedSegmentAudioFiles, RecResults):
    RecResultsDict = { RecResult['file']: RecResult for RecResult in RecResults }
    Out = []
    for File in OrderedSegmentAudioFiles:
        if not File in RecResultsDict:
            lara_utils.print_and_flush(f'*** Warning: {File} not found in rec results')
        else:
            Out += [ RecResultsDict[File] ]
    return Out





        
