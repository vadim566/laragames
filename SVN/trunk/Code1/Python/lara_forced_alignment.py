
import lara_audio
import lara_split_and_clean
import lara_top
import lara_config
import lara_parse_utils
import lara_utils
# Import this only when we need it
# pip install textgrid
# https://github.com/kylebgorman/textgrid
#import textgrid
import wave

##  {
##    "text": "Once upon a time there were four little Rabbits, and their names were-- Flopsy, Mopsy, Cotton-tail, and Peter.",
##    "file": "50768_191122_141252415.wav",
##    "source": ""
##  },

_prosodic_phrase_boundary = '%%'

def test(Id):
    if Id == 'peter_rabbit_lab_files':
        Dir = '$LARA/Content/peter_rabbit/forced_alignment/cathyc'
        ConfigFile = '$LARA/Content/peter_rabbit/corpus/local_config.json'
        format_segment_directory_for_forced_alignment(Dir, ConfigFile)
    elif Id == 'peter_rabbit_check':
        BreakpointsFile = '$LARA/tmp_resources/peter_rabbit_tmp_segment_audio_word_breakpoint_file.csv'
        TextgridDir = '$LARA/Content/peter_rabbit/forced_alignment/cathyc_aligned/cathyc'
        check_compatibility_of_breakpoints_file_with_textgrid_dir(BreakpointsFile, TextgridDir)
    elif Id == 'peter_rabbit_csv':
        BlankBreakpointsFile = '$LARA/tmp_resources/peter_rabbit_tmp_segment_audio_word_breakpoint_file.csv'
        TextgridDir = '$LARA/Content/peter_rabbit/forced_alignment/cathyc_aligned/cathyc'
        BreakpointsFile = '$LARA/tmp_resources/peter_rabbit_tmp_segment_audio_word_breakpoint_file_instantiated.csv'
        instantiate_breakpoints_file_from_textgrid_dir(BlankBreakpointsFile, TextgridDir, BreakpointsFile)
        
    elif Id == 'le_petit_prince_lab_files':
        Dir = '$LARA/Content/le_petit_prince/forced_alignment/hossein'
        ConfigFile = '$LARA/Content/le_petit_prince/corpus/local_config_audio_extraction.json'
        format_segment_directory_for_forced_alignment(Dir, ConfigFile)
    elif Id == 'le_petit_prince_separate_by_framerate':
        Dir = '$LARA/Content/le_petit_prince/forced_alignment/hossein'
        separate_labelled_wavfile_dir_by_framerates(Dir)
    elif Id == 'le_petit_prince_csv':
        BlankBreakpointsFile = '$LARA/tmp_resources/Le_petit_prince_audio_extraction_tmp_segment_audio_word_breakpoint_file.csv'
        TextgridDir = '$LARA/Content/le_petit_prince/forced_alignment/aligned_all'
        BreakpointsFile = '$LARA/tmp_resources/Le_petit_prince_audio_extraction_tmp_segment_audio_word_breakpoint_file_instantiated.csv'
        instantiate_breakpoints_file_from_textgrid_dir(BlankBreakpointsFile, TextgridDir, BreakpointsFile)

    elif Id == 'le_bonheur_lab_files':
        Dir = '$LARA/Content/le_bonheur/forced_alignment/chadi'
        ConfigFile = '$LARA/Content/le_bonheur/corpus/local_config_audio_extraction.json'
        format_segment_directory_for_forced_alignment(Dir, ConfigFile)
    elif Id == 'le_bonheur_separate_by_framerate':
        Dir = '$LARA/Content/le_bonheur/forced_alignment/chadi'
        separate_labelled_wavfile_dir_by_framerates(Dir)
    # bin/mfa_align corpus_directory dictionary_path acoustic_model_path output_directory
    # bin/mfa_align -c $LARA/Content/le_bonheur/forced_alignment/chadi lexica/french_prosodylab_dictionary_extended.txt \
    #   pretrained_models/french_prosodylab.zip $LARA/Content/le_bonheur/forced_alignment/aligned_all/chadi
    elif Id == 'le_bonheur_csv':
        BlankBreakpointsFile = '$LARA/tmp_resources/le_bonheur_audio_extraction_tmp_segment_audio_word_breakpoint_file.csv'
        TextgridDir = '$LARA/Content/le_bonheur/forced_alignment/aligned_all/chadi/chadi'
        BreakpointsFile = '$LARA/tmp_resources/le_bonheur_audio_extraction_tmp_segment_audio_word_breakpoint_file_instantiated.csv'
        instantiate_breakpoints_file_from_textgrid_dir(BlankBreakpointsFile, TextgridDir, BreakpointsFile)
        
    else:
        lara_utils.print_and_flush(f'*** Error: unknown id: {Id}')

