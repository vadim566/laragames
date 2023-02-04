import lara_top
import lara_config
import lara_audio
import lara_parse_utils
import lara_utils

## Unpack word or segment audio zipfile from LDT, convert to mp3, and copy things into place
def install_audio_zipfile(Zipfile, RecordingScriptFile, WordsOrSegments, ConfigFile, BadItemsFile0):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    BadItemsFile = default_bad_items_file(Params) if BadItemsFile0 == 'default' else BadItemsFile0
    ToDir = audio_dir_for_type(ConfigFile, WordsOrSegments)
    if not ToDir:
        lara_utils.print_and_flush(f'*** Error: unable to find "{WordsOrSegments}" audio dir for {ConfigFile}')
        return False
    if not lara_utils.file_exists(Zipfile):
        lara_utils.print_and_flush(f'*** Error: unable to find "{Zipfile}"')
        return False
    TmpDir = lara_utils.get_tmp_directory(Params)
    lara_utils.unzip_file(Zipfile, TmpDir)
    lara_utils.print_and_flush(f'Unzipped {Zipfile} to {TmpDir}')
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if not Params.video_annotations == 'yes':
        TargetExtension = 'mp3'
        convert_lara_audio_directory_to_mp3_format(TmpDir, ConfigFile, BadItemsFile)
        ConvertedTmpDir = converted_mp3_dir_for_dir(TmpDir)
        if not lara_utils.directory_exists(ConvertedTmpDir):
            lara_utils.print_and_flush('*** Error: unable to find converted mp3 dir {ConvertedTmpDir}')
            return False
        # We don't need TmpDir anymore, will only be using ConvertedTmpDir
        lara_utils.delete_directory_if_it_exists(TmpDir)
    else:
        # If we're doing video annotation, we don't convert the file format
        TargetExtension = 'webm'
        ConvertedTmpDir = TmpDir
    install_audio_zipfile1(ConvertedTmpDir, TargetExtension, RecordingScriptFile, ToDir, WordsOrSegments, Params)

def default_bad_items_file(Params):
    return lara_top.lara_tmp_file('bad_ldt_files', Params)

## Unpack segment non-LDT audio zipfile, copy things into place and update metadata file
def install_non_ldt_audio_zipfile(Zipfile, ConfigFile):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    ToDir = audio_dir_for_type(ConfigFile, 'segments')
    if not ToDir:
        lara_utils.print_and_flush(f'*** Error: unable to find segments audio dir for {ConfigFile}')
        return False
    if not lara_utils.file_exists(Zipfile):
        lara_utils.print_and_flush(f'*** Error: unable to find "{Zipfile}"')
        return False
    TmpDir = lara_utils.get_tmp_directory(Params)
    lara_utils.unzip_file(Zipfile, TmpDir)
    lara_utils.print_and_flush(f'Unzipped {Zipfile} to {TmpDir}')
    if not lara_utils.directory_exists(TmpDir):
        lara_utils.print_and_flush(f'*** Error: unable to find unzipped dir {TmpDir}')
        return False
    install_non_ldt_audio_zipfile1(TmpDir, ToDir)

def audio_dir_for_type(ConfigFile, WordsOrSegments):
    if not WordsOrSegments in ('words', 'segments'):
        lara_utils.print_and_flush(f'*** Error: bad second arg "{WordsOrSegments}" to audio_dir_for_type')
        return False
    ConfigData = lara_config.read_lara_local_config_file(ConfigFile)
    if not ConfigData:
        lara_utils.print_and_flush(f'*** Error: unable to read config file "{ConfigFile}"')
        return False
    if WordsOrSegments == 'words' and 'word_audio_directory' in ConfigData:
        return ConfigData['word_audio_directory']
    elif WordsOrSegments == 'segments' and 'segment_audio_directory' in ConfigData:
        return ConfigData['segment_audio_directory']

