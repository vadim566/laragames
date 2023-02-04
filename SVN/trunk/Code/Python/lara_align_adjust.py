
##    Adjust segmentation created by splitting on silences and aligned against text
##    so that it matches segmentation created by source/target alignment from YouAlign.
##
##    Inputs:
##
##    1. Corpus
##    2. TMX file converted to JSON: ordered source/target Triples 
##       with segmentation defined by YouAlign
##    3. Aligned audio in metadata (segment texts -> audio files)
##       with segmentation defined by naive splitting on silences + text/audio alignment
##    4. Rec results (audio files -> word rec results)
##    5. Silence information (audio files -> locations of silences)
##
##    Processing:
##
##    - Add markers for both segmentations to corpus.
##    - Extract decomposition of YouAlign segments into (in general, pieces of) Silences segments.
##    - Extract required decomposition of Silences segments.
##    - [Non-trivial part] Develop method for splitting audio segment at text period.
##      - In most cases, the period will coincide with some kind of pause, so silences will give information.
##      - Rec word results will give information.
##      - Combine to create alignment method.
##        Plausible first cut: existing alignment method with bonus for matching period against silence.
##
##    Outputs:
##
##    1. Corpus with segmentation defined by YouAlign.
##    2. New set of audio files corresponding to segmentation defined by YouAlign

import lara_config
#import lara_align_from_audio
import lara_tmx
import lara_translations
import lara_audio
import lara_install_audio_zipfile
import lara_split_and_clean
import lara_partitioned_text_files
import lara_parse_utils
import lara_utils
import re