def format_segment_directory_for_forced_alignment(Dir, ConfigFile):
    if not lara_utils.directory_exists(Dir):
        lara_utils.print_and_flush(f'*** Error: directory not found: {Dir}')
        return False
    if not store_split_text_versions_of_clean_text(ConfigFile):
        lara_utils.print_and_flush(f'*** Error: unable to store split text for config file: {ConfigFile}')
        return False
    MetadataFile = f'{Dir}/metadata_help.json'
    if not lara_utils.file_exists(MetadataFile):
        lara_utils.print_and_flush(f'*** Error: file not found: {MetadataFile}')
        return False
    Metadata = lara_utils.read_json_file(MetadataFile)
    if not isinstance(Metadata, list):
        lara_utils.print_and_flush(f'*** Error: contents of file not a list: {MetadataFile}')
        return False
    for Record in Metadata:
        if not well_formed_metadata_record(Record):
            lara_utils.print_and_flush(f'*** Error: not a well-formed metadat record: {Record}')
            return False
        ( Text, File ) = ( Record['text'], Record['file'] )
        Text1 = make_clean_text_compatible_with_split_text(Text)
        BaseFile = File.split('.')[0]
        LabFile = f'{Dir}/{BaseFile}.lab'
        lara_utils.write_lara_text_file(Text1, LabFile)
    lara_utils.print_and_flush(f'--- {len(Metadata)} .lab files written to {Dir}')
    return True

_clean_text_to_split_compatible_text = {}

def store_split_text_versions_of_clean_text(ConfigFile):
    global _clean_text_to_split_compatible_text
    _clean_text_to_split_compatible_text = {}
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if not Params:
        return False
    SplitFile = lara_top.lara_tmp_file('split', Params)
    PageOrientedSplitList = lara_split_and_clean.read_split_file(SplitFile, Params)
    for ( PageInfo, SplitList ) in PageOrientedSplitList:
        for Chunk in SplitList:
            ( Raw, MinimalCleaned, Pairs ) = Chunk[:3]
            SplitTextCompatible = ' '.join([ Pair[0] for Pair in Pairs if Pair[1] != '' ])
            _clean_text_to_split_compatible_text[MinimalCleaned] = make_text_canonical_for_lab(SplitTextCompatible)
    lara_utils.print_and_flush(f'--- Stored split-text compatible forms for {len(_clean_text_to_split_compatible_text)} segments')
    return True

_replacements_for_lab_files = { "’": "'",
                                "œ": "oe"
                                }

_replacement_regex = lara_utils.make_multiple_replacement_regex(_replacements_for_lab_files)

def make_text_canonical_for_lab(Str):
    return lara_utils.apply_multiple_replacement_regex(_replacements_for_lab_files, _replacement_regex, Str)
    
def make_clean_text_compatible_with_split_text(Text):
    if not Text in _clean_text_to_split_compatible_text:
        lara_utils.print_and_flush(f'*** Warning: unable to find split-compatible equivalent of "{Text}"')
        return Text
    else:
        return _clean_text_to_split_compatible_text[Text]

def well_formed_metadata_record(Record):
    return isinstance(Record, dict) and 'text' in Record and 'file' in Record

##    $ bin/mfa_align.exe $LARA/Content/peter_rabbit/forced_alignment/cathyc lexica/librispeech-lexicon.txt english $LARA/Content/peter_rabbit/forced_alignment/cathyc_aligned
##    Setting up corpus information...
##    Number of speakers in corpus: 1, average number of utterances per speaker: 39.0
##    Creating dictionary information...
##    Setting up training data...
##    There were words not found in the dictionary. Would you like to abort to fix them? (Y/N)n
##    Calculating MFCCs...
##    Calculating CMVN...
##    Number of speakers in corpus: 1, average number of utterances per speaker: 39.0
##    Done with setup.
##    100%|##########| 2/2 [00:15<00:00,  7.53s/it]
##    Done! Everything took 76.49871897697449 seconds

