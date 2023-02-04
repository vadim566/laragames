
import lara_top
import lara_audio
import lara_transform_tagged_file
import lara_config
import lara_parse_utils
import lara_utils

def test_lara_parallel_text(Id):
    if Id == 'völuspa1':
        ConfigFile = '$LARA/Content/völuspá/corpus/local_config.json'
        CSVFile = '$LARA/Content/völuspá/corpus/völuspá_parallel_text.csv'
        make_parallel_text_spreadsheet(ConfigFile, CSVFile)
    elif Id == 'völuspa2':
        ConfigFile = '$LARA/Content/völuspá/corpus/local_config.json'
        CSVFile = '$LARA/Content/völuspá/corpus/völuspá_parallel_text_filled.csv'
        TextFileOut = '$LARA/Content/völuspá/corpus/völuspá_2column.txt'
        insert_parallel_text_in_file(ConfigFile, CSVFile, TextFileOut)
    elif Id == 'hávamál1':
        ConfigFile = '$LARA/Content/hávamál_is/corpus/local_config.json'
        CSVFile = '$LARA/Content/hávamál_is/corpus/hávamál_parallel_text.csv'
        make_parallel_text_spreadsheet(ConfigFile, CSVFile)
    elif Id == 'hávamál2':
        ConfigFile = '$LARA/Content/hávamál_is/corpus/local_config.json'
        CSVFile = '$LARA/Content/hávamál/corpus/hávamál_parallel_instantiated.csv'
        TextFileOut = '$LARA/Content/hávamál_is/corpus/hávamál_audio_controls.txt'
        insert_parallel_text_and_audio_tracking_in_edda_file(ConfigFile, CSVFile, TextFileOut)
    elif Id == 'lokasenna1':
        ConfigFile = '$LARA/Content/Lokasenna_English/corpus/local_config.json'
        CSVFile = '$LARA/Content/Lokasenna_English/corpus/lokasenna_parallel_text.csv'
        make_parallel_text_spreadsheet(ConfigFile, CSVFile)
    elif Id == 'lokasenna2':
        ConfigFile = '$LARA/Content/Lokasenna_English/corpus/local_config.json'
        CSVFile = '$LARA/Content/Lokasenna_English/corpus/lokasenna_parallel_text_instantiated.csv'
        TextFileOut = '$LARA/Content/Lokasenna_English/corpus/Lokasenna_two_column.txt'
        insert_parallel_text_and_audio_tracking_in_edda_file(ConfigFile, CSVFile, TextFileOut)
    elif Id == 'allvísmál1':
        ConfigFile = '$LARA/Content/alvíssmál_en/corpus/local_config.json'
        CSVFile = '$LARA/Content/alvíssmál_en/corpus/alvíssmál_parallel_text.csv'
        make_parallel_text_spreadsheet(ConfigFile, CSVFile)
    elif Id == 'allvísmál2':
        ConfigFile = '$LARA/Content/alvíssmál_en/corpus/local_config.json'
        CSVFile = '$LARA/Content/alvíssmál_en/corpus/alvíssmál_parallel_text_instantiated.csv'
        TextFileOut = '$LARA/Content/alvíssmál_en/corpus/alvíssmál_two_column.txt'
        insert_parallel_text_and_audio_tracking_in_edda_file(ConfigFile, CSVFile, TextFileOut)
    elif Id == 'Þrymskviða1':
        ConfigFile = '$LARA/Content/Þrymskviða_English/corpus/local_config.json'
        CSVFile = '$LARA/Content/Þrymskviða_English/corpus/Þrymskviða_parallel_text.csv'
        make_parallel_text_spreadsheet(ConfigFile, CSVFile)
    elif Id == 'Þrymskviða2':
        ConfigFile = '$LARA/Content/Þrymskviða_English/corpus/local_config.json'
        CSVFile = '$LARA/Content/Þrymskviða_English/corpus/Þrymskviða_parallel_text_instantiated.csv'
        TextFileOut = '$LARA/Content/Þrymskviða_English/corpus/Þrymskviða_two_column.txt'
        insert_parallel_text_and_audio_tracking_in_edda_file(ConfigFile, CSVFile, TextFileOut)
    elif Id == 'Skírnismál1':
        ConfigFile = '$LARA/Content/Skírnismál2/corpus/local_config.json'
        CSVFile = '$LARA/Content/Skírnismál2/corpus/Skírnismál_parallel_text.csv'
        make_parallel_text_spreadsheet(ConfigFile, CSVFile)
    elif Id == 'Skírnismál2':
        ConfigFile = '$LARA/Content/Skírnismál2/corpus/local_config.json'
        CSVFile = '$LARA/Content/Skírnismál2/corpus/Skírnismál_parallel_text_instantiated.csv'
        TextFileOut = '$LARA/Content/Skírnismál2/corpus/Skírnismál_two_column.txt'
        insert_parallel_text_and_audio_tracking_in_edda_file(ConfigFile, CSVFile, TextFileOut)
    elif Id == 'Vafþrúðnismál1':
        ConfigFile = '$LARA/Content/Vafþrúðnismál_English/corpus/local_config.json'
        CSVFile = '$LARA/Content/Vafþrúðnismál_English/corpus/Vafþrúðnismál_parallel_text.csv'
        make_parallel_text_spreadsheet(ConfigFile, CSVFile)
    elif Id == 'Vafþrúðnismál2':
        ConfigFile = '$LARA/Content/Vafþrúðnismál_English/corpus/local_config.json'
        CSVFile = '$LARA/Content/Vafþrúðnismál_English/corpus/Vafþrúðnismál_parallel_text_instantiated.csv'
        TextFileOut = '$LARA/Content/Vafþrúðnismál_English/corpus/Vafþrúðnismál_two_column.txt'
        insert_parallel_text_and_audio_tracking_in_edda_file(ConfigFile, CSVFile, TextFileOut)
    elif Id == 'Hárbarðsljóð1':
        ConfigFile = '$LARA/Content/Hárbarðsljóð_English/corpus/local_config.json'
        CSVFile = '$LARA/Content/Hárbarðsljóð_English/corpus/Hárbarðsljóð_parallel_text.csv'
        make_parallel_text_spreadsheet(ConfigFile, CSVFile)
    elif Id == 'Hárbarðsljóð2':
        ConfigFile = '$LARA/Content/Hárbarðsljóð_English/corpus/local_config.json'
        CSVFile = '$LARA/Content/Hárbarðsljóð_English/corpus/Hárbarðsljóð_parallel_text_instantiated.csv'
        TextFileOut = '$LARA/Content/Hárbarðsljóð_English/corpus/Hárbarðsljóð_two_column.txt'
        insert_parallel_text_and_audio_tracking_in_edda_file(ConfigFile, CSVFile, TextFileOut)
    elif Id == 'Grímnismál1':
        ConfigFile = '$LARA/Content/Grímnismál_English/corpus/local_config.json'
        CSVFile = '$LARA/Content/Grímnismál_English/corpus/Grímnismál_parallel_text.csv'
        make_parallel_text_spreadsheet(ConfigFile, CSVFile)
    elif Id == 'Grímnismál2':
        ConfigFile = '$LARA/Content/Grímnismál_English/corpus/local_config.json'
        CSVFile = '$LARA/Content/Grímnismál_English/corpus/Grímnismál_parallel_text_instantiated.csv'
        TextFileOut = '$LARA/Content/Grímnismál_English/corpus/Grímnismál_two_column.txt'
        insert_parallel_text_and_audio_tracking_in_edda_file(ConfigFile, CSVFile, TextFileOut)
    elif Id == 'Hymiskviða1':
        ConfigFile = '$LARA/Content/Hymiskviða_English/corpus/local_config.json'
        CSVFile = '$LARA/Content/Hymiskviða_English/corpus/Hymiskviða_parallel_text.csv'
        make_parallel_text_spreadsheet(ConfigFile, CSVFile)
    elif Id == 'Hymiskviða2':
        ConfigFile = '$LARA/Content/Hymiskviða_English/corpus/local_config.json'
        CSVFile = '$LARA/Content/Hymiskviða_English/corpus/Hymiskviða_parallel_text_instantiated.csv'
        TextFileOut = '$LARA/Content/Hymiskviða_English/corpus/Hymiskviða_two_column.txt'
        insert_parallel_text_and_audio_tracking_in_edda_file(ConfigFile, CSVFile, TextFileOut)

