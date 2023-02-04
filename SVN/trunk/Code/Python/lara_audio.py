
import lara_top
import lara_picturebook
import lara_translations
import lara_split_and_clean
import lara_config
import lara_play_all
import lara_utils
import lara_replace_chars
import lara_drama
import lara_parse_utils
import copy

def count_recorded_files(Params):
    return { 'segments': count_recorded_segments(Params),
             'words': count_recorded_words(Params)
             }

# In general, we might have more than one segment audio directory
def make_recording_file(SplitFile, RecordingFile, NewOrFull, Params):
    if not check_new_or_full_arg(NewOrFull):
        return False
    load_segment_translation_file_if_doing_sign_language(Params)
    read_and_store_ldt_metadata_files(all_segment_audio_dirs(Params), 'segments', Params)
    InList = [ Chunk for ( PageInfo, Chunks ) in lara_split_and_clean.read_split_file_expanding_annotated_images(SplitFile, Params) for Chunk in Chunks ]
    for FileType in [ 'txt', 'json' ]:
        OutList = make_recording_file1(InList, NewOrFull, FileType, Params)
        OutList1 = lara_utils.remove_duplicates_general(OutList) if Params.segment_audio_keep_duplicates == 'no' else OutList
        write_recording_file(OutList1, FileType, RecordingFile)

def count_recorded_segments(Params):
    read_and_store_ldt_metadata_files(all_segment_audio_dirs(Params), 'segments', Params)
    InList = [ Chunk for ( PageInfo, Chunks ) in lara_split_and_clean.read_split_file_expanding_annotated_images(Params.split_file, Params) for Chunk in Chunks ]
    OutList = make_recording_file1(InList, 'full', 'json', Params)
    return count_recorded_and_missing_lines(OutList)

def make_word_recording_file(SplitFile, RecordingFile, NewOrFull, Params):
    if not check_new_or_full_arg(NewOrFull):
        return False
    load_lemma_translation_file_if_doing_sign_language(Params)
    read_and_store_ldt_metadata_files(all_word_audio_dirs(Params), 'word', Params)
    Words = get_words_from_page_oriented_split_list(lara_split_and_clean.read_split_file_expanding_annotated_images(SplitFile, Params), Params)
    for FileType in [ 'txt', 'json' ]:
        OutList = make_word_recording_file1(Words, NewOrFull, FileType, Params)
        write_recording_file(OutList, FileType, RecordingFile)

# If we're doing video annotations for sign languages, we might need to translate the text before recording it
def load_segment_translation_file_if_doing_sign_language(Params):
    if Params.video_annotations_from_translation == 'yes' and Params.segment_translation_spreadsheet != '':
        lara_translations.process_segment_spreadsheet_file('local_files', Params.segment_translation_spreadsheet)

def load_lemma_translation_file_if_doing_sign_language(Params):
    if Params.video_annotations_from_translation == 'yes' and Params.word_translations_on == 'lemma' and Params.translation_spreadsheet != '':
        lara_translations.process_word_spreadsheet_file('local_files', Params.translation_spreadsheet, Params)

def count_recorded_words(Params):
    read_and_store_ldt_metadata_files(all_word_audio_dirs(Params), 'word', Params)
    Words = get_words_from_page_oriented_split_list(lara_split_and_clean.read_split_file_expanding_annotated_images(Params.split_file, Params), Params)
    OutList = make_word_recording_file1(Words, 'full', 'json', Params)
    return count_recorded_and_missing_lines(OutList)

def check_new_or_full_arg(NewOrFull):
    if not NewOrFull in ( 'new_only', 'full' ):
        printf(f'*** Error: illegal argument "NewOrFull" when trying to make recording file, must be "new_only" or "full"')
        return False
    else:
        return True

def all_segment_audio_dirs(Params):
    OwnSegmentDirList = [] if Params.segment_audio_directory == '' else [ Params.segment_audio_directory ]
    return OwnSegmentDirList 

def all_word_audio_dirs(Params):
    OwnDirList = [] if Params.word_audio_directory == '' else [ Params.word_audio_directory ]
    return OwnDirList 

def process_recorded_audio_directory(Params, SplitList, WordsOrSegments):
    AudioDirs = all_segment_audio_dirs(Params) if WordsOrSegments == 'segments' else all_word_audio_dirs(Params)
    WordsDict = { Word: True for Word in get_words_from_page_oriented_split_list(SplitList, Params) }
    read_and_store_ldt_metadata_files(AudioDirs, WordsOrSegments, Params)
    MultimediaDir = lara_utils.get_multimedia_dir_from_params(Params)
    for AudioDir in AudioDirs:
        if lara_utils.directory_exists(AudioDir):
            copy_audio_files(['wav', 'mp3', 'mp4', 'webm'], AudioDir, MultimediaDir, WordsOrSegments, WordsDict, Params)
        else:
            lara_utils.print_and_flush(f'*** Warning: audio directory {AudioDir} not found')
            
def copy_audio_files(Extensions, AudioDir, MultimediaDir, WordsOrSegments, WordsDict, Params):
    if Params.abstract_html in ( 'abstract_html_only', 'plain_via_abstract_html' ):
        lara_utils.print_and_flush(f'--- Producing abstract HTML only, not copying {WordsOrSegments} audio files')
        return
    for Extension in Extensions:
        copy_audio_files_with_extension(Extension, AudioDir, MultimediaDir, WordsOrSegments, WordsDict, Params)

##def copy_audio_files_with_extension(Extension, AudioDir, MultimediaDir, WordsDict, Params):
##    Files = lara_utils.files_with_given_extension_in_directory(AudioDir, Extension)
##    if len(Files) > 0:
##        Command = f'cp {AudioDir}/*.{Extension} {MultimediaDir}'
##        lara_utils.print_and_flush(f'--- Copying {len(Files)} audio files of type "{Extension}" from {AudioDir}... ')
##        Status = lara_utils.execute_lara_os_call(Command, Params)
##        if Status == 0:
##            lara_utils.print_and_flush('--- done')
##        else:
##            lara_utils.print_and_flush(f'*** Warning: Copying of whole directory failed, trying to copy files one at a time')
##            lara_utils.copy_directory_one_file_at_a_time(AudioDir, MultimediaDir, [Extension])

def copy_audio_files_with_extension(Extension, AudioDir, MultimediaDir, WordsOrSegments, WordsDict, Params):
    Files = relevant_files_in_audio_directory(AudioDir, WordsOrSegments, WordsDict, Extension)
    if len(Files) > 0:
        lara_utils.copy_named_files_between_directories(Files, AudioDir, MultimediaDir)

def relevant_files_in_audio_directory(AudioDir, WordsOrSegments, WordsDict, Extension):
    AllFiles = lara_utils.files_with_given_extension_in_directory(AudioDir, Extension)
    # We want to include all the segment audio files - some of them may be embedded audio
    if WordsOrSegments == 'segments':
        return AllFiles
    # But we only take the word audio files for words that occur in the text
    else:
        return [ File for File in AllFiles if File in ldt_words_for_files and ldt_words_for_files[File] in WordsDict ]

# --------------------------------------

def make_recording_file1(Chunks, NewOrFull, FileType, Params):
    #lara_utils.print_and_flush(f'make_recording_file1(<{len(Chunks)} chunks>, {NewOrFull}, {FileType}, Params)')
    if NewOrFull == 'full' and ( FileType == 'txt' or FileType == 'json' and Params.segment_audio_keep_duplicates != 'yes' ):
        return [ recording_file_line_for_chunk(Chunk, [], FileType, Params) for Chunk in Chunks if not null_chunk(Chunk) ]
    elif NewOrFull == 'full' and FileType == 'json' and Params.segment_audio_keep_duplicates == 'yes':
        ( Out, TextSoFar ) = ( [], [] )
        for Chunk in Chunks:
            if not null_chunk(Chunk):
                Next = recording_file_line_for_chunk(Chunk, TextSoFar, FileType, Params)
                ( Out, TextSoFar ) = ( Out + [ Next ], TextSoFar + Next['text'].split() )
        return Out
    else:
        return [ recording_file_line_for_chunk(Chunk, [], FileType, Params) for Chunk in Chunks
                 if not audio_for_chunk_exists(Chunk, Params) and not null_chunk(Chunk) ]

