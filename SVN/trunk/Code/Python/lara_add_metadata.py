
import lara_top
import lara_audio
import lara_config
import lara_parse_utils
import lara_utils

# -----------------------------------------------

def add_metadata_to_lara_resource_directory(Dir, CorpusOrLanguage):
    try:
        return add_metadata_to_lara_resource_directory_main(Dir, CorpusOrLanguage)
    except Exception as e:
        lara_utils.print_and_flush(f'*** Error: something went wrong when trying to create metadata for {Dir} as {CorpusOrLanguage}')
        lara_utils.print_and_flush(str(e))
        return False

def add_metadata_to_lara_resource_directory_main(Dir, CorpusOrLanguage):
    if not CorpusOrLanguage in ['corpus', 'language']:
        lara_utils.print_and_flush(f'*** Error: unknown arg "{CorpusOrLanguage}. Needs to be "corpus" or "language".')
        return False
    if not lara_utils.directory_exists(Dir):
        lara_utils.print_and_flush(f'*** Error: unable to find directory "{Dir}.')
        return False
    Valid = True
    if not add_trivial_metadata_to_directory(Dir):
        Valid = False
    Subdirs = get_lara_subdirs(Dir, CorpusOrLanguage)
    if Subdirs:
        for Subdir in Subdirs:
            Result = add_metadata_to_lara_resource_subdirectory(Subdir, Dir, CorpusOrLanguage)
            if not Result:
                Valid = False
    return Valid

def add_trivial_metadata_to_directory(Dir):
    Subdirs = lara_utils.directory_members_of_directory(Dir)
    Files = lara_utils.file_members_of_directory(Dir)
    Metadata = { 'directories': Subdirs, 'files': Files }
    TrivialMetadataFile = f'{Dir}/trivial_metadata.json'
    Okay = True
    if not lara_utils.write_json_to_file(Metadata, TrivialMetadataFile):
        lara_utils.print_and_flush(f'*** Error: unable to write trivial metadata file for directory {Dir}')
        Okay = False
    for Subdir in Subdirs:
        if not add_trivial_metadata_to_directory(f'{Dir}/{Subdir}'):
            Okay = False
    if not Okay:
        lara_utils.print_and_flush(f'*** Error: unable to add trivial metadata to directory {Dir}')
    return Okay

def get_lara_subdirs(Dir, CorpusOrLanguage):
    Subdirs = lara_utils.directory_members_of_directory(Dir)
    if check_valid_subdirs(Subdirs, Dir, CorpusOrLanguage) and check_required_subdirs_present(Subdirs, Dir, CorpusOrLanguage):
        return Subdirs
    else:
        return False

def check_valid_subdirs(Subdirs, Dir, CorpusOrLanguage):
    Valid = True
    for Subdir in Subdirs:
        if not valid_subdir(CorpusOrLanguage, Subdir, Dir):
            lara_utils.print_and_flush(f'*** Error: {Subdir} is not a permitted subdirectory of {Dir} for a {CorpusOrLanguage} resource')
            Valid = False
    return Valid

def valid_subdir(CorpusOrLanguage, SubDir, Dir):
    if CorpusOrLanguage == 'corpus':
        Result = SubDir in [ 'audio', 'corpus', 'images', 'translations' ] 
    elif CorpusOrLanguage == 'language':
        Result = SubDir in [ 'audio', 'translations', 'corpus' ]
    else:
        lara_utils.print_and_flush(f'*** Error: unknown first argument "{CorpusOrLanguage}" in valid_subdir/2')
        return False
    if not Result:
        #lara_utils.print_and_flush(f'*** Error: unknown subdirectory {SubDir} in {CorpusOrLanguage} resource {Dir}')
        lara_utils.print_and_flush(f'*** Warning: unknown subdirectory "{SubDir}" in {CorpusOrLanguage} resource {Dir}')
    #return Result
    return True
                        
def check_required_subdirs_present(Subdirs, Dir, CorpusOrLanguage):
    Valid = True
    if CorpusOrLanguage == 'corpus':
        for RequiredSubdir in [ 'corpus' ]:
            if not RequiredSubdir in Subdirs:
                lara_utils.print_and_flush(f'*** Error: no {RequiredSubdir} subdirectory of {Dir} found. Required for {CorpusOrLanguage} resource')
                Valid = False
    return Valid

