
import lara_top
import lara_picturebook
import lara_transform_tagged_file
import lara_config
import lara_split_and_clean
import lara_parse_utils
import lara_utils
import copy
import re

# TODO:
# (interesting part) develop methods for filtering false positives - ML?

def test_mwe(Id):
    if Id == 'load_english':
        load_mwe_file('$LARA/Content/english/corpus/mwe_defs.txt')
    elif Id == 'test_segment1':
        load_mwe_file('$LARA/Content/english/corpus/mwe_defs.txt')
        Segment = [ 'He arrived, at last',
                    'He arrived at last',
                    [ ['He', 'he'], ['arrived', 'arrive'], ['at', 'at'], ['last', 'last'] ],
                    'null_tag'
                    ]
        lara_utils.prettyprint(mark_mwes_in_segment(Segment, {}))
    elif Id == 'test_segment1a':
        load_mwe_file('$LARA/Content/english/corpus/mwe_defs.txt')
        Segment = [ 'He arrived, at last',
                    'He arrived at last',
                    [ ['He', 'he/PRO'], ['arrived', 'arrive/V'], ['at', 'at/P'], ['last', 'last/ADJ'] ],
                    'null_tag'
                    ]
        lara_utils.prettyprint(mark_mwes_in_segment(Segment, {}))
    elif Id == 'test_segment2':
        load_mwe_file('$LARA/Content/english/corpus/mwe_defs.txt')
        Segment = [ 'He gave up trying at last',
                    'He gave up trying at last',
                    [ ['He', 'he'], ['gave', 'give'], ['up', 'up'], ['trying', 'try'],
                      ['at', 'at'], ['last', 'last'] ],
                    'null_tag'
                    ]
        lara_utils.prettyprint(mark_mwes_in_segment(Segment, {})) 
    elif Id == 'test_segment3':
        load_mwe_file('$LARA/Content/english/corpus/mwe_defs.txt')
        Segment = [ 'He gave them up at last',
                    'He gave them up  at last',
                    [ ['He', 'he'], ['gave', 'give'], ['them', 'they'], ['up', 'up'],
                      ['at', 'at'], ['last', 'last'] ],
                    'null_tag'
                    ]
        lara_utils.prettyprint(mark_mwes_in_segment(Segment, {})) 
    elif Id == 'test_segment4':
        load_mwe_file('$LARA/Content/english/corpus/mwe_defs.txt')
        Segment = [ 'He gave them up',
                    'He gave them up',
                    [ ['He', 'he'], ['gave', 'give'], ['them', 'they'], ['up', 'up']],
                    'null_tag'
                    ]
        lara_utils.prettyprint(mark_mwes_in_segment(Segment, {}))
    elif Id == 'test_segment5':
        load_mwe_file('$LARA/Content/french/corpus/mwe_defs.txt')
        Segment = [ 'S’#se#|il vous plaît#plaire#',
                    'S’il vous plaît',
                    [ [ "S", "se" ], [ "il", "il" ], [ "vous", "vous" ], [ "pla\u00eet", "plaire" ] ],
                    'null_tag'
                    ]
        lara_utils.prettyprint(mark_mwes_in_segment(Segment, {}))
    elif Id == 'test_segment6':
        load_mwe_file('$LARA/Content/english/corpus/mwe_defs.txt')
        Segment = [ 'getting#mwe_part_2_get up/V# up#mwe_part_2_get up/ADV#',
                    'getting up',
                    [ ['getting', 'V'], ['up', 'P'] ],
                    'null_tag'
                    ]
        lara_utils.prettyprint(mark_mwes_in_segment(Segment, {}))
    elif Id == 'test_völuspá1':
        Params = lara_config.read_lara_local_config_file('$LARA/Content/völuspá/corpus/local_config_kenningar.json')
        load_mwe_file('$LARA/Content/oldnorse/corpus/mwe_defs.txt')
        Segment = [ '\u00f3r Brimis bl\u00f3\u00f0i',
                    '\u00f3r Brimis bl\u00f3\u00f0i',
                    [[ "\u00f3r", "\u00f3r" ],
                     [ " ", "" ],
                     [ "Brimis", "Brimir" ],
                     [ " ", "" ],
                     [ "bl\u00f3\u00f0i", "bl\u00f3\u00f0" ]
                     ],
                    'null_tag'
                    ]
        lara_utils.prettyprint(mark_mwes_in_segment(Segment, {}, Params))
    elif Id == 'test_völuspá2':
        Params = lara_config.read_lara_local_config_file('$LARA/Content/völuspá/corpus/local_config_kenningar.json')
        load_mwe_file('$LARA/Content/oldnorse/corpus/mwe_defs.txt')
        Segment = [ 'tungls#tungl# tj\u00fagari</td><td>',
                    'tungls tj\u00fagari',
                    [[ "tungls", "tungl" ],
                     [ " ", "" ],
                     [ "tj\u00fagari</td><td>", "tj\u00fagari" ]
                     #[ "tj\u00fagari", "tj\u00fagari" ]
                     ],
                    'null_tag'
                    ]
        lara_utils.prettyprint(mark_mwes_in_segment(Segment, {}, Params))
    elif Id == 'test_völuspá3':
        Params = lara_config.read_lara_local_config_file('$LARA/Content/völuspá/corpus/local_config_kenningar.json')
        load_mwe_file('$LARA/Content/oldnorse/corpus/mwe_defs.txt')
        Segment = [ 'Baldrs#Baldr# br\u00f3\u00f0ir',
                    'Baldrs br\u00f3\u00f0ir',
                    [[ "Baldrs", "Baldr" ],
                     [ " ", "" ],
                     [ "br\u00f3\u00f0ir", "br\u00f3\u00f0ir" ],
                     ],
                    'null_tag'
                    ]
        lara_utils.prettyprint(mark_mwes_in_segment(Segment, {}, Params))
    elif Id == 'test_völuspá4':
        Params = lara_config.read_lara_local_config_file('$LARA/Content/völuspá/corpus/local_config_kenningar.json')
        load_mwe_file('$LARA/Content/oldnorse/corpus/mwe_defs.txt')
        Segment = [ 'yggjungr#Yggjungr# \u00e1sa#\u00e1ss#',
                    'yggjungr \u00e1sa',
                    [[ "yggjungr", "Yggjungr" ],
                     [ " ", "" ],
                     [ "\u00e1sa", "\u00e1ss" ]
                     ],
                    'null_tag'
                    ]
        lara_utils.prettyprint(mark_mwes_in_segment(Segment, {}, Params))
    elif Id == 'animal_farm_small1':
        load_mwe_file('$LARA/Content/english/corpus/mwe_defs.txt')
        InFile = '$LARA/tmp_resources/animal_farm_small_split.json'
        JSONTraceFile = '$LARA/tmp_resources/animal_farm_small_mwe_trace.html'
        mark_mwes_in_split_file(InFile, JSONTraceFile)
    elif Id == 'animal_farm_full1':
        load_mwe_file('$LARA/Content/english/corpus/mwe_defs.txt')
        InFile = '$LARA/tmp_resources/animal_farm_mwe_split.json'
        AnnotatedJSONTraceFile = '$LARA/Content/animal_farm/corpus/animal_farm_mwe_annotations.json'
        JSONTraceFile = '$LARA/tmp_resources/animal_farm_mwe_tmp_mwe_annotations.json'
        mark_mwes_in_split_file(InFile, AnnotatedJSONTraceFile, JSONTraceFile)
    elif Id == 'animal_farm_full2':
        InFile = '$LARA/tmp_resources/animal_farm_split.json'
        JSONTraceFile = '$LARA/tmp_resources/animal_farm_tmp_mwe_annotations.json'
        OutFile = '$LARA/tmp_resources/animal_farm_mwe_annotated.docx'
        HTMLTraceFile = '$LARA/tmp_resources/animal_farm_mwe_trace.html'
        apply_marked_mwes_in_split_file(InFile, JSONTraceFile, OutFile, HTMLTraceFile)
    elif Id == 'animal_farm_canonical':
        InFile = '$LARA/Content/animal_farm/corpus/TaggedAndCleaned_AnimalFarmMWE.docx'
        OutFile = '$LARA/Content/animal_farm/corpus/TaggedAndCleaned_AnimalFarmMWECanonical.docx'
        make_mwes_canonical(InFile, OutFile)
    elif Id == 'le_petit_prince1':
        load_mwe_file('$LARA/Content/french/corpus/mwe_defs.txt')
        InFile = '$LARA/tmp_resources/le_petit_prince_mwe_split.json'
        AnnotatedJSONTraceFile = '$LARA/Content/le_petit_prince_small/corpus/le_petit_prince_mwe_annotations.json'
        JSONTraceFile = '$LARA/tmp_resources/le_petit_prince_small_tmp_mwe_annotations.json'
        mark_mwes_in_split_file(InFile, AnnotatedJSONTraceFile, JSONTraceFile)
    elif Id == 'le_petit_prince2':
        InFile = '$LARA/tmp_resources/le_petit_prince_mwe_split.json'
        JSONTraceFile = '$LARA/Content/le_petit_prince_small/corpus/le_petit_prince_mwe_annotations.json'
        OutFile = '$LARA/tmp_resources/le_petit_prince_small_mwe_annotated.txt'
        HTMLTraceFile = '$LARA/tmp_resources/le_petit_prince_small_mwe_trace.html'
        apply_marked_mwes_in_split_file(InFile, JSONTraceFile, OutFile, HTMLTraceFile)
    elif Id == 'alice2':
        InFile = '$LARA/tmp_resources/alice_in_wonderland_split.json'
        JSONTraceFile = '$LARA/Content/alice_in_wonderland/corpus/alice_in_wonderland_mwe_annotations.json'
        OutFile = '$LARA/tmp_resources/alice_in_wonderland_mwe_annotated.txt'
        HTMLTraceFile = '$LARA/tmp_resources/alice_in_wonderland_mwe_trace.html'
        apply_marked_mwes_in_split_file(InFile, JSONTraceFile, OutFile, HTMLTraceFile)
    elif Id == 'alice_canonical':
        InFile = '$LARA/Content/alice_in_wonderland/corpus/alice_in_wonderland.txt'
        OutFile = '$LARA/Content/alice_in_wonderland/corpus/alice_in_wonderland_canonical.txt'
        make_mwes_canonical(InFile, OutFile)
    elif Id == 'little_prince':
        ConfigFile = '$LARA/Content/the_little_prince/corpus/local_config.json'
        Params = lara_config.read_lara_local_config_file(ConfigFile)
        InFile = '$LARA/tmp_resources/the_little_prince_split.json'
        JSONTraceFile = '$LARA/Content/the_little_prince/corpus/the_little_prince_mwe_annotations.json'
        OutFile = '$LARA/tmp_resources/the_little_prince_mwe_annotated.docx'
        HTMLTraceFile = '$LARA/tmp_resources/the_little_prince_mwe_trace.html'
        apply_marked_mwes_in_split_file(InFile, JSONTraceFile, OutFile, HTMLTraceFile, Params)
    elif Id == 'convert_combray_mwes':
        JSONFileIn = '$LARA/tmp_resources/combray_double_align_tmp_mwe_annotations.json'
        TextFile = '$LARA/tmp_resources/combray_double_align_tmp_mwe_annotations_summary_edited.txt'
        JSONFileOut = '$LARA/Content/combray/corpus/mwe_annotations_double_align.json'
        N = 1000000
        update_mwe_json_file_from_mwe_text_file(JSONFileIn, TextFile, JSONFileOut, N)
    elif Id == 'convert_combray_mwes_small':
        JSONFileIn = '$LARA/tmp_resources/combray_segmented_by_audio_small_tmp_mwe_annotations.json'
        TextFile = '$LARA/tmp_resources/combray_segmented_by_audio_small_tmp_mwe_annotations_summary.txt'
        JSONFileOut = '$LARA/Content/combray/corpus/mwe_annotations_small.json'
        N = 1000000
        update_mwe_json_file_from_mwe_text_file(JSONFileIn, TextFile, JSONFileOut, N)

