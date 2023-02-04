
import lara_top
import lara_crowdsource
import lara_import_export
import lara_generic_tts
import lara_install_audio_zipfile
import lara_abstract_html
import lara_config
import lara_utils

# - Cut up project to create crowdsourcing zipfile
# - Create subprojects for zipfile
# - Download audio for LDT (manual)
# - For each subjproject, do install audio, make resources, make word pages
# - Stick together subprojects into single HTML

_original_master_config = '$LARA/Content/lpp_farsi_full2/corpus/local_config.json'

_subprojects_zipfile = '$LARA/Content/lpp_farsi_full2/tmp/all_subprojects.zip'

_subprojects_zipfile_dir = '$LARA/Content/lpp_farsi_full2/tmp/all_subprojects'

_master_config_for_sticking_together = '$LARA/Content/lpp_farsi_full2/corpus/local_config_combined.json'

_list_of_subprojects_dirs_file = '$LARA/Content/lpp_farsi_full2/tmp/list_of_subprojects_dirs.json'

def store_subproject_dirs(CorpusDirs):
    lara_utils.write_json_to_file(CorpusDirs, _list_of_subprojects_dirs_file)
    lara_utils.print_and_flush(f'--- Written names of {len(_list_of_subprojects_dirs_file)} subproject directories to {_list_of_subprojects_dirs_file}')

def get_subproject_dirs():
    return lara_utils.read_json_file(_list_of_subprojects_dirs_file)

# - Cut up project to create crowdsourcing zipfile
def cut_up_project():
    ConfigFile = _original_master_config
    MasterZipfile = _subprojects_zipfile
    lara_crowdsource.cut_up_project(ConfigFile, MasterZipfile)

# - Create subprojects for zipfile
def import_subprojects():
    lara_utils.unzip_file(_subprojects_zipfile, _subprojects_zipfile_dir)
    ComponentZipfiles = lara_utils.file_members_of_directory(_subprojects_zipfile_dir)
    CorpusDirs = []
    for ComponentZipfile in ComponentZipfiles:
        CorpusDir = import_subproject(ComponentZipfile)
        CorpusDirs += [ CorpusDir ]
    store_subproject_dirs(CorpusDirs)

# Import each subproject
# Correct names of audio directories so that we have unique ones for each subproject.
# If we don't do this, the word audio will collide
# Typical name: lpp_farsi_full2_export_0003.zip
def import_subproject(ComponentZipfile):
    FullComponentZipfile = f'{_subprojects_zipfile_dir}/{ComponentZipfile}'
    ComponentCorpusDir = ComponentZipfile.replace('.zip', '').replace('_export', '')
    AudioDirName = ComponentCorpusDir
    FullCorpusDir = f'$LARA/Content/{ComponentCorpusDir}'
    LanguageRootDir = '$LARA/Content'
    ConfigFileForImport = _original_master_config
    Result = lara_import_export.import_zipfile(FullComponentZipfile, FullCorpusDir, LanguageRootDir, ConfigFileForImport)
    if not Result:
        return False
    change_audio_dirs_in_config_file(FullCorpusDir, AudioDirName)
    return FullCorpusDir

##{
##    "allow_table_of_contents": "yes",
##    ...
##    "segment_audio_directory": "C:/cygwin64/home/sf2/callector-lara-svn/trunk/Content/lpp_farsi_full2_0000/audio/larafarsi",
##    ...
##    "word_audio_directory": "C:/cygwin64/home/sf2/callector-lara-svn/trunk/Content/farsi/audio/farsi_readspeaker_Female01",
##    ...
##}

def change_audio_dirs_in_config_file(CorpusDir, AudioDirName):
    ConfigFile = config_file_for_dir(CorpusDir)
    Content = lara_utils.read_json_file(ConfigFile)
    Content1 = change_audio_dirs_in_config_file_content(['segment_audio_directory', 'word_audio_directory'], Content, AudioDirName)
    lara_utils.write_json_to_file(Content1, ConfigFile)
    lara_utils.print_and_flush(f'--- Adjusted audio dirs in {ConfigFile}')

