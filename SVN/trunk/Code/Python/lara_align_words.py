import lara_align_from_audio
import lara_audio
import lara_split_and_clean
import lara_config
import lara_top
import lara_picturebook
import lara_parse_utils
import lara_utils

# Manual alignment of text with audio to extract word audio.
#
#  Inputs to first step (command-line call):
#  
#  1. words to record in JSON form (resources file)
#  
#   {
#       "file": "",
#       "text": "nyakuku"
#   },
#      
#  2. word translations surface type, JSON (resources file)
#  
#   [
#       "nyakuku",
#       "will see",
#       3,
#       [
#           "nyakuku",
#           "minymangku Ingkatjinya nyakuku"
#       ]
#   ],
#      
#  3. sentence audio metadata
#  
#  {
#       "context": "you water. tjitjingkunta mina ungkuku The woman will see Ingkatji.",
#       "file": "extracted_file_ch13_3193.mp3",
#       "text": "minymangku Ingkatjinya nyakuku"
#      },
#
#  4. Split file
#  
#  [
#                  " minyma|ngku Ingkatjinya#Ingkatji# nyakuku#nya#",
#                  "minymangku Ingkatjinya nyakuku",
#                  [
#                      [ " ", "" ],
#                      [ "minyma", "minyma"],
#                      [ "ngku", "ngku" ],
#                      [ " ", "" ],
#                      [ "Ingkatjinya", "Ingkatji" ],
#                      [ " ", "" ],
#                      [ "nyakuku", "nya" ]
#                  ],
#                  "local_files"
#              ],
#  
#  Output:
#  
#  Create file in tmp_resources dir with list of entries like
#  
#  {
#       "audio_file": "$LARA/Content/pitjantjatjara_course/audio/pitjantjatjara_voice/extracted_file_ch13_3193.mp3",
#       "text": "minymangku Ingkatjinya nyakuku",
#  	"label_file": "$LARA/Content/pitjantjatjara_course/corpus/extracted_file_ch13_3193.txt",
#  	"words": [ "minyma", "ngku", "Ingkatjinya", "nyakuku" ],
#       "relevant_word": "nyakuku",
#  	"labelled_text": "|1|minyma|2|ngku|3| |4|Ingkatjinya|5| |6|nyakuku|7|"
#  }
#  
#  Create empty version of label_file for convenience.
#  
#  Manual annotation step follows. Annotator uses Audacity to create label files

def test(Id):
    if Id == 'pitj1':
        ConfigFile = '$LARA/Content/pitjantjatjara_course/corpus/local_config.json'
        make_manual_word_alignment_file(ConfigFile)
    elif Id == 'pitj2':
        ConfigFile = '$LARA/Content/pitjantjatjara_course/corpus/local_config.json'
        extract_word_audio(ConfigFile)
    else:
        lara_utils.print_and_flush(f'*** Error: unknown ID: {Id}')

def make_manual_word_alignment_file(ConfigFile):
    Resources = get_manual_word_alignment_file_resources(ConfigFile)
    if Resources == False:
        return
    make_manual_word_alignment_file_from_resources(Resources)

def make_manual_word_alignment_file_from_resources(Resources):
    WordsToRecord = Resources['words_to_record']
    ExampleSentsDict = Resources['example_sentences_for_words']
    SentAudioFileDict = Resources['audio_files_for_sents']
    SentsToPairsDict = Resources['sents_to_pairs']
    Params = Resources['params']
    Items = []
    for Word in WordsToRecord:
        Item = make_manual_word_alignment_item(Word, ExampleSentsDict, SentAudioFileDict, SentsToPairsDict, Params)
        if Item != False:
            Items += [ Item ]
    create_empty_label_track_files_if_necessary(Items)
    write_out_manual_word_alignment_file(Items, Params)

#  {
#       "audio_file": "$LARA/Content/pitjantjatjara_course/audio/pitjantjatjara_voice/extracted_file_ch13_3193.mp3",
#       "text": "minymangku Ingkatjinya nyakuku",
#  	"label_file": "$LARA/Content/pitjantjatjara_course/corpus/extracted_file_ch13_3193.txt",
#  	"words": [ "minyma", "ngku", "Ingkatjinya", "nyakuku" ],
#  	"labelled_text": "|1|minyma|2|ngku|3| |4|Ingkatjinya|5| |6|nyakuku|7|"
#  }

