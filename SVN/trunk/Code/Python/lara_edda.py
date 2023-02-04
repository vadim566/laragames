
import lara_transform_tagged_file
import lara_audio
import lara_parse_utils
import lara_top
import lara_config
import lara_old_norse
import lara_utils
import xml.etree.ElementTree as ET
import copy

##       import lara_edda
##    lara_edda = importlib.reload(lara_edda)
##    poems = lara_edda.get_poems()
##    first_poem = poems[0]
##    verses = lara_edda.get_verses_from_poem(first_poem)
##    first_verse = verses[0]
##    print(lara_edda.get_lara_form_from_verse(first_verse))

#edda_xml_file = '$LARA/Content/edda/corpus/Codex Regius 2019-03-28.xml'
edda_xml_file = '$LARA/Content/edda/corpus/Codex Regius 2019-03-28_v2.xml'
edda_xml_tree = None
#edda_corpus_file = '$LARA/Content/edda/corpus/edda_converted.txt'
edda_corpus_file = '$LARA/Content/edda/corpus/edda_converted2.txt'
edda_config_file = '$LARA/Content/edda/corpus/local_config.json'
edda_word_lemma_file = '$LARA/Content/oldnorse/corpus/edda_words2lemmas.json'

def convert_edda():
    poems = get_poems()
    converted_text = '\n\n'.join([get_lara_form_from_poem(poem) for poem in poems ])
    lara_utils.write_lara_text_file(converted_text, edda_corpus_file)

def make_edda_word_lemma_file():
    Params = lara_config.read_lara_local_config_file(edda_config_file)
    lara_top.compile_lara_local_clean(Params)
    SplitFile = lara_top.lara_tmp_file('split', Params)
    WordLemmaDict = split_file_to_word_lemma_dict(SplitFile)
    lara_utils.write_json_to_file(WordLemmaDict, edda_word_lemma_file)

def get_poems():
    body = get_body()
    return [ child for child in body if child.tag == '{http://www.tei-c.org/ns/1.0}div' ]

def read_xml_file():
    global edda_xml_file
    global edda_xml_tree
    edda_xml_tree = ET.parse(lara_utils.absolute_file_name(edda_xml_file))
    lara_utils.print_and_flush(f'--- Read and internalised {edda_xml_file}')

def get_body():
    read_xml_file()
    root = edda_xml_tree.getroot()
    text = root[1]
    body = text[0]
    return body

def get_lara_form_from_poem(poem):
    title = get_title_from_poem(poem)
    verses = get_verses_from_poem(poem)
    verses_text = '\n\n'.join([ get_lara_form_from_verse(verse) for verse in verses ])
    return f'<h1>{title}||</h1>\n{verses_text}'

def get_title_from_poem(poem):
    if '{http://www.w3.org/XML/1998/namespace}id' in poem.attrib:
        return poem.attrib['{http://www.w3.org/XML/1998/namespace}id']
    else:
        return '??'

def get_verses_from_poem(poem):
    top_level_verses = [ verse for verse in poem
                         if verse.tag == '{http://www.tei-c.org/ns/1.0}lg' ]
    subpoem_verses = [ verse for subpoem in poem
                       if subpoem.tag == '{http://www.tei-c.org/ns/1.0}div'
                       for verse in subpoem
                       if verse.tag == '{http://www.tei-c.org/ns/1.0}lg' ]
    return top_level_verses + subpoem_verses

def get_lara_form_from_verse(verse):
    title = get_title_from_verse(verse)
    body_lines = get_lines_from_verse(verse)
    title_lines = [ f'/*{title}*/' ] if title else []
    return '\n'.join(title_lines + body_lines) + '||'

def get_title_from_verse(verse):
    if '{http://www.w3.org/XML/1998/namespace}id' in verse.attrib:
        return verse.attrib['{http://www.w3.org/XML/1998/namespace}id']
    else:
        return ''

def get_lines_from_verse(verse):
    return [ get_words_from_line(line) for line in verse if line.tag == '{http://www.tei-c.org/ns/1.0}l' ]

