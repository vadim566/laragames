
#import lara
import lara_top
import lara_html
import lara_mwe
import lara_translations
import lara_audio
import lara_extra_info
import lara_play_all
import lara_picturebook
import lara_split_and_clean
import lara_config
import lara_replace_chars
import lara_parse_utils
import lara_utils
import re
import copy

# ----------------------------------------------------------------

# Testing
def test_abstract_html_to_html(Id):
    if Id == 'mary':
        AbstractHTMLFile = '$LARA/tmp_resources/mary_had_a_little_lamb_abstract_html.json'
        ConfigFile = '$LARA/Content/mary_had_a_little_lamb/corpus/local_config_abstract_html.json'
        abstract_html_to_html(ConfigFile, AbstractHTMLFile)
    elif Id == 'peter_rabbit':
        AbstractHTMLFile = '$LARA/tmp_resources/peter_rabbit_abstract_html.json'
        ConfigFile = '$LARA/Content/peter_rabbit/corpus/local_config_abstract_html.json'
        abstract_html_to_html(ConfigFile, AbstractHTMLFile)
    elif Id == 'kejseren':
        AbstractHTMLFile = '$LARA/tmp_resources/kejserens_nye_klæder_abstract_html.json'
        ConfigFile = '$LARA/Content/kejserens_nye_klæder/corpus/local_config_abstract_html.json'
        abstract_html_to_html(ConfigFile, AbstractHTMLFile)
    elif Id == 'völuspá':
        AbstractHTMLFile = '$LARA/tmp_resources/völuspá_abstract_html.json'
        ConfigFile = '$LARA/Content/völuspá/corpus/local_config_abstract_html.json'
        abstract_html_to_html(ConfigFile, AbstractHTMLFile)
    elif Id == 'mary_peter':
        MasterConfigFile = '$LARA/Content/mary_peter/corpus/local_config.json'
        ComponentConfigFiles = [ '$LARA/Content/mary_had_a_little_lamb/corpus/local_config.json',
                                 '$LARA/Content/peter_rabbit/corpus/local_config.json'
                                 ]
        abstract_html_to_html_multiple(MasterConfigFile, ComponentConfigFiles)
    elif Id == 'edda3':
        MasterConfigFile = '$LARA/Content/edda_combined3/corpus/local_config.json'
        ComponentConfigFiles = [ '$LARA/Content/völuspá/corpus/local_config.json',
                                 '$LARA/Content/hávamál5/corpus/local_config.json',
                                 '$LARA/Content/Lokasenna_English_v2/corpus/local_config.json'
                                 ]
        abstract_html_to_html_multiple(MasterConfigFile, ComponentConfigFiles)
    elif Id == 'japanese_little_prince_zipfile':
        ConfigFile = '$LARA/Content/japanese_little_prince/corpus/local_config.json'
        Format = 'json'
        Zipfile = '$LARA/Content/japanese_little_prince/corpus/abstract_html_and_multimedia.jzipson'
        abstract_html_to_html_zipfile(ConfigFile, Format, Zipfile)
    else:
        lara_utils.print_and_flush(f'*** Error: unknown Id {Id}')
        return False
    
# ----------------------------------------------------------------

# Top level calls
# Convert contents of abstract HTML file into concrete HTML, putting results in directory defined by config file.
# If the value of AbstractHTMLFile is 'from_config', use the default file specified by the config file.

def abstract_html_to_html(ConfigFile, AbstractHTMLFile):
    return abstract_html_to_html_main(ConfigFile, [ ConfigFile ], AbstractHTMLFile)

def abstract_html_to_html_multiple(MasterConfigFile, ComponentConfigFiles):
    Params = lara_config.read_lara_local_config_file(MasterConfigFile)
    AbstractHTMLFile = abstract_html_file_specified_by_config(Params)
    combine_abstract_html_files_specified_by_configs(ComponentConfigFiles, AbstractHTMLFile)
    abstract_html_to_html_main(MasterConfigFile, ComponentConfigFiles, AbstractHTMLFile)

def abstract_html_to_html_main(ConfigFile, ComponentConfigFiles, AbstractHTMLFile):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    AbstractHTML = read_abstract_html_file(AbstractHTMLFile, Params)
    if AbstractHTML == False:
        lara_utils.print_and_flush(f'*** Error: unable to read abstract HTML from {AbstractHTMLFile}')
        return False
    ComponentParamsOkay = add_component_config_params_to_params(ComponentConfigFiles, Params)
    if ComponentParamsOkay == False:
        return False
    set_word_pages_dir(Params, 'default')
    copy_multimedia(AbstractHTML, Params)
    internalise_pos_colours_if_necessary(Params)
    replace_this_segment_and_this_page_references(AbstractHTML, Params)
    LemmaFreqDict = make_lemma_freq_dict(AbstractHTML)
    NotesDict = make_notes_dict(AbstractHTML)
    PageRepresentations = AbstractHTML['pages']
    AllPageNames = [ ( PageRepresentation['corpus_name'], PageRepresentation['page_name'] ) for PageRepresentation in PageRepresentations ]
    make_top_level_html_file(AllPageNames, Params)
    make_auxiliary_files(AbstractHTML, NotesDict, Params)
    make_main_text_pages(AbstractHTML, LemmaFreqDict, NotesDict, AllPageNames, Params)
    make_concordance_pages(AbstractHTML, LemmaFreqDict, NotesDict, Params)
    make_play_all_files(AbstractHTML, Params)
    lara_utils.print_and_flush(f'--- Created HTML files')
    return True

def add_component_config_params_to_params(ComponentConfigFiles, Params):
    ComponentParamsDict = {}
    for ComponentConfigFile in ComponentConfigFiles:
        ComponentParams = lara_config.read_lara_local_config_file(ComponentConfigFile)
        if ComponentParams == False:
            lara_utils.print_and_flush(f'*** Error: unable to read config file {ComponentConfigFile}')
            return False
        ComponentParamsDict[ComponentParams.id] = ComponentParams
    Params.component_params = ComponentParamsDict

# Create a zipfile containing an abstract HTML file in the format determined by Format (either 'pickle' or 'json')
# and a folder containing all the multimedia files needed.
def abstract_html_to_html_zipfile(ConfigFile, Format, Zipfile):
    if not Format in ( 'pickle', 'json' ):
        lara_utils.print_and_flush(f'*** Error: abstract HTML format "{Format}" needs to be "pickle" or "json"')
        return False
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    add_component_config_params_to_params([ConfigFile], Params)
    AbstractHTML = read_abstract_html_file('from_config', Params)
    if AbstractHTML == False:
        lara_utils.print_and_flush(f'*** Error: unable to read abstract HTML from {AbstractHTMLFile}')
        return False
    Dir = lara_utils.get_tmp_directory(Params)
    set_word_pages_dir(Params, Dir)
    copy_multimedia(AbstractHTML, Params)
    if Format == 'pickle':
        AbstractHTMLFile1 = f'{Dir}/abstract_html.data.gz'
        lara_utils.save_data_to_pickled_gzipped_file(AbstractHTML, AbstractHTMLFile1)
    else:
        AbstractHTMLFile1 = f'{Dir}/abstract_html.json'
        lara_utils.write_json_to_file_plain_utf8(AbstractHTML, AbstractHTMLFile1)
    lara_utils.make_zipfile(Dir, Zipfile)
    lara_utils.print_and_flush(f'--- Created zipfile with abstract HTML in {Format} format and multimedia: {Zipfile}')
    return True

# ----------------------------------------------------------------

# Combining abstract HTML:

def combine_abstract_html_files_specified_by_configs(ComponentConfigFiles, AbstractHTMLFile):
    AbstractHTMLList = [ read_abstract_html_file_specified_by_config(ConfigFile) for ConfigFile in ComponentConfigFiles ]
    if False in AbstractHTMLList:
        return
    AbstractHTML = combine_abstract_html(AbstractHTMLList)
    Extension = lara_utils.extension_for_file(AbstractHTMLFile)
    if Extension == 'gz':
        lara_utils.save_data_to_pickled_gzipped_file(AbstractHTML, AbstractHTMLFile)
    else:
        lara_utils.write_json_to_file_plain_utf8(AbstractHTML, AbstractHTMLFile)

def read_abstract_html_file_specified_by_config(ConfigFile):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if Params == False:
        return False
    File = abstract_html_file_specified_by_config(Params)
    return read_abstract_html_file(File, Params) if File != False else False

def combine_abstract_html(AbstractHTMLList):
    return { "segments": combine_abstract_html_segments(AbstractHTMLList),
             "pages": combine_abstract_html_pages(AbstractHTMLList),
             "word_pages": combine_abstract_html_word_pages(AbstractHTMLList),
             "alphabetical_index": combine_abstract_html_alphabetical_index(AbstractHTMLList),
             "frequency_index": combine_abstract_html_frequency_index(AbstractHTMLList),
             "notes": combine_abstract_html_notes(AbstractHTMLList),
             "image_lexicon": combine_abstract_html_image_lexicon(AbstractHTMLList),
             "toc": combine_abstract_html_toc(AbstractHTMLList),
             "css": combine_abstract_html_css(AbstractHTMLList),
             "custom_css": combine_abstract_html_custom_css(AbstractHTMLList),
             "script": combine_abstract_html_script(AbstractHTMLList),
             "custom_script": combine_abstract_html_custom_script(AbstractHTMLList),
             "audio_tracking_data": combine_abstract_html_audio_tracking_data(AbstractHTMLList)
             }

# segments: merge dicts
def combine_abstract_html_segments(AbstractHTMLList):
    Dict = {}
    for AbstractHTML in AbstractHTMLList:
        if 'segments' in AbstractHTML:
            Dict = lara_utils.merge_dicts(Dict, AbstractHTML['segments'])
    return Dict

# pages: concatenate lists 
def combine_abstract_html_pages(AbstractHTMLList):
    return lara_utils.concatenate_lists([ AbstractHTML['pages']
                                          for AbstractHTML in AbstractHTMLList if 'pages' in AbstractHTML ])