# Internalise and store MWE file.
def load_mwe_file(File):
    ParsedLines = read_mwe_file(File)
    if ParsedLines == False: 
        return False
    if False in ParsedLines:
        lara_utils.print_and_flush(f'*** Error: unable to internalise MWE entries')
        return False
    Result = store_mwe_defs(ParsedLines)
    #lara_utils.write_json_to_file(mwe_entries, '$LARA/tmp/tmp_mwe_entries.json')
    return Result

def read_mwe_file(File):
    global mwe_entries
    mwe_entries = {}
    if not lara_utils.file_exists(File):
        lara_utils.print_and_flush(f'*** Warning: MWE file not found: {File}')
        return False
    Lines = lara_utils.read_lara_text_file(File).split('\n')
    lara_parse_utils.init_parse_mwe_file()
    return [ lara_parse_utils.parse_mwe_def(Line) for Line in Lines if not null_mwe_line(Line)]

def mwe_txt_file_to_json(InFile, OutFile):
    ParsedLines = read_mwe_file(InFile)
    if ParsedLines == False or False in ParsedLines:
        lara_utils.print_and_flush(f'*** Error: unable to internalise MWE entries')
        return False
    Content = parsed_mwe_lines_to_json_structure(ParsedLines)
    lara_utils.write_json_to_file(Content, OutFile)
    return True

def mwe_json_file_to_txt(InFile, OutFile):
    Content = lara_utils.read_json_file(InFile)
    if Content == False:
        lara_utils.print_and_flush(f'*** Error: unable to read {InFile} as JSON file')
        return False
    if not isinstance(Content, dict) or not 'classes' in Content or not 'transforms' in Content or not 'mwes' in Content:
        lara_utils.print_and_flush(f"*** Error: {InFile} not a dict containing the key 'transforms', 'classes' and 'mwes'")
        return False
    ( Transforms, Classes, MWEs ) = ( Content['transforms'], Content['classes'], Content['mwes'] )
    TransformTextList = [ mwe_json_transform_item_to_text(Transform) for Transform in Transforms ]
    ClassesTextList = [ mwe_json_class_item_to_text(Class, Classes[Class]) for Class in Classes ]
    MWETextList = [ mwe_json_normal_item_to_text(MWE, MWEs[MWE]) for MWE in MWEs ]
    AllLines = [ '\n# Transforms' ] + TransformTextList + \
               [ '\n# Classes' ] + ClassesTextList + \
               [ '\n# Normal MWE entries' ] + MWETextList
    lara_utils.write_lara_text_file('\n'.join(AllLines), OutFile)

#  "*verb* si -> si *verb*"
#  transform: *verb* si -> si *verb*

def mwe_json_transform_item_to_text(Transform):
    return f'transform: {Transform}'

# "di": [ "di", "d'" ]
# class: di di d' 

def mwe_json_class_item_to_text(ClassName, ClassBody):
    return f"class: {ClassName} {' '.join(ClassBody)}"

# "ACCENDERE si": { "name": "accendersi", "pos": "V" }
# ACCENDERE si | POS:V NAME:accendersi

def mwe_json_normal_item_to_text(MWEBody, MWEAnnotations):
    if not 'pos' in MWEAnnotations and not 'name' in MWEAnnotations:
        return MWEBody
    PosComponent = f" POS:{MWEAnnotations['pos']}" if 'pos' in MWEAnnotations and MWEAnnotations['pos'] != '' else ''
    #NameComponent = f" NAME:{MWEAnnotations['name']}" if 'name' in MWEAnnotations and MWEAnnotations['name'] != '' else ''
    NameComponent = f" NAME:{MWEAnnotations['name']}" if 'name' in MWEAnnotations and MWEAnnotations['name'] != '' else \
                    f" NAME:{lara_parse_utils.default_name_for_mwe_words(MWEBody)}"
    return f"{MWEBody} |{PosComponent}{NameComponent}"

def mark_mwes_in_split_file(InFile, AnnotatedJSONTraceFile, JSONTraceFile, Params):
    InList = lara_utils.read_json_file(InFile)
    PreviousJudgementsAssoc = annotated_mwe_trace_file_to_dict(AnnotatedJSONTraceFile, [ 'mwe_okay', 'mwe_not_okay' ])
    Traces = mark_mwes_in_page_oriented_split_list(InList, PreviousJudgementsAssoc, Params)
    if not Traces:
        return False
    return write_mwe_trace_file_json(Traces, JSONTraceFile)

def mwe_matches_file_to_summary(JSONTraceFile, SummaryFile):
    if not lara_utils.file_exists(JSONTraceFile):
        lara_utils.print_and_flush(f'--- Warning: {JSONTraceFile} not found')
        return
    InList = lara_utils.read_json_file(JSONTraceFile)
    OutList = [ summarise_mwe_match_record_as_html_para(Record) for Record in InList ]
    Header = [ '<html>', '<body>' ]
    Coda = [ '</body>', '</html>' ]
    AllLines = Header + OutList + Coda
    lara_utils.write_lara_text_file('\n'.join(AllLines), SummaryFile)
    lara_utils.print_and_flush(f'--- Written {SummaryFile} ({len(OutList)} items)')

def summarise_mwe_match_record_as_html_para(Record):
    MatchText = Record['match']
    MWE = Record['mwe']
    OK = Record['ok']
    HighlightedMWE = emphasize_for_trace(MWE, 'html')
    #return f'<p>{MatchText} [{HighlightedMWE}]</p>'
    return f'<p>{OK} | {HighlightedMWE} | {MatchText}</p>'

def read_split_file_applying_mwes_if_possible_and_expanding_annotated_images(Params):
    SplitFileData0 = read_split_file_applying_mwes_if_possible(Params)
    if SplitFileData0 == False:
        return False
    return lara_picturebook.expand_annotated_images_in_split_list(SplitFileData0)

