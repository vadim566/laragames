import lara
import lara_utils
import lara_config
import lara_top
import webbrowser

def main( Args ):
    # get config file to use
    ConfigFile = lara_top.find_config_file( False if len(Args) < 1 else Args[0] )
    if not ConfigFile:
        return False
    # Load config file
    ConfigData = lara_config.read_lara_local_config_file(ConfigFile)
    if not ConfigData:
        lara_utils.print_and_flush(f'*** Error: cannot read configuration file {ConfigFile}')
        return False
    # get name of hyperlinked text file
    hyperlinkedTextFile = f'{ConfigData.compiled_directory}/{ConfigData.id}{lara_top.base_name_for_lara_compiled_dir("word_pages_directory")}/{lara.formatted_hyperlinked_text_file_for_word_pages_short()}'
    hyperlinkedTextFile = lara_utils.absolute_file_name( hyperlinkedTextFile )
    if not lara_utils.file_exists( hyperlinkedTextFile ):
        lara_utils.print_and_flush( f'*** Error: the file does not exist: {hyperlinkedTextFile}')
        return False
    # open in browser        
    lara_utils.print_and_flush( f'--- open in browser: {hyperlinkedTextFile}')
    webbrowser.open( hyperlinkedTextFile )
    return

if __name__=="__main__":
    from sys import argv
    if len(argv) > 2:
        lara_utils.print_and_flush(f'*** Usage: {lara_utils.python_executable()} $LARA/Code/Python/lara_open_in_browser.py [ <ConfigFile> ]')
    else:
        main( argv[1:] )