# Handle segs as well
def get_words_from_line(line):
    out = ''
    for component in line:
        lara_component = get_lara_form_from_line_component(component)
        if lara_component:
            ( word_or_punct, lara_text ) = lara_component
            if not lara_text:
                True
            elif out == '':
                out = lara_text
            elif word_or_punct in ( 'word', 'seg', 'unclear_seg' ):
                out += f' {lara_text}'
            else:
                out += lara_text
    return out

def get_lara_form_from_line_component(component):
    if component.tag == '{http://www.tei-c.org/ns/1.0}seg':
        return ( 'seg', get_words_from_line(component) )
    if component.tag == '{http://www.tei-c.org/ns/1.0}unclear':
        return ( 'unclear_seg', get_words_from_line(component) )
    elif component.tag == '{http://www.tei-c.org/ns/1.0}w':
        surface = get_surface_form_from_word(component)
        lemma = get_lemma_from_word(component)
        if not surface:
            return False
        if not lemma or surface == lemma and surface.islower():
            return ( 'word', surface )
        else:
            return ( 'word', f'{surface}#{lemma}#' )
    elif component.tag == '{http://www.menota.org/ns/1.0}punct':
        return ( 'punct', get_surface_form_from_word(component) )
    else:
        return False

def get_lemma_from_word(word):
    if 'lemma' in word.attrib:
        return word.attrib['lemma']
    else:
        return False

def get_surface_form_from_word(word):
    choices = get_choices_from_word(word)
    if choices:
        for choice in choices:
            if choice.tag == '{http://www.menota.org/ns/1.0}norm' and len(choice) > 0 and choice[0].text:
                return choice[0].text
            elif choice.tag == '{http://www.menota.org/ns/1.0}norm' and choice.text:
                return choice.text
    return False

def get_choices_from_word(word):
    for component in word:
        if component.tag == '{http://www.tei-c.org/ns/1.0}choice':
            return component
    return False

# ------------------------------------

# The following is superseded by the code in lara_parallel_text.py

def add_audio_tracking_to_voluspa_branislav():
    SplitFile = '$LARA/tmp_resources/völuspá_2column_split.json'
    AudioDir = '$LARA/Content/völuspá/audio/branislav'
    OutFile = '$LARA/Content/völuspá/corpus/völuspá_audio_tracking_branislav.txt'
    AudioTrackingSpreadsheet = '$LARA/Content/völuspá/corpus/völuspá_audio_tracking_branislav.csv'
    add_audio_tracking_to_2column_edda_file(SplitFile, AudioDir, OutFile, AudioTrackingSpreadsheet)

def add_audio_tracking_to_voluspa_imba():
    SplitFile = '$LARA/tmp_resources/völuspá_2column_split.json'
    AudioDir = '$LARA/Content/völuspá/audio/imba'
    OutFile = '$LARA/Content/völuspá/corpus/völuspá_audio_tracking_imba.txt'
    AudioTrackingSpreadsheet = '$LARA/Content/völuspá/corpus/völuspá_audio_tracking_imba.csv'
    add_audio_tracking_to_2column_edda_file(SplitFile, AudioDir, OutFile, AudioTrackingSpreadsheet)

def add_audio_tracking_to_2column_edda_file(SplitFile, AudioDir, OutFile, AudioTrackingSpreadsheet):
    lara_audio.read_and_store_ldt_metadata_files([ AudioDir ], 'segments')
    SplitFileContents = lara_utils.read_json_file(SplitFile)
    ( SplitFileContents1, AudioTrackingData, AudioCounter ) = ( [], [], 1 )
    for ( PageInfo, Segments ) in SplitFileContents:
        ( Segments1, AudioTrackingDataNext, AudioCounterNext ) = add_audio_tracking_to_segments(Segments, AudioCounter)
        SplitFileContents1 += [ [ PageInfo, Segments1 ] ]
        AudioTrackingData += AudioTrackingDataNext
        AudioCounter = AudioCounterNext
    lara_transform_tagged_file.split_file_content_to_text_file(SplitFileContents1, OutFile)
    lara_utils.write_lara_csv(AudioTrackingData, AudioTrackingSpreadsheet)