def read_split_file_applying_mwes_if_possible(Params):
    CorpusFile = Params.corpus
    MWEAnnotationsFile = Params.mwe_annotations_file
    SplitFile = lara_top.lara_tmp_file('split', Params)
    SplitMWEFile = lara_top.lara_tmp_file('split_mwe', Params)
    # Case 1: no MWE annotations file. Just get the split file, remaking it if necessary.
    if not lara_utils.file_exists(MWEAnnotationsFile):
        return lara_split_and_clean.read_split_file(SplitFile, Params)
    # Case 2: split_mwe file is up to date. Return it.
    if lara_utils.file_is_newer_than_file(SplitMWEFile, CorpusFile) and \
       lara_utils.file_is_newer_than_file(SplitMWEFile, SplitFile) and \
       lara_utils.file_is_newer_than_file(SplitMWEFile, MWEAnnotationsFile):
        SplitMWEFileContent = lara_utils.read_json_file(SplitMWEFile)
        if not SplitMWEFileContent:
            lara_utils.print_and_flush(f'*** Warning: internalised file with MWEs {SplitMWEFile} exists but could not be read')
            return False
        else:
            lara_utils.print_and_flush(f'--- Internalised file with MWEs {SplitMWEFile} is up to date')
            return SplitMWEFileContent
    # Case 3: there is an MWE annotations file, but split_mwe file is not up to date. Remake the split_mwe file and return it.
    PageOrientedSplitList = lara_split_and_clean.read_split_file(SplitFile, Params)
    if not PageOrientedSplitList:
        return False
    ( OutList, Traces ) = merge_page_oriented_split_list_and_mwe_annotations_file(PageOrientedSplitList, MWEAnnotationsFile, Params)
    if OutList != False:
        lara_utils.print_and_flush(f'--- Remade internalised file with MWEs {SplitMWEFile}')
        lara_utils.write_json_to_file(OutList, SplitMWEFile)
    else:
        lara_utils.print_and_flush(f'*** Error: unable to remake internalised file with MWEs {SplitMWEFile}')
    return OutList

def apply_marked_mwes_in_split_file(SplitFile, MWEAnnotationsFile, OutFile, HTMLTraceFile, Params):
    InList = lara_utils.read_json_file(SplitFile)
    ( OutList, Traces ) = merge_page_oriented_split_list_and_mwe_annotations_file(InList, MWEAnnotationsFile, Params)
    if not OutList == False:
        lara_transform_tagged_file.split_file_content_to_text_file(OutList, OutFile)
        lara_utils.print_and_flush(f'--- Added {len(Traces)} multi word expression annotations to file')
        return write_mwe_trace_file_html(Traces, HTMLTraceFile)

def merge_page_oriented_split_list_and_mwe_annotations_file(InList, MWEAnnotationsFile, Params):
    Assoc = annotated_mwe_trace_file_to_dict(MWEAnnotationsFile, [ 'mwe_okay' ])
    ( OutList, Traces ) = apply_marked_mwes_in_page_oriented_split_list(InList, Assoc, Params)
    if not isinstance(OutList, list) or OutList == []:
        lara_utils.print_and_flush(f'*** Error: unable to insert MWEs in corpus')
        return ( False, False )
    else:
        return ( OutList, Traces )


def annotated_mwe_trace_file_to_dict(File, PermittedStatusList):
    if not File:
        return {}
    if not lara_utils.file_exists(File):
        lara_utils.print_and_flush(f'*** Warning: MWE annotations file not found: {File}')
        return {}
    ( InList, Assoc, I ) = ( lara_utils.read_json_file(File), {}, 0 )
    if InList == False:
        return {}
    for Record in InList:
        if Record['ok'] in PermittedStatusList:
            Key = key_for_mwe_record(Record)
            Records = Assoc[Key] if Key in Assoc else []
            Records += [ Record ]
            Assoc[Key] = Records
            I += 1
    lara_utils.print_and_flush(f'--- {I} MWE annotations read from {File}')
    return Assoc

# We want a plain list of words. The elements of the 'words' field could be either words or
# [ Word, POSTag ] pairs.
def key_for_mwe_record(Record):
    return tuple([ word_or_pair_to_word(Item) for Item in Record['words'] ])

def word_or_pair_to_word(Item):
    return clean_word_for_mwe_record(Item[0]) if isinstance(Item, list) else Item

def clean_word_for_mwe_record(Word):
    #return lara_parse_utils.remove_html_annotations_from_string(Word)[0]
    #return lara_parse_utils.remove_hashtag_comment_and_html_annotations1(Word, 'delete_comments')[0].strip()
    Cleaned = lara_parse_utils.remove_hashtag_comment_and_html_annotations1(Word, 'delete_comments')[0]
    return Cleaned if word_only_contains_spaces_and_punctuation(Cleaned) else Cleaned.strip()

def word_only_contains_spaces_and_punctuation(Word):
    return len( [ Char for Char in Word if not Char.isspace() and not lara_parse_utils.is_punctuation_char(Char) ] ) == 0

def mark_mwes_in_page_oriented_split_list(InList, PreviousJudgementsAssoc, Params):
    TracesList = [ mark_mwes_in_page(Page, PreviousJudgementsAssoc, Params) for Page in InList ]
    if TracesList == False:
        return False
    AllTraces = [ TraceElement for Trace in TracesList for TraceElement in Trace ]
    return AllTraces

def apply_marked_mwes_in_page_oriented_split_list(InList, Assoc, Params):
    OutPagesAndTraces = [ apply_marked_mwes_in_page(Page, Assoc, Params) for Page in InList ]
    OutPages = [ Item[0] for Item in OutPagesAndTraces ]
    Traces = [ Item[1] for Item in OutPagesAndTraces ]
    AllTraces = [ TraceElement for Trace in Traces for TraceElement in Trace ]
    return ( OutPages, AllTraces )

def mark_mwes_in_page(InPage, PreviousJudgementsAssoc, Params):
    #lara_utils.print_and_flush(f'--- mark_mwes_in_page({InPage}, {PreviousJudgementsAssoc}, Params)')
    ( PageInfo, InSegments ) = InPage
    TracesList = [ mark_mwes_in_segment(Segment, PreviousJudgementsAssoc, Params) for Segment in InSegments ]
    #lara_utils.print_and_flush(f'--- TracesList = {TracesList}')
    if TracesList == False or False in TracesList:
        #lara_utils.print_and_flush(f'--- Return False')
        return False
    AllTraces = [ TraceElement for Trace in TracesList for TraceElement in Trace ]
    #lara_utils.print_and_flush(f'--- Return {AllTraces}')
    return AllTraces

def apply_marked_mwes_in_page(InPage, Assoc, Params):
    ( PageInfo, InSegments ) = InPage
    OutSegmentsAndTraces = [ apply_marked_mwes_in_segment(Segment, Assoc, Params) for Segment in InSegments ]
    OutSegments = [ Item[0] for Item in OutSegmentsAndTraces ]
    Traces = [ Item[1] for Item in OutSegmentsAndTraces ]
    OutPage = ( PageInfo, OutSegments )
    AllTraces = [ TraceElement for Trace in Traces for TraceElement in Trace ]
    return ( OutPage, AllTraces )

def mark_mwes_in_segment(InSegment, PreviousJudgementsAssoc, Params):
    #lara_utils.print_and_flush(f'--- mark_mwes_in_segment({InSegment}, {PreviousJudgementsAssoc}, Params)')
    MaxGaps = Params.mwe_max_gaps
    if lara_picturebook.is_annotated_image_segment(InSegment):
        InSegments = lara_picturebook.annotated_image_segments(InSegment)
        TracesList = [ mark_mwes_in_segment(InSegment, PreviousJudgementsAssoc, Params)
                       for InSegment in InSegments ]
        if False in TracesList:
            #lara_utils.print_and_flush(f'--- Return False')
            return False
        AllTraces = [ TraceElement for Trace in TracesList for TraceElement in Trace ]
        return AllTraces
    ( Raw, Clean, Words, Tag ) = InSegment
    WordsWithPOS = [ word_lemma_pair_to_triple(Item) for Item in Words ]
    RegularisedWordsWithPOS = [ regularise_word_lemma_pair(Item) for Item in Words ]
    if Words == False:
        lara_utils.print_and_flush(f'*** Error: bad surface/lemma list: {Words}')
        #lara_utils.print_and_flush(f'--- Return False')
        return False
    AllTraces = []
    for I in range(0, len(RegularisedWordsWithPOS)):
        ( Surface0, Lemma0, POSTag ) = RegularisedWordsWithPOS[I]
        Surface = regularise_surface_word(Surface0)
        Lemma = regularise_lemma(Lemma0)
        PossibleMatches = mwe_matches(Surface, Lemma, RegularisedWordsWithPOS, I, MaxGaps)
        for Match in PossibleMatches:
            TraceElement = trace_line_for_match(Match, WordsWithPOS, Clean, 'json')
            #lara_utils.prettyprint(TraceElement)
            ( IndexList, MWEName, POS ) = Match
            JudgementFromExistingMatch = check_for_existing_match(MWEName, IndexList, WordsWithPOS)
            #if len(IndexList) == 2 and IndexList[0] + 1 == IndexList[1]:
            #    lara_utils.print_and_flush(f'{JudgementFromExistingMatch} = check_for_existing_match({MWEName}, {IndexList}, {Words})')
            PreviousJudgement = judgement_for_trace(TraceElement, PreviousJudgementsAssoc)
            if JudgementFromExistingMatch in [ 'mwe_okay', 'mwe_not_okay' ]:
                AllTraces += [ change_judgement_in_trace(TraceElement, JudgementFromExistingMatch) ]
            elif PreviousJudgement in [ 'mwe_okay', 'mwe_not_okay' ]:
                AllTraces += [ change_judgement_in_trace(TraceElement, PreviousJudgement) ]
            else:
                AllTraces += [ TraceElement ]
    #lara_utils.print_and_flush(f'--- Return {AllTraces}')
    return AllTraces