# Version for non-LDT audio files
# Copy over all files and either update metadata file or create a new one if necessary
##def install_audio_zipfile1(ConvertedTmpDir, RecordingScriptFile, ToDir):
##    NMP3Files = len(lara_utils.files_with_given_extension_in_directory(ConvertedTmpDir, 'mp3'))
##    MetadataFile = f'{ConvertedTmpDir}/metadata_help.txt'
##    if NMP3Files == 0:
##        lara_utils.print_and_flush(f'*** Warning: no MP3 files found in {ConvertedTmpDir}')
##        return True
##    if not lara_utils.file_exists(MetadataFile):
##        lara_utils.print_and_flush(f'*** Error: metadata file {MetadataFile} not found')
##        return False
##    lara_utils.create_directory_if_it_doesnt_exist(ToDir)
##    lara_utils.copy_directory_one_file_at_a_time(ConvertedTmpDir, ToDir, ['mp3'])
##    ToMetadataFile = f'{ToDir}/metadata_help.txt'
##    if not lara_utils.file_exists(ToMetadataFile):
##        lara_utils.copy_file(MetadataFile, ToMetadataFile)
##        lara_utils.print_and_flush(f'--- Copied metadata file from {ConvertedTmpDir} to {ToDir}')
##    else:
##        OldMetadata = lara_utils.read_lara_text_file(ToMetadataFile)
##        NewMetadata = lara_utils.read_lara_text_file(MetadataFile)
##        UpdatedMetadata = OldMetadata + '\n' + NewMetadata
##        UpdatedMetadata1 = clean_audio_metadata(UpdatedMetadata)
##        lara_utils.write_unicode_text_file(UpdatedMetadata1, ToMetadataFile)
##        lara_utils.print_and_flush(f'--- Updated metadata file {ToMetadataFile} from {MetadataFile}')
##    print_information_about_missing_ldt_files(RecordingScriptFile, MetadataFile)
##    return True

# TargetExtension will be 'mp3' for audio and 'webm' for video
def install_audio_zipfile1(ConvertedTmpDir, TargetExtension, RecordingScriptFile, ToDir, WordsOrSegments, Params):
    NMP3Files = len(lara_utils.files_with_given_extension_in_directory(ConvertedTmpDir, TargetExtension))
    MetadataToInstall0 = lara_audio.read_ldt_metadata_file(ConvertedTmpDir)
    MetadataToInstall = lara_audio.maybe_add_contexts_to_metadata(MetadataToInstall0, WordsOrSegments, Params)
    if NMP3Files == 0:
        lara_utils.print_and_flush(f'*** Warning: no {TargetExtension} files found in {ConvertedTmpDir}')
        return True
    if NMP3Files > 0 and MetadataToInstall == []:
        lara_utils.print_and_flush(f'*** Error: no metadata found in audio zipfile')
        return False
    lara_utils.create_directory_if_it_doesnt_exist(ToDir)
    lara_utils.copy_directory_one_file_at_a_time(ConvertedTmpDir, ToDir, [TargetExtension])
    OldMetadata = lara_audio.read_ldt_metadata_file(ToDir)
    UpdatedMetadata = clean_audio_metadata(OldMetadata + MetadataToInstall)
    lara_audio.write_ldt_metadata_file(UpdatedMetadata, ToDir)
    lara_utils.print_and_flush(f'--- Updated metadata file in {ToDir} from downloaded metadata file')
    print_information_about_missing_ldt_files(RecordingScriptFile, MetadataToInstall)
    # Once we've installed the files, we no longer need ConvertedTmpDir
    lara_utils.delete_directory_if_it_exists(ConvertedTmpDir)
    return True

def print_information_about_missing_ldt_files(RecordingScriptFile, MetadataToInstall):
    try:
        RecordingTexts = texts_in_ldt_recording_script(RecordingScriptFile)
        MetadataTexts = [ Item['text'] for Item in MetadataToInstall if 'text' in Item ]
        if RecordingTexts != False:
            Missing = [Text for Text in RecordingTexts if
                       len(Text)> 0 and not Text.isspace() and not Text in MetadataTexts]
            NMissing = len(Missing)
            lara_utils.print_and_flush(f'--- {NMissing} recorded files missing.')
            if NMissing > 0:
                lara_utils.prettyprint(Missing)
        else:
            lara_utils.print_and_flush(f'*** Warning: unable to calculate number of missing files')
    except:
        lara_utils.print_and_flush(f'*** Warning: unable to calculate number of missing files')
 

# Copy over all the converted MP3s. If there isn't a metadata file already, copy that over too.
# If there is one, update it.
# Typical metadata entry looks like this:
# NonLDTAudioFile inferno_i_1-12.mp3
def install_non_ldt_audio_zipfile1(TmpDir, AudioDir):
    AudioFiles = lara_utils.directory_files(TmpDir)
    NAudioFiles = len(AudioFiles)
    if NAudioFiles == 0:
        lara_utils.print_and_flush(f'*** Warning: no files found in {TmpDir}')
        return True
    lara_utils.create_directory_if_it_doesnt_exist(AudioDir)
    lara_utils.copy_directory_one_file_at_a_time(TmpDir, AudioDir, 'all')
    OldMetadata = lara_audio.read_ldt_metadata_file(AudioDir)
    #NewMetadata = [ f'NonLDTAudioFile {File}' for File in AudioFiles ]
    MetadataToInstall = [ { 'text': 'NonLDTAudioFile', 'file': File } for File in AudioFiles ]
    UpdatedMetadata = clean_audio_metadata(OldMetadata + MetadataToInstall)
    #lara_utils.write_unicode_text_file('\n'.join(AllMetadata), ToMetadataFile)
    lara_audio.write_ldt_metadata_file(UpdatedMetadata, AudioDir)
    lara_utils.print_and_flush(f'--- Updated metadata file for {AudioDir} from non-LDT audio data')
    # Once we've installed the files, we no longer need ConvertedTmpDir
    lara_utils.delete_directory_if_it_exists(TmpDir)
    return True