# ----------------------------------

def make_parallel_text_spreadsheet(ConfigFile, CSVFile):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if not Params:
        return False
    SegmentAudioMetadata = get_segment_audio_metadata_dict(Params)
    lara_top.compile_lara_local_clean(Params)
    SplitFile = lara_top.lara_tmp_file('split', Params)
    Lines = get_lines_from_split_file(SplitFile, SegmentAudioMetadata)
    write_out_parallel_text_spreadsheet(Lines, CSVFile)

def get_segment_audio_metadata_dict(Params):
    SegmentAudioMetadata = lara_audio.read_ldt_metadata_file(Params.segment_audio_directory)
    return { Item['text']: Item['file'] for Item in SegmentAudioMetadata } if isinstance(SegmentAudioMetadata, list) else {}

def get_lines_from_split_file(SplitFile, SegmentAudioMetadata):
    InList = lara_utils.read_json_file(SplitFile)
    LinesLists = [ get_lines_from_page(Page, SegmentAudioMetadata) for Page in InList ]
    return [ Line for LinesList in LinesLists for Line in LinesList ]

def get_lines_from_page(Page, SegmentAudioMetadata):
    ( PageInfo, InSegments ) = Page
    LinesLists = [ get_lines_from_segment(Segment, SegmentAudioMetadata) for Segment in InSegments ]
    return [ Line for LinesList in LinesLists for Line in LinesList ]