def textgrid_dir_to_file_word_sequences_dict(Dir):
    if not lara_utils.directory_exists(Dir):
        lara_utils.print_and_flush(f'*** Error: unable to find directory {Dir}')
        return False
    Files = lara_utils.files_with_given_extension_in_directory(Dir, 'textgrid')
    return { lara_utils.change_extension(File, 'mp3'): textgrid_file_to_word_interval_sequence(f'{Dir}/{File}') for \
             File in Files }

def textgrid_file_to_word_interval_sequence(File):
    try:
        import textgrid
    except:
        lara_utils.print_and_flush(f'*** Error: you need to install textgrid. Do "pip install textgrid"')
        return False
    tg = textgrid.TextGrid.fromFile(lara_utils.absolute_file_name(File))
    tg0 = tg[0]
    return [ { 'word': tg0[i].mark, 'fromTime': tg0[i].minTime, 'toTime': tg0[i].maxTime } for \
             i in range(0, len(tg0)) ]

def check_compatibility_of_breakpoints_file_with_textgrid_dir(BreakpointsFile, TextgridDir):
    BreakpointsInfo = lara_audio.read_segment_audio_word_breakpoint_csv(BreakpointsFile)
    TextgridInfo = textgrid_dir_to_file_word_sequences_dict(TextgridDir)
    for ( File, BreakpointWords, Breakpoints ) in BreakpointsInfo:
        if not File in TextgridInfo:
            lara_utils.print_and_flush(f'*** Warning: {File} not listed in TextGrid info ({BreakpointWords}) ')
        else:
            TextgridWordsAndTimes = TextgridInfo[File]
            check_compatibility_of_breakpoints_words_with_textgrid_words(File, BreakpointWords, TextgridWordsAndTimes)

def check_compatibility_of_breakpoints_words_with_textgrid_words(File, BreakpointWords, TextgridWordsAndTimes):
    SplitBreakpointWords = [ SplitComponent for Word in BreakpointWords \
                             for SplitComponent in lara_utils.split_on_multiple_delimiters([' '], Word) ]
    # Remove final *end*
    SplitBreakpointWords1 = SplitBreakpointWords[:-1]
    TextgridWords = [ Record['word'] for Record in TextgridWordsAndTimes if Record['word'] != '' ]
    if len(SplitBreakpointWords1) != len(TextgridWords):
        lara_utils.print_and_flush(f'*** Warning ({File}):')
        lara_utils.print_and_flush(f'*** Breakpoint words = {SplitBreakpointWords1}, {len(SplitBreakpointWords1)} components')
        lara_utils.print_and_flush(f'*** TextGrid words = {TextgridWords}, {len(TextgridWords)} components')

def instantiate_breakpoints_file_from_textgrid_dir(BlankBreakpointsFile, TextgridDir, BreakpointsFile):
    BreakpointsInfo = lara_audio.read_segment_audio_word_breakpoint_csv(BlankBreakpointsFile)
    TextgridInfo = textgrid_dir_to_file_word_sequences_dict(TextgridDir)
    lara_utils.print_and_flush(f'--- Read blank breakpoints file, {len(BreakpointsInfo)} items, {BlankBreakpointsFile}')
    lara_utils.print_and_flush(f'--- Read TextGrid directory, {len(TextgridInfo)} items')
    NewBreakpointsInfo = []
    for ( File, BreakpointWords, Breakpoints ) in BreakpointsInfo:
        if len(Breakpoints) == len(BreakpointWords) and lara_audio.is_numbers_line(Breakpoints):
            InstantiatedBreakpoints = Breakpoints
        elif not File in TextgridInfo:
            lara_utils.print_and_flush(f'*** Warning: {File} not listed in TextGrid info ({BreakpointWords})')
            InstantiatedBreakpoints = Breakpoints
        else:
            TextgridWordsAndTimes0 = TextgridInfo[File]
            TextgridWordsAndTimes = [ Record for Record in TextgridWordsAndTimes0 if Record['word'] != '' ]
            InstantiatedBreakpoints0 = instantiate_breakpoints_from_textgrid_file(File, BreakpointWords, TextgridWordsAndTimes)
            if InstantiatedBreakpoints0 == False:
                TextgridWords = [ Record['word'] for Record in TextgridWordsAndTimes ]
                lara_utils.print_and_flush(f'*** Warning: unable to match {File}:')
                lara_utils.print_and_flush(f'*** LARA words = {BreakpointWords}')
                lara_utils.print_and_flush(f'*** TextGrid words = {TextgridWords}')
                InstantiatedBreakpoints = Breakpoints
            else:
                InstantiatedBreakpoints = InstantiatedBreakpoints0
        NewBreakpointsInfo += [ [File], BreakpointWords, InstantiatedBreakpoints ]
    lara_utils.write_lara_csv(NewBreakpointsInfo, BreakpointsFile)
                             