def test(Id):
    if Id == 'combray_small':
        ConfigFile = '$LARA/Content/combray/corpus/local_config_small.json'
        Spec = 'all'
        TMXFile = '$LARA/Content/combray/translations/combray_small_FRA-ENG_BT.tmx'
        SourceLang = 'fr'
        TargetLang = 'en'
        TMXSegmentedCorpusFile = '$LARA/Content/combray/corpus/combray_small_translation_segmented.txt'
        TranslationsCSV = '$LARA/Content/combray/translations/french_english_from_tmx_small.csv'
        add_tmx_segmentation_to_corpus(ConfigFile, Spec, TMXFile, SourceLang, TargetLang, TMXSegmentedCorpusFile, TranslationsCSV)
    elif Id == 'combray_ch1':
        ConfigFile = '$LARA/Content/combray/corpus/local_config_ch1_double_align.json'
        Spec = 'ch1'
        TMXFile = '$LARA/Content/combray/translations/combray_ch1_FRA-ENG_BT.tmx'
        SourceLang = 'fr'
        TargetLang = 'en'
        TMXSegmentedCorpusFile = '$LARA/Content/combray/corpus/combray_ch1_translation_segmented.txt'
        TranslationsCSV = '$LARA/Content/combray/translations/french_english_from_tmx_ch1.csv'
        add_tmx_segmentation_to_corpus(ConfigFile, Spec, TMXFile, SourceLang, TargetLang, TMXSegmentedCorpusFile, TranslationsCSV)
    elif Id == 'combray_ch2_fre_text_for_you_align':
        FileIn = '$LARA/Content/combray/corpus/combray_segmented_from_aligner_ch2_double_align.txt'
        FileOut = '$LARA/Content/combray/corpus/combray_fre_ch2.txt'
        lara_parse_utils.remove_segment_markings_and_html_from_file(FileIn, FileOut)
    elif Id == 'combray_ch2_translation_align':
        ConfigFile = '$LARA/Content/combray/corpus/local_config_ch2_double_align.json'
        Spec = 'ch2'
        TMXFile = '$LARA/Content/combray/translations/combray_ch2_FRA-ENG_BT.tmx'
        SourceLang = 'fr'
        TargetLang = 'en'
        TMXSegmentedCorpusFile = '$LARA/Content/combray/corpus/combray_ch2_translation_segmented.txt'
        TranslationsCSV = '$LARA/Content/combray/translations/french_english_from_tmx_ch2.csv'
        add_tmx_segmentation_to_corpus(ConfigFile, Spec, TMXFile, SourceLang, TargetLang, TMXSegmentedCorpusFile, TranslationsCSV)
    elif Id == 'check_combray_small':
        DoubleAlignedFile = '$LARA/Content/combray/corpus/combray_segmented_from_aligner_small.txt'
        SegmentTranslationCSV = '$LARA/Content/combray/translations/french_english_from_tmx_small.csv'
        ConfigFile = '$LARA/Content/combray/corpus/local_config_small.json'
        check_segment_translations_in_double_aligned_file(DoubleAlignedFile, SegmentTranslationCSV, ConfigFile)
    elif Id == 'check_combray_ch1':
        DoubleAlignedFile = '$LARA/Content/combray/corpus/combray_segmented_from_aligner_ch1_double_align.txt'
        SegmentTranslationCSV = '$LARA/Content/combray/translations/french_english_from_tmx_ch1.csv'
        ConfigFile = '$LARA/Content/combray/corpus/local_config_ch1_double_align.json'
        check_segment_translations_in_double_aligned_file(DoubleAlignedFile, SegmentTranslationCSV, ConfigFile)
    elif Id == 'check_combray_ch2':
        DoubleAlignedFile = '$LARA/Content/combray/corpus/combray_segmented_from_aligner_ch2_double_segmented.txt'
        SegmentTranslationCSV = '$LARA/Content/combray/translations/french_english_from_tmx_ch2.csv'
        ConfigFile = '$LARA/Content/combray/corpus/local_config_ch2_double_align.json'
        check_segment_translations_in_double_aligned_file(DoubleAlignedFile, SegmentTranslationCSV, ConfigFile)
    elif Id == 'correct_combray_ch2_translations':
        DoubleAlignedFile = '$LARA/Content/combray/corpus/combray_segmented_from_aligner_ch2_double_segmented.txt'
        SegmentTranslationCSV = '$LARA/Content/combray/translations/french_english_from_tmx_ch2.csv'
        SegmentTranslationCSV1 = '$LARA/Content/combray/translations/french_english_from_tmx_ch2_corrected.csv'
        ConfigFile = '$LARA/Content/combray/corpus/local_config_ch2_double_align.json'
        correct_segment_translations_for_double_aligned_file(DoubleAlignedFile, 'ch2', SegmentTranslationCSV, SegmentTranslationCSV1, ConfigFile)
    elif Id == 'make_merged_content_combray_small':
        DoubleAlignedFile = '$LARA/Content/combray/corpus/combray_segmented_from_aligner_small.txt'
        SegmentTranslationCSV = '$LARA/Content/combray/translations/french_english_from_tmx_small.csv'
        ConfigFile = '$LARA/Content/combray/corpus/local_config_small.json'
        make_corpus_audio_and_translations_for_double_aligned_file(DoubleAlignedFile, 'all', SegmentTranslationCSV, ConfigFile)
    elif Id == 'make_merged_content_combray_ch1':
        DoubleAlignedFile = '$LARA/Content/combray/corpus/combray_segmented_from_aligner_ch1_double_align.txt'
        SegmentTranslationCSV = '$LARA/Content/combray/translations/french_english_from_tmx_ch1.csv'
        ConfigFile = '$LARA/Content/combray/corpus/local_config_ch1_double_align.json'
        make_corpus_audio_and_translations_for_double_aligned_file(DoubleAlignedFile, 'ch1', SegmentTranslationCSV, ConfigFile)
    elif Id == 'make_merged_content_combray_ch2':
        DoubleAlignedFile = '$LARA/Content/combray/corpus/combray_segmented_from_aligner_ch2_double_segmented.txt'
        SegmentTranslationCSV = '$LARA/Content/combray/translations/french_english_from_tmx_ch2.csv'
        ConfigFile = '$LARA/Content/combray/corpus/local_config_ch2_double_align.json'
        make_corpus_audio_and_translations_for_double_aligned_file(DoubleAlignedFile, 'ch2', SegmentTranslationCSV, ConfigFile)
    else:
        lara_utils.print_and_flush(f'*** Error: unknown ID: {Id}')

def add_tmx_segmentation_from_config_file(ConfigFile, Label):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if Params == False:
        return
    ( TMXFile, SourceLang, TargetLang ) = get_tmx_segmentation_info_from_params(Params, Label)
    if TMXFile == False:
        return
    CorpusTriples = get_word_triples_for_corpus(Label, Params)
    if CorpusTriples == False:
        return
    TMXTriples = tmx_file_to_word_triples(TMXFile, SourceLang, TargetLang, Params)
    if TMXTriples == False:
        return
    TMXSegmentedCorpusTriples = add_tmx_segmentation_to_word_triples(CorpusTriples, TMXTriples)
    update_audio_alignment_corpus_from_tmx_triples(TMXSegmentedCorpusTriples, Label, Params)
    update_segment_translations_csv_from_tmx_triples(TMXSegmentedCorpusTriples, Params)

