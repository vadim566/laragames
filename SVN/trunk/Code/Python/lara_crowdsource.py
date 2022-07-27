
import lara_config
import lara_import_export
import lara_audio
import lara_utils
import copy

_cut_tag = '<cut>'

def test(Id):
    if Id == 'cut_up_father_william':
        ConfigFile = '$LARA/Content/father_william/corpus/local_config.json'
        MasterZipfile = '$LARA/tmp/father_william_crowdsouce.zip'
        cut_up_project(ConfigFile, MasterZipfile)
    elif Id == 'stick_together_father_william':
        FileWithListOfConfigFiles = '$LARA/tmp/father_william_collected_config_files.json'
        ListOfConfigFiles = [ '$LARA/Content/father_william_0/corpus/local_config.json',
                              '$LARA/Content/father_william_1/corpus/local_config.json' ]
        lara_utils.write_json_to_file(ListOfConfigFiles, FileWithListOfConfigFiles)
        ConfigFile = '$LARA/Content/father_william/corpus/local_config.json'
        stick_together_projects(FileWithListOfConfigFiles, ConfigFile)
    else:
        lara_utils.print_and_flush(f'*** Error: unknown Id "{Id}"')

# ------------------------------------------

def cut_up_project(ConfigFile, MasterZipfile):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if Params == False:
        lara_utils.print_and_flush(f'*** Error: unable to read {ConfigFile}')
        return False
    Id = Params.id
    CorpusFile = Params.corpus
    Text = lara_utils.read_lara_text_file(CorpusFile)
    TextComponents = Text.split(_cut_tag)
    NComponents = len(TextComponents)
    if NComponents == 0:
        lara_utils.print_and_flush(f'*** Error: unable to read {Params.corpus}')
        return False
    elif NComponents == 1:
        lara_utils.print_and_flush(f'*** Error: unable to find occurrences of "{_cut_tag}" in {Params.corpus}, nothing to do')
        return False
    SubConfigFiles = [ make_config_file_for_piece_of_corpus(ConfigFile, Params, TextComponents, Index)
                       for Index in range(0, NComponents) ]
    CrowdsourcingDir = lara_utils.get_tmp_directory(Params)
    for Index in range(0, len(SubConfigFiles)):
        SubConfigFile = SubConfigFiles[Index]
        SubZipfile = f'{CrowdsourcingDir}/{Id}_export_{str(Index).zfill(4)}.zip'
        Result = lara_import_export.make_export_zipfile(SubConfigFile, SubZipfile)
        if Result == False:
            lara_utils.print_and_flush(f'*** Error: something went wrong when making export file {Index}')
            return False
    lara_utils.make_zipfile(CrowdsourcingDir, MasterZipfile)
    return True

def make_config_file_for_piece_of_corpus(ConfigFile, Params, TextComponents, Index):
    SubConfigFile = sub_config_file_name(ConfigFile, Index)
    SubCorpusFile = make_sub_corpus_file(Params, TextComponents, Index)
    SubId = f'{Params.id}_{str(Index).zfill(4)}'
    SubParams = copy.copy(Params)
    SubParams.id = SubId
    SubParams.corpus = SubCorpusFile
    SubParamsDict = dict(SubParams)
    # Clean up the contents of the params by getting rid of everything that's set at its default value
    Keys = list(SubParamsDict.keys())
    for Key in Keys:
        if SubParamsDict[Key] == lara_config.default_value_for_param(Key) or lara_config.is_internal_param(Key):
            del SubParamsDict[Key]
    lara_utils.write_json_to_file(SubParamsDict, SubConfigFile)
    return SubConfigFile

def sub_config_file_name(ConfigFile, Index):    
    ( BaseFile, Extension ) = lara_utils.file_to_base_file_and_extension(ConfigFile)
    return f'{BaseFile}_{Index}.{Extension}'

def make_sub_corpus_file(Params, TextComponents, Index):
    Text = TextComponents[Index]
    CorpusFile = Params.corpus
    ( BaseFile, Extension ) = lara_utils.file_to_base_file_and_extension(CorpusFile)
    SubCorpusFile = f'{BaseFile}_{Index}.{Extension}'
    lara_utils.write_lara_text_file(Text, SubCorpusFile)
    return SubCorpusFile

# ------------------------------------------
    