# --------------------------------------

def make_segment_audio_word_breakpoint_csv(SplitFile, BreakpointFile, Params):
    read_and_store_segment_audio_word_breakpoint_csv(Params)
    SegmentAudioToCleanDict = make_segment_audio_to_clean_dict(Params)
    if not isinstance(SegmentAudioToCleanDict, dict):
        return
    CleanToWordsDict = make_clean_to_words_dict(SplitFile, Params)
    OutList = make_segment_audio_word_breakpoint_csv1(SegmentAudioToCleanDict, CleanToWordsDict)
    write_segment_audio_word_breakpoint_csv(OutList, BreakpointFile)

def make_segment_audio_to_clean_dict(Params):
    SegmentDir = Params.segment_audio_directory
    if SegmentDir == '':
        return False
    Metadata = read_ldt_metadata_file(SegmentDir)
    Dict = {}
    for Record in Metadata:
        if isinstance(Record, dict) and 'file' in Record and 'text' in Record:
            Dict[Record['file']] = Record['text']
    return Dict

def make_clean_to_words_dict(SplitFile, Params):
    ChunkList = [ Chunk for ( PageInfo, Chunks ) in lara_split_and_clean.read_split_file_expanding_annotated_images(SplitFile, Params) for Chunk in Chunks ]
    Dict = {}
    for Chunk in ChunkList:
        ( Raw, Cleaned, Pairs ) = Chunk[:3]
        Dict[Cleaned] = [ Pair[0] for Pair in Pairs if Pair[1] != '' ]
    return Dict

def make_segment_audio_word_breakpoint_csv1(SegmentAudioToCleanDict, CleanToWordsDict):
    Out = []
    for File in SegmentAudioToCleanDict:
        Clean = SegmentAudioToCleanDict[File]
        if Clean in CleanToWordsDict:
            Words = CleanToWordsDict[Clean] + [ '*end*' ]
            Breakpoints0 = segment_audio_word_breakpoints_for_file(File)
            Breakpoints = Breakpoints0 if not Breakpoints0 == False else []
            if Breakpoints != [] and len(Words) != len(Breakpoints):
                lara_utils.print_and_flush(f'*** Error: {File} is associated with {len(Words) - 1} words and {len(Breakpoints) - 1} breakpoints')
                return False
            Out += [ [ File ],
                     Words,
                     Breakpoints ]
    return Out
                            
def write_segment_audio_word_breakpoint_csv(OutList, BreakpointFile):
    return lara_utils.write_lara_csv(OutList, BreakpointFile)

segment_audio_word_breakpoints = {}

def segment_audio_word_breakpoints_for_file(File):
    return False if not File in segment_audio_word_breakpoints else segment_audio_word_breakpoints[File]

def read_and_store_segment_audio_word_breakpoint_csv(Params):
    global segment_audio_word_breakpoints
    segment_audio_word_breakpoints = {}
    BreakpointFile = Params.segment_audio_word_breakpoint_csv
    if BreakpointFile == '':
        return False
    Data = read_segment_audio_word_breakpoint_csv(BreakpointFile)
    if Data == False:
        return False
    I = 0
    for ( File, Text, Breakpoints ) in Data:
        if len(Breakpoints) > 0:
            segment_audio_word_breakpoints[File] = Breakpoints
            I += 1
    lara_utils.print_and_flush(f'--- Loaded breakpoints for {I} files from {BreakpointFile}') 
    return True

def read_segment_audio_word_breakpoint_csv(File):
    if not lara_utils.file_exists(File):
        return []
    RawData = lara_utils.read_lara_csv(File)
    if RawData == False:
        return False
    ( Out, I ) = ( [], 0 )
    while len(RawData) > 0:
        if len(RawData) < 3:
            lara_utils.print_and_flush(f'*** Warning: number of lines in {File} not divisible by 3, data may have been lost')
            return Out
        ( FileLine0, Text, Breakpoints0 ) = RawData[:3]
        FileLine = remove_trailing_empty_cells(FileLine0)
        if not len(FileLine) == 1:
            lara_utils.print_and_flush(f'*** Error: file line {I} of {File} not a single file name')
            return False
        Breakpoints = remove_trailing_empty_cells(Breakpoints0)
        if not is_numbers_line(Breakpoints):
            lara_utils.print_and_flush(f'*** Error: breaskpoints line {I + 2} of {File} not an increasing sequence of numbers')
            return False
        BreakpointsAsNumbers = [ lara_utils.safe_string_to_number(X) for X in Breakpoints ]
        Out += [ [ FileLine[0], Text, BreakpointsAsNumbers ] ]
        RawData = RawData[3:]
        I += 3
    return Out

def remove_trailing_empty_cells(Line):
    for I in range(0, len(Line)):
        if line_from_index_on_is_empty(Line, I):
            return Line[:I]
    return Line

def line_from_index_on_is_empty(Line, I):
    for J in range(I, len(Line)):
        cell = Line[J]
        if cell != '' and not cell.isspace():
            return False
    return True

def is_numbers_line(Line):
    Last = False
    for X in Line:
        XAsNumber = lara_utils.safe_string_to_number(X)
        # Unfortunately it turns out that 0 == False
        if XAsNumber == False and isinstance(X, bool):
            lara_utils.print_and_flush(f'*** Error: {X} is not a number')
            return False
        if Last != False and not XAsNumber > Last:
            lara_utils.print_and_flush(f'*** Error: {X} is not greater than {Last}')
            return False
        Last = XAsNumber
    return True

def maybe_add_word_breakpoints_to_params(Params, MinimallyCleaned, Context):
    AudioURL = get_audio_url_for_chunk_or_word(MinimallyCleaned, Context, 'segments', Params)
    File = audio_url_to_base_file(AudioURL)
    if File != False and File in segment_audio_word_breakpoints:
        Breakpoints = segment_audio_word_breakpoints[File]
        Params.segment_audio_for_word_audio = AudioURL
        Params.word_audio_breakpoints = Breakpoints
    else:
        Params.segment_audio_for_word_audio = False
        Params.word_audio_breakpoints = False

def audio_url_to_base_file(AudioURL):
    return False if null_audio_url(AudioURL) else AudioURL.split('/')[-1]
    
def construct_play_sound_call_for_word(AudioURL, Params):
    if params_say_to_play_part_of_segment_audio_for_word(Params):
        AudioURL = Params.segment_audio_for_word_audio
        breakpoints = Params.word_audio_breakpoints
        offset = Params.segment_audio_word_offset
        index = Params.word_token_index
        left = Params.segment_audio_word_window_left
        right = Params.segment_audio_word_window_right
        if left == 'prosodic_phrase' or right == 'prosodic_phrase':
            prosodic_boundaries = Params.word_audio_prosodic_boundaries
            from_index = max( [ 0 ] + [ boundary for boundary in prosodic_boundaries if boundary <= index ] )
            to_index = min( [ len(breakpoints) - 1 ] + [ boundary for boundary in prosodic_boundaries if boundary > index ] )
            #lara_utils.print_and_flush(f'from_index={from_index}, to_index={to_index}')
        else:
            from_index = max(0, index - left)
            to_index = min(len(breakpoints) - 1, index + 1 + right)
            #lara_utils.print_and_flush(f'left = {left}, right={right}, from_index={from_index}, to_index={to_index}')
        from_breakpoint = breakpoints[from_index] + offset
        to_breakpoint = breakpoints[to_index] + offset
        return f'playSoundPart(\'{AudioURL}\', {from_breakpoint}, {to_breakpoint});'
    elif AudioURL != '*no_audio_url*':
        return f'playSound(\'{AudioURL}\');'
    else:
        return ''