def add_audio_tracking_to_segments(Segments, AudioCounter):
    ( Segments1, AudioTrackingData ) = ( [], [] )
    for Segment in Segments:
        ( Segment1, AudioTrackingNext, AudioCounterNext ) = add_audio_tracking_to_segment(Segment, AudioCounter)
        Segments1 += [ Segment1 ]
        AudioTrackingData += AudioTrackingNext
        AudioCounter = AudioCounterNext
    return ( Segments1, AudioTrackingData, AudioCounter )

##   <tr><td><audio id="audio_1" src="423772_191222_150857678.mp3"/><br/></td><td>/**/</td></tr>
##   <tr><td>/*v.Vsp.1*/</td><td>/**/</td></tr>
##   <tr><td class="audio_1_line">Hljóðs#hljóð# bið#biðja# ek allar#allr#</td><td>/*Hliods bið ec allar*/</td></tr>
##   <tr><td class="audio_1_line">kindir#kind#,</td><td>/*kindir*/</td></tr>
##   <tr><td class="audio_1_line">meiri ok minni</td><td>/*meiri oc miNi*/</td></tr>
##   <tr><td class="audio_1_line">mögu#mögr# Heimdalar#Heimdallr#;</td><td>/*mavgo ¦ heimdallar*/</td></tr>
##   <tr><td class="audio_1_line">vild#vilja# u#þú# að#at# ek, Valföðr#Valföðr#,</td><td>/*vilðo at ec ualfa/þr*/</td></tr>
##   <tr><td class="audio_1_line">vel fram telja</td><td>/*uel fyr telia*/</td></tr>
##   <tr><td class="audio_1_line">forn spjöll#spjall# fira#firar#,</td><td>/*forn ¦ spioll fíra*/</td></tr>
##   <tr><td class="audio_1_line">þau#sá# er fremst#framr# um man#muna#.||</td><td>/*þa/ er fremst um man.*/</td></tr>   <tr><td></td><td>/**/</td></tr>
##   <tr><td></td><td>/**/</td></tr>
  
def add_audio_tracking_to_segment(Segment, AudioCounter):
    ( Raw, Clean, Pairs, Tag) = Segment
    RawLines = Raw.split('\n')
    # If we have no LARA content, we can't put in any embedded audio
    # If there are three or fewer line, it's probably a title or something similar rather than a verse
    if Clean == '' or len(RawLines) < 4:
        return (Segment, [], AudioCounter)
    ( AudioId, AudioClass ) = ( f'audio_{AudioCounter}', f'audio_{AudioCounter}_line' )
    AudioFile0 = get_audio_file_for_segment(Clean)
    AudioFile = 'MISSING_AUDIO_FILE' if not AudioFile0 else AudioFile0
    AudioControlLine = audio_control_line(AudioFile, AudioCounter)
    LinesWithAudioControl = insert_audio_control(RawLines, AudioControlLine)
    if not LinesWithAudioControl:
        return (Segment, [], AudioCounter)
    AnnotatedLines = insert_audio_class_markings(LinesWithAudioControl, AudioClass)
    AnnotatedRaw = '\n'.join(AnnotatedLines)
    Segment1 = ( AnnotatedRaw, Clean, Pairs, Tag)
    AudioTrackingLine = [ AudioId, Clean, '' ]
    return ( Segment1, [ AudioTrackingLine ], AudioCounter + 1 )

def get_audio_file_for_segment(Clean):
    File = lara_audio.ldt_file_for_segment(Clean)
    if not File:
        return False
    Components = File.split('/')
    return Components[-1]

def audio_control_line(AudioFile, AudioCounter):
    return f'   <tr><td><audio id="audio_{AudioCounter}" src="{AudioFile}"/><br/></td><td>/**/</td></tr>'

def insert_audio_control(RawLines, AudioControlLine):
    TitleLine = first_line_that_looks_like_title(RawLines)
    FirstContentLine = first_line_that_looks_like_normal_content(RawLines)
    LineToPutAudioControlBefore = TitleLine if TitleLine else FirstContentLine
    if not LineToPutAudioControlBefore or not LineToPutAudioControlBefore in RawLines:
        return False
    Index = RawLines.index(LineToPutAudioControlBefore)
    return RawLines[:Index] + [ AudioControlLine ] + RawLines[Index:]