def stick_together_projects(FileWithListOfConfigFiles, ConfigFile):
    ListOfConfigs = lara_utils.read_json_file(FileWithListOfConfigFiles)
    if not isinstance(ListOfConfigs, list) and len(ListOfConfigs) > 0:
        lara_utils.print_and_flush(f'*** Error: unable to read list of config files from {FileWithListOfConfigFiles}')
        return False
    elif incompatible_projects(ListOfConfigs):
        lara_utils.print_and_flush(f'*** Error: bad list of projects: {FileWithListOfConfigFiles}')
        return False
    else:
        lara_utils.print_and_flush(f'--- Sticking together {len(ListOfConfigs)} projects)')
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if Params == False:
        lara_utils.print_and_flush(f'*** Error: unable to read config files {ConfigFile}')
        return False
    UpdateDict = collect_update_dict_information(ListOfConfigs)
    return update_project_from_update_dict(UpdateDict, Params)

def incompatible_projects(ListOfConfigs):
    AllParams = []
    for ConfigFile in ListOfConfigs:
        Params = lara_config.read_lara_local_config_file(ConfigFile)
        if Params == False:
            lara_utils.print_and_flush(f'*** Error: unable to read config file: {ConfigFile}')
            return True
        else:
            AllParams += [ Params ]
    AllLangs = lara_utils.remove_duplicates( [ Params.language for Params in AllParams ] )
    if len(AllLangs) != 1:
        lara_utils.print_and_flush(f'*** Error: multiple languages in subprojects: {AllLangs}')
        return True
    else:
        return False

def collect_update_dict_information(ListOfConfigs):
    UpdateDict = {}
    for ConfigFile in ListOfConfigs:
        Params = lara_config.read_lara_local_config_file(ConfigFile)
        collect_update_dict_information_from_params(Params, UpdateDict)
    return UpdateDict

def collect_update_dict_information_from_params(Params, UpdateDict):
    collect_corpus_information_from_params(Params, UpdateDict)
    collect_audio_information_from_params(Params, UpdateDict)
    collect_segment_translation_information_from_params(Params, UpdateDict)
    collect_token_translation_information_from_params(Params, UpdateDict)
    collect_mwe_translation_information_from_params(Params, UpdateDict)

def collect_corpus_information_from_params(Params, UpdateDict):
    CorpusFile = Params.corpus
    if not lara_utils.file_exists(CorpusFile):
        return
    Text = lara_utils.read_lara_text_file(CorpusFile)
    if not Text:
        return
    else:
        UpdateDict['corpus'] = [ Text ] if not 'corpus' in UpdateDict else UpdateDict['corpus'] + [ Text ]

def collect_audio_information_from_params(Params, UpdateDict):
    SegmentAudioDir = Params.segment_audio_directory
    if SegmentAudioDir != '' and lara_utils.directory_exists(SegmentAudioDir):
        if not 'segment_audio_dirs' in UpdateDict:
            UpdateDict['segment_audio_dirs'] = [ SegmentAudioDir ]
        else:
            UpdateDict['segment_audio_dirs'] += [ SegmentAudioDir ]

def collect_segment_translation_information_from_params(Params, UpdateDict):
    SegmentTranslationFile = Params.segment_translation_spreadsheet
    if SegmentTranslationFile != '' and lara_utils.file_exists(SegmentTranslationFile):
        Lines = lara_utils.read_lara_csv(SegmentTranslationFile)
        if not 'segment_translation_lines' in UpdateDict:
            UpdateDict['segment_translation_lines'] = [ Lines ]
        else:
            UpdateDict['segment_translation_lines'] += [ Lines ]
 
def collect_token_translation_information_from_params(Params, UpdateDict):
    TokenTranslationFile = Params.translation_spreadsheet_tokens
    if TokenTranslationFile != '' and lara_utils.file_exists(TokenTranslationFile):
        Lines = lara_utils.read_lara_csv(TokenTranslationFile)
        if not 'token_translation_lines' in UpdateDict:
            UpdateDict['token_translation_lines'] = [ Lines ]
        else:
            UpdateDict['token_translation_lines'] += [ Lines ]
    
