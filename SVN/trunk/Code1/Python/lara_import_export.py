
import lara_config
import lara_utils

def init_trace():
    global Trace
    Trace = []

def print_and_trace(Str):
    global Trace
    lara_utils.print_and_flush(Str)
    Trace.append(Str)

def copy_file_and_trace(File1, File2):
    if not lara_utils.file_exists(File1):
        print_and_trace(f'*** Warning: file not found: {File1}')
        return
    Result = lara_utils.copy_file(File1, File2)
    if not Result or not lara_utils.file_exists(File2):
        print_and_trace(f'*** Warning: something went wrong in copying')
    else:
        print_and_trace(f'--- File copied to {File2}')

def print_trace_to_file(File):
    global Trace
    lara_utils.write_unicode_text_file('\n'.join(Trace), File)

def make_export_zipfile(ConfigFile, Zipfile):
    init_trace()
    print_and_trace(f'--- Making export zipfile for {ConfigFile}')
    # We read the config file as a piece of JSON because we don't want the default values filled in,
    # they just cause trouble.
    if not lara_utils.file_exists(ConfigFile):
        print_and_trace(f'*** Error: cannot find config file {ConfigFile}')
        return False
    Params = lara_utils.read_json_file(ConfigFile)
    if not Params:
        print_and_trace(f'*** Error: cannot read config file {ConfigFile}')
        return False
    if lara_config.bad_values_in_config_data(Params):
        print_and_trace(f'*** Error: bad values in {ConfigFile}, file is probably out of date')
        return False
    if not 'language' in Params:
        print_and_trace(f'*** Error: "language" not defined in {ConfigFile}')
        return False
    Id = Params['id']
    CorpusDir = lara_utils.directory_for_pathname(ConfigFile)
    # but here we read it normally a second time, since we're doing it to get the working directories
    TmpDirTop = lara_utils.get_tmp_directory(lara_config.read_lara_local_config_file(ConfigFile))
    TmpDir = f'{TmpDirTop}/{Id}'
    lara_utils.create_directory(TmpDir)
    lara_utils.create_directory(f'{TmpDir}/audio')
    lara_utils.create_directory(f'{TmpDir}/corpus')
    lara_utils.create_directory(f'{TmpDir}/images')
    lara_utils.create_directory(f'{TmpDir}/translations')
    Params1 = {}
    for Key in Params:
        Value1 = process_config_element_for_export(Key, Params, TmpDir)
        if Value1 == False:
            print_and_trace(f'*** Error: processing failed for {Key}')
            return False
        if not Value1 == '*irrelevant*':
            Params1[Key] = Value1
    print_and_trace(f'--- Creating config file')
    lara_utils.write_json_to_file(Params1, f'{TmpDir}/corpus/local_config.json')
    NCSSAndJSFiles = lara_utils.number_of_directory_files_with_extension(CorpusDir, ['css', 'js'])
    print_and_trace(f'--- Copying CSS and JS files ({NCSSAndJSFiles} files)')
    lara_utils.copy_directory_one_file_at_a_time(CorpusDir, f'{TmpDir}/corpus', ['css', 'js'])
    print_trace_to_file(f'{TmpDir}/corpus/trace.txt')
    lara_utils.print_and_flush(f'--- Making zipfile')
    lara_utils.make_zipfile(TmpDirTop, Zipfile)
    lara_utils.delete_directory_if_it_exists(TmpDirTop)
    return True