def instantiate_breakpoints_from_textgrid_file(File, BreakpointWords, TextgridWordsAndTimes):
    NonemptyTextgridRecords = [ Record for Record in TextgridWordsAndTimes if Record['word'] != '' ]
    ( BreakpointI, TextgridI, BreakpointN, TextgridN, Breakpoints, EndT ) = ( 0, 0, len(BreakpointWords), len(NonemptyTextgridRecords), [], 0.0 )
    lara_utils.print_and_flush(f'--- Instantiating {File}, {len(BreakpointWords)} words')
    while True:
        # Shouldn't happen...
        if BreakpointI >= BreakpointN:
            lara_utils.print_and_flush(f'--- Instantiated breakpoints for {File}, {len(Breakpoints)} words')
            return Breakpoints
        CurrentBreakpointWord = BreakpointWords[BreakpointI]
        if CurrentBreakpointWord == '*end*':
            Breakpoints += [ EndT ]
            lara_utils.print_and_flush(f'--- Instantiated breakpoints for {File}, {len(Breakpoints)} words')
            return Breakpoints
        CurrentBreakpointWords = CurrentBreakpointWord.split()
        MatchedRecords = match_words_to_textgrid_records(CurrentBreakpointWords, NonemptyTextgridRecords, TextgridI, TextgridN)
        if MatchedRecords == False:
            lara_utils.print_and_flush(f'*** Warning: unable to match "{CurrentBreakpointWord}"')
            return False
        BreakpointI += 1
        TextgridI += len(MatchedRecords)
        Breakpoints += [ MatchedRecords[0]['fromTime'] ]
        EndT = MatchedRecords[-1]['toTime']
    lara_utils.print_and_flush(f'--- Instantiated breakpoints for {File}, {len(Breakpoints)} words')
    return Breakpoints

def match_words_to_textgrid_records(BreakpointWords, TextgridRecords, TextgridI, TextgridN):
    if BreakpointWords == []:
        return []
    ( First, Rest ) = ( BreakpointWords[0], BreakpointWords[1:] )
    MatchedFirst = match_word_to_textgrid_records(First, TextgridRecords, TextgridI, TextgridN)
    if MatchedFirst == False:
        return False
    MatchedRest = match_words_to_textgrid_records(Rest, TextgridRecords, TextgridI + len(MatchedFirst), TextgridN)
    if MatchedRest == False:
        return False
    return MatchedFirst + MatchedRest

def match_word_to_textgrid_records(Word0, TextgridRecords, TextgridI, TextgridN):
    Word = make_canonical_for_textgrid_match(Word0)
    TextgridWord1 = make_canonical_for_textgrid_match(TextgridRecords[TextgridI]['word'])
    TextgridWord2 = make_canonical_for_textgrid_match(TextgridRecords[TextgridI + 1]['word']) if TextgridI + 1 < TextgridN else False
    # Simplest and most common case: same word in LARA and TextGrid
    if Word == TextgridWord1:
        return [ TextgridRecords[TextgridI] ]
    # 'Cotton-tail' matches '<unk>', 'tail'
    # 'black-currant' matches '<unk>', 'currant'
    elif TextgridWord1 == '<unk>' and TextgridWord2 != False and TextgridWord2 in Word:
        return [ TextgridRecords[TextgridI], TextgridRecords[TextgridI + 1] ]
    elif TextgridWord1 in Word and TextgridWord2 == '<unk>':
        return [ TextgridRecords[TextgridI], TextgridRecords[TextgridI + 1] ]
    # 'bed-time' matches 'bed', 'time'
    elif TextgridWord1 in Word and TextgridWord2 in Word:
        return [ TextgridRecords[TextgridI], TextgridRecords[TextgridI + 1] ]
    # 'table-spoonful' matches '<unk>'
    elif TextgridWord1 == '<unk>' and \
         ( TextgridWord2 == False or \
           ( TextgridWord2 != False and not TextgridWord2 in Word ) ):
        return [ TextgridRecords[TextgridI] ]
    else:
        lara_utils.print_and_flush(f'*** Warning: no match: Word = "{Word}", TextgridWord1 = "{TextgridWord1}", TextgridWord2 = "{TextgridWord2}"')
        return False