def get_tmx_segmentation_info_from_params(Params, Label):
    if Params.audio_alignment_corpus == '':
        lara_utils.print_and_flush(f'*** Error: audio_alignment_corpus is not defined')
        return ( False, False, False)
    if Params.segment_translation_spreadsheet == '':
        lara_utils.print_and_flush(f'*** Error: segment_translation_spreadsheet is not defined')
        return ( False, False, False)
    TMXFiles = Params.tmx_files
    SourceLang = Params.tmx_source_lang
    TargetLang = Params.tmx_target_lang
    if TMXFiles == False:
        lara_utils.print_and_flush(f'*** Error: tmx_files is not defined')
        return ( False, False, False)
    if not isinstance(TMXFiles, ( dict )) or not Label in TMXFiles:
        lara_utils.print_and_flush(f'*** Error: "{Label}" not specified in tmx_files value {TMXFiles}')
        return ( False, False, False)
    TMXFile = TMXFiles[Label]
    if not lara_utils.file_exists(TMXFile):
        lara_utils.print_and_flush(f'*** Error: {TMXFile} not found')
        return ( False, False, False)
    if SourceLang == '':
        lara_utils.print_and_flush(f'*** Error: tmx_source_lang is not defined')
        return ( False, False, False)
    if TargetLang == '':
        lara_utils.print_and_flush(f'*** Error: tmx_target_lang is not defined')
        return ( False, False, False)
    return ( TMXFile, SourceLang, TargetLang )

def add_tmx_segmentation_to_corpus(ConfigFile, Label, TMXFile, SourceLang, TargetLang, TMXSegmentedCorpusFile, TranslationsCSV):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if Params == False:
        return
    CorpusTriples = get_word_triples_for_corpus(Label, Params)
    if CorpusTriples == False:
        return
    TMXTriples = tmx_file_to_word_triples(TMXFile, SourceLang, TargetLang, Params)
    if TMXTriples == False:
        return
    TMXSegmentedCorpusTriples = add_tmx_segmentation_to_word_triples(CorpusTriples, TMXTriples)
    make_tmx_segmented_corpus_file(TMXSegmentedCorpusTriples, TMXSegmentedCorpusFile)
    make_tmx_segment_translations_csv(TMXSegmentedCorpusTriples, TranslationsCSV, Params)

#---------------------------------

def get_word_triples_for_corpus(Label, Params):
    File = Params.source_file
    if File == '':
        lara_utils.print_and_flush(f'*** Error: source_file is not defined in config file')
        return False
    Text = lara_partitioned_text_files.extract_from_partitioned_file(File, Label)
    return False if Text == False else string_to_word_triples(Text, Params)

def tmx_file_to_word_triples(TMXFile, SourceLang, TargetLang, Params):
    Extension = lara_utils.extension_for_file(TMXFile)
    if Extension == 'tmx':
        TmpJSONFile = lara_utils.get_tmp_json_file(Params)
        lara_tmx.convert_tmx_to_json(TMXFile, SourceLang, TargetLang, TmpJSONFile)
        TMXContent = lara_utils.read_json_file(TmpJSONFile)
    elif Extension == 'json':
        TMXContent = lara_utils.read_json_file(TMXFile)
    else:
        lara_utils.print_and_flush(f'*** Error: extension of TMX file {TMXFile} is neither "tmx" nor "json"')
        return False
    return [ { 'source': Item['source'],
               'target': Item['target'],
               'source_triples': string_to_word_triples(Item['source'], Params) }
             for Item in TMXContent ]

def string_to_word_triples(Str, Params):
    ( Pairs, Errors ) = lara_split_and_clean.string_to_annotated_words(Str)
    if Errors != []:
        return False
    return pairs_to_word_triples(Pairs, Params)

def pairs_to_word_triples(Pairs, Params):
    return [ pair_to_word_triple(Pair, Params) for Pair in Pairs ]

def pair_to_word_triple(Pair, Params):
    ( Surface, Lemma ) = Pair
    Regularised = regularise_for_word_triple(Surface, Params)
    return ( Regularised, Surface, Lemma )

def regularise_for_word_triple(Str, Params):
    Str1 = lara_parse_utils.remove_hashtag_comment_and_html_annotations(Str, Params)[0].replace('|', '')
    return lara_parse_utils.regularise_spaces(Str1.replace('\n', ' '))

#---------------------------------

def add_tmx_segmentation_to_word_triples(CorpusTriples, TMXTriplesList):
    ( RemainingTriples, Out ) = ( CorpusTriples, [] )
    for TMXTriplesItem in TMXTriplesList:
        ( Source, Target, TMXTriples ) = ( TMXTriplesItem['source'], TMXTriplesItem['target'], TMXTriplesItem['source_triples'] )
        Result = match_tmx_triples_against_corpus_triples(TMXTriples, RemainingTriples)
        if Result == False:
            report_failed_tmx_match(Source, TMXTriples, RemainingTriples)
            return False
        ( SkippedTriples, MatchedTriples, RemainingTriples ) = Result
        #lara_utils.print_and_flush(f'--- Skipped: {SkippedTriples}')
        #lara_utils.print_and_flush(f'--- Matched: {MatchedTriples}')
        #lara_utils.print_and_flush(f'--- Remain: {RemainingTriples[:100]}')
        if SkippedTriples == []:
            Out += [ { 'source_triples': MatchedTriples, 'target': Target } ]
        else:
            Out += [ { 'source_triples': SkippedTriples, 'target': '' },
                     { 'source_triples': MatchedTriples, 'target': Target } ]
    return Out

