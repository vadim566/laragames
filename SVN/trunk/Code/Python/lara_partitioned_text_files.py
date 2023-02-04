
# Utilities for manipulating text files divided using tags of the form
# <file id="...ID...">

import lara_config
import lara_utils
import re

def expand_source_and_target_files(ConfigFile):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if Params == False:
        return
    ( SourceFile, TargetFile ) = ( Params.source_file, Params.target_file )
    if SourceFile == '':
        lara_utils.print_and_flush(f'*** Error: source_file not defined')
        return
    if not lara_utils.file_exists(SourceFile):
        lara_utils.print_and_flush(f'*** Error: unable to find {SourceFile}')
        return
    if TargetFile == '':
        lara_utils.print_and_flush(f'*** Error: source_file not defined')
        return
    if not lara_utils.file_exists(TargetFile):
        lara_utils.print_and_flush(f'*** Error: unable to find {TargetFile}')
        return
    SourceTags = labels_in_partitioned_file(SourceFile)
    TargetTags = labels_in_partitioned_file(TargetFile)
    if SourceTags != TargetTags:
        lara_utils.print_and_flush(f'*** Error: source tags {SourceTags} different from target tags {TargetTags}')
        return
    expand_partitioned_text_file(SourceFile)
    expand_partitioned_text_file(TargetFile)

def expand_partitioned_text_file(File):
    ( Base, Ext ) = lara_utils.file_to_base_file_and_extension(File)
    ParsedFile = parse_partitioned_text_file(File)
    AllTags = [ Component[0] for Component in ParsedFile ]
    for ( Tag, Text) in ParsedFile:
        lara_utils.write_lara_text_file(Text, f'{Base}_{Tag}.{Ext}')
    lara_utils.print_and_flush(f'--- Expanded {File} to {len(AllTags)} files. Tags = {AllTags}')

def extract_from_partitioned_file(File, ThisLabel):
    ParsedText = parse_partitioned_text_file(File)
    for ( Label, Text ) in ParsedText:
        if Label == ThisLabel:
            return Text
    lara_utils.print_and_flush(f'*** Error: {Label} not defined in partitioned file {File}')
    return False

def update_partitioned_text_file(File, NewLabel, NewText, Params):
    make_blank_partitioned_text_file_if_necessary(Params, File)
    CurrentContent = parse_partitioned_text_file(File)
    Tags = [ Component[0] for Component in CurrentContent ]
    if not NewLabel in Tags:
        lara_utils.print_and_flush(f'*** Error: {NewLabel} not defined in partitioned file {File}')
        return False
    NewContent = []
    for ( Label, Text ) in CurrentContent:
        NewContent += [ ( Label, NewText if Label == NewLabel else Text ) ]
    write_partitioned_text_file(NewContent, File)
    return True

def make_blank_partitioned_text_file_if_necessary(Params, File):
    if lara_utils.file_exists(File):
        return
    SourceFile = Params.source_file
    if SourceFile == '':
        lara_utils.print_and_flush(f'*** Error: source_file not defined')
        return
    if not lara_utils.file_exists(SourceFile):
        lara_utils.print_and_flush(f'*** Error: unable to find {SourceFile}')
        return
    SourceTags = labels_in_partitioned_file(SourceFile)
    Content = [ ( Tag, '' ) for Tag in SourceTags ]
    write_partitioned_text_file(Content, File)    

def labels_in_partitioned_file(File):
    ParsedFile = parse_partitioned_text_file(File)
    return False if ParsedFile == False else [ Component[0] for Component in ParsedFile ]

def parse_partitioned_text_file(File):
    Text = lara_utils.read_lara_text_file(File)
    if Text == False:
        lara_utils.print_and_flush(f'*** Error: unable to read {File}')
        return False
    return parse_partitioned_text(Text)

# Search for tags of form <file id="(Id)">

def parse_partitioned_text(Text):
    ( CurrentFileId, OutList ) = ( '*init*', [] )
    while True:
        Match = re.search('<file[\s]+id="([^"]*)"\s*>', Text, flags=re.DOTALL)
        if Match == None:
            OutList += [ [ CurrentFileId, Text ] ]
            return OutList
        else:
            ( TagStartIndex, TagEndIndex ) = Match.span()
            TagFile = Match.group(1)
            if CurrentFileId != '*init*':
                OutList += [ [ CurrentFileId, Text[:TagStartIndex] ] ]
            CurrentFileId = TagFile
            Text = Text[TagEndIndex:]
    # Shouldn't get here...
    return OutList    

def write_partitioned_text_file(Content, File):
    NewContent = ''.join([ f'<file id="{Label}">{Text}' for ( Label, Text ) in Content ])
    lara_utils.write_lara_text_file(NewContent, File)
