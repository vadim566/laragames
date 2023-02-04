
import lara_top
import lara_translations
import lara_asr
import lara_audio
import lara_picturebook
import lara_install_audio_zipfile
import lara_config
import lara_split_and_clean
import lara_html
import lara_align_adjust
import lara_partitioned_text_files
import lara_parse_utils
import lara_utils
import re
import time

def test(Id):
    if Id == 'combray':
        AudioId = 'ch1'
        AudioFile = '$LARA/Content/combray/audio/MoniqueVincens_src/Marcel_Proust_-_Du_Cote_de_chez_Swann_L1_Combray_Chap01.mp3'
        AudioLabelsFile = '$LARA/Content/combray/corpus/LitteratureAudioCh1LabelTrack.txt'
        SourceTextFile = '$LARA/Content/combray/corpus/combray_segmented_by_audio.txt'
        TargetTextFile = '$LARA/Content/combray/corpus/combray_en_segmented_by_audio.txt'
        ConfigFile = '$LARA/Content/combray/corpus/local_config_overture_segmented_by_audio.json'
        StartLabel = 0
        EndLabel = 78
        create_aligned_files(AudioFile, AudioId, AudioLabelsFile, SourceTextFile, TargetTextFile, ConfigFile, StartLabel, EndLabel)
    elif Id == 'candide_plain_corpus':
        ConfigFile = '$LARA/Content/candide/corpus/local_config.json'
        LabelledFile = '$LARA/Content/candide/corpus/candide_plain.txt'
        create_plain_corpus(ConfigFile, LabelledFile)
    elif Id == 'candide_labelled_corpus':
        ConfigFile = '$LARA/Content/candide/corpus/local_config.json'
        LabelledFile = '$LARA/Content/candide/corpus/candide_segmented_for_audio.txt'
        create_corpus_with_numbered_labels(ConfigFile, LabelledFile)
    elif Id == 'candide_word_pair_corpus':
        ConfigFile = '$LARA/Content/candide/corpus/local_config.json'
        WordPairFile = '$LARA/Content/candide/corpus/candide_word_pairs.json'
        create_word_pair_corpus(ConfigFile, WordPairFile)
    elif Id == 'candide_rec_align_ch1_small':
        RecResultsFile = '$LARA/Content/candide/audio/litteratureaudio/recognition_results_ch1_separate_small.json'
        PairsFile = '$LARA/Content/candide/corpus/candide_word_pairs_small.json'
        BeamWidth = 20
        StartPage = 1
        AlignedFile = '$LARA/Content/candide/corpus/candide_ch1_aligned_small.json'
        SegmentedTextFile = '$LARA/Content/candide/corpus/candide_ch1_segmented_small.json'
        AudioMetadataFile = '$LARA/Content/candide/audio/litteratureaudio/metadata_help.json'
        AudioMetadataStatus = 'already_exists'
        align_rec_results_to_text(RecResultsFile, PairsFile, BeamWidth, StartPage, AlignedFile, SegmentedTextFile, AudioMetadataFile, AudioMetadataStatus)
    elif Id == 'candide_rec_align_ch1':
        RecResultsFile = '$LARA/Content/candide/audio/litteratureaudio/recognition_results_ch1_separate.json'
        PairsFile = '$LARA/Content/candide/corpus/candide_word_pairs.json'
        BeamWidth = 20
        StartPage = 1
        AlignedFile = '$LARA/Content/candide/corpus/candide_ch1_aligned.json'
        SegmentedTextFile = '$LARA/Content/candide/corpus/candide_ch1_segmented.json'
        AudioMetadataFile = '$LARA/Content/candide/audio/litteratureaudio/metadata_help.json'
        AudioMetadataStatus = 'already_exists'
        align_rec_results_to_text(RecResultsFile, PairsFile, BeamWidth, StartPage, AlignedFile, SegmentedTextFile, AudioMetadataFile, AudioMetadataStatus)
    elif Id == 'candide_rec_align_ch1_and_2':
        RecResultsFiles = [ '$LARA/Content/candide/audio/litteratureaudio/recognition_results_ch1_separate_fixed.json',
                            '$LARA/Content/candide/audio/litteratureaudio/recognition_results_ch2_separate_fixed.json' ]
        PairsFile = '$LARA/Content/candide/corpus/candide_word_pairs.json'
        BeamWidth = 40
        StartPage = 1
        AlignedFile = '$LARA/Content/candide/corpus/candide_ch1_and_2_aligned.json'
        SegmentedTextFile = '$LARA/Content/candide/corpus/candide_ch1_and_2_segmented.json'
        AudioMetadataFile = '$LARA/Content/candide/audio/litteratureaudio/metadata_help.json'
        AudioMetadataStatus = 'already_exists'
        align_rec_results_to_text(RecResultsFiles, PairsFile, BeamWidth, StartPage, AlignedFile, SegmentedTextFile, AudioMetadataFile, AudioMetadataStatus)
    elif Id == 'combray_overture_word_pair_corpus':
        ConfigFile = '$LARA/Content/combray/corpus/local_config_segmented_by_audio.json'
        WordTripleFile = '$LARA/Content/combray/corpus/combray_overture_word_pairs.json'
        create_word_pair_corpus(ConfigFile, WordTripleFile)
    elif Id == 'combray_overture_rec_align':
        #RecResultsFiles = [ '$LARA/Content/combray/audio/MoniqueVincens/recognition_results_overture.json' ]
        RecResultsFiles = [ '$LARA/Content/combray/audio/MoniqueVincens_overture/recognition_results_overture_fixed.json' ]
        PairsFile = '$LARA/Content/combray/corpus/combray_overture_word_pairs.json'
        BeamWidth = 40
        StartPage = 1
        AlignedFile = '$LARA/Content/combray/corpus/combray_overture_aligned.json'
        SegmentedTextFile = '$LARA/Content/combray/corpus/combray_overture_segmented_from_aligner.json'
        AudioMetadataFile = '$LARA/Content/combray/audio/MoniqueVincens_overture/metadata_help.json'
        AudioMetadataStatus = 'already_exists'
        align_rec_results_to_text(RecResultsFiles, PairsFile, BeamWidth, StartPage, AlignedFile, SegmentedTextFile, AudioMetadataFile, AudioMetadataStatus)
    elif Id == 'combray_full_word_pair_corpus':
        ConfigFile = '$LARA/Content/combray/corpus/local_config_tts.json'
        WordTripleFile = '$LARA/Content/combray/corpus/combray_full_word_pairs.json'
        create_word_pair_corpus(ConfigFile, WordTripleFile)
    elif Id == 'combray_ch1_rec_align':
        RecResultsFiles = [ '$LARA/Content/combray/audio/MoniqueVincens_full/recognition_results_ch1_all.json' ]
        PairsFile = '$LARA/Content/combray/corpus/combray_full_word_pairs.json'
        BeamWidth = 40
        StartPage = 1
        AlignedFile = '$LARA/Content/combray/corpus/combray_ch1_aligned.json'
        SegmentedTextFile = '$LARA/Content/combray/corpus/combray_ch1_segmented_from_aligner.txt'
        AudioMetadataFile = '$LARA/Content/combray/audio/MoniqueVincens_full/metadata_help.json'
        AudioMetadataStatus = 'create'
        align_rec_results_to_text(RecResultsFiles, PairsFile, BeamWidth, StartPage, AlignedFile, SegmentedTextFile, AudioMetadataFile, AudioMetadataStatus)
    elif Id == 'recueillement_tmp_word_pair_corpus':
        ConfigFile = '$LARA/Content/recueillement/corpus/local_config.json'
        WordTripleFile = '$LARA/Content/recueillement_tmp/corpus/recueillement_word_pairs.json'
        create_word_pair_corpus(ConfigFile, WordTripleFile)
    elif Id == 'recueillement_tmp_align':
        RecResultsFiles = [ '$LARA/Content/recueillement_tmp/audio/litteratureaudio/recognition_results.json' ]
        PairsFile = '$LARA/Content/recueillement_tmp/corpus/recueillement_word_pairs.json'
        BeamWidth = 20
        StartPage = 1
        AlignedFile = '$LARA/Content/recueillement_tmp/corpus/recueillement_aligned.json'
        SegmentedTextFile = '$LARA/Content/recueillement_tmp/corpus/recueillement_segmented_from_aligner.txt'
        AudioMetadataFile = '$LARA/Content/recueillement_tmp/audio/litteratureaudio/metadata_help.json'
        AudioMetadataStatus = 'create'
        align_rec_results_to_text(RecResultsFiles, PairsFile, BeamWidth, StartPage, AlignedFile, SegmentedTextFile, AudioMetadataFile, AudioMetadataStatus)
    elif Id == 'recueillement_tmp_align_config_part1':
        ConfigFile = '$LARA/Content/recueillement_tmp/corpus/local_config.json'
        RangeSpec = 'part1'
        EvaluateOrCreate = 'create'
        align_rec_results_to_text_from_config(ConfigFile, RangeSpec, EvaluateOrCreate)
    elif Id == 'recueillement_tmp_align_config_part1_evaluate':
        ConfigFile = '$LARA/Content/recueillement_tmp/corpus/local_config.json'
        RangeSpec = 'part1'
        EvaluateOrCreate = 'evaluate'
        align_rec_results_to_text_from_config(ConfigFile, RangeSpec, EvaluateOrCreate)
    elif Id == 'recueillement_tmp_align_config_part2':
        ConfigFile = '$LARA/Content/recueillement_tmp/corpus/local_config.json'
        RangeSpec = 'part2'
        EvaluateOrCreate = 'create'
        align_rec_results_to_text_from_config(ConfigFile, RangeSpec, EvaluateOrCreate)
    elif Id == 'cautionary_tales_align':
        ConfigFile = '$LARA/Content/cautionary_tales_for_children/corpus/local_config.json'
        RangeSpec = 'default'
        EvaluateOrCreate = 'create'
        align_rec_results_to_text_from_config(ConfigFile, RangeSpec, EvaluateOrCreate)
    elif Id == 'cautionary_tales_update_from_align':
        ConfigFile = '$LARA/Content/cautionary_tales_for_children/corpus/local_config.json'
        RangeSpec = 'default'
        EvaluateOrCreate = 'create'
        update_segmented_text_and_metadata_from_aligned_file(ConfigFile, RangeSpec)
    elif Id == 'combray_display':
        ConfigFile = '$LARA/Content/combray/corpus/local_config_segmented_by_audio.json'
        AlignedFile = '$LARA/Content/combray/corpus/combray_aligned.json'
        DisplayDir = '$LARA/Content/combray/corpus/segments_not_ending_in_punctuation'
        find_segments_not_ending_in_punctuation(ConfigFile, AlignedFile, DisplayDir)
    elif Id == 'combray_2458':
        RecResultsFile = '$LARA/Content/combray/audio/MoniqueVincens_double_align_ch2/recognition_results_2458.json'
        TextFile = '$LARA/Content/combray/corpus/combray_ch2_2458.txt'
        BeamWidth = 80
        AlignedFile = '$LARA/Content/combray/corpus/combray_aligned_2458.json'
        MatchFunction = 'ngram'
        SegmentedTextFile = '$LARA/Content/combray/corpus/combray_segmented_2458.txt'
        AudioMetadataFile = '$LARA/Content/combray/corpus/metadata_help_2458.txt'
        CreateOrEvaluate = 'create' 
        align_rec_results_to_text(RecResultsFile, TextFile, BeamWidth, AlignedFile, MatchFunction, SegmentedTextFile, AudioMetadataFile, CreateOrEvaluate)
    elif Id == 'combray_2458_reduced':
        RecResultsFile = '$LARA/Content/combray/audio/MoniqueVincens_double_align_ch2/recognition_results_2458_reduced.json'
        TextFile = '$LARA/Content/combray/corpus/combray_ch2_2458_reduced.txt'
        BeamWidth = 80
        AlignedFile = '$LARA/Content/combray/corpus/combray_aligned_2458_reduced.json'
        MatchFunction = 'ngram'
        SegmentedTextFile = '$LARA/Content/combray/corpus/combray_segmented_2458_reduced.txt'
        AudioMetadataFile = '$LARA/Content/combray/corpus/metadata_help_2458_reduced.txt'
        CreateOrEvaluate = 'create' 
        align_rec_results_to_text(RecResultsFile, TextFile, BeamWidth, AlignedFile, MatchFunction, SegmentedTextFile, AudioMetadataFile, CreateOrEvaluate)
    else:
        lara_utils.print_and_flush(f'*** Error: unknown ID {Id}')
        return