def word_lemma_pair_to_triple(Item):
    if not isinstance(Item, list) and len(Item, 2):
        lara_utils.print_and_flush(f'*** Error: bad element: {Item}')
        return False
    ( Surface, LemmaTag ) = Item
    Components = LemmaTag.split('/')
    ( Lemma, POSTag ) = ( LemmaTag, '' ) if len(Components) == 1 else Components[:2]
    return ( Surface, Lemma, POSTag )

def regularise_word_lemma_pair(Item):
    if not isinstance(Item, list) and len(Item, 2):
        lara_utils.print_and_flush(f'*** Error: bad element: {Item}')
        return False
    ( Surface, LemmaTag ) = Item
    RegularisedSurface = regularise_surface_word(Surface)
    Components = LemmaTag.split('/')
    ( Lemma, POSTag ) = ( LemmaTag, '' ) if len(Components) == 1 else Components[:2]
    return ( RegularisedSurface, Lemma, POSTag )

def change_judgement_in_trace(TraceElement, Judgement):
    TraceElement['ok'] = Judgement
    return TraceElement

def apply_marked_mwes_in_segment(InSegment, Assoc, Params):
    if lara_picturebook.is_annotated_image_segment(InSegment):
        Image = lara_picturebook.annotated_image_image(InSegment)
        InSegments = lara_picturebook.annotated_image_segments(InSegment)
        OutSegmentsAndTraces = [ apply_marked_mwes_in_segment(InSegment, Assoc, Params)
                                 for InSegment in InSegments ]
        OutSegments = [ Item[0] for Item in OutSegmentsAndTraces ]
        Traces = [ Item[1] for Item in OutSegmentsAndTraces ]
        AllTraces = [ TraceElement for Trace in Traces for TraceElement in Trace ]
        return ( lara_picturebook.make_annotated_image_segment(Image, OutSegments), AllTraces )
    ( Raw0, Clean0, Words0, Tag0 ) = InSegment
    Key = tuple( [ clean_word_for_mwe_record(Pair[0]) for Pair in Words0 ] )
    if Key not in Assoc:
        return ( InSegment, [] )
    ( OutSegment, Trace ) = ( copy.copy(InSegment), [])
    ( Raw, Clean, Words, Tag ) = OutSegment
    Records = Assoc[Key]
    for Record in Records:
        ( IndexList, MWEName, POS ) = ( Record['word_index_list'], Record['mwe'], Record['pos'] )
        Match = [ IndexList, add_mwe_part_tag(MWEName, IndexList), POS ]
        OverlapStatus = check_for_overlapping_match(MWEName, IndexList, Words)
        if OverlapStatus in [ 'does_not_overlap', 'already_done' ]:
            # apply_match changes Words to replace the lemmas
            # If we've already applied the match, we do it again because we may be fixing up the tags
            # but if so, we don't add the record to the trace
            TraceElement = apply_match(Match, Words, Clean, 'html', Params)
            if OverlapStatus != 'already_done':
                Trace += [ TraceElement ]
            Raw = update_raw_text_from_word_list(Words, Raw)
    OutSegment = ( Raw, Clean, Words, Tag )
    return ( OutSegment, Trace )

# In this version, we check to see if one of the words in the match has already been used for a different MWE
# If it has, we return True, else we return False

def check_for_overlapping_match(MWEName, IndexList, Words):
    for Index in IndexList:
        ( Surface, Lemma ) = Words[Index]
        if is_mwe_lemma(Lemma):
            OtherMWEName = strip_off_mwe_part_tag_and_pos_tag(Lemma)
            SegmentText = word_tuples_to_string(Words)
            if OtherMWEName != MWEName:
                lara_utils.print_and_flush(f'*** Warning: overlapping MWE applications, "{OtherMWEName}" and "{MWEName}" in "{SegmentText}"')
                return 'overlaps_with_other_mew'
            else:
                return 'already_done'
    return 'does_not_overlap'

# In this version, we check to see if either
#
# a) One of the words has already been used for an existing match, if so return 'mwe_not_okay'
# b) All of the words have already been used for this match, if so return 'mwe_okay'
# c) Otherwise, return False
def check_for_existing_match(MWEName, IndexList, Words):
    all_words_used_for_this_match = True
    for Index in IndexList:
        ( Surface, Lemma, POS ) = Words[Index]
        if Lemma != strip_off_mwe_part_tag_and_pos_tag(Lemma):
            OtherMWEName = strip_off_mwe_part_tag_and_pos_tag(Lemma)
            SegmentText = word_tuples_to_string(Words)
            if OtherMWEName != MWEName:
                return 'mwe_not_okay'
        else:
            all_words_used_for_this_match = False
    return 'mwe_okay' if all_words_used_for_this_match else False
    
def add_mwe_part_tag(MWEName, IndexList):
    return f'mwe_part_{len(IndexList)}_{MWEName}'

# The next two functions assume that an MWE will never be more than 9 words long,
# so the number part of the tag wil be a single digit
def strip_off_mwe_part_tag(LemmaName):
    if LemmaName.startswith('mwe_part_'):
        return LemmaName[len('mwe_part_') + 2:]
    else:
        return LemmaName

def strip_off_mwe_part_tag_and_pos_tag(LemmaName):
    LemmaName1 = LemmaName.split('/')[0]
    if LemmaName1.startswith('mwe_part_'):
        return LemmaName1[len('mwe_part_') + 2:]
    else:
        return LemmaName1

def strip_off_mwe_part_tag_returning_lemma_and_length(Lemma):
    if is_mwe_lemma(Lemma):
        Lemma1 = regularise_pos_tag_for_mwe_lemma(Lemma)
        return ( Lemma1[len('mwe_part_') + 2:], int(Lemma1[len('mwe_part_'):len('mwe_part_') + 1]) )
    else:
        return ( Lemma, 1 )

def regularise_pos_tag_for_mwe_lemma(Lemma):
    if is_mwe_lemma(Lemma) and '/' in Lemma and len(Lemma.split('/')) == 2:
        ( MainLemma, POSTag) = Lemma.split('/')
        #return f'{MainLemma}/MWE'
        return f'{MainLemma}/{POSTag}'
    else:
        return Lemma
                    
def is_mwe_word_lemma_pair(Pair):
    return isinstance(Pair, list) and len(Pair) == 2 and is_mwe_lemma(Pair[1])

def is_mwe_lemma(LemmaName):
    return LemmaName.startswith('mwe_part_')
 
def mwe_matches(Surface, Lemma, Words, I, MaxGaps):
    # Allow overlapping matches in order to get negative training examples
    # If the current word is already part of an MWE, give up
    #if is_mwe_lemma(Lemma):
    #    return []
    SurfaceMWEDefs = get_mwe_defs('surface', Surface)
    LemmaMWEDefs = get_mwe_defs('lemma', Lemma)
    VirtualMWEDefs = virtual_mwe_defs(Lemma, Words, I)
    AllMWEDefs = SurfaceMWEDefs + LemmaMWEDefs + VirtualMWEDefs
    Matches = []
    for ( DefWords, Name, POS ) in AllMWEDefs:
        Match = match_mwe_def(DefWords, Words, I, Name, POS, MaxGaps)
        if Match != False:
            Matches += [ Match ]
    return Matches

# If we've got the first occurrence in this segment of an MWE lemma like 'mwe_part_2_kick off',
# we create a virtual MWE def to find the rest of it.
def virtual_mwe_defs(Lemma, Words, I):
    if is_mwe_lemma(Lemma) and beginning_of_mwe(Words, I, Lemma):
        ( MWEName, NComponents ) = strip_off_mwe_part_tag_returning_lemma_and_length(Lemma)
        ReducedMWEName = MWEName.split('/')[0]
        POS = pos_for_mwe_name(ReducedMWEName)
        VirtualDef = [ [ [ 'lemma', Lemma ] for I in range(0, NComponents-1) ], MWEName, POS ]
        return [ VirtualDef ]
    else:
        return []

def beginning_of_mwe(Words, I, Lemma):
    for ( Surface, OtherLemma, POS ) in Words[:I]:
        if OtherLemma == Lemma:
            return False
    return True

def match_mwe_def(DefWords, Words, I, Name, POS, MaxGaps):
    IndexListRest = index_sequence(DefWords, Words, I, [], 0, MaxGaps)
    return [ [ I ] + IndexListRest, Name, POS ] if IndexListRest else False

