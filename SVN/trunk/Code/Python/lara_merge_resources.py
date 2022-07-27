import lara_config
import lara_audio
import lara_install_audio_zipfile
import lara_translations
import lara_utils
import lara_add_metadata
import lara_mwe
import time

# Merge two language resources to create a new language resource
# We need the config file to say where the tmp directory is

def merge_language_resources(Dir1, Dir2, Dir12, ConfigFile):
    try:
        return merge_language_resources_main(Dir1, Dir2, Dir12, ConfigFile)
    except Exception as e:
        lara_utils.print_and_flush(f'*** Error: something went wrong when trying to merge {Dir1} and {Dir2} to {Dir12}')
        lara_utils.print_and_flush(str(e))
        return False

def merge_language_resources_main(Dir1, Dir2, Dir12, ConfigFile):
    if not check_valid_language_resource(Dir1):
        return False
    if not check_valid_language_resource(Dir2):
        return False
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if not Params:
        return False
    if not lara_utils.create_directory_deleting_old_if_necessary(Dir12):
        lara_utils.print_and_flush(f'*** Error: unable to create target directory {Dir12}')
        return False
    if not merge_language_resources_audio(Dir1, Dir2, Dir12):
        lara_utils.print_and_flush(f'*** Error: unable to merge audio directories')
        return False
    if not merge_language_resources_translations(Dir1, Dir2, Dir12, Params):
        lara_utils.print_and_flush(f'*** Error: unable to merge translation directories')
        return False
    if not merge_language_resources_corpus(Dir1, Dir2, Dir12, Params):
        lara_utils.print_and_flush(f'*** Error: unable to merge corpus directories')
        return False
    lara_utils.print_and_flush(f'--- Successfully merged language resources {Dir1} and {Dir2} to {Dir12}')

def check_valid_language_resource(Dir):
    if not lara_add_metadata.add_metadata_to_lara_resource_directory(Dir, 'language'):
        lara_utils.print_and_flush(f'*** Error: unable to add metadata to {Dir}, probably there is something wrong with the resource')
        return False
    else:
        lara_utils.print_and_flush(f'--- Able to add metadata to {Dir}, assuming resource is okay')
        return True

_valid_audio_file_extensions = ['mp3', 'wav', 'webm']

_valid_audio_file_extensions_including_metadata = ['mp3', 'wav', 'webm', 'txt', 'json']

def merge_language_resources_audio(Dir1, Dir2, Dir12):
    AudioDir1 = f'{Dir1}/audio'
    AudioDir2 = f'{Dir2}/audio'
    AudioDir12 = f'{Dir12}/audio'
    lara_utils.create_directory_if_it_doesnt_exist(AudioDir12)
    VoiceDirs1 = lara_utils.directory_members_of_directory(AudioDir1) if lara_utils.directory_exists(AudioDir1) else []
    VoiceDirs2 = lara_utils.directory_members_of_directory(AudioDir2) if lara_utils.directory_exists(AudioDir2) else []
    # Just copy the voice directories directly that are in one audio directory but not the other
    for VoiceDir in [ Dir for Dir in VoiceDirs1 if not Dir in VoiceDirs2 ]:
        Target = f'{AudioDir12}/{VoiceDir}'
        if not lara_utils.create_directory_if_it_doesnt_exist(Target):
            lara_utils.print_and_flush(f'*** Error: unable to create directory {Target}')
            return False
        lara_utils.copy_directory_one_file_at_a_time(f'{AudioDir1}/{VoiceDir}', Target, _valid_audio_file_extensions_including_metadata)
        lara_utils.print_and_flush(f'--- Copied {VoiceDir} from {AudioDir1} to {AudioDir12}')
    for VoiceDir in [ Dir for Dir in VoiceDirs2 if not Dir in VoiceDirs1 ]:
        Target = f'{AudioDir12}/{VoiceDir}'
        if not lara_utils.create_directory_if_it_doesnt_exist(Target):
            lara_utils.print_and_flush(f'*** Error: unable to create directory {Target}')
            return False
        lara_utils.copy_directory_one_file_at_a_time(f'{AudioDir2}/{VoiceDir}', Target, _valid_audio_file_extensions_including_metadata)
        lara_utils.print_and_flush(f'--- Copied {VoiceDir} from {AudioDir2} to {AudioDir12}')
    # If they're in both directories, we have to merge them
    for VoiceDir in [ Dir for Dir in VoiceDirs1 if Dir in VoiceDirs2 ]:
        Target = f'{AudioDir12}/{VoiceDir}'
        if not lara_utils.create_directory_if_it_doesnt_exist(Target):
            lara_utils.print_and_flush(f'*** Error: unable to create directory {Target}')
            return False
        merge_language_resources_audio1(f'{AudioDir1}/{VoiceDir}', f'{AudioDir2}/{VoiceDir}', Target)
    return True

