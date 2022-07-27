
import lara_utils
import re

_placeHolders = {}

def main( contentid ):
    if not lara_utils.check_environment_variable_directory('LARA'):
        return False
    contentDirectory = f'$LARA/Content/{contentid}'
    if not _check_contentid( contentid, contentDirectory ):
        return False
    absoluteContentDirectory = lara_utils.absolute_file_name( contentDirectory )
    
    global _placeHolders
    _placeHolders = { "CONTENTID" : contentid }

    success = True
    try:
    
        # Unzip content template to content directory
        zipfile = lara_utils.absolute_filename_in_python_directory('lara_newcontent_template.zip')
        lara_utils.unzip_file(zipfile, absoluteContentDirectory)

        # replace placeholders in all filenames (recusively) and file contents
        import pathlib
        allFiles = [ str(path) for path in pathlib.Path(absoluteContentDirectory).glob('**/*.*') ]
        for file in allFiles:
            success = _handle_file( file )
            if not success:
                break
    except:
        success = False
    
    if success:
        lara_utils.print_and_flush(f'\n\nContent "{contentid}" created.\nHappy LARA-ation!\n')

def _check_contentid( contentid, contentDirectory ):
    if not lara_utils.is_valid_contentid( contentid ):
        lara_utils.print_and_flush(f'*** Error: invalid content-ID "{contentid}". The content-ID must start with a letter (a-z) followed by a sequence of letters, digits or the underscore.')
        return False
    if lara_utils.directory_exists( contentDirectory ):
        lara_utils.print_and_flush(f'*** Error: the content directory "{contentDirectory}" already exists.')
        return False
    if not lara_utils.create_directory( contentDirectory ):
        lara_utils.print_and_flush(f'*** Error: could not create the content directory "{contentDirectory}".')
        return False
    return True

def _handle_file( file ):
    # Handle file's name
    newfile = apply_placeholders( file )
    if file != newfile:
        if not lara_utils.rename_file( file, newfile ):
            return False
        file = newfile

    # Handle file's content
    oldContent = lara_utils.read_lara_text_file( newfile )
    if not oldContent:
        return False
    newContent = apply_placeholders( oldContent )
    if oldContent != newContent:
        lara_utils.write_lara_text_file( newContent, file )
    return True        

def apply_placeholders( text ):
   return re.sub('\$([^$]*)\$', apply_placeholder, text)

def apply_placeholder(m):
    placeholder = m.group(1)
    if placeholder == "":
        return "$"
    if not placeholder in _placeHolders:
        errorMessage = f'invalid placeholder "{placeholder}" encountered.'
        lara_utils.print_and_flush(f'*** Error: {errorMessage}')
        raise ValueError(errorMessage)
    return _placeHolders[placeholder]

if __name__=="__main__":
    from sys import argv
    if len(argv) < 2:
        lara_utils.print_and_flush(f'*** Usage: {lara_utils.python_executable()} $LARA/Code/Python/lara_new_content.py <ContentID>.')
    else:
        main( argv[1] )