# word_pages: concatenate examples, extra_info, images in each page
def combine_abstract_html_word_pages(AbstractHTMLList):
    Dict = {}
    for AbstractHTML in AbstractHTMLList:
        if 'word_pages' in AbstractHTML:
            WordPages = AbstractHTML['word_pages']
            for Key in WordPages:
                NewWordPage = WordPages[Key]
                if not Key in Dict:
                    Dict[Key] = NewWordPage
                else:
                    OldWordPage = Dict[Key]
                    if 'examples' in OldWordPage and 'examples' in NewWordPage:
                        OldWordPage['examples'] += NewWordPage['examples']
                    elif 'examples' in NewWordPage:
                        OldWordPage['examples'] = NewWordPage['examples']
                        
                    if 'extra_info' in OldWordPage and 'extra_info' in NewWordPage:    
                        OldWordPage['extra_info'] += NewWordPage['extra_info']
                    elif 'extra_info' in NewWordPage:    
                        OldWordPage['extra_info'] = NewWordPage['extra_info']
                        
                    if 'images' in OldWordPage and 'images' in NewWordPage:  
                        OldWordPage['images'] += NewWordPage['images'] 
                    elif 'images' in NewWordPage:  
                        OldWordPage['images'] = NewWordPage['images'] 
    for Key in Dict:
        WordPage = Dict[Key]
        if 'extra_info' in WordPage and isinstance(WordPage['extra_info'], list) and len(WordPage['extra_info']) != 0:
            WordPage['extra_info'] = lara_utils.remove_duplicates_general(WordPage['extra_info'])
    return Dict


##        {
##            "count": 3,
##            "word": [
##                {
##                    "lemma": "a",
##                    "word": "a"
##                }
##            ]
##        },
# alphabetical_index: combine and sum counts
def combine_abstract_html_alphabetical_index(AbstractHTMLList):
    Dict = {}
    for AbstractHTML in AbstractHTMLList:
        if 'alphabetical_index' in AbstractHTML:
            AlphabeticalIndex = AbstractHTML['alphabetical_index']
            for Item in AlphabeticalIndex:
                Count = Item['count']
                Lemma = Item['word'][0]['lemma']
                Word = Item['word'][0]['word']
                NewCount = Count if not Lemma in Dict else Dict[Lemma]['count'] + Count
                Dict[Lemma] = { 'word': Word, 'count': NewCount }
    AlphabeticalIndex1 = [ { 'count': Dict[Lemma]['count'], 'word':[{ 'lemma': Lemma, 'word': Dict[Lemma]['word'] }] } for Lemma in Dict ]
    return sorted(AlphabeticalIndex1, key=lambda x: x['word'][0]['lemma'])

##{
##            "count": 4,
##            "cumulative_percentage": "7.02%",
##            "word": [
##                {
##                    "lemma": "lamb",
##                    "word": "lamb"
##                }
##            ]
##        },
# frequency_index: combine, sum counts, and recalculate cumulative percentage
def combine_abstract_html_frequency_index(AbstractHTMLList):
    Dict = {}
    for AbstractHTML in AbstractHTMLList:
        if 'frequency_index' in AbstractHTML:
            FrequencyIndex = AbstractHTML['frequency_index']
            for Item in FrequencyIndex:
                Count = Item['count']
                Lemma = Item['word'][0]['lemma']
                Word = Item['word'][0]['word']
                NewCount = Count if not Lemma in Dict else Dict[Lemma]['count'] + Count
                Dict[Lemma] = { 'word': Word, 'count': NewCount }
    FrequencyIndex1 = [ { 'count': Dict[Lemma]['count'], 'word':[{ 'lemma': Lemma, 'word': Dict[Lemma]['word'] }] } for Lemma in Dict ]
    FrequencyIndex2 = sorted(FrequencyIndex1, key=lambda x: x['count'], reverse=True)
    Total = sum ([ Item['count'] for Item in FrequencyIndex2])
    CumulativeTotal = 0
    for Item in FrequencyIndex2:
        CumulativeTotal += Item['count']
        Item['cumulative_percentage'] = '{0:.2f}%'.format( 100.0 * CumulativeTotal / Total )
    return FrequencyIndex2

##{
##    "note": "Possibly the Virgin Mary.",
##    "word": [
##        {
##            "lemma": "mary",
##            "word": "mary"
##        }
##    ]
##}
# notes: concatenate notes
def combine_abstract_html_notes(AbstractHTMLList):
    Dict = {}
    for AbstractHTML in AbstractHTMLList:
        if 'notes' in AbstractHTML and isinstance(AbstractHTML['notes'], list):
            Notes = AbstractHTML['notes']
            for Item in Notes:
                Note = Item['note']
                Lemma = Item['word'][0]['lemma']
                Word = Item['word'][0]['word']
                NewNote = Note if not Lemma in Dict else Dict[Lemma]['note'] + '\n' + Note
                Dict[Lemma] = { 'word': Word, 'note': NewNote }
    Notes1 = [ { 'note': Dict[Lemma]['note'], 'word':[{ 'lemma': Lemma, 'word': Dict[Lemma]['word'] }] } for Lemma in Dict ]
    return sorted(Notes1, key=lambda x: x['word'][0]['lemma'])

##        {
##            "images": [
##                {
##                    "corpus_name": "Mary_had_a_little_lamb",
##                    "file": "lamb.jpg"
##                }
##            ],
##            "lemma": "lamb"
##        },
# image_lexicon: concatenate images
def combine_abstract_html_image_lexicon(AbstractHTMLList):
    Dict = {}
    for AbstractHTML in AbstractHTMLList:
        if 'image_lexicon' in AbstractHTML and isinstance(AbstractHTML['image_lexicon'], list):
            ImageItems = AbstractHTML['image_lexicon']
            for Item in ImageItems:
                Images = Item['images']
                Lemma = Item['lemma']
                NewImages = Images if not Lemma in Dict else Dict[Lemma] + Images
                Dict[Lemma] = NewImages 
    return [ { 'images': Dict[Lemma], 'lemma': Lemma } for Lemma in Dict ]

##{
##       "anchor": "Mary_had_a_little_lamb_page_1_segment_1",
##       "corpus_name": "Mary_had_a_little_lamb",
##       "page_name": 1,
##       "plain_text": " Mary Had a Little Lamb ",
##       "tag": "h1"
##   },
# toc: concatenate lists
def combine_abstract_html_toc(AbstractHTMLList):
    return lara_utils.concatenate_lists([ AbstractHTML['toc']
                                          for AbstractHTML in AbstractHTMLList if 'toc' in AbstractHTML ])

# css: use first example
def combine_abstract_html_css(AbstractHTMLList):
    for AbstractHTML in AbstractHTMLList:
        if 'css' in AbstractHTML and is_non_null_list(AbstractHTML['css']):
            return AbstractHTML['css']
    return []

def is_non_null_list(X):
    return isinstance(X, ( list, tuple )) and len(X) != 0

# custom_css: use first non-trivial example, if any
def combine_abstract_html_custom_css(AbstractHTMLList):
    for AbstractHTML in AbstractHTMLList:
        if 'custom_css' in AbstractHTML and is_non_null_list(AbstractHTML['custom_css']):
            return AbstractHTML['custom_css']
    return []

# script: use first example
def combine_abstract_html_script(AbstractHTMLList):
    for AbstractHTML in AbstractHTMLList:
        if 'script' in AbstractHTML and is_non_null_list(AbstractHTML['script']):
            return AbstractHTML['script']
    return []

# custom_script: use first non-trivial example, if any
def combine_abstract_html_custom_script(AbstractHTMLList):
    for AbstractHTML in AbstractHTMLList:
        if 'custom_script' in AbstractHTML and is_non_null_list(AbstractHTML['custom_script']):
            return AbstractHTML['custom_script']
    return []

# audio_tracking_data: concatenate lists
def combine_abstract_html_audio_tracking_data(AbstractHTMLList):
    return lara_utils.concatenate_lists([ AbstractHTML['audio_tracking_data']
                                          for AbstractHTML in AbstractHTMLList
                                          if 'audio_tracking_data' in AbstractHTML and isinstance(AbstractHTML['audio_tracking_data'], list) ])

# ----------------------------------------------------------------

# Read the abstract representation. We support two possible formats: JSON (mostly for testing) and pickled gzipped (efficient)
def read_abstract_html_file(File, Params):
    if File == 'from_config':
        File1 = abstract_html_file_specified_by_config(Params)
        return read_abstract_html_file(File1, Params) if File1 != False else False
    lara_utils.print_and_flush(f'--- Reading abstract HTML from {File}')
    Extension = lara_utils.extension_for_file(File).lower()
    if Extension == 'json':
        return lara_utils.read_json_file(File)
    elif Extension == 'gz':
        return lara_utils.get_data_from_pickled_gzipped_file(File)
    else:
        lara_utils.print_and_flush(f'*** Error: unable to read abstract HTML file {File}, extension must be json or gz.')
        return False

def abstract_html_file_specified_by_config(Params):
    Format = Params.abstract_html_format
    return lara_top.lara_tmp_file('abstract_html_json_file', Params) if Format == 'json_only' else lara_top.lara_tmp_file('abstract_html_file', Params)
    
# ----------------------------------------------------------------

# Create the directories where we're going to put the results
def set_word_pages_dir(Params, WordPagesDir0):
    if WordPagesDir0 == 'default':
        #WordPagesDir = lara_top.lara_compiled_dir('word_pages_from_abstract_html_directory', Params)
        WordPagesDir = lara_top.lara_compiled_dir('word_pages_directory', Params)
    else:
        WordPagesDir = WordPagesDir0
    lara_utils.create_directory_deleting_old_if_necessary(WordPagesDir)
    Params.word_pages_directory = WordPagesDir
    lara_utils.create_directory_deleting_old_if_necessary(f'{Params.word_pages_directory}/multimedia')

# Copy the multimedia files we're using to the target multimedia direct
def copy_multimedia(AbstractHTML, Params):
    ( WordAudioDict, SegmentAudioDict, ImagesDict ) = find_multimedia_to_copy(AbstractHTML)
    copy_word_audio(WordAudioDict, Params)
    copy_segment_audio(SegmentAudioDict, Params)
    copy_images(ImagesDict, Params)

def find_multimedia_to_copy(AbstractHTML):
    SegmentDict = AbstractHTML['segments']
    ImageLexicon = AbstractHTML['image_lexicon']
    ( WordAudioDict, SegmentAudioDict, ImagesDict ) = ( {}, {}, {} )
    for Key in SegmentDict:
        find_multimedia_to_copy_in_segment(SegmentDict[Key], WordAudioDict, SegmentAudioDict, ImagesDict)
    for Item in ImageLexicon:
        find_multimedia_to_copy_in_image_lexicon_item(Item, ImagesDict)
    return ( WordAudioDict, SegmentAudioDict, ImagesDict )