_audio_file_line_tag = '*** Audio file ***'

def get_lines_from_segment(Segment, SegmentAudioMetadata):
    ( Raw, Clean, Words, Tag ) = Segment
    if Clean in SegmentAudioMetadata:
        AudioFile = SegmentAudioMetadata[Clean]
        FileLines = [ f'{_audio_file_line_tag} {AudioFile}' ]
    else:
        FileLines = [ ]
    return FileLines + [ clean_up_line(Line) for Line in Raw.split('\n') ]

def write_out_parallel_text_spreadsheet(Lines, CSVFile):
    FullLines = [ [ Line, '' ] for Line in Lines ]
    lara_utils.write_lara_csv(FullLines, CSVFile)

# ----------------------------------

def insert_parallel_text_in_file(ConfigFile, CSVFile, TextFileOut):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if not Params:
        return False
    lara_top.compile_lara_local_clean(Params)
    SplitFile = lara_top.lara_tmp_file('split', Params)
    ParallelText = read_parallel_text_csv(CSVFile)
    InList = lara_utils.read_json_file(SplitFile)
    OutList = insert_parallel_text_in_split_file_contents(InList, ParallelText)
    lara_transform_tagged_file.split_file_content_to_text_file_no_separators(OutList, TextFileOut)

def read_parallel_text_csv(CSVFile):
    Records = lara_utils.read_lara_csv(CSVFile)
    return [ [ clean_up_line(Record[0]), Record[1] ] for Record in Records
             if not _audio_file_line_tag in Record[0] ]

def insert_parallel_text_in_split_file_contents(InList, ParallelText):
    return [ insert_parallel_text_in_page(Page, ParallelText) for Page in InList ]

def insert_parallel_text_in_page(Page, ParallelText):
    ( PageInfo, InSegments ) = Page
    OutSegments = [ insert_parallel_text_in_segment(Segment, ParallelText) for Segment in InSegments ]
    add_parallel_text_intro_and_coda(OutSegments)
    return ( PageInfo, OutSegments )