def first_line_that_looks_like_title(RawLines):
    for Line in RawLines:
        if looks_like_title(Line):
            return Line
    return False

##   <tr><td>/*v.Vsp.1*/</td><td>/**/</td></tr>
def looks_like_title(Line):
    return is_comment(first_td_field_in_tr_line(Line))

def first_line_that_looks_like_normal_content(RawLines):
    for Line in RawLines:
        if looks_like_normal_content(Line):
            return Line
    return False

## Normally a complete <tr> tag
##   <tr><td>Hljóðs#hljóð# bið#biðja# ek allar#allr#</td><td>/*Hliods bið ec allar*/</td></tr>
##
## but can be incomplete in the case of the last line of a verse
##   <tr><td>\u00feau#s\u00e1# er fremst#framr# um man#muna#.
                      
def looks_like_normal_content(Line):
    return is_normal_text(first_td_field_in_tr_line(Line))

def first_td_field_in_tr_line(Line):
    StartTrIndex = Line.find('<tr>')
    if StartTrIndex < 0:
        return False
    EndTrIndex = StartTrIndex + len('<tr>')
    StartTdIndex = Line.find('<td>', EndTrIndex)
    if StartTdIndex < 0:
        return False
    EndTdIndex = StartTdIndex + len('<td>')
    StartCloseTdIndex = Line.find('</td>', EndTdIndex)
    EndTdFieldIndex = StartCloseTdIndex if StartCloseTdIndex > -1 else len(Line)
    return Line[EndTdIndex:EndTdFieldIndex]

def is_comment(Text):
    if not Text:
        return False
    Text1 = Text.strip()
    return Text1.startswith('/*') and Text1.endswith('*/')
    
def is_normal_text(Text):
    if Text == False or is_comment(Text):
        return False
    return len(lara_parse_utils.remove_top_level_tags_and_comments(Text)[0].strip()) > 0

def insert_audio_class_markings(Lines, AudioClass):
    return [ insert_audio_class_marking_in_line(Line, AudioClass) for Line in Lines ]

##   <tr><td class="audio_1_line">Hljóðs#hljóð# bið#biðja# ek allar#allr#</td><td>/*Hliods bið ec allar*/</td></tr>
def insert_audio_class_marking_in_line(Line, AudioClass):
    if not looks_like_normal_content(Line) or line_with_audio_control(Line):
        return Line
    StartTrIndex = Line.find('<tr>')
    EndTrIndex = StartTrIndex + len('<tr>')
    StartTdIndex = Line.find('<td', EndTrIndex)
    EndTdIndex = StartTdIndex + len('<td')
    return Line[:EndTdIndex] + f' class="{AudioClass}"' + Line[EndTdIndex:]

def line_with_audio_control(Line):
    return Line.find('<audio') > 0

# ------------------------------------------

def split_file_to_word_lemma_dict(File):
    Content = lara_utils.read_json_file(File)
    Dict = {}
    for ( PageInfo, Chunks ) in Content:
        for ( Raw, Clean, Pairs, Tag ) in Chunks:
            for ( Surface, Lemma ) in Pairs:
                if Lemma != '':
                    List = Dict[Surface] if Surface in Dict else []
                    if not Lemma in List:
                        List += [ Lemma ]
                        Dict[Surface] = List
    return Dict
    
# ------------------------------------------

def transfer_audio_tracking_data_völuspá():
    OldFile = '$LARA/Content/völuspá_is/corpus/völuspá_kenningar_no_audio_tracking.txt'
    AudioTrackingFile = '$LARA/Content/völuspá/corpus/völuspá_audio_tracking_with_timings_imba.txt'
    NewFile = '$LARA/Content/völuspá_is/corpus/völuspá_kenningar.txt'
    transfer_audio_tracking_data(OldFile, AudioTrackingFile, NewFile)