def clean_audio_dir(Dir):
    if not lara_utils.directory_exists(Dir):
        lara_utils.print_and_flush(f'*** Error unable to find {InFile}')
        return False
    MetadataFile = lara_audio.ldt_metadata_file(Dir)
    CleanMetadataFile = clean_audio_metadata_file(MetadataFile)
    if not CleanMetadataFile:
        return False
    FilesReferencedInMetadata = files_referenced_in_ldt_metadata_file(CleanMetadataFile)
    AudioFilesInDir = lara_utils.files_with_one_of_given_extensions_in_directory(Dir, ['mp3', 'wav', 'mp4', 'webm'])
    lara_utils.print_and_flush(f'--- Found {len(AudioFilesInDir)} audio files in directory')
    ReferencedDict = { File: True for File in FilesReferencedInMetadata }
    InDirDict = { File: True for File in AudioFilesInDir }
    NotReferenced = [ File for File in InDirDict if not File in ReferencedDict ]
    NotReferencedFile = f'{Dir}_not_referenced.txt'
    lara_utils.write_lara_text_file('\n'.join(NotReferenced), NotReferencedFile)
    lara_utils.print_and_flush(f'--- {len(NotReferenced)} files not referenced. Listed in {NotReferencedFile}')
    return NotReferencedFile
        
def clean_audio_metadata_file(InFile):
    if not lara_utils.file_exists(InFile):
        lara_utils.print_and_flush(f'*** Error unable to find {InFile}')
        return False
    save_timestamped_copy_of_file(InFile)
    InData = lara_audio.read_named_ldt_metadata_file(InFile)
    OutData = clean_audio_metadata(InData)
    # It's possible that we've got a txt file - if so, change the extension to json
    InFileJSON = lara_utils.change_extension(InFile, 'json')
    lara_audio.write_named_ldt_metadata_file(OutData, InFileJSON)
    return InFileJSON

def save_timestamped_copy_of_file(InFile):
    ( Base, Extension ) = lara_utils.file_to_base_file_and_extension(InFile)
    OldFile = f'{Base}_{lara_utils.timestamp()}.{Extension}'
    lara_utils.copy_file(InFile, OldFile)
    lara_utils.print_and_flush(f'--- Saved copy of {InFile} as {OldFile}')    

def clean_audio_metadata(Metadata):
    ( LinesOutDict, NKept, NRemoved ) = ( {}, 0, 0 )
    for MetadataItem in [ Item for Item in Metadata if isinstance(Item, dict) and 'text' in Item and 'file' in Item if Item['file'] != '' ]:
        Text = MetadataItem['text']
        File = MetadataItem['file']
        Context = MetadataItem['context'] if 'context' in MetadataItem else ''
        # If it's a non-LDT audio file, use the file as the key to make it unique
        if Text == 'NonLDTAudioFile':
            Key = File
        elif Context == '':
            Key = Text
        else:
            Key = f'{Text} ## after "{Context}"'
        # if it's not already listed, add it
        if not Key in LinesOutDict:
            LinesOutDict[Key] = MetadataItem
            NKept += 1
        # else replace the old one, since the later entries take precedence
        else:
            LinesOutDict[Key] = MetadataItem
            NRemoved += 1
        # If we have an item with a context, and we previously had the same item with no context, remove the old item
        if Context != '' and Text in LinesOutDict:
            del LinesOutDict[Text]
            NRemoved += 1
    CleanedMetadata = [ LinesOutDict[Key] for Key in LinesOutDict ]
    lara_utils.print_and_flush(f'\n--- {NRemoved} metadata lines removed, {NKept} kept.')
    return CleanedMetadata