def create_aligned_files_from_config_file(ConfigFile, AudioId):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if Params == False or not params_defined_for_create_aligned_files(Params):
        return
    if Params.labelled_source_corpus == '':
        lara_utils.print_and_flush(f'*** Error: "labelled_corpus_source" not defined in config file')
        return
    else:
        SourceTextFile = Params.labelled_source_corpus
    TargetTextFile =  TargetTextFile = False if Params.labelled_target_corpus == '' else Params.labelled_target_corpus
    AudioInfo = get_audio_cutting_up_parameters(Params, AudioId)
    if AudioInfo == False:
        return
    ( AudioFile, AudioLabelsFile, StartLabel, EndLabel) = AudioInfo
    create_aligned_files(AudioFile, AudioId, AudioLabelsFile, SourceTextFile, TargetTextFile, ConfigFile, StartLabel, EndLabel)

def cut_up_audio_without_text_from_config_file(ConfigFile, AudioId):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if Params == False or not params_defined_for_cut_up_audio_without_text(Params):
        return
    AudioInfo = get_audio_cutting_up_parameters(Params, AudioId)
    if AudioInfo == False:
        return
    ( AudioFile, AudioLabelsFile, StartLabel, EndLabel) = AudioInfo
    cut_up_audio_without_text(AudioFile, AudioId, AudioLabelsFile, ConfigFile, StartLabel, EndLabel)

def get_audio_cutting_up_parameters(Params, AudioId):
    CuttingUpParameters = Params.audio_cutting_up_parameters
    if CuttingUpParameters == '':
        lara_utils.print_and_flush(f'*** Error: "audio_cutting_up_parameters" not defined in config file')
        return False
    if not valid_audio_cutting_up_parameters(CuttingUpParameters):
        lara_utils.print_and_flush(f'*** Error: "audio_cutting_up_parameters" is not a list of valid dicts')
        return False
    if AudioId == '' and len(CuttingUpParameters) == 1:
        TheseCuttingUpParameters = CuttingUpParameters[0]
    else:
        RelevantCuttingUpParameters = [ Item for Item in CuttingUpParameters if 'id' in Item and Item['id'] == AudioId ]
        if len(RelevantCuttingUpParameters) == 0:
            lara_utils.print_and_flush(f'*** Error: "id" = "{AudioId}" not defined in audio_cutting_up_parameters')
            return False
        elif len(RelevantCuttingUpParameters) > 1:
            lara_utils.print_and_flush(f'*** Error: "id" = "{AudioId}" multiply defined in audio_cutting_up_parameters')
        else:
            TheseCuttingUpParameters = RelevantCuttingUpParameters[0]
    if not 'start_label' in TheseCuttingUpParameters or not 'end_label' in TheseCuttingUpParameters:
        Result = get_start_and_end_labels_from_audio_labels_file(TheseCuttingUpParameters['audio_labels_file'])
        if Result == False:
            return False
        ( TheseCuttingUpParameters['start_label'], TheseCuttingUpParameters['end_label'] ) = Result
    return ( TheseCuttingUpParameters['audio_file'], TheseCuttingUpParameters['audio_labels_file'],
             TheseCuttingUpParameters['start_label'], TheseCuttingUpParameters['end_label'] )

def get_start_and_end_labels_from_audio_labels_file(AudioLabelsFile):
    AudioLabelsAndTimings = get_audio_labels_and_timings(AudioLabelsFile)
    if AudioLabelsAndTimings == False:
        return False
    return ( AudioLabelsAndTimings[0][0], AudioLabelsAndTimings[-1][0] )

def valid_audio_cutting_up_parameters(CuttingUpParameters):
    if not isinstance(CuttingUpParameters, ( list, tuple )):
        lara_utils.print_and_flush(f'*** Error: "audio_cutting_up_parameters" is not a list')
        return False
    for Item in CuttingUpParameters:
        if not isinstance(Item, ( dict )) or not 'audio_file' in Item or not 'audio_labels_file' in Item:
            lara_utils.print_and_flush(f'*** Error: bad item {Item} in audio_cutting_up_parameters')
            return False
        if not lara_utils.file_exists(Item['audio_file']):
            lara_utils.print_and_flush(f"*** Error: unable to find {Item['audio_file']}")
            return False
        if not lara_utils.file_exists(Item['audio_labels_file']):
            lara_utils.print_and_flush(f"*** Error: unable to find {Item['audio_labels_file']}")
            return False
    return True

def cut_up_audio_without_text(AudioFile, AudioId, AudioLabelsFile, ConfigFile, StartLabel, EndLabel):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if not params_defined_for_cut_up_audio_without_text(Params):
        return
    # We won't have meaningful transcriptions here, so contexts make no sense
    Params.segment_audio_keep_duplicates = 'no'
    AudioLabelsAndTimings = get_audio_labels_and_timings(AudioLabelsFile)
    AudioLabels = [ Item[0] for Item in AudioLabelsAndTimings ]
    SourceLabelsAndTexts = [ [ AudioLabels[I], f'*no_text* {AudioId} {I}' ] for I in range(0, len(AudioLabels)) ]
    AlignedLabels = get_aligned_labels({'audio labels': AudioLabels,
                                        'source labels': AudioLabels},
                                       StartLabel, EndLabel)
    create_segment_audio(AlignedLabels, AudioLabelsAndTimings, SourceLabelsAndTexts, AudioFile, AudioId, Params)
    return

def create_aligned_files(AudioFile, AudioId, AudioLabelsFile, SourceTextFile, TargetTextFile, ConfigFile, StartLabel, EndLabel):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if not params_defined_for_create_aligned_files(Params):
        return
    AudioLabelsAndTimings = get_audio_labels_and_timings(AudioLabelsFile)
    SourceLabelsAndTexts = get_text_labels_and_texts(SourceTextFile)
    TargetLabelsAndTexts = get_text_labels_and_texts(TargetTextFile)
    AudioLabels = [ Item[0] for Item in AudioLabelsAndTimings ]
    SourceLabels = [ Item[0] for Item in SourceLabelsAndTexts ] 
    TargetLabels = [ Item[0] for Item in TargetLabelsAndTexts ] if TargetLabelsAndTexts != False else False
    AlignedLabels = get_aligned_labels({'audio labels': AudioLabels,
                                        'source labels': SourceLabels,
                                        'target labels': TargetLabels},
                                       StartLabel, EndLabel)
    create_segmented_corpus(AlignedLabels, SourceLabelsAndTexts, Params)
    create_segment_translations(AlignedLabels, SourceLabelsAndTexts, TargetLabelsAndTexts, Params)
    create_segment_audio(AlignedLabels, AudioLabelsAndTimings, SourceLabelsAndTexts, AudioFile, AudioId, Params)
    return

# Check that all needed params are there
def params_defined_for_cut_up_audio_without_text(Params):
    if Params.segment_audio_directory != '':
        return True
    else:
        lara_utils.print_and_flush(f'*** Error: config file must define "segment_audio_directory"')
        return False

def params_defined_for_create_aligned_files(Params):
    if Params.untagged_corpus != '' and Params.segment_audio_directory != '' and Params.segment_translation_spreadsheet != '':
        return True
    else:
        lara_utils.print_and_flush(f'*** Error: config file must define "untagged_corpus", "segment_audio_directory" and "segment_translation_spreadsheet"')
        return False

# Extract from Audacity labels file
# Input format is list of lines like
#
# 11.588591	11.588591	1
#
# Output format is list of elements like
#
# [ 1, 1.588591 ]
def get_audio_labels_and_timings(AudioLabelsFile):
    Lines = lara_utils.read_lara_text_file(AudioLabelsFile).split('\n')
    if Lines == False:
        lara_utils.print_and_flush(f'*** Error: unable to read "AudioLabelsFile"')
        return []
    if audio_labels_look_like_numbers(Lines):
        lara_utils.print_and_flush(f'--- Audio labels look like numbers, using them')
        return [ [ convert_to_int_if_not_corrupted(Line.split()[2]), float(Line.split()[1]) ] for Line in Lines if len(Line.split()) == 3 ]
    else:
        lara_utils.print_and_flush(f'--- Audio labels do not look like numbers, converting to 1, 2, 3...')
        Times = [ float(Line.split()[1]) for Line in Lines if len(Line.split()) in ( 2, 3 ) ]
        # Normalise labels to 1,2,3...
        return [ [ Index + 1, Times[Index] ] for Index in range(0, len(Times)) ]

def convert_to_int_if_not_corrupted(Str):
    return Str if Str == "corrupted" else int(Str)

def audio_labels_look_like_numbers(Lines):
    for Line in Lines:
        Components = Line.split()
        if len(Components) != 3 and len(Components) != 0:
            lara_utils.print_and_flush(f'--- Audio labels line does not have 3 components: "{Line}"')
            return False
        elif len(Components) == 3:
            Label = Components[2]
            LabelAsNumber = lara_utils.safe_string_to_int(Label)
            if LabelAsNumber == False and not Label in ( "0", "corrupted" ):
                lara_utils.print_and_flush(f'--- Audio label "{Label}" in "{Line}" does not look like a number')
                return False
    return True

# Extract from labelled text file.
# Input format looks like
#
#(musique)|1|
#Marcel Proust |2|
#A la recherche du temps perdu |3|
#Du côté de chez Swann |4|
#PREMIÈRE PARTIE
#COMBRAY |5|
#
# Output format is list of elements like
# [ 1, '(musique)' ]
def get_text_labels_and_texts(TextFile):
    if TextFile == False:
        return False
    Text = lara_utils.read_lara_text_file(TextFile)
    return False if Text == False else get_text_labels_and_texts_from_string(Text)

def get_text_labels_and_texts_from_string(Str):
    (Index, Out ) = ( 0, [] )
    while True:
        #lara_utils.print_and_flush(f'--- Searching at string position {Index}')
        if Str[Index:].find('|') == -1:
            return Out
        Match = re.search("([^\|]*)\|([0-9]+)\|", Str[Index:])
        if Match == None:
            return Out
        Text = Match.group(1)
        Label = int(Match.group(2))
        Out += [ [ Label, Text ] ]
        Index += Match.end()