def params_say_to_use_extracted_audio(Params):
    return Params.segment_audio_word_breakpoint_csv != '' 

def params_say_to_play_part_of_segment_audio_for_word(Params):
    #print_params_breakpoint_info(Params)
    return Params.word_audio_breakpoints != False and \
           Params.segment_audio_for_word_audio != False and \
           isinstance(Params.word_token_index, int)
                               
def print_params_breakpoint_info(Params):
    lara_utils.print_and_flush(f'Params.word_audio_breakpoints = {Params.word_audio_breakpoints}')
    lara_utils.print_and_flush(f'Params.segment_audio_for_word_audio = {Params.segment_audio_for_word_audio}')
    lara_utils.print_and_flush(f'Params.word_token_index = {Params.word_token_index}')

# --------------------------------------

def null_chunk(Chunk):
    return Chunk[1].isspace() or Chunk[1] == ''
             
def write_recording_file(List, FileType, File):
    if FileType == 'txt':
        List1 = [ Item for Item in List if isinstance(Item, str) and not fake_recording_line(Item) ]
        lara_utils.write_unicode_text_file('\n'.join(List1), File)
        lara_utils.print_and_flush(f'--- Written recording file (txt, {len(List1)} lines) {File}')
    else:
        JSONFile = lara_utils.change_extension(File, 'json')
        List1 = [ Item for Item in List if isinstance(Item, dict) and 'file' in Item and not fake_file(Item['file']) ]
        lara_utils.write_json_to_file(List1, JSONFile)
        lara_utils.print_and_flush(f'--- Written recording file (JSON, {len(List1)} lines) {File}')

def get_words_from_page_oriented_split_list(SplitList, Params):
    AllChunks = [ Chunk for ( PageInfo, Chunks ) in SplitList for Chunk in Chunks ]
    return get_words_from_split_file_contents(AllChunks, Params)

##def get_words_from_split_file_contents(ChunksList, Params):
##    if Params.video_annotations != 'yes' and Params.phonetic_text != 'yes':
##        Words = [ make_word_canonical_for_word_recording_dont_restore_chars(Word)
##                  for Chunk in ChunksList if not lara_picturebook.is_annotated_image_segment(Chunk)
##                  for ( Word, Tag ) in Chunk[2]
##                  if not Tag == '' and not lara_parse_utils.is_punctuation_string(Word) ]
##    else:
##        # If we're doing video recording, we record the lemmas rather than the words
##        # This depends on sign languages not being inflected.
##        # Similarly, in a phonetic text we record the lemmas, which are the phonetic content.
##        Words = [ make_word_canonical_for_word_recording_dont_restore_chars(Tag)
##                  for Chunk in ChunksList if not lara_picturebook.is_annotated_image_segment(Chunk)
##                  for ( Word, Tag ) in Chunk[2]
##                  if not Tag == '' and not lara_parse_utils.is_punctuation_string(Tag) ]
##    return sorted(lara_utils.remove_duplicates(Words))

# If we're doing video recording, we record the lemmas rather than the words
# This depends on sign languages not being inflected.
# Similarly, in a phonetic text we record the lemmas, which are the phonetic content.
def get_words_from_split_file_contents(SegmentList, Params):
    Words = []
    for Segment in SegmentList:
        if lara_picturebook.is_annotated_image_segment(Segment):
            InnerSegmentList = lara_picturebook.annotated_image_segments(Segment)
            Words += get_words_from_split_file_contents(InnerSegmentList, Params)
        else:
            Pairs = Segment[2]
            for ( Word, Tag ) in Pairs:
                if not Tag == '' and not lara_parse_utils.is_punctuation_string(Word):
                    Element = Word if Params.video_annotations != 'yes' and Params.phonetic_text != 'yes' else Tag
                    Words += [ make_word_canonical_for_word_recording_dont_restore_chars(Element) ]
    return sorted(lara_utils.remove_duplicates(Words))

def make_word_canonical_for_word_recording(Word):
    return make_word_canonical_for_word_recording1(Word, True)

def make_word_canonical_for_word_recording_dont_restore_chars(Word):
    return make_word_canonical_for_word_recording1(Word, False)

def make_word_canonical_for_word_recording1(Word, RestoreChars):
    ( WordMinusHTML, Trace ) = lara_parse_utils.remove_html_annotations_from_string(Word)
    if len(Trace) == 0:
        LowercaseWord = WordMinusHTML.lower()
        LowercaseWord1 = LowercaseWord.replace('\n', '')
        LowercaseWord2 = lara_replace_chars.restore_reserved_chars(LowercaseWord1) if RestoreChars else LowercaseWord1
        LowercaseWord3 = lara_parse_utils.remove_weird_characters(LowercaseWord2)
        LowercaseWord4 = lara_parse_utils.remove_initial_and_final_spaces(LowercaseWord3)
        return lara_parse_utils.remove_final_hyphen(LowercaseWord4)
    else:
        lara_utils.print_and_flush('\n'.join(Trace))
        return False   

def make_segment_canonical_for_recording(SegmentOrWord):
    return lara_replace_chars.restore_reserved_chars(lara_parse_utils.remove_weird_characters(SegmentOrWord))

def internalise_text_from_audio_metadata_file(SegmentOrWord):
    return lara_replace_chars.replace_reserved_chars(SegmentOrWord)

def make_word_recording_file1(Words, NewOrFull, FileType, Params):
    if NewOrFull == 'full':
        return [ recording_file_line_for_word(Word, FileType, Params) for Word in Words ]
    else:
        return [ recording_file_line_for_word(Word, FileType, Params) for Word in Words if not audio_for_word_exists(Word) ]

def audio_for_word_exists(Word):
    global ldt_files_for_words
    return True if Word in ldt_files_for_words else False

def ldt_wavfile_for_word(Word, Params):
    global ldt_files_for_words
    return cached_ldt_file_to_base_ldt_file(ldt_files_for_words[Word], Params) if Word in ldt_files_for_words else 'MISSING_FILE'

def cached_ldt_file_to_base_ldt_file(File, Params):
    if lara_utils.looks_like_a_url(File):
        return File
    # The raw LDT files are .webm for signed video annotation, otherwise .wav
    LDTExtension = 'webm' if Params.video_annotations == 'yes' else 'wav'
    return f"help/{lara_utils.change_extension(File.split('/')[-1], LDTExtension)}"

def maybe_add_contexts_to_metadata(Metadata, WordsOrSegments, Params):
    lara_utils.print_and_flush(f'--- Audio: Params.segment_audio_keep_duplicates = {Params.segment_audio_keep_duplicates}')
    if WordsOrSegments != 'segments' or Params.segment_audio_keep_duplicates == 'no':
        return Metadata
    ( Out, TextSoFar ) = ( [], ['*start*'] )
    for Record in Metadata:
        if 'context' in Record:
            Record1 = Record
        else:
            Record1 = copy.copy(Record)
            Record1['context'] = text_so_far_to_context(TextSoFar, Params)
        TextSoFar += Record['text'].split()
        Out += [ Record1 ]
    return Out    