def collect_mwe_translation_information_from_params(Params, UpdateDict):
    MWEAnnotationsFile = Params.mwe_annotations_file
    if MWEAnnotationsFile != '' and lara_utils.file_exists(MWEAnnotationsFile):
        Records = lara_utils.read_json_file(MWEAnnotationsFile)
        if not 'mwe_annotation_records' in UpdateDict:
            UpdateDict['mwe_annotation_records'] = [ Records ]
        else:
            UpdateDict['mwe_annotation_records'] += [ Records ]

def update_project_from_update_dict(UpdateDict, Params):
    update_project_corpus_information_from_dict(UpdateDict, Params)
    update_project_audio_information_from_dict(UpdateDict, Params)
    update_project_segment_translation_information_from_dict(UpdateDict, Params)
    update_project_token_translation_information_from_dict(UpdateDict, Params)
    update_project_mwe_translation_information_from_dict(UpdateDict, Params)

def update_project_corpus_information_from_dict(UpdateDict, Params):
    if 'corpus' in UpdateDict and UpdateDict['corpus'] != '':
        PiecesOfText = UpdateDict['corpus']
        Text = '<cut>'.join(PiecesOfText)
        CorpusFile = Params.corpus
        lara_utils.write_lara_text_file(Text, CorpusFile)
        lara_utils.print_and_flush(f'--- Collected corpus file {CorpusFile} from {len(PiecesOfText)} pieces of text.')

def update_project_audio_information_from_dict(UpdateDict, Params):
    if 'segment_audio_dirs' in UpdateDict and UpdateDict['segment_audio_dirs'] != []:
        CombinedMetadata = []
        CombinedSegmentAudioDir = Params.segment_audio_directory
        lara_utils.create_directory_if_it_doesnt_exist(CombinedSegmentAudioDir)
        AudioDirs = UpdateDict['segment_audio_dirs']
        for SegmentAudioDir in AudioDirs:
            Metadata = update_project_audio_information_single(SegmentAudioDir, CombinedSegmentAudioDir)
            CombinedMetadata += Metadata
        lara_audio.write_ldt_metadata_file(CombinedMetadata, CombinedSegmentAudioDir)
        lara_utils.print_and_flush(f'--- Collected segment audio data directory {CombinedSegmentAudioDir} from {len(AudioDirs)} audio directories')

def update_project_audio_information_single(SegmentAudioDir, CombinedSegmentAudioDir):
    Metadata = lara_audio.read_ldt_metadata_file(SegmentAudioDir)
    for Record in Metadata:
        File = Record['file']
        lara_utils.copy_file(f'{SegmentAudioDir}/{File}', f'{CombinedSegmentAudioDir}/{File}')
    return Metadata

def update_project_segment_translation_information_from_dict(UpdateDict, Params):
    if 'segment_translation_lines' in UpdateDict:
        ListOfLines = UpdateDict['segment_translation_lines']
        Lines = lara_utils.concatenate_lists(ListOfLines)
        SegmentTranslationFile = Params.segment_translation_spreadsheet
        lara_utils.write_lara_csv(Lines, SegmentTranslationFile)
        lara_utils.print_and_flush(f'--- Collected segment translation file {SegmentTranslationFile} from {len(ListOfLines)} segment translation files')

def update_project_token_translation_information_from_dict(UpdateDict, Params):
    if 'token_translation_lines' in UpdateDict:
        ListOfLines = UpdateDict['token_translation_lines']
        Lines = lara_utils.concatenate_lists(ListOfLines)
        TokenTranslationFile = Params.translation_spreadsheet_tokens
        lara_utils.write_lara_csv(Lines, TokenTranslationFile)
        lara_utils.print_and_flush(f'--- Collected token translation file {TokenTranslationFile} from {len(ListOfLines)} token translation files')

def update_project_mwe_translation_information_from_dict(UpdateDict, Params):
    if 'mwe_annotation_records' in UpdateDict:
        ListOfListsOfRecords = UpdateDict['mwe_annotation_records']
        Records = lara_utils.concatenate_lists(ListOfListsOfRecords)
        MWEAnnotationsFile = Params.mwe_annotations_file
        lara_utils.write_json_to_file(Records, MWEAnnotationsFile)
        lara_utils.print_and_flush(f'--- Collected MWE annotations file {MWEAnnotationsFile} from {len(ListOfListsOfRecords)} MWE annotations files')

                                 
    