# Get the maximal initial set of aligned labels and print trace info if there is a mismatch
# Input is dict where keys are names of files and values are lists of labels
# Output is list of labels
def get_aligned_labels(LabelsDict0, StartLabel, EndLabel):
    LabelsDict = extract_relevant_sequences_in_labels_dict(LabelsDict0, StartLabel, EndLabel)
    if LabelsDict == False:
        return []
    AlignedLabels = []
    Keys = [ Key for Key in LabelsDict ]
    N = min([ len(LabelsDict[Key]) for Key in LabelsDict if isinstance(LabelsDict[Key], ( list )) ])
    for I in range(0, N):
        Labels = [ LabelsDict[Key][I] for Key in Keys ]
        if len(lara_utils.remove_duplicates(Labels)) == 1:
           AlignedLabels += [  Labels[0] ]
        else:
            KeysAndLabels = { Key: LabelsDict[Key][I] for Key in Keys }
            lara_utils.print_and_flush(f'*** Error: label mismatch at position {I}: {KeysAndLabels}')
            return []
    lara_utils.print_and_flush(f'--- Found {len(AlignedLabels)} aligned labels')
    return AlignedLabels

def extract_relevant_sequences_in_labels_dict(LabelsDict, StartLabel, EndLabel):
    LabelsDict1 = {}
    for Key in LabelsDict:
        LabelSequence =  LabelsDict[Key]
        if LabelSequence == False:
            continue
        elif not StartLabel in LabelSequence:
            lara_utils.print_and_flush(f'*** Error: start label "{StartLabel}" not found in "{Key}" labels')
            return False
        elif not EndLabel in LabelSequence:
            lara_utils.print_and_flush(f'*** Error: end label "{EndLabel}" not found in "{Key}" labels')
            return False
        elif LabelSequence.index(EndLabel) < LabelSequence.index(StartLabel):
            lara_utils.print_and_flush(f'*** Error: end label "{EndLabel}" is before start label "{StartLabel}" in "{Key}" labels')
            return False
        else:
            LabelSequence1 = LabelSequence[LabelSequence.index(StartLabel):LabelSequence.index(EndLabel)+1]
            LabelsDict1[Key] = LabelSequence1
    return LabelsDict1       

# Create a segmented corpus that can be used as input to tagging
def create_segmented_corpus(AlignedLabels, SourceLabelsAndTexts, Params):
    TextPieces = [ Item[1] for Item in SourceLabelsAndTexts if Item[0] in AlignedLabels ]
    Text = '||'.join(TextPieces)
    File = Params.untagged_raw_corpus if Params.untagged_raw_corpus != '' else Params.untagged_corpus
    lara_utils.write_lara_text_file(Text, File)
    lara_utils.print_and_flush(f'--- Written segmented corpus ({len(TextPieces)} segments), {File}')

# Create a segment translation CSV
def create_segment_translations(AlignedLabels, SourceLabelsAndTexts, TargetLabelsAndTexts, Params):
    if TargetLabelsAndTexts == False:
        lara_utils.print_and_flush(f'--- Not creating translation spreadsheet')
        return
    SourceTextPieces = [ Item[1] for Item in SourceLabelsAndTexts if Item[0] in AlignedLabels ]
    TargetTextPieces = [ Item[1] for Item in TargetLabelsAndTexts if Item[0] in AlignedLabels ]
    SourceTextPieces1 = [ internalise_source_string(TextPiece, Params) for TextPiece in SourceTextPieces ]
    TargetTextPieces1 = [ internalise_target_string(TextPiece, Params) for TextPiece in TargetTextPieces ]
    Lines = list(zip(SourceTextPieces1, TargetTextPieces1))
    Header = [ 'Source', 'Target' ]
    File = Params.segment_translation_spreadsheet
    lara_utils.write_lara_csv([ Header ] + Lines, File)
    lara_utils.print_and_flush(f'--- Written translation spreadsheet ({len(Lines)} lines), {File}')

def internalise_source_string(Str, Params):
    return lara_split_and_clean.minimal_clean_lara_string(Str, Params)[0]

def internalise_target_string(Str, Params):
    CleanedStr = lara_split_and_clean.minimal_clean_lara_string(Str, Params)[0]
    return lara_translations.internalise_text_from_segment_spreadsheet(CleanedStr)

# Create a segment audio file, including metadata
# Code needs to work even if we've been careless and repeated a label
def create_segment_audio(AlignedLabels, AudioLabelsAndTimings, SourceLabelsAndTexts, AudioFile, AudioId, Params):
    AudioDir = Params.segment_audio_directory
    lara_utils.create_directory_if_it_doesnt_exist(AudioDir)
    AudioLabelsAndTimings1 = [ ( Label, Time ) for ( Label, Time ) in AudioLabelsAndTimings if Label in AlignedLabels ]
    Texts1 = [ ( Label, internalise_source_string(Text, Params) ) for ( Label, Text ) in SourceLabelsAndTexts if Label in AlignedLabels ]
    # Start with first label. 
    ( CurrentTime, Metadata ) = ( AudioLabelsAndTimings1[0][1], [] )
    Indices = range(1, min([len(AudioLabelsAndTimings1), len(Texts1)]))
    for I in Indices:
        ( NextLabel, NextTime ) = AudioLabelsAndTimings1[I]
        ( NextLabel1, Text ) = Texts1[I]
        AudioId1 = AudioId if AudioId != '' else 'default'
        BaseFileName = f'extracted_file_{AudioId1}_{NextLabel}.mp3'
        Result = extract_audio_file_from_mp3(AudioFile, BaseFileName, CurrentTime, NextTime, Text, AudioDir, Params)
        if BaseFileName != False:
            Metadata += [ { 'text': Text, 'file': BaseFileName } ]
        CurrentTime = NextTime
    lara_utils.print_and_flush(f'--- Align: Params.segment_audio_keep_duplicates = {Params.segment_audio_keep_duplicates}')
    MetadataWithContexts = lara_audio.maybe_add_contexts_to_metadata(Metadata, 'segments', Params)
    write_or_update_metadata_file(MetadataWithContexts, AudioId, AudioDir)
    lara_utils.print_and_flush(f'--- Updated segment audio dir ({len(MetadataWithContexts)} files), {AudioDir}')

def extract_audio_file_from_mp3(AudioFile, BaseExtractedFile, FromTime, ToTime, Text, AudioDir, Params):
    ExtractedFile = f'{AudioDir}/{BaseExtractedFile}'
    AbsExtractedFile = lara_utils.absolute_file_name(ExtractedFile)
    AbsAudioFile = lara_utils.absolute_file_name(AudioFile)
    Command = f'ffmpeg -i {AbsAudioFile} -ss {FromTime:.2f} -to {ToTime:.2f} -c copy {AbsExtractedFile}'
    lara_utils.print_and_flush(f'--- Extracting audio from {FromTime:.2f}s to {ToTime:.2f}s ({BaseExtractedFile}; "{Text}")')
    Result = execute_ffmpeg_command(Command, AbsExtractedFile, Params)
    if Result:
        return True
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

def write_or_update_metadata_file(Metadata, AudioId, AudioDir):
    OldMetadata0 = lara_audio.read_ldt_metadata_file(AudioDir)
    if AudioId != False:
        OldMetadata = remove_extracted_audio_metadata_for_audio_id(OldMetadata0, AudioId)
    else:
        OldMetadata = OldMetadata0
    UpdatedMetadata = lara_install_audio_zipfile.clean_audio_metadata(OldMetadata + Metadata)
    lara_audio.write_ldt_metadata_file(UpdatedMetadata, AudioDir)
    lara_utils.print_and_flush(f'--- Updated metadata file in {AudioDir} with metadata for extracted audio')

def remove_extracted_audio_metadata_for_audio_id(Metadata, AudioId):
    Metadata1 = [ Item for Item in Metadata if not is_extracted_audio_metadata_for_audio_id(Item, AudioId) ]
    NItemsDeleted = len(Metadata) - len(Metadata1)
    lara_utils.print_and_flush(f'--- Removed {NItemsDeleted} old metadata items for {AudioId}')
    return Metadata1

def is_extracted_audio_metadata_for_audio_id(Item, AudioId):
    return isinstance(Item, dict) and 'file' in Item and (Item['file']).startswith(f'extracted_file_{AudioId}')

# ------------------------------------------

_dp_trace_level = 1
#_dp_trace_level = 0

_evaluate_or_create_values = ( 'evaluate', 'create' )

def align_rec_results_to_text_from_config(ConfigFile, Id, MatchFunction, CreateOrEvaluate):
    if not MatchFunction in _match_function_ids:
        lara_utils.print_and_flush(f'*** Error: unknown match function: "{MatchFunction}". Possible values are "{_match_function_ids}"')
        return 
    if not CreateOrEvaluate in _evaluate_or_create_values:
        lara_utils.print_and_flush(f'*** Error: bad value for CreateOrEvaluate "{CreateOrEvaluate}": needs to be in {_evaluate_or_create_values}')
        return
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if not check_params_for_align_rec_results(Params):
        return
    BeamWidth = Params.audio_alignment_beam_width
    RecResults = get_ordered_segment_audio_rec_results_from_params_and_spec(Params, Id)
    if RecResults == False:
        lara_utils.print_and_flush(f'*** Error: unable to get rec results')
        return
    if len(RecResults) == 0:
        return
    Pairs = get_word_pairs_from_params_and_spec(Params, Id)
    if Pairs == False:
        lara_utils.print_and_flush(f'*** Error: unable to get word pairs')
        return
    lara_utils.print_and_flush(f'--- Performing alignment')
    FilesAndAlignedTextList = align_rec_results_to_pairs(RecResults, BeamWidth, MatchFunction, Pairs, Params)
    if FilesAndAlignedTextList == False:
        return
    adjust_files_and_aligned_text_list(FilesAndAlignedTextList, Params)
    if CreateOrEvaluate == 'evaluate' and Params.aligned_segments_file_evaluate != '':
        AlignedFile = Params.aligned_segments_file_evaluate
    else:
        AlignedFile = Params.aligned_segments_file
    AlignedItemsList = update_aligned_file_from_aligned_list(RecResults, FilesAndAlignedTextList, Id, CreateOrEvaluate, AlignedFile, Params)
    if CreateOrEvaluate == 'create':
        update_segmented_text_and_metadata_from_aligned_list(FilesAndAlignedTextList, Id, Params)
        lara_align_adjust.correct_segment_translations_for_double_aligned_from_params(Id, Params)
    summarise_segments_and_words(RecResults, Pairs)
    summarise_audio_time(RecResults)
    if CreateOrEvaluate == 'evaluate':
        summarise_errors_in_terms_of_edit_distance(AlignedItemsList)

def update_segmented_text_and_metadata_from_aligned_file(ConfigFile, Id):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if not check_params_for_align_rec_results(Params):
        return
    FilesAndAlignedTextList = get_aligned_list_from_aligned_file(Id, Params)
    if FilesAndAlignedTextList == False:
        return
    update_segmented_text_and_metadata_from_aligned_list(FilesAndAlignedTextList, Id, Params)       

def update_segmented_text_and_metadata_from_aligned_list(FilesAndAlignedTextList, Id, Params):
    NewText = files_and_aligned_text_list_to_segmented_text(FilesAndAlignedTextList)
    NewMetadata = files_and_aligned_text_list_to_audio_metadata(FilesAndAlignedTextList)
    if not insert_text_for_spec_into_untagged_corpus(NewText, Id, Params):
        return
    insert_metadata_from_alignment_into_segment_audio_dir(NewMetadata, Params)
    
def check_params_for_align_rec_results(Params):
    if Params.untagged_corpus == '':
        lara_utils.print_and_flush(f'*** Error: untagged_corpus not defined in config file')
        return False
    if Params.segment_audio_directory == '':
        lara_utils.print_and_flush(f'*** Error: segment_audio_directory not defined in config file')
        return False
    if Params.audio_alignment_corpus == '':
        lara_utils.print_and_flush(f'*** Error: audio_alignment_corpus not defined in config file')
        return False
    if Params.audio_cutting_up_parameters == None:
        lara_utils.print_and_flush(f'*** Error: audio_cutting_up_parameters not defined in config file')
        return False
    if Params.aligned_segments_file == '':
        lara_utils.print_and_flush(f'*** Error: aligned_segments_file not defined in config file')
        return False
    #if not check_audio_alignment_corpus_compatible_with_cutting_up_params(Params):
    #    return False
    return True