def make_manual_word_alignment_item(Word, ExampleSentsDict, SentAudioFileDict, SentsToPairsDict, Params):
    if not Word in ExampleSentsDict:
        lara_utils.print_and_flush(f'*** Error: no examples found for {Word}')
        return False
    Examples = ExampleSentsDict[Word]
    UsableExamples = { Example for Example in Examples
                       if Example in SentAudioFileDict and Example in SentsToPairsDict }
    if len(UsableExamples) == 0:
        lara_utils.print_and_flush(f'*** Warning: no examples for "{Word}" have both an associated audio file and a pairs entry. Examples:')
        lara_utils.prettyprint(Examples)
        return False
    ShortestExample = sorted(UsableExamples, key=lambda x: len(x.split()))[0]
    AudioFile = audio_file_for_example(ShortestExample, SentAudioFileDict, Params)
    LabelFile = label_file_for_audio_file(ShortestExample, SentAudioFileDict, Params)
    ( Words, LabelledText, CleanedLabelledText ) = words_and_labelled_text_for_example(ShortestExample, SentsToPairsDict)
    return {  'audio_file': AudioFile,
              'text': CleanedLabelledText,
              'label_file': LabelFile,
              'words': Words,
              'relevant_word': Word,
              'labelled_text': LabelledText
              }

def create_empty_label_track_files_if_necessary(Items):
    for Item in Items:
        File = Item['label_file']
        if not lara_utils.file_exists(File):
            lara_utils.write_lara_text_file('[Placeholder]', File)

def write_out_manual_word_alignment_file(Items, Params):
    File = word_alignment_file(Params)
    if File == False:
        return
    SortedItems = sorted(Items, key=lambda x: x['audio_file'])
    UniqueSortedItems = lara_utils.remove_duplicates_general(SortedItems)
    lara_utils.write_json_to_file_plain_utf8(UniqueSortedItems, File)
    lara_utils.print_and_flush(f'--- Written word alignment file ({len(UniqueSortedItems)} items, {File}')

#       "audio_file": "$LARA/Content/pitjantjatjara_course/audio/pitjantjatjara_voice/extracted_file_ch13_3193.mp3",

def audio_file_for_example(Sent, SentAudioFileDict, Params):
    BaseAudioFile = SentAudioFileDict[Sent]
    Dir = Params.segment_audio_directory
    return f'{Dir}/{BaseAudioFile}'

#  	"label_file": "$LARA/Content/pitjantjatjara_course/corpus/extracted_file_ch13_3193.txt",

def label_file_for_audio_file(Sent, SentAudioFileDict, Params):
    CorpusFile = Params.corpus
    Dir = '/'.join(CorpusFile.split('/')[:-1])
    AudioFile = SentAudioFileDict[Sent]
    BaseFile = lara_utils.change_extension(AudioFile, 'txt')
    return f'{Dir}/LabelTrack_{BaseFile}'

#  	"words": [ "minyma", "ngku", "Ingkatjinya", "nyakuku" ],
#  	"labelled_text": "|1|minyma|2|ngku|3| |4|Ingkatjinya|5| |6|nyakuku|7|"

def words_and_labelled_text_for_example(Example, SentsToPairsDict):
    Pairs = SentsToPairsDict[Example]
    Words = [ Pair[0] for Pair in Pairs if Pair[1] != '' ]
    SegmentedText = ''.join([ Pair[0] if Pair[1] == '' else f'||{Pair[0]}||' for Pair in Pairs ]).replace('||||', '||')
    LabelledText = segmented_text_to_labelled_text(SegmentedText).strip()
    CleanedLabelledText = SegmentedText.strip().replace('||', '')
    return ( Words, LabelledText, CleanedLabelledText )

def segmented_text_to_labelled_text(SegmentedText):
    ( LabelledText, Index, LabelIndex ) = ( '', 0, 1 )
    while True:
        NextSeparatorIndex = SegmentedText.find("||", Index)
        if NextSeparatorIndex < 0:
            return LabelledText + SegmentedText[Index:]
        else:
            LabelledText += ( SegmentedText[Index:NextSeparatorIndex] + f'|{LabelIndex}|' )
            Index = NextSeparatorIndex + len('||')
            LabelIndex += 1
                                   