def find_multimedia_to_copy_in_segment(Segment, WordAudioDict, SegmentAudioDict, ImagesDict):
    if 'audio' in Segment:
        SegmentAudioDict[( Segment['audio']['corpus_name'], Segment['audio']['file'] )] = True
    for Item in Segment['words']:
        if 'audio' in Item:
            WordAudioDict[( Item['audio']['corpus_name'], Item['audio']['file'] )] = True
        if 'multimedia' in Item and Item['multimedia'] == 'audio':
            SegmentAudioDict[( Item['corpus_name'], Item['file'] )] = True
        if 'multimedia' in Item and Item['multimedia'] == 'img':
            ImagesDict[( Item['corpus_name'], Item['file'] )] = True

## {
##            
##            "images": [ { "corpus_name": "Mary_had_a_little_lamb",
##                          "file": "lamb.jpg" }
##            ],
##            "lemma": "lamb"
##        },
def find_multimedia_to_copy_in_image_lexicon_item(LemmaItem, ImagesDict):
    for ImageItem in LemmaItem['images']:
        ImagesDict[( ImageItem['corpus_name'], ImageItem['file'] )] = True

def copy_word_audio(WordAudioDict, Params):
    Files = WordAudioDict.keys()
    NFiles = len(Files)
    lara_utils.print_and_flush(f'--- {NFiles} word audio files to copy')
    if len(Files) == 0:
        return
    for ( CorpusName, File ) in Files:
        ComponentParams = Params.component_params[CorpusName]
        lara_utils.copy_file(f'{ComponentParams.word_audio_directory}/{File}', f'{Params.word_pages_directory}/multimedia/{File}')
    lara_utils.print_and_flush(f'--- files copied')

def copy_segment_audio(SegmentAudioDict, Params):
    Files = SegmentAudioDict.keys()
    NFiles = len(Files)
    lara_utils.print_and_flush(f'--- {NFiles} segment audio files to copy')
    if len(Files) == 0:
        return
    for ( CorpusName, File ) in Files:
        if not File in ( 'this segment', 'this page' ):
            ComponentParams = Params.component_params[CorpusName]
            lara_utils.copy_file(f'{ComponentParams.segment_audio_directory}/{File}', f'{Params.word_pages_directory}/multimedia/{File}')
    lara_utils.print_and_flush(f'--- files copied')

def copy_images(ImagesDict, Params):
    if Params.hide_images == 'yes':
        return
    Files = ImagesDict.keys()
    NFiles = len(Files)
    lara_utils.print_and_flush(f'--- {NFiles} image files to copy')
    if len(Files) == 0:
        return
    for ( CorpusName, File ) in Files:
        ComponentParams = Params.component_params[CorpusName]
        lara_utils.copy_file(f'{ComponentParams.image_directory}/{File}', f'{Params.word_pages_directory}/multimedia/{File}')
    lara_utils.print_and_flush(f'--- files copied')

# ----------------------------------------------------------------

# Replace the virtual audio files "this segment" and "this page" with real pathnames

def replace_this_segment_and_this_page_references(AbstractHTML, Params):
    PlayAllList = get_play_all_list(AbstractHTML)
    PageToPlayAllFileDict = { ( Item['corpus_name'], Item['page_name'] ): Item['file_name'] for Item in PlayAllList }
    Segments = AbstractHTML['segments']
    for Key in Segments:
        replace_this_segment_and_this_page_references_in_segment(Segments[Key], PageToPlayAllFileDict)

##"play_all": {
##                "file_name": "play_all_1.mp3",
##                "page_name": 1,
##                "segment_audio_files": [
##                    "958994_200913_125158576.mp3",
##                    "958995_200913_125218080.mp3",
##                    "958996_200913_125243220.mp3",
##                    (...)

def replace_this_segment_and_this_page_references_in_segment(Segment, PageToPlayAllFileDict):
    ThisSegmentAudio = Segment['audio']['file'] if 'audio' in Segment else False
    ThisCorpusName = Segment['corpus_name']
    ThisPage = Segment['page']
    ThisPageAudio = PageToPlayAllFileDict[( ThisCorpusName, ThisPage )] if ( ThisCorpusName, ThisPage ) in PageToPlayAllFileDict else False
    for Item in Segment['words']:
        replace_this_segment_and_this_page_references_in_words_item(Item, ThisSegmentAudio, ThisPageAudio)

def replace_this_segment_and_this_page_references_in_words_item(Item, ThisSegmentAudio, ThisPageAudio):
    if isinstance(Item, dict) and 'multimedia' in Item and Item['multimedia'] == 'audio' and Item['file'] in ( 'this segment', 'this page' ):
        Item['file'] = ThisSegmentAudio if Item['file'] == 'this segment' else ThisPageAudio

# ----------------------------------------------------------------

# 'this page' files refer to audio files created by concatenating all the audio file on the page, in order.
# Make them using the 'play_all' lists

def make_play_all_files(AbstractHTML, Params):
    PlayAllList = get_play_all_list(AbstractHTML)
    lara_play_all.create_play_all_audio_files_if_necessary(PlayAllList, Params)

def get_play_all_list(AbstractHTML):
    Pages = AbstractHTML['pages']
    return [ Page['play_all'] for Page in Pages if 'play_all' in Page ]

# ----------------------------------------------------------------

# Make the top-level file

def make_top_level_html_file(AllPageNames, Params):
    if Params.html_style == 'social_network':
        return False
    else:
        File = page_name_for_hyperlinked_text_file(Params)
        format_hyperlinked_text_file(File, AllPageNames, Params)
        return File

def format_hyperlinked_text_file(File, AllPageNames, Params):
    FirstMainFile = short_name_of_first_main_text_file(AllPageNames)
    HeaderLines = lara_html.hyperlinked_text_file_header(FirstMainFile, Params)
    ClosingLines = lara_html.hyperlinked_text_file_closing(Params)
    lara_utils.write_unicode_text_file('\n'.join(HeaderLines + ClosingLines), File)
    lara_utils.print_and_flush(f'--- Written top level HTML file {File}')

# ----------------------------------------------------------------

# Make the main text pages out of the 'pages' component.

def make_main_text_pages(AbstractHTML, LemmaFreqDict, NotesDict, AllPageNames, Params):
    PageRepresentations = AbstractHTML['pages']
    SegmentRepresentationDict = AbstractHTML['segments']
    for Page in PageRepresentations:
        make_main_text_page(Page, SegmentRepresentationDict, LemmaFreqDict, NotesDict, AllPageNames, Params)
    return True

##{
##            "custom_css_file": {
##                "content": [
##                    "",
##                    "h2 ",
##                    "{",
##                    "\tfont-family: sans-serif; font-size: 3em;",
##                    "}",
##                    "",
##                    "p {",
##                    "\tfont-family: sans-serif; font-size: 2em;",
##                    "}",
##                    "",
##                    "td {",
##                    "        font-family: sans-serif; font-size: 2em;",
##                    "",
##                    "}",
##                    "",
##                    ""
##                ],
##                "file_name": "alphabet_page.css"
##            },
##            "custom_script_file": null,
##            "page_name": 2,
##            "play_all": {
##                "file_name": "play_all_2.mp3",
##                "page_name": 2,
##                "segment_audio_files": false
##            },
##            "segments": [
##                "barngarla_alphabet_page_2_segment_1",
##                "barngarla_alphabet_page_2_segment_2",
##                "barngarla_alphabet_page_2_segment_3"
##            ]
##        },

def make_main_text_page(Page, SegmentRepresentationDict, LemmaFreqDict, NotesDict, AllPageNames, Params):
    CorpusId = Page['corpus_name']
    PageName = Page['page_name']
    SegmentNamesOrImages = Page['segments']
    CustomCSSFileInfo = Page['custom_css_file'] if 'custom_css_file' in Page else False
    CustomScriptFileInfo = Page['custom_script_file'] if 'custom_script_file' in Page else False
    if Params.picturebook == 'yes' and Params.picturebook_word_locations_file != '':
        Segments = make_picturebook_segments_for_page(PageName, SegmentNamesOrImages, SegmentRepresentationDict, Params)
    else:
        ( Segments, MapLines ) = ( [], [] )
        for SegmentNameOrImage in SegmentNamesOrImages:
            if lara_picturebook.is_annotated_image_representation(SegmentNameOrImage):
                ( Segment, Map ) = make_annotated_image(SegmentNameOrImage, SegmentRepresentationDict, Params)
                MapLines += [ Map ]
            else:
                Segment = make_segment(SegmentRepresentationDict[SegmentNameOrImage], LemmaFreqDict, NotesDict, 'main_text', Params)
            Segments += [ Segment ]
    make_main_text_page1(CorpusId, PageName, Segments, MapLines, LemmaFreqDict, NotesDict, AllPageNames, CustomCSSFileInfo, CustomScriptFileInfo, Params)

def make_main_text_page1(CorpusId, PageName, Segments, MapLines, LemmaFreqDict, NotesDict, AllPageNames, CustomCSSFileInfo, CustomScriptFileInfo, Params):
    CurrentFile = full_name_of_main_text_file(CorpusId, PageName, Params)
    PrecedingMainFile = short_name_of_preceding_main_text_file(CorpusId, PageName, AllPageNames)
    FollowingMainFile = short_name_of_following_main_text_file(CorpusId, PageName, AllPageNames)
    FirstMainFile = short_name_of_first_main_text_file(AllPageNames)
    ParamsForHeader = handle_custom_css_and_script_files_for_main_text_page(Params, CustomCSSFileInfo, CustomScriptFileInfo)
    CountFile = formatted_count_file_for_word_pages_short()
    AlphabeticalFile = formatted_alphabetical_file_for_word_pages_short(),
    HeaderLines = lara_html.main_text_file_header(PageName, PrecedingMainFile, FollowingMainFile, FirstMainFile,
                                                  CountFile, AlphabeticalFile, ParamsForHeader)
    AllSegments = ''.join(Segments)
    #lara_utils.print_and_flush(f'--- Segments: "{Segments}"')
    SegmentLines = AllSegments.split('\n')
    MainHTMLLines = hyperlinked_lines_to_html_lines(SegmentLines)
    ClosingLines = lara_html.main_text_file_closing(PrecedingMainFile, FollowingMainFile, Params)
    File = full_name_of_main_text_file(CorpusId, PageName, Params)
    lara_utils.write_unicode_text_file('\n'.join(HeaderLines + MainHTMLLines + MapLines + ClosingLines), File)
    lara_utils.print_and_flush(f'--- Written main text file {File}')