def align_rec_results_to_text(RecResultsFile, TextFile, BeamWidth, AlignedFile, MatchFunction, SegmentedTextFile, AudioMetadataFile, CreateOrEvaluate):
    if not CreateOrEvaluate in ( 'create', 'evaluate' ):
        lara_utils.print_and_flush(f'*** Error: bad value for CreateOrEvaluate "{CreateOrEvaluate}": needs to "create" or "evaluate"')
        return
    Params = lara_config.default_params()
    Id = 'all'
    RecResults = lara_utils.read_json_file(RecResultsFile)
    if RecResults == False: return
    Text = lara_utils.read_lara_text_file(TextFile)
    if Text == False: return
    Text1 = normalise_text_for_adjusting_aligned_text(Text)
    ( Pairs, Errors ) = lara_split_and_clean.string_to_annotated_words(Text1)
    if Errors != []:
        return False
    Pairs = pairs_to_pairs_for_word_list_corpus(Pairs, Params)
    FilesAndAlignedTextList = align_rec_results_to_pairs(RecResults, BeamWidth, MatchFunction, Pairs, Params)
    if FilesAndAlignedTextList == False: return
    adjust_files_and_aligned_text_list(FilesAndAlignedTextList)
    if CreateOrEvaluate == 'create':
        files_and_aligned_text_list_to_audio_metadata_file(FilesAndAlignedTextList, AudioMetadataFile)
    AlignedItemsList = update_aligned_file_from_aligned_list(RecResults, FilesAndAlignedTextList, Id, CreateOrEvaluate, AlignedFile, Params)
##    if CreateOrEvaluate == 'create':
##        update_segmented_text_and_metadata_from_aligned_list(FilesAndAlignedTextList, Id, Params)
##    summarise_segments_and_words(RecResults, Pairs)
##    summarise_audio_time(RecResults)
##    if CreateOrEvaluate == 'evaluate':
##        summarise_errors_in_terms_of_edit_distance(AlignedItemsList)
        
def summarise_segments_and_words(RecResults, Pairs):
    SuccessfulRecResults = [ RecResult for RecResult in RecResults
                             if 'result' in RecResult and 'transcript' in RecResult['result'] and RecResult['result']['transcript'] != False ]
    NSegments = len(SuccessfulRecResults)
    NRecWords = sum([ len(RecResult['result']['transcript'].split()) for RecResult in SuccessfulRecResults ])
    NTextWords = len([ Pair for Pair in Pairs if Pair[0] != '' ])
    WordsPerSegment = NRecWords / NSegments
    lara_utils.print_and_flush(f'--- {NSegments} segments, {NRecWords} recognised words, {NTextWords} text words ({WordsPerSegment:.1f} recognised words/segment)')

def summarise_errors_in_terms_of_edit_distance(AlignedItemsList0):
    AlignedItemsList = [ Item for Item in AlignedItemsList0 if 'text_aligned_reference' in Item and 'edit_distance' in Item ]
    if len(AlignedItemsList) == 0:
        return
    TotalChars = sum([ len(Item['text_aligned_reference']) for Item in AlignedItemsList ])
    TotalEditDistance = sum([ Item['edit_distance'] for Item in AlignedItemsList ])
    Percent = 100.0 * TotalEditDistance / TotalChars
    lara_utils.print_and_flush(f'--- {TotalEditDistance} char errors from {TotalChars} chars ({Percent:.2f}%)')

def summarise_audio_time(RecResults):
    NFiles = len(RecResults)
    TotalTimeInMinutes = sum([ lara_utils.length_of_mp3(RecResult['file']) for RecResult in RecResults ]) / 60.0
    lara_utils.print_and_flush(f'--- Total audio time = {TotalTimeInMinutes:.1f} minutes from {NFiles} files')

##    [
##        {
##            "corpus": "local_files",
##            "page": 1
##        },
##        [
##            [
##                "",
##                "\n<h1> "
##            ],
##            [
##                "voltaire",
##                "Voltaire"
##            ],
##            [
##                "",
##                ":  "
##            ],
##            [
##                "candide",
##                "Candide"
##            ],
##            [
##                "",
##                "</h1>\n"
##            ]
##        ]
##    ],

def get_pairs_from_pairs_pages(PagesWithPairs, StartPage):
    RelevantPages = [ Page for Page in PagesWithPairs if Page[0]['page'] >= StartPage ]
    return [ Pair for Page in RelevantPages for Pair in Page[1] ]



# ------------------------------------------------------------

_savedDPDict = {}

def align_rec_results_to_pairs(RecResults, BeamWidth, MatchFunction, Pairs, Params):
    global _savedDPDict
    StartTime = time.time()
    ( LastPairsIndex, StartingRange, TotalRecWordsAligned, CurrentBestMatch, CurrentBestScore, DPDict, Epoch ) = ( len(Pairs) - 1, [0, 0], 0, [], 0, {}, 0 )
    DPDict[(0, 0)] = ( 0, [] )
    ( NRecognisedWords, AvWordLength ) = n_recognised_words_and_average_rec_result_word_length_in_seconds(RecResults, Params)
    lara_utils.print_and_flush(f'--- Average length of word = {AvWordLength:.2f} s over {NRecognisedWords} recognised words')
    for RecResult in RecResults:
        AlignResult = align_single_rec_result_to_pairs(RecResult, Pairs, StartingRange, TotalRecWordsAligned,
                                                       DPDict, BeamWidth, MatchFunction, LastPairsIndex, AvWordLength)
        ( NRecWordsAligned, NewBestMatch, EndingRange, NewBestScore ) = AlignResult
        report_change_in_alignment_score(NewBestMatch, NRecWordsAligned, CurrentBestScore, NewBestScore)
        if NewBestMatch == '*error*':
            return False
        elif NewBestMatch != False:
            CurrentBestMatch = NewBestMatch
            StartingRange = EndingRange
            TotalRecWordsAligned += NRecWordsAligned
            CurrentBestScore = NewBestScore
        Epoch += 1
        maybe_clean_up_dp_dict(Epoch, DPDict, StartingRange)
    if StartTime is not None: 
        lara_utils.print_and_flush_with_elapsed_time('--- Finished aligning', StartTime)
    if _dp_trace_level >= 1:
        _savedDPDict = DPDict
    return alignment_from_dp_dict_result(CurrentBestMatch, Pairs)

def maybe_clean_up_dp_dict(Epoch, DPDict, StartingRange):
    if Epoch % 100 != 0:
        return
    CurrentIndex = StartingRange[0]
    IndexCutoff = CurrentIndex - 10000
    Keys = list(DPDict.keys())
    NKeys = len(Keys)
    KeysToDelete = [ Key for Key in Keys
                     if isinstance(Key, ( tuple )) and len(Key) == 2 and isinstance(Key[1], ( int )) and Key[1] < IndexCutoff ]
    NKeysToDelete = len(KeysToDelete)
    for Key in KeysToDelete:
        del DPDict[Key]
    KeysAfterDeletion = list(DPDict.keys())
    NKeysAfterDeletion = len(KeysAfterDeletion)
    lara_utils.print_and_flush(f'--- Cleaned up DP dict: {NKeys} before cleaning, {NKeysAfterDeletion} after')
    time.sleep(2)

def report_change_in_alignment_score(NewBestMatch, NRecWordsAligned, CurrentBestScore, NewBestScore):
    if NewBestMatch == '*error*':
        return
    elif NewBestMatch == False or NRecWordsAligned == 0:
        lara_utils.print_and_flush(f'--- No words aligned')
        return
    else:
        ScorePerRecWord = ( NewBestScore - CurrentBestScore ) / NRecWordsAligned
        lara_utils.print_and_flush(f'--- Score per word ({NRecWordsAligned} words)): {ScorePerRecWord:.2f}')
        if ScorePerRecWord > 0.5:
            lara_utils.print_and_flush(f'*** WARNING: HIGH VALUE')

def align_single_rec_result_to_pairs(RecResult, Pairs, StartingRange, NRecWordsPreviouslyAligned, DPDict, BeamWidth, MatchFunction,
                                     LastPairsIndex, AvWordLength):
    if _dp_trace_level >= 1:
        lara_utils.print_and_flush(f'----------')
    ( RecFile, RecTranscript ) = get_file_and_transcript_from_rec_result(RecResult, AvWordLength)
    if RecTranscript == False:
        if _dp_trace_level >= 1:
            lara_utils.print_and_flush(f'--- Skipping {RecFile} - no rec result')
        ( NRecWords, CurrentBestMatch, EndingRange, BestScore ) = ( 0, False, StartingRange, False )
    else:
        RecWords0 = rec_transcript_to_words(RecTranscript)
        RecWords = RecWords0 + [ f'END_FILE:{RecFile}' ]
        NRecWords = len(RecWords)
        NPairs = len(Pairs)
        ( StartIndexLower, StartIndexUpper ) = StartingRange
        EndIndexUpper = min([ NPairs - 1, count_n_more_content_words_in_pairs_or_end(StartIndexUpper, NRecWords, Pairs) + BeamWidth ])
        NMatchablePairs = EndIndexUpper - StartIndexLower + 1
        if _dp_trace_level >= 1:
            lara_utils.print_and_flush(f'--- Matching {RecFile} - "{"|".join(RecWords)}".')
            lara_utils.print_and_flush(f'--- Rec range: {NRecWordsPreviouslyAligned}-{NRecWordsPreviouslyAligned + NRecWords}.')
            TextInterval = text_interval_from_pairs([StartIndexLower, EndIndexUpper], Pairs)
            lara_utils.print_and_flush(f'--- Txt range: {StartIndexLower}-{EndIndexUpper}. ("{TextInterval}")')
        for TotalIndex in range(0, NRecWords + NMatchablePairs ):
            for IndexRec in range(0, TotalIndex + 1):
                IndexPairs = ( TotalIndex - IndexRec ) + StartIndexLower
                Result = extend(RecWords, Pairs, IndexRec, IndexPairs, NRecWords, NPairs, EndIndexUpper, NRecWordsPreviouslyAligned,
                                MatchFunction, DPDict)
                if Result == False:
                    return ( 0, '*error*', False, False )
        TotalRecWordsAligned = NRecWordsPreviouslyAligned + NRecWords
        PairIndexesAndScores = [ ( PairIndex, DPDict[(TotalRecWordsAligned, PairIndex)][0] )
                                 for PairIndex in range(StartIndexLower, EndIndexUpper + 2)
                                 if (TotalRecWordsAligned, PairIndex) in DPDict ]
        ( BestPairIndex, BestScore ) = sorted(PairIndexesAndScores, key=lambda x: x[1])[0]
        #EndingRange = ( max([ 0, BestPairIndex - BeamWidth ]), min( [ EndIndexUpper, BestPairIndex + BeamWidth ] ) )
        #EndingRange = ( max([ 0, BestPairIndex - int( BeamWidth / 2 ) ]), min( [ EndIndexUpper, BestPairIndex + int( 3 * BeamWidth / 2 ) ] ) )
        EndingRange = ( max([ 0, BestPairIndex - int( BeamWidth / 3 ) ]), min( [ EndIndexUpper, BestPairIndex + int( 5 * BeamWidth / 3 ) ] ) )
        CurrentBestMatch = DPDict[(TotalRecWordsAligned, BestPairIndex)][1]
        if _dp_trace_level >= 2:
            lara_utils.print_and_flush(f'--- Best match so far = {CurrentBestMatch}')
        elif _dp_trace_level >= 1:
            Alignments = alignment_from_dp_dict_result(CurrentBestMatch, Pairs)
            lara_utils.print_and_flush(f'--- Matched. EndingRange = {EndingRange}, Score = {BestScore:.2f}, RecIndex = {TotalRecWordsAligned}, PairsIndex = {BestPairIndex}, latest match = {Alignments[-1]}')
    return ( NRecWords, CurrentBestMatch, EndingRange, BestScore )

