import lara_utils
import os
import lara_config
import lara_top

EditFileIds = {
    "config_file" : {
        "config_setting": None, # <=> use the config file!
        "editor_variable": "LARA_TEXTEDITOR"
    },
    "corpus" : {
        "config_setting": "corpus",
        "editor_variable": "LARA_TEXTEDITOR"
    },
    "untagged_corpus" : {
        "config_setting": "untagged_corpus",
        "editor_variable": "LARA_TEXTEDITOR"
    },
    "translation_spreadsheet" : {
        "config_setting": "translation_spreadsheet",
        "editor_variable": "LARA_CSVEDITOR"
    },
    "segment_translation_spreadsheet" : {
        "config_setting": "segment_translation_spreadsheet",
        "editor_variable": "LARA_CSVEDITOR"
    },
    "custom_css_file" : {
        "config_setting": "css_file",
        "editor_variable": "LARA_TEXTEDITOR",
        "prepend_corpus_directory": True
    },
    "custom_script_file" : {
        "config_setting": "script_file",
        "editor_variable": "LARA_TEXTEDITOR",
        "prepend_corpus_directory": True
    },
}

def valid_fileids():
    for key in EditFileIds.keys():
        yield key
        yield _shortkey(key)

def _shortkey(key):
    import re
    return re.sub("(^(.)[^_]*)|(_(.)[^_]*)", r'\g<2>\g<4>', key )

def main( Args ):
    # get config file to use
    ConfigFile = lara_top.find_config_file( False if len(Args) < 2 else Args[1] )
    if not ConfigFile:
        return False
    # check fileid to use
    fileId = Args[0]
    # find the file entry
    entry = None
    for key in EditFileIds.keys():
        if key.lower() == fileId.lower() or _shortkey(key.lower()) == fileId.lower():
            entry = EditFileIds[key]
            break
    if not entry:
        lara_utils.print_and_flush( f'*** Error: invalid <FileID> "{fileId}". Valid <FileID>\'s include:')
        lara_utils.print_and_flush( "\n".join(valid_fileids()))
        return False
    # Check environment variable
    editorVar = entry['editor_variable']
    if not editorVar in os.environ:
        lara_utils.print_and_flush(f'*** Error: environment variable {editorVar} not found')
        return False
    editorToRun = os.environ[editorVar]
    # Load config file
    ConfigData = lara_config.read_lara_local_config_file(ConfigFile)
    if not ConfigData:
        lara_utils.print_and_flush(f'*** Error: cannot read configuration file {ConfigFile}')
        return False
    # determine file to edit
    fileToEdit = ConfigFile        
    if entry['config_setting'] != None:
        if not entry['config_setting'] in ConfigData:
            lara_utils.print_and_flush(f'*** Error: setting "{entry["config_setting"]}" not specified configuration file {ConfigFile}')
            return False
        fileToEdit = ConfigData[entry['config_setting']]
        if 'prepend_corpus_directory' in entry and entry['prepend_corpus_directory']:
            if ConfigData.corpus and ConfigData.corpus != '':
                fileToEdit = f'{lara_utils.directory_for_pathname(ConfigData.corpus)}/{fileToEdit}'
    fileToEdit = lara_utils.absolute_file_name( fileToEdit )
    if not lara_utils.file_exists(fileToEdit):
        lara_utils.print_and_flush(f'*** Error: file "{fileToEdit} does not exist')
        return False
    import subprocess
    lara_utils.print_and_flush(f'--- starting editor "{editorToRun}" with file "{fileToEdit}""')
    subprocess.Popen([editorToRun, fileToEdit])
    return

if __name__=="__main__":
    from sys import argv
    if len(argv) < 2 or len(argv) > 3:
        lara_utils.print_and_flush(f'*** Usage: {lara_utils.python_executable()} $LARA/Code/Python/lara_edit.py <FileID> [ <ConfigFile> ]')
    else:
        main( argv[1:] )
