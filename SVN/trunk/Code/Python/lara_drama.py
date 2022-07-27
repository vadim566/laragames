
import lara_top
import lara_config
import lara_audio
import lara_split_and_clean
import lara_parse_utils
import lara_utils

def test_make_play_part_file(Id):
    if Id == 'antigone':
        SplitFile = '$LARA/tmp_resources/antigone_split.json'
        CharacterNames = ['ANTIGONE',
                          'LA NOURRICE',
                          'ISMENE',
                          'HEMON',
                          'CREON',
                          'LA NOURRICE',
                          'LE CHŒUR',
                          'LE PROLOGUE',
                          'LE GARDE',
                          'LE DEUXIEME GARDE',
                          'LE TROISIEME GARDE',
                          'LE MESSAGER',
                          'LE PAGE']
        RecordingStringPartFile = '$LARA/tmp_resources/antigone_recording_string_parts.json'
        ConfigFile = '$LARA/Content/antigone/corpus/local_config.json'
    else:
        lara_utils.print_and_flush(f'*** Error: unknown id: {Id}')
        return False
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if Params:
        make_play_part_file(SplitFile, CharacterNames, RecordingStringPartFile, Params)
    

def make_play_part_file(SplitFile, CharacterNames, RecordingStringPartFile, Params):
    AllChunks = [ Chunk for ( PageInfo, Chunks ) in lara_split_and_clean.read_split_file(SplitFile, Params)
                  for Chunk in Chunks ]
    ( CurrentPart, InStageDirection, TextSoFar, RecordingStringPartList ) = ( False, False, [], [] )
    for Chunk in  AllChunks:
        ( Raw, Cleaned ) = Chunk[:2]
        Type = segment_type(Raw, Cleaned, CharacterNames)
        #lara_utils.print_and_flush(f'--- "{Type}" = segment_type("{Raw}", "{Cleaned}", CharacterNames)')
        Context = lara_audio.text_so_far_to_context(TextSoFar)
        if not Type:
            lara_utils.print_and_flush(f'*** Error: unable to identify type of segment: "{Raw}"')
            return False
        elif isinstance(Type, list) and len(Type) == 2 and Type[0] == 'part_name':
            CurrentPart = Type[1]
            Label = 'part_name'
        elif Type == 'start_of_stage_direction':
            Label = 'stage_direction'
            InStageDirection = True
        elif Type in ( 'complete_stage_direction', 'end_of_stage_direction' ):
            Label = 'stage_direction'
            InStageDirection = False
        elif Type == 'plain':
            if InStageDirection:
                Label = 'stage_direction'
            # We assume that plain material before any part names is going to be dramatis personae etc.
            elif CurrentPart == False and InStageDirection == False:
                Label = 'other'
            else:
                Label = [ 'line', CurrentPart ]
        else:
            Label = Type
        RecordingString = lara_audio.make_segment_canonical_for_recording(Cleaned)
        RecordingStringPartList += [ { 'text': RecordingString, 'context': Context, 'label': Label } ]
        TextSoFar += RecordingString.split()
    lara_utils.write_json_to_file(RecordingStringPartList, RecordingStringPartFile)
    lara_utils.print_and_flush(f'--- Written recording string part file ({len(RecordingStringPartList)} items) {RecordingStringPartFile}')
    summarise_string_part_list(RecordingStringPartList)
    return True

def segment_type(Raw, Cleaned, CharacterNames):
    # Assume part names are in bold
    if Raw.find('<b>') >= 0:
        for Name in CharacterNames:
            if not isinstance(Cleaned, str) or not isinstance(Name, str):
                lara_utils.print_and_flush(f'*** Error: bad values: Cleaned = "{Cleaned}", Name = {Name}')
            if Cleaned.find(Name) >= 0:
                return [ 'part_name', Name ]
        lara_utils.print_and_flush(f'*** Warning: might be unknown part name: "{Raw}"')
        return 'other'
    # Assume anything with an <h1> or an <h2> is a heading
    if Raw.find('<h1>') >= 0 or Raw.find('<h2>') >= 0:
        return 'heading'
    # Assume anything with a <i> and a </i> is a complete stage direction
    if Raw.find('<i>') >= 0 and Raw.find('</i>') >= 0:
        return 'complete_stage_direction'
    # Assume anything with a <i> and no </i> is the start of a stage direction
    if Raw.find('<i>') >= 0:
        return 'start_of_stage_direction'
    # Assume anything with a </i> and no <i> is the end of a stage direction
    if Raw.find('</i>') >= 0:
        return 'end_of_stage_direction'
    else:
        return 'plain'
    