def match_tmx_triples_against_corpus_triples(TMXTriples, CorpusTriples):
    ( SkippedTriples, RemainingTriples ) = ( [], CorpusTriples )
    while True:
        if len(RemainingTriples) == 0 or len(SkippedTriples) > 100:
            return False
        Result = plain_match_tmx_triples_against_corpus_triples(TMXTriples, RemainingTriples)
        if Result == False:
            SkippedTriples += [ RemainingTriples[0] ]
            RemainingTriples = RemainingTriples[1:]
        else:
            ( MatchedTriples, RemainingTriples ) = Result
            return ( SkippedTriples, MatchedTriples, RemainingTriples )

# It can easily happen that punctuation marks etc don't match and we assume we can handle this.
# If words don't match then we can't so easily recover.
def plain_match_tmx_triples_against_corpus_triples(TMXTriples, TextTriples):
    ( TMXIndex, TextIndex, TMXLen, TextLen ) = ( 0, 0, len(TMXTriples), len(TextTriples) )
    while True:
        if TMXIndex >= TMXLen or TextIndex >= TextLen:
            return ( TextTriples[:TextIndex], TextTriples[TextIndex:] )
        ( TMXTriple,  TextTriple ) = ( TMXTriples[TMXIndex], TextTriples[TextIndex] )
        # Same or two different non-words, continue
        if TMXTriple[0] == TextTriple[0] or ( TMXTriple[2] == '' and TextTriple[2] == '' ):
            TMXIndex += 1
            TextIndex += 1
        # Different and they are both words. Give up and notify if several words have already been matched
        elif TMXTriple[2] != '' and TextTriple[2] != '':
            if TMXIndex > 2:
                lara_utils.print_and_flush(f'--- Match failed at TMXIndex = {TMXIndex}, TextIndex = {TextIndex}, {TMXTriple} versus {TextTriple}')
            return False
        # Different and TMX is not a word. Skip it
        elif TMXTriple[2] == '':
            TMXIndex += 1
        # Different and Text is not a word. Skip it
        elif TextTriple[2] == '':
            TextIndex += 1
        else:
            lara_utils.print_and_flush(f'--- Undefined match: TMXIndex = {TMXIndex}, TextIndex = {TextIndex}, {TMXTriple} versus {TextTriple}')
            return False

def report_failed_tmx_match(Source, TMXTriples, RemainingTriples):
    TruncatedRemainingTriples = RemainingTriples if len(RemainingTriples) <= 100 else RemainingTriples[:100] + ['...']
    lara_utils.print_and_flush(f'*** Error: unable to match "{Source}"')
    lara_utils.print_and_flush(f'*** Error: TMX triples : {TMXTriples}')
    lara_utils.print_and_flush(f'*** Error: text triples: {TruncatedRemainingTriples}')

_TMXSeparator = '//'

def make_tmx_segmented_corpus_file(TMXSegmentedCorpusTriples, TMXSegmentedCorpusFile):
    if TMXSegmentedCorpusTriples == False:
        return
    Text = _TMXSeparator.join([ triples_to_text(Item['source_triples']) for Item in TMXSegmentedCorpusTriples ])
    lara_utils.write_lara_text_file(Text, TMXSegmentedCorpusFile)

def update_audio_alignment_corpus_from_tmx_triples(TMXSegmentedCorpusTriples, Label, Params):
    if TMXSegmentedCorpusTriples == False:
        return
    File = Params.audio_alignment_corpus
    Text = _TMXSeparator.join([ triples_to_text(Item['source_triples']) for Item in TMXSegmentedCorpusTriples ])
    lara_partitioned_text_files.update_partitioned_text_file(File, Label, Text, Params)

def make_tmx_segment_translations_csv(TMXSegmentedCorpusTriples, TranslationsCSV, Params):
    if TMXSegmentedCorpusTriples == False:
        return
    SourceTargetPairs = [ [ lara_split_and_clean.minimal_clean_lara_string(triples_to_text(Item['source_triples']), Params)[0],
                            Item['target'] ]
                          for Item in TMXSegmentedCorpusTriples ]
    Header = ['Segment', 'Translation']
    lara_translations.write_translation_csv(Header, SourceTargetPairs, TranslationsCSV)