def merge_language_resources_audio1(Dir1, Dir2, Dir12):
    lara_utils.copy_directory_one_file_at_a_time(Dir1, Dir12, _valid_audio_file_extensions)
    Metadata1 = lara_audio.read_ldt_metadata_file(Dir1)
    lara_utils.copy_directory_one_file_at_a_time(Dir2, Dir12, _valid_audio_file_extensions)
    Metadata2 = lara_audio.read_ldt_metadata_file(Dir2)
    #Metadata12 = lara_utils.remove_duplicates(Metadata1 + Metadata2)
    Metadata12 = lara_install_audio_zipfile.clean_audio_metadata(Metadata1 + Metadata2)
    lara_audio.write_ldt_metadata_file(Metadata12, Dir12)
    lara_utils.print_and_flush(f'--- Merged audio directories {Dir1} and {Dir2} to {Dir12}')

def merge_language_resources_translations(Dir1, Dir2, Dir12, Params):
    TranslationDir1 = f'{Dir1}/translations'
    TranslationDir2 = f'{Dir2}/translations'
    TranslationDir12 = f'{Dir12}/translations'
    lara_utils.create_directory_if_it_doesnt_exist(TranslationDir12)
    TranslationCVS1 = lara_utils.files_with_given_extension_in_directory(TranslationDir1, 'csv')
    TranslationCVS2 = lara_utils.files_with_given_extension_in_directory(TranslationDir2, 'csv')
    FilesOnlyInDir1 = [ F for F in TranslationCVS1 if not F in TranslationCVS2 ]
    FilesOnlyInDir2 = [ F for F in TranslationCVS2 if not F in TranslationCVS1 ]
    FilesInBothDirs = [ F for F in TranslationCVS1 if F in TranslationCVS2 ]
    for File in FilesOnlyInDir1:
        lara_utils.copy_file_with_feedback(f'{TranslationDir1}/{File}', f'{TranslationDir12}/{File}')
    if len(FilesOnlyInDir1) > 0:
        lara_utils.print_and_flush(f'--- Copied {len(FilesOnlyInDir1)} spreadsheets from {TranslationDir1} to {TranslationDir12}')
    for File in FilesOnlyInDir2:
        lara_utils.copy_file_with_feedback(f'{TranslationDir2}/{File}', f'{TranslationDir12}/{File}')
    if len(FilesOnlyInDir2) > 0:
        lara_utils.print_and_flush(f'--- Copied {len(FilesOnlyInDir2)} spreadsheets from {TranslationDir2} to {TranslationDir12}')
    for File in FilesInBothDirs:
        TmpFile = lara_utils.get_tmp_trace_file(Params)
        merge_translation_spreadsheets(f'{TranslationDir1}/{File}', f'{TranslationDir2}/{File}', TmpFile)
        lara_utils.copy_file_with_feedback(TmpFile, f'{TranslationDir12}/{File}')
        lara_utils.delete_file_if_it_exists(TmpFile)
    if len(FilesInBothDirs) > 0:
        lara_utils.print_and_flush(f'--- Merged {len(FilesInBothDirs)} spreadsheets from {TranslationDir1} and {TranslationDir2} to {TranslationDir12}')
    return True

def safe_merge_and_replace_spreadsheet(Spreadsheet, UpdateSpreadsheet):
    Lockfile = wait_until_file_is_unlocked_then_lock_it(Spreadsheet)
    if not Lockfile:
        lara_utils.print_and_flush(f'*** Error: unable to obtain lockfile for {Spreadsheet}')
        return False
    else:
        lara_utils.print_and_flush(f'--- safe_merge_and_replace_spreadsheet: obtained lockfile {Lockfile}')
    try:
        merge_translation_spreadsheets(Spreadsheet, UpdateSpreadsheet, Spreadsheet)
        lara_utils.delete_file_if_it_exists(Lockfile)
        return True
    except Exception as e:
        lara_utils.print_and_flush(f'*** Error: something went wrong in "safe_merge_and_replace_spreadsheet({Spreadsheet}, {UpdateSpreadsheet})"')
        lara_utils.print_and_flush(str(e))
        lara_utils.delete_file_if_it_exists(Lockfile)
        return False
        
def merge_translation_spreadsheets(Spreadsheet1, Spreadsheet2, Spreadsheet12):
    Data1 = lara_utils.read_lara_csv(Spreadsheet1)
    Data2 = lara_utils.read_lara_csv(Spreadsheet2)
    if Data1 == False or Data2 == False:
        lara_utils.print_and_flush(f'*** Warning: unable to carry out merge, one of the spreadsheets is missing')
    else:
        Merged = merge_spreadsheet_data(Data1, Data2)
        lara_utils.write_lara_csv(Merged, Spreadsheet12)