def get_manual_word_alignment_file_resources(ConfigFile):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if Params == False:
        return
    WordsToRecord = get_words_to_record(Params)
    ExampleSentsDict = get_examples_sents_dict(Params)
    SentAudioFileDict = get_sent_audio_file_dict(Params)
    SentsToPairsDict = get_sents_to_pairs_dict(Params)
    if False in ( WordsToRecord, ExampleSentsDict, SentAudioFileDict ):
        return False
    return { 'words_to_record':WordsToRecord,
             'example_sentences_for_words':ExampleSentsDict,
             'audio_files_for_sents':SentAudioFileDict,
             'sents_to_pairs': SentsToPairsDict,
             'params':Params
             }

#   {
#       "file": "",
#       "text": "nyakuku"
#   },

def get_words_to_record(Params):
    File = lara_top.lara_tmp_file('ldt_word_recording_file_json', Params)
    Data = lara_utils.read_json_file(File)
    return False if Data == False else [ Item['text'] for Item in Data ]

#   [
#       "nyakuku",
#       "will see",
#       3,
#       [
#           "nyakuku",
#           "minymangku Ingkatjinya nyakuku"
#       ]
#   ],

def get_examples_sents_dict(Params):
    File = lara_top.lara_tmp_file('tmp_translation_spreadsheet_surface_type_json', Params)
    Data = lara_utils.read_json_file(File)
    return False if Data == False else { Item[0]: Item[3] for Item in Data }

#  3. sentence audio metadata
#  
#  {
#       "context": "you water. tjitjingkunta mina ungkuku The woman will see Ingkatji.",
#       "file": "extracted_file_ch13_3193.mp3",
#       "text": "minymangku Ingkatjinya nyakuku"
#      },

def get_sent_audio_file_dict(Params):
    Dir = Params.segment_audio_directory
    Data = lara_audio.read_ldt_metadata_file(Dir)
    return False if Data == False else { Item['text']: Item['file'] for Item in Data }

#  [
#                  " minyma|ngku Ingkatjinya#Ingkatji# nyakuku#nya#",
#                  "minymangku Ingkatjinya nyakuku",
#                  [
#                      [ " ", "" ],
#                      [ "minyma", "minyma"],
#                      [ "ngku", "ngku" ],
#                      [ " ", "" ],
#                      [ "Ingkatjinya", "Ingkatji" ],
#                      [ " ", "" ],
#                      [ "nyakuku", "nya" ]
#                  ],
#                  "local_files"
#              ],

def get_sents_to_pairs_dict(Params):
    PageOrientedSplitList = lara_split_and_clean.read_split_file('', Params)
    Dict = {}
    for ( PageInfo, Segments ) in PageOrientedSplitList:
        for Segment in Segments:
            if lara_picturebook.is_annotated_image_segment(Segment):
                InnerSegmentList = lara_picturebook.annotated_image_segments(Segment)
                for Segment1 in InnerSegmentList:
                    Dict[Segment1[1]] = Segment1[2]
            else:
                Dict[Segment[1]] = Segment[2]
    return Dict
 
#  Inputs to second step (command-line call):
#
#  1. File created from first step
#  2. Audio files referenced
#  3. Instantiated label files
#
#  Output:
#  
#  Extract audio and metadata for word audio directory.
#  	
#  Produce warning messages if label files are missing or don't match labelled text.

def extract_word_audio(ConfigFile):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if Params == False:
        return
    WordAudioMetadataFile = word_alignment_file(Params)
    if WordAudioMetadataFile == False:
        return
    Metadata = lara_utils.read_json_file(WordAudioMetadataFile)
    if Metadata == False:
        return
    ( AudioDir, BadItems ) = ( Params.word_audio_directory, [] )
    if AudioDir == '':
        lara_utils.print_and_flush(f'*** Error: word_audio_directory not defined')
        return
    lara_utils.create_directory_if_it_doesnt_exist(AudioDir)
    for Item in Metadata:
        Result = extract_word_audio_for_item(Item, AudioDir, Params)
        if Result == False:
            BadItems += [ Item ]
    lara_utils.print_and_flush(f'--- Word audio extracted for {len(Metadata) - len(BadItems)} items')
    if len(BadItems) != 0:
        lara_utils.print_and_flush(f'*** Error: unable to process following {len(BadItems)} items:')
        lara_utils.prettyprint(BadItems)