def summarise_string_part_list(RecordingStringPartList):
    Summary = {}
    for Item in RecordingStringPartList:
        ( Text, Context, Tag ) = ( Item['text'], Item['context'], Item['label'] )
        Label = Tag[1] if isinstance(Tag, list) and len(Tag) == 2 and Tag[0] == 'line' else Tag
        if not Label in Summary:
            Summary[Label] = 1
        else:
            Summary[Label] += 1
    for Label in Summary:
        lara_utils.print_and_flush(f'{Summary[Label]:4}  {Label}')

##[
##        "No one has ever understood why.",
##        [
##            "line",
##            "THE PROLOGUE"
##        ]
##    ],
            
def combine_play_segment_audio(Params):
    SegmentAudioDir = Params.segment_audio_directory
    if SegmentAudioDir == '':
        lara_utils.print_and_flush(f'*** Error: segment_audio_directory is not set in config file')
        return False    
    PartsDirsDict = Params.play_combine_parts
    RecordingStringPartList = get_recording_string_parts_list(Params)
    if not check_play_combine_parts(PartsDirsDict, SegmentAudioDir, Params):
        return False
    if not RecordingStringPartList:
        return False
    lara_utils.create_directory_if_it_doesnt_exist(SegmentAudioDir)
    OtherAudioDirs = lara_utils.remove_duplicates([ PartsDirsDict[Part] for Part in PartsDirsDict ])
    ( AudioDict, CombinedSegmentMetadata ) = ( {}, [] )
    for Dir in OtherAudioDirs:
        # Assume all segment audio directories are sisters 
        FullDir = f'{SegmentAudioDir}/../{Dir}'
        update_audio_file_dict_from_audio_dir(FullDir, Dir, AudioDict)
    for Item in RecordingStringPartList:
        if isinstance(Item, dict) and 'text' in Item and 'label' in Item and 'context' in Item and \
           isinstance(Item['label'], list) and len(Item['label']) == 2 and Item['label'][0] == 'line':
            Text = Item['text']
            Context = Item['context']
            Part = Item['label'][1]
            Dir = PartsDirsDict[Part]
            FullDir = f'{SegmentAudioDir}/../{Dir}'
            Key = ( Text, Context, Dir )
            if Key in AudioDict:
                File = AudioDict[Key]
                if lara_utils.copy_file(f'{FullDir}/{File}', f'{SegmentAudioDir}/{File}'):
                    CombinedSegmentMetadata += [ { 'file': File, 'text': Text, 'context': Context } ]
                else:
                    lara_utils.print_and_flush(f'*** Error: bad copy: Part = "{Part}", Text = "{Text}", Context = {Context}')
    lara_audio.write_ldt_metadata_file(CombinedSegmentMetadata, SegmentAudioDir)
    lara_utils.print_and_flush(f'--- Written audio metadata ({len(CombinedSegmentMetadata)} items) to {SegmentAudioDir}')
    return True

def check_play_combine_parts(PartsDirsDict, SegmentAudioDir, Params):
    Parts = Params.play_parts
    for Part in PartsDirsDict:
        if not Part in Parts:
            lara_utils.print_and_flush(f'*** Error: part "{Part}" in play_combine_parts not defined in play_parts in config file')
            return False
        Dir = PartsDirsDict[Part]
        if not isinstance(Dir, str):
            lara_utils.print_and_flush(f'*** Error: value for part "{Part}" in play_combine_parts, "{Dir}", not a string')
            return False
        # Assume all segment audio directories are sisters 
        FullDir = f'{SegmentAudioDir}/../{Dir}'
        if not lara_utils.directory_exists(FullDir):
            lara_utils.print_and_flush(f'*** Warning: directory for part "{Part}" in play_combine_parts, "{FullDir}", not found')
    return True    
        