def update_segment_translations_csv_from_tmx_triples(TMXSegmentedCorpusTriples, Params):
    File = Params.segment_translation_spreadsheet
    if TMXSegmentedCorpusTriples == False:
        return
    SourceTargetPairs = [ [ lara_split_and_clean.minimal_clean_lara_string(triples_to_text(Item['source_triples']), Params)[0],
                            Item['target'] ]
                          for Item in TMXSegmentedCorpusTriples ]
    Header = ['Segment', 'Translation']
    CurrentSourceTargetPairs = lara_utils.read_lara_csv(File)[1:] if lara_utils.file_exists(File) else []
    UpdatedSourceTargetPairs = update_source_target_pairs(CurrentSourceTargetPairs, SourceTargetPairs)
    lara_translations.write_translation_csv(Header, UpdatedSourceTargetPairs, File)

def update_source_target_pairs(CurrentSourceTargetPairs, SourceTargetPairs):
    Dict = { Source: Target for ( Source, Target ) in CurrentSourceTargetPairs + SourceTargetPairs }
    return [ [ Key, Dict[Key] ] for Key in Dict ]

def triples_to_text(Triples):
    return ''.join([ Triple[1] for Triple in Triples ])

# -------------------------------------------

def check_segment_translations_in_double_aligned_file(DoubleAlignedFile, SegmentTranslationCSV, ConfigFile):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if Params == False:
        return
    SegmentTranslationDict = segment_translation_csv_to_dict(SegmentTranslationCSV)
    Text = lara_utils.read_lara_text_file(DoubleAlignedFile)
    if Text == False:
        return
    TranslationSegments = Text.split('//')
    NMissingTranslations = 0
    for TranslationSegment in TranslationSegments:
        TranslationSegment1 = normalise_double_aligned_text_for_source_translation(TranslationSegment, Params)
        if not TranslationSegment1 in SegmentTranslationDict:
            lara_utils.print_and_flush(f'*** Warning: no translation found for "{TranslationSegment1}"')
            NMissingTranslations += 1
    lara_utils.print_and_flush(f'--- {NMissingTranslations} missing translations')

# -------------------------------------------

def correct_segment_translations_for_double_aligned_file(DoubleAlignedFile, Id, SegmentTranslationCSV, SegmentTranslationCSV1, ConfigFile):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if Params == False:
        return
    correct_segment_translations_for_double_aligned_file1(DoubleAlignedFile, Id, SegmentTranslationCSV, SegmentTranslationCSV1, Params)

def correct_segment_translations_for_double_aligned_from_params(Id, Params):
    if not audio_alignment_corpus_contains_translation_segmention_markers(Params):
        return
    DoubleAlignedFile = Params.double_segmented_corpus if Params.double_segmented_corpus != '' else Params.untagged_corpus
    SegmentTranslationCSV = Params.segment_translation_spreadsheet
    correct_segment_translations_for_double_aligned_file1(DoubleAlignedFile, Id, SegmentTranslationCSV, SegmentTranslationCSV, Params)

def audio_alignment_corpus_contains_translation_segmention_markers(Params):
    AudioAlignmentCorpus = Params.audio_alignment_corpus
    AudioAlignmentText = lara_utils.read_lara_text_file(AudioAlignmentCorpus)
    return '//' in AudioAlignmentText

def correct_segment_translations_for_double_aligned_file1(DoubleAlignedFile, Id, SegmentTranslationCSV, SegmentTranslationCSV1, Params):
    SegmentTranslationDict = segment_translation_csv_to_dict(SegmentTranslationCSV)
    SegmentTranslationDictWords = segment_translation_csv_to_word_based_dict(SegmentTranslationCSV)
    Text = lara_partitioned_text_files.extract_from_partitioned_file(DoubleAlignedFile, Id)
    if Text == False:
        return
    TranslationSegments = Text.split('//')
    lara_utils.print_and_flush(f'--- Found {len(TranslationSegments)} translation segments in partition "{Id}" of {DoubleAlignedFile}')
    SegmentTranslationCSVDictOut = SegmentTranslationDict
    ( NMissingTranslations, NCorrectedTranslations ) = ( 0, 0 )
    for TranslationSegment in TranslationSegments:
        TranslationSegment1 = normalise_double_aligned_text_for_source_translation(TranslationSegment, Params)
        if not TranslationSegment1 in SegmentTranslationDict and not trivial_normalised_component(TranslationSegment1):
            lara_utils.print_and_flush(f'*** Warning: no translation found for "{TranslationSegment1}"')
            NMissingTranslations += 1
            TranslationSegment1Words = text_to_just_words(TranslationSegment1)
            if TranslationSegment1Words in SegmentTranslationDictWords:
                OriginalSource = SegmentTranslationDictWords[TranslationSegment1Words]['original_source']
                Translation = SegmentTranslationDictWords[TranslationSegment1Words]['translation']
                lara_utils.print_and_flush(f'--- Using translation for "{OriginalSource}"')
                SegmentTranslationCSVDictOut[TranslationSegment1] = Translation
                NCorrectedTranslations += 1
    lara_utils.print_and_flush(f'--- {NMissingTranslations} missing translations, {NCorrectedTranslations} corrected')
    Lines = [ [ Key, SegmentTranslationCSVDictOut[Key] ] for Key in SegmentTranslationCSVDictOut.keys() ]
    Header = [ 'Source', 'Translation' ]
    lara_utils.write_lara_csv( [ Header ] + Lines, SegmentTranslationCSV1)
    lara_utils.print_and_flush(f'--- Written corrected segment translation CSV ({len(Lines)} lines) {SegmentTranslationCSV1}')
    