##            "custom_css_file": {
##                "content": [
##                    "",
##                    "h2 ",
##                    "{",
##                    "\tfont-family: sans-serif; font-size: 3em;",
##                    "}",
##                    "",
##                    "p {",
##                    "\tfont-family: sans-serif; font-size: 2em;",
##                    "}",
##                    "",
##                    "td {",
##                    "        font-family: sans-serif; font-size: 2em;",
##                    "",
##                    "}",
##                    "",
##                    ""
##                ],
##                "file_name": "alphabet_page.css"
##            },
##            "custom_script_file": null,
    
def handle_custom_css_and_script_files_for_main_text_page(Params, CustomCSSFileInfo, CustomScriptFileInfo):
    Params1 = copy.copy(Params)
    if isinstance(CustomCSSFileInfo, dict):
        if 'file_name' in CustomCSSFileInfo:
            Params1.css_file_for_page = CustomCSSFileInfo['file_name']
        if 'content' in CustomCSSFileInfo and isinstance(CustomCSSFileInfo['content'], list):
            Text = '\n'.join(CustomCSSFileInfo['content'])
            lara_utils.write_lara_text_file(Text, f'{Params.word_pages_directory}/{lara_html.css_file_for_page(Params1)}')
    if isinstance(CustomScriptFileInfo, dict):
        if 'file_name' in CustomScriptFileInfo:
            Params1.script_file_for_page = CustomScriptFileInfo['file_name']
        if 'content' in CustomScriptFileInfo and isinstance(CustomScriptFileInfo['content'], list):
            Text = '\n'.join(CustomScriptFileInfo['content'])
            lara_utils.write_lara_text_file(Text, f'{Params.word_pages_directory}/{lara_html.script_file_for_page(Params1)}')
    return Params1

# ----------------------------------------------------------------

# Make the concordance pages out of the 'word_pages' component.

##"mary": {
##            "examples": [
##                "Mary_had_a_little_lamb_page_1_segment_1",
##                "Mary_had_a_little_lamb_page_2_segment_3",
##                "Mary_had_a_little_lamb_page_2_segment_5"
##            ],
##            "extra_info": [
##                "<p>&#9998;&nbsp;Possibly the Virgin Mary.</p>",
##                ""
##            ],
##            "images": [
##                {
##                    "corpus": "Mary_had_a_little_lamb",
##                    "file": "mary.jpg",
##                    "multimedia": "img"
##                }
##            ],
##            "lemma": "mary"
##        },

def make_concordance_pages(AbstractHTML, LemmaFreqDict, NotesDict, Params):
    WordPagesDict = AbstractHTML['word_pages']
    SegmentRepresentationDict = AbstractHTML['segments']
    NotesAreDefined = False if AbstractHTML['notes'] in ( False, None ) else True
    lara_utils.print_and_flush(f'--- Making {len(WordPagesDict)} concordance pages')
    ParamsForConcordancePages = copy.copy(Params)
    ParamsForConcordancePages.audio_on_click = 'no'
    for Lemma in WordPagesDict:
        make_concordance_page(WordPagesDict[Lemma], SegmentRepresentationDict, LemmaFreqDict, NotesDict, NotesAreDefined, ParamsForConcordancePages)
    lara_utils.print_and_flush(f'--- Done')

def make_concordance_page(WordPagesItem, SegmentRepresentationDict, LemmaFreqDict, NotesDict, NotesAreDefined, Params):
    Lemma = WordPagesItem['lemma']
    ExampleNames = WordPagesItem['examples']
    ExtraInfo = WordPagesItem['extra_info']
    Images = WordPagesItem['images']
    Examples = [ make_concordance_page_example(SegmentRepresentationDict[ExampleName], LemmaFreqDict, NotesDict, Lemma, Params)
                 for ExampleName in ExampleNames ]
    make_concordance_page1(Lemma, Examples, ExtraInfo, Images, NotesAreDefined, Params)

def make_concordance_page1(Lemma, Examples, ExtraInfo, Images, NotesAreDefined, Params):
    Intro = lara_html.word_page_lines_header(Lemma, Params)
    NotesFile = False if NotesAreDefined == False else formatted_notes_file_for_word_pages_short()
    Closing = lara_html.word_page_lines_closing(formatted_count_file_for_word_pages_short(),
                                                formatted_alphabetical_file_for_word_pages_short(),
                                                NotesFile,
                                                Params)
    ImagesLines = [ format_image_for_extra_info(Image['file'], Params) for Image in Images ]
    HTMLLines = Intro + ImagesLines + ExtraInfo + Examples + Closing
    FileName = full_file_name_for_word(Lemma, Params.word_pages_directory)
    lara_utils.write_unicode_text_file('\n'.join(HTMLLines), FileName)

#_width_of_image_in_extra_info = 400

def format_image_for_extra_info(Image, Params):
    ImageSize = lara_utils.size_of_image(f'{Params.word_pages_directory}/multimedia/{Image}')
    width_of_image_in_extra_info = Params.image_width_in_concordance_pages
    if ImageSize == False:
        return f'<p>(Unable to format image {Image})</p>'
    else:
        ( Width, Height ) = ImageSize
        ( Width1, Height1 ) = ( width_of_image_in_extra_info, int( Height * width_of_image_in_extra_info / Width ) )
        return f'<img src="multimedia/{Image}" width="{Width1}" height="{Height1}" />'

_height_of_image_in_thumbnail = 80

def format_image_for_thumbnail(Image, Params):
    ImageSize = lara_utils.size_of_image(f'{Params.word_pages_directory}/multimedia/{Image}')
    if ImageSize == False:
        return f'<p>(Unable to format image {Image})</p>'
    else:
        ( Width, Height ) = ImageSize
        ( Width1, Height1 ) = ( int( Width * _height_of_image_in_thumbnail / Height ), _height_of_image_in_thumbnail )
        return f'<img src="multimedia/{Image}" width="{Width1}" height="{Height1}" />'

def make_concordance_page_example(SegmentRepresentation, LemmaFreqDict, NotesDict, Lemma, Params):
    SegmentContext = ( 'example_for', Lemma )
    Segment = make_segment(SegmentRepresentation, LemmaFreqDict, NotesDict, SegmentContext, Params)
    return f'<p>{Segment}</p>'

# ----------------------------------------------------------------

# Make the segments we'll need in the main text pages and the concordance pages.
# Note that segments are formatted differently depending on the context.

##"Mary_had_a_little_lamb_page_1_segment_2": {
##            "anchor": "Mary_had_a_little_lamb_page_1_segment_2",
##            "audio": {
##                "corpus": "Mary_had_a_little_lamb",
##                "file": "491463_200311_022336032.mp3"
##            },
##            "plain_text": "Traditional",
##            "translation": "Gammal folkvisa",
##            "words": [
##                {
##                    "word": "</h1>\n<b>"
##                },
##                {
##                    "audio": {
##                        "corpus": "Mary_had_a_little_lamb",
##                        "file": "120784_190721_202648297.mp3"
##                    },
##                    "lemma": "traditional",
##                    "translation": "Gammal folkvisa",
##                    "word": "Traditional"
##                }
##            ]
##        },

def make_segment(SegmentRepresentation, LemmaFreqDict, NotesDict, SegmentContext, Params):
    Anchor = SegmentRepresentation['anchor']
    PlainText = SegmentRepresentation['plain_text']
    CorpusId = SegmentRepresentation['corpus_name']
    Page = SegmentRepresentation['page']
    Audio = get_audio_reference_from_representation(SegmentRepresentation, Params)
    Translation = SegmentRepresentation['translation'] if 'translation' in SegmentRepresentation else '*no_translation*'
    WordRepresentations = SegmentRepresentation['words']
##    Words = [ make_word_or_embedded_multimedia(WordRepresentation, LemmaFreqDict, NotesDict, SegmentContext, Params)
##              for WordRepresentation in WordRepresentations ]
    Words = [ make_word_or_embedded_multimedia(I, WordRepresentations[I], Anchor, LemmaFreqDict, NotesDict, SegmentContext, Params)
              for I in range(0, len(WordRepresentations)) ]
    return make_segment1(Words, Anchor, PlainText, CorpusId, Page, Translation, Audio, SegmentContext, Params)

def make_segment1(Words, Anchor, PlainText, CorpusId, Page, Translation, Audio, SegmentContext, Params):
    SegmentText = ''.join(Words)
    LoudspeakerIcon = lara_extra_info.loudspeaker_icon_html_code(Params)
    TranslationIcon = lara_extra_info.translation_icon_html_code(Params)
    if Params.html_style != 'social_network':
        Controls = lara_extra_info.audio_and_translation_control_for_line(LoudspeakerIcon, TranslationIcon, Audio, SegmentText, Translation, Params)
    else:
        QuotPlainText = PlainText.replace("'", "&apos;")
        QuotTranslation = Translation.replace("'", "&apos;")
        QuotTranslation2 = Translation.replace("\"", "&quot;")
        OnClickAudioCall = f'segment_audio_onclick_action(\'{PlainText}\', \'{Audio}\');'
        OnHoverAudioCall = f'segment_audio_onhover_action(\'{PlainText}\', \'{Audio}\');'
        AudioControl = f'<span onclick="{OnClickAudioCall} onhover="{OnHoverAudioCall}">{LoudspeakerIcon}</span>'
        OnClickTranslationCall = f'segment_translation_onclick_action(\'{QuotPlainText}\', \'{QuotTranslation}\');'
        OnHoverTranslationCall = f'segment_translation_onhover_action(\'{QuotPlainText}\', \'{QuotTranslation}\');'
        TranslationControl = f'<span title="{QuotTranslation2}" onclick="{OnClickTranslationCall} onhover="{OnHoverTranslationCall}">{TranslationIcon}</span>'
        AudioControl1 = '' if Params.audio_segments == 'no' else AudioControl
        TranslationControl1 = '' if Params.segment_translation_mouseover == 'no' else TranslationControl
        Controls = f'{AudioControl1}{TranslationControl1}'
    IdTag = segment_id_tag(SegmentContext, CorpusId, Params)
    SegmentText1 = SegmentText if PlainText == '' or PlainText.isspace() or IdTag == '' and Controls == '' else f'{SegmentText} {IdTag}{Controls}' 
    if SegmentContext == 'main_text':
        return insert_before_first_real_text(f'<a id="{Anchor}"></a>', SegmentText1)
    else:
        return add_back_arrow_to_example(SegmentText1, Anchor, CorpusId, Page, Params)

