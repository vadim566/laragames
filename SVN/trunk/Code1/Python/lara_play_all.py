
import lara_top
import lara_config
import lara_utils

def create_play_all_audio_files_if_necessary(AllSentsAudioList, Params):
    # If we are only creating abstract HTML then we'll make the play-all files later or not at all
    if AllSentsAudioList == False or AllSentsAudioList == []:
        lara_utils.print_and_flush(f'--- No need to create play-all audio files')
        return 
    File = lara_top.lara_tmp_file('all_audio_segments_file', Params)
    lara_utils.write_json_to_file(AllSentsAudioList, File)
    for Item in AllSentsAudioList:
        if not isinstance(Item, dict) or \
           not 'file_name' in Item or not 'page_name' or not 'segment_audio_files' in Item:
            lara_utils.print_and_flush(f'*** Error: bad item {Item} in play-all-sents file {File}')
        else:
            create_single_play_all_audio_file(Item, Params)

##          "file_name": "play_all_1.mp3",
##        "page_name": 1,
##        "segment_audio_files": [
##            "423750_191217_160527931.mp3",
##            "423751_191217_160629019.mp3",
##            "423752_191217_160635688.mp3",
##            "423753_191217_160640706.mp3",
##            "423754_191217_160645940.mp3",
##            "423755_191217_160652069.mp3",
##            "423756_191217_160659646.mp3"
##        ]
##    }

##  Recipe from https://superuser.com/questions/314239/how-to-join-merge-many-mp3-files:
##  
##  This will concatenate a folder full of MP3 into a single MP3 file:
##  
##  1) Save a list of the MP3 files to concatenate, e.g.,
##  
##  $ cat mylist.txt
##  file '/tmp/01.mp3'
##  file '/tmp/02.mp3'
##  file '/tmp/03.mp3'
##  
##  2) Run the following command (-safe 0 is not required if mylist.txt uses relative paths instead):
##  
##  $ ffmpeg -f concat -safe 0 -i mylist.txt -c copy output.mp3

## I can't figure out how to make the ffmpeg concat command use absolute pathnames.
## So use relative pathnames and put ListFile in the multimedia directory.             
def create_single_play_all_audio_file(Item, Params):
    CorpusId = Item['corpus_name']
    PageName = Item['page_name']
    ComponentFileNames = Item['segment_audio_files']
    TargetFile0 = Item['file_name']
    TargetFile = absolute_multimedia_dir_file(TargetFile0, Params)
    if ComponentFileNames == False or ComponentFileNames == []:
        return
    #ListFile = lara_utils.get_tmp_trace_file(Params)
    ListFile = absolute_multimedia_dir_file(f'play_all_list_file_{CorpusId}_{PageName}.txt', Params)
    try:
        lara_utils.print_and_flush(f'--- Making play_all file {TargetFile0}')
        write_component_files_to_list_file(CorpusId, ComponentFileNames, ListFile, Params)
        AbsListFile = lara_utils.absolute_file_name(ListFile)
        Command = f'ffmpeg -f concat -safe 0 -i {ListFile} -c copy {TargetFile}'
        Result = lara_utils.execute_lara_os_call_direct(Command)
    except Exception as e:
        lara_utils.print_and_flush(f'*** Warning: something went wrong when making play_all file"')
        lara_utils.print_and_flush(str(e))
##    finally:
##        lara_utils.delete_file_if_it_exists(ListFile)

def write_component_files_to_list_file(CorpusId, ComponentFileNames, ListFile, Params):
    #AbsFiles = [ f"file '{absolute_segment_audio_dir_file(File, Params)}'" for File in ComponentFileNames ]
    #lara_utils.write_lara_text_file('\n'.join(AbsFiles), ListFile)
    if CorpusId in Params.component_params:
        ComponentParams = Params.component_params[CorpusId]
        Dir = ComponentParams.segment_audio_directory
    else:
        Dir = Params.segment_audio_directory
    Lines = []
    for File in ComponentFileNames:
        if not lara_utils.file_exists(f'{Dir}/{File}'):
            lara_utils.print_and_flush(f'*** Warning: unable to find {File}')
        else:
            Lines += [ f" file '{File}'" ]
    lara_utils.write_lara_text_file('\n'.join(Lines), ListFile)
    