##   {
##        "file": "$LARA/Content/candide/audio/litteratureaudio/extracted_file_ch1_1.mp3",
##        "result": {
##            "confidence": 0.9385558366775513,
##            "transcript": "voltaire Candide",
##            "word_info": [
##                {
##                    "start_end": [ 0.0, 1.3 ],
##                    "word": "voltaire"
##                },
##                {
##                    "start_end": [ 1.3, 2.4 ],
##                    "word": "Candide"
##                }
##            ]
##        }
##    },

def n_recognised_words_and_average_rec_result_word_length_in_seconds(RecResults, Params):
    WordLengths = []
    for RecResult in RecResults:
        if 'result' in RecResult and 'word_info' in RecResult['result']:
            for WordInfoItem in RecResult['result']['word_info']:
                Length = WordInfoItem['start_end'][1] - WordInfoItem['start_end'][0]
                WordLengths += [ Length ]
    ( NWords, TotalTime ) = ( len(WordLengths), sum(WordLengths) )
    if NWords == 0:
        return n_recognised_words_and_average_rec_result_word_length_in_seconds_simple(RecResults, Params)
    lara_utils.print_and_flush(f'--- Found {NWords} words, total length = {TotalTime:.1f} s')
    return ( len(WordLengths), sum(WordLengths) / len(WordLengths) )

##    {
##        "file": "extracted_file_ch1_2.mp3",
##        "result": {
##            "transcript": "an prionsa beag"
##        }
##    },

def n_recognised_words_and_average_rec_result_word_length_in_seconds_simple(RecResults, Params):
    ( NWords, TotalTime ) = ( 0, 0.0 )
    for RecResult in RecResults:
        if 'file' in RecResult and 'result' in RecResult and 'transcript' in RecResult['result']:
            AudioFile = RecResult['file']
            NWords += len(RecResult['result']['transcript'].split())
            TotalTime += lara_utils.length_of_mp3(AudioFile)
    lara_utils.print_and_flush(f'--- Found {NWords} words, total length = {TotalTime:.1f} s')
    return ( NWords, NWords / TotalTime )

_guess_extra_words_cutoff = 5

def get_file_and_transcript_from_rec_result(RecResult, AvWordLength):
    File = RecResult['file']
    LengthInSeconds = lara_utils.length_of_mp3(File)
    RecTranscript = RecResult['result']['transcript']
    if RecTranscript == False:
        return ( File, False )
    if 'word_info' in RecResult['result'] and len(RecResult['result']['word_info']) != 0:
        LastRecWordTime = RecResult['result']['word_info'][-1]['start_end'][1]
    else:
        LastRecWordTime = 0.0
    ExpectedNumberOfUnrecognisedWordsAtEnd = int( ( LengthInSeconds - LastRecWordTime ) / AvWordLength )
    if ExpectedNumberOfUnrecognisedWordsAtEnd >= _guess_extra_words_cutoff:
        lara_utils.print_and_flush(f'--- Hypothesising {ExpectedNumberOfUnrecognisedWordsAtEnd} extra words at end of {File}')
        RecTranscript += ExpectedNumberOfUnrecognisedWordsAtEnd * ' *missing_word*' 
    return ( File, RecTranscript )

# Do it this way rather with a simple split() so that the division is consistent.
##def rec_transcript_to_words(Transcript):
##    ( Pairs, Errors ) = lara_split_and_clean.string_to_annotated_words(Transcript)
##    return [ Word for ( Word, Lemma ) in Pairs if Lemma != '' ]

def rec_transcript_to_words(Transcript):
    return [ Word.lower() for Word in Transcript.split() ]

def text_interval_from_pairs(Interval, Pairs):
    ( From, To ) = Interval
    return '|'.join([ Pairs[Index][1] for Index in range(From, To) if 0 <= Index and Index < len(Pairs) ])

def extend(RecWords, Pairs, IndexRec, IndexPairs, NRecWords, NPairs, EndIndexUpper, NRecWordsPreviouslyAligned, MatchFunction, DPDict):
    if IndexRec > NRecWords - 1 or IndexRec > EndIndexUpper or IndexPairs > NPairs - 1 :
        return True
    ( CurrentRecWord, CurrentPairsWord ) = ( RecWords[IndexRec], Pairs[IndexPairs][0] )
    IndexRecForDict = IndexRec + NRecWordsPreviouslyAligned
    if _dp_trace_level >= 3:
        lara_utils.print_and_flush(f'--- Extending from {(IndexRecForDict, IndexPairs)}')
    CurrentDPDictEntry = lookup_dp_dict(DPDict, IndexRecForDict, IndexPairs)
    if CurrentDPDictEntry == False:
        lara_utils.print_and_flush(f'*** Warning: entry not found in DP Dict: {( IndexRecForDict, IndexPairs )}')
        lara_utils.print_and_flush(f'*** Warning: Rec word: "{CurrentRecWord}", Text word: "{CurrentPairsWord}"')
        return False
    ( CurrentCost, CurrentRecWords ) = CurrentDPDictEntry
    # Pairs word is filler, and at end of file
    if CurrentPairsWord == '' and CurrentRecWord.startswith('END_FILE:'):
        update_dp_dict(DPDict, IndexRecForDict, IndexPairs + 1, CurrentCost, CurrentRecWords )
        File = CurrentRecWord.replace('END_FILE:', '')
        PunctuationBonus = get_segment_final_punctuation_bonus(Pairs, IndexPairs)
        # Skip end of file without cost
        update_dp_dict(DPDict, IndexRecForDict + 1, IndexPairs, CurrentCost, CurrentRecWords + [ ( File, IndexPairs ) ] )
        # Skip end of file and punctuation, and get bonus
        update_dp_dict(DPDict, IndexRecForDict + 1, IndexPairs + 1, CurrentCost - PunctuationBonus, CurrentRecWords + [ ( File, IndexPairs + 1 ) ] )
    # Pairs word is filler, so we skip it without cost
    elif CurrentPairsWord == '':
        update_dp_dict(DPDict, IndexRecForDict, IndexPairs + 1, CurrentCost, CurrentRecWords )
        # Insert: skip a rec word
        update_dp_dict(DPDict, IndexRecForDict + 1, IndexPairs, CurrentCost + 1, CurrentRecWords )
    elif CurrentRecWord.startswith('END_FILE:'):
        File = CurrentRecWord.replace('END_FILE:', '')
        update_dp_dict(DPDict, IndexRecForDict + 1, IndexPairs, CurrentCost, CurrentRecWords + [ ( File, IndexPairs ) ] )
        # Delete: skip a pairs word
        update_dp_dict(DPDict, IndexRecForDict, IndexPairs + 1, CurrentCost + 1, CurrentRecWords )
    # Normal words in both rec results and pairs
    else:
        # Match or substitute; also allow intermediate result for similar words
        MatchCost = match_cost(CurrentRecWord, CurrentPairsWord, MatchFunction)
        #lara_utils.print_and_flush(f'{MatchCost} = match_cost({CurrentRecWord}, {CurrentPairsWord}, {MatchFunction})')
        update_dp_dict(DPDict, IndexRecForDict + 1, IndexPairs + 1, CurrentCost + MatchCost, CurrentRecWords )
        # Insert: skip a rec word
        update_dp_dict(DPDict, IndexRecForDict + 1, IndexPairs, CurrentCost + 1, CurrentRecWords )
        # Delete: skip a pairs word
        update_dp_dict(DPDict, IndexRecForDict, IndexPairs + 1, CurrentCost + 1, CurrentRecWords )
    return True

# Bonus for punctuation mark at end of segment
def get_segment_final_punctuation_bonus(Pairs, Index):
    FinalPair = Pairs[Index]
    if FinalPair[0] != '':
        return 0
    Str = FinalPair[1].strip()
    # No punctuation
    if Str == '':
        return 0
    LastChar = Str[-1]
    if not lara_parse_utils.is_punctuation_char(LastChar):
        return 0
    return segment_final_punctuation_bonus(LastChar)
        
def segment_final_punctuation_bonus(Char):
    # Plausible at end of segment
    if Char in '.!?;:,—»)]':
        return 0.5
    # Implausible at end of segment
    elif Char in '«(':
        return -0.5
    else:
        return 0

_match_function_ids = [ 'binary', 'ngram' ]

def match_cost(RecWord, PairsWord, MatchFunction):
    if not MatchFunction in _match_function_ids:
        lara_utils.print_and_flush(f'*** Error: unknown match function: "{MatchFunction}". Possible values are "{_match_function_ids}"')
        return False
    if MatchFunction == 'binary':
        return match_cost_binary(RecWord, PairsWord)
    elif MatchFunction == 'ngram':
        return match_cost_ngram(RecWord, PairsWord)

def match_cost_binary(RecWord, PairsWord):
    return 0 if RecWord == PairsWord else 1

_cached_ngram_match_costs = {}

def match_cost_ngram(RecWord, PairsWord):
    if RecWord == PairsWord:
        return 0
    Key = tuple([RecWord, PairsWord])
    if Key in _cached_ngram_match_costs:
        return _cached_ngram_match_costs[Key]
    ( RecWordNgrams, PairsWordNGrams ) = ( get_ngrams_from_word(RecWord), get_ngrams_from_word(PairsWord) )
    Score = match_ngrams(RecWordNgrams, PairsWordNGrams)
    _cached_ngram_match_costs[Key] = Score
    return Score

def get_ngrams_from_word(Word):
    return { 'unigrams': { Char: True for Char in Word },
             'bigrams': { Word[I:I+2]: True for I in range(0, len(Word) - 2) },
             'trigrams': { Word[I:I+3]: True for I in range(0, len(Word) - 3) }
             }

_ngram_weights = { 'unigrams': 1,
                   'bigrams': 2,
                   'trigrams': 3
                   }

_total_ngram_weights = sum([ _ngram_weights[I] for I in _ngram_weights ])

def match_ngrams(RecWordNgrams, PairsWordNGrams):
    return 1.0 - 0.5 * ( match_ngrams_asymmetric(RecWordNgrams, PairsWordNGrams) + match_ngrams_asymmetric(PairsWordNGrams, RecWordNgrams) )

def match_ngrams_asymmetric(RecWordNgrams, PairsWordNGrams):
    return sum([ _ngram_weights[Component] * match_ngrams_component(Component, RecWordNgrams, PairsWordNGrams)
                 for Component in ( 'unigrams', 'bigrams', 'trigrams' ) ]) / _total_ngram_weights

def match_ngrams_component(Component, RecWordNgrams, PairsWordNGrams):
    ( RecWordNgrams1, PairsWordNGrams1 ) = ( RecWordNgrams[Component], PairsWordNGrams[Component] )
    if len(RecWordNgrams1) == 0 or len(PairsWordNGrams1) == 0:
        return 0
    return len([ Key for Key in RecWordNgrams1 if Key in PairsWordNGrams1 ]) / len(RecWordNgrams1)

def lookup_dp_dict(DPDict, IndexRecForDict, IndexPairs):
    Key = ( IndexRecForDict, IndexPairs )
    if not Key in DPDict:
        #lara_utils.print_and_flush(f'*** Error: entry not found in DP Dict: {Key}')
        return False
    else:
        return DPDict[Key]