## AudioOutput help any_speaker MISSING_FILE Once upon a time there were four little rabbits.# (no trace info)
## AudioOutput help any_speaker help/190284_190926_163736873.wav rabbit# (no trace info)
def recording_file_line_for_chunk(Chunk, TextSoFar, FileType, Params):
    Text = make_segment_canonical_for_recording(Chunk[1])
    if Params.phonetic_text == 'yes':
        Text = Text.lower()
    Context = text_so_far_to_context(TextSoFar, Params) if Params.segment_audio_keep_duplicates == 'yes' else ''
    FileOrMissing = ldt_wavfile_for_chunk(Chunk, Context, Params)
    if FileType == 'txt':
        return f'AudioOutput help any_speaker {FileOrMissing} {Text}# (no trace info)'
    # For the special case that we're doing translated video annotations
    elif Params.video_annotations == 'yes' and Params.video_annotations_from_translation == 'yes' and \
         Params.segment_translation_spreadsheet != '':
        return { 'source': Text,
                 'text': lara_translations.translation_for_segment_or_null(Text, 'local_files'),
                 'file': '' if FileOrMissing == 'MISSING_FILE' else maybe_remove_help_prefix(FileOrMissing) }
    else:
        return { 'text': Text,
                 'file': '' if FileOrMissing == 'MISSING_FILE' else maybe_remove_help_prefix(FileOrMissing) }

def text_so_far_to_context(TextSoFar, Params):
    if not isinstance(TextSoFar, list):
        lara_utils.print_and_flush(f'*** Error when creating segment recording file: value of TextSoFar, "{str(TextSoFar)[200:]}", is not a list')
        return ''
    else:
        ContextWindow = Params.preceding_context_window
        PrecedingContent = ' '.join(TextSoFar[-1 * ContextWindow:])
        return f'{PrecedingContent}'
 
def recording_file_line_for_word(Word0, FileType, Params):
    Word = lara_replace_chars.restore_reserved_chars(Word0)
    FileOrMissing = ldt_wavfile_for_word(Word0, Params)
    if FileType == 'txt':
        return f'AudioOutput help any_speaker {FileOrMissing} {Word}# (no trace info)'
    # For the special case that we're doing translated video annotations
    elif Params.video_annotations == 'yes' and Params.video_annotations_from_translation == 'yes' and \
         Params.word_translations_on == 'lemma' and Params.translation_spreadsheet != '':                                                                    
        return { 'source': Word,
                 'text': lara_translations.translation_for_word_or_null(Word0, 'local_files', Params),
                 'file': '' if FileOrMissing == 'MISSING_FILE' else maybe_remove_help_prefix(FileOrMissing) }
    else:
        return { 'text': Word,
                 'file': '' if FileOrMissing == 'MISSING_FILE' else maybe_remove_help_prefix(FileOrMissing) }

def maybe_remove_help_prefix(File):
    return File[len('help/'):] if File.startswith('help/') else File

def count_recorded_and_missing_lines(List):
    NMissing = len([ Item for Item in List if is_recording_item_with_missing_file(Item) ])
    NRecorded = len(List) - NMissing
    return { 'recorded': NRecorded, 'not_recorded': NMissing }

def is_recording_item_with_missing_file(Item):
    if not isinstance(Item, dict) or not 'file' in Item:
        lara_utils.print_and_flush(f'*** Error: bad item in recording file list {Item}')
        return True
    return Item['file'] == ''

# -----------------------------------------------

# If video_annotation is set, then the LDT word files are going to be video files

def sign_language_video_for_word(Word, Params):
    if not Params.video_annotations == 'yes':
        return False
    ResultPlain = ldt_file_for_word(Word)
    ResultCanonical = ldt_file_for_word(make_word_canonical_for_word_recording(Word))
    if ResultPlain:
        return ResultPlain
    elif ResultCanonical:
        return ResultCanonical
    else:
        return False

# -----------------------------------------------

ldt_files_for_segments = {}
ldt_files_for_words = {}
ldt_words_for_files = {}
ldt_urls_for_segment_and_corpus = {}
ldt_urls_for_words = {}

def init_stored_downloaded_audio_metadata():
    ldt_urls_for_segment_and_corpus = {}
    ldt_urls_for_words = {}

def no_audio(SegmentsOrWords, Params):
    # This seems logical, but unfortuately it interacts badly with embedded audio using "this segment"
    #if SegmentsOrWords == 'segments' and Params.audio_segments == 'no':
    #    return True
    if SegmentsOrWords == 'words' and Params.audio_mouseover == 'no':
        return True
    CorpusIdTag = lara_utils.get_corpus_id_from_params(Params)
    return no_audio1(CorpusIdTag, SegmentsOrWords)

def no_audio1(CorpusIdTag, SegmentsOrWords):
    global ldt_files_for_segments
    global ldt_files_for_words
    global ldt_urls_for_segment_and_corpus
    global ldt_urls_for_words
    if CorpusIdTag == 'local_files' and SegmentsOrWords == 'segments':
        if ldt_files_for_segments == {}:
            return True
        else:
            return False
    elif CorpusIdTag == 'local_files' and SegmentsOrWords == 'words':
        if ldt_files_for_words == {}:
            return True
        else:
            return False
    elif SegmentsOrWords == 'segments':
        if not CorpusIdTag in ldt_urls_for_segment_and_corpus:
            return True
        else:
            return False
    elif SegmentsOrWords == 'words':
        if ldt_urls_for_words == {}:
            return True
        else:
            return False
    else:
        return True

def ldt_file_for_segment(Segment, Context, Params):
    global ldt_files_for_segments
    if Segment in ldt_files_for_segments:
        AudioRecords = ldt_files_for_segments[Segment] 
        File = best_segment_file_for_context(AudioRecords, Context, Params)
        if not File:
            warn_about_missing_segment_audio(Segment, Params)
            return False
        else:
            return File
    else:
        warn_about_missing_segment_audio(Segment, Params)
        return False

def warn_about_missing_segment_audio(Segment, Params):
    if not Params.audio_segment_warnings == 'no' and not lara_drama.is_non_spoken_line(Segment, Params):
        Error = f'*** Warning: No audio file stored for segment "{Segment}"'
        lara_utils.print_and_flush_warning(Error)
    

def ldt_file_for_word(Word):
    global ldt_files_for_words
    if Word in ldt_files_for_words:
        return ldt_files_for_words[Word]
    else:
        Error = f'*** Warning: No audio file stored for word "{Word}"'
        lara_utils.print_and_flush_warning(Error)
        return False

def audio_for_chunk_exists(Chunk, Params):
    global ldt_files_for_segments
    Text = audio_text_for_chunk(Chunk, Params)
    return True if Text in ldt_files_for_segments else False

def ldt_wavfile_for_chunk(Chunk, Context, Params):
    global ldt_files_for_segments
    Text = audio_text_for_chunk(Chunk, Params)
    if not Text in ldt_files_for_segments:
        return 'MISSING_FILE'
    AudioRecords = ldt_files_for_segments[Text] 
    File0 = best_segment_file_for_context(AudioRecords, Context, Params)
    return cached_ldt_file_to_base_ldt_file(File0, Params) if File0 != False else 'MISSING_FILE'

def audio_text_for_chunk(Chunk, Params):
    return Chunk[1] if Params.phonetic_text != 'yes' else Chunk[1].lower()

# -----------------------------------------------

def read_and_store_ldt_metadata_files(LDTDirs, WordsOrSegments, Params):
    global ldt_files_for_segments
    global ldt_files_for_words
    if WordsOrSegments == 'segments':
        ldt_files_for_segments = {}
    else:
        ldt_files_for_words = {}
        ldt_words_for_files = {}
    for LDTDir in LDTDirs:
        List = read_ldt_metadata_file(LDTDir)
        store_ldt_metadata_file1(List, WordsOrSegments, Params)