def get_recording_string_parts_list(Params):
    File = lara_top.lara_tmp_file('recording_string_play_parts', Params)
    if not lara_utils.file_exists(File):
        lara_utils.print_and_flush(f'*** Warning: "{File}" not found')
        return False
    return lara_utils.read_json_file(File)

##{
##        "file": "1030787_200929_113858149.mp3",
##        "text": "Well, here we are. These people that you see here are about to act out the story of Antigone for you."
##    },

def update_audio_file_dict_from_audio_dir(FullDir, Dir, AudioDict):
    if not lara_utils.directory_exists(FullDir):
        return True
    Metadata = lara_audio.read_ldt_metadata_file(FullDir)
    for Item in Metadata:
        if not isinstance(Item, dict) or not 'file' in Item or not 'text' in Item:
            lara_utils.print_and_flush(f'*** Error: bad item "{Item}" in metadata for "{Dir}"')
            return False
        ( File, Text ) = ( Item['file'], Item['text'] )
        if File != '' and 'context' in Item:
            Context = Item['context'] 
            Key = ( Text, Context, Dir )
            AudioDict[Key] = File
    return True

# -----------------------------------------------------------

##PlayPartList:
##
##{
##        "context": "group and moves forward. SCENE I: THE PROLOGUE THE PROLOGUE",
##        "label": [
##            "line",
##            "THE PROLOGUE"
##        ],
##        "text": "Well, here we are. These people that you see here are about to act out the story of Antigone for you."
##    },
##
##Metadata:
##
##{
##        "context": "group and moves forward. SCENE I: THE PROLOGUE THE PROLOGUE",
##        "file": "1050816_201005_011652724.mp3",
##        "text": "Well, here we are. These people that you see here are about to act out the story of Antigone for you."
##    },
        
def find_unrecorded_lines_in_play(Params):
    RecordingStringPartList = get_recording_string_parts_list(Params)
    if RecordingStringPartList == False:
        lara_utils.print_and_flush(f'*** Error: unable to find string/part list')
        return False
    if Params.segment_audio_directory == '' or not lara_utils.directory_exists(Params.segment_audio_directory):
        lara_utils.print_and_flush(f'*** Error: unable to find segment audio directory')
        return False
    SegmentMetadata = lara_audio.read_ldt_metadata_file(Params.segment_audio_directory)
    if SegmentMetadata == False or SegmentMetadata == []:
        lara_utils.print_and_flush(f'*** Error: unable to find segment metadata')
        return False
    SegmentMetadataDict = make_segment_metadata_dict(SegmentMetadata)
    MissingLines = []
    for Item in RecordingStringPartList:
        if 'context' in Item and 'text' in Item and 'label' in Item and \
           isinstance(Item['label'], list) and len(Item['label']) == 2 and Item['label'][0] == 'line' and \
           contains_more_than_spaces_and_punctuation(Item['text']):
            ( Text, Context, Part ) = ( Item['text'], Item['context'], Item['label'][1] )
            Key = ( Text, Context )
            if not Key in SegmentMetadataDict:
                MissingLines += [ { 'text': Text, 'context': Context, 'part': Part } ]
    write_out_unrecorded_lines_list(MissingLines, Params)
    return True

def contains_more_than_spaces_and_punctuation(Str):
    for Char in Str:
        if not Char.isspace() and not lara_parse_utils.is_punctuation_char(Char):
            return True
    return False

def make_segment_metadata_dict(SegmentMetadata):
    Dict = {}
    for Item in SegmentMetadata:
        if 'context' in Item and 'text' in Item and 'file' in Item and Item['file'] != '':
            ( Text, Context, File ) = ( Item['text'], Item['context'], Item['file'] )
            Key = ( Text, Context )
            Dict[Key] = File
    return Dict