##Transform
##
##   <tr><td><audio id="audio_völuspá_kenningar_1" src="this segment"/><br/></td><td>/**/</td></tr>
##   <tr><td>/*v.Vsp.1*/</td><td>/**/</td></tr>
##   <tr><td class="audio_völuspá_kenningar_1_line">Hljóðs#hljóð# bið#biðja# ek</td><td>#ek#/*Hliods bið ec*/</td></tr>
##
##into
##
##   <tr><td><audio tracking="yes" src="this segment"/><br/></td><td>/**/</td></tr>
##   <tr><td>/*v.Vsp.1*/</td><td>/**/</td></tr>
##   <tr><td end_time="2.3">Hljóðs#hljóð# bið#biðja# ek</td><td>/*Hliods bið ec*/</td></tr>

def transfer_audio_tracking_data(OldFile, AudioTrackingFile, NewFile):
    OldLines = lara_utils.read_lara_text_file(OldFile).split('\n')
    AudioLines = lara_utils.read_lara_text_file(AudioTrackingFile).split('\n')
    NAudioTrackingLines = len([ Line for Line in AudioLines if Line.find('end_time=') >= 0 ])
    NOldAudioLines = len([ Line for Line in OldLines if Line.find('class="audio') >= 0 ])
    if NOldAudioLines != NAudioTrackingLines:
        lara_utils.print_and_flush(f'*** Error: {NOldAudioLines} audio lines in {OldFile}')
        lara_utils.print_and_flush(f'*** Error: {NAudioTrackingLines} audio lines in {AudioTrackingFile}')
        return False
    TrackingTimes = [ extract_tracking_time(Line) for Line in AudioLines if Line.find('end_time=') >= 0 ]
    NewLines = transfer_audio_tracking_data1(OldLines, TrackingTimes)
    if NewLines != False:
        lara_utils.write_lara_text_file('\n'.join(NewLines), NewFile)

def extract_tracking_time(Line):
    StartEndTimeIndex = Line.find('end_time="')
    if StartEndTimeIndex < 0:
        return False
    StartIndex = Line.find('"', StartEndTimeIndex) + 1
    EndIndex = Line.find('"', StartIndex)
    return Line[StartIndex:EndIndex]

def transfer_audio_tracking_data1(OldLines, TrackingTimes):
    Index = 0
    NewLines = []
    for Line in OldLines:
        if Line.find('<audio id="') >= 0:
            StartIndex = Line.find('id="')
            EndIndex = Line.find('"', StartIndex + len('id="') + 1)
            if StartIndex < 0 or EndIndex < 0:
                lara_utils.print_and_flush(f'*** Error: bad line {Line}')
            NewLine = Line[:StartIndex] + 'tracking="yes"' + Line[EndIndex + 1:]
        elif Line.find('class="audio') >= 0:
            StartIndex = Line.find('class="')
            EndIndex = Line.find('"', StartIndex + len('class="') + 1)
            if StartIndex < 0 or EndIndex < 0:
                lara_utils.print_and_flush(f'*** Error: bad line {Line}')
            NewLine = Line[:StartIndex] + 'end_time="' + TrackingTimes[Index] + '"' + Line[EndIndex + 1:]
            Index += 1
        else:
            NewLine = Line
        NewLines += [ NewLine ]
    return NewLines

# ------------------------------------

_edda_split_file = '$LARA/tmp_resources/edda_split.json'
_edda_old_norse_lexicon_spreadsheet = '$LARA/tmp_resources/edda_old_norse_lexicon_spreadsheet.csv'

def create_edda_old_norse_lexicon_spreadsheet():
    Content = lara_utils.read_json_file(_edda_split_file)
    Dict = {}
    for ( PageInfo, Chunks ) in Content:
        for ( Raw, Clean, Pairs, Tag ) in Chunks:
            for ( Surface, Lemma ) in Pairs:
                if Lemma != '':
                    POS = lara_old_norse.old_norse_lemma_to_pos(Lemma)
                    POS1 = '' if POS == 'None' else POS
                    if not Lemma in Dict:
                        Dict[Lemma] = { 'word': Surface, 'context': Clean, 'pos': POS1 }
    write_dict_to_old_norse_lexicon_speadsheet(Dict)