def read_ldt_metadata_file(LDTDir):
    LDTJSONMetadataFile = ldt_json_metadata_file(LDTDir)
    LDTTextMetadataFile = ldt_text_metadata_file(LDTDir)
    if lara_utils.file_exists(LDTJSONMetadataFile):
        Data = read_named_ldt_metadata_file(LDTJSONMetadataFile)
        lara_utils.print_and_flush(f'--- Read audio metadata from {LDTJSONMetadataFile} ({len(Data)} records).')
        return Data
    elif lara_utils.file_exists(LDTTextMetadataFile):
        Data = read_named_ldt_metadata_file(LDTTextMetadataFile)
        lara_utils.print_and_flush(f'--- Read audio metadata from {LDTTextMetadataFile} ({len(Data)} records).')
        return Data
    else:
        lara_utils.print_and_flush(f'*** Warning: cannot find either {LDTJSONMetadataFile} or {LDTTextMetadataFile}.')
        return []

def read_named_ldt_metadata_file(File):
    Extension = lara_utils.extension_for_file(File)
    if not Extension in ( 'json', 'txt' ):
        lara_utils.print_and_flush(f'*** Error: audio metadata file {File} does not have a json or txt extension')
        return False
    if Extension == 'json':
        Metadata = lara_utils.read_json_file(File)
    elif Extension == 'txt':
        Text = lara_utils.read_lara_text_file(File)
        if not Text:
            return False
        else:
            Lines = Text.split('\n')
            Metadata = [ ldt_text_metadata_line_to_dict(Line) for Line in Lines ]
    return [ Item for Item in Metadata if isinstance(Item, dict) and 'file' in Item and not fake_file(Item['file']) ]

def ldt_metadata_file(LDTDir):
    return ldt_text_metadata_file(LDTDir)
                  
def ldt_text_metadata_file(LDTDir):
    return f'{LDTDir}/metadata_help.txt'

def ldt_json_metadata_file(LDTDir):
    return f'{LDTDir}/metadata_help.json'

def ldt_text_metadata_line_to_dict(Line):
    ParsedLine = lara_parse_utils.parse_ldt_metadata_file_line(Line)
    if not ParsedLine:
        return False
    else:
        ( File, SegmentOrWord ) = ParsedLine
        return { 'file': File, 'text': SegmentOrWord }

##  {
##    "text": "folkvíg",
##    "file": "469759_200302_154111290.wav"
##  },

def store_ldt_metadata_file1(ParsedLineList, WordsOrSegments, Params):
    for ParsedLine in ParsedLineList:
        store_ldt_metadata_file_parsed_line(ParsedLine, WordsOrSegments, Params)

def store_ldt_metadata_file_parsed_line(ParsedLine, WordsOrSegments, Params):
    global ldt_files_for_segments
    global ldt_files_for_words
    if ParsedLine and isinstance(ParsedLine, dict) and \
       'text' in ParsedLine and ParsedLine['text'] != '' and not ParsedLine['text'].isspace() and \
       'file' in ParsedLine and ParsedLine['file'] != '' and not fake_file(ParsedLine['file']):
        File = ParsedLine['file']
        # We've recorded signed video from a translated language
        if 'source' in ParsedLine and ParsedLine['source'] != None and Params.video_annotations_from_translation == 'yes':
            SegmentOrWord = ParsedLine['source']
        else:
            SegmentOrWord = ParsedLine['text']
        Context = ParsedLine['context'] if 'context' in ParsedLine else ''
        File1 = File if lara_utils.looks_like_a_url(File) else f'{lara_utils.relative_multimedia_dir(Params)}/{File}'
        SegmentOrWord1 = internalise_text_from_audio_metadata_file(SegmentOrWord)
        if WordsOrSegments == 'segments':
            #ldt_files_for_segments[make_segment_canonical_for_recording(SegmentOrWord)] = File1
            if not SegmentOrWord1 in ldt_files_for_segments:
                ldt_files_for_segments[SegmentOrWord1] = []
            Record = { 'file': File1, 'context': Context } 
            ldt_files_for_segments[SegmentOrWord1] = ldt_files_for_segments[SegmentOrWord1] + [ Record ]
        else:
            ldt_files_for_words[SegmentOrWord1] = File1
            ldt_words_for_files[File] = SegmentOrWord1

def store_downloaded_audio_metadata(WordsOrSegments, Voice, CorpusId, URL, File):
    global ldt_urls_for_segment_and_corpus
    Params = lara_config.default_params()
    if not lara_utils.file_exists(File):
        lara_utils.print_and_flush(f'*** Warning: LDT metadata file {File} not found.')
        List = []
    elif not lara_utils.extension_for_file(File) in ( 'txt', 'json' ):
        lara_utils.print_and_flush(f'*** Warning: LDT metadata file {File} not in txt or json format, unable to use.')
        List = []                        
    else: 
        ParsedLines = read_named_ldt_metadata_file(File)
        lara_utils.print_and_flush(f'--- Read LDT metadata file ({len(ParsedLines)} lines) {File}')
    if WordsOrSegments == 'segments':
        if CorpusId in ldt_urls_for_segment_and_corpus:
            SubDict = ldt_urls_for_segment_and_corpus[CorpusId]
        else:
            SubDict = {}
        SubDict['*base_url*'] = URL
        ldt_urls_for_segment_and_corpus[CorpusId] = SubDict
    if WordsOrSegments == 'words':
        for Line in ParsedLines:
            store_downloaded_audio_metadata_line(Line, '', WordsOrSegments, Voice, CorpusId, URL)
    else:
        TextSoFar = []
        for Line in ParsedLines:
            Context = text_so_far_to_context(TextSoFar, Params)
            store_downloaded_audio_metadata_line(Line, Context, WordsOrSegments, Voice, CorpusId, URL)
            TextSoFar += Line['text'].split()

## We will in general have multiple corpora, and we could also have multiple language resources
## We will also have multiple voices
def store_downloaded_audio_metadata_line(ParsedLine, Context, WordsOrSegments, Voice, CorpusId, URL):
    global ldt_urls_for_segment_and_corpus
    global ldt_urls_for_words
    if isinstance(ParsedLine, dict) and 'text' in ParsedLine and 'file' in ParsedLine and ParsedLine['file'] != '':
        ( File, SegmentOrWord ) = ( ParsedLine['file'], ParsedLine['text'] )
        FullURL = f'{URL}/{File}'
        #CanonicalSegmentOrWord = make_segment_canonical_for_recording(SegmentOrWord)
        CanonicalSegmentOrWord = internalise_text_from_audio_metadata_file(SegmentOrWord)
        # We index segment audio by corpus, segment and context
        if WordsOrSegments == 'segments':
            if CorpusId in ldt_urls_for_segment_and_corpus:
                SubDict = ldt_urls_for_segment_and_corpus[CorpusId]
            else:
                SubDict = {}
            if CanonicalSegmentOrWord in SubDict:
                AudioRecords = SubDict[CanonicalSegmentOrWord]
            else:
                AudioRecords = []
            AudioRecords += [ { 'file': FullURL, 'context': Context } ]
            SubDict[CanonicalSegmentOrWord] = AudioRecords
            ldt_urls_for_segment_and_corpus[CorpusId] = SubDict
        # We index word audio by language (i.e. corpusid), word and voice
        else:
            if CorpusId in ldt_urls_for_words:
                SubDict = ldt_urls_for_words[CorpusId]
            else:
                SubDict = {}
            if CanonicalSegmentOrWord in SubDict:
                SubSubDict = SubDict[CanonicalSegmentOrWord]
            else:
                SubSubDict = {}
            SubSubDict[Voice] = FullURL
            SubDict[CanonicalSegmentOrWord] = SubSubDict
            ldt_urls_for_words[CorpusId] = SubDict

def audio_url_for_corpus_id(CorpusId):
    global ldt_urls_for_segment_and_corpus
    if CorpusId in ldt_urls_for_segment_and_corpus and '*base_url*' in ldt_urls_for_segment_and_corpus[CorpusId]:
        return ldt_urls_for_segment_and_corpus[CorpusId]['*base_url*']
    else:
        lara_utils.print_and_flush_warning(f'*** Warning: base audio URL not defined for "{CorpusId}"')
        return ''