def merge_spreadsheet_data(Lines1, Lines2):
    Dict1 = { Line[0]: Line[1:] for Line in Lines1 if not trivial_translation_spreadsheet_line(Line) }
    Dict2 = { Line[0]: Line[1:] for Line in Lines2 if not trivial_translation_spreadsheet_line(Line) }
    Dict12 = lara_utils.merge_dicts(Dict1, Dict2)
    return [ [ Key ] + Dict12[Key] for Key in Dict12 ]

def trivial_translation_spreadsheet_line(Line):
    return len(Line) == 0 or Line[0] == '' or Line[0].isspace()

# ------------------------------------------------------------

def merge_language_resources_corpus(Dir1, Dir2, Dir12, Params):
    CorpusDir1 = f'{Dir1}/corpus'
    CorpusDir2 = f'{Dir2}/corpus'
    MWEFile1 = find_mwe_defs_file_in_dir(CorpusDir1)
    MWEFile2 = find_mwe_defs_file_in_dir(CorpusDir2)
    MWEFile12 = f'{Dir12}/corpus/mwe_defs.txt'
    CorpusDir12 = f'{Dir12}/corpus'
    lara_utils.create_directory_if_it_doesnt_exist(CorpusDir12)
    # There are no MWE defs files, nothing to do
    if not MWEFile1 and not MWEFile2:
        return True
    # Only one file, copy it
    elif not MWEFile1:
        return lara_utils.copy_file_with_feedback(MWEFile2, MWEFile12)
    elif not MWEFile2:
        return lara_utils.copy_file_with_feedback(MWEFile1, MWEFile12)
    # Nontrivial case: we need to merge two files
    else:
        return merge_mwe_defs_files(MWEFile1, MWEFile2, MWEFile12, Params)

def find_mwe_defs_file_in_dir(Dir):
    TxtFiles = lara_utils.files_with_given_extension_in_directory(Dir, 'txt')
    PossibleMWEDefsFiles = [ f'{Dir}/{File}' for File in TxtFiles if lara_mwe.read_mwe_file(f'{Dir}/{File}') ]
    if len(PossibleMWEDefsFiles) == 0:
        lara_utils.print_and_flush(f'--- Found no MWE defs file in {Dir}')
        return False
    elif len(PossibleMWEDefsFiles) > 1:
        lara_utils.print_and_flush(f'*** Error: more than one MWE defs file in {Dir}')
        return False
    else:
        File = PossibleMWEDefsFiles[0]
        lara_utils.print_and_flush(f'--- Found one MWE defs file in {Dir}, {File}')
        return File

def safe_merge_and_replace_mwe_defs_file(MWEFile, UpdateMWEFile, ConfigFile):
    Lockfile = wait_until_file_is_unlocked_then_lock_it(MWEFile)
    if not Lockfile:
        lara_utils.print_and_flush(f'*** Error: unable to obtain lockfile for {MWEFile}')
        return False
    else:
        lara_utils.print_and_flush(f'--- safe_merge_and_replace_mwe_defs: obtained lockfile {Lockfile}')
    try:
        Params = lara_config.read_lara_local_config_file(ConfigFile)
        if not Params:
            return False
        merge_mwe_defs_files(MWEFile, UpdateMWEFile, MWEFile, Params)
        lara_utils.delete_file_if_it_exists(Lockfile)
        return True
    except Exception as e:
        lara_utils.print_and_flush(f'*** Error: something went wrong in "safe_merge_and_replace_mwe_defs_file({MWEFile}, {UpdateMWEFile})"')
        lara_utils.print_and_flush(str(e))
        lara_utils.delete_file_if_it_exists(Lockfile)
        return False

def merge_mwe_defs_files(MWEFile1, MWEFile2, MWEFile12, Params):
    TmpMWEJSONFile1 = lara_utils.get_tmp_json_file(Params)
    TmpMWEJSONFile2 = lara_utils.get_tmp_json_file(Params)
    TmpMWEJSONFile12 = lara_utils.get_tmp_json_file(Params)
    ConvertResult1 = lara_mwe.mwe_txt_file_to_json(MWEFile1, TmpMWEJSONFile1)
    if not ConvertResult1:
        lara_utils.print_and_flush(f'*** Error: unable to convert {MWEFile1} to JSON')
        return False
    ConvertResult2 = lara_mwe.mwe_txt_file_to_json(MWEFile2, TmpMWEJSONFile2)
    if not ConvertResult2:
        lara_utils.print_and_flush(f'*** Error: unable to convert {MWEFile2} to JSON')
        return False
    JSONContents1 = lara_utils.read_json_file(TmpMWEJSONFile1)
    JSONContents2 = lara_utils.read_json_file(TmpMWEJSONFile2)
    JSONContents12 = { 'mwes': lara_utils.merge_dicts(JSONContents1['mwes'], JSONContents2['mwes']),
                       'classes': lara_utils.merge_dicts(JSONContents1['classes'], JSONContents2['classes']),
                       'transforms': lara_utils.remove_duplicates(JSONContents1['transforms'] + JSONContents2['transforms'])
                       }
    lara_utils.write_json_to_file(JSONContents12, TmpMWEJSONFile12)
    lara_mwe.mwe_json_file_to_txt(TmpMWEJSONFile12, MWEFile12)
    lara_utils.delete_file_if_it_exists(TmpMWEJSONFile1)
    lara_utils.delete_file_if_it_exists(TmpMWEJSONFile2)
    lara_utils.delete_file_if_it_exists(TmpMWEJSONFile12)
    return True
                                                        