def write_out_unrecorded_lines_list(MissingLines, Params):
    if len(MissingLines) == 0:
        lara_utils.print_and_flush(f'--- All lines appear to have been recorded')
        return 
    File = f'{Params.lara_tmp_directory}/{Params.id}_unrecorded_lines.html'
    write_out_unrecorded_lines_list1(MissingLines, File)
    AllParts = lara_utils.remove_duplicates([ Item['part'] for Item in MissingLines ])
    for Part in AllParts:
        MissingLinesForPart = [ Item for Item in MissingLines if Item['part'] == Part ]
        FileForPart = f'{Params.lara_tmp_directory}/{Params.id}_unrecorded_lines_for_{Part}.html'
        write_out_unrecorded_lines_list1(MissingLinesForPart, FileForPart)

def write_out_unrecorded_lines_list1(MissingLines, File):
    Lines = []
    Intro = ['<html>',
             '<body>']
    Lines += Intro
    for Item in MissingLines:
        NextLines = [ f"<p><i>[After: {Item['context']}]</i><br>",
                      f"<b>{Item['part']}:</b> {Item['text']}</p>" ]
        Lines += NextLines
    Coda = ['</body>',
            '</html>']
    Lines += Coda
    lara_utils.write_lara_text_file('\n'.join(Lines), File)
    lara_utils.print_and_flush(f'--- Written {len(MissingLines)} unrecorded lines to {File}')
    
# -----------------------------------------------------------

##1. The play part list associates role names with line/context pairs, e.g.
##
##{
##        "context": "second Empire \u2026 \u00e7a n'est pas mal non plus. GARCIN",
##        "label": [
##            "line",
##            "GARCIN"
##        ],
##        "text": "Ah ! bon. Bon, bon, bon."
##    },
##
##2. The audio metadata associates line/context pairs with audio files:
##
##{
##        "context": "second Empire \u2026 \u00e7a n'est pas mal non plus. GARCIN",
##        "file": "1581633_210407_111302141.mp3",
##        "text": "Ah ! bon. Bon, bon, bon."
##    },
##
##3. The ffmpeg 'volume' audio filter lets you change the volume on an mp3. https://trac.ffmpeg.org/wiki/AudioVolume, in particular
##
##To change the audio volume, you may use FFmpeg's ​volume audio filter.
##
##If we want our volume to be half of the input volume:
##
##ffmpeg -i input.wav -filter:a "volume=0.5" output.wav
##
##150% of current volume:
##
##ffmpeg -i input.wav -filter:a "volume=1.5" output.wav

def test_change_volume_for_play_part(Id):
    if Id == 'no_exit':
        ConfigFile = '$LARA/Content/no_exit/corpus/local_config.json'
        PartName = 'THE VALET'
        Factor = 'a'
        change_volume_for_play_part(ConfigFile, PartName, Factor)
    else:
        lara_utils.print_and_flush(f'*** Error: unknown ID {Id}')