#
# -------------------------------------------

def make_corpus_audio_and_translations_for_double_aligned_file(DoubleAlignedFile, SegmentTranslationCSV, ConfigFile, Id):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if not check_params_for_make_corpus_audio_and_translations_for_double_aligned_file(Params):
        return
    make_corpus_audio_and_translations_for_double_aligned_file1(DoubleAlignedFile, SegmentTranslationCSV, Params, Id)

def make_corpus_audio_and_translations_for_double_aligned_file_from_config(ConfigFile, Id):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if not check_params_for_make_corpus_audio_and_translations_for_double_aligned_file(Params):
        return
    DoubleAlignedFile = Params.double_segmented_corpus 
    SegmentTranslationCSV = Params.segment_translation_spreadsheet
    make_corpus_audio_and_translations_for_double_aligned_file1(DoubleAlignedFile, SegmentTranslationCSV, Params, Id)

def make_corpus_audio_and_translations_for_double_aligned_file1(DoubleAlignedFile, SegmentTranslationCSV, Params, Id):
    SegmentAudioDir = Params.segment_audio_directory
    SegmentTranslationDict = segment_translation_csv_to_dict(SegmentTranslationCSV)
    SegmentAudioMultiDict = segment_audio_dir_to_multi_dict(SegmentAudioDir)
    # Segment boundaries are coherent when we get a || and a // together. Normalise the order.
    Text0 = lara_partitioned_text_files.extract_from_partitioned_file(DoubleAlignedFile, Id)
    Text = Text0.replace('//||', '||//')
    CoherentSegments = Text.split('||//')
    lara_utils.print_and_flush(f'--- Found {len(CoherentSegments)} merged segments')
    ( CoherentSegments1, TranslationPairs, AudioMergeSpecs ) = ( [], [], [] )
    for CoherentSegment in CoherentSegments:
        CoherentSegments1 += [ remove_segmentation_marks_from_coherent_segment(CoherentSegment) ]
        TranslationPairs += [ coherent_segment_to_translation_pair(CoherentSegment, SegmentTranslationDict, Params) ]
        AudioMergeSpecs += [ coherent_segment_to_audio_merge_spec(CoherentSegment, SegmentAudioMultiDict, Params) ]
    if False in TranslationPairs or False in AudioMergeSpecs:
        return
    #make_segmented_corpus(CoherentSegments1, Params)
    update_segmented_corpus(CoherentSegments1, Params, Id)
    add_translation_pairs_to_translation_csv(TranslationPairs, SegmentTranslationCSV)
    make_merged_audio(AudioMergeSpecs, SegmentAudioDir, Params)

def check_params_for_make_corpus_audio_and_translations_for_double_aligned_file(Params):
    if Params == False:
        return False
    if Params.untagged_corpus == '':
        lara_print_and_flush(f'*** Error: untagged_corpus not defined')
        return False
    if Params.segment_audio_directory == '':
        lara_print_and_flush(f'*** Error: untagged_corpus not defined')
        return False
    if not lara_utils.directory_exists(Params.segment_audio_directory):
        lara_print_and_flush(f'*** Error: segment_audio_directory {Params.segment_audio_directory} not found')
        return False
    return True

def remove_segmentation_marks_from_coherent_segment(Str):
    return Str.replace('||', '').replace('//', '')

def coherent_segment_to_translation_pair(Str, SegmentTranslationDict, Params):
    Components = Str.split('//')
    ( SourceList, TargetList ) = ( [], [] )
    for Component in Components:
        NormalisedComponent = normalise_double_aligned_text_for_source_translation(Component, Params)
        if not trivial_normalised_component(NormalisedComponent):
            if not NormalisedComponent in SegmentTranslationDict:
                lara_utils.print_and_flush(f'*** Error: no translation found for "{NormalisedComponent}"')
                Translation = False
            else:
                Translation = SegmentTranslationDict[NormalisedComponent]
            SourceList += [ Component ]
            TargetList += [ Translation ]
    NormalisedCombinedSource = normalise_double_aligned_text_for_source_translation(''.join(SourceList), Params)
    return False if False in TargetList else ( NormalisedCombinedSource, ' '.join(TargetList) )