def process_config_element_for_export(Key, Params, TmpDir):
    Value = Params[Key]
    if Key in [ 'compiled_directory', 'lara_tmp_directory', 'working_tmp_directory',
                'word_pages_directory',
                'tagged_corpus', 'postags_file' ]:
        return '*irrelevant*'
    elif Key == 'corpus':
        return process_corpus_file_for_export(Value, TmpDir)
    elif Key == 'untagged_corpus':
        return process_untagged_corpus_file_for_export(Value, TmpDir)
    elif Key == 'image_directory':
        return process_image_directory_for_export(Value, TmpDir)
    elif Key == 'segment_translation_spreadsheet':
        return process_segment_translation_spreadsheet_for_export(Value, TmpDir)
    elif Key in [ 'translation_spreadsheet', 'translation_spreadsheet_surface' ]:
        return process_word_translation_spreadsheet_for_export(Value, TmpDir)
    elif Key == 'translation_spreadsheet_tokens':
        return process_word_token_translation_spreadsheet_for_export(Value, TmpDir)
    elif Key == 'notes_spreadsheet':
        return process_notes_spreadsheet_for_export(Value, TmpDir)
    elif Key == 'segment_audio_directory':
        return process_segment_audio_directory_for_export(Value, TmpDir)
    elif Key == 'audio_tracking_file':
        return process_audio_tracking_file_for_export(Value, TmpDir)
    elif Key == 'word_audio_directory':
        return process_word_audio_directory_for_export(Value, TmpDir)
    elif Key == 'mwe_file':
        return process_mwe_defs_file_for_export(Value, TmpDir)
    elif Key == 'mwe_annotations_file':
        return process_mwe_annotations_file_for_export(Value, TmpDir)
    else:
        return Value

def process_corpus_file_for_export(CorpusFile, TmpDir):
    print_and_trace(f'--- Copying corpus file: {CorpusFile}')
    BaseName = lara_utils.base_name_for_pathname(CorpusFile)
    copy_file_and_trace(CorpusFile, f'{TmpDir}/corpus/{BaseName}')
    return f'*CORPUS_DIR*/corpus/{BaseName}'

def process_untagged_corpus_file_for_export(CorpusFile, TmpDir):
    print_and_trace(f'--- Copying untagged corpus file: {CorpusFile}')
    BaseName = lara_utils.base_name_for_pathname(CorpusFile)
    copy_file_and_trace(CorpusFile, f'{TmpDir}/corpus/{BaseName}')
    return f'*CORPUS_DIR*/corpus/{BaseName}'

def process_segment_translation_spreadsheet_for_export(Spreadsheet, TmpDir):
    print_and_trace(f'--- Copying segment translation spreadsheet: "{Spreadsheet}"')
    if Spreadsheet == '':
        print_and_trace(f'--- Not processing because null value')
        return '*irrelevant*'
    BaseName = lara_utils.base_name_for_pathname(Spreadsheet)
    copy_file_and_trace(Spreadsheet, f'{TmpDir}/translations/{BaseName}')
    return f'*CORPUS_DIR*/translations/{BaseName}'

def process_word_token_translation_spreadsheet_for_export(Spreadsheet, TmpDir):
    print_and_trace(f'--- Copying word token translation spreadsheet: "{Spreadsheet}"')
    if Spreadsheet == '':
        print_and_trace(f'--- Not processing because null value')
        return '*irrelevant*'
    BaseName = lara_utils.base_name_for_pathname(Spreadsheet)
    copy_file_and_trace(Spreadsheet, f'{TmpDir}/translations/{BaseName}')
    return f'*CORPUS_DIR*/translations/{BaseName}'

def process_notes_spreadsheet_for_export(Spreadsheet, TmpDir):
    print_and_trace(f'--- Copying notes spreadsheet: "{Spreadsheet}"')
    if Spreadsheet == '':
        print_and_trace(f'--- Not processing because null value')
        return '*irrelevant*'
    BaseName = lara_utils.base_name_for_pathname(Spreadsheet)
    copy_file_and_trace(Spreadsheet, f'{TmpDir}/corpus/{BaseName}')
    return f'*CORPUS_DIR*/corpus/{BaseName}'

_image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'mp4', 'webm']