def write_dict_to_old_norse_lexicon_speadsheet(Dict):
    Lines = [ [ Lemma, Dict[Lemma]['pos'], Dict[Lemma]['word'], Dict[Lemma]['context'] ]
              for Lemma in Dict ]
    SortedLines = sorted(Lines, key=lambda x: x[0])
    NLemmasWithPOS = len([ Line for Line in SortedLines if Line[1] != '' ])
    NLemmasWithoutPOS = len([ Line for Line in SortedLines if Line[1] == '' ])
    lara_utils.write_lara_csv(SortedLines, _edda_old_norse_lexicon_spreadsheet)
    lara_utils.print_and_flush(f'--- Written out lexicon spreadsheet: {NLemmasWithPOS} entries with POS, {NLemmasWithoutPOS} without')

# ------------------------------------

def create_numbered_hávamál_metadata():
    create_numbered_metadata_file('$LARA/Content/hávamál2/audio/Birgitta/metadata_help.json',
                                  '$LARA/Content/hávamál2/audio/Birgitta/metadata_help_numbered.json')
    create_numbered_metadata_file('$LARA/Content/hávamál3/audio/Birgitta/metadata_help.json',
                                  '$LARA/Content/hávamál3/audio/Birgitta/metadata_help_numbered.json')

def create_numbered_metadata_file(File, File1):
    Metadata = lara_utils.read_json_file(File)
    lara_utils.print_and_flush(f'--- Read metadata file ({len(Metadata)} records)')
    Metadata1 = []
    for I in range( 0, len(Metadata) ):
        Item = Metadata[I]
        Item['index'] = I
        Metadata1 += [ Item ]
    lara_utils.write_json_to_file(Metadata1, File1)
    lara_utils.print_and_flush(f'--- Written numbered metadata file ({len(Metadata1)} records)')
    
def create_unnumbered_metadata_file(File, File1):
    Metadata = lara_utils.read_json_file(File)
    lara_utils.print_and_flush(f'--- Read metadata file ({len(Metadata)} records)')
    Metadata1 = []
    for I in range( 0, len(Metadata) ):
        Item = Metadata[I]
        del Item['index']
        Metadata1 += [ Item ]
    lara_utils.write_json_to_file(Metadata1, File1)
    lara_utils.print_and_flush(f'--- Written numbered metadata file ({len(Metadata1)} records')
    
# ------------------------------------

## "Abel": [
##         {
##             "def": "Abel",
##             "pos": "noun m.",
##             "url": "https://skaldic.abdn.ac.uk/m.php?p=lemma&i=1809"
##         }
##
## Agnarr | noun m. | Agnarr Agnarr er einn skal ráða, Geirröðar sonr, Gotna landi.																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																												
        

def add_new_onp_entries():
    onp_index_file = '$LARA/Content/oldnorse/corpus/onp_index.json'
    extended_onp_index_file = '$LARA/Content/oldnorse/corpus/onp_index_extended.json'
    new_onp_spreadsheet = '$LARA/Content/oldnorse/corpus/edda_old_norse_lexicon_spreadsheet_brynjarr.csv'
    ONPData = lara_utils.read_json_file(onp_index_file)
    lara_utils.print_and_flush(f'--- Read old ONP data, {len(ONPData.keys())} items, from {onp_index_file}')
    NewONPData = lara_utils.read_lara_csv(new_onp_spreadsheet)
    for Line in NewONPData:
        if len(Line) >= 2:
            ( Lemma, POS ) = Line[:2]
            if not Lemma in ONPData:
                ONPData[Lemma] = [ { 'pos': POS } ]
    lara_utils.write_json_to_file(ONPData, extended_onp_index_file)
    lara_utils.print_and_flush(f'--- Written new ONP data, {len(ONPData.keys())} items, to {extended_onp_index_file}')

# ------------------------------------

_master_configs_for_sticking_together = { 'english': '$LARA/Content/edda_combined3/corpus/local_config.json',
                                          'icelandic': '$LARA/Content/edda_combined3/corpus/local_config_is.json' }