# For a language resource, we are so far only interested in using the audio and translations directories
def add_metadata_to_lara_resource_subdirectory(Subdir, Dir, CorpusOrLanguage):
    if Subdir == 'corpus' and CorpusOrLanguage == 'corpus':
        return add_metadata_to_corpus_directory(Dir)
    elif Subdir == 'images' and CorpusOrLanguage == 'corpus':
        return add_metadata_to_images_directory(Dir)
    elif Subdir == 'audio':
        return add_metadata_to_audio_directory(Dir)
    elif Subdir == 'translations':
        return add_metadata_to_translations_directory(Dir, CorpusOrLanguage)
    else:
        return True

# Metadata content for corpus directory looks like this:
#
# { "config": "local_config.json", corpus: "peter_rabbit.txt" }
#
# Two possible ways to find the corpus:
# 1. It is the only txt file in the directory
# 2. There is a JSON file which identifies it

def add_metadata_to_corpus_directory(Dir):
    CorpusDir = f'{Dir}/corpus'
    MetadataFile = f'{Dir}/corpus/metadata.json'
    TxtFiles = lara_utils.files_with_one_of_given_extensions_in_directory(CorpusDir, ['txt', 'docx'])
    JSONFiles = lara_utils.files_with_one_of_given_extensions_in_directory(CorpusDir, ['json'])
    CSSFiles = lara_utils.files_with_one_of_given_extensions_in_directory(CorpusDir, ['css'])
    JSFiles = lara_utils.files_with_one_of_given_extensions_in_directory(CorpusDir, ['js'])
    if len(TxtFiles) == 0:
        lara_utils.print_and_flush(f'*** Error: no txt or docx files in corpus directory')
        return False
    elif len(JSONFiles) > 0:
        ( CorpusFile, ConfigFile ) = try_to_get_corpus_file_from_config_file_in_list(JSONFiles, CorpusDir)
        if not CorpusFile:
            lara_utils.print_and_flush(f'*** Error: {len(TxtFiles)} txt files in corpus directory but unable to find corpus file')
            return False
        else:
            lara_utils.print_and_flush(f'--- Assuming {CorpusFile}, identified in {ConfigFile}, is the corpus.')
    NotesFiles = get_notes_files_from_config_file_and_dir(ConfigFile, Dir)
    FullConfigFile = f'{CorpusDir}/{ConfigFile}'
    Params = lara_config.read_lara_local_config_file(FullConfigFile)
    # If we have MWEs defined, we combine them with the annotated corpus and use the combined file instead
    if there_are_uncombined_MWE_annotations(Params):
        CorpusFile1 = get_mwe_corpus_file_name(CorpusFile)
        FullCorpusFile1 = f'{CorpusDir}/{CorpusFile1}'
        # It would be cleaner to create a version of the config file that references the MWE corpus file,
        # but if we leave it lying around it will confuse add_metadata next time we call it. So rely on the
        # config file not being used to get the corpus since - since we pass that explicitly it seems safe
        #ConfigFile1 = make_mwe_config_file(FullConfigFile, FullCorpusFile1)
        TraceFile = f'{CorpusDir}/mwe_trace.html'
        lara_top.apply_mwe_annotations_and_copy(FullConfigFile, FullCorpusFile1, TraceFile)
    # Otherwise use the annotated corpus file as is.
    else:
        CorpusFile1 = CorpusFile
    Metadata = { "config": ConfigFile,
                 "corpus": CorpusFile1,
                 "notes": NotesFiles,
                 "css": CSSFiles,
                 "js": JSFiles
                 }
    lara_utils.write_json_to_file(Metadata, MetadataFile)
    return True

def there_are_uncombined_MWE_annotations(Params):
    return Params and \
           Params.mwe_annotations_file and \
           lara_utils.file_exists(Params.mwe_annotations_file) and \
           not there_are_mwes_in_corpus_file(Params)

def there_are_mwes_in_corpus_file(Params):
    Text = lara_utils.read_lara_text_file(Params.corpus)
    if Text.find('#mwe_part_') > 0:
        lara_utils.print_and_flush(f'--- There are already MWE annotations in the corpus file, publish it as is')
        return True
    else:
        lara_utils.print_and_flush(f'--- No MWE annotations in the corpus file, combine it with the MWE annotations file and publish that')
        return False

def get_mwe_corpus_file_name(CorpusFile):
    ( BaseFile, Extension ) = CorpusFile.split('.')
    return f'{BaseFile}_with_MWEs.{Extension}'