def index_sequence(DefWords, Words, I, IndicesSoFar, GapsSoFar, MaxGaps):
    if GapsSoFar > MaxGaps:
        return False
    if len(DefWords) == 0:
        return IndicesSoFar
    ( DefWordsF, DefWordsR) = ( DefWords[0], DefWords[1:] )
    ( SurfaceOrLemma, SearchWord ) = DefWordsF
    NextI = mwe_index(SurfaceOrLemma, SearchWord, I + 1, Words, GapsSoFar, MaxGaps)
    # Allow overlapping matches in order to get negative training examples
    #if NextI == False or is_mwe_word_lemma_pair(Words[NextI]):
    if NextI == False:
        return False
    else:
        NewGaps = NextI - ( I + 1 )
        GapsSoFar1 = GapsSoFar + NewGaps
        return index_sequence(DefWordsR, Words, NextI, IndicesSoFar + [ NextI ], GapsSoFar1, MaxGaps)

def mwe_index(SurfaceOrLemma, SearchWord, I, Words, GapsSoFar, MaxGaps):
    for Index in range(I, len(Words)):
        ( Surface, Lemma, POSTag ) = Words[Index]
        # If lemmas contain lexical casing, we need to regularise them
        if SurfaceOrLemma == 'surface' and SearchWord == regularise_surface_word(Surface) or \
           SurfaceOrLemma == 'lemma' and SearchWord == regularise_lemma(Lemma): 
            return Index
    return False

def best_match(PossibleMatches):
    SortedMatches = sorted(PossibleMatches, key = lambda x: len(x[0]), reverse=True)
    return SortedMatches[0]

def apply_match(Match, Segment, Clean, TraceFileFormat, Params):
    #lara_utils.print_and_flush(f'--- Apply match: {Match}')
    ( IndexList, MWEName, POS ) = Match
    NewLemma = add_pos_to_lemma_if_necessary(MWEName, POS, Params)
    if not NewLemma:
        lara_utils.print_and_flush(f'*** Error: unable to combine MWE name {MWEName} with POS tag {POS}')
        return False
    for Index in IndexList:
        ( Surface, OldLemma ) = Segment[Index]
        Segment[Index] = [ Surface, NewLemma ]
    return trace_line_for_match(Match, Segment, Clean, TraceFileFormat)

def add_pos_to_lemma_if_necessary(MWEName, POS, Params):
    Components = MWEName.split('/')
    if len(Components) == 1 and Params.add_postags_to_lemma == 'no':
        return MWEName
    elif len(Components) <= 2:
        return f'{Components[0]}/{POS}'
    else:
        return False

def trace_line_for_match(Match, Segment, Clean, TraceFileFormat):
    if TraceFileFormat == 'html':
        return html_trace_line_for_match(Match, Segment, Clean)
    else:
        return json_trace_line_for_match(Match, Segment, Clean)

def html_trace_line_for_match(Match, Segment, Clean):
    ( NSkipped, MainText ) = n_words_skipped_and_string_for_match(Match, Segment, 'html')
    MatchText = emphasize_for_trace(strip_off_mwe_part_tag_and_pos_tag(Match[1]), 'html')
    Line = f'<p>Marked "{MatchText}" in "{MainText}" ({NSkipped} words skipped)</p>'
    return ( NSkipped, Line )

def json_trace_line_for_match(Match, Segment, Clean):
    ( IndexList, MWEName, POS ) = Match
    ( NSkipped, MainText ) = n_words_skipped_and_string_for_match(Match, Segment, 'json')
    SurfaceWordsAndPOSTags = [ [ Item[0], Item[2] ] for Item in Segment ]
    Record = { 'match': MainText,
               'mwe': MWEName,
               'pos': POS,
               'ok':'mwe_status_unknown',
               'skipped': NSkipped,
               'words': SurfaceWordsAndPOSTags,
               'word_index_list': IndexList
               }
    return Record

def new_mwe_candidate(Record):
    return isinstance(Record, dict) and 'ok' in Record and Record['ok'] == 'mwe_status_unknown'

def judgement_for_trace(TraceElement, PreviousJudgementsAssoc):
    Key = tuple([ clean_word_for_mwe_record(Item[0]) for Item in TraceElement['words'] ])
    if not Key in PreviousJudgementsAssoc:
        return False
    PreviousJudgements = PreviousJudgementsAssoc[Key]
    for PreviousJudgement in PreviousJudgements:
        if PreviousJudgement['mwe'] == TraceElement['mwe'] and \
           PreviousJudgement['word_index_list'] == TraceElement['word_index_list']:
            return PreviousJudgement['ok']
    return False

def n_words_skipped_and_string_for_match(Match, Segment, TraceFileFormat):
    ( IndexList, MWEName, POS ) = Match
    Segment1 = copy.copy(Segment)
##    for Index in IndexList:
##        Surface = Segment1[Index][0]
##        Segment1[Index] = [ emphasize_for_trace(clean_word_for_mwe_record(Surface), TraceFileFormat), MWEName ]
    for Index in range(0, len(Segment1)):
        ( Surface, Lemma ) = Segment1[Index][:2]
        if Index in IndexList:
            Segment1[Index] = [ emphasize_for_trace(clean_word_for_mwe_record(Surface), TraceFileFormat), MWEName ]
        else:
            Segment1[Index] = [ clean_word_for_mwe_record(Surface), Lemma ]
    return ( n_words_skipped_in_index_list(IndexList, Segment), word_tuples_to_string_no_clean(Segment1) )

def n_words_skipped_in_index_list(IndexList, Segment):
    if len(IndexList) < 2:
        return 0
    else:
        return IndexList[1] - ( IndexList[0] + 1 ) - \
               n_filler_words_in_interval(IndexList[0], IndexList[1], Segment) +  \
               n_words_skipped_in_index_list(IndexList[1:], Segment)

def n_filler_words_in_interval(Lower, Upper, Segment):
    ( I, Count ) = ( Lower, 0 )
    while True:
        if I >= Upper:
            return Count
        elif Segment[I][1] == '':
            Count += 1
        I += 1

def word_tuples_to_string(Segment):
    return lara_parse_utils.regularise_spaces(''.join([ clean_word_for_mwe_record(Pair[0]) for Pair in Segment ]))

def word_tuples_to_string_no_clean(Segment):
    return lara_parse_utils.regularise_spaces(''.join([ Pair[0] for Pair in Segment ]))

def emphasize_for_trace(Word, TraceFileFormat):
    #return f'<span style="color:red">{Word}</span>' if TraceFileFormat == 'html' else f'*{Word}*'
    return f'<span style="color:red">{Word}</span>' if TraceFileFormat == 'html' else f"<span style='color:#ff6666'>{Word}</span>"

def update_raw_text_from_word_list(Pairs, Raw):
    ( Index, N, Raw1 ) = ( 0, len(Raw), '' )
    for ( Word, Lemma ) in Pairs:
        if Lemma != '':
            ( Index, Raw1 ) = update_raw_text_from_word_list_single(Word, Lemma, Raw, Index, N, Raw1)
    return Raw1 + Raw[Index:]
        
def update_raw_text_from_word_list_single(Word, Lemma, Raw, Index0, N, Raw1):
    #lara_utils.print_and_flush( (Word, Lemma, Raw, Index0, N, Raw1) )
    ( InsideTagP, InsideAtSigns ) = ( '*not_inside_tag*', '*not_inside_at_signs*' )
    Index = Index0
    while True:
        if Index >= N:
            lara_utils.print_and_flush(f'*** Error: unable to find "{Word}" in "{Raw[Index0:]}"')
            lara_utils.print_and_flush(f'*** Error: (full string was "{Raw}", lemma was "{Lemma}")')
            lara_utils.print_and_flush(f'*** Error: status = {( InsideTagP, InsideAtSigns )}')
            return False
        elif InsideTagP == '*not_inside_tag*' and lara_parse_utils.substring_found_at_index(Raw, Index, Word):
            ( Index, Raw1 ) = ( Index + len(Word), Raw1 + Word )
            # Index now marks the end of Word. 
            # If the next char is @ and we're inside @-signs, it's enclosed in @ ... @, so skip one.
            if Index < N and Raw[Index] == '@' and InsideAtSigns == '*inside_at_signs*':
                ( Index, Raw1, InsideAtSigns ) = ( Index + 1, Raw1 + '@', '*not_inside_at_signs*' )
            # There could be apostrophes or hyphens before the #, so skip and transfer them to Raw1
            ( Index, Raw1 ) = skip_apostrophes_and_hyphens(Raw, Raw1, Index, N)
            # And if the next char is #, there's a tag, so skip to the end of the tag 
            if Index < N and Raw[Index] == '#':
                Index1 = Raw.find('#', Index + 1) 
                if Index1 < 0:
                    # There was no matching #
                    lara_utils.print_and_flush(f'*** Error: unmatched # in "{Raw[Index + 1:]}"')
                    return False
                else:
                    # There was one, so skip it
                    Index = Index1 + 1
            # If needed, add #Lemma# as the tag
            if Word.lower() != Lemma:
                Raw1 = Raw1 + f'#{Lemma}#'
            return ( Index, Raw1 )
        else:
            if Raw[Index] == '<':
                InsideTagP = '*inside_tag*'
            elif Raw[Index] == '>':
                InsideTagP = '*not_inside_tag*'
            elif Raw[Index] == '@' and InsideAtSigns == '*not_inside_at_signs*':
                InsideAtSigns = '*inside_at_signs*'
            elif Raw[Index] == '@' and InsideAtSigns == '*inside_at_signs*':
                InsideAtSigns = '*not_inside_at_signs*'
            Raw1 += Raw[Index]
            Index += 1

