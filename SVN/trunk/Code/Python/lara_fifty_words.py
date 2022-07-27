# Process '50 words' data for Barngarla

import lara_audio
import lara_parse_utils
import lara_utils

def make_50words_files():
    Dir = '$LARA/Content/barngarla_fifty_words/tmp/50words_audio'
    Dir1 = '$LARA/Content/barngarla_fifty_words/tmp/50words_audio_cleaned_wav'
    lara_utils.create_directory_deleting_old_if_necessary(Dir1)
    Metadata = read_metadata(Dir)
    ( NProcessed, NProduced) = ( 0, 0 )
    for Item in Metadata:
        if Item and len(Item) == 2:
            NProcessed += 1
            ( File, Words ) = Item
            Result = make_clean_file(File, Words, Dir, Dir1)
            if Result:
               NProduced += 1 
    lara_utils.print_and_flush(f'--- Successfully processed {NProduced}/{NProcessed} files')

def read_metadata(Dir):
    Lines = lara_audio.read_ldt_metadata_file(Dir)
    return [ lara_parse_utils.parse_ldt_metadata_file_line(Line) for Line in Lines ]

def make_clean_file(File, Words, Dir, Dir1):
    CleanWords = clean_words(Words)
    FromFile = f'{Dir}/{File}'
    ToFile = f'{Dir1}/{CleanWords}.wav'
    Result = lara_utils.copy_file(FromFile, ToFile)
    if not Result:
        lara_utils.print_and_flush('*** Error: unable to copy {FromFile} to {ToFile}')
        return False
    else:
        return True

def clean_words(Words):
    return Words.replace('/', ' or ').replace('?', '')