##def make_mwe_config_file(FullConfigFile, FullCorpusFile1):
##    ( BaseFile, Extension ) = lara_utils.file_to_base_file_and_extension(FullConfigFile)
##    FullCorpusFile1 = f'{BaseFile}_with_MWEs.{Extension}'
##    Content = lara_utils.read_json_file(FullConfigFile)
##    Content['corpus'] = FullCorpusFile1
##    del Content['mwe_annotations_file']
##    lara_utils.write_json_to_file(Content, FullCorpusFile1)

def get_notes_files_from_config_file_and_dir(ConfigFile0, Dir):
    CorpusDir = f'{Dir}/corpus'
    ConfigFile = f'{CorpusDir}/{ConfigFile0}'
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if not Params:
        lara_utils.print_and_flush(f'*** Error: unable to read config file {ConfigFile}')
        return False
    NotesFile = Params.notes_spreadsheet
    if NotesFile == '':
        return []
    elif not lara_utils.file_exists(NotesFile):
        lara_utils.print_and_flush(f'*** Error: unable to find notes file {NotesFile}')
        return False
    else:
        ReducedNotesFile = NotesFile.split('/')[-1]
        if not lara_utils.file_exists(f'{CorpusDir}/{ReducedNotesFile}'):
            lara_utils.print_and_flush(f'*** Error: notes file {NotesFile} is not in {Dir}')
            return False
        else:
            lara_utils.print_and_flush(f'--- Notes file {NotesFile}, identified in {ConfigFile}, found in {CorpusDir}.')
            return [ ReducedNotesFile ]

# If we've already created metadata in the corpus directory, there will be a JSON file called metadata.json with a "corpus" key.
def try_to_get_corpus_file_from_config_file_in_list(JSONFiles, CorpusDir):
    for JSONFile in JSONFiles:
        try:
            Content = lara_utils.read_json_file(f'{CorpusDir}/{JSONFile}')
            if not JSONFile == 'metadata.json' and type(Content) is dict and 'corpus' in Content:
                FullCorpusFile = Content['corpus']
                if lara_utils.file_exists(FullCorpusFile):
                    CorpusFile = FullCorpusFile.split('/')[-1]
                    return ( CorpusFile, JSONFile )
                else:
                    lara_utils.print_and_flush(f'*** Error: {FullCorpusFile} defined in config file {JSONFile} but not found')
                    return ( False, False )
        except:
            lara_utils.print_and_flush(f'*** Warning: unable to read {JSONFile}')
    return ( False, False )

# Metadata content for images directory looks like this:
#
# 01VeryBigFirTree.jpg
# 02YourFatherHadAnAccident.jpg
# 03DontGetIntoMischief.jpg
#(...)

def add_metadata_to_images_directory(Dir):
    CorpusDir = f'{Dir}/images'
    MetadataFile = f'{Dir}/images/metadata.txt'
    ImageFiles = lara_utils.files_with_one_of_given_extensions_in_directory(CorpusDir, ['jpg', 'jpeg', 'png', 'gif', 'mp4', 'webm'])
    Metadata = ImageFiles
    lara_utils.write_unicode_text_file('\n'.join(Metadata), MetadataFile)
    lara_utils.print_and_flush(f'--- Written images metadata file for {len(ImageFiles)} images, {MetadataFile}')
    return True

# Metadata content for translation directory looks like this:
# {  "french":"english_french.csv", "french_manny":"english_french_manny.csv", "russian":"russian.csv" }
# Keys with an underscore are either <L1>_<UserId> or surface_<L1> or surface_<L1>_<UserId> 

def add_metadata_to_translations_directory(Dir, _CorpusOrLanguage):
    TranslationsDir = f'{Dir}/translations'
    MetadataFile = f'{Dir}/translations/metadata.json'
    CSVFiles = lara_utils.files_with_one_of_given_extensions_in_directory(TranslationsDir, ['csv'])
    Metadata = {}
    for File in CSVFiles:
        Result = csv_file_name_to_key_and_l2(File)
        if not Result:
            lara_utils.print_and_flush(f'*** Warning: CSV file "{File}" in {TranslationsDir} not of form ')
            lara_utils.print_and_flush(f'"<L2>_<L1>", "<L1>_<UserId>", "surface_<L1>" or "surface_<L1>_<UserId>"')
        else:
            L1 = Result[0]
            Metadata[L1] = File
    if len(Metadata) > 0:
        lara_utils.print_and_flush(f'--- {len(Metadata)} translation files found in {TranslationsDir}')
        lara_utils.write_json_to_file(Metadata, MetadataFile)
    else:
        lara_utils.print_and_flush(f'*** Warning: no translation files found in {TranslationsDir}')
    return True