#     {
#             "audio_file": "$LARA/Content/pitjantjatjara_course/audio/pitjantjatjara_voice/extracted_file_ch16_4105.mp3",
#             "label_file": "$LARA/Content/pitjantjatjara_course/corpus/LabelTrack_extracted_file_ch16_4105.txt",
#             "labelled_text": "|1|wati|2|ngku|3| |4|wakaṉu|5|",
#             "text": "watingku wakaṉu",
#             "relevant_word": "wakaṉu",
#             "words": [
#                 "wati",
#                 "ngku",
#                 "wakaṉu"
#             ]
#         },

def extract_word_audio_for_item(Item, AudioDir, Params):
    AudioFile = Item['audio_file']
    AudioLabelsFile = Item['label_file']
    LabelledText = Item['labelled_text']
    Text = Item['text']
    RelevantWord = Item['relevant_word']
    lara_utils.print_and_flush(f'------------------------------------------')
    lara_utils.print_and_flush(f'Processing {AudioFile} ("{LabelledText}")')
    AudioLabelsAndTimings = lara_align_from_audio.get_audio_labels_and_timings(AudioLabelsFile)
    SourceLabelsAndTexts = lara_align_from_audio.get_text_labels_and_texts_from_string(LabelledText)
    AudioLabels = [ Item[0] for Item in AudioLabelsAndTimings ]
    SourceLabels = [ Item[0] for Item in SourceLabelsAndTexts ]
    ( StartLabel, EndLabel ) = ( SourceLabels[0], SourceLabels[-1] )
    AlignedLabels = lara_align_from_audio.get_aligned_labels({'audio labels': AudioLabels,
                                                              'source labels': SourceLabels},
                                                              StartLabel, EndLabel)
    if len(AlignedLabels) < 2:
        return False                                            
    extract_word_audio_for_item1(RelevantWord, AlignedLabels, AudioLabelsAndTimings, SourceLabelsAndTexts, AudioFile, AudioDir, Params)

def extract_word_audio_for_item1(RelevantWord0, AlignedLabels, AudioLabelsAndTimings, SourceLabelsAndTexts, AudioFile, AudioDir, Params):
    RelevantWord = lara_audio.make_word_canonical_for_word_recording(RelevantWord0)
    AudioLabelsAndTimings1 = [ ( Label, Time ) for ( Label, Time ) in AudioLabelsAndTimings if Label in AlignedLabels ]
    Texts1 = [ ( Label, lara_audio.make_word_canonical_for_word_recording(Text) )
               for ( Label, Text ) in SourceLabelsAndTexts if Label in AlignedLabels ]
    ( CurrentTime, Metadata ) = ( AudioLabelsAndTimings1[0][1], [] )
    Indices = range(1, min([len(AudioLabelsAndTimings1), len(Texts1)]))
    for I in Indices:
        ( NextLabel, NextTime ) = AudioLabelsAndTimings1[I]
        ( NextLabel1, Text ) = Texts1[I]
        if RelevantWord == Text:
            BaseFileName = f'extracted_file_word_{Text}.mp3'
            Result = lara_align_from_audio.extract_audio_file_from_mp3(AudioFile, BaseFileName, CurrentTime, NextTime, Text, AudioDir, Params)
            if BaseFileName != False:
                Metadata += [ { 'text': Text, 'file': BaseFileName } ]
        CurrentTime = NextTime
    AudioId = False
    lara_align_from_audio.write_or_update_metadata_file(Metadata, AudioId, AudioDir)
    lara_utils.print_and_flush(f'--- Updated word audio dir ({len(Metadata)} files), {AudioDir}')
    
def trivial_word_extraction_text(Str):
    for Char in Str:
        if not Char.isspace() and not lara_parse_utils.is_punctuation_char(Char):
            return False
    return True

def word_alignment_file(Params):
    File = lara_top.lara_tmp_file('word_alignment_file', Params)
    #File = Params.word_alignment_file
    if File == '':
        lara_utils.print_and_flush(f'*** Error: word_alignment_file is not defined')
        return False
    else:
        return File