def process_image_directory_for_export(Dir, TmpDir):
    NFiles = lara_utils.number_of_directory_files_with_extension(Dir, _image_extensions)
    print_and_trace(f'--- Copying image directory ({NFiles} files) "{Dir}"')
    lara_utils.copy_directory_one_file_at_a_time(Dir, f'{TmpDir}/images', _image_extensions)
    return f'*CORPUS_DIR*/images'

_audio_extensions = ['mp3', 'wav', 'webm', 'txt', 'json']

def process_segment_audio_directory_for_export(Dir, TmpDir):
    NFiles = lara_utils.number_of_directory_files_with_extension(Dir, _audio_extensions)
    print_and_trace(f'--- Copying segment audio directory ({NFiles} files) "{Dir}"')
    BaseName = lara_utils.base_name_for_pathname(Dir)
    if BaseName == 'audio':
        print_and_trace(f'--- Not processing because pathname ends in "audio"')
        return '*irrelevant*'
    lara_utils.create_directory(f'{TmpDir}/audio/{BaseName}')
    lara_utils.copy_directory_one_file_at_a_time(Dir, f'{TmpDir}/audio/{BaseName}', _audio_extensions)
    return f'*CORPUS_DIR*/audio/{BaseName}'

def process_audio_tracking_file_for_export(File, TmpDir):
    print_and_trace(f'--- Processing declaration for audio tracking file: "{File}"')
    if File == '':
        print_and_trace(f'--- Not processing because null value')
        return '*irrelevant*'
    Components = File.split('/')
    if len(Components) >= 4 and Components[-3] == 'audio' and lara_utils.extension_for_file(File) == 'json':
        return f'*CORPUS_DIR*/audio/{Components[-2]}/{Components[-1]}'
    else:
        print_and_trace(f'*** Error: audio tracking file pathname not of form "*CORPUS_DIR*/audio/<Voice>/<File>.json"')

def process_word_translation_spreadsheet_for_export(Spreadsheet, TmpDir):
    print_and_trace(f'--- Processing word translation spreadsheet "{Spreadsheet}"')
    if Spreadsheet == '':
        print_and_trace(f'--- Not processing because null value')
        return '*irrelevant*'
    Components = Spreadsheet.split('/')
    return f"*LANGUAGE_DIR*/{'/'.join(Components[-2:])}" if len(Components) >= 2 else '*irrelevant*'

def process_word_audio_directory_for_export(Dir, TmpDir):
    print_and_trace(f'--- Processing word audio directory "{Dir}"')
    if Dir == '':
        print_and_trace(f'--- Not processing because null value')
        return '*irrelevant*'
    Components = Dir.split('/')
    return f"*LANGUAGE_DIR*/{'/'.join(Components[-2:])}" if len(Components) >= 2 else '*irrelevant*'

def process_mwe_defs_file_for_export(File, TmpDir):
    print_and_trace(f'--- Processing MWE defs file "{File}"')
    if File == '':
        print_and_trace(f'--- Not processing because null value')
        return '*irrelevant*'
    Components = File.split('/')
    return f"*LANGUAGE_DIR*/{'/'.join(Components[-2:])}" if len(Components) >= 2 else '*irrelevant*'

def process_mwe_annotations_file_for_export(AnnotationsFile, TmpDir):
    print_and_trace(f'--- Copying MWE annotations file: {AnnotationsFile}')
    if AnnotationsFile == '':
        print_and_trace(f'--- Not processing because null value')
        return '*irrelevant*'
    BaseName = lara_utils.base_name_for_pathname(AnnotationsFile)
    copy_file_and_trace(AnnotationsFile, f'{TmpDir}/corpus/{BaseName}')
    return f'*CORPUS_DIR*/corpus/{BaseName}'

# ----------------------------------------------