def audio_url_for_language_id(LanguageId):
    global ldt_urls_for_words
    if LanguageId in ldt_urls_for_words and '*base_url*' in ldt_urls_for_words[LanguageId]:
        return ldt_urls_for_words[LanguageId]['*base_url*']
    else:
        lara_utils.print_and_flush_warning(f'*** Warning: base audio URL not defined for "{LanguageId}"')
        return ''

def ldt_url_for_segment_and_corpus(Segment, Context, CorpusId, Params):
    global ldt_urls_for_segment_and_corpus
    if CorpusId in ldt_urls_for_segment_and_corpus:
        SubDict = ldt_urls_for_segment_and_corpus[CorpusId]
        if Segment in SubDict:
            return best_segment_file_for_context(SubDict[Segment], Context, Params)
        else:
            Error = f'*** Warning: No audio URL stored for {Segment} in {CorpusId}'
            lara_utils.print_and_flush_warning(Error)
            return Error
    else:
        Error = f'*** Warning: No audio data for {CorpusId}'
        lara_utils.print_and_flush_warning(Error)
        return Error

def ldt_url_for_word(Word, LanguageId, Params):
    global ldt_urls_for_words
    if LanguageId in ldt_urls_for_words:
        SubDict = ldt_urls_for_words[LanguageId]
        if Word in SubDict:
            return best_audio_url_for_word(SubDict[Word], Params)
        else:
            Error = f'*** Warning: No audio URL stored for {Word} in {LanguageId}'
            lara_utils.print_and_flush_warning(Error)
            return Error
    else:
        Error = f'*** Warning: No audio data for {LanguageId}'
        lara_utils.print_and_flush_warning(Error)
        return Error

# We should have a dict of URLs indexed by voice. Use the one for the preferred voice
# if it's there, otherwise just pick one.
def best_audio_url_for_word(SubSubDict, Params):
    if not isinstance(SubSubDict, dict) or SubSubDict == {}:
        return '*** Warning: No audio data'
    Key = Params.preferred_voice if Params.preferred_voice in SubSubDict else next(iter(SubSubDict))
    return SubSubDict[Key]

# We should have a list of <context, file/url> pairs. Use the one with the best-matching context.
def best_segment_file_for_context(AudioRecords, Context, Params):
##    # If there's only one record, or the context is null, use the first record
##    if len(AudioRecords) == 1 or Context == '':
##        return AudioRecords[0]['file']
    # If the context is null because we're not using contexts, return the first record
    if Context == '':
        return AudioRecords[0]['file']
    # If there is a record with the same context, return it.
    for AudioRecord in AudioRecords:
        if AudioRecord['context'] == Context:
            return AudioRecord['file']
    # If we're requiring exact matches, fail
    if Params.segment_audio_exact_context_match == 'yes':
        return False
    # Otherwise, return the record with the closest context.
    Pairs = [ ( AudioRecord['file'], lara_utils.word_edit_distance(AudioRecord['context'], Context) ) for AudioRecord in AudioRecords ]
    return sorted(Pairs, key=lambda x: x[1])[0][0]

# -----------------------------------------------

def write_ldt_metadata_file(Data, Dir):
    File = ldt_json_metadata_file(Dir)
    write_named_ldt_metadata_file(Data, File)

def write_named_ldt_metadata_file(Data, File):
    if not valid_ldt_metadata(Data):
        ShortData = str(Data)[:100]
        lara_utils.print_and_flush(f'*** Error: bad metadata in lara_audio.write_named_ldt_metadata_file: {ShortData}')
        return False
    lara_utils.write_json_to_file(Data, File)

def valid_ldt_metadata(Data):
    if not isinstance(Data, list):
        return False
    for Item in Data:
        if not isinstance(Item, dict) or not 'file' in Item or not 'text' in Item:
            return False
    return True

# -----------------------------------------------    

def add_audio_mouseover_to_word(AnnotatedWord, Word, Params):
    if no_audio('words', Params):
        return AnnotatedWord
    else:
        AudioURL = get_audio_url_for_chunk_or_word(Word, '', 'words', Params)
        #PlaySoundCall = f'playSound(\'{AudioURL}\');'
        PlaySoundCall = construct_play_sound_call_for_word(AudioURL, Params)
        Trigger = 'onclick' if Params.audio_on_click == 'yes' else 'onmouseover'
        if not null_audio_url(AudioURL):
           #return f'<span class="sound" {Trigger}="{PlaySoundCall}" ontouchstart="{PlaySoundCall}">{AnnotatedWord}</span>'
            return f'<span class="sound" {Trigger}="{PlaySoundCall}">{AnnotatedWord}</span>'
        else:
            lara_utils.print_and_flush_warning(f'*** Warning: unable to find audio for "{Word}"')
            return AnnotatedWord

def null_audio_url(AudioURL):
    return AudioURL == '*no_audio_url*' or \
           AudioURL == False or \
           ( isinstance(AudioURL, str) and '/.' in AudioURL )

def get_audio_url_for_word(Word, Params):
    if params_say_to_play_part_of_segment_audio_for_word(Params):
        return '*use_extracted_audio*'
    AudioURL = get_audio_url_for_chunk_or_word(Word, '', 'words', Params)
    if AudioURL != '*no_audio_url*':
        return AudioURL
    else:
        if not no_audio('words', Params):
            lara_utils.print_and_flush_warning(f'*** Warning: unable to find audio for "{Word}"')
        return False

def get_audio_url_for_chunk_or_word(MinimallyCleaned, Context, WordsOrSegments, Params):
    if no_audio(WordsOrSegments, Params):
        return '*no_audio_url*'
    else:
        CorpusId = lara_utils.get_corpus_id_from_params(Params)
        if CorpusId == 'local_files' and WordsOrSegments == 'segments':
            return ldt_file_for_segment(MinimallyCleaned, Context, Params)
        elif CorpusId == 'local_files' and WordsOrSegments == 'words':
            MinimallyCleaned1 = make_word_canonical_for_word_recording_dont_restore_chars(MinimallyCleaned)
            return ldt_file_for_word(MinimallyCleaned1)
        elif WordsOrSegments == 'segments':
            return ldt_url_for_segment_and_corpus(MinimallyCleaned, Context, CorpusId, Params)
        elif WordsOrSegments == 'words':
            MinimallyCleaned1 = make_word_canonical_for_word_recording(MinimallyCleaned)
            LanguageId = lara_utils.get_language_id_from_params(Params)
            return ldt_url_for_word(MinimallyCleaned1, LanguageId, Params)

# -----------------------------------------------

##   <tr><td><audio tracking="yes" src="this segment"/><br/></td><td>/**/</td></tr>
##   <tr><td>/*v.Vsp.1*/</td><td>/**/</td></tr>
##   <tr><td end_time="0">Hljóðs#hljóð# bið#biðja# ek</td><td>/*Hliods bið ec*/</td></tr>
##   <tr><td end_time="3.0">allar#allr# kindir#kind#,</td><td>/*allar kindir*/</td></tr>
##
##   ->
##
##   <tr><td><audio id="audio_1" src="this segment"/><br/></td><td>/**/</td></tr>
##   <tr><td>/*v.Vsp.1*/</td><td>/**/</td></tr>
##   <tr><td class="audio_1_line">Hljóðs#hljóð# bið#biðja# ek</td><td>/*Hliods bið ec*/</td></tr>
##   <tr><td class="audio_1_line">allar#allr# kindir#kind#,</td><td>/*allar kindir*/</td></tr>