def insert_parallel_text_in_segment(Segment, ParallelText):
    ( Raw, Clean, Words, Tag ) = Segment
    ( LinesIn, LinesOut ) = ( Raw.split('\n'), [] )
    N = len(LinesIn)
    for I in range(0, N):
        Line = LinesIn[I]
        ( Parallel1, Parallel2 ) = ParallelText.pop(0) if len(ParallelText) > 0 else ( '', '' )
        CleanLine = clean_up_line(Line)
        if Parallel1 != clean_up_line(Line):
            lara_utils.print_and_flush(f'*** Error in line {Line}. Clean version should be {Parallel1}, is {CleanLine}')
            return False
        IsLastLine = True if I == N - 1 else False
        LinesOut += [ make_two_column_line(Line, Parallel2, IsLastLine) ]
    RawOut = '\n'.join(LinesOut)
    return [ RawOut, Clean, Words, Tag ]

def make_two_column_line(Column1, Column2, IsLastLine):
    SegmentBreak = '||' if IsLastLine else ''
    return f'   <tr><td>{Column1}{SegmentBreak}</td><td>/*{Column2}*/</td></tr>'

def add_parallel_text_intro_and_coda(Segments):
    insert_parallel_text_intro(Segments[0])
    insert_parallel_text_coda(Segments[-1])

def insert_parallel_text_intro(Segment):
    Raw = Segment[0]
    Segment[0] = f'<table>\n{Raw}'

def insert_parallel_text_coda(Segment):
    Raw = Segment[0]
    Segment[0] = f'{Raw}\n</table>'

def write_out_parallel_text_spreadsheet(Lines, CSVFile):
    FullLines = [ [ Line, '' ] for Line in Lines ]
    lara_utils.write_lara_csv(FullLines, CSVFile)

# ----------------------------------

def insert_parallel_text_and_audio_tracking_in_edda_file(ConfigFile, CSVFile, TextFileOut):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if not Params:
        return False
    lara_top.compile_lara_local_clean(Params)
    SplitFile = lara_top.lara_tmp_file('split', Params)
    ParallelText = read_parallel_text_csv(CSVFile)
    InList = lara_utils.read_json_file(SplitFile)
    OutList = insert_parallel_text_and_audio_tracking_in_edda_split_file_contents(InList, ParallelText)
    lara_transform_tagged_file.split_file_content_to_text_file_no_separators(OutList, TextFileOut)

def read_parallel_text_csv(CSVFile):
    Records = lara_utils.read_lara_csv(CSVFile)
    return [ [ clean_up_line(Record[0]) ] + Record[1:] for Record in Records
             if not _audio_file_line_tag in Record[0]]

def insert_parallel_text_and_audio_tracking_in_edda_split_file_contents(InList, ParallelText):
    return [ insert_parallel_text_and_audio_tracking_in_edda_page(Page, ParallelText) for Page in InList ]

def insert_parallel_text_and_audio_tracking_in_edda_page(Page, ParallelText):
    ( PageInfo, InSegments ) = Page
    OutSegments = [ insert_parallel_text_and_audio_tracking_in_edda_segment(Segment, ParallelText) for Segment in InSegments ]
    add_parallel_text_intro_and_coda(OutSegments)
    return ( PageInfo, OutSegments )

# We want the result to look like this:
#
#   <tr><td><audio tracking="yes" src="this segment"/><br/></td><td>/**/</td></tr>
#   <tr><td>/*v.Vsp.2*/</td><td>/**/</td></tr>
#   <tr><td end_time="">Ek#ek# man#muna# jötna#jötunn#</td><td>/*Ec man iotna ¦*/</td></tr>
#   <tr><td end_time="">ár um borna#bera#,</td><td>/*ár um borna*/</td></tr>
#   <tr><td end_time="">þá#sá# er forðum mik#ek#</td><td>/*þa er fordom mic */</td></tr>
#   <tr><td end_time="">fædda#fæða# höfðu#hafa#;</td><td>/*fǫdda hofdo*/</td></tr>
#   <tr><td end_time="">níu man#muna# ek heima#heimr#,</td><td>/*nio man æc heima ¦*/</td></tr>
#   <tr><td end_time="">níu íviðjur#íviðja#,</td><td>/*nío iviþi*/</td></tr>
#   <tr><td end_time="">mjötvið#mjötviðr# mæran#mærr#</td><td>/*miot uið mǫraN*/</td></tr>
#   <tr><td end_time="">fyr mold neðan.||</td><td>/*fyr mold nedan.*/</td></tr>   <tr><td></td><td>/**/</td></tr>
#   <tr><td></td><td>/**/</td></tr>