def change_volume_for_play_part(ConfigFile, PartName, Factor0):
    if isinstance(Factor0, ( int, float )):
        Factor = Factor0
    elif isinstance(Factor0, str):
        Factor = lara_utils.safe_string_to_number(Factor0)
        if Factor == False:
            lara_utils.print_and_flush(f'*** Error: factor "{Factor0}" needs to be a number')
            return False
    else:
        lara_utils.print_and_flush(f'*** Error: factor {Factor0} needs to be a number')
        return False
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if Params == False:
        return False
    RecordingStringPartList = get_recording_string_parts_list(Params)
    if RecordingStringPartList == False:
        lara_utils.print_and_flush(f'*** Error: unable to find string/part list')
        return False
    SegmentAudioDict = Params.segment_audio_directory
    SegmentAudioMetadata = lara_audio.read_ldt_metadata_file(SegmentAudioDict)
    if SegmentAudioMetadata == False:
        lara_utils.print_and_flush(f'*** Error: unable to find segment audio metadata for {ConfigFile}')
        return False
    AudioMetadataDict = { ( Item['text'], Item['context'] ): Item['file'] for Item in SegmentAudioMetadata }
    TextAndContextListForPart = [ { 'text': Item['text'], 'context': Item['context'] }
                                  for Item in RecordingStringPartList
                                  if isinstance(Item['label'], list) and len(Item['label']) == 2 and Item['label'][1] == PartName ]
    if len(TextAndContextListForPart) == 0:
        lara_utils.print_and_flush(f'*** Error: no lines found for "{PartName}"')
        return False
    ( NGood, NBad ) = ( 0, 0 )
    for Item in TextAndContextListForPart:
        ( Text, Context ) = ( Item['text'], Item['context'] )
        Key = ( Text, Context )
        if Key in AudioMetadataDict:
            File = AudioMetadataDict[Key]
            Result = change_volume_for_audio_file(File, SegmentAudioDict, Factor, Params)
            if Result == True:
                NGood += 1
            else:
                NBad += 1
    lara_utils.print_and_flush(f'--- Changed volume for {NGood} files by factor of {Factor}. {NBad} attempts failed.')

# ffmpeg -i input.wav -filter:a "volume=0.5" output.wav
def change_volume_for_audio_file(File, SegmentAudioDict, Factor, Params):
    OldFile = f'{SegmentAudioDict}/{File}'
    ( BaseFile, Extension ) = lara_utils.file_to_base_file_and_extension(File)
    SavedFile = f'{BaseFile}_orig.{Extension}'
    ChangedFile = f'{BaseFile}_new.{Extension}'
    Command = f'ffmpeg -i {OldFile} -filter:a "volume={Factor}" {ChangedFile}'
    Status = lara_utils.execute_lara_os_call(Command, Params)
    if Status != 0:
        lara_utils.print_and_flush(f'*** Error: unable to change volume for {File} by factor of {Factor}')
        return False
    lara_utils.copy_file(OldFile, SavedFile)
    lara_utils.copy_file(ChangedFile, OldFile)
    lara_utils.delete_file_if_it_exists(ChangedFile)
    return True


# -----------------------------------------------------------

##    {
##        "context": "group and moves forward. SCENE I: THE PROLOGUE THE PROLOGUE",
##        "label": [
##            "line",
##            "THE PROLOGUE"
##        ],
##        "text": "Well, here we are. These people that you see here are about to act out the story of Antigone for you."
##    },

def is_non_spoken_line(Text, Params):
    #lara_utils.print_and_flush(f'--- checking if "{Text}" is a non-spoken line')
    Dict = get_non_spoken_lines_dict(Params)
    if Dict == False:
        #lara_utils.print_and_flush(f'--- no dict') 
        return False
    else:
        #lara_utils.print_and_flush(f'--- dict has {len(Dict)} entries') 
        Result = Text in Dict
        #lara_utils.print_and_flush(f'--- Result = {Result}')
        return Result

_cached_non_spoken_lines_dict = '*uninitialised*'

def get_non_spoken_lines_dict(Params):
    if _cached_non_spoken_lines_dict == '*uninitialised*':
        initialise_non_spoken_lines_dict(Params)
    if _cached_non_spoken_lines_dict == False:
        return {}
    else:
        return _cached_non_spoken_lines_dict

def initialise_non_spoken_lines_dict(Params):
    global _cached_non_spoken_lines_dict
    RecordingStringPartList = get_recording_string_parts_list(Params)
    if RecordingStringPartList == False:
        _cached_non_spoken_lines_dict = False
    else:
        _cached_non_spoken_lines_dict = {}
        for Item in RecordingStringPartList:
            Label = Item['label']
            Text = Item['text']
            if not ( isinstance(Label, list) and len(Label) == 2 and Label[0] == 'line' ):
                _cached_non_spoken_lines_dict[Text] = True
    File = f'{Params.lara_tmp_directory}/{Params.id}_non_spoken_lines_dict.json'
    lara_utils.write_json_to_file(_cached_non_spoken_lines_dict, File)



    