# Insert material in string, skipping initial whitespaces and some tags
def insert_before_first_real_text(ToInsert, StrIn):
    I = 0
    N = len(StrIn)
    StrOut = ''
    while True:
        if I >= N:
            return StrIn + ToInsert
        elif StrIn[I].isspace():
            I += 1
        elif StrIn[I] == "<" and not starts_with_content_tag(StrIn[I:]):
            EndOfTag = StrIn.find(">", I+1)
            I = EndOfTag + 1
        else:
            return StrIn[:I] + ToInsert + StrIn[I:]

# We don't skip over these tags (provisional version, list may well change later)
content_tag_strings = ['<a ', '<span ', '<p>']

def starts_with_content_tag(Str):
    for TagStr in content_tag_strings:
        if Str.startswith(TagStr):
            return True
    return False

# Add the back-arrow link to an example
def add_back_arrow_to_example(Example, Anchor, CorpusId, Page, Params):
    MainTextPage = short_name_of_main_text_file(CorpusId, Page)
    ScreenName = lara_utils.split_screen_pane_name_for_main_text_screen(Params)
    if Params.html_style != 'social_network':
        return f'<a href="{MainTextPage}#{Anchor}" target="{ScreenName}"><b>{lara_extra_info.arrow_html_code(Params)}</b></a> {Example}'
    else:
        return f'<span onclick="load_main_text(\'{Params.relative_compiled_directory}/{MainTextPage}#{Anchor}\');"><b>&larr;</b></span> {Example}'

def segment_id_tag(SegmentContext, CorpusId, Params):
    if Params.id_on_examples == 'yes' and isinstance(SegmentContext, tuple) and len(SegmentContext) == 2 and SegmentContext[0] == 'example_for':
        return f'<b>[{print_form_for_corpus_id(CorpusId, Params)}]</b> '
    else:
        return '' 

def print_form_for_corpus_id(CorpusId, Params):
    ExplicitPrintform = Params.component_params[CorpusId].id_printform
    return ExplicitPrintform if ExplicitPrintform != '' else CorpusId

# ----------------------------------------------------------------

# For a picturebook, we add content to pictures using the <map> tag. The result looks like the following:

##    <img src="./multimedia/hello_world.jpg" width="480" usemap="#hello_world_map" height="404"/> <a id="page_1_segment_1"></a>
##    <map name="hello_world_map">
##      <area shape="rect" coords="92,80,351,188" href="word_hello.html" target="aux_frame" title="góðan daginn" onclick="playSound('./multimedia/1765174_210520_072441339.mp3');">
##      <area shape="rect" coords="82,205,384,311" href="word_world.html" target="aux_frame" title="heimur" onclick="playSound('./multimedia/150603_190806_163115365.mp3');">
##    </map>

def make_picturebook_segments_for_page(PageName, SegmentNames, SegmentRepresentationDict, Params):
    SegmentRepresentations = [SegmentRepresentationDict[SegmentName] for SegmentName in SegmentNames ]
    MapName = f'page_{PageName}_map'
    AnchorElements = make_picturebook_anchor_elements_for_page(SegmentNames)
    ( ImageElements, AreaElements ) = make_picturebook_segments_for_page1(SegmentRepresentations, MapName, Params)
    MapTagLines = make_picturebook_map_tag(AreaElements, MapName)
    return ImageElements + AnchorElements + MapTagLines

##                {
##                    "annotated_image": "yes",
##                    "image": "restaurant_date.jpg",
##                    "page": 1,
##                    "segments": [
##                        "picturebook_examples_mixed_toy_page_1_segment_1_1",
##                        "picturebook_examples_mixed_toy_page_1_segment_1_2",
##                        "picturebook_examples_mixed_toy_page_1_segment_1_3",
##                        "picturebook_examples_mixed_toy_page_1_segment_1_4"
##                    ]
##                }

def make_annotated_image(ImageRepresentation, SegmentRepresentationDict, Params):
    SegmentNames = ImageRepresentation['segments']
    ImageName = ImageRepresentation['image']
    MapName = f'{ImageName}_map'
    SegmentRepresentations = [SegmentRepresentationDict[SegmentName] for SegmentName in SegmentNames ]
    AnchorElements = make_picturebook_anchor_elements_for_page(SegmentNames)
    ( ImageElements, AreaElements ) = make_picturebook_segments_for_page1(SegmentRepresentations, MapName, Params)
    MapTagLines = make_picturebook_map_tag(AreaElements, MapName)
    #return ''.join(ImageElements + AnchorElements + MapTag)
    return ( ''.join(ImageElements + AnchorElements), '\n'.join(MapTagLines) )

def make_picturebook_anchor_elements_for_page(SegmentNames):
    return [ f'<a id="{SegmentName}"></a>' for SegmentName in SegmentNames ]

# Return ( ImageElements, AreaElements ) 
def make_picturebook_segments_for_page1(SegmentRepresentations, MapName, Params):
    Pairs = [ make_picturebook_segment(SegmentRepresentation, MapName, Params) for SegmentRepresentation in SegmentRepresentations ]
    #lara_utils.print_and_flush(Pairs)
    ImageElements = lara_utils.concatenate_lists([ Pair[0] for Pair in Pairs ])
    AreaElements = lara_utils.concatenate_lists([ Pair[1] for Pair in Pairs ])
    return ( ImageElements, AreaElements )

def make_picturebook_segment(SegmentRepresentation, MapName, Params):
    ComponentRepresentations = SegmentRepresentation['words']
    AudioControlElements = make_picturebook_segment_audio_control_elements(SegmentRepresentation, Params)
    TranslationControlElements = make_picturebook_segment_translation_control_elements(SegmentRepresentation, Params)
    Pairs = [ make_picturebook_word_or_image(ComponentRepresentation, MapName, Params) for ComponentRepresentation in ComponentRepresentations ]
    #lara_utils.print_and_flush(Pairs)
    ImageElements = lara_utils.concatenate_lists([ Pair[0] for Pair in Pairs ])
    WordAreaElements = lara_utils.concatenate_lists([ Pair[1] for Pair in Pairs ])
    AreaElements = AudioControlElements + TranslationControlElements + WordAreaElements
    return ( ImageElements, AreaElements )

def make_picturebook_segment_audio_control_elements(SegmentRepresentation, Params):
    if not 'audio' in SegmentRepresentation or not 'speaker_control_location' in SegmentRepresentation:
        return []
    Coords = SegmentRepresentation['speaker_control_location']
    Shape = 'rect' if len(Coords) == 2 else 'poly'
    Intro = f'<area shape="{Shape}" '
    CoordsNumbersStr = location_to_coords_string(Coords)
    if CoordsNumbersStr == False:
        return []
    CoordsStr = f'coords="{CoordsNumbersStr}" '
    AudioFile = SegmentRepresentation['audio']['file']
    RelativeAudioFile = f'{Params.relative_compiled_directory}/multimedia/{AudioFile}'
    PlaySoundCall = lara_audio.construct_play_sound_call_for_word(RelativeAudioFile, Params)
    Trigger = 'onclick' 
    AudioStr = f'{Trigger}="{PlaySoundCall}" '
    Coda = f'>'
    return [ Intro + CoordsStr + AudioStr + Coda ]

def make_picturebook_segment_translation_control_elements(SegmentRepresentation, Params):
    if not 'translation' in SegmentRepresentation or not 'translation_control_location' in SegmentRepresentation:
        return []
    Coords = SegmentRepresentation['translation_control_location']
    Shape = 'rect' if len(Coords) == 2 else 'poly'
    Intro = f'<area shape="{Shape}" '
    CoordsNumbersStr = location_to_coords_string(Coords)
    if CoordsNumbersStr == False:
        return []
    CoordsStr = f'coords="{CoordsNumbersStr}" '
    QuotTranslation = SegmentRepresentation['translation'].replace("'", "&apos;")
    TranslationStr = f'title="{QuotTranslation}" '
    Coda = f'>'
    return [ Intro + CoordsStr + TranslationStr + Coda ]

##    <img src="./multimedia/hello_world.jpg" width="480" usemap="#hello_world_map" height="404"/> <a id="page_1_segment_1"></a>
##    <map name="hello_world_map">
##      <area shape="rect" coords="92,80,351,188" href="word_hello.html" target="aux_frame" title="góðan daginn" onclick="playSound('./multimedia/1765174_210520_072441339.mp3');">
##      <area shape="rect" coords="82,205,384,311" href="word_world.html" target="aux_frame" title="heimur" onclick="playSound('./multimedia/150603_190806_163115365.mp3');">
##    </map>


def make_picturebook_word_or_image(ComponentRepresentation, MapName, Params):
    if isinstance(ComponentRepresentation, dict) and 'multimedia' in ComponentRepresentation and ComponentRepresentation['multimedia'] == 'img':
        return make_picturebook_image(ComponentRepresentation, MapName, Params)
    elif isinstance(ComponentRepresentation, dict) and 'location' in ComponentRepresentation and 'word' in ComponentRepresentation:
        return make_picturebook_word(ComponentRepresentation, Params)
    else:
        return ( [], [] )

##                {
##                    "corpus_name": "mary_manuscript",
##                    "file": "page1.jpg",
##                    "height": 791,
##                    "multimedia": "img",
##                    "width": 717
##                },

##    <img src="./multimedia/hello_world.jpg" width="480" usemap="#hello_world_map" height="404"/>

def make_picturebook_image(Representation, MapName, Params):
    if not ( 'file' in Representation and 'width' in Representation and 'height' in Representation ):
        lara_utils.print_and_flush(f'*** Error: bad img representation: {Representation}')
        return False
    File = Representation['file']
    URL = f'{lara_utils.relative_multimedia_dir(Params)}/{File}'
    Width = Representation['width']
    Height = Representation['height']
    ImageElements = [ f'<img class="map" src="{URL}" usemap="#{MapName}" width="{Width}" height="{Height}" />' ]
    AreaElements = []
    return ( ImageElements, AreaElements )

##                {
##                    "audio": {
##                        "corpus_name": "mary_manuscript",
##                        "file": "118812_190719_183034441.mp3"
##                    },
##                    "lemma": "Mary",
##                    "location": [ [ 32, 101 ], [ 215, 217 ] ],
##                    "translation": "Mary",
##                    "word": "Mary"
##                },
##
##  <area shape="rect" coords="92,80,351,188" href="word_hello.html" target="aux_frame"
##        title="góðan daginn" onclick="playSound('./multimedia/1765174_210520_072441339.mp3');">

##    FileName = file_name_for_word(Lemma)
##    ScreenName = lara_utils.split_screen_pane_name_for_word_page_screen(Params)
##    if WordContext == '*current_word_on_word_page*' and Params.html_style != 'social_network':
##        Result = ColouredWord
##    elif Params.html_style != 'social_network':
##        Result = f'<a href="{FileName}" target="{ScreenName}"><span id={WordId}>{ColouredWord}</span></a>'