def coherent_segment_to_audio_merge_spec(Str, SegmentAudioMultiDict, Params):
    Components = Str.split('||')
    ( TextList, AudioFilesList ) = ( [], [] )
    for Component in Components:
        NormalisedComponent = normalise_double_aligned_text_for_audio(Component, Params)
        if not trivial_normalised_component(NormalisedComponent):
            if not NormalisedComponent in SegmentAudioMultiDict:
                lara_utils.print_and_flush(f'*** Error: no audio found for "{NormalisedComponent}"')
                AudioFiles = False
            else:
                AudioFiles = SegmentAudioMultiDict[NormalisedComponent]
            TextList += [ Component ]
            AudioFilesList += [ AudioFiles ]
    AudioFilesList1 = find_consistent_audio_file_list(AudioFilesList)
    NormalisedCombinedText = normalise_double_aligned_text_for_audio(''.join(TextList), Params)
    return False if False in AudioFilesList1 else { 'text': NormalisedCombinedText,
                                                    'audio_files': AudioFilesList1 }

def find_consistent_audio_file_list(AudioFilesList):
    if len([ Item for Item in AudioFilesList if len(Item) != 1 ]) == 0:
        # There's only one choice in each group, so just pick it
        return [ Item[0] for Item in AudioFilesList ]
    return find_consistent_audio_file_list_nontrivial(AudioFilesList)

def find_consistent_audio_file_list_nontrivial(AudioFilesList):
    lara_utils.print_and_flush(f'find_consistent_audio_file_list_nontrivial({AudioFilesList})')
    AnnotatedAudioFiles = [ [ parse_audio_file_name(AudioFile) for AudioFile in AudioFiles ]
                            for AudioFiles in AudioFilesList ]
    if False in AnnotatedAudioFiles:
        return False
    Result = audio_file_list_consistent_with_previous_choice(AnnotatedAudioFiles, False)
    if Result == False:
        lara_utils.print_and_flush(f'*** Error: unable to find consistent set of files in:')
        lara_utils.prettyprint(AudioFilesList)
    return Result

def audio_file_list_consistent_with_previous_choice(AnnotatedAudioFiles, PreviousChoice):
    if AnnotatedAudioFiles == []:
        return []
    ( CurrentChoices, Rest ) = ( AnnotatedAudioFiles[0], AnnotatedAudioFiles[1:] )
    for Choice in CurrentChoices:
        if consecutive_audio_files(PreviousChoice, Choice):
            ThisAudioFile = Choice['name']
            RestAudioFiles = audio_file_list_consistent_with_previous_choice(AnnotatedAudioFiles[1:], Choice)
            if RestAudioFiles != False:
                return [ ThisAudioFile ] + RestAudioFiles
    return False

def consecutive_audio_files(PreviousChoice, Choice):
    if PreviousChoice == False:
        return True
    else:
        return Choice['id'] == PreviousChoice['id'] and Choice['number'] == PreviousChoice['number'] + 1

# extracted_file_ch1_12.mp3
def parse_audio_file_name(AudioFile):
    Match = re.search("extracted_file_(.*)_([0-9]+).mp3", AudioFile)
    if Match == None:
        lara_utils.print_and_flush(f'*** Error: unable to parse "{AudioFile}" as name of audio file')
        return False
    Id = Match.group(1)
    Number = int(Match.group(2))
    return { 'name': AudioFile, 'id': Id, 'number': Number }

def trivial_normalised_component(Str):
    return Str.isspace() or Str == ''

def add_translation_pairs_to_translation_csv(NewPairs, SegmentTranslationCSV):
    OldPairs = lara_utils.read_lara_csv(SegmentTranslationCSV)
    AllPairs = OldPairs + NewPairs
    AllPairs1 = lara_utils.remove_duplicates_general(AllPairs)
    lara_utils.write_lara_csv(AllPairs1, SegmentTranslationCSV)

def update_segmented_corpus(CoherentSegments, Params, Id):
    SegmentedCorpusFile = Params.untagged_corpus
    Text = '||'.join(CoherentSegments) + '||'
    #lara_utils.write_lara_text_file(Text, SegmentedCorpusFile)
    lara_partitioned_text_files.update_partitioned_text_file(SegmentedCorpusFile, Id, Text, Params)

def make_merged_audio(AudioMergeSpecs, SegmentAudioDir, Params):
    NewMetadataItems = []
    for AudioMergeSpec in AudioMergeSpecs:
        MetadataItem = execute_audio_merge_spec(AudioMergeSpec, SegmentAudioDir, Params)
        if MetadataItem != 'trivial':
            NewMetadataItems += [ MetadataItem ]
    if not False in NewMetadataItems:
        add_audio_metadata_to_segment_dir(NewMetadataItems, SegmentAudioDir, Params)