def config_file_for_dir(SubprojectDir):
    return f'{SubprojectDir}/corpus/local_config.json'

def change_audio_dirs_in_config_file_content(Keys, Content, AudioDirName):
    for Key in Keys:
        CurrentDir = Content[Key]
        Components = CurrentDir.split('/')
        Components1 = Components[:-1] + [ AudioDirName ]
        NewDir = '/'.join(Components1)
        Content[Key] = NewDir
    return Content

# - Download audio for LDT (manual)

_edit_ids = [ 'titles', 'titles2', 'remove_page_tags' ]

def edit_text_in_subprojects(Id):
    if not Id in _edit_ids:
        lara_utils.print_and_flush(f'*** Error: unknown Id {Id} in edit_text_in_subprojects. Needs to be in {_edit_ids}')
        return 
    SubprojectDirs = get_subproject_dirs()
    for SubprojectDir in SubprojectDirs:
        edit_text_in_subproject(SubprojectDir, Id)

def edit_text_in_subproject(SubprojectDir, Id):
    ConfigFile = config_file_for_dir(SubprojectDir)
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    CorpusFile = Params.corpus
    Text = lara_utils.read_lara_text_file(CorpusFile)
    Text1 = edit_text(Text, Id)
    lara_utils.write_lara_text_file(Text1, CorpusFile)
    lara_utils.print_and_flush(f'--- Edited text in {SubprojectDir}')

def edit_text(Text, Id):
    if Id == 'titles':
        return Text.replace('||<h', '<h').replace('</h', '||</h')
    if Id == 'titles2':
        return Text.replace('||<h', '<h')
    if Id == 'remove_page_tags':
        return Text.replace('<page>', '')
    else:
        return Text

# - For each subjproject, make resources, optionally do install audio, make word pages
def compile_subprojects(InstallAudio):
    SubprojectDirs = get_subproject_dirs()
    for SubprojectDir in SubprojectDirs:
        compile_subproject(SubprojectDir, InstallAudio)

def make_and_install_tts_word_audio_for_subprojects():
    SubprojectDirs = get_subproject_dirs()
    for SubprojectDir in SubprojectDirs:
        make_and_install_tts_word_audio_for_subproject(SubprojectDir)

def compile_subproject(SubprojectDir, InstallAudio):
    make_resources(SubprojectDir)
    if InstallAudio == 'install_audio':
        install_segment_or_word_audio(SubprojectDir, 'segments')
        install_segment_or_word_audio(SubprojectDir, 'words')
    make_word_pages(SubprojectDir)

def make_and_install_tts_word_audio_for_subproject(SubprojectDir):
    if find_downloaded_zipfile(SubprojectDir, 'words') != False:
        return
    lara_utils.print_and_flush(f'--------------------')
    lara_utils.print_and_flush(f'--- Creating TTS word audio for {SubprojectDir}')
    make_config_file_use_tts_for_word_audio(SubprojectDir)
    make_resources(SubprojectDir)
    RecordingScriptFile = find_recording_script(SubprojectDir, 'words', 'partial')
    if len(lara_utils.read_json_file(RecordingScriptFile)) == 0:
        lara_utils.print_and_flush(f'--- All TTS audio already exists for {SubprojectDir}')
        return
    create_tts_word_audio_for_subproject(SubprojectDir)
    install_tts_word_audio(SubprojectDir)

def make_config_file_use_tts_for_word_audio(SubprojectDir):
    ConfigFile = config_file_for_dir(SubprojectDir)
    ConfigFileDict = lara_utils.read_json_file(ConfigFile)
    if ConfigFileDict['word_audio_directory'] == '$LARA/Content/farsi/audio/farsi_readspeaker_Female01':
        return
    ConfigFileDict['word_audio_directory'] = '$LARA/Content/farsi/audio/farsi_readspeaker_Female01'
    lara_utils.write_json_to_file(ConfigFileDict, ConfigFile)
    lara_utils.print_and_flush(f'--- Set word_audio_directory = $LARA/Content/farsi/audio/farsi_readspeaker_Female01 in {SubprojectDir}')
    