def make_picturebook_word(Representation, Params):
    Coords = Representation['location']
    Shape = 'rect' if len(Coords) == 2 else 'poly'
    Intro = f'<area shape="{Shape}" '
    CoordsNumbersStr = location_to_coords_string(Coords)
    if CoordsNumbersStr == False:
        #lara_utils.print_and_flush(f'--- No location for coords {Coords}')
        return ( [], [] )
    CoordsStr = f'coords="{CoordsNumbersStr}" '
    FileName = file_name_for_word(Representation['lemma'])
    ScreenName = lara_utils.split_screen_pane_name_for_word_page_screen(Params)
    ConcordanceStr = f'href="{FileName}" target="{ScreenName}" '
    if 'translation' in Representation:
        QuotTranslation = Representation['translation'].replace("'", "&apos;")
        TranslationStr = f'title="{QuotTranslation}" '
    else:
        TranslationStr = ''
    if 'audio' in Representation:
        AudioFile = Representation['audio']['file']
        RelativeAudioFile = f'{Params.relative_compiled_directory}/multimedia/{AudioFile}'
        PlaySoundCall = lara_audio.construct_play_sound_call_for_word(RelativeAudioFile, Params)
        Trigger = 'onclick' if Params.audio_on_click == 'yes' else 'onmouseover'
        AudioStr = f'{Trigger}="{PlaySoundCall}" '
    else:
        AudioStr = ''
    Coda = f'>'
    ImageElements = []
    AreaElements = [ Intro + CoordsStr + ConcordanceStr + TranslationStr + AudioStr + Coda ]
    return ( ImageElements, AreaElements )

def location_to_coords_string(Coords):
    if not valid_coords_list(Coords):
        return False
    CoordsNumbers = lara_utils.concatenate_lists(Coords)
    return ','.join( [ str(X) for X in CoordsNumbers ] ) if not '' in CoordsNumbers else False

def valid_coords_list(CoordsList):
    if not isinstance(CoordsList, ( list, tuple )) or len(CoordsList) < 2:
        lara_utils.print_and_flush(f'*** Error: invalid coordinates list {CoordsList}')
        return False
    for Coords in CoordsList:
        if not isinstance(Coords, ( list, tuple )) or len(Coords) != 2:
            lara_utils.print_and_flush(f'*** Error: invalid coordinate {Coords} in list {CoordsList}')
            return False
        for Coord in Coords:
            if not isinstance(Coord, int) and not Coord == '':
                lara_utils.print_and_flush(f'*** Error: invalid coordinate {Coords} in list {CoordsList}')
                return False
    return True

##def bounding_box_coords_to_four_coords_string(BoundingBoxCoords):
##    if not isinstance(BoundingBoxCoords, ( list, tuple )) or not len(BoundingBoxCoords) == 2 or \
##       not isinstance(BoundingBoxCoords[0], ( list, tuple )) or not len(BoundingBoxCoords[0]) == 2 or \
##       not isinstance(BoundingBoxCoords[1], ( list, tuple )) or not len(BoundingBoxCoords[1]) == 2:
##        lara_utils.print_and_flush(f'*** Error: invalid bounding box "{BoundingBoxCoords}", should be pair of pairs of numbers')
##        return False
##    CoordsNumbers = BoundingBoxCoords[0] + BoundingBoxCoords[1]
##    if not is_list_of_ints(CoordsNumbers):
##        return False
##    else:
##        return ','.join( [ str(X) for X in CoordsNumbers ] )

def is_list_of_ints(List):
    return False if len([ X for X in List if not isinstance(X, int ) ]) != 0 else True

def make_picturebook_map_tag(AreaElements, MapName):
    return [ f'<map name="{MapName}">' ] + AreaElements + [ f'</map>' ]

# ----------------------------------------------------------------

# Make the elements in a segment's 'words' component.

def make_word_or_embedded_multimedia(Index, WordRepresentation, SegmentAnchor, LemmaFreqDict, NotesDict, SegmentContext, Params):
    if is_embedded_img_multimedia(WordRepresentation):
        return make_embedded_img_multimedia(WordRepresentation, SegmentContext, Params)
    elif is_embedded_audio_multimedia(WordRepresentation):
        return make_embedded_audio_multimedia(WordRepresentation, SegmentContext, Params)
    elif is_annotated_word(WordRepresentation):
        return make_annotated_word(Index, WordRepresentation, SegmentAnchor, LemmaFreqDict, NotesDict, SegmentContext, Params)
    else:
        return format_plain_text(WordRepresentation['word'], SegmentContext, Params)

def is_embedded_img_multimedia(WordRepresentation):
    return 'multimedia' in WordRepresentation and WordRepresentation['multimedia'] == 'img'


def is_embedded_audio_multimedia(WordRepresentation):
    return 'multimedia' in WordRepresentation and WordRepresentation['multimedia'] == 'audio'

def is_annotated_word(WordRepresentation):
    return 'lemma' in WordRepresentation and WordRepresentation['lemma'] != ''

def format_plain_text(Str0, SegmentContext, Params):
    Str = lara_replace_chars.restore_reserved_chars(Str0)
    if SegmentContext == 'main_text':
        return remove_comment_markers(Str)
    else:
        KeepComments = 'delete_comments' if Params.keep_comments == 'no' else 'keep_comments'
        Str1 = lara_parse_utils.remove_hashtag_comment_and_html_annotations1(Str, KeepComments)[0]
        # replace sequence of white space with single blank
        return re.sub(r"\s+", " ", Str1)

def remove_comment_markers(Str):
    return Str.replace('/*', '').replace('*/', '')    

##                {
##                    "corpus": "Mary_had_a_little_lamb_abstract_html",
##                    "file": "MaryAndLamb.jpg",
##                    "height": 292,
##                    "multimedia": "img",
##                    "width": 517
##                },
    
def make_embedded_img_multimedia(Representation, SegmentContext, Params):
    if SegmentContext != 'main_text':
        return ''
    if Params.hide_images == 'yes':
        return ''
    if not 'file' in Representation and 'width' in Representation and 'height' in Representation:
        lara_utils.print_and_flush(f'*** Error: bad img representation: {Representation}')
        return False
    File = Representation['file']
    URL = f'{lara_utils.relative_multimedia_dir(Params)}/{File}'
    Width = Representation['width']
    Height = Representation['height']
    return f'<img src="{URL}" width="{Width}" height="{Height}" />'

##                {
##                    "corpus": "Mary_had_a_little_lamb_abstract_html",
##                    "file": "MaryVerse1.mp3",
##                    "multimedia": "audio"
##                }
def make_embedded_audio_multimedia(Representation, SegmentContext, Params):
    if SegmentContext != 'main_text':
        return ''
    if not 'file' in Representation:
        lara_utils.print_and_flush(f'*** Error: bad audio representation: {Representation}')
        return False
    File = Representation['file']
    URL = f'{lara_utils.relative_multimedia_dir(Params)}/{File}'
    if 'id' in Representation:
        # We are doing audio tracking
        ID = Representation['id']
        return f'<audio id="{ID}" controls="true"><source src="{URL}" type="audio/mp3">'
    else:
        return f'<audio controls="true"><source src="{URL}" type="audio/mp3">'

##                {
##                    "audio": {
##                        "corpus": "Mary_had_a_little_lamb_abstract_html",
##                        "file": "118811_190719_183031264.mp3"
##                    },
##                    "lemma": "little",
##                    "translation": "litet ",
##                    "word": "little"
##                },
def make_annotated_word(Index, WordRepresentation, SegmentAnchor, LemmaFreqDict, NotesDict, SegmentContext, Params):
    Word0 = WordRepresentation['word']
    Word = lara_replace_chars.restore_reserved_chars(Word0)
    Lemma = WordRepresentation['lemma']
    WordId = f'{SegmentAnchor}_word_{Index}'
    Count = LemmaFreqDict[Lemma] if isinstance(LemmaFreqDict, dict) and Lemma in LemmaFreqDict else 1
    Translation = WordRepresentation['translation'] if 'translation' in WordRepresentation else ''
    Audio = get_audio_reference_from_representation(WordRepresentation, Params)
    Images = WordRepresentation['images'] if 'images' in WordRepresentation else ''
    WordContext = segment_context_to_word_context(SegmentContext, Lemma)
    if Params.picture_words and isinstance(Images, (list, tuple)) and len(Images) != 0:
        ( Word1, Colour ) = ( format_image_for_thumbnail(Images[0], Params), 'black' )
    else:
        #( Word1, Colour ) = ( Word, colour_for_word(Word, Lemma, Count, WordContext, NotesDict, Audio, Translation, Params) )
        Word1 = lara_parse_utils.remove_disambiguation_annotation_from_word(Word)
        Colour = colour_for_word(Word, Lemma, Count, WordContext, NotesDict, Audio, Translation, Params)
    return add_translation_audio_and_colour_annotations_to_word(Word1, WordId, Lemma, Translation, Audio, Colour, WordContext, Params)

def thumbnail_for_word(Word, Params):
    return

##                    "audio": {
##                        "corpus": "Mary_had_a_little_lamb_abstract_html",
##                        "file": "118811_190719_183031264.mp3"
##                    },
def get_audio_reference_from_representation(Representation, Params):
    return f"{lara_utils.relative_multimedia_dir(Params)}/{Representation['audio']['file']}" if 'audio' in Representation else '*no_audio_url*'

def add_translation_audio_and_colour_annotations_to_word(Word, WordId, Lemma, Translation, Audio, Colour, WordContext, Params):
    if Params.plain_text == 'yes':
        return Word 
    AnnotatedWord = add_translation_and_or_audio_mouseovers_to_word(Word, Lemma, Translation, Audio, WordContext, Params)
    ColouredWord = add_colour_to_word(AnnotatedWord, Colour)
    FileName = file_name_for_word(Lemma)
    ScreenName = lara_utils.split_screen_pane_name_for_word_page_screen(Params)
    if WordContext == '*current_word_on_word_page*' and Params.html_style != 'social_network':
        Result = ColouredWord
    elif Params.html_style != 'social_network':
        Result = f'<a href="{FileName}" target="{ScreenName}"><span id={WordId}>{ColouredWord}</span></a>'
    else:
        QuotTranslation = Translation.replace("'", "&apos;")
        QuotWord = Word.replace("'", "&apos;")
        OnClickCall = f'word_onclick_action(\'{QuotWord}\', \'{Params.relative_compiled_directory}/{FileName}\', \'{Audio}\', \'{QuotTranslation}\');'
        OnHoverCall = f'word_onhover_action(\'{QuotWord}\', \'{Audio}\', \'{QuotTranslation}\');'
        Result = f'<span id={WordId} onclick="{OnClickCall}" onhover="{OnHoverCall}">{ColouredWord}</span>'
    return Result