def texts_in_ldt_recording_script(File):
    Extension = lara_utils.extension_for_file(File)
    if Extension == 'txt':
        return texts_in_ldt_recording_script_text(File)
    elif Extension == 'json':
        return texts_in_ldt_recording_script_json(File)
    else:
        lara_utils.print_and_flush(f'*** Error in lara_install_audio_zipfile.texts_in_ldt_recording_script: bad file {File}: LDT recording script files must have a txt or json extension.')
        return False

def texts_in_ldt_recording_script_text(File):
    Lines = lara_utils.read_unicode_text_file_to_lines(File)
    if not Lines:
        lara_utils.print_and_flush(f'*** Warning: unable to read LDT recording script {File}')
        return False
    RecordingTexts = lara_utils.non_false_members([ text_from_recording_script_line(Line) for Line in Lines ])
    lara_utils.print_and_flush(f'--- Found {len(RecordingTexts)} texts to record')
    return RecordingTexts

def texts_in_ldt_recording_script_json(File):
    Data = lara_utils.read_json_file(File)
    if Data == False:
        return False
    if not isinstance(Data, list):
        lara_utils.print_and_flush(f'*** Error: contents of json recording script file do not appear to be a list: {File}')
        return False
    return [ Item['text'] for Item in Data if isinstance(Item, dict) and 'text' in Item ]

def text_from_recording_script_line(Line):
    return lara_parse_utils.parse_ldt_recording_script_line(Line)

def texts_in_ldt_metadata_file(File):
    Metadata = lara_audio.read_named_ldt_metadata_file(File)
    if not Metadata:
        lara_utils.print_and_flush(f'*** Warning: unable to read LDT metadata file {File}')
        return False
    MetadataTexts = lara_utils.remove_duplicates([ Item['text'] for Item in Metadata if isinstance(Item, dict) and 'text' in Item])
    lara_utils.print_and_flush(f'--- Found {len(MetadataTexts)} referenced in metadata file {File}')
    return MetadataTexts

def files_referenced_in_ldt_metadata_file(File):
    Metadata = lara_audio.read_named_ldt_metadata_file(File)
    if not Metadata:
        lara_utils.print_and_flush(f'*** Warning: unable to read LDT metadata file {File}')
        return False
    Files = lara_utils.remove_duplicates([ Item['file'] for Item in Metadata if isinstance(Item, dict) and 'file' in Item])
    lara_utils.print_and_flush(f'--- Found {len(Files)} recorded audio files referenced in metadata file {File}')
    return Files

##def text_from_ldt_metadata_line(Line):
##    Result = lara_parse_utils.parse_ldt_metadata_file_ldt_line(Line)
##    return Result[1] if Result else False
##
##def file_from_ldt_metadata_line(Line):
##    Result = lara_parse_utils.parse_ldt_metadata_file_ldt_line(Line)
##    return Result[0] if Result else False

# -----------------------------------------------

def convert_lara_audio_directory_to_mp3_format(Dir, ConfigFile, BadItemsFile):
    if not Dir or Dir == '':
        lara_utils.print_and_flush(f'*** Error: empty directory not allowed')
        return False
    if not lara_utils.directory_exists(Dir):
        lara_utils.print_and_flush(f'*** Error: unable to find directory {Dir}')
        return False
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if not Params:
        lara_utils.print_and_flush(f'*** Error: unable to find config file {ConfigFile}')
    Dir1 = converted_mp3_dir_for_dir(Dir)
    lara_utils.create_directory_deleting_old_if_necessary(Dir1)
    Files = lara_utils.directory_files(Dir)
    ( AbsDir, AbsDir1 ) = ( lara_utils.absolute_file_name(Dir), lara_utils.absolute_file_name(Dir1) )
    ( NumFilesSuccessfullyConverted, BadFileMetadata ) = convert_lara_audio_directory_to_mp3_format1(Files, AbsDir, AbsDir1, Params)
    lara_utils.write_json_to_file(BadFileMetadata, BadItemsFile)
    lara_utils.print_and_flush(f'--- Sucessfully converted {NumFilesSuccessfullyConverted} files to mp3 format or meta file')
    if len(BadFileMetadata) > 0:
        lara_utils.print_and_flush(f'--- Conversion failed on {len(BadFileMetadata)} files, metadata written to {BadItemsFile}')
    lara_utils.print_and_flush(f'--- Source directory: {AbsDir}')
    lara_utils.print_and_flush(f'--- Target directory: {AbsDir1}')

def converted_mp3_dir_for_dir(Dir):
    return f'{Dir}_mp3'