##    Völuspá
##    Hávamál
##    Vafþrúðnismál
##    Grímnismál
##    Skírnismál 
##    Hárbarðslióð
##    Hýmiskviða
##    Lokasenna
##    Þrymskviða
##    Alvíssmál

_list_of_subprojects_dirs = [ '$LARA/Content/völuspá',
                              '$LARA/Content/hávamál5',
                              '$LARA/Content/Vafþrúðnismál_English',
                              '$LARA/Content/Grímnismál_English',
                              '$LARA/Content/Skírnismál2',
                              '$LARA/Content/Hárbarðsljóð_English',
                              '$LARA/Content/Hymiskviða_English',
                              '$LARA/Content/Lokasenna_English_v2',
                              '$LARA/Content/Þrymskviða_English',
                              '$LARA/Content/alvíssmál_en' ]

##   For each directory
##   - create IS config file
##   - resources on IS config file
##   - word_pages on IS config file
  
##   Create IS version of combined file
##   
##   Combine IS versions using adapted version of EN combination code
##   Name of config file: add "_isl" to EN name.
##       
##   "id": add "_is"
##   "segment_translation_mouseover": set to "no"
##   "segment_translation_spreadsheet": change "english.csv" to "icelandic.csv"
##   "translation_spreadsheet_surface": change "english.csv" to "icelandic.csv"
##   "translation_spreadsheet_tokens": change "english.csv" to "icelandic.csv"

def create_all_icelandic_config_files():
    for Dir in _list_of_subprojects_dirs: 
        create_icelandic_config_file(Dir)

def make_all_icelandic_resources():
    for Dir in _list_of_subprojects_dirs:
        perform_resources_step_for_dir(Dir, 'icelandic')

def make_all_icelandic_word_pages():
    for Dir in _list_of_subprojects_dirs:
        perform_word_pages_step_for_dir(Dir, 'icelandic')

# - Stick together subprojects into single HTML
def stick_together_subprojects(Language):
    import lara_abstract_html
    MasterConfigFile = _master_configs_for_sticking_together[Language]
    ComponentDirs = _list_of_subprojects_dirs
    ComponentConfigFiles = [ config_file_for_dir(Dir, Language) for Dir in ComponentDirs ]
    lara_abstract_html.abstract_html_to_html_multiple(MasterConfigFile, ComponentConfigFiles)

def create_icelandic_config_file(Dir):
    ConfigFileEN = config_file_for_dir(Dir, 'english')
    ConfigFileIS = config_file_for_dir(Dir, 'icelandic')
    ContentEN = lara_utils.read_json_file(ConfigFileEN)
    ContentIS = copy.copy(ContentEN)
    ContentIS['id'] = ContentEN['id'] + '_is'
    ContentIS['segment_translation_mouseover'] = 'no'
    ContentIS['segment_translation_spreadsheet'] = ContentEN['segment_translation_spreadsheet'].replace('english.csv', 'icelandic.csv')
    ContentIS['translation_spreadsheet_surface'] = ContentEN['translation_spreadsheet_surface'].replace('english.csv', 'icelandic.csv')
    ContentIS['translation_spreadsheet_tokens'] = ContentEN['translation_spreadsheet_tokens'].replace('english.csv', 'icelandic.csv')
    lara_utils.write_json_to_file(ContentIS, ConfigFileIS)
    lara_utils.print_and_flush(f'--- Written Iceland config file for {Dir}')

def perform_resources_step_for_dir(Dir, Language):
    ConfigFile = config_file_for_dir(Dir, Language)
    lara_top.compile_lara_local_resources(ConfigFile)

def perform_word_pages_step_for_dir(Dir, Language):
    ConfigFile = config_file_for_dir(Dir, Language)
    lara_top.compile_lara_local_word_pages(ConfigFile)
                             
def config_file_for_dir(Dir, Language):
    if Language == 'english':
        return f'{Dir}/corpus/local_config.json'
    elif Language == 'icelandic':
        return f'{Dir}/corpus/local_config_is.json'
    else:
        lara_utils.print_and_flush(f'*** Error: unknown language "{Language}"')
        return False
    