def test_extract_audio_tracking_data_from_file():
    InFile = '$LARA/Content/völuspá/corpus/völuspá_audio_tracking_with_timings_imba.txt'
    OutFile = '$LARA/Content/völuspá/corpus/völuspá_audio_tracking_reconstituted_imba.txt'
    AudioTrackingFile = '$LARA/tmp/völuspá_audio_tracking.json'
    Params = lara_config.read_lara_local_config_file('$LARA/Content/völuspá/corpus/local_config_audio_tracking_imba.json')
    extract_audio_tracking_data_from_file(InFile, OutFile, AudioTrackingFile, Params)

def extract_audio_tracking_data_from_file(InFile, OutFile, AudioTrackingFile, Params):
    if not lara_utils.file_exists(InFile):
        lara_utils.print_and_flush(f'*** Error: unable to find {InFile}')
        return 'error'
    InStr = lara_utils.read_lara_text_file(InFile).split('\n')
    ( OutStr, TrackingData, Errors ) = extract_audio_tracking_data_from_string(InStr, Params)
    if len(Errors) > 0:
        for Error in Errors:
            lara_utils.print_and_flush(Error)
        return False
    if len(TrackingData) > 0:
        lara_utils.write_lara_text_file(OutStr, OutFile)
        lara_utils.write_json_to_file(TrackingData, AudioTrackingFile)
        return True
    else:
        return False

def extract_audio_tracking_data_from_string(InStr, Params):
    # Tmp dummy
    #return ( InStr, {}, [] )
    ( CorpusId, Counter, CurrentAudioId, LinesOut, TrackingData ) = ( Params.id, 1, False, [], {} )
    for Line in InStr.split('\n'):
        ( Type, Time, Errors ) = get_audio_tracking_type_for_line(Line)
        if Type == 'error':
            return ( 'error', {}, Errors )
        elif Type == 'audio_with_tracking':
            CurrentAudioId = f'audio_{CorpusId}_{Counter}'
            Counter += 1
            LineOut = Line.replace(f'tracking="yes"', f'id="{CurrentAudioId}"')
        elif Type == 'time':
            if not CurrentAudioId:
                Error = f'*** Error: line contains "end_time" but no preceding audio line with "tracking": "{Line}"' 
                return ( 'error', {}, [ Error ] )
            LineOut = Line.replace(f'end_time="{Time}"', f'class="{CurrentAudioId}_line"')
            CurrentTrackingData = TrackingData[CurrentAudioId] if CurrentAudioId in TrackingData else [ 0.0 ]
            TrackingData[CurrentAudioId] = CurrentTrackingData + [ float(Time) ]
        else:
            LineOut = Line
        LinesOut += [ LineOut ]
    OutStr = '\n'.join(LinesOut)
    if len(TrackingData):
        lara_utils.print_and_flush(f'--- Found {len(TrackingData)} audio files with tracking enabled')
    return ( OutStr, TrackingData, [] )

def get_audio_tracking_type_for_line(Line):
    if Line.find('<audio') >= 0 and Line.find('tracking="yes"') > 0:
        return ( 'audio_with_tracking', False, [] )
    SearchString = 'end_time="'
    if Line.find('<td') >= 0:
        Start = Line.find(SearchString)
        if Start > 0:
            End = Line.find('"', Start + len(SearchString))
            if End > 0:
                Time = Line[Start + len(SearchString):End]
                if not string_is_a_float(Time):
                    Error = f'*** Error: value of "end_time" is not a number: "{Line}"'
                    return ( 'error', False, [ Error ] )
                return ( 'time', Time, [] )
    return ( 'other', False, [] )

def string_is_a_float(Str):
    try:
        Num = float(Str)
        return True
    except:
        return False

def write_audio_tracking_data_to_tmp_resources(AudioTrackingData, Params):
    File =  lara_top.lara_tmp_file('audio_tracking', Params)
    lara_utils.write_json_to_file(AudioTrackingData, File)

def get_audio_tracking_file_from_tmp_resources(Params):
    File = lara_top.lara_tmp_file('audio_tracking', Params)
    return File if lara_utils.file_exists(File) else False                   

# -----------------------------------------------

def process_audio_tags_in_string(RawStr, CleanText, Params):
    if lara_utils.no_corpus_id_in_params(Params):
        return ( RawStr, [], False )
    if lara_utils.get_corpus_id_from_params(Params) == 'local_files' and Params.segment_audio_directory == '':
        return ( RawStr, [], False )
    if Params.segment_audio_directory != '':
        Dir = lara_utils.absolute_file_name(Params.segment_audio_directory)
    else:
        Dir = '*no_dir*'
    return process_audio_tags_in_string1(RawStr, CleanText, Params, Dir)

def audio_files_referenced_in_string(Str):
    audio_tag_start = '<audio'
    audio_tag_end = '/>'
    ( Index, N, audioFiles ) = ( 0, len(Str), [] )
    while True:
        if Index >= N:
            return audioFiles
        if lara_parse_utils.substring_found_at_index(Str, Index, audio_tag_start) > 0:
            EndOfTagIndex = Str.find(audio_tag_end, Index+len(audio_tag_start))
            if EndOfTagIndex > 0:
                ( Components, Errors ) = parse_audio_tag(Str[Index+len(audio_tag_start):EndOfTagIndex])
                Index = EndOfTagIndex + len(audio_tag_end)
                if 'src' in Components and Components['src'] != 'this segment' and Components['src'] != 'this page':
                    audioFiles += [ Components['src'] ]
            else:
                # We have an open audio tag, but try to carry on anyway
                return audioFiles
        else:
            Index += 1

def process_audio_tags_in_string1(Str, CleanText, Params, Dir):
    ThisPageAudioFileUsedAll = False
    if Str.find('<') < 0:
        return ( Str, [], False )
    audio_tag_start = '<audio'
    audio_tag_end = '/>'
    ( Index, N, OutStr, AllErrors ) = ( 0, len(Str), '', [] )
    while True:
        if Index >= N:
            return ( OutStr, AllErrors, ThisPageAudioFileUsedAll )
        if lara_parse_utils.substring_found_at_index(Str, Index, audio_tag_start) > 0:
            EndOfTagIndex = Str.find(audio_tag_end, Index+len(audio_tag_start))
            if EndOfTagIndex > 0:
                ( TagText1, Errors, ThisPageAudioFileUsedNext ) = \
                  process_audio_tag(Str[Index+len(audio_tag_start):EndOfTagIndex], CleanText, Params, Dir)
                OutStr += TagText1
                Index = EndOfTagIndex + len(audio_tag_end)
                AllErrors += Errors
                ThisPageAudioFileUsedAll = ThisPageAudioFileUsedAll or ThisPageAudioFileUsedNext
            else:
                return ( OutStr, [f'*** Error: open audio tag: "{Str[Index:Index+100]}"'], ThisPageAudioFileUsedAll )
        else:
            OutStr += Str[Index]
            Index += 1
                         
def process_audio_tag(TagText, MinimallyCleaned, Params, Dir):
    ( Components, Errors ) = parse_audio_tag(TagText)
    if len(Errors) > 0:
        return ( '', Errors, False )
    else:
        if 'src' in Components:
            if Components['src'].lower() == 'this segment':
                RealURL = get_audio_url_for_chunk_or_word(MinimallyCleaned, '', 'segments', Params)
                if RealURL != False and RealURL != '*no_audio_url*':
                    ( URL, Errors1 ) = ( RealURL, [] )
                elif MinimallyCleaned == '*no_clean_text*':
                    ( URL, Errors1 ) = ( 'no_audio.mp3', [] )
                else:
                    ( URL, Errors1 ) = ( 'no_audio.mp3', [ f'*** Warning: unable to add audio for "{MinimallyCleaned}"' ] )
                ThisPageAudioFileUsedAll = False
            elif Components['src'].lower() == 'this page':
                RealURL = get_audio_url_for_current_page(Params)
                ( URL, Errors1 ) = ( RealURL, [] ) if RealURL != False and RealURL != '*no_audio_url*' else \
                                   ( 'no_audio.mp3', [ f'*** Warning: unable to add audio for page' ] )
                ThisPageAudioFileUsedAll = True
            else:
                ( URL, Errors1 ) = url_for_audio_file_in_tag(Components['src'], Params, Dir)
                ThisPageAudioFileUsedAll = False
            ( AudioType, Errors2 ) = get_audio_type_for_url(URL)
            audio_id = '' if not 'id' in Components else f'id="{Components["id"]}"'
            return ( f'<audio {audio_id} controls="true"><source src="{URL}" type="audio/{AudioType}">Your browser does not support the HTML5 audio element.</audio>',
                     Errors1 + Errors2,
                     ThisPageAudioFileUsedAll
                     )
        else:
            return ( '', [ '*** Error: malformed audio tag "<audio {TagText}/>"' ], False )