def skip_apostrophes_and_hyphens(Raw, Raw1, Index, N):
    _hyphens_and_commas = "'’-"
    while True:
        if Index >= N or not Raw[Index] in _hyphens_and_commas:
            return ( Index, Raw1 )
        HyphenOrComma = Raw[Index]
        Raw1 += HyphenOrComma
        Index += 1

def parsed_mwe_lines_to_json_structure(ParsedLines):
    ( Transforms, ClassDefs, RegularDefs ) = ( [], {}, {} )
    for ParsedLine in ParsedLines:
        add_parsed_mwe_line_to_json_structures(ParsedLine, Transforms, ClassDefs, RegularDefs)
    return { 'transforms': Transforms, 'classes': ClassDefs, 'mwes': RegularDefs }

def add_parsed_mwe_line_to_json_structures(ParsedLine, Transforms, ClassDefs, RegularDefs):
    if is_parsed_transform_def(ParsedLine):
        Transforms += [ parsed_transform_def_to_string(ParsedLine) ]
    elif is_parsed_class_def(ParsedLine):
        ( ClassName, ClassEntries ) = ( ParsedLine['name'], ParsedLine['body'] )
        ClassDefs[ClassName] = ClassEntries
    elif is_parsed_regular_def(ParsedLine):
        ( MultiwordName, POS, Body ) = ( ParsedLine['name'], ParsedLine['pos'], ParsedLine['body'] )
        Key = parsed_mwe_body_to_string(Body)
        RegularDefs[Key] = { 'name': MultiwordName, 'pos': POS }
    else:
        lara_utils.print_and_flush(f'*** Error: unknown element in internalised MWE file: {ParsedLine}')

def parsed_transform_def_to_string(ParsedLine):
    ( LHS, RHS ) = ( ParsedLine['lhs'], ParsedLine['rhs'] )
    return f'{parsed_transform_def_side_to_string(LHS)} -> {parsed_transform_def_side_to_string(RHS)}'

def parsed_transform_def_side_to_string(LHSOrRHS):
    return ' '.join([ Element[1] for Element in LHSOrRHS ])

def parsed_mwe_body_to_string(Body):
    return ' '.join([ parsed_mwe_body_element_to_string(Element) for Element in Body ])

def parsed_mwe_body_element_to_string(Element):
    ( Type, Word ) = Element
    #return Word.upper() if Type == 'lemma' else Word.lower()
    return f'*{Word}*' if Type == 'lemma' else Word.lower()
            
mwe_entries = {}

def store_mwe_defs(ParsedLines):
    global mwe_entries
    mwe_entries = {}
    # Do the transforms and class defs first since the regular defs will need them
    return store_mwe_transforms(ParsedLines) and \
           store_mwe_class_defs(ParsedLines) and \
           store_mwe_regular_defs(ParsedLines)

def store_mwe_transforms(ParsedLines):
    global mwe_entries
    Result = True
    for ParsedLine in ParsedLines:
        if is_parsed_transform_def(ParsedLine):
            if not store_mwe_transform_def(ParsedLine):
                Result =  False
    return Result

def store_mwe_class_defs(ParsedLines):
    global mwe_entries
    Result = True
    for ParsedLine in ParsedLines:
        if is_parsed_class_def(ParsedLine):
            if not store_mwe_class_def(ParsedLine):
                Result =  False
    return Result

def store_mwe_regular_defs(ParsedLines):
    global mwe_entries
    Result = True
    for ParsedLine in ParsedLines:
        if is_parsed_regular_def(ParsedLine):
            if not store_mwe_regular_def(ParsedLine):
                Result =  False
    return Result

def is_parsed_transform_def(ParsedLine):
    return isinstance(ParsedLine, dict) and 'type' in ParsedLine and ParsedLine['type'] == 'transform'

def store_mwe_transform_def(ParsedLine):
    global mwe_entries
    ( LHS, RHS ) = ( ParsedLine['lhs'], ParsedLine['rhs'] )
    transform_list = mwe_entries['transforms'] if 'transforms' in mwe_entries else []
    mwe_entries['transforms'] = transform_list + [ ParsedLine ]
    return True

def is_parsed_class_def(ParsedLine):
    return isinstance(ParsedLine, dict) and 'type' in ParsedLine and ParsedLine['type'] == 'class'

def store_mwe_class_def(ParsedLine):
    global mwe_entries
    ( ClassName, ClassEntries ) = ( ParsedLine['name'], ParsedLine['body'] )
    subdict = mwe_entries['class'] if 'class' in mwe_entries else {}
    if ClassName in subdict:
        lara_utils.print_and_flush(f'*** Error: MWE word class {ClassName} multiply defined')
        return False
    subdict[ClassName] = ClassEntries
    mwe_entries['class'] = subdict
    return True

def is_parsed_regular_def(ParsedLine):
    return isinstance(ParsedLine, dict) and 'type' in ParsedLine and ParsedLine['type'] == 'mwe_def'

def store_mwe_regular_def(ParsedLine):
    global mwe_entries
    ( MultiwordName, POS, Body ) = ( ParsedLine['name'], ParsedLine['pos'], ParsedLine['body'] )
    for ExpandedParsedLine in expand_mwe_regular_def(Body):
        store_expanded_mwe_regular_def(ExpandedParsedLine, MultiwordName, POS)
    return True

def expand_mwe_regular_def(Body0):
    TransformedBodies = apply_transforms(Body0)
    ExpandedLists = [ expand_mwe_regular_def1(Body) for Body in TransformedBodies ]
    return [ ExpandedBody for ExpandedList in ExpandedLists for ExpandedBody in ExpandedList ]

def apply_transforms(Body):
    Transforms = get_transforms()
    Transformed0 = [ apply_transform(Transform, Body) for Transform in Transforms ]
    return [ Body ] + lara_utils.non_false_members(Transformed0)

def get_transforms():
    global mwe_entries
    return mwe_entries['transforms'] if 'transforms' in mwe_entries else []

# Return result of applying transform if possible, else False
def apply_transform(Transform, Body):
    #lara_utils.print_and_flush(f'--- Apply transform {Transform} to {Body}')
    ( LHS, RHS ) = ( Transform['lhs'], Transform['rhs'] )
    if len(LHS) != len(Body):
        return False
    Substitutions = {}
    for I in range(0, len(Body)):
        ( TransformElement, BodyElement ) = ( LHS[I], Body[I] )
        ( TransformElementType, TransformElementContent ) = TransformElement
        ( BodyElementType, BodyElementContent ) = BodyElement
        if TransformElementType == 'var':
            Substitutions[TransformElementContent] = BodyElement
        elif TransformElementType == 'const' and TransformElementContent != BodyElementContent:
            return False
    Result = apply_transform_substitutions(RHS, Substitutions)
    if not Result:
        lara_utils.print_and_flush(f'*** Error: unable to apply transform {Transform} to {Body}')
    return Result

def apply_transform_substitutions(RHS, Substitutions):
    return [ apply_transform_substitutions_to_element(Element, Substitutions) for Element in RHS ]

def apply_transform_substitutions_to_element(Element, Substitutions):
    ( ElementType, ElementContent ) = Element
    if ElementType == 'const':
        return [ 'surface', ElementContent ]
    elif ElementType == 'var' and ElementContent in Substitutions:
        return Substitutions[ElementContent]
    else:
        return False

def expand_mwe_regular_def1(Body):
    if len(Body) == 1:
        return expand_mwe_regular_def_component(Body[0])
    ( First, Rest ) = ( Body[0], Body[1:] )
    ExpandedFirst = expand_mwe_regular_def_component(First)
    ExpandedRest = expand_mwe_regular_def(Rest)
    return [ F + R for F in ExpandedFirst for R in ExpandedRest ]

def expand_mwe_regular_def_component(Component):
    ( Type, Word ) = Component
    if Type == 'surface' and is_mwe_word_class(Word):
        return [ [ [ 'surface', ClassMember ] ] for ClassMember in get_mwe_word_class(Word) ]
    else:
        return [ [ Component ] ]

def store_expanded_mwe_regular_def(ParsedLine, MultiwordName, POS):
    global mwe_entries
    ( SurfaceOrLemma, Word ) = ParsedLine[0]
    subdict = mwe_entries[SurfaceOrLemma] if SurfaceOrLemma in mwe_entries else {}
    Entries = subdict[Word] if Word in subdict else []
    Entries += [ [ ParsedLine[1:], MultiwordName, POS ] ]
    subdict[Word] = Entries
    mwe_entries[SurfaceOrLemma] = subdict
    store_pos_for_mwe_name(MultiwordName, POS)
    return True