def make_canonical_for_textgrid_match(Word):
    Word1 = make_text_canonical_for_lab(Word)
    return lara_parse_utils.remove_final_punctuation_marks(Word1.lower())
    
# --------------------------------------------

def separate_labelled_wavfile_dir_by_framerates(Dir):
    Wavfiles = lara_utils.files_with_given_extension_in_directory(Dir, 'wav')
    Pairs = [ ( File, get_framerate_for_wavfile(f'{Dir}/{File}') ) for File in Wavfiles ]
    DifferentFramerates = lara_utils.remove_duplicates([ Pair[1] for Pair in Pairs ])
    lara_utils.print_and_flush(f'--- Framerates: {DifferentFramerates}')
    if len(DifferentFramerates) == 1:
        lara_utils.print_and_flush(f'--- All files have framerate {DifferentFramerates[0]}, taking no action')
    else:
        for Framerate in DifferentFramerates:
            Subdir = f'{Dir}/framerate_{Framerate}'
            lara_utils.create_directory_deleting_old_if_necessary(Subdir)
            FilesForFramerate = [ Pair[0] for Pair in Pairs if Pair[1] == Framerate ]
            for File in FilesForFramerate:
                LabFile = lara_utils.change_extension(File, 'lab')
                lara_utils.copy_file(f'{Dir}/{File}', f'{Subdir}/{File}')
                if lara_utils.file_exists(f'{Dir}/{LabFile}'):
                    lara_utils.copy_file(f'{Dir}/{LabFile}', f'{Subdir}/{LabFile}')  
            lara_utils.print_and_flush(f'--- Copied {len(FilesForFramerate)} files with framerate {Framerate} to {Subdir}')
            

def check_wavfile_dir_framerates(Dir):
    Wavfiles = lara_utils.files_with_given_extension_in_directory(Dir, 'wav')
    Pairs = [ ( File, get_framerate_for_wavfile(f'{Dir}/{File}') ) for File in Wavfiles ]
    DifferentFramerates = lara_utils.remove_duplicates([ Pair[1] for Pair in Pairs ])
    lara_utils.print_and_flush(f'--- Framerates: {DifferentFramerates}')
    if len(DifferentFramerates) > 1:
        for Framerate in DifferentFramerates:
            FilesForFramerate = [ Pair[0] for Pair in Pairs if Pair[1] == Framerate ]
            lara_utils.print_and_flush(f'--- {len(FilesForFramerate)} files with framerate {Framerate}:')
            #lara_utils.prettyprint(FilesForFramerate)

def get_framerate_for_wavfile(File):
    if not lara_utils.file_exists(File):
        lara_utils.print_and_flush(f'*** Warning: {File} not found')
        return False
    try:
        WaveRead = wave.open(lara_utils.absolute_file_name(File), 'r')
    except:
        lara_utils.print_and_flush(f'*** Warning: unabe to open {File} as wavfile')
        return False
    Framerate = WaveRead.getframerate()
    WaveRead.close()
    return Framerate

# --------------------------------------------

def annotated_word_pairs_to_prosodic_phrase_boundary_index_list(Pairs):
    ( I, Out ) = ( 0, [] )
    for ( Surface, Lemma ) in Pairs:
        if Lemma != '':
            I += 1
        elif string_contains_prosodic_phrase_boundaries(Surface):
            Out += [ I ]
    return Out

def maybe_add_prosodic_boundary_list_to_params(Params, Raw, Pairs):
    if string_contains_prosodic_phrase_boundaries(Raw):
        Boundaries = annotated_word_pairs_to_prosodic_phrase_boundary_index_list(Pairs)
    else:
        Boundaries = []
    #lara_utils.print_and_flush(f'Pairs = {Pairs}, Raw= "{Raw}", Boundaries = {Boundaries}')
    Params.word_audio_prosodic_boundaries = Boundaries

def string_contains_prosodic_phrase_boundaries(Str):
    return Str.find(_prosodic_phrase_boundary) >= 0

def remove_prosodic_phrase_boundaries_from_string(Str):
    return Str.replace(_prosodic_phrase_boundary, '')


    
                         
    