def import_zipfile(Zipfile, CorpusDir, LanguageRootDir, ConfigFile):
    Params = lara_config.read_lara_local_config_file_dont_check_directories(ConfigFile)
    if not Params:
        return False
    TmpDir = lara_utils.get_tmp_directory(Params)
    if not lara_utils.unzip_file(Zipfile, TmpDir):
        print_and_trace(f'*** Error: unable to unzip file: {Zipfile}')
        return False
    lara_utils.delete_directory_if_it_exists(CorpusDir)
    UnzippedSubdirs = lara_utils.directory_members_of_directory(TmpDir)
    if not len(UnzippedSubdirs) == 1:
        lara_utils.print_and_flush(f'*** Error: {len(UnzippedSubdirs)} directories in {Zipfile}')
        return False
    MainUnzippedDir = f'{TmpDir}/{UnzippedSubdirs[0]}'
    if not lara_utils.move(MainUnzippedDir, CorpusDir):
        lara_utils.print_and_flush(f'*** Error: unable to moved unzipped director {MainUnzippedDir} to {CorpusDir}')
        return False
    if not correct_config_file_in_imported_zipfile(CorpusDir, LanguageRootDir):
        lara_utils.print_and_flush(f'*** Error: unable to correct config file in {CorpusDir}')
        return False
    lara_utils.delete_directory_if_it_exists(TmpDir)
    lara_utils.print_and_flush(f'--- Unpacked and installed zipfile to {CorpusDir}')
    return True

def correct_config_file_in_imported_zipfile(CorpusDir, LanguageRootDir):
    if not lara_utils.directory_exists(CorpusDir):
        lara_utils.print_and_flush(f'*** Error: {CorpusDir} is not a directory')
        return False
    if not lara_utils.directory_exists(LanguageRootDir):
        lara_utils.print_and_flush(f'*** Error: {LanguageRootDir} is not a directory')
        return False
    ConfigFile = f'{CorpusDir}/corpus/local_config.json'
    if not lara_utils.file_exists(ConfigFile):
        lara_utils.print_and_flush(f'*** Error: unable to find {ConfigFile}')
        return False
    ConfigFileContent = lara_utils.read_json_file(ConfigFile)
    if not ConfigFileContent:
        lara_utils.print_and_flush(f'*** Error: unable to read {ConfigFile}')
        return False
    ConfigFileContent1 = correct_config_file_content(ConfigFileContent, CorpusDir, LanguageRootDir)
    if not ConfigFileContent1:
        lara_utils.print_and_flush(f'*** Error: unable to update {ConfigFile} content')
        return False
    if not lara_utils.write_json_to_file(ConfigFileContent1, ConfigFile):
        lara_utils.print_and_flush(f'*** Error: unable to write out updated {ConfigFile}')
        return False
    return True

def correct_config_file_content(ConfigFileContent, CorpusDir, LanguageRootDir):
    try:
        if not 'language' in ConfigFileContent:
            lara_utils.print_and_flush(f'*** Error: "language" is not defined in the config file')
            return False
        Language = ConfigFileContent['language']
        LanguageDir = f'{LanguageRootDir}/{Language}'
        ConfigFileContent1 = {}
        for Key in ConfigFileContent:
            Value1 = correct_config_file_value(Key, ConfigFileContent[Key], CorpusDir, LanguageDir)
            if Value1 == '*error*':
                return False
            ConfigFileContent1[Key] = Value1
        lara_utils.print_and_flush(f'--- Updated config file to match corpus dir {CorpusDir} and language dir {LanguageDir}')
        return ConfigFileContent1
    except Exception as e:
        lara_utils.print_and_flush(f'*** Error: something went wrong when updating config file content')
        lara_utils.print_and_flush(str(e))
        return False

def correct_config_file_value(Key, Value, CorpusDir, LanguageDir):
    try:
        return Value.replace('*CORPUS_DIR*', CorpusDir).replace('*LANGUAGE_DIR*', LanguageDir) if isinstance(Value, str) else Value
    except Exception as e:
        lara_utils.print_and_flush(f'*** Error: bad value "{Value}" for key "{Key}" in config file content')
        lara_utils.print_and_flush(str(e))
        return '*error*'