def absolute_multimedia_dir_file(File, Params):
    return lara_utils.absolute_file_name(f'{lara_utils.get_multimedia_dir_from_params(Params)}/{File}')

def absolute_segment_audio_dir_file(File, Params):
    return lara_utils.absolute_file_name(f'{Params.segment_audio_directory}/{File}')

def base_play_all_audio_file_name_for_current_page(Params):
    PageName = Params.page_name
    return base_play_all_audio_file_name_for_page(PageName, Params)

def base_play_all_audio_file_name_for_page(PageName, Params):
    return False if PageName == '' else f'play_all_{Params.id}_{PageName}.mp3'

# ---------------------------------------

# We find the most common sampling rate, convert mp3s with different rates to that rate, and copy everything else.
#
# This should no longer be needed - there was a confusion about how to convert LDT files, now fixed. But
# the processing could conceivably still be useful for old projects.

def test_make_copy_of_audio_directory_with_uniform_sampling_rate(Id):
    if Id == 'antigone_en':
        Dir = '$LARA/Content/antigone_en/audio/combined_rosa_kirsten'
        Dir1 = '$LARA/Content/antigone_en/audio/combined_rosa_kirsten_uniform_sample_rate'
        ConfigFile = '$LARA/Content/antigone_en/corpus/local_config_rosa_kirsten.json'
    elif Id == 'sample_english':
        Dir = '$LARA/Content/sample_english/audio/tmp'
        Dir1 = '$LARA/Content/sample_english/audio/tmp1'
        ConfigFile = '$LARA/Content/sample_english/corpus/local_config.json'
    if Id == 'huis_clos':
        Dir = '$LARA/Content/huis_clos/audio/HuisClos'
        Dir1 = '$LARA/Content/huis_clos/audio/HuisClos_uniform_sample_rate'
        ConfigFile = '$LARA/Content/huis_clos/corpus/local_config.json'
    else:
        lara_utils.print_and_flush(f'*** Error: unknown ID {Id}')
        return False
    make_copy_of_audio_directory_with_uniform_sampling_rate(Dir, Dir1, ConfigFile)

def make_copy_of_audio_directory_with_uniform_sampling_rate(Dir, Dir1, ConfigFile):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if Params == False:
        return False
    if not lara_utils.create_directory_deleting_old_if_necessary(Dir1):
        lara_utils.print_and_flush(f'*** Error: unable to create new directory {Dir1}')
        return False
    FileSamplingRateDict = get_sampling_rates_for_files_in_dir(Dir, Params)
    SamplingRates = [ FileSamplingRateDict[File] for File in FileSamplingRateDict ]
    if len(SamplingRates) == 0:
        lara_utils.print_and_flush(f'--- Directory {Dir} has no audio files, nothing to do')
        return True
    SamplingRatesMultiSet = lara_utils.list_to_ordered_multiset(SamplingRates)
    ( MostCommonSamplingRate, Count ) = SamplingRatesMultiSet[0]
    NAudioFiles = len(SamplingRates)
    lara_utils.print_and_flush(f'--- Converting to {MostCommonSamplingRate}: most common sampling rate, {Count}/{NAudioFiles}')
    Files = lara_utils.directory_files(Dir)
    Converted = 0
    for File in Files:
        FromFile = f'{Dir}/{File}'
        ToFile = f'{Dir1}/{File}'
        Extension = lara_utils.extension_for_file(File)
        if Extension != 'mp3':
            if lara_utils.copy_file(FromFile, ToFile) == False:
                return False
        else:
            SamplingRate = FileSamplingRateDict[File]
            if SamplingRate == MostCommonSamplingRate:
                lara_utils.copy_file(FromFile, ToFile)
            else:
                if change_sampling_rate_of_mp3(FromFile, MostCommonSamplingRate, ToFile, Params) == False:
                    return False
                Converted += 1
    lara_utils.print_and_flush(f'--- Created {Dir1} with all mp3 sampled at {MostCommonSamplingRate}, {Converted} files converted.')
    return True