def add_colour_to_word(Word, Colour):
    return f'<span class="{Colour}">{Word}</span>' if Colour != 'black' else Word

def add_translation_and_or_audio_mouseovers_to_word(Word, Lemma, Translation, Audio, WordContext, Params):
    ## For social network, just add the translation mouseover if there is a translation
    if Params.html_style == 'social_network':
        return lara_extra_info.add_translation_mouseover_to_word(Word, Translation) if Params.translation_mouseover == 'yes' and Translation else Word
    elif Params.translation_mouseover == 'yes' and Params.audio_mouseover != 'no' and Translation and Audio != '*no_audio_url*':
        return lara_extra_info.add_translation_and_audio_mouseovers_to_word(Word, Translation, Audio, Params)
    elif Params.translation_mouseover == 'yes' and Translation:
        return lara_extra_info.add_translation_mouseover_to_word(Word, Translation)
    elif Params.audio_mouseover != 'no' and Audio != '*no_audio_url*':
        return add_audio_mouseover_to_word(Word, Audio, Params)
    else:
        return Word

def add_audio_mouseover_to_word(AnnotatedWord, Audio, Params):
    PlaySoundCall = lara_audio.construct_play_sound_call_for_word(Audio, Params)
    Trigger = 'onclick' if Params.audio_on_click == 'yes' else 'onmouseover'
    return f'<span class="sound" {Trigger}="{PlaySoundCall}">{AnnotatedWord}</span>'

def segment_context_to_word_context(SegmentContext, Lemma):
    if isinstance(SegmentContext, (list, tuple)) and len(SegmentContext) == 2 and SegmentContext[0] == 'example_for':
        if SegmentContext[1] == Lemma:
            return '*current_word_on_word_page*'
        else:
            return '*non_current_word_on_word_page*'
    else:
        return '*word_on_main_page*'

def internalise_pos_colours_if_necessary(Params):
    POSColoursFile = Params.postags_colours_file
    if POSColoursFile == '':
        return
    PosColourLines = lara_utils.read_lara_csv(POSColoursFile)
    if PosColourLines == False:
        lara_utils.print_and_flush(f'*** Warning: unable to read POS colour spreadsheet {POSColoursFile}')
        return
    Dict = {}
    for Line in PosColourLines:
        if len(Line) >= 2 and Line[0] != '' and Line[1] != '':
            ( POS, Colour ) = Line[:2]
            if not Colour in lara_config.lara_html_colours:
                lara_utils.print_and_flush(f'*** Warning: unknown colour "{Colour}". Supported colours are {lara_config.lara_html_colours}')
            else:
                Dict[POS] = Colour
    Params.postag_colours = Dict
                                                                     
def colour_for_word(Word, Lemma, Count, WordContext, NotesDict, Audio, Translation, Params):
    if WordContext == '*current_word_on_word_page*':
        return 'red'
    elif WordContext == '*non_current_word_on_word_page*':
        return colour_for_pos_tag_in_lemma(Lemma, Params)
    else:
        return colour_for_main_text_word(Word, Lemma, Count, NotesDict, Audio, Translation, Params)

## If we aren't using colour for frequencies, we might want to use it to mark audio words or notes or MWEs
def colour_for_main_text_word(Word, Lemma, Count, NotesDict, Audio, Translation, Params):
    if Params.audio_words_in_colour != 'no' and Params.audio_mouseover != 'no' and Params.coloured_words == 'no' and Audio != '*no_audio_url*':
        return Params.audio_words_in_colour
    elif Params.note_words_in_colour != 'no' and Params.coloured_words == 'no' and Lemma in NotesDict:
        return 'red'
    elif Params.image_dict_words_in_colour != 'no' and Params.coloured_words == 'no' and len(lara_translations.all_images_for_word(Lemma)) > 0:
        return 'red'
    elif Params.translated_words_in_colour != 'no' and Params.coloured_words == 'no' and Translation != '':
        return 'red'
    elif Params.translated_words_not_in_colour != 'no' and Params.coloured_words == 'no' and ( Translation == '' or Translation.isspace() ):
        return 'red'
    elif Params.mwe_words_in_colour != 'no' and Params.coloured_words == 'no' and lemma_looks_like_multiword(Lemma, Params):
        return 'red'
    elif Params.postags_colours_file != '':
        Colour = colour_for_pos_tag_in_lemma(Lemma, Params)
        #lara_utils.print_and_flush(f'{Colour} = colour_for_pos_tag_in_lemma({Lemma}, Params)')
        return Colour
    elif Params.coloured_words == 'no':
        return 'black'
    else:
        return colour_id_for_count(Count)

def colour_for_pos_tag_in_lemma(Lemma, Params):
    Components = Lemma.split('/')
    if len(Components) == 1:
        # No POS
        return 'black'
    POS = Components[1]
    PostagColourDict = Params.postag_colours
    return PostagColourDict[POS] if POS in PostagColourDict else 'black'    

def colour_id_for_count(Count):
    if Count <= 1:
        return 'red'
    elif 2 <= Count and Count <= 3:
        return 'green'
    elif 4 <= Count and Count <= 5:
        return 'blue'
    else:
        return 'black'

def lemma_looks_like_multiword(Lemma, Params):
    return ' ' in Lemma or \
           looks_like_an_italian_reflexive(Lemma, Params) or \
           looks_like_a_french_reflexive(Lemma, Params)

# This is a hack, need a better way to identify MWEs with no spaces

def looks_like_an_italian_reflexive(Lemma, Params):
    return Params.language == 'italian' and Lemma.endswith('rsi')

def looks_like_a_french_reflexive(Lemma, Params):
    return Params.language == 'french' and Lemma.startswith("s'")

# ----------------------------------------------------------------

# Make the various auxiliary files
    
def make_auxiliary_files(AbstractHTML, NotesDict, Params):
    make_frequency_ordered_index_file(AbstractHTML, NotesDict, Params)
    make_alphabetically_ordered_index_file(AbstractHTML, NotesDict, Params)
    make_notes_file(AbstractHTML, Params)
    make_css_file(AbstractHTML, Params)
    make_custom_css_file(AbstractHTML, Params)
    make_script_file(AbstractHTML, Params)
    make_custom_script_file(AbstractHTML, Params)
    make_toc_file(AbstractHTML, Params)

##"alphabetical_index": [
##        {
##            "count": 3,
##            "word": [
##                {
##                    "lemma": "a",
##                    "translation": "un/une",
##                    "word": "a"
##                }
##            ]
##        },
##        (...)

def make_lemma_freq_dict(AbstractHTML):
    Index = AbstractHTML['alphabetical_index']
    return { Item['word'][0]['lemma']: Item['count'] for Item in Index }

def make_alphabetically_ordered_index_file(AbstractHTML, NotesDict, Params):
    Params1 = adapt_params_for_count_and_alphabetical_files(Params)
    Items = AbstractHTML['alphabetical_index']
    HTMLList = [ alphabetically_ordered_index_file_item_to_html_line(Item, NotesDict, Params1) for Item in Items ]
    Header = [lara_config.get_ui_text('index_heading_word', Params),
              lara_config.get_ui_text('index_heading_freq', Params)]
    OutFile = f'{Params.word_pages_directory}/{formatted_alphabetical_file_for_word_pages_short()}'
    lara_html.print_lara_html_table(lara_config.get_ui_text('alphabetical_index', Params), Header, HTMLList, OutFile, Params)

def alphabetically_ordered_index_file_item_to_html_line(Item, NotesDict, Params):
    WordRepresentation = Item['word'][0]
    Count = Item['count']
    # We don't need lemma frequencies
    LemmaFreqDict = {}
    SegmentContext = '*index_page*'
    Word = WordRepresentation['word']
    AnnotatedWord = make_annotated_word(0, WordRepresentation, f'alphabetical_index_{Word}', LemmaFreqDict, NotesDict, SegmentContext, Params)
    return ( AnnotatedWord, Count )

##"frequency_index": [
##        {
##            "count": 4,
##            "cumulative_percentage": "7.55%",
##            "word": [
##                {
##                    "lemma": "lamb",
##                    "word": "lamb"
##                }
##            ]
##        },

def make_frequency_ordered_index_file(AbstractHTML, NotesDict, Params):
    Params1 = adapt_params_for_count_and_alphabetical_files(Params)
    Items = AbstractHTML['frequency_index']
    if Params.frequency_list_only_images == 'yes':
        Items = frequency_list_items_with_images(Items)
    HTMLList = []
    for Index in range(0, len(Items)):
        HTMLList += [ frequency_ordered_index_file_item_to_html_line(Items[Index], Index + 1, NotesDict, Params1) ]
    Header = [lara_config.get_ui_text('index_heading_rank', Params),
              lara_config.get_ui_text('index_heading_word', Params),
              lara_config.get_ui_text('index_heading_freq', Params),
              lara_config.get_ui_text('index_heading_cumul', Params)]
    # Don't show percentages if we've taken out items
    if Params.frequency_list_only_images == 'yes':
        Header = Header[:3]
    OutFile = f'{Params.word_pages_directory}/{formatted_count_file_for_word_pages_short()}'
    lara_html.print_lara_html_table(lara_config.get_ui_text('frequency_index', Params), Header, HTMLList, OutFile, Params)

def frequency_list_items_with_images(Items):
    return [ Item for Item in Items
             if 'word' in Item and isinstance(Item['word'], ( list, tuple )) and len(Item['word']) != 0 and
             'images' in Item['word'][0] and len(Item['word'][0]['images']) != 0 ]

def frequency_ordered_index_file_item_to_html_line(Item, Rank, NotesDict, Params):
    WordRepresentation = Item['word'][0]
    Count = Item['count']
    CumulativePercentage = Item['cumulative_percentage']
    # We don't need lemma frequencies
    LemmaFreqDict = {}
    SegmentContext = '*index_page*'
    Word = WordRepresentation['word']
    AnnotatedWord = make_annotated_word(0, WordRepresentation, f'frequency_index_{Word}', LemmaFreqDict, NotesDict, SegmentContext, Params)
    return ( Rank, AnnotatedWord, Count ) if Params.frequency_list_only_images == 'yes' else ( Rank, AnnotatedWord, Count, CumulativePercentage )