def store_pos_for_mwe_name(MultiwordName, POS):
    global mwe_entries
    if not 'pos_for_mwe_name' in mwe_entries:
        mwe_entries['pos_for_mwe_name'] = {}
    subdict = mwe_entries['pos_for_mwe_name']
    subdict[MultiwordName] = POS

def pos_for_mwe_name(MultiwordName):
    global mwe_entries
    if not 'pos_for_mwe_name' in mwe_entries:
        lara_utils.print_and_flush(f'*** Warning: undeclared MWE in text: "{MultiwordName}"')
        return ''
    subdict = mwe_entries['pos_for_mwe_name']
    Result = subdict[MultiwordName] if  MultiwordName in subdict else 'MWE'
    #lara_utils.print_and_flush(f'pos_for_mwe_name({MultiwordName}) = {Result}')
    return Result

def construct_multiword_name(ParsedLine):
    return ' '.join([ Component[1] for Component in ParsedLine ])

def is_mwe_word_class(Word):
    return 'class' in mwe_entries and Word in mwe_entries['class']

def get_mwe_word_class(Word):
    if 'class' in mwe_entries and Word in mwe_entries['class']:
        return mwe_entries['class'][Word]
    else:
        lara_utils.print_and_flush(f'*** Error: unable to access MWE class for "{Word}"')
        return False

def get_mwe_defs(SurfaceOrLemma, Word):
    global mwe_entries
    if not SurfaceOrLemma in mwe_entries:
        return []
    subdict = mwe_entries[SurfaceOrLemma]
    return subdict[Word] if Word in subdict else []

def write_mwe_trace_file_html(TraceElements, TraceFile):
    SortedTraces = sorted(TraceElements, key=lambda x: x[0])
    TraceLines = [ TraceElement[1] for TraceElement in SortedTraces ]
    AllLines = mwe_trace_file_intro() + TraceLines + mwe_trace_file_coda()
    return lara_utils.write_lara_text_file('\n'.join(AllLines), TraceFile)

def write_mwe_trace_file_json(TraceElements, TraceFile):
    TraceElements1 = remove_duplicates_from_json_traces(TraceElements)
    SortedTraces = sorted(TraceElements1, key=lambda x: x['skipped'])
    Result = lara_utils.write_json_to_file(SortedTraces, TraceFile)
    NNewTraces = count_new_mwe_candidates(SortedTraces)
    lara_utils.print_and_flush(f'--- Found {NNewTraces} new candidate multi word expressions ({len(SortedTraces)} total)')
    return Result

def remove_duplicates_from_json_traces(Traces):
    ( Assoc, OutList ) = ( {}, [] )
    for Trace in Traces:
        Key = tuple([ clean_word_for_mwe_record(Item[0]) for Item in Trace['words'] ] + \
                    Trace['word_index_list'] + \
                    [ Trace['mwe'] ])
        if not Key in Assoc:
            OutList += [ Trace ]
            Assoc[Key] = True
    return OutList

def count_new_mwe_candidates(Records):
    return len([ Record for Record in Records if new_mwe_candidate(Record) ])

def mwe_trace_file_intro():
    return [ '<html>' ]

def mwe_trace_file_coda():
    return [ '</html>' ]

def list_of_mwe_def_elements(List):
    if not isinstance(List, list):
        return False
    for X in List:
        if not isinstance(X, list) or len(X) != 2 or not X[0] in ['surface', 'lemma']:
            return False
    return True

def list_of_strs(List):
    if not isinstance(List, list):
        return False
    for X in List:
        if not isinstance(X, str):
            return False
    return True

# '\ufeff' = BOM mark - can get in if the file is read with the wrong encoding
def null_mwe_line(Line):
    return Line == '' or Line == '\ufeff' or Line.isspace() or Line[0] == '#' 

def regularise_surface_word(Word):
    #return Word.lower()
    return clean_word_for_mwe_record(Word).lower()

def regularise_lemma(Lemma):
    return Lemma.lower()

# ---------------------------------------

def make_mwes_canonical(InFile, OutFile):
    InText = lara_utils.read_lara_text_file(InFile)
    if not InText:
        return False
    OutText = make_mwes_canonical_in_string(InText)
    if not OutText:
        return False
    lara_utils.write_lara_text_file(OutText, OutFile)

def make_mwes_canonical_in_string(InText):
    # If there's no @ in the string, we don't need to do anything
    if InText.find('@') < 0:
        return InText
    ( OutText, I, N, MWECount ) = ( '', 0, len(InText), 0 )
    while I < N:
        Char = InText[I]
        if Char != '@':
            OutText += Char
            I += 1
        else:
            MWEResult = read_mwe_from_string(InText, I, N)
            if not MWEResult:
                lara_utils.print_and_flush(f'*** Error: unable to read MWE at "{InText[I:I+100]}"')
                return False
            ( Raw, Surface, Lemma, EndI) = MWEResult
            Components = Surface.split()
            if len(Components) == 1:
                OutText += Raw
                I += len(Raw)
            else:
                CanonicalMWE = make_single_mwe_canonical(Surface, Lemma)
                OutText += CanonicalMWE
                I += len(Raw)
            MWECount += 1
    if MWECount > 0:
        lara_utils.print_and_flush(f'--- Replaced {MWECount} MWEs with canonical versions')
    return OutText

def read_mwe_from_string(InText, StartAtSignIndex, N):
    CloseAtSignIndex = InText.find('@', StartAtSignIndex+1)
    if CloseAtSignIndex < 0:
        return False
    Surface = InText[StartAtSignIndex+1:CloseAtSignIndex]
    if CloseAtSignIndex+1 < N and InText[CloseAtSignIndex+1] == '#':
        StartHashIndex = CloseAtSignIndex+1
        CloseHashIndex = InText.find('#', StartHashIndex+1)
        if CloseHashIndex < 0:
            return False
        Lemma = InText[StartHashIndex+1:CloseHashIndex]
        EndI = CloseHashIndex+1
    else:
        Lemma = Surface.lower()
        EndI = CloseAtSignIndex+1
    Raw = InText[StartAtSignIndex:EndI]
    return ( Raw, Surface, Lemma, EndI)                                    

def make_single_mwe_canonical(Surface, Lemma):
    Components = Surface.split()
    N = len(Components)
    MWELemma = f'mwe_part_{N}_{Lemma}'
    return ' '.join([ f'{Component}#{MWELemma}#' for Component in Components ])

# ---------------------------------------

def simplify_mwe_lemmas_in_split_list(SplitList):
    return [ simplify_mwe_lemmas_in_page(Page) for Page in SplitList ]

def simplify_mwe_lemmas_in_page(Page):
    ( PageInfo, Segments ) = Page
    return ( PageInfo, [ simplify_mwe_lemmas_in_segment(Segment) for Segment in Segments ] )

def simplify_mwe_lemmas_in_segment(Segment):
    ( Raw, Clean, Pairs, Tag ) = Segment
    return ( Raw, Clean, simplify_mwe_lemmas_in_annotated_pairs(Pairs), Tag )

def simplify_mwe_lemmas_in_annotated_pairs(Pairs):
    return [ simplify_mwe_lemmas_in_pair(Pair) for Pair in Pairs ]

def simplify_mwe_lemmas_in_pair(Pair):
    ( Surface, Lemma ) = Pair
    return ( Surface, simplify_mwe_lemma(Lemma) )

def simplify_mwe_lemma(Lemma):
    return strip_off_mwe_part_tag_returning_lemma_and_length(Lemma)[0]

# ---------------------------------------

#def split_file_and_token_translation_file_to_translation_pairs_taking_account_of_mwes(SplitFile, TokenTranslationFile):
def split_file_and_token_translation_file_to_translation_pairs_taking_account_of_mwes(Params, TokenTranslationFile):
    Triples = split_file_and_token_translation_file_to_translation_context_tuples_taking_account_of_mwes(Params, TokenTranslationFile)
    return [ Triple[:2] for Triple in Triples ]

#def split_file_and_token_translation_file_to_translation_context_triples_taking_account_of_mwes(SplitFile, TokenTranslationFile):
def split_file_and_token_translation_file_to_translation_context_tuples_taking_account_of_mwes(Params, TokenTranslationFile):
    #SplitList = lara_utils.read_json_file(SplitFile)
    SplitList = read_split_file_applying_mwes_if_possible(Params)
    TokenTranslationList0 = lara_utils.read_json_file(TokenTranslationFile)
    TokenTranslationList = [ Record for Record in TokenTranslationList0 if nonempty_token_translation_record(Record) ]
    WordIndicesAndContextsList = split_list_to_words_indices_and_contexts(SplitList, Params)
    ( Len1, Len2 ) = ( len(WordIndicesAndContextsList), len(TokenTranslationList) )
    if Len1 != Len2:
        lara_utils.print_and_flush(f'*** Error: different number of segment records in internalised corpus ({Len1}) and {TokenTranslationFile} ({Len2})')
        return False
    SegmentPairs = zip(WordIndicesAndContextsList, TokenTranslationList)
    return sum([ word_and_index_record_and_token_translation_record_to_translation_pairs(WICRecord, TokenTranslationRecord) for
                 (WICRecord, TokenTranslationRecord) in SegmentPairs ],
               [])