def csv_file_name_to_key_and_l2(File):
    ( BaseFile0, Extension ) = lara_utils.file_to_base_file_and_extension(File)
    BaseFile = BaseFile0.split('/')[-1]
    Components = BaseFile.split('_')
    if Extension == 'csv' and len(Components) == 2:
        ( L2, L1 ) = Components
        return ( L1, L2 )
    elif Extension == 'csv' and len(Components) == 3 and Components[0] == 'type':
        ( Surface, L2, L1 ) = Components
        return ( f'type_{L1}', L2 )
    elif Extension == 'csv' and len(Components) == 3 and Components[0] == 'token':
        ( Surface, L2, L1 ) = Components
        return ( f'token_{L1}', L2 )
    elif Extension == 'csv' and len(Components) == 3:
        ( L2, L1, UserId ) = Components
        return ( f'{L1}_{UserId}', L2 )
    elif Extension == 'csv' and len(Components) == 4 and Components[0] == 'type':
        ( Surface, L2, L1, UserId ) = Components
        return ( f'type_{L1}_{UserId}', L2 )
    elif Extension == 'csv' and len(Components) == 4 and Components[0] == 'token':
        ( Surface, L2, L1, UserId ) = Components
        return ( f'token_{L1}_{UserId}', L2 )
    else:
        return False

# Metadata content for translation directory looks like this:
# [
#  "branislav",
#  "svavar_voice"
# ]

def add_metadata_to_audio_directory(Dir):
    Valid = True
    AudioDir = f'{Dir}/audio'
    MetadataFile = f'{Dir}/audio/metadata.json'
    Subdirs = lara_utils.directory_members_of_directory(AudioDir)
    Metadata = Subdirs
    if len(Metadata) > 0:
        lara_utils.write_json_to_file(Metadata, MetadataFile)
        for Subdir in Subdirs:
            Result = check_metadata_in_audio_voice_directory(f'{AudioDir}/{Subdir}')
            if not Result:
                Valid = False
    return Valid

# Audio metadata file content looks like this:
# AudioOutput help any_speaker help/50768_181219203839.wav Once upon a time there were four little Rabbits, and their names were-- Flopsy, Mopsy, Cotton-tail, and Peter.# |
# AudioOutput help any_speaker help/50769_181219201554.wav They lived with their Mother in a sand-bank, underneath the root of a very big fir-tree.# |
# (...)

def check_metadata_in_audio_voice_directory(VoiceDir):
    if not lara_utils.directory_exists(VoiceDir):
        lara_utils.print_and_flush(f'*** Warning: {VoiceDir} not found')
        return True
    RealAudioFiles = lara_utils.files_with_one_of_given_extensions_in_directory(VoiceDir, ['wav', 'mp3', 'mp4', 'webm'])
    ParsedAudioMetadata = lara_audio.read_ldt_metadata_file(VoiceDir)
    if not isinstance(ParsedAudioMetadata, list) or ( len(ParsedAudioMetadata) == 0 and len(ParsedAudioMetadata) > 0 ):
        lara_utils.print_and_flush(f'*** Error: there are audio files in {VoiceDir}, but no metadata found')
        return False
    MetadataAudioFiles = [ Item['file'] for Item in ParsedAudioMetadata if 'file' in Item ]
    NErrors = compare_real_wavfiles_with_metadata_wavfiles(RealAudioFiles, MetadataAudioFiles)
    if NErrors > 0:
        lara_utils.print_and_flush(f'*** Warning: audio metadata not completely correct, {NErrors} warnings.')
        return True
    else:
        lara_utils.print_and_flush(f'--- Checked audio directory {VoiceDir}. The {len(RealAudioFiles)} audio files match the metadata.')
        return True

def get_files_from_audio_metadata_lines(Lines):
    return [ lara_parse_utils.parse_ldt_metadata_file_line(Line)[0] for Line in Lines if lara_parse_utils.parse_ldt_metadata_file_line(Line) ]

def compare_real_wavfiles_with_metadata_wavfiles(RealWavfiles, MetadataWavfiles):
    NErrors = 0
    for File in RealWavfiles:
        if not File in MetadataWavfiles:
            lara_utils.print_and_flush(f'*** Warning: {File} not listed in metadata')
            NErrors += 1
    for File in MetadataWavfiles:
        if not File in RealWavfiles:
            lara_utils.print_and_flush(f'*** Warning: {File} listed in metadata but not found')
            NErrors += 1
    return NErrors

# -----------------------------------------------