def convert_lara_audio_directory_to_mp3_format1(Files, Dir, Dir1, Params):
    I = 0
    NumFilesSuccessfullyConverted = 0
    BadFiles = []
    for File in Files:
        if convert_lara_audio_directory_file_to_mp3(File, Dir, Dir1, Params):
            NumFilesSuccessfullyConverted += 1
        else:
            BadFiles += [ File ]
        I += 1
        lara_utils.print_and_flush_no_newline('.')
        if I%100 == 0:
            lara_utils.print_and_flush_no_newline(f' ({I})')
    BadFileMetadata = make_bad_file_metadata(BadFiles, Dir)
    return ( NumFilesSuccessfullyConverted, BadFileMetadata )

def make_bad_file_metadata(BadFiles, Dir):
    AllMetadata = lara_audio.read_ldt_metadata_file(Dir)
    AllMetadataDict = { Record['file']: { 'file': Record['file'], 'text': Record['text'] } for Record in AllMetadata if \
                        isinstance(Record, dict) and 'file' in Record and 'text' in Record }
    BadFileMetadata = []
    for File in BadFiles:
        if not File in AllMetadataDict:
            lara_utils.print_and_flush(f'*** Warning: file {File} not correctly processed and not found in metadata')
        else:
            BadFileMetadata += [ AllMetadataDict[File] ]
    return BadFileMetadata

def convert_lara_audio_directory_file_to_mp3(File, Dir, Dir1, Params):
    ( BaseFile, OldExtension ) = split_pathname_into_base_file_and_extension(File)
    FullFile = f'{Dir}/{File}'
    FullFileTo = f'{Dir1}/{BaseFile}.mp3'
    # If it's already an mp3, just copy it
    if OldExtension.lower() == 'mp3':
        return lara_utils.copy_file(FullFile, FullFileTo)
    # If it's a wav file, convert it
    # Set sampling rate to a uniform 48000 so that we can concatenate mp3s if necessary
    elif OldExtension.lower() == 'wav':
        Command = f'ffmpeg -i {FullFile} -b:a 50k -ar 48000 {FullFileTo}'
        Result = execute_ffmpeg_command(Command, FullFileTo, Params)
        if Result:
            return True
        else:
            lara_utils.print_and_flush(f'\n*** Warning: unable to convert {FullFile}')
            lara_utils.print_and_flush(f'*** with command {Command}')
            return False
    # If it's a json or txt file, it should be metadata
    elif OldExtension.lower() == 'json':
        FullFileTo = f'{Dir1}/{File}'
        convert_lara_audio_metadata_file_json(FullFile, FullFileTo)
        return True
    elif OldExtension.lower() == 'txt':
        FullFileTo = f'{Dir1}/{File}'
        convert_lara_audio_metadata_file_txt(FullFile, FullFileTo)
        return True
    else:
        lara_utils.print_and_flush(f'\n--- skipping {File} (nothing to convert)')
    return False


def execute_ffmpeg_command(Command, OutFile, Params):
    lara_utils.delete_file_if_it_exists(OutFile)
    Status = lara_utils.execute_lara_os_call(Command, Params)
    if Status == 0:
        return True
    else:
        return False

def convert_lara_audio_metadata_file_json(File, File1):
    Metadata = lara_utils.read_json_file(File)
    Metadata1 = [ convert_lara_audio_metadata_file_json_item(Item) for Item in Metadata ]
    if False in Metadata1:
        lara_utils.print_and_flush('*** Error: cannot convert json metadata file: {File}')
        return False
    lara_utils.write_json_to_file(Metadata1, File1)
    lara_utils.print_and_flush(f'\n--- Converted metadata file {File} to {File1}')
    return True

def convert_lara_audio_metadata_file_json_item(Item):
    if not isinstance(Item, dict) or not 'text' in Item or not 'file' in Item:
        lara_utils.print_and_flush(f'*** Error: bad item in json metadata file: {Item}')
        return False
    ( Text, File ) = ( Item['text'], Item['file'] )
    return { 'text': Text, 'file': File.replace('.wav', '.mp3') }

def convert_lara_audio_metadata_file_txt(File, File1):
    Lines = lara_utils.read_unicode_text_file_to_lines(File)
    Lines1 = [ convert_lara_audio_metadata_file_line(Line) for Line in Lines ]
    lara_utils.write_unicode_text_file(''.join(Lines1), File1)
    lara_utils.print_and_flush(f'\n--- Converted metadata file {File} to {File1}')
    return True

def convert_lara_audio_metadata_file_line(Line):
    return Line.replace('.wav ', '.mp3 ')

def split_pathname_into_base_file_and_extension(File):
    Components = File.split('.')
    if len(Components) == 1:
        return ( File, '')
    else:
        return ( '.'.join(Components[:-1]), Components[-1] )
    