# ------------------------------------------------------------

def find_deleted_lines_in_translation_spreadsheet_and_write(OldSpreadsheet, NewSpreadsheet, AnswerFile):
    N = find_deleted_lines_in_translation_spreadsheet(OldSpreadsheet, NewSpreadsheet)
    lara_utils.write_json_to_file(N, AnswerFile)
    lara_utils.print_and_flush(f'--- Written answer ({N} lines deleted) to {AnswerFile}')

def find_deleted_lines_in_word_token_spreadsheet_and_write(OldSpreadsheet, NewSpreadsheet, AnswerFile):
    N = find_deleted_lines_in_word_token_spreadsheet(OldSpreadsheet, NewSpreadsheet)
    lara_utils.write_json_to_file(N, AnswerFile)
    lara_utils.print_and_flush(f'--- Written answer ({N} lines deleted) to {AnswerFile}')

def find_deleted_lines_in_translation_spreadsheet(OldSpreadsheet, NewSpreadsheet):
    Lines1 = lara_utils.read_lara_csv(OldSpreadsheet)
    Lines2 = lara_utils.read_lara_csv(NewSpreadsheet)
    if not Lines1 or not Lines2:
        return 0
    Dict1 = { Line[0]: Line[1:] for Line in Lines1 if not trivial_translation_spreadsheet_line(Line) }
    Dict2 = { Line[0]: Line[1:] for Line in Lines2 if not trivial_translation_spreadsheet_line(Line) }
    DeletedLines = [ Key for Key in Dict2 if \
                     Key in Dict1 and \
                     trivial_translation_spreadsheet_line(Dict2[Key]) and \
                     not trivial_translation_spreadsheet_line(Dict1[Key]) ]
    return len(DeletedLines)

def find_deleted_lines_in_word_token_spreadsheet(OldSpreadsheet, NewSpreadsheet):
    Lines1 = lara_translations.read_word_token_spreadsheet_file(OldSpreadsheet, 'remove_mwe_markings')
    Lines2 = lara_translations.read_word_token_spreadsheet_file(NewSpreadsheet, 'remove_mwe_markings')
    if not Lines1 or not Lines2:
        return 0
    Dict1 = { tuple(Line[0]): Line[1] for Line in Lines1 }
    Dict2 = { tuple(Line[0]): Line[1] for Line in Lines2 }
    DeletedLines = [ Key for Key in Dict2 if \
                     Key in Dict1 and \
                     trivial_translation_spreadsheet_line(Dict2[Key]) and \
                     not trivial_translation_spreadsheet_line(Dict1[Key]) ]
    return len(DeletedLines)

# ------------------------------------------------------------

def wait_until_file_is_unlocked_then_lock_it(Spreadsheet):
    _maxattempts = 100
    ( Lockfile, NAttempts ) = ( lockfile_for_file(Spreadsheet), 0 )
    while file_is_locked_according_to_lockfile(Lockfile):
        time.sleep(0.1)
        NAttempts += 1
        if NAttempts > _maxattempts:
            lara_utils.print_and_flush(f'*** Error: could not obtain lockfile {Lockfile} after {_maxattempts} attempts, giving up')
            return False
    lara_utils.write_lara_text_file('Locked', Lockfile)
    return Lockfile

def lockfile_for_file(File):
    ( Base, Ext ) = lara_utils.file_to_base_file_and_extension(File)
    return f'{Base}_{Ext}_lockfile.txt'

def file_is_locked_according_to_lockfile(Lockfile):
    _max_number_of_seconds_file_can_be_locked = 60
    # If there is no lockfile, we are good to go
    if not lara_utils.file_exists(Lockfile):
        return False
    # If there is an old lockfile, assume something went wrong before it could be deleted
    if lara_utils.file_age_in_seconds(Lockfile) > _max_number_of_seconds_file_can_be_locked:
        return False
    # Otherwise assume file is still locked
    return True 

                                                          

    