_two_column_audio_control_line = '   <tr><td><audio tracking="yes" src="this segment"/><br/></td><td>/**/</td></tr>'

def insert_parallel_text_and_audio_tracking_in_edda_segment(Segment, ParallelText):
    ( Raw, Clean, Words, Tag ) = Segment
    ( LinesIn, LinesOut ) = ( Raw.split('\n'), [] )
    #lara_utils.print_and_flush(f'LinesIn = {LinesIn}')
    N = len(LinesIn)
    for I in range(0, N):
        Line = LinesIn[I]
        if is_edda_verse_title_line(Line) == True:
            LinesOut += [ _two_column_audio_control_line ]
        ParallelTextLine = ParallelText.pop(0) if len(ParallelText) > 0 else ( '', '', '' )
        if len(ParallelTextLine) >= 3:
            ( Parallel1, Parallel2, EndTime ) = ParallelTextLine[:3]
        elif len(ParallelTextLine) == 2:
            ( Parallel1, Parallel2, EndTime ) = ( ParallelTextLine[0], ParallelTextLine[1], '' )
        elif len(ParallelTextLine) == 1:
            ( Parallel1, Parallel2, EndTime ) = ( ParallelTextLine[0], '', '' )
        CleanLine = clean_up_line(Line)
        if Parallel1 != clean_up_line(Line):
            lara_utils.print_and_flush(f'*** Error in line {Line}. Clean version should be {Parallel1}, is {CleanLine}')
            return False
        IsLastLine = True if I == N - 1 else False
        LinesOut += [ make_two_column_line(Line, Parallel2, EndTime, IsLastLine) ]
    RawOut = '\n'.join(LinesOut)
    return [ RawOut, Clean, Words, Tag ]

# /*v.Vsp.2*/
def is_edda_verse_title_line(Line):
    StartOfCommentMarker = Line.find('/*')
    if StartOfCommentMarker < 0:
        return False
    EndOfComment = Line.find('*/', StartOfCommentMarker + len('/*'))
    if EndOfComment < 0:
        return False
    Comment = Line[StartOfCommentMarker + len('/*'):EndOfComment]
    return is_edda_verse_title_content(Comment)

def is_edda_verse_title_content(Comment):
    CommentComponents = Comment.split('.')
    return True if len(CommentComponents) >= 2 and all_digits(CommentComponents[-1]) else False

def all_digits(Str):
    if Str == '':
        return False
    for Char in Str:
        if not Char.isdigit():
            return False
    return True

def make_two_column_line(Column1, Column2, EndTime, IsLastLine):
    SegmentBreak = '||' if IsLastLine else ''
    EndTime = EndTime.replace(',', '.')
    Column2 = Column2.replace(' ', ' ')
    OpeningTDTag = f'<td end_time="{EndTime}">' if is_verse_line(Column1) else '<td>'
    return f'   <tr>{OpeningTDTag}{Column1}{SegmentBreak}</td><td>/*{Column2}*/</td></tr>'

def is_verse_line(Line):
    return not Line == '' and not Line.isspace() and not is_edda_verse_title_line(Line)

def add_parallel_text_intro_and_coda(Segments):
    insert_parallel_text_intro(Segments[0])
    insert_parallel_text_coda(Segments[-1])

def insert_parallel_text_intro(Segment):
    Raw = Segment[0]
    Segment[0] = f'<table>\n{Raw}'

def insert_parallel_text_coda(Segment):
    Raw = Segment[0]
    Segment[0] = f'{Raw}\n</table>'

def write_out_parallel_text_spreadsheet(Lines, CSVFile):
    FullLines = [ [ Line, '' ] for Line in Lines ]
    lara_utils.write_lara_csv(FullLines, CSVFile)

# ----------------------------------

def clean_up_line(Line):
    return lara_parse_utils.remove_hashtag_comment_and_html_annotations1(Line, 'keep_comments')[0]