def get_sampling_rates_for_files_in_dir(Dir, Params):
    if not lara_utils.directory_exists(Dir):
        lara_utils.print_and_flush(f'*** Error: unable to find directory {Dir1}')
        return False
    Files = lara_utils.directory_files(Dir)
    return { File: get_sampling_rate_for_mp3(f'{Dir}/{File}', Params) for File in Files \
             if lara_utils.extension_for_file(f'{Dir}/{File}') == 'mp3' }

##  Metadata:
##    encoder         : Lavf58.27.103
##  Duration: 00:00:15.18, start: 0.025057, bitrate: 48 kb/s
##    Stream #0:0: Audio: mp3, 44100 Hz, mono, fltp, 48 kb/s

def get_sampling_rate_for_mp3(File, Params):
    if not lara_utils.file_exists(File):
        lara_utils.print_and_flush(f'*** Error: unable to get sampling rate for {File}, file not found.')
        return False
    if not lara_utils.extension_for_file(File) == 'mp3':
        lara_utils.print_and_flush(f'*** Error: unable to get sampling rate for {File}, file does not have "mp3" extension.')
        return False
    TmpFile = lara_utils.get_tmp_trace_file(Params)
    try:
        AbsTmpFile = lara_utils.absolute_file_name(TmpFile)
        AbsFile = lara_utils.absolute_file_name(File)
        Command = f'ffprobe {AbsFile} >& {AbsTmpFile}'
        Result = lara_utils.execute_lara_os_call(Command, Params)
        if Result != 0:
            lara_utils.print_and_flush(f'*** Error: unable to get sampling rate for {File}, call to ffprobe failed.')
            return False
        if not lara_utils.file_exists(TmpFile):
            lara_utils.print_and_flush(f'*** Error: unable to get sampling rate for {File}, call to ffprobe failed.')
            return False
        TraceText = lara_utils.read_lara_text_file(TmpFile)
        TraceLines = TraceText.split('\n')
        for Line in TraceLines:
            Components = Line.split()
            for i in range(0, len(Components)):
                if i > 0 and Components[i] == 'Hz,':
                    return lara_utils.safe_string_to_int(Components[i-1])
        lara_utils.print_and_flush(f'*** Error: unable to get sampling rate for {File}, could not find information in trace:.')
        lara_utils.print_and_flush(f'{TraceText}')
        return False
    except Exception as e:
        lara_utils.print_and_flush(f'*** Warning: something went wrong during direct OS call: "{Command}"')
        lara_utils.print_and_flush(str(e))
        return False
    finally:
        lara_utils.delete_file_if_it_exists(TmpFile)

## ffmpeg -i file1.mp3 -ar 44100 file1-enc.mp3

def change_sampling_rate_of_mp3(File, SamplingRate, File1, Params):
    if not lara_utils.file_exists(File):
        lara_utils.print_and_flush(f'*** Error: unable to change sampling rate for {File}, file not found.')
        return False
    if not lara_utils.extension_for_file(File) == 'mp3':
        lara_utils.print_and_flush(f'*** Error: unable to change sampling rate for {File}, file does not have "mp3" extension.')
        return False
    if not lara_utils.extension_for_file(File) == 'mp3':
        lara_utils.print_and_flush(f'*** Error: unable to change sampling rate for {File}, target file {File1} does not have "mp3" extension.')
        return False
    if not lara_utils.delete_file_if_it_exists(File1):
        lara_utils.print_and_flush(f'*** Error: unable to change sampling rate for {File}, target file {File1} already exists and cannot be overwritten.')
        return False
    try:
        Command = f'ffmpeg -i {File} -ar {SamplingRate} {File1}'
        #lara_utils.print_and_flush(f'--- Executing {Command}')
        Result = lara_utils.execute_lara_os_call(Command, Params)
        if Result != 0 or not lara_utils.file_exists(File1):
            lara_utils.print_and_flush(f'*** Error: unable to change sampling rate for {File}, call to ffmpeg failed.')
            return False
        else:
            return True
    except Exception as e:
        lara_utils.print_and_flush(f'*** Warning: something went wrong during direct OS call: "{Command}"')
        lara_utils.print_and_flush(str(e))
        return False
    