def execute_audio_merge_spec(AudioMergeSpec, SegmentAudioDir, Params):
    if not isinstance(AudioMergeSpec, dict) and 'text' in AudioMergeSpec and 'audio_files' in AudioMergeSpec:
        lara_utils.print_and_flush(f'*** Error: bad audio merge spec: {AudioMergeSpec}')
        return False
    ( Text, AudioFileList ) = ( AudioMergeSpec['text'], AudioMergeSpec['audio_files'] )
    if len(AudioFileList) <= 1:
        return 'trivial'
    NewAudioFileShort = make_merged_audio_file_name_short(AudioFileList)
    NewAudioFile = make_merged_audio_file_name(AudioFileList, SegmentAudioDir)
    ListFile = make_merged_audio_list_file_name(AudioFileList, SegmentAudioDir)
    try:
        lara_utils.print_and_flush(f'--- Making merged audio file {NewAudioFile}')
        lara_utils.delete_file_if_it_exists(NewAudioFile)
        write_audio_files_to_list_file(AudioFileList, ListFile, SegmentAudioDir)
        AbsNewAudioFile = lara_utils.absolute_file_name(NewAudioFile)
        AbsListFile = lara_utils.absolute_file_name(ListFile)
        Command = f'ffmpeg -f concat -safe 0 -i {AbsListFile} -c copy {AbsNewAudioFile}'
        Result = lara_utils.execute_lara_os_call_direct(Command)
        return { 'text': Text, 'file': NewAudioFileShort }
    except Exception as e:
        lara_utils.print_and_flush(f'*** Warning: something went wrong when making merged audio file"')
        lara_utils.print_and_flush(str(e))
        return False

def write_audio_files_to_list_file(AudioFileList, ListFile, SegmentAudioDir):
    Lines = []
    for File in AudioFileList:
        if not lara_utils.file_exists(f'{SegmentAudioDir}/{File}'):
            lara_utils.print_and_flush(f'*** Warning: unable to find {SegmentAudioDir}/{File}')
        else:
            Lines += [ f" file '{File}'" ]
    lara_utils.write_lara_text_file('\n'.join(Lines), ListFile)

def make_merged_audio_file_name(AudioFileList, Dir):
    return f'{Dir}/{make_merged_audio_file_name_short(AudioFileList)}'

def make_merged_audio_file_name_short(AudioFileList):
    return f'{AudioFileList[0]}_to_{AudioFileList[-1]}_merged.mp3'

def make_merged_audio_list_file_name(AudioFileList, Dir):
    return f'{Dir}/list_{AudioFileList[0]}_to_{AudioFileList[-1]}.txt'

def add_audio_metadata_to_segment_dir(NewMetadata, SegmentAudioDir, Params):
    OldMetadata = lara_audio.read_ldt_metadata_file(SegmentAudioDir)
    AllMetadata = lara_install_audio_zipfile.clean_audio_metadata(OldMetadata + NewMetadata)
    lara_audio.write_ldt_metadata_file(AllMetadata, SegmentAudioDir)

# -------------------------------------------

def segment_translation_csv_to_dict(SegmentTranslationCSV):
    Tuples0 = lara_utils.read_lara_csv(SegmentTranslationCSV)
    Tuples = Tuples0[1:]
    return { Tuple[0]: Tuple[1] for Tuple in Tuples }

def segment_translation_csv_to_word_based_dict(SegmentTranslationCSV):
    Tuples0 = lara_utils.read_lara_csv(SegmentTranslationCSV)
    Tuples = Tuples0[1:]
    return { text_to_just_words(Tuple[0]): { 'original_source':Tuple[0], 'translation':Tuple[1] } for Tuple in Tuples }

def text_to_just_words(Str):
    Pairs = lara_split_and_clean.string_to_annotated_words(Str)[0]
    return ' '.join([ Pair[0] for Pair in Pairs if Pair[1] != '' ])

def segment_audio_dir_to_dict(Dir):
    Metadata = lara_audio.read_ldt_metadata_file(Dir)
    return { MetadataItem['text']: MetadataItem['file'] for MetadataItem in Metadata }

def segment_audio_dir_to_multi_dict(Dir):
    Metadata = lara_audio.read_ldt_metadata_file(Dir)
    Dict = {}
    for MetadataItem in Metadata:
        ( Text, File ) = ( MetadataItem['text'], MetadataItem['file'] )
        if Text != '':
            CurrentEntry = Dict[Text] if Text in Dict else []
            Dict[Text] = CurrentEntry + [ File ]
    return Dict
    
def normalise_double_aligned_text_for_source_translation(Str, Params):
    return lara_split_and_clean.minimal_clean_lara_string(Str.replace('||', ''), Params)[0]

def normalise_double_aligned_text_for_audio(Str, Params):
    return lara_split_and_clean.minimal_clean_lara_string(Str.replace('//', ''), Params)[0]

def normalise_double_aligned_text_for_audio_keep_double_slashes(Str, Params):
    return lara_split_and_clean.minimal_clean_lara_string(Str, Params)[0]