def get_audio_url_for_current_page(Params):
    BaseFileName = lara_play_all.base_play_all_audio_file_name_for_current_page(Params)
    return '*no_audio_url*' if BaseFileName == False else f'{lara_utils.relative_multimedia_dir(Params)}/{BaseFileName}'

def url_for_audio_file_in_tag(Src, Params, Dir):
    CorpusId = lara_utils.get_corpus_id_from_params(Params)
    if CorpusId == 'local_files':
        #URL = f'multimedia/{Src}'
        URL = f'{lara_utils.relative_multimedia_dir(Params)}/{Src}'
        return ( URL, check_if_audio_file_exists(Dir, Src) )
    else:
        CorpusAudioURL = audio_url_for_corpus_id(CorpusId)
        if CorpusAudioURL:
            URL = f'{CorpusAudioURL}/{Src}'
            return ( URL, [] )
        # If we are doing distributed LARA and we can't find the audio, create a bad reference
	# to the local multimedia directory and don't interrupt compilation.
        else:
            lara_utils.print_and_flush(f'*** Warning: missing audio file "{Src}"')
            #return ( f'multimedia/{Src}', [] )
            return ( f'{lara_utils.relative_multimedia_dir(Params)}/{Src}', [] )
                        
def check_if_audio_file_exists(Dir, Src):
    if lara_utils.looks_like_a_url(Src):
        return []
    File = f'{Dir}/{Src}'
    if lara_utils.file_exists(File):
        return []
    else:
        return [f'*** Warning: missing audio file "{Src}"']

def get_audio_type_for_url(AudioURL):
    if AudioURL == '*no_audio_url*':
        return ( 'mp3', [] )
    Components = AudioURL.split('.')
    if len(Components) > 1:
        AudioType = Components[-1].lower()
        if known_audio_type_for_audio_tag(AudioType):
            return ( AudioType, [] )
        else:
            return ( AudioType, [ f'*** Error: bad audio URL "{AudioURL}".' ] )
    else:
        return ( False, [ f'*** Error: bad audio URL "{AudioURL}".' ] )

def known_audio_type_for_audio_tag(Type):
    return Type in ['mp3', 'wav']

def is_audio_tag(Str):
    return Str.startswith('<audio') and Str.endswith('/>') 

def audio_tag_to_representation(Str):
    if not is_audio_tag(Str):
        lara_utils.print_and_flush(f'*** Error: bad call to audio_tag_to_representation, "{Str}" is not an img tag')
        return False
    StartIndex = len('<audio') 
    EndIndex = Str.find('/>')
    Str1 = Str[StartIndex:EndIndex]
    ( Representation, Errors ) = parse_audio_tag(Str1)
    if len(Errors) > 0:
        for Error in Errors:
            lara_utils.print_and_flush(Error)
        return False
    else:
        Representation['multimedia'] = 'audio'
        Representation['file'] = Representation['src']
        del Representation['src']
        return Representation

def parse_audio_tag(Str):
    ( Index, N, OutDict ) = ( 0, len(Str), {} )
    while True:
        Index = lara_parse_utils.skip_spaces(Str, Index)
        if Index >= N:
            return ( OutDict, [] )
        else:
            ( Key, Value, Index1, Errors ) = parse_audio_tag_component(Str, Index)
            if len(Errors) > 0:
                return ( OutDict, Errors )
            elif Key:
                OutDict[Key] = Value
                Index = Index1
            elif lara_parse_utils.skip_spaces(Str, Index1) >= N:
                return ( OutDict, [] )
            else:
                return ( OutDict, [ f'*** Error: unknown text in audio tag: "{Str[Index:]}"' ] )
                
def parse_audio_tag_component(Str, Index):
    for Key in [ 'src', 'id', 'tracking' ]:
        if lara_parse_utils.substring_found_at_index(Str, Index, Key + '="'):
            StartOfValueIndex = Index + len(Key) + 2
            EndOfValueIndex = Str.find('"', StartOfValueIndex)
            if EndOfValueIndex >= StartOfValueIndex:
                Value = Str[StartOfValueIndex:EndOfValueIndex]
                return ( Key, Value, EndOfValueIndex + 1, [] )
            else:
                return ( False, False, False, ['*** Error: malformed audio tag "<audio {Str}/>"' ] )
    # We didn't find any key/value pair
    return ( False, False, False, [] )

# -----------------------------------------------

# Create a copy of an audio dir where the files have mnemonic names
def convert_audio_dir_to_mnemonic_audio_dir(Dir, Dir1):
    if not lara_utils.directory_exists(Dir):
        lara_utils.print_and_flush(f'*** Error: unable to find {Dir}')
        return False
    lara_utils.create_directory_deleting_old_if_necessary(Dir1)
    MetadataLines = read_ldt_metadata_file(Dir)
    if not MetadataLines:
        lara_utils.print_and_flush(f'*** Error: unable to find metadata in {Dir}')
        return False
    MetadataItems = [ lara_parse_utils.parse_ldt_metadata_file_line(Line) for Line in MetadataLines ]
    ( PreviousMnemonicBaseFiles, I, NBad, NCopied ) = ( [], 1, 0, 0 )
    for MetadataItem in MetadataItems:
        if MetadataItem and len(MetadataItem) == 2:
            ( File, Text ) = MetadataItem
            File1 = mnemonic_file_name(Text, I, File, PreviousMnemonicBaseFiles)
            PreviousMnemonicBaseFiles += [ lara_utils.file_to_base_file_and_extension(File1)[0] ]
            Result = lara_utils.copy_file(f'{Dir}/{File}', f'{Dir1}/{File1}')
            NCopied += 1
            I += 1
            if not Result:
                lara_utils.print_and_flush(f'*** Warning: unable to copy {File} to {File1}')
                NBad += 1
    lara_utils.print_and_flush(f'--- Copied {NCopied} files, {NBad} failed')

def mnemonic_file_name(Text, I, File, PreviousMnemonicBaseFiles):
    Extension = lara_utils.extension_for_file(File)
    ThreeDigitI = number_to_three_digit_string(I)
    TextNoPunc = lara_parse_utils.remove_punctuation_marks(Text.lower())
    ShortText = ' '.join(TextNoPunc.split()[:7])
    if not ShortText in PreviousMnemonicBaseFiles:
        return f'{ThreeDigitI}_{ShortText}.{Extension}'
    N = 1
    while True:
        ShortTextN = f'{ThreeDigitI}_{ShortText}_{N}'
        if not ShortTextN in PreviousMnemonicBaseFiles:
            return f'{ThreeDigitI}_{ShortTextN}.{Extension}'
        N += 1

def number_to_three_digit_string(I):
    if I < 10:
        return f'00{I}'
    if I < 100:
        return f'0{I}'
    return f'{I}'

# It's possible for various kinds of null values to get into the metadata
def fake_file(File):
    return File == '.wav' or File == '.mp3'

def fake_recording_line(Line):
    return isinstance(Line, str) and ( 'help/.wav' in Line or 'help/.mp3' in Line )