def nonempty_token_translation_record(Record):
    return isinstance(Record, list) and len(Record) == 3 and isinstance(Record[0], list) and len(Record[0]) > 0

def word_and_index_record_and_token_translation_record_to_translation_pairs(WICRecord, TokenTranslationRecord):
    Triples = [ word_indices_and_context_to_translation_record(WICItem, TokenTranslationRecord)
                for WICItem in WICRecord ]
    return [ Triple for Triple in Triples if Triple != False ]

def word_indices_and_context_to_translation_record(WICItem, TokenTranslationRecord):
    ( Word, Indices, Lemma, IsMWE, Context ) = WICItem
    TranslationComponents = [ TokenTranslationRecord[1][Index].strip() if Index < len(TokenTranslationRecord[1]) else False
                              for Index in Indices ]
    if not False in TranslationComponents:
        return ( clean_word_for_mwe_record(Word),
                 word_and_indices_translation_components_to_translation(TranslationComponents),
                 Context,
                 Lemma,
                 IsMWE )
    else:
        return False

# There are two possible ways to add token translations to an MWE:
# - translate each component the same, in which case we return that translation
# - translate components separately, in which case we concatenate them
def word_and_indices_translation_components_to_translation(TranslationComponents):
    if False in TranslationComponents:
        return False
    elif identical_values(TranslationComponents):
        return TranslationComponents[0]
    else:
        return ' '.join(TranslationComponents)

def identical_values(TranslationComponents):
    return len(lara_utils.remove_duplicates(TranslationComponents)) == 1

def split_list_to_words_indices_and_contexts(SplitList, Params):
    WIList0 = sum([ page_to_words_indices_and_contexts(Page, Params) for Page in SplitList ], [])
    return [ List for List in WIList0 if len(List) > 0 ]

def page_to_words_indices_and_contexts(Page, Params):
    ( PageInfo, Segments ) = Page
    return [ segment_to_words_indices_and_contexts(Segment, Params) for Segment in Segments ]

def segment_to_words_indices_and_contexts(Segment, Params):
    ( Raw, Clean, Pairs0, Tag ) = Segment
    Pairs = [ Pair for Pair in Pairs0 if Pair[1] != '' ]
    WordAndIndices = pairs_to_words_and_indices(Pairs, Params)
    return [ WordsAndIndicesPair + [ Clean ] for WordsAndIndicesPair in WordAndIndices ]

def pairs_to_words_and_indices(Pairs, Params):
    PairsWithMarkers = [ [ Pair, 'not_used' ] for Pair in Pairs ]
    WordsAndIndices = []
    N = len(PairsWithMarkers)
    for I in range(0, N):
        ( Surface, Lemma) = Pairs[I]
        if Lemma != '' and PairsWithMarkers[I][1] != 'used':
            ( RealLemma, MWELength ) = strip_off_mwe_part_tag_returning_lemma_and_length(Lemma)
            if MWELength == 1:
                # This is for old tagged files which mark MWEs using the deprecated @ ... @ notation
                IsMWE = True if ' ' in RealLemma else False
                WordsAndIndices += [ [ Surface, [ I ], RealLemma, IsMWE ] ]
            else:
                ( OtherSurfaceWords, OtherIndices ) = find_rest_of_mwe_in_pairs(PairsWithMarkers, Pairs, Lemma, I + 1, N, MWELength-1)
                SurfaceMWE = ' '.join( [ Surface ] + OtherSurfaceWords )
                Indices = [ I ] + OtherIndices
                WordsAndIndices += [ [ SurfaceMWE, Indices, RealLemma, True ] ]
    return WordsAndIndices

def find_rest_of_mwe_in_pairs(PairsWithMarkers, Pairs, MWELemma, I, N, NumberLeft):
    if NumberLeft <= 0:
        return ( [], [] )
    elif I >= N:
        lara_utils.print_and_flush(f'*** Warning: unable to find all of MWE "{MWELemma}" in {Pairs}')
        return ( [], [] )
    else:
        ( Pair, Marker ) = PairsWithMarkers[I]
        ( Surface, Lemma ) = Pair
        if Marker == 'used' or MWELemma != Lemma:
            return find_rest_of_mwe_in_pairs(PairsWithMarkers, Pairs, MWELemma, I+1, N, NumberLeft)
        else:
            PairsWithMarkers[I][1] = 'used'
            SurfaceClean = clean_word_for_mwe_record(Surface)
            ( RestSurface, RestI ) =  find_rest_of_mwe_in_pairs(PairsWithMarkers, Pairs, MWELemma, I+1, N, NumberLeft-1)
            return ( [ SurfaceClean ] + RestSurface, [ I ] + RestI )
        
# ---------------------------------------------

def update_mwes_from_text_file(ConfigFile):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if Params == False:
        return
    JSONFileIn = lara_top.lara_tmp_file('tmp_mwe_annotations', Params)
    HTMLFile = lara_top.lara_tmp_file('tmp_mwe_annotations_summary', Params)
    TextFile = lara_utils.change_extension(HTMLFile, 'txt')
    JSONFileOut = Params.mwe_annotations_file
    N = 1000000
    update_mwe_json_file_from_mwe_text_file(JSONFileIn, TextFile, JSONFileOut, N)

def update_mwe_json_file_from_mwe_text_file(JSONFileIn, TextFile, JSONFileOut, N):
    JSONDataIn0 = lara_utils.read_json_file(JSONFileIn)
    if JSONDataIn0 == False:
        return
    lara_utils.print_and_flush(f'--- Read JSON MWE file ({len(JSONDataIn0)} records), {JSONFileIn}')
    JSONDataIn = JSONDataIn0[:N]
    TextData0 = lara_utils.read_lara_text_file(TextFile)
    if TextData0 == False:
        return
    TextData1 = TextData0.split('\n')
    lara_utils.print_and_flush(f'--- Read text MWE file ({len(TextData1)} records), {TextFile}')
    TextData = TextData1[:N]
    TextDataParsed = [ parse_mwe_annotated_text_line(Line) for Line in TextData ]
    JSONTextPairs = zip(JSONDataIn, TextDataParsed)
    JSONDataOut = [ update_json_data_from_parsed_text_data(JSONItem, ParsedTextItem)
                    for (JSONItem, ParsedTextItem) in JSONTextPairs ]
    lara_utils.write_json_to_file(JSONDataOut, JSONFileOut)

def parse_mwe_annotated_text_line(Line):
    #return parse_mwe_annotated_text_line_old_format(Line)
    return parse_mwe_annotated_text_line_new_format(Line)

# Old format
# Longtemps, je me suis couché de bonne heure. [de bonne heure] GOOD

##_convert_mwe_judgements = { 'GOOD': 'mwe_okay', 'BAD': 'mwe_not_okay', 'UNDEFINED': 'mwe_status_unknown' }
##
##def parse_mwe_annotated_text_line_old_format(Line):
##    Components = re.split('\[|\]', Line)
##    if len(Components) != 3:
##        return False
##    ( Text, MWE, Judgement0 ) = Components
##    Judgement1 = Judgement0.strip()
##    Judgement = _convert_mwe_judgements[Judgement1] if Judgement1 in _convert_mwe_judgements else 'mwe_status_unknown'
##    return { 'text': Text, 'mwe': MWE, 'ok': Judgement }

# mwe_ok | de bonne heure | Longtemps, je me suis couché de bonne heure.

_valid_mwe_judgements = [ 'mwe_okay', 'mwe_not_okay', 'mwe_status_unknown' ]

def parse_mwe_annotated_text_line_new_format(Line):
    Components = Line.split(' | ')
    if len(Components) != 3:
        return False
    ( Judgement0, MWE, Text ) = Components
    if Judgement0 in _valid_mwe_judgements:
        Judgement = Judgement0
    else:
        lara_utils.print_and_flush(f'*** Warning: unknown MWE status "{Judgement0}" in "{Line}" discarded. Must be in {_valid_mwe_judgements}')
        Judgement = 'mwe_status_unknown'
    return { 'text': Text, 'mwe': MWE, 'ok': Judgement }

def update_json_data_from_parsed_text_data(JSONItem, ParsedTextItem):
    JSONItem1 = copy.copy(JSONItem)
    if ParsedTextItem == False:
        return JSONItem
    ( Text, MWE, OK ) = ( ParsedTextItem['text'], ParsedTextItem['mwe'], ParsedTextItem['ok'] )
    if JSONItem['mwe'] != MWE:
        lara_utils.print_and_flush(f"*** Warning: MWE in JSON is {JSONItem['mwe']}, MWE in annotated text is {MWE}")
    JSONItem1['ok'] = OK
    return JSONItem1


                                   
                                   
        
            
                   
                   