# We can't have audio mouseovers in these files, because they are lemmas rather than surface words
# Also, we can't use a surface_word_token model here
def adapt_params_for_count_and_alphabetical_files(Params):
    Params1 = copy.copy(Params)
    Params1.corpus_id = 'local_files'
    Params1.audio_mouseover = 'no'
    if Params.word_translations_on == 'surface_word_token':
        Params1.word_translations_on = 'lemma'
    # We don't want to cache any annotated words created here, because they will lack audio
    Params1.switch_off_caching = 'yes'
    return Params1

##"notes": [
##        {
##            "note": "Could be Jesus.",
##            "word": [
##                {
##                    "lemma": "lamb",
##                    "word": "lamb"
##                }
##            ]
##        },
##        {
##            "note": "Possibly the Virgin Mary.",
##            "word": [
##                {
##                    "lemma": "mary",
##                    "word": "mary"
##                }
##            ]
##        }
##    ],

def make_notes_dict(AbstractHTML):
    NotesItems = AbstractHTML['notes']
    if NotesItems in ( False, None ):
        return {}
    else:
        return { NoteItem['word'][0]['lemma']: NoteItem['note'] for NoteItem in NotesItems }

def make_notes_file(AbstractHTML, Params):
    NotesItems = AbstractHTML['notes']
    if NotesItems in ( False, None ):
        return
    HTMLList = [ note_representation_to_line(NoteItem, Params) for NoteItem in NotesItems ]
    Header = [lara_config.get_ui_text('index_heading_word', Params),
              lara_config.get_ui_text('index_heading_note', Params)]
    File = f'{Params.word_pages_directory}/{formatted_notes_file_for_word_pages_short()}'
    lara_html.print_lara_html_table(lara_config.get_ui_text('notes', Params), Header, HTMLList, File, Params)
    lara_utils.print_and_flush(f'--- Written notes file {File}')

def note_representation_to_line(NoteItem, Params):
    WordRepresentation = NoteItem['word'][0]
    Note = NoteItem['note']
    # We don't need lemma frequencies
    LemmaFreqDict = {}
    NotesDict = {}
    SegmentContext = '*index_page*'
    AnnotatedWord = make_annotated_word(1, WordRepresentation, 'note', LemmaFreqDict, NotesDict, SegmentContext, Params)
    return ( AnnotatedWord, Note )

#make_annotated_word(Index, WordRepresentation, SegmentAnchor, LemmaFreqDict, NotesDict, SegmentContext, Params)

def make_css_file(AbstractHTML, Params):
    CSSLines = AbstractHTML['css']
    CssText = '\n'.join(CSSLines)
    File = f'{Params.word_pages_directory}/_styles_.css'
    lara_utils.write_unicode_text_file(CssText, File)
    lara_utils.print_and_flush(f'--- Written css file {File}')

def make_custom_css_file(AbstractHTML, Params):
    CSSLines = AbstractHTML['custom_css']
    if CSSLines in ( False, None ):
        return
    CssText = '\n'.join(CSSLines)
    File = f'{Params.word_pages_directory}/_custom_styles_.css'
    lara_utils.write_unicode_text_file(CssText, File)
    lara_utils.print_and_flush(f'--- Written css file {File}')

def make_script_file(AbstractHTML, Params):
    MainScriptLines = AbstractHTML['script']
    AudioTrackingData = AbstractHTML['audio_tracking_data']
    AudioTrackingLines = lara_html.audio_tracking_scriptfunction(AudioTrackingData).split('\n')
    ScriptLines = MainScriptLines + AudioTrackingLines
    ScriptText = '\n'.join(ScriptLines)
    File = f'{Params.word_pages_directory}/_script_.js'
    lara_utils.write_unicode_text_file(ScriptText, File)
    lara_utils.print_and_flush(f'--- Written script file {File}')

def make_custom_script_file(AbstractHTML, Params):
    ScriptLines = AbstractHTML['custom_script']
    if ScriptLines in ( False, None ):
        return
    ScriptText = '\n'.join(ScriptLines)
    File = f'{Params.word_pages_directory}/_custom_script_.js'
    lara_utils.write_unicode_text_file(ScriptText, File)
    lara_utils.print_and_flush(f'--- Written custom script file {File}')

##"toc": [
##        {
##            "anchor": "Mary_had_a_little_lamb_page_1_segment_1",
##            "page_name": 1,
##            "plain_text": " Mary Had a Little Lamb ",
##            "tag": "h1"
##        },
##        {
##            "anchor": "Mary_had_a_little_lamb_page_2_segment_1",
##            "page_name": 2,
##            "plain_text": " Verse 1 ",
##            "tag": "h2"
##        },
##        {
##            "anchor": "Mary_had_a_little_lamb_page_3_segment_1",
##            "page_name": 3,
##            "plain_text": " Verse 2 ",
##            "tag": "h2"
##        }
##    ],
def make_toc_file(AbstractHTML, Params):
    if not 'toc' in AbstractHTML or AbstractHTML['toc'] == False:
        return
    TOCItems = AbstractHTML['toc']    
    Intro = lara_html.toc_lines_intro( lara_config.get_ui_text("table_of_contents", Params), Params )
    Body = [ make_toc_line(TOCItem, Params) for TOCItem in TOCItems ]
    Closing = lara_html.toc_lines_closing()
    Lines = Intro + Body + Closing
    File = f'{Params.word_pages_directory}/_toc_.html'            
    lara_utils.write_unicode_text_file("\n".join( Lines ), File)
    lara_utils.print_and_flush(f'--- Written table of contents file {File}')

def make_toc_line(TOCItem, Params):
    Anchor = TOCItem['anchor']
    CorpusId = TOCItem['corpus_name']
    PageName = TOCItem['page_name']
    Text = TOCItem['plain_text']
    Tag = TOCItem['tag']
    Target = lara_utils.split_screen_pane_name_for_main_text_screen(Params)
    Href = f'{short_name_of_main_text_file(CorpusId, PageName)}#{Anchor}'
    return f"<{Tag} class='toc'><a target='{Target}' href='{Href}'><b>{lara_extra_info.arrow_html_code(Params)}</b> {Text}</{Tag}>"

# ----------------------------------------------------------------

# Turn lines into HTML by adding <p> tags
def hyperlinked_lines_to_html_lines(HyperlinkedLines):
    return [ word_page_line_to_html_line(HyperlinkedLine) for HyperlinkedLine in HyperlinkedLines ]

def word_page_line_to_html_line(HyperlinkedLine):
    if HyperlinkedLine.isspace() or HyperlinkedLine == '':
        HyperlinkedLine1 = '&nbsp;'
    else:
        HyperlinkedLine1 = HyperlinkedLine
    if line_starts_with_tag_not_needing_paragraph(HyperlinkedLine1):
        #lara_utils.print_and_flush(f'--- Does not require paragraph: "{HyperlinkedLine1}"')
        return HyperlinkedLine1
    else:
        #lara_utils.print_and_flush(f'--- Requires paragraph: "{HyperlinkedLine1}"')
        return f'<p>{HyperlinkedLine1}</p>'

tags_not_needing_paragraph = ['<h1', '<h2',
                              '<img', '<video' '<audio',
                              '<table', '</table>',
                              '<tr', '<td', '</tr', '</td']

# Don't wrap a <p> around headers, images, embedded audio and table elements
def line_starts_with_tag_not_needing_paragraph(Line):
    Line1 = remove_anchor_tags(Line.lstrip().lower())
    for Tag in tags_not_needing_paragraph:
        if Line1.startswith(Tag):
            return True
    return False

def remove_anchor_tags(Str):
    return re.sub(r'<a[^>]*>|</a>', '', Str)

# ----------------------------------------------------------------
 
def full_name_of_main_text_file(CorpusId, PageName, Params):
    ShortName = short_name_of_main_text_file(CorpusId, PageName)
    Dir = Params.word_pages_directory
    return f'{Dir}/{ShortName}'

def short_name_of_main_text_file(CorpusId, PageName):
    return f'_main_text_{CorpusId}_{PageName}.html'
    #return f'_main_text_{PageName}_.html'

def short_name_of_preceding_main_text_file(CorpusId, PageName, AllPageNames):
    if not ( CorpusId, PageName ) in AllPageNames:
        lara_utils.print_and_flush(f'*** Error: ( {CorpusId}, {PageName} ) not in list of page names {AllPageNames}')
        return False
    Index = AllPageNames.index(( CorpusId, PageName ))
    if Index == 0:
        return False
    ( CorpusId1, PageName1 ) = AllPageNames[Index - 1]
    return short_name_of_main_text_file(CorpusId1, PageName1) 

def short_name_of_following_main_text_file(CorpusId, PageName, AllPageNames):
    if not ( CorpusId, PageName ) in AllPageNames:
        lara_utils.print_and_flush(f'*** Error: ( {CorpusId}, {PageName} ) not in list of page names {AllPageNames}')
        return False
    Index = AllPageNames.index(( CorpusId, PageName ))
    if Index == len(AllPageNames) - 1:
        return False
    ( CorpusId1, PageName1 ) = AllPageNames[Index + 1]
    return short_name_of_main_text_file(CorpusId1, PageName1) 
    
def short_name_of_first_main_text_file(AllPageNames):
    ( CorpusId, PageName ) = AllPageNames[0]
    return short_name_of_main_text_file(CorpusId, PageName)
    
# Name of word page file for a given word
def full_file_name_for_word(Word, MultimediaDir):
    FileName = file_name_for_word(Word)
    return f'{MultimediaDir}/{FileName}'

def file_name_for_word(Word0):
    Word = lara_mwe.strip_off_mwe_part_tag_returning_lemma_and_length(Word0)[0]
    Word1 = lara_split_and_clean.clean_up_word_for_files(Word)
    return f'word_{Word1}.html'

def page_name_for_hyperlinked_text_file(Params):
    return f'{Params.word_pages_directory}/{formatted_hyperlinked_text_file_for_word_pages_short()}'

# Names of top-level files
def formatted_hyperlinked_text_file_for_word_pages_short():
    return '_hyperlinked_text_.html'

def formatted_main_text_file_for_word_pages_short(PageName):
    return f'_main_text_{PageName}_.html'

def formatted_count_file_for_word_pages_short():
    return '_index_.html'

def formatted_alphabetical_file_for_word_pages_short():
    return '_alphabetical_index_.html'

def formatted_notes_file_for_word_pages_short():
    return '_notes_.html'

def pages_file_for_word_pages_short():
    return '_pages_.json'