def make_resources(SubprojectDir):
    ConfigFile = config_file_for_dir(SubprojectDir)
    lara_top.compile_lara_local_resources(ConfigFile)

def create_tts_word_audio_for_subproject(SubprojectDir):
    ConfigFile = config_file_for_dir(SubprojectDir)
    RecordingScriptFile = find_recording_script(SubprojectDir, 'words', 'partial')
    AudioZipfile = find_tts_words_zipfile(SubprojectDir)
    lara_generic_tts.create_tts_audio(RecordingScriptFile, ConfigFile, AudioZipfile)

def install_segment_or_word_audio(SubprojectDir, SegmentsOrWords):
    ConfigFile = config_file_for_dir(SubprojectDir)
    Zipfile = find_downloaded_zipfile(SubprojectDir, SegmentsOrWords)
    if Zipfile == False:
        return
    RecordingScriptFile = find_recording_script(SubprojectDir, SegmentsOrWords, 'full')
    lara_install_audio_zipfile.install_audio_zipfile(Zipfile, RecordingScriptFile, SegmentsOrWords, ConfigFile, 'default')

def install_tts_word_audio(SubprojectDir):
    ConfigFile = config_file_for_dir(SubprojectDir)
    Zipfile = find_tts_words_zipfile(SubprojectDir)
    if Zipfile == False:
        lara_utils.print_and_flush(f'*** Error: TTS zipfile {Zipfile} not found')
        return
    RecordingScriptFile = find_recording_script(SubprojectDir, 'words', 'partial')
    lara_install_audio_zipfile.install_audio_zipfile(Zipfile, RecordingScriptFile, 'words', ConfigFile, 'default')

def find_downloaded_zipfile(SubprojectDir, SegmentsOrWords):
    CorpusDir = f'{SubprojectDir}/corpus'
    Files = lara_utils.file_members_of_directory(CorpusDir)
    PossibleFiles = [File for File in Files
                     if SegmentsOrWords in File and '.zip' in File ]
    if len(PossibleFiles) == 0:
        lara_utils.print_and_flush(f'*** Error: unable to find {SegmentsOrWords} zipfile in {CorpusDir}')
        return False
    if len(PossibleFiles) > 1:
        lara_utils.print_and_flush(f'*** Error: found more than one {SegmentsOrWords} zipfile in {CorpusDir}')
        return False
    return f'{CorpusDir}/{PossibleFiles[0]}'

def find_tts_words_zipfile(SubprojectDir):
    CorpusDir = f'{SubprojectDir}/corpus'
    return f'{CorpusDir}/TTSWords.zip'

def find_recording_script(SubprojectDir, SegmentsOrWords, FullOrPartial):
    if not FullOrPartial in ( 'full', 'partial' ):
        lara_utils.print_and_flush(f'*** Error: bad value for FullOrPartial "{FullOrPartial}" in find_recording_script')
        return False
    ConfigFile = config_file_for_dir(SubprojectDir)
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if FullOrPartial == 'full':
        Key = 'ldt_segment_recording_file_full_json' if SegmentsOrWords == 'segments' else 'ldt_word_recording_file_full_json'
    if FullOrPartial == 'partial':
        Key = 'ldt_segment_recording_file_json' if SegmentsOrWords == 'segments' else 'ldt_word_recording_file_json'
    return lara_top.lara_tmp_file(Key, Params)

def make_word_pages(SubprojectDir):
    ConfigFile = config_file_for_dir(SubprojectDir)
    lara_top.compile_lara_local_word_pages(ConfigFile)

# - Stick together subprojects into single HTML
def stick_together_subprojects():
    MasterConfigFile = _master_config_for_sticking_together
    ComponentDirs = lara_utils.read_json_file(_list_of_subprojects_dirs_file)
    ComponentConfigFiles = [ config_file_for_dir(Dir) for Dir in ComponentDirs ]
    lara_abstract_html.abstract_html_to_html_multiple(MasterConfigFile, ComponentConfigFiles)