def update_dp_dict(DPDict, IndexRecForDict, IndexPairs, NewCost, NewRecWords ):
    Key = ( IndexRecForDict, IndexPairs )
    if _dp_trace_level >= 2:
        lara_utils.print_and_flush(f'--- Marked result at {Key}')
    ( CurrentCost, CurrentRecWords ) = DPDict[Key] if Key in DPDict else ( False, False )
    if CurrentCost == False or NewCost < CurrentCost :
        DPDict[Key] = ( NewCost, NewRecWords )      

def count_n_more_content_words_in_pairs_or_end(CurrentIndex, N, Pairs):
    ( NPairs, NContentWordsCounted ) = ( len(Pairs), 0 )
    for Index in range(CurrentIndex, NPairs):
        if NContentWordsCounted == N:
            return Index
        elif Pairs[Index][0] != '':
            NContentWordsCounted += 1
    return NPairs

def alignment_from_dp_dict_result(DPDictResult, Pairs):
    #FileAndPairsIndexList = [ Item for Item in DPDictResult if isinstance(Item, ( tuple, list )) and len(Item) == 2 ]
    #return file_and_pairs_index_list_to_file_text_alignments(FileAndPairsIndexList, Pairs)
    return file_and_pairs_index_list_to_file_text_alignments(DPDictResult, Pairs)

# List of items of the form ( ( File, IndexPair ) where
# File is the audio file
# Index is the index into the list of pairs
# Return list of pairs of the form ( File, AlignedText )
def file_and_pairs_index_list_to_file_text_alignments(FileAndPairsIndexList0, Pairs):
    #lara_utils.print_and_flush(f'--- FileAndPairsIndexList:')
    #lara_utils.prettyprint(FileAndPairsIndexList0)
    ( FileAndPairsIndexList, AlignedPairs, CurrentText, NPairs ) = ( FileAndPairsIndexList0, [], '', len(Pairs) )
    for Index in range(0, NPairs + 1):
        if len(FileAndPairsIndexList) == 0:
            #lara_utils.print_and_flush(f'--- AlignedPairs:')
            #lara_utils.prettyprint(AlignedPairs)
            return AlignedPairs
        elif Index == FileAndPairsIndexList[0][1]:
            AlignedPairs += [ [ FileAndPairsIndexList[0][0], CurrentText ] ]
            FileAndPairsIndexList = FileAndPairsIndexList[1:]
            CurrentText = Pairs[Index][1] if Index < NPairs else ''
        else:
            CurrentText += Pairs[Index][1] if Index < NPairs else ''
    # Shouldn't get here, but...
    #lara_utils.print_and_flush(f'--- AlignedPairs (anomalous):')
    #lara_utils.prettyprint(AlignedPairs)
    return AlignedPairs

def update_aligned_file_from_aligned_list(RecResults, FilesAndAlignedTextList, Id, EvaluateOrCreate, AlignedFile, Params):
    FilesAndAlignedTextDict = { Item[0]: Item[1] for Item in FilesAndAlignedTextList }
    AlignedItemsList = [ rec_result_to_aligned_item(Item, FilesAndAlignedTextDict) for Item in RecResults ]
    if EvaluateOrCreate == 'evaluate':
        add_correct_transcriptions_to_aligned_items_list_from_audio_metadata(AlignedItemsList, Params)
    AlignedItemsData = lara_utils.read_json_file(AlignedFile) if lara_utils.file_exists(AlignedFile) else {}
    if not isinstance(AlignedItemsData, ( dict )):
        AlignedItemsData = { Id: AlignedItemsList }
    else:
        AlignedItemsData[Id] = AlignedItemsList
    lara_utils.write_json_to_file_plain_utf8(AlignedItemsData, AlignedFile)
    lara_utils.print_and_flush(f'--- Written aligned items data for "{Id}" ({len(AlignedItemsList)} items) to {AlignedFile}')
    return AlignedItemsList

def get_aligned_list_from_aligned_file(Id, Params):
    AlignedFile = Params.aligned_segments_file
    AlignedFileContents = lara_utils.read_json_file(AlignedFile)
    if not isinstance(AlignedFileContents, ( dict )):
        lara_utils.print_and_flush(f'*** Error: unable to read aligned file {AlignedFile}')
        return False
    if len(AlignedFileContents.keys()) == 1:
        AlignedFileList = list(AlignedFileContents.values())[0]
    elif not Id in AlignedFileContents:
        lara_utils.print_and_flush(f'*** Error: unable to find data for "{Id}" in {AlignedFile}')
        return False
    else:
        AlignedFileList = AlignedFileContents[Id]
    return [ [ Item['file'], Item['text_aligned'] ] for Item in AlignedFileList ]

def rec_result_to_aligned_item(RecResult, FilesAndAlignedTextDict):
    File = RecResult['file']
    Transcript = RecResult['result']['transcript']
    AlignedText = FilesAndAlignedTextDict[File] if File in FilesAndAlignedTextDict else False
    return { 'file': File,
             'recognised': Transcript,
             'text_aligned': AlignedText }

def add_correct_transcriptions_to_aligned_items_list_from_audio_metadata(FilesAndAlignedTextList, Params):
    AudioDir = Params.segment_audio_directory
    if AudioDir == '':
        lara_utils.print_and_flush(f'*** Error: segment_audio_directory not defined')
        return
    AudioMetadata = lara_audio.read_ldt_metadata_file(AudioDir)
    if AudioMetadata == False:
        lara_utils.print_and_flush(f'*** Error: unable to read audio metadata file from {AudioDir}')
        return
    AudioMetadataDict = { Item['file']: Item['text'] for Item in AudioMetadata }
    for Item in FilesAndAlignedTextList:
        add_text_aligned_correct_from_audio_metadata(Item, AudioMetadataDict)

def add_text_aligned_correct_from_audio_metadata(Item, AudioMetadataDict):
    File = Item['file']
    BaseFile = File.split('/')[-1]
    if BaseFile in AudioMetadataDict:
        Item['text_aligned_reference'] = AudioMetadataDict[BaseFile]
        EditDistance = lara_utils.word_edit_distance(str(Item['text_aligned_reference']).strip(),
                                                 lara_parse_utils.remove_html_annotations_from_string(str(Item['text_aligned']))[0].strip())
        Item['edit_distance'] = EditDistance
        Item['status'] = summarise_edit_distance(EditDistance)

def summarise_edit_distance(EditDistance):
    if EditDistance == 0:
        return 'fully_correct'
    if EditDistance < 5:
        return 'almost_correct'
    if EditDistance < 10:
        return 'minor_error'
    else:
        return 'wrong'

def files_and_aligned_text_list_to_segmented_text_file(FilesAndAlignedTextList, File):
    SegmentedText = files_and_aligned_text_list_to_segmented_text(FilesAndAlignedTextList)
    lara_utils.write_lara_text_file(SegmentedText, File)
    lara_utils.print_and_flush(f'--- Written segmented text file ({len(FilesAndAlignedTextList)} segments): {File}')

def files_and_aligned_text_list_to_segmented_text(FilesAndAlignedTextList):
    TextList = [ Item[1] for Item in FilesAndAlignedTextList if isinstance(Item[1], ( str ))]
    return '||'.join(TextList)

def adjust_files_and_aligned_text_list(FilesAndAlignedTextList, Params):
    if len(FilesAndAlignedTextList) == 0 or Params.alignment_postprocessing == 'no':
        return FilesAndAlignedTextList
    I = 0
    while True:
        ChangesMade = adjust_files_and_aligned_text_list1(FilesAndAlignedTextList)
        lara_utils.print_and_flush(f'--- Round: "{I}", ChangesMade: {ChangesMade}')
        I += 1
        if ChangesMade == False or I >= 10:
            return FilesAndAlignedTextList

def adjust_files_and_aligned_text_list1(FilesAndAlignedTextList):
    AnyChangesMade = False  
    for Index in range(0, len(FilesAndAlignedTextList)):  
        ( File, Text ) = FilesAndAlignedTextList[Index]
        Operation = get_adjust_files_and_aligned_text_operation(Text)
        if Operation != False:
            ChangesMade = perform_adjust_files_and_aligned_text_operation(Operation, FilesAndAlignedTextList, Index)
            lara_utils.print_and_flush(f'--- Text: "{Text}", Operation: {Operation}, ChangesMade = {ChangesMade}')
            AnyChangesMade = AnyChangesMade or ChangesMade
    return AnyChangesMade

_perform_adjust_files_and_aligned_text_operations = [ 'move_to_next_line',
                                                      'move_to_previous_line',
                                                      'change_line' ]

def perform_adjust_files_and_aligned_text_operation(Operation, FilesAndAlignedTextList, Index):
    if not isinstance(Operation, dict) or not 'type' in Operation or not 'left' in Operation or not 'to_move' in Operation:
        lara_utils.print_and_flush(f'*** Error: bad adjust_files_and_aligned_text operation: {Operation}.')
        return False
    Type = Operation['type']
    if Type == 'move_to_next_line':
        return move_material_to_next_line(Operation, FilesAndAlignedTextList, Index)
    elif Type == 'move_to_previous_line':
        return move_material_to_previous_line(Operation, FilesAndAlignedTextList, Index)
    elif Type == 'change_line':
        return change_line(Operation, FilesAndAlignedTextList, Index)
    else:
        lara_utils.print_and_flush(f'*** Error: unknown adjust_files_and_aligned_text operation: {Type}.')
        lara_utils.print_and_flush(f'*** Needs to be one of {_perform_adjust_files_and_aligned_text_operations}')
        return False               

def move_material_to_next_line(Operation, FilesAndAlignedTextList, Index):
    NItems = len(FilesAndAlignedTextList)
    # At end, there is nowhere to move the material
    if Index + 1 >= NItems :
        return False
    else:
        ( File, Text ) = FilesAndAlignedTextList[Index]
        ( File1, Text1 ) = FilesAndAlignedTextList[Index + 1] 
        ( MaterialLeft, MaterialToMove ) = ( Operation['left'], Operation['to_move'] )
        if not check_material_moved_to_next_line(Text, MaterialLeft, MaterialToMove):
            return False
        FilesAndAlignedTextList[Index] = [ File, MaterialLeft ]
        FilesAndAlignedTextList[Index + 1] = [ File1, MaterialToMove + Text1 ]
        return True

def check_material_moved_to_next_line(Text, MainText, MaterialToMove):
    if len(Text) != len(MainText) + len(MaterialToMove):
        lara_utils.print_and_flush(f'*** Error: "{Text}" split into "{MainText}" + "{MaterialToMove}"')
        return False
    else:
        return True

def move_material_to_previous_line(Operation, FilesAndAlignedTextList, Index):
    # At start, there is nowhere to move the material
    if Index == 0:
        return False
    else:
        ( File, Text ) = FilesAndAlignedTextList[Index]
        ( File1, Text1 ) = FilesAndAlignedTextList[Index - 1]
        ( MaterialLeft, MaterialToMove ) = ( Operation['left'], Operation['to_move'] )
        if not check_material_moved_to_previous_line(Text, MaterialLeft, MaterialToMove):
            return False
        FilesAndAlignedTextList[Index - 1] = [ File1, Text1 + MaterialToMove ]
        FilesAndAlignedTextList[Index] = [ File, MaterialLeft ]
        return True

def check_material_moved_to_previous_line(Text, MainText, MaterialToMove):
    if len(Text) != len(MaterialToMove) + len(MainText):
        lara_utils.print_and_flush(f'*** Error: "{Text}" split into "{MaterialToMove}" and "{MainText}"')
        return False
    else:
        return True

