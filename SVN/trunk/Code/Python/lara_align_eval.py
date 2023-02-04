
import lara_align_from_audio
import lara_config
import lara_split_and_clean
import lara_asr
import lara_audio
import lara_utils

def print_alignment_statistics(ConfigFile):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if Params == False:
        return
    lara_utils.print_and_flush(f'\n\n=====================================')
    print_word_error_rates(Params)
    lara_utils.print_and_flush(f'\n\n=====================================')
    print_double_segmented_corpus_statistics(Params)

def print_word_error_rates(Params):
    Dir = Params.segment_audio_directory
    if Dir == '':
        lara_utils.print_and_flush(f'*** Error: unable to calculate recognition WER: segment_audio_directory not defined')
        return
    AudioMetadata = lara_audio.read_ldt_metadata_file(Dir)
    if AudioMetadata == False:
        lara_utils.print_and_flush(f'*** Error: unable to find audio metadata')
        return
    RecResults = lara_asr.read_rec_results_file(Dir)
    if RecResults == False:
        lara_utils.print_and_flush(f'*** Error: unable to find rec results')
        return
    AudioMetadataDict = { Item['file']: Item['text'] for Item in AudioMetadata
                          if not '*no_text*' in Item['text'] and not 'merged' in Item['file'] }
    RecResultDict = { Item['file']: Item['result']['transcript'] for Item in RecResults
                      if isinstance(Item['result'], dict) and 'transcript' in Item['result'] and not Item['result']['transcript'] == False }
    ( TotalFiles, TotalWords, TotalWordErrors, TotalChars, TotalCharErrors ) = ( 0, 0, 0, 0, 0 )
    for File in AudioMetadataDict:
        if File in RecResultDict:
            ( MetadataTranscript, RecTranscript ) = (  AudioMetadataDict[File], RecResultDict[File] )
            ( MetadataWords, RecWords ) = ( normalise_to_words(MetadataTranscript), normalise_to_words(RecTranscript) )
            ( MetadataChars, RecChars ) = ( ' '.join(MetadataWords), ' '.join(RecWords) )
            ( NWords, NWordErrors ) = ( len(MetadataWords), lara_utils.word_edit_distance(MetadataWords, RecWords) )
            ( NChars, NCharErrors ) = ( len(MetadataChars), lara_utils.word_edit_distance(MetadataChars, RecChars) )
            print_metadata_rec_and_errors(MetadataTranscript, RecTranscript, NWords, NWordErrors, NChars, NCharErrors)
            TotalFiles += 1
            TotalWords += NWords
            TotalWordErrors += NWordErrors
            TotalChars += NChars
            TotalCharErrors += NCharErrors
    lara_utils.print_and_flush(f'----------------')
    lara_utils.print_and_flush(f'     #Files: {TotalFiles}')
    lara_utils.print_and_flush(f'     #Words: {TotalWords}')
    lara_utils.print_and_flush(f'#WordErrors: {TotalWordErrors}')
    lara_utils.print_and_flush(f'     #Chars: {TotalChars}')
    lara_utils.print_and_flush(f'#CharErrors: {TotalCharErrors}')
    if TotalWords != 0:
        lara_utils.print_and_flush(f'    WER: {100.0 * TotalWordErrors / TotalWords:.1f}%')
        lara_utils.print_and_flush(f'   ChER: {100.0 * TotalCharErrors / TotalChars:.1f}%')

def print_metadata_rec_and_errors(MetadataTranscript, RecTranscript, NWords, NWordErrors, NChars, NCharErrors):
    lara_utils.print_and_flush(f'----------------')
    lara_utils.print_and_flush(f'         Ref: {MetadataTranscript}')
    lara_utils.print_and_flush(f'         Rec: {RecTranscript}')
    lara_utils.print_and_flush(f'      #Words: {NWords}')
    lara_utils.print_and_flush(f' #WordErrors: {NWordErrors}')
    lara_utils.print_and_flush(f'      #Chars: {NChars}')
    lara_utils.print_and_flush(f' #CharErrors: {NCharErrors}')

def print_double_segmented_corpus_statistics(Params):
    DoubleSegmentedFile = Params.double_segmented_corpus
    UntaggedFile = Params.untagged_corpus
    if DoubleSegmentedFile == '':
        lara_utils.print_and_flush(f'*** Error: double_segmented_corpus not defined')
        return
    if UntaggedFile == '':
        lara_utils.print_and_flush(f'*** Error: untagged_corpus not defined')
        return
    DSText = lara_utils.read_lara_text_file(DoubleSegmentedFile)
    if DSText == False:
        lara_utils.print_and_flush(f'*** Error: unable to read {DoubleSegmentedFile}')
        return
    Text = lara_utils.read_lara_text_file(UntaggedFile)
    if Text == False:
        lara_utils.print_and_flush(f'*** Error: unable to read {UntaggedFile}')
        return
    ( AudioSegments, TrSegments ) = ( DSText.split('||'), DSText.split('//') )
    ( AudioSegmentsWords, TrSegmentsWords ) = ( normalise_list_to_words(AudioSegments), normalise_list_to_words(TrSegments) )
    JointSegments = Text.split('||')
    JointSegmentsWords = normalise_list_to_words(JointSegments)
    print_segment_statistics('Splitting on silences', AudioSegmentsWords)
    print_segment_statistics('Translation alignment', TrSegmentsWords)
    print_segment_statistics('Joint alignment', JointSegmentsWords)

def print_segment_statistics(Heading, Segments):
    NSegments = len(Segments)
    NWords = sum([len(Segment) for Segment in Segments])
    AvSegmentLength = NWords / NSegments if NSegments != 0 else 0.0
    lara_utils.print_and_flush(f'----------------')
    lara_utils.print_and_flush(f'{Heading}')
    lara_utils.print_and_flush(f' #Segments: {NSegments}')
    lara_utils.print_and_flush(f'   #NWords: {NWords}')
    lara_utils.print_and_flush(f'Av. length: {AvSegmentLength:.1f} words')

def normalise_list_to_words(ListOfStrs):
    return [ normalise_to_words(Str) for Str in ListOfStrs ]
    
def normalise_to_words(Str):
    Pairs = lara_split_and_clean.string_to_annotated_words(Str)[0]
    return [ Pair[0].lower() for Pair in Pairs if Pair[1] != '' ]
    
