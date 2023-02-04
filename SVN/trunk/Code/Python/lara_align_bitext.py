
import lara_config
import lara_split_and_clean
import lara_translations
import lara_parse_utils
import lara_utils

def create_translations_from_bitext(ConfigFile):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if Params == False:
        return
    if check_params_for_create_translations_from_bitext(Params) == False:
        return
    Text0 = read_bitext(Params)
    if Text0 == False:
        return
    Text = lara_parse_utils.remove_html_annotations_from_string(Text0)[0]
    Lines = [ Line for Line in Text.split('\n')
              if not Line == '' and not Line.isspace() ]
    if not len(Lines) % 2 == 0:
        lara_utils.print_and_flush(f'*** Error: not an even number of lines. Final lines are:')
        lara_utils.prettyprint(Lines[-5:])
        return
    LinePairs = [ ( Lines[2*I], Lines[2*I + 1] ) for I in range(0, ( int(len(Lines) / 2) ) - 1) ]
    SegmentPairs = []
    for ( Line1, Line2 ) in LinePairs:
        ( Segments1, Segments2 ) = ( nontrivial_translation_components(Line1), nontrivial_translation_components(Line2) )
        if len(Segments1) != len(Segments2):
            lara_utils.print_and_flush(f'*** Error: different number of segments in line pair:')
            lara_utils.prettyprint([Line1, Line2])
            return
        for I in range(0, len(Segments1)):
            SegmentPairs += [ [ Segments1[I], Segments2[I] ] ]
        for I in range(0, len(Segments1)):
            SegmentPairs += [ [ Segments2[I], Segments1[I] ] ]
    write_segment_translations_from_bitext(SegmentPairs, Params)

def nontrivial_translation_components(Str):
    return [ Segment for Segment in Str.split('//') if Segment != '' and not Segment.isspace() ]

def check_params_for_create_translations_from_bitext(Params):
    if Params.audio_alignment_corpus == '':
        lara_utils.print_and_flush(f'*** Error: audio_alignment_corpus not defined:')
        return False
    if Params.segment_translation_spreadsheet == '':
        lara_utils.print_and_flush(f'*** Error: segment_translation_spreadsheet not defined:')
        return False
    return True

def read_bitext(Params):
    File = Params.audio_alignment_corpus
    return lara_utils.read_lara_text_file(File)

def write_segment_translations_from_bitext(Tuples, Params):
    Spreadsheet = Params.segment_translation_spreadsheet
    Tuples1 = [ regularise_translation_pair(Tuple, Params) for Tuple in Tuples ]
    if False in Tuples1:
        return
    Header = [ 'Source', 'Target' ]
    lara_translations.write_translation_csv(Header, Tuples1, Spreadsheet)
    return

def regularise_translation_pair(Tuple, Params):
    if not isinstance(Tuple, ( list, tuple )) or not len(Tuple) == 2:
        lara_utils.print_and_flush(f'*** Error: bad translation tuple: {Tuple}')
        return False
    return [ lara_split_and_clean.minimal_clean_lara_string(Tuple[I], Params)[0] for I in [ 0, 1 ] ]