def change_line(Operation, FilesAndAlignedTextList, Index):
    ( File, Text ) = FilesAndAlignedTextList[Index]
    MaterialLeft = Operation['left']
    if not check_change_line(Text, MaterialLeft):
        return False
    FilesAndAlignedTextList[Index] = [ File, MaterialLeft ]
    return True

def check_change_line(Text, MainText):
    if len(Text) != len(MainText):
        lara_utils.print_and_flush(f'*** Error: "{Text}" replaced by "{MainText}"')
        return False
    else:
        return True

# Handle some common cases:
# 1. Newline near end of line with at most one word following usually belongs to next line, so move it.
#    Ignore HTML tags (in particular, audio control can easily occur here).
# 2. // near end of line with at most one word following usually belongs to next line, so move it.
#    Ignore HTML tags (in particular, audio control can easily occur here).
# 3. Whitespace at end of line should always be moved 

def get_adjust_files_and_aligned_text_operation(Text0):
    #Text = normalise_text_for_adjusting_aligned_text(Text0)
    Text = Text0
    ComponentsNL = Text.split('\n')
    ComponentsSL = Text.split('//')
    RStripped = Text.rstrip()
    LeftPunctAtEndMatch = re.search(r'([^\S]*[“«\(])$', Text)
    LeftPunctAtEndStr = False if LeftPunctAtEndMatch == None else LeftPunctAtEndMatch.group(1)
    #    Newline near end of line with at most one word following usually belongs to next line, so move it.
    #    Ignore HTML tags (in particular, audio control can easily occur here).
    if len(ComponentsNL) > 1 and contains_at_most_one_word(ComponentsNL[-1]) and contains_at_least_one_word(ComponentsNL[-2]):
        MaterialToMove = '\n' + ComponentsNL[-1]
        MaterialLeft = Text[:-1 * ( len(MaterialToMove) )]
        return { 'type': 'move_to_next_line', 'to_move': MaterialToMove, 'left': MaterialLeft }
    #   Whitespace at end of line should always be moved 
    elif Text != RStripped:
        MaterialLeft = RStripped
        MaterialToMove = Text[-1 * ( len(Text) - len(MaterialLeft) ):]
        return { 'type': 'move_to_next_line', 'to_move': MaterialToMove, 'left': MaterialLeft }
    #    // near end of line with at most one word following usually belongs to next line, so move it.
    #    Ignore HTML tags (in particular, audio control can easily occur here).
    elif len(ComponentsSL) > 1 and contains_at_most_one_word(ComponentsSL[-1]) and contains_at_least_one_word(ComponentsSL[-2]):
        MaterialToMove = '//' + ComponentsSL[-1]
        MaterialLeft = Text[:-1 * ( len(MaterialToMove) )]
        return { 'type': 'move_to_next_line', 'to_move': MaterialToMove, 'left': MaterialLeft }
    # Moving non-content before initial // after it.
    elif len(ComponentsSL) > 1 and ComponentsSL[0] != '' and contains_no_words(ComponentsSL[0]):
        MaterialToMove = ''
        MaterialLeft = '//' + ComponentsSL[0] + Text[len(ComponentsSL[0]) + len('//'):]
        return { 'type': 'change_line', 'to_move': MaterialToMove, 'left': MaterialLeft }
    # Move a left-quote or left-parenthesis at the end to the next line, together with preceding spaces
    elif LeftPunctAtEndStr != False:
        MaterialToMove = LeftPunctAtEndStr
        MaterialLeft = Text[:-1 * ( len(MaterialToMove) )]
        return { 'type': 'move_to_next_line', 'to_move': MaterialToMove, 'left': MaterialLeft }
    else:
        return False

# Consolidate multiple newlines into a single newline
def normalise_text_for_adjusting_aligned_text(Text):
    return re.sub(r'(\n)+', '\n', Text)

def contains_no_words(Text):
    Text1 = lara_parse_utils.remove_punctuation_marks(lara_parse_utils.remove_html_annotations_from_string(Text)[0])
    return len(Text1.split()) == 0

def contains_one_word(Text):
    Text1 = lara_parse_utils.remove_punctuation_marks(lara_parse_utils.remove_html_annotations_from_string(Text)[0])
    return len(Text1.split()) == 1

def contains_at_most_one_word(Text):
    Text1 = lara_parse_utils.remove_punctuation_marks(lara_parse_utils.remove_html_annotations_from_string(Text)[0])
    return len(Text1.split()) <= 1

def contains_at_least_one_word(Text):
    Text1 = lara_parse_utils.remove_punctuation_marks(lara_parse_utils.remove_html_annotations_from_string(Text)[0])
    return len(Text1.split()) >= 1

def files_and_aligned_text_list_to_audio_metadata_file(FilesAndAlignedTextList, File):
    Metadata = files_and_aligned_text_list_to_audio_metadata(FilesAndAlignedTextList)
    lara_utils.write_json_to_file_plain_utf8(Metadata, File)
    lara_utils.print_and_flush(f'--- Written audio metadata file ({len(FilesAndAlignedTextList)} item): {File}')

def files_and_aligned_text_list_to_audio_metadata(FilesAndAlignedTextList):
    Params = lara_config.default_params()
    return [ files_and_aligned_text_list_item_to_audio_metadata_item(Item, Params) for Item in FilesAndAlignedTextList
             if isinstance(Item[1], ( str ))]

def files_and_aligned_text_list_item_to_audio_metadata_item(Item, Params):
    ( File, RawText ) = Item
    BaseFile = File.split('/')[-1]
    CleanedText = lara_split_and_clean.minimal_clean_lara_string(RawText.replace('//', ''), Params)[0]
    return { 'file': BaseFile, 'text': CleanedText }

# ------------------------------------------

def create_corpus_with_numbered_labels(ConfigFile, LabelledFile):
    create_plain_or_labelled_corpus(ConfigFile, 'numbered_labels', LabelledFile)

def create_plain_corpus(ConfigFile, LabelledFile):
    create_plain_or_labelled_corpus(ConfigFile, 'plain', LabelledFile)

_known_corpus_label_types = ( 'numbered_labels', 'plain' )

def create_plain_or_labelled_corpus(ConfigFile, LabelType, LabelledFile):
    if not LabelType in _known_corpus_label_types:
        lara_utils.print_and_flush(f'*** Error: unknown label type "{LabelType}". Must be in {_known_corpus_label_types}')
        return
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if Params == False:
        return
    SplitFile = lara_top.lara_tmp_file('split', Params)
    PageOrientedSplitList = lara_split_and_clean.read_split_file(SplitFile, Params)
    ( OutText, CurrentLabel ) = ( '', 1 )
    for ( PageInfo, Units ) in PageOrientedSplitList:
        for Unit in Units:
            if lara_picturebook.is_annotated_image_segment(Unit):
                InnerUnits = lara_picturebook.annotated_image_segments(Unit)
                for InnerUnit in InnerUnits:
                    RawText = InnerUnit[0]
                    Text = regularise_for_create_corpus_with_numbered_labels(RawText, Params)
                    LabelText = f'|{CurrentLabel}|' if LabelType == 'numbered_labels' else ''
                    OutText += f'{Text}{LabelText}'
                    CurrentLabel += 1
            else:     
                RawText = Unit[0]
                Text = regularise_for_create_corpus_with_numbered_labels(RawText, Params)
                LabelText = f'|{CurrentLabel}|' if LabelType == 'numbered_labels' else ''
                OutText += f'{Text}{LabelText}'
                CurrentLabel += 1
    lara_utils.write_lara_text_file(OutText, LabelledFile)
    lara_utils.print_and_flush(f'--- Written {LabelType} corpus file ({CurrentLabel-1} segments): {LabelledFile}')

# ------------------------------------------

def check_audio_alignment_corpus_compatible_with_cutting_up_params(Params):
    CuttingUpParams = Params.audio_cutting_up_parameters
    if not check_cutting_up_params_valid_for_alignment(Params):
        return False
    CorpusLabels = lara_partitioned_text_files.labels_in_partitioned_file(Params.audio_alignment_corpus)
    if len(CorpusLabels) == 1 and len(CuttingUpParams) == 1:
        return True
    ParamsLabels = [ Item['id'] for Item in CuttingUpParams ]
    if CorpusLabels == ParamsLabels:
        return True
    else:
        lara_utils.print_and_flush(f'*** Error: labels in audio_alignment_corpus are not the same as labels in audio_cutting_up_parameters')
        lara_utils.print_and_flush(f'*** Error:      audio_alignment_corpus labels: {CorpusLabels}')
        lara_utils.print_and_flush(f'*** Error: audio_cutting_up_parameters labels: {ParamsLabels}')
        return False

def check_cutting_up_params_valid_for_alignment(Params):
    CuttingUpParams = Params.audio_cutting_up_parameters
    if not isinstance(CuttingUpParams, ( list, tuple ) ):
        lara_utils.print_and_flush(f'*** Error: audio_cutting_up_parameters is not a list')
        return False
    for Item in CuttingUpParams:
        if not 'id' in Item:
            lara_utils.print_and_flush(f'*** Error: Item {Item} audio_cutting_up_parameters does not include an "id" field')
            return False
    return True   

# ------------------------------------------

# We build the untagged_corpus out of aligned data separated by <file id="{Label}"> tags
# i.e. same format as audio_alignment_corpus

def insert_text_for_spec_into_untagged_corpus(NewText, NewLabel, Params):
    # Use Params.double_segmented_corpus if it exists, else Params.untagged_corpus
    UntaggedCorpusFile = Params.double_segmented_corpus if Params.double_segmented_corpus != '' else Params.untagged_corpus
    # Add a ||// or || to the end to separate from next partition
    EndOfPartitionSeparator = '||//' if lara_align_adjust.audio_alignment_corpus_contains_translation_segmention_markers(Params) else '||'
    NewText1 = NewText + EndOfPartitionSeparator
    lara_partitioned_text_files.update_partitioned_text_file(UntaggedCorpusFile, NewLabel, NewText1, Params)
    return True

# ------------------------------------------

# Note that, unlike the normal case, we use the FILES as key and replace the TEXT, rather than vice versa.
def insert_metadata_from_alignment_into_segment_audio_dir(NewMetadata, Params):
    AudioDir = Params.segment_audio_directory
    OldMetadata = lara_audio.read_ldt_metadata_file(AudioDir)
    UpdatedMetadata = clean_audio_metadata_from_alignment(OldMetadata + NewMetadata)
    lara_audio.write_ldt_metadata_file(UpdatedMetadata, AudioDir)
    lara_utils.print_and_flush(f'--- Updated metadata file in {AudioDir} with metadata from alignment')

def clean_audio_metadata_from_alignment(Metadata):
    ( LinesOutDict, NKept, NRemoved ) = ( {}, 0, 0 )
    for MetadataItem in [ Item for Item in Metadata if isinstance(Item, dict) and 'text' in Item and 'file' in Item if Item['file'] != '' ]:
        Text = MetadataItem['text']
        File = MetadataItem['file']
        Context = MetadataItem['context'] if 'context' in MetadataItem else ''
        # Use the file as the key, since this data comes from files rather than text
        Key = File
        # if it's not already listed, add it
        if not Key in LinesOutDict:
            LinesOutDict[Key] = MetadataItem
            NKept += 1
        # else replace the old one, since the later entries take precedence
        else:
            LinesOutDict[Key] = MetadataItem
            NRemoved += 1
    CleanedMetadata = [ LinesOutDict[Key] for Key in LinesOutDict ]
    lara_utils.print_and_flush(f'\n--- {NRemoved} metadata lines removed, {NKept} kept.')
    return CleanedMetadata

# ------------------------------------------

def get_ordered_segment_audio_rec_results_from_params_and_spec(Params, Label):
    AudioDir = Params.segment_audio_directory
    CuttingUpParams = Params.audio_cutting_up_parameters
    lara_utils.print_and_flush(f'--- CuttingUpParams = {CuttingUpParams}')
    AllRecResults = lara_asr.read_rec_results_file(AudioDir)
    if AllRecResults == False:
        lara_utils.print_and_flush(f'*** Error: no recognition results found')
        return
    if 'use_all_rec_results' in CuttingUpParams[0] and CuttingUpParams[0]['use_all_rec_results'] == 'yes':
        lara_utils.print_and_flush(f'--- Use all rec results and assume they are ordered')
        SortedRelevantRecResults = AllRecResults
    else:
        RelevantRecResultsAndKeys = get_rec_results_and_keys_for_labels(AllRecResults, [ Label ])
        SortedRelevantRecResultsAndKeys = sorted(RelevantRecResultsAndKeys, key=lambda x: x[1])
        SortedRelevantRecResults = [ Item[0] for Item in SortedRelevantRecResultsAndKeys ]
    return [ add_dir_to_rec_result_file(AudioDir, Item)
             for Item in SortedRelevantRecResults ]    

def add_dir_to_rec_result_file(Dir, RecResult):
    return { 'file': f"{Dir}/{RecResult['file']}",
             'result': RecResult['result']
             }

# Format of file name is
# extracted_file_<Label>_<Index>.mp3
# extracted_file_part1_3.mp3

def get_rec_results_and_keys_for_labels(AllRecResults, RelevantLabels):
    OutList = []
    for RecResult in AllRecResults:
        File = RecResult['file']
        ( Label, FileIndex ) = get_label_and_index_from_audio_file(File)
        if Label in RelevantLabels:
            LabelIndex = RelevantLabels.index(Label)
            # We want to sort by LabelIndex first and then FileIndex
            Key = 100000 * LabelIndex + FileIndex
            OutList += [ [ RecResult, Key ] ]
    return OutList

def get_label_and_index_from_audio_file(File):
    Match = re.search("extracted_file_(.*)_([0-9]+).mp3", File)
    if Match == None:
        lara_utils.print_and_flush(f'*** Error: cannot extract label and index from audio file name {File}')
        return ( False, False )
    ( Label, Index ) = ( Match.group(1), lara_utils.safe_string_to_int(Match.group(2)) )
    return ( Label, Index )
                         
# ------------------------------------------

def get_word_pairs_from_params_and_spec(Params, Label):
    File = Params.audio_alignment_corpus
    Text = lara_partitioned_text_files.extract_from_partitioned_file(File, Label)
    if Text == False:
        return False
    Text1 = normalise_text_for_adjusting_aligned_text(Text)
    ( Pairs, Errors ) = lara_split_and_clean.string_to_annotated_words(Text1)
    if Errors != []:
        return False
    return pairs_to_pairs_for_word_list_corpus(Pairs, Params)

# Create a list of ( RegularisedWord, Surface, Lemma ) triples
def create_word_pair_corpus(ConfigFile, WordPairsFile):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if Params == False:
        return
    SplitFile = lara_top.lara_tmp_file('split', Params)
    PageOrientedSplitList = lara_split_and_clean.read_split_file(SplitFile, Params)
    PageList = []
    for ( PageInfo, Units ) in PageOrientedSplitList:
        PairsList = []
        for Unit in Units:
            if lara_picturebook.is_annotated_image_segment(Unit):
                InnerUnits = lara_picturebook.annotated_image_segments(Unit)
                for InnerUnit in InnerUnits:
                    Pairs = InnerUnit[2]
                    PairsList += pairs_to_pairs_for_word_list_corpus(Pairs, Params)
            else:     
                Pairs = Unit[2]
                PairsList += pairs_to_pairs_for_word_list_corpus(Pairs, Params)
        PageList += [ ( PageInfo, PairsList ) ]
    lara_utils.write_json_to_file_plain_utf8(PageList, WordPairsFile)
    AllWords = [ Pair for ( PageInfo, PairsList ) in PageList for Pair in PairsList ]
    lara_utils.print_and_flush(f'--- Written words pairs file ({len(AllWords)} words): {WordPairsFile}')

def pairs_to_pairs_for_word_list_corpus(Pairs, Params):
    Pairs1 = [ pairs_to_pair_for_word_list_corpus(Pair, Params) for Pair in Pairs ]
    return consolidate_pairs_in_list_for_word_list_corpus(Pairs1)

_apostrophes_and_hyphens = "'’-"

def consolidate_pairs_in_list_for_word_list_corpus(Pairs):
    if len(Pairs) == 0:
        return Pairs
    ( OutPairs, CurrentPair ) = ( [], Pairs[0] )
    for Pair in Pairs[1:]:
        # If two content words are in sequence with no filler in between, join them
        if ( CurrentPair[0] != '' and Pair[0] != '' ):
            CurrentPair = ( CurrentPair[0] + Pair[0], CurrentPair[1] + Pair[1] )
        elif ( CurrentPair[0] == '' and Pair[0] == '' ):
            CurrentPair = ( '', CurrentPair[1] + Pair[1] )
        #elif ( CurrentPair[0] != '' and Pair[1] == '-' ):
        #    CurrentPair = ( CurrentPair[0] + '-', CurrentPair[1] + '-' )
        # If a content word is followed by a single apostrophe or hyphen, join them
        # This will produce the wrong result if the apostrophe is being used as a quotation mark
        # and there is no following whitespace or other punctuation mark.
        # Hopefully this is very rare. It should not be correct punctuation.
        elif ( CurrentPair[0] != '' and Pair[1] in _apostrophes_and_hyphens ):
            CurrentPair = ( CurrentPair[0] + Pair[1], CurrentPair[1] + Pair[1] )
        else:
            OutPairs += [ CurrentPair ]
            CurrentPair = Pair
    return OutPairs + [ CurrentPair ]

def pairs_to_pair_for_word_list_corpus(Pair, Params):
    ( Surface, Lemma ) = Pair
    Regularised = regularise_for_create_corpus_with_numbered_labels(Surface, Params).lower() if Lemma != '' else ''
    return ( Regularised, Surface ) 

def regularise_for_create_corpus_with_numbered_labels(RawText, Params):
    return lara_parse_utils.remove_hashtag_comment_and_html_annotations(RawText, Params)[0].replace('|', '')

def read_json_file_or_files(FileOrFiles):
    if isinstance(FileOrFiles, ( str )):
        lara_utils.print_and_flush(f'--- Trying to read {FileOrFiles} as single file')
        return lara_utils.read_json_file(FileOrFiles)
    elif isinstance(FileOrFiles, ( list, tuple )):
        lara_utils.print_and_flush(f'--- Trying to read {FileOrFiles} as list of files')
        AllContents = []
        for File in FileOrFiles:
            Contents = lara_utils.read_json_file(File)
            if Contents == False:
                lara_utils.print_and_flush(f'*** Error: unable to read {File}')
                return False
            elif not isinstance(Contents, ( list, tuple )):
                lara_utils.print_and_flush(f'*** Error: contents of {File} are not a list')
                return False
            else:
                AllContents += list(Contents)
    return AllContents

# ------------------------------------------

##def find_segments_not_ending_in_punctuation(ConfigFile, AlignedFile, DisplayDir):
##    Params = lara_config.read_lara_local_config_file(ConfigFile)
##    SegmentAudioDir = Params.segment_audio_directory
##    if Params == False or SegmentAudioDir == '':
##        return False
##    lara_utils.create_directory_deleting_old_if_necessary(DisplayDir)
##    DisplayFile = f'{DisplayDir}/segments_not_ending_in_punctuation.html'
##    MultimediaDir = f'{DisplayDir}/multimedia'
##    SegmentAudioDict = get_segment_audio_dict(Params)
##    AlignedFileContent = lara_utils.read_json_file(AlignedFile)
##    Items = [ Item for Key in AlignedFileContent for Item in AlignedFileContent[Key] ]
##    lara_utils.print_and_flush(f'--- Read aligned data ({len(Items)} items)')
##    Items1 = [ Item for Item in Items if item_not_ending_in_punctuation(Item) ]
##    lara_utils.print_and_flush(f'--- {len(Items1)} items not ending in punctuation')
##    make_aligned_item_audio_display_file(Items1, DisplayDir, SegmentAudioDir, SegmentAudioDict, MultimediaDir, Params)
##
##def get_segment_audio_dict(Params):
##    AudioDict = Params.segment_audio_directory
##    Metadata = lara_audio.read_ldt_metadata_file(AudioDict)
##    return { Item['text']: Item['file'] for Item in Metadata }
##
##def item_not_ending_in_punctuation(Item):
##    AlignedText = Item['text_aligned']
##    if AlignedText == False:
##        return False
##    return text_not_ending_in_punctuation(AlignedText)
##
##def text_not_ending_in_punctuation(Text):
##    Text = Text.strip()
##    if Text == '':
##        return False
##    LastChar = Text[-1]
##    return not lara_parse_utils.is_punctuation_char(LastChar) and not LastChar in '>'
##
##def make_aligned_item_audio_display_file(Items, DisplayDir, SegmentAudioDir, SegmentAudioDict, MultimediaDir, Params):
##    HeaderLines = aligned_item_audio_display_file_header(Params)
##    BodyLines = [ aligned_item_audio_display_line(Item, DisplayDir, SegmentAudioDir, SegmentAudioDict, MultimediaDir, Params)
##                  for Item in Items ]
##    Coda = aligned_item_audio_display_file_coda(Params)
##    AllLines = HeaderLines + BodyLines + Coda
##    DisplayFile = f'{DisplayDir}/items.html'
##    lara_utils.write_lara_text_file('\n'.join(AllLines), DisplayFile)
##
##def aligned_item_audio_display_line(Item, DisplayDir, SegmentAudioDir, SegmentAudioDict, MultimediaDir, Params):
##    AlignedText = Item['text_aligned']
##    if AlignedText == False:
##        return '(null item)'
##    CleanedAlignedText = lara_split_and_clean.minimal_clean_lara_string(AlignedText, Params)[0]
##    AudioFile = SegmentAudioDict[CleanedAlignedText] if CleanedAlignedText in SegmentAudioDict else False
##    if AudioFile == False:
##        SpeakerControl = ''
##        lara_utils.print_and_flush(f'*** Warning: no audio file found for "{CleanedAlignedText}"')
##    else:
##        lara_utils.copy_file(f'{SegmentAudioDir}/{AudioFile}', f'{DisplayDir}/{AudioFile}')
##        PlaySoundCall = lara_audio.construct_play_sound_call_for_word(f'{AudioFile}', Params)
##        LoudspeakerIcon = '&#x1f50a;'
##        SpeakerControl = f'<span class="sound" onclick="{PlaySoundCall}">{LoudspeakerIcon}</span>'
##    return f'<p>{AlignedText} {SpeakerControl}</p>'
##
##def aligned_item_audio_display_file_header(Params):
##    return [f'{lara_html.html_tag_for_vocab_pages(Params)}',  
##	    '<head>',
##	    '<meta http-equiv="Content-Type" content="text/html;charset=UTF-8">',
##	    lara_html.link_to_css_files(Params),
##	    '<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.0/jquery.min.js"></script>'] + \
##	    [lara_html.link_to_script_files(Params),
##	    '</head>',
##	    '<body>']
##
##def aligned_item_audio_display_file_coda(Params):
##    return ['</body>',
##            '</html>' ]





    
    
