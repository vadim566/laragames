
import lara_top
import lara_download_metadata
import lara_html
import lara_images
import lara_audio
import lara_split_and_clean
import lara_translations
import lara_extra_info
import lara_utils
import lara_parse_utils
import lara_replace_chars
import lara_config
import lara_mwe
import lara_forced_alignment
import lara_postags
import lara_play_all
import time
import math
import statistics
import copy
import re

# Make the internal json-formatted frequency count file
def count_file(SplitFile, CountFile, Params):
    #InList = lara_split_and_clean.read_split_file(SplitFile, Params)
    InList = lara_mwe.read_split_file_applying_mwes_if_possible(Params)
    if not InList:
        lara_utils.print_and_flush(f'*** Error: unable to find {SplitFile} so unable to create count file')
        return False
    Assoc = {}
    count_lara_list(InList, Assoc)
    write_lara_count_file(Assoc, CountFile)
    store_headword_word_table(InList)

def surface_count_file(SplitFile, CountFile, Params):
    #InList = lara_split_and_clean.read_split_file(SplitFile, Params)
    InList = lara_mwe.read_split_file_applying_mwes_if_possible(Params)
    if not InList:
        lara_utils.print_and_flush(f'*** Error: unable to read MWE split list so unable to create surface count file')
        return False
    Assoc = {}
    surface_count_lara_list(InList, Assoc)
    write_lara_count_file(Assoc, CountFile)

# Read the count/surface count file. Try to remake it if it doesn't already exist
def read_count_file(CountFile, Params):
    if not lara_utils.file_exists(CountFile) and Params.split_file != '':
        lara_utils.print_and_flush(f'*** Warning: unable to find {CountFile}, trying to remake')
        try:
            count_file(Params.split_file, CountFile, Params)
        except:
            lara_utils.print_and_flush(f'*** Error: something went wrong when trying to remake count file')
            return False
    if not lara_utils.file_exists(CountFile):
        lara_utils.print_and_flush(f'*** Error: unable to find or remake count file')
        return False
    return lara_utils.read_json_file(CountFile)

def read_surface_count_file(CountFile, Params):
    if not lara_utils.file_exists(CountFile) and Params.split_file != '':
        lara_utils.print_and_flush(f'*** Warning: unable to find {CountFile}, trying to remake')
        try:
            surface_count_file(Params.split_file, CountFile, Params)
        except:
            lara_utils.print_and_flush(f'*** Error: something went wrong when trying to remake count file')
            return False
    if not lara_utils.file_exists(CountFile):
        lara_utils.print_and_flush(f'*** Error: unable to find or remake surface count file')
        return False
    return lara_utils.read_json_file(CountFile)

# Make the full set of compiled word pages (second stage of compilation)
def make_word_pages(Params):
    init_make_word_pages(Params)
    SplitList = init_resources_from_local_files(Params)
    Result = make_word_pages_main(SplitList, Params)
    if Params.compile_cache_file:
        cache_compilation_data(Params)
    return Result

# --------------------------------------

# Processing to create the internal count file
def count_lara_list(InList, Assoc):
    for ( PageInfo, Chunks) in InList:
        for Chunk in Chunks:
            Clean = Chunk[2]
            for ( Surface, Lemma0 ) in Clean:
                # If it's part of an MWE, divide count by length of MWE
                # so we end up with 1 for the whole MWE
                if Lemma0 != '':
                    ( Lemma, MWELen ) = lara_mwe.strip_off_mwe_part_tag_returning_lemma_and_length(Lemma0)
                    lara_utils.inc_assoc_by_amount(Assoc, Lemma, 1/MWELen)

def surface_count_lara_list(InList, Assoc):
    for ( PageInfo, Chunks) in InList:
        for Chunk in Chunks:
            Clean = Chunk[2]
            for ( Surface, Lemma ) in Clean:
                if Lemma != '':
                    lara_utils.inc_assoc(Assoc, Surface)

def write_lara_count_file(Assoc, File):
    List = [ [Lemma, round(Assoc[Lemma]) ] for Lemma in Assoc ]
    SortedList = sorted(List, key=lambda x: x[1], reverse=True)
    lara_utils.write_json_to_file(SortedList, File)
    lara_utils.print_and_flush(f'--- Written count file ({len(SortedList)} records) {File}')

headword_word = {}

# Create a table which associates words with lemmas
def store_headword_word_table(InList):
    Pairs0 = [ ( Tag, Word ) for ( PageInfo, Chunks) in InList for Chunk in Chunks
               for ( Word, Tag ) in Chunk[2] \
               if Tag != '' and not lara_parse_utils.is_punctuation_string(Word) ]
    Pairs = lara_utils.remove_duplicates(Pairs0)
    store_headword_word_table1(Pairs)
    lara_utils.print_and_flush(f'--- Stored {len(Pairs)} headword/surface-word associations')

def store_headword_word_table1(Pairs):
    global headword_word
    headword_word = {}
    for ( Tag, Word ) in Pairs:
        if Tag in headword_word:
            headword_word[Tag] += [Word]
        else:
            headword_word[Tag] = [Word]

# --------------------------------------

cached_compilation_data_available = False

# Either initialise data or else restore cached data if we're incrementally compiling
def init_make_word_pages(Params):
    WordPagesDir = lara_utils.absolute_file_name(Params.word_pages_directory)
    MultimediaDir = f'{WordPagesDir}/multimedia'
    # Not saving word_to_annotated_word - it is typically going to be large, so guessing that the overhead
    # of saving and restoring is not worth the payoff
    init_word_to_annotated_word()
    if not ( Params.recompile and lara_utils.directory_exists(WordPagesDir) ):
        lara_utils.create_directory_deleting_old_if_necessary(WordPagesDir)
    if not ( Params.recompile and lara_utils.directory_exists(MultimediaDir) ):
        lara_utils.create_directory(MultimediaDir)
    if Params.recompile and Params.compile_cache_file and lara_utils.file_exists(Params.compile_cache_file):
        restore_cached_compilation_data(Params)
    else:
        init_compilation_data()

# If we're doing local compilation, initialise audio and translation data from the appropriate directories
def init_resources_from_local_files(Params):
    StartTime = time.time()
    #SplitList0 = lara_split_and_clean.read_split_file(Params.split_file, Params)
    SplitList0 = lara_mwe.read_split_file_applying_mwes_if_possible(Params)
    # Now that we're translating MWEs as such, we need to keep the MWE lemma information longer
    #SplitList = lara_mwe.simplify_mwe_lemmas_in_split_list(SplitList0)
    SplitList = SplitList0
    if Params.local_files == 'yes':
        lara_images.process_image_directory(Params)
        lara_audio.process_recorded_audio_directory(Params, SplitList, 'segments')
        lara_audio.process_recorded_audio_directory(Params, SplitList, 'words')
        lara_audio.read_and_store_segment_audio_word_breakpoint_csv(Params)
        lara_translations.init_translation_tables(Params)
        if Params.segment_translation_spreadsheet:
            lara_translations.process_segment_spreadsheet_file('local_files', Params.segment_translation_spreadsheet)
        else:
            lara_utils.print_and_flush('--- No segment translation spreadsheet defined')
            
        if Params.word_translations_on == 'surface_word_token' and Params.translation_spreadsheet_tokens != '':
            lara_translations.process_word_token_spreadsheet_file('local_files', Params.translation_spreadsheet_tokens)
        elif Params.word_translations_on == 'surface_word_type' and Params.translation_spreadsheet_surface != '':
            lara_translations.process_word_spreadsheet_file('local_files', Params.translation_spreadsheet_surface, Params)
        elif Params.word_translations_on == 'lemma' and Params.translation_spreadsheet != '':
            lara_translations.process_word_spreadsheet_file('local_files', Params.translation_spreadsheet, Params)
        else:
            lara_utils.print_and_flush('--- No word translation spreadsheet defined')
            
        if Params.notes_spreadsheet != '':
            lara_translations.process_note_file('local_files', Params.notes_spreadsheet, Params)
        else:
            lara_utils.print_and_flush('--- No notes spreadsheet defined')

        if Params.image_dict_spreadsheet != '':
            lara_translations.process_image_dict_file('local_files', Params.image_dict_spreadsheet, Params)
        else:
            lara_utils.print_and_flush('--- No image dictionary spreadsheet defined')
        
    if StartTime is not None: 
        lara_utils.print_and_flush_with_elapsed_time('--- Completed initialisation', StartTime)
    return SplitList

# Having done initialisation, make the top-level pages, collect the word-page info, then make the word pages
def make_word_pages_main(PageOrientedSplitList, Params):
    global word_page_info_assoc
    PagesDir = Params.word_pages_directory
    store_vocab_counts(Params.count_file, Params)
    ParamsForIndexPages = make_index_page_version_of_params(Params)
    FrequencyIndexFileRepresentation = format_count_file_for_word_pages(Params.count_file, PagesDir, ParamsForIndexPages)
    AlphabeticalIndexFileRepresentation = format_alphabetical_file_for_word_pages(Params.count_file, PagesDir, ParamsForIndexPages)
    NotesFileRepresentation = format_notes_file_for_word_pages(PagesDir, ParamsForIndexPages)
    LemmaImageListRepresentation = lara_translations.lemma_and_image_list_for_representation(Params)
    ( TextFiles, PageRepresentations ) = format_main_text_files_for_word_pages(PageOrientedSplitList, PagesDir, Params)
    TopFile = format_hyperlinked_text_file_for_word_pages(Params)
    TOCFileRepresentation = format_toc_file(f'{PagesDir}/_toc_.html', Params)
    CSSFile = format_default_css_file(f'{PagesDir}/_styles_.css', Params)
    CustomCSSFile = format_custom_css_file(f'{PagesDir}/_custom_styles_.css', Params)
    ( ScriptFile, AudioTrackingData ) = format_default_script_file(f'{PagesDir}/_script_.js', Params)
    CustomScriptFile = format_custom_script_file(f'{PagesDir}/_custom_script_.js', Params)
    SplitList = [ Chunk for ( PageInfo, Chunks ) in PageOrientedSplitList if is_new_page(PageInfo, Params) for Chunk in Chunks ]
    ParamsForWordPages = make_concordance_page_version_of_params(Params)
    ( Assoc, ChangedWordsAssoc ) = collect_word_page_info(SplitList, ParamsForWordPages, ParamsForWordPages.max_examples_per_word_page)
    WordPagesRepresentation = make_word_pages1(Assoc, ChangedWordsAssoc, PagesDir, ParamsForWordPages)
    word_page_info_assoc = Assoc
    make_representation_file(FrequencyIndexFileRepresentation, AlphabeticalIndexFileRepresentation,
                             NotesFileRepresentation, LemmaImageListRepresentation,
                             TOCFileRepresentation, CSSFile, CustomCSSFile, ScriptFile, CustomScriptFile, AudioTrackingData,
                             PageRepresentations, WordPagesRepresentation,
                             Params)     
    return { 'top_file': TopFile, 'text_files': TextFiles }

def make_representation_file(FrequencyIndexFileRepresentation, AlphabeticalIndexFileRepresentation,
                             NotesFileRepresentation, LemmaImageListRepresentation,
                             TOCFileRepresentation, CSSFile, CustomCSSFile, ScriptFile, CustomScriptFile, AudioTrackingData,
                             PagesRepresentation, WordPagesRepresentation,
                             Params):
    if Params.abstract_html == 'plain_html_only':
        return
    Representation = { 'frequency_index': FrequencyIndexFileRepresentation,
                       'alphabetical_index': AlphabeticalIndexFileRepresentation,
                       'notes': NotesFileRepresentation,
                       'image_lexicon': LemmaImageListRepresentation,
                       'toc': TOCFileRepresentation,
                       'css': CSSFile,
                       'custom_css': CustomCSSFile,
                       'script': ScriptFile,
                       'custom_script': CustomScriptFile,
                       'audio_tracking_data': AudioTrackingData,
                       'pages': PagesRepresentation,
                       'word_pages': WordPagesRepresentation }
    Representation1 = remove_null_items_from_representation(Representation)
    RepresentationFinal = replace_segments_by_anchors(Representation1)
    if Params.abstract_html_format != 'plain_html_only':
        #RepresentationFile = lara_top.lara_tmp_file('abstract_html_file', Params)
        RepresentationFile = get_abstract_html_file(Params)
        lara_utils.save_data_to_pickled_gzipped_file(RepresentationFinal, RepresentationFile)
    if Params.abstract_html_format != 'pickle_only':
        #JSONRepresentationFile = lara_top.lara_tmp_file('abstract_html_json_file', Params)
        JSONRepresentationFile = get_abstract_html_json_file(Params)
        lara_utils.write_json_to_file_plain_utf8(RepresentationFinal, JSONRepresentationFile)

def get_abstract_html_file(Params):
    if Params.abstract_html_file != '' and lara_utils.extension_for_file(Params.abstract_html_file) == 'gz':
        return Params.abstract_html_file
    else:
        return lara_top.lara_tmp_file('abstract_html_file', Params)

def get_abstract_html_json_file(Params):
    if Params.abstract_html_file != '' and lara_utils.extension_for_file(Params.abstract_html_file) == 'json':
        return Params.abstract_html_file
    else:
        return lara_top.lara_tmp_file('abstract_html_json_file', Params)

def remove_null_items_from_representation(Representation):
    if isinstance(Representation, ( list, tuple )):
        return [ remove_null_items_from_representation(Item) for Item in Representation ]
    elif isinstance(Representation, dict):
        return { Key: remove_null_items_from_representation(Representation[Key]) for Key in Representation
                 if not null_value_for_representation_key(Key, Representation[Key]) }
    else:
        return Representation

def null_value_for_representation_key(Key, Value):
    if Key == 'lemma':
        return Value  == '' 
    elif Key == 'audio':
        return isinstance(Value, dict) and 'file' in Value and Value['file'] in ( '*no_audio_url*', False )
    elif Key == 'translation':
        return Value in ( '*no_translation*', False )
    else:
        return False

def replace_segments_by_anchors(Representation):
    Pages = Representation['pages']
    SegmentDict = {}
    for Page in Pages:
        if 'segments' in Page:
            Anchors = []
            for Segment in Page['segments']:
                Anchor = Segment['anchor']
                Anchors += [ Anchor ]
                SegmentDict[Anchor] = Segment
            Page['segments'] = Anchors
    Representation['segments'] = SegmentDict
    return Representation

# Don't try to put audio on index items, since they are lemmas rather than surface words
def make_index_page_version_of_params(Params):
    ParamsNoAudio = copy.copy(Params)
    ParamsNoAudio.audio_mouseover = 'no'
    ParamsNoAudio.audio_segments = 'no'
    ParamsNoAudio.audio_segment_warnings = 'no'
    return ParamsNoAudio

# We might do audio on mouseover for the concordance pages
def make_concordance_page_version_of_params(Params):
    ParamsForWordPages = copy.copy(Params)
    ParamsForWordPages.audio_on_click = Params.audio_on_click if lara_audio.params_say_to_use_extracted_audio(Params) else 'no'
    return ParamsForWordPages

# Is this the new page when we're doing an incremental compile?
def is_new_page(PageInfo, Params):
    if not Params.recompile or not cached_compilation_data_available:
        return True
    else:
        ( Corpus, PageNumber ) = Params.recompile
        return Corpus == PageInfo['corpus']['corpus'] and PageNumber == PageInfo['page']

# Make the top-level text page (holder for the real pages)
def format_hyperlinked_text_file_for_word_pages(Params):
    if Params.html_style == 'social_network':
        return False
    else:
        File = page_name_for_hyperlinked_text_file(Params)
        format_hyperlinked_text_file(File, Params)
        return File

def page_name_for_hyperlinked_text_file(Params):
    return f'{Params.word_pages_directory}/{formatted_hyperlinked_text_file_for_word_pages_short()}'

# Make the content pages
def format_main_text_files_for_word_pages(PageOrientedSplitList, PagesDir, Params):
    StartTime = time.time()
    AllErrors = []
    AllPageFiles = []
    AllPageRepresentations = []
    AllSentAudioList = []
    lara_utils.print_and_flush(f'--- Creating {len(PageOrientedSplitList)} main text pages')
    # We need to do this first so that we can put in forward links
    create_main_page_list(PageOrientedSplitList, PagesDir)
    for ( PageInfo, SplitList ) in PageOrientedSplitList:
        #print('PageInfo:')
        #lara_utils.prettyprint(PageInfo)
        FullPageName = full_page_name_for_page_info(PageInfo)
        LongFile = main_text_page_name_for_page_info_and_compiled_dir(PageInfo, PagesDir)
        PageParams = add_page_info_to_params(PageInfo, FullPageName, Params)
        #print('PageParams:')
        #lara_utils.prettyprint(PageParams)
        CustomCSSFileRepresentation = maybe_format_custom_css_file_for_page(PageParams, PageInfo)
        CustomScriptFileRepresentation = maybe_format_custom_script_file_for_page(PageParams, PageInfo)
        ( MadeNewPage, PageRepresentation, Errors, AllSentAudioFiles ) = format_main_text_file(SplitList, LongFile, FullPageName, PageParams)
        if MadeNewPage:
            AllPageFiles += [ [ key_for_page_info(PageInfo), LongFile ] ]
            AllSentAudioInfo = { 'corpus_name': Params.id,
                                 'page_name': FullPageName,
                                 'file_name': lara_play_all.base_play_all_audio_file_name_for_page(FullPageName, Params),
                                 'segment_audio_files': AllSentAudioFiles }
            AllSentAudioList += [ AllSentAudioInfo ]
            PageRepresentation['play_all'] = AllSentAudioInfo
            PageRepresentation['custom_css_file'] = CustomCSSFileRepresentation
            PageRepresentation['custom_script_file'] = CustomScriptFileRepresentation
            AllPageRepresentations += [ PageRepresentation ]
        AllErrors += Errors
    print_main_text_file_errors(AllErrors)
    print_pages_file(PagesDir, Params)
    if Params.abstract_html not in ( 'abstract_html_only', 'plain_via_abstract_html' ):
        lara_play_all.create_play_all_audio_files_if_necessary(AllSentAudioList, Params)
    if StartTime is not None: 
        lara_utils.print_and_flush_with_elapsed_time('--- Created main text files', StartTime)
    return ( AllPageFiles, AllPageRepresentations ) 

# In the key/value list of pages, the key is a pair ( <CorpusName>, <PageNumber> )
def key_for_page_info(PageInfo):
    if 'page' in PageInfo and 'corpus' in PageInfo and 'corpus' in PageInfo['corpus']:
        return ( PageInfo['corpus']['corpus'], PageInfo['page'] )
    elif 'page' in PageInfo and 'corpus' in PageInfo:
        return ( PageInfo['corpus'], PageInfo['page'] )
    elif 'page' in PageInfo:
        return ( 'corpus', PageInfo['page'] )
    else:
        lara_utils.print_and_flush(f'*** Error: unable to make PageInfo {PageInfo} into key')
        return False

def corpus_name_for_page_info(PageInfo):
    Key = key_for_page_info(PageInfo)
    return Key[0] if Key else False

# Full pathname for a main content page
def main_text_page_name_for_page_info_and_compiled_dir(PageInfo, PagesDir):
    ShortFile = formatted_main_text_file_for_word_pages_short(full_page_name_for_page_info(PageInfo))
    return f'{PagesDir}/{ShortFile}'

# Filename for main content page, derived from page info
def full_page_name_for_page_info(PageInfo):
    CorpusInfo = PageInfo['corpus']
    CorpusName = CorpusInfo['corpus'] if isinstance(CorpusInfo, dict) else CorpusInfo
    PageName = PageInfo['page']
    return full_page_name_for_corpus_and_page(CorpusName, PageName)

def full_page_name_for_corpus_and_page(CorpusName, PageName):
    #return f'{CorpusName}_{PageName}'
    return PageName if CorpusName == 'local_files' else f'{CorpusName}_{PageName}'

# Create dict and list of content pages (needed for navigation functionality)
def create_main_page_list(PageOrientedSplitList, PagesDir):
    for ( PageInfo, SplitList ) in PageOrientedSplitList:
        FullPageName = full_page_name_for_page_info(PageInfo)
        ShortFile = formatted_main_text_file_for_word_pages_short(FullPageName)
        LongFile = f'{PagesDir}/{ShortFile}'
        add_main_page_to_list(FullPageName, ShortFile, LongFile)

def add_main_page_to_list(Name, ShortPage, FullPage):
    global list_of_main_pages
    global dict_of_main_pages
    list_of_main_pages += [{'name':Name, 'short_page':ShortPage, 'full_page':FullPage}]
    dict_of_main_pages[Name] = {'short_page':ShortPage, 'full_page':FullPage}

def print_pages_file(PagesDir, Params):
    global list_of_main_pages
    AllShortPages = [ Item['short_page'] for Item in list_of_main_pages ]
    ShortFile = pages_file_for_word_pages_short()
    LongFile = f'{PagesDir}/{ShortFile}'
    lara_utils.write_json_to_file(AllShortPages, LongFile)
    lara_utils.print_and_flush(f'--- Written pages file ({len(AllShortPages)} pages) to {LongFile}')

# Add the word_audio_voice and the word_translations_on to the params if they are non-null.
# We will need them if we are doing distributed LARA
# Add the css file from the page info to the params. We will need it if we have special css files for pages
# Add the script file similarly
def add_page_info_to_params(PageInfo, PageName, Params):
    PageParams = copy.copy(Params)
    PageParams.page_name = PageName
    if 'corpus' in PageInfo and 'corpus' in PageInfo['corpus'] and not PageInfo['corpus']['corpus'] == '':
        lara_utils.add_corpus_id_tag_to_params(PageParams, PageInfo['corpus']['corpus'])
    else:
        lara_utils.add_corpus_id_tag_to_params(PageParams, 'local_files')
    if 'corpus' in PageInfo and 'word_audio_voice' in PageInfo['corpus'] and not PageInfo['corpus']['word_audio_voice'] == '':
        PageParams.preferred_voice = PageInfo['corpus']['word_audio_voice']
    if 'corpus' in PageInfo and 'word_translations_on' in PageInfo['corpus'] and not PageInfo['corpus']['word_translations_on'] == '':
        PageParams.word_translations_on = PageInfo['corpus']['word_translations_on']
    # Use the specific CSS file defined for the page if it's there
    if 'css_file' in PageInfo:
        PageParams.css_file_for_page = PageInfo['css_file']
    # Otherwise the CSS file for the corpus if that's defined
    elif 'corpus' in PageInfo and 'css_file' in PageInfo['corpus'] and not PageInfo['corpus']['css_file'] == '':
        PageParams.css_file_for_page = PageInfo['corpus']['css_file']
    if 'corpus' in PageInfo and 'script_file' in PageInfo['corpus'] and not PageInfo['corpus']['script_file'] == '':
        PageParams.script_file_for_page = PageInfo['corpus']['script_file']
    return PageParams

# Again, if we have a special css or script file for a page we need to take care of it here
def maybe_format_custom_css_file_for_page(Params, PageInfo):
    if Params.css_file_for_page != '':
        PagesDir = Params.word_pages_directory
        CSSFile = lara_html.css_file_for_page(Params)
        CorpusName = corpus_name_for_page_info(PageInfo)
        ContentString = format_custom_css_file_for_page(f'{PagesDir}/{CSSFile}', CorpusName, Params)
        return { 'file_name': Params.css_file_for_page,
                 'content': ContentString.split('\n') if isinstance(ContentString, str) else False }

def maybe_format_custom_script_file_for_page(Params, PageInfo):
    if Params.script_file_for_page != '':
        PagesDir = Params.word_pages_directory
        ScriptFile = lara_html.script_file_for_page(Params)
        CorpusName = corpus_name_for_page_info(PageInfo)
        ContentString = format_custom_script_file_for_page(f'{PagesDir}/{ScriptFile}', CorpusName, Params)
        return { 'file_name': Params.script_file_for_page,
                 'content': ContentString.split('\n') if isinstance(ContentString, str) else False }

##def format_main_text_file_for_word_pages(SplitList, PagesDir, Params):
##    FormattedFile = f'{PagesDir}/{formatted_main_text_file_for_word_pages_short()}'
##    format_main_text_file(SplitList, FormattedFile, Params)

# Make the frequency-ordered vocabulary file
def format_count_file_for_word_pages(CountFile, PagesDir, Params):
    FormattedFile = f'{PagesDir}/{formatted_count_file_for_word_pages_short()}'
    return format_count_file(CountFile, FormattedFile, Params)

# Make the alphabetically ordered vocabulary file 
def format_alphabetical_file_for_word_pages(CountFile, PagesDir, Params):
    FormattedFile = f'{PagesDir}/{formatted_alphabetical_file_for_word_pages_short()}'
    return format_alphabetical_file(CountFile, FormattedFile, Params)

# Make the alphabetically ordered vocabulary file 
def format_notes_file_for_word_pages(PagesDir, Params):
    FormattedFile = f'{PagesDir}/{formatted_notes_file_for_word_pages_short()}'
    return format_notes_file(FormattedFile, Params)

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

# --------------------------------------

# Storing vocabulary counts in a dict

word_count_info = {}
surface_word_count_info = {}

def store_vocab_counts(CountFile, Params):
    global word_count_info
    word_count_info = {}
    CountData = read_count_file(CountFile, Params)
    for (Word, Count) in CountData:
        if Count == 0:
            lara_utils.print_and_flush(f'*** Warning: zero count for "{Word}" in store_vocab_counts adjusted to 1')
            Count = 1
        word_count_info[Word] = ( Count, math.log(Count) )
    lara_utils.print_and_flush(f'--- Loaded {len(CountData)} lemma counts from {CountFile}')

def store_surface_vocab_counts(CountFile, Params):
    global surface_word_count_info
    surface_word_count_info = {}
    CountData = read_surface_count_file(CountFile, Params)
    for (Word, Count) in CountData:
        surface_word_count_info[Word] = ( Count, math.log(Count) )
    lara_utils.print_and_flush(f'--- Loaded {len(CountData)} surface word counts from {CountFile}')

def get_word_count_info(Word):
    global word_count_info
    if Word in word_count_info:
        return word_count_info[Word]
    else:
        return False

def get_surface_word_count_info(Word0):
    global surface_word_count_info
    Word = lara_translations.regularise_word(Word0)
    if Word in surface_word_count_info:
        return surface_word_count_info[Word]
    else:
        return False

# --------------------------------------

# Formatting the vocabulary files
def format_count_file(CountFile, OutFile, Params0):
    Params = adapt_params_for_count_and_alphabetical_files(Params0)
    InList = remove_punctuation_words(read_count_file(CountFile, Params0))
    TotalCount = sum([Count for (Word, Count) in InList])
    ( HTMLList, RepresentationList ) = count_list_to_formatted_count_lines(InList, TotalCount, Params)
    Header = [lara_config.get_ui_text('index_heading_rank', Params),
              lara_config.get_ui_text('index_heading_word', Params),
              lara_config.get_ui_text('index_heading_freq', Params),
              lara_config.get_ui_text('index_heading_cumul', Params)]
    if Params.abstract_html in ( 'abstract_html_only', 'plain_via_abstract_html' ):
        lara_utils.print_and_flush(f'--- Producing abstract HTML only, not creating frequency ordered index file')
    else:
        lara_html.print_lara_html_table(lara_config.get_ui_text('frequency_index', Params), Header, HTMLList, OutFile, Params)
    return RepresentationList

def format_alphabetical_file(CountFile, OutFile, Params0):
    Params = adapt_params_for_count_and_alphabetical_files(Params0)
    InList = remove_punctuation_words(read_count_file(CountFile, Params0))
    SortedInList = order_count_list_alphabetically(InList)
    ( HTMLList, RepresentationList ) = count_list_to_formatted_alphabetical_lines(SortedInList, Params)
    Header = [lara_config.get_ui_text('index_heading_word', Params),
              lara_config.get_ui_text('index_heading_freq', Params)]
    if Params.abstract_html in ( 'abstract_html_only', 'plain_via_abstract_html' ):
        lara_utils.print_and_flush(f'--- Producing abstract HTML only, not creating alphabetical index file')
    else:
        lara_html.print_lara_html_table(lara_config.get_ui_text('alphabetical_index', Params), Header, HTMLList, OutFile, Params)
    return RepresentationList

def format_notes_file(OutFile, Params0):
    if not lara_translations.notes_are_defined():
        return False
    Params = adapt_params_for_count_and_alphabetical_files(Params0)
    InList = lara_translations.lemma_and_notes_list()
    SortedInList = order_count_list_alphabetically(InList)
    ( HTMLList, RepresentationList ) = notes_list_to_formatted_notes_lines(SortedInList, Params)
    Header = [lara_config.get_ui_text('index_heading_word', Params),
              lara_config.get_ui_text('index_heading_note', Params)]
    if Params.abstract_html in ( 'abstract_html_only', 'plain_via_abstract_html' ):
        lara_utils.print_and_flush(f'--- Producing abstract HTML only, not creating notes file')
    else:
        lara_html.print_lara_html_table(lara_config.get_ui_text('notes', Params), Header, HTMLList, OutFile, Params)
    return RepresentationList

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

def order_count_list_alphabetically(InList):
    return sorted(InList, key=lambda x: x[0].lower())

def remove_punctuation_words(InList):
    return [ (Word, Count) for (Word, Count) in InList if not lara_parse_utils.is_punctuation_string(Word) ]

def count_list_to_formatted_count_lines(InList, TotalCount, Params):
    ( Cuml, I, HTMLLines, RepresentationLines ) = ( 0, 1, [], [] )
    for (Word, Count) in InList:
        ( FormattedWord, WordRepresentation, CumlPCField, Cuml ) = count_list_item_to_formatted_count_line(Word, Count, TotalCount, I, Cuml, Params)
        HTMLLines += [[ I, FormattedWord, Count, CumlPCField ]]
        if Params.abstract_html != 'plain_html_only':
            RepresentationLines += [ { 'word': WordRepresentation, 'count': Count, 'cumulative_percentage': CumlPCField } ]
        I += 1
    return ( HTMLLines, RepresentationLines )

def count_list_item_to_formatted_count_line(Word, Count, TotalCount, I, CumlIn, Params):
    CumlOut = CumlIn + Count
    CumlPC = 100.0 * CumlOut / TotalCount
    CumlPCField = '{0:.2f}%'.format(CumlPC)
    # Tries to make POS tags more readable
    Word1 = reformat_pos_tags_in_lemma(Word, Params)
    # Turns word into a link
    ( FormattedWord, WordRepresentation ) = format_line_for_word_page(Word1, Word1, [[Word1, Word]], '*no_current_word*', Params)
    return ( FormattedWord, WordRepresentation, CumlPCField, CumlOut )

def count_list_to_formatted_alphabetical_lines(InList, Params):
    ( HTMLLines, RepresentationLines ) = ( [], [] )
    for (Word, Count) in InList:
        ( FormattedWord, WordRepresentation, Count ) = count_list_item_to_formatted_alphabetical_line(Word, Count, Params)
        HTMLLines += [[ FormattedWord, Count ]]
        if Params.abstract_html != 'plain_html_only':
            RepresentationLines += [ { 'word': WordRepresentation, 'count': Count } ]
    return ( HTMLLines, RepresentationLines )

def count_list_item_to_formatted_alphabetical_line(Word, Count, Params):
    # Tries to make POS tags more readable
    Word1 = reformat_pos_tags_in_lemma(Word, Params)
    # Turns word into a link
    ( FormattedWord, WordRepresentation ) = format_line_for_word_page(Word1, Word1, [[Word1, Word]], '*no_current_word*', Params)
    return [FormattedWord, WordRepresentation, Count]

def notes_list_to_formatted_notes_lines(InList, Params):
    ( HTMLLines, RepresentationLines ) = ( [], [] )
    for (Word, Notes) in InList:
        ( FormattedWord, WordRepresentation, Note ) = notes_list_item_to_formatted_notes_line(Word, Notes, Params)
        HTMLLines += [[ FormattedWord, Note ]]
        if Params.abstract_html != 'plain_html_only':
            RepresentationLines += [ { 'word': WordRepresentation, 'note': Note } ]
    return ( HTMLLines, RepresentationLines )

def notes_list_item_to_formatted_notes_line(Word, Notes, Params):
    # Tries to make POS tags more readable
    Word1 = reformat_pos_tags_in_lemma(Word, Params)
    # Turns word into a link
    ( FormattedWord, WordRepresentation ) = format_line_for_word_page(Word1, Word1, [[Word1, Word]], '*no_current_word*', Params)
    return [FormattedWord, WordRepresentation, '\n'.join(Notes)]

# Adapt code in lara_html.word_page_header_for_word
def reformat_pos_tags_in_lemma(Word0, Params):
    #Word = lara_replace_chars.restore_reserved_chars(Word0)
    Word = Word0
    Parts = Word.split('/')
    FormattedPosText = ''
    if len(Parts) > 1 and Parts[1] != '':
        PosText = lara_postags.translate_postag(Parts[1], Params)
        if PosText != '':
            FormattedPosText = f' ({PosText})'
    return f'{Parts[0]}{FormattedPosText}'

# --------------------------------------

# Collect all the info we're going to use to generate the word pages in a dict
# Iterate through the chunks
def collect_word_page_info(SplitList, Params, Limit):
    StartTime = time.time()
    lara_utils.print_and_flush(f'--- Collecting word page info for {len(SplitList)} segments')
    ( I, Assoc, ChangedWordsAssoc ) = ( 0, initial_assoc_for_word_page_info(Params), {} )
    for Chunk in [ Chunk for Chunk in SplitList if not lara_utils.is_page_tag_chunk(Chunk) ]:
        collect_word_page_info1(Chunk, Params, Limit, Assoc, ChangedWordsAssoc)
        I += 1
        if I%500 == 0:
            lara_utils.print_and_flush_no_newline(f'({I}) ')
    if StartTime is not None: 
        lara_utils.print_and_flush_with_elapsed_time('--- Collected word page info', StartTime)
    return ( Assoc, ChangedWordsAssoc )

def collect_word_page_info_simple(SplitList, Params):
    StartTime = time.time()
    Limit = Params.max_examples_per_word_page
    LemmaOrSurface = 'lemma' if Params.word_translations_on in [ 'lemma', 'lemma_notes', 'lemma_image_dict' ] else 'surface'
    if LemmaOrSurface == 'lemma':
        store_vocab_counts(Params.count_file, Params)
    else:
        store_surface_vocab_counts(Params.surface_count_file, Params)
    lara_utils.print_and_flush(f'--- Collecting simple example info for {len(SplitList)} segments')
    ( I, Assoc ) = ( 0, {} )
    for Chunk in [ Chunk for Chunk in SplitList if not lara_utils.is_page_tag_chunk(Chunk) ]:
        collect_word_page_info_simple1(Chunk, Params, LemmaOrSurface, Limit, Assoc)
        I += 1
        if I%500 == 0:
            lara_utils.print_and_flush_no_newline(f'({I}) ')
    if StartTime is not None: 
        lara_utils.print_and_flush_with_elapsed_time(f'--- Collected simple word page info ({LemmaOrSurface})', StartTime)
    return Assoc

def initial_assoc_for_word_page_info(Params):
    return word_page_info_assoc if Params.recompile and word_page_info_assoc != {} else {}

# Collect the word page info for a chunk
# Create the example words and calculate the score
def collect_word_page_info1(Chunk, Params0, Limit, Assoc, ChangedWordsAssoc):
    ( Raw, MinimallyCleaned, AnnotatedWords0, CorpusIdTag ) = Chunk
    Params = lara_utils.add_corpus_id_tag_to_params(Params0, CorpusIdTag)
    AnnotatedWords = regularise_html_tags_and_spaces_in_annotated_words(AnnotatedWords0, Params)
    Score = score_for_example(AnnotatedWords)
    collect_word_page_info2(Raw, MinimallyCleaned, AnnotatedWords, CorpusIdTag, Score, Params, Limit, Assoc, ChangedWordsAssoc)

def collect_word_page_info_simple1(Chunk, Params0, LemmaOrSurface, Limit, Assoc):
    ( Raw, MinimallyCleaned, AnnotatedWords0, CorpusIdTag ) = Chunk
    Params = lara_utils.add_corpus_id_tag_to_params(Params0, CorpusIdTag)
    AnnotatedWords = regularise_html_tags_and_spaces_in_annotated_words(AnnotatedWords0, Params)
    Score = score_for_example(AnnotatedWords) if LemmaOrSurface == 'lemma' else surface_score_for_example(AnnotatedWords)
    collect_word_page_info_simple2(MinimallyCleaned, AnnotatedWords, CorpusIdTag, Score, Params, LemmaOrSurface, Limit, Assoc)

# Iterate down the list of words
def collect_word_page_info2(Raw, MinimallyCleaned, AnnotatedWords, CorpusIdTag, Score, Params, Limit, Assoc, ChangedWordsAssoc):
    for ( Word, Lemma0 ) in AnnotatedWords:
        Lemma = lara_translations.regularise_lemma(Lemma0)
        if Lemma != '':
            if get_word_count_info(Lemma) and not lara_parse_utils.is_punctuation_string(Lemma):
                ( FormattedLine, LineRepresentation ) = format_line_for_word_page(Raw, MinimallyCleaned, AnnotatedWords, Lemma, Params)
                Examples = Assoc[Lemma] if Lemma in Assoc else []
                if len([ Example for Example in Examples if Example[1] == FormattedLine and Example[2] == MinimallyCleaned ]) == 0:
                    PossibleNewExample = ( Score, FormattedLine, LineRepresentation, MinimallyCleaned, CorpusIdTag )
                    if len(Examples) < Limit:
                        Assoc[Lemma] = Examples + [ PossibleNewExample ]
                        ChangedWordsAssoc[Lemma] = 'changed'
                    else:
                        LowestScoringExample = lowest_scoring_example(Examples)
                        if PossibleNewExample[0] > LowestScoringExample[0]:
                            Examples.remove(LowestScoringExample)
                            Assoc[Lemma] = Examples + [ PossibleNewExample ]
                            ChangedWordsAssoc[Lemma] = 'changed'

def collect_word_page_info_simple2(MinimallyCleaned, AnnotatedWords, CorpusIdTag, Score, Params, LemmaOrSurface, Limit, Assoc):
##    for ( Word, Lemma ) in AnnotatedWords:
##        if Lemma != '':
##            Key = lara_translations.regularise_lemma(Lemma) if LemmaOrSurface == 'lemma' else lara_translations.regularise_word(Word)
    if LemmaOrSurface == 'lemma':
        Keys = [ lara_translations.regularise_lemma(Lemma) for ( Word, Lemma ) in AnnotatedWords if Lemma != '' ]
    else:
        # WordsAndIndices will be a list of ( Word, Indices ) pairs where Word may be a surface MWE
        WordsAndIndices = lara_mwe.pairs_to_words_and_indices(AnnotatedWords, Params)
        #lara_utils.print_and_flush(f'WordsAndIndices for "{MinimallyCleaned}": {WordsAndIndices}, taken from {AnnotatedWords}')
        Keys = [ lara_translations.regularise_word(Word) for ( Word, Indices, Lemma, MWE ) in WordsAndIndices ]
    for Key in Keys:
        ( Freq, Examples ) = Assoc[Key] if Key in Assoc else ( 0, [] )
        Freq1 = Freq + 1
        if len([ Example for Example in Examples if Example[1] == MinimallyCleaned ]) > 0:
            Assoc[Key] = ( Freq1, Examples )
        else:
            PossibleNewExample = ( Score, MinimallyCleaned )
            if len(Examples) < Limit:
                Assoc[Key] = ( Freq1, Examples + [ PossibleNewExample ] )
            else:
                LowestScoringExample = lowest_scoring_example(Examples)
                if PossibleNewExample[0] > LowestScoringExample[0]:
                    Examples.remove(LowestScoringExample)
                    Assoc[Key] = ( Freq1, Examples + [ PossibleNewExample ] )

def regularise_html_tags_and_spaces_in_annotated_words(AnnotatedWords, Params):
    return [ regularise_html_tags_and_spaces_in_word_lemma_pair(Word, Lemma, Params) for ( Word, Lemma) in AnnotatedWords ]

def regularise_html_tags_and_spaces_in_word_lemma_pair(Surface, Lemma, Params):
    #return  ( lara_parse_utils.remove_html_annotations_from_string(Word)[0], lara_translations.regularise_lemma(Lemma) ) if Lemma != '' else ( ' ', '' )
    if Lemma != '':
        Surface1 = lara_parse_utils.remove_html_annotations_from_string(Surface)[0]
        #Lemma1 = lara_translations.regularise_lemma(Lemma)
        Lemma1 = Lemma
    else:
        Surface1 = lara_parse_utils.remove_hashtag_comment_and_html_annotations(Surface, Params)[0]
        Lemma1 = ''
    return ( Surface1, Lemma1 )

# Other things being equal, prefer examples with common words
def score_for_example(AnnotatedWords):
    if len(AnnotatedWords) == 0:
        return 100.0
    else:
        LogScores = [ get_word_count_info(Lemma)[1] for ( Word, Lemma ) in AnnotatedWords if get_word_count_info(Lemma) ]
        return statistics.mean(LogScores) - penalty_for_short_example(AnnotatedWords) if len(LogScores) > 0 else 100.0

def surface_score_for_example(AnnotatedWords):
    if len(AnnotatedWords) == 0:
        return 100.0
    else:
        LogScores = [ get_surface_word_count_info(Word)[1] for ( Word, Lemma ) in AnnotatedWords if get_surface_word_count_info(Word) ]
        return statistics.mean(LogScores) - penalty_for_short_example(AnnotatedWords) if len(LogScores) > 0 else 100.0

# But avoid examples that are too short
def penalty_for_short_example(AnnotatedWords):
    Cutoff = 5
    PenaltyFactor = 1
    if len(AnnotatedWords) < Cutoff:
        return ( Cutoff - len(AnnotatedWords) ) * PenaltyFactor
    else:
        return 0.0

def lowest_scoring_example(Examples):
    return sorted(Examples, key=lambda x: x[0])[0]
	
# --------------------------------------

# Information collected during the compilation that's cached for next time

# Navigation
list_of_main_pages = []

# Navigation
dict_of_main_pages = {}

# Back-pointer arrows in examples
indexes_for_chunks = {}

# Table of contents
toc_for_html = [] # [ ( "plain text", Tag, Page, Segment ), ... ]

# Structure holding examples used to generate word pages
word_page_info_assoc = {}

# Zero all this information
def init_compilation_data():
    global list_of_main_pages
    global dict_of_main_pages
    global indexes_for_chunks
    global toc_for_html
    global word_page_info_assoc
    list_of_main_pages = []
    dict_of_main_pages = {}
    indexes_for_chunks = {}
    toc_for_html = []
    word_page_info_assoc = {}
    cached_compilation_data_available = False

# Cache it for next time
def cache_compilation_data(Params):
    DataToCache = { 'list_of_main_pages': list_of_main_pages,
                    'dict_of_main_pages': dict_of_main_pages,
                    'indexes_for_chunks': indexes_for_chunks,
                    'toc_for_html': toc_for_html,
                    'word_page_info_assoc': word_page_info_assoc }
    CacheFile = Params.compile_cache_file
    if not CacheFile:
        lara_utils.print_and_flush(f'*** Error: compile_cache_file not defined')
        return False
    lara_utils.save_data_to_pickled_gzipped_file(DataToCache, CacheFile)

# Restore from last run
def restore_cached_compilation_data(Params):
    global cached_compilation_data_available 
    global list_of_main_pages
    global dict_of_main_pages
    global indexes_for_chunks
    global toc_for_html
    global word_page_info_assoc
    cached_compilation_data_available = False
    CacheFile = Params.compile_cache_file
    if not CacheFile:
        lara_utils.print_and_flush(f'*** Error: compile_cache_file not defined')
        return False
    CachedData = lara_utils.get_data_from_pickled_gzipped_file(CacheFile)
    if not CachedData:
        lara_utils.print_and_flush(f'*** Error: unable to read cache file {CacheFile}')
        return False
    if not 'list_of_main_pages' in CachedData or \
       not 'dict_of_main_pages' in CachedData or \
       not 'indexes_for_chunks' in CachedData or \
       not 'toc_for_html' in CachedData or \
       not 'word_page_info_assoc' in CachedData:
        lara_utils.print_and_flush(f'*** Error: did not find expected data in cache file {CacheFile}')
        return False
    list_of_main_pages = CachedData['list_of_main_pages']
    dict_of_main_pages = CachedData['dict_of_main_pages']
    indexes_for_chunks = CachedData['indexes_for_chunks']
    toc_for_html = CachedData['toc_for_html']
    word_page_info_assoc = CachedData['word_page_info_assoc']
    cached_compilation_data_available = True

# First page for navigation
def short_name_of_first_main_file():
    global list_of_main_pages
    return list_of_main_pages[0]['short_page']

# Table of contents file
def short_name_of_toc_file():
    return '_toc_.html'

# Preceding file for navigation
def short_name_of_preceding_main_file(PageName):
    global list_of_main_pages
    for i in range(1, len(list_of_main_pages)):
        if list_of_main_pages[i]['name'] == PageName:
            return list_of_main_pages[i-1]['short_page']
    return False

# Following file for navigation
def short_name_of_following_main_file(PageName):
    global list_of_main_pages
    for i in range(0, len(list_of_main_pages)-1):
        if list_of_main_pages[i]['name'] == PageName:
            return list_of_main_pages[i+1]['short_page']
    return False

# Store the index for the minimally cleaned string (in fact, not the chunk)
def store_index_for_chunk(Index, Chunk):
    global indexes_for_chunks
    indexes_for_chunks[Chunk] = Index

# Find the index for the minimally cleaned string (in fact, not the chunk)
def index_for_chunk(Chunk):
    global indexes_for_chunks
    if Chunk in indexes_for_chunks:
        return indexes_for_chunks[Chunk]
    else:
        return False

# Store a line for the table of contents
def store_toc_for_html( Index, Anchor, HtmlText, Params ):
    Match = re.search("<(h[12])>(.*)", HtmlText, flags=re.DOTALL)
    if Match is not None:
        # replace <tag..> and "speaker" symbol with blank
        PlainText = re.sub( "<[^>]+>", " ", Match.group(2))
        PlainText = re.sub( lara_extra_info.loudspeaker_icon_html_code(Params), " ", PlainText )
        # replace segment translation charcter with null if there is one defined
        if Params.segment_translation_character != '':
            PlainText = re.sub( lara_utils.str_to_html_str(Params.segment_translation_character), "", PlainText )
        # replace sequence of white space with single blank
        PlainText = re.sub( r"\s+", " ", PlainText)
        toc_for_html.append( ( PlainText, Match.group(1), Index[0], Index[1], Anchor ) )

# Make the top-level file
def format_hyperlinked_text_file(File, Params):
    if Params.abstract_html in ( 'abstract_html_only', 'plain_via_abstract_html' ):
        lara_utils.print_and_flush(f'--- Producing abstract HTML only, not creating top-level text file')
        return
    FirstMainFile = short_name_of_first_main_file()
    HeaderLines = lara_html.hyperlinked_text_file_header(FirstMainFile, Params)
    ClosingLines = lara_html.hyperlinked_text_file_closing(Params)
    lara_utils.write_unicode_text_file('\n'.join(HeaderLines + ClosingLines), File)
    lara_utils.print_and_flush(f'--- Written hyperlinked text file {File}')

# Make the table of contents file
def format_toc_file(File, Params):
    Lines = lara_html.toc_lines_intro( lara_config.get_ui_text("table_of_contents", Params), Params ) \
        + [ f"<{Tag} class='toc'><a target='{lara_utils.split_screen_pane_name_for_main_text_screen(Params)}' href='{formatted_main_text_file_for_word_pages_short(PageName)}#{anchor_for_index((PageName, Segment), Params)}'><b>{lara_extra_info.arrow_html_code(Params)}</b> {PlainText}</{Tag}>"
            for ( PlainText, Tag, PageName, Segment, Anchor ) in toc_for_html ] \
        + lara_html.toc_lines_closing()
    if Params.abstract_html in ( 'abstract_html_only', 'plain_via_abstract_html' ):
        lara_utils.print_and_flush(f'--- Producing abstract HTML only, not creating table of contents file')
    else:
        lara_utils.write_unicode_text_file("\n".join( Lines ), File)
        lara_utils.print_and_flush(f'--- Written table of contents file {File}')
    if Params.abstract_html != 'plain_html_only':
        Representation = [ { 'plain_text': PlainText, 'tag': Tag, 'corpus_name': Params.id, 'page_name': PageName, 'anchor': Anchor } \
                           for ( PlainText, Tag, PageName, Segment, Anchor ) in toc_for_html ]
        return Representation
    else:
        return []

# Make a main content file
def format_main_text_file(SplitList, File, PageName, Params):
    if Params.recompile and cached_compilation_data_available and lara_utils.file_exists(File):
        return ( False, [], [], False )
    PrecedingMainFile = short_name_of_preceding_main_file(PageName)
    FollowingMainFile = short_name_of_following_main_file(PageName)
    FirstMainFile = short_name_of_first_main_file()
    HeaderLines = lara_html.main_text_file_header(PrecedingMainFile, FollowingMainFile, FirstMainFile, Params)
    ( BodyLines, LineRepresentations, Errors, AllSentAudioFiles ) = format_hyperlinked_text_file_lines(SplitList, PageName, Params)
    ClosingLines = lara_html.main_text_file_closing(PrecedingMainFile, FollowingMainFile, Params)
    if not Params.abstract_html in ( 'abstract_html_only', 'plain_via_abstract_html' ):
        lara_utils.write_unicode_text_file('\n'.join(HeaderLines + BodyLines + ClosingLines), File)
        lara_utils.print_and_flush(f'--- Written main text file {File}')
    PageRepresentation = make_page_representation(PageName, LineRepresentations, Params)
    return ( True, PageRepresentation, Errors, AllSentAudioFiles )

def make_page_representation(PageName, SegmentRepresentations, Params):
    return { 'page_name': PageName,
             'corpus_name': Params.id,
             'segments': SegmentRepresentations }

# Write out the default css file
def format_default_css_file(File, Params):
    CssText = lara_html.default_styles(Params)
    if Params.abstract_html in ( 'abstract_html_only', 'plain_via_abstract_html' ):
        lara_utils.print_and_flush(f'--- Producing abstract HTML only, not creating default css file')
    else:
        lara_utils.write_unicode_text_file(CssText, File)
        lara_utils.print_and_flush(f'--- Written css file {File}')
    return CssText.split('\n')

# Write out a custom css file, if we have defined one for a page
def format_custom_css_file(File, Params):
    #lara_utils.prettyprint(['--- format_custom_css_file', File, Params])
    if Params.css_file != '' and Params.corpus != '':
        #SourceFile = Params.css_file
        SourceFile = f'{lara_utils.directory_for_pathname(Params.corpus)}/{Params.css_file}'
        #Result = lara_utils.copy_file( SourceFile, File )
        Result = lara_images.process_img_tags_in_css_or_script_file(SourceFile, File, Params)
        if not Result:
            lara_utils.print_and_flush(f'*** Error: unable to copy file: {SourceFile} to {File}')
            return False
        lara_utils.print_and_flush(f'--- Copied custom css file {SourceFile} to {File}')
        return Result.split('\n')

# Write out the default script file
def format_default_script_file(File, Params):
    MainScriptText = lara_html.default_script(Params)
    AudioTrackingData = lara_html.get_audio_tracking_data(Params)
    AudioTrackingScriptText = lara_html.audio_tracking_scriptfunction(AudioTrackingData)
    ScriptText = '\n'.join( (MainScriptText, AudioTrackingScriptText ) )
    if Params.abstract_html in ( 'abstract_html_only', 'plain_via_abstract_html' ):
        lara_utils.print_and_flush(f'--- Producing abstract HTML only, not creating default script file')
    else:
        lara_utils.write_unicode_text_file(ScriptText, File)
        lara_utils.print_and_flush(f'--- Written script file {File}')
    return ( MainScriptText.split('\n'), AudioTrackingData)

# Write out a custom script file, if we have defined one for a page
def format_custom_script_file(File, Params):
    if Params.script_file != '' and Params.corpus != '':
        #SourceFile = Params.script_file
        SourceFile = f'{lara_utils.directory_for_pathname(Params.corpus)}/{Params.script_file}'
        #Result = lara_utils.copy_file( SourceFile, File )
        FileContent = lara_images.process_img_tags_in_css_or_script_file(SourceFile, File, Params)
        if not FileContent:
            lara_utils.print_and_flush(f'*** Error: unable to install script file {SourceFile} to {File}')
            return False
        lara_utils.print_and_flush(f'--- Written custom script file {File}')
        return FileContent.split('\n')

## Often we will use the same style file for many pages, so only copy it once.
## We create a new target directory for each compile, so there should be no danger of
## finding an old version still lying around.
def format_custom_css_file_for_page(File, CorpusName, Params):
    #lara_utils.prettyprint(['--- format_custom_css_file_for_page', File, CorpusName, Params])
    if Params.css_file_for_page != '' and not lara_utils.file_exists(File):
        if lara_download_metadata.downloaded_css_file_name(Params, CorpusName, Params.css_file_for_page):
            SourceFile = lara_download_metadata.downloaded_css_file_name(Params, CorpusName, Params.css_file_for_page)
        elif Params.corpus and not Params.corpus == '':
            SourceFile = f'{lara_utils.directory_for_pathname(Params.corpus)}/{Params.css_file_for_page}'
        else:
            lara_utils.print_and_flush(f'*** Error: unable to find CSS file {File}')
            return False
        #Result = lara_utils.copy_file( SourceFile, File )
        FileContent = lara_images.process_img_tags_in_css_or_script_file(SourceFile, File, Params)
        if not FileContent:
            lara_utils.print_and_flush(f'*** Error: unable to copy file: {SourceFile} to {File}')
            return False
        lara_utils.print_and_flush(f'--- Written custom css file for page {File}')
        return FileContent
    else:
        return False

## Similarly for script files
def format_custom_script_file_for_page(File, CorpusName, Params):
    if Params.script_file_for_page != '' and not lara_utils.file_exists(File):
        if lara_download_metadata.downloaded_script_file_name(Params, CorpusName, Params.script_file_for_page):
            SourceFile = lara_download_metadata.downloaded_script_file_name(Params, CorpusName, Params.script_file_for_page)
        else:
            lara_utils.print_and_flush(f'*** Error: unable to find script file {File}')
            return False
        FileContent = lara_images.process_img_tags_in_css_or_script_file(SourceFile, File, Params)
        if not Result:
            lara_utils.print_and_flush(f'*** Error: unable to copy file: {SourceFile} to {File}')
        lara_utils.print_and_flush(f'--- Written script file for page {File}')
        return FileContent
    else:
        return False

# Sort all the errors and warnings and print them separately
def print_main_text_file_errors(ErrorsAndWarnings):
    if len(ErrorsAndWarnings) > 0:
        UniqueErrorsAndWarnings = lara_utils.remove_duplicates(ErrorsAndWarnings)
        ( UniqueErrors, UniqueWarnings ) = separate_errors_and_warnings(UniqueErrorsAndWarnings)
        if len(UniqueErrors) > 0:
            lara_utils.print_and_flush(f'{len(UniqueErrors)} errors:')
            for Error in UniqueErrors:
                lara_utils.print_and_flush(Error)
        if len(UniqueWarnings) > 0:
            lara_utils.print_and_flush(f'{len(UniqueWarnings)} warnings:')
            for Warning in UniqueWarnings:
                lara_utils.print_and_flush(Warning)

def separate_errors_and_warnings(ErrorsAndWarnings):
    Errors = [ Str for Str in ErrorsAndWarnings if (Str.lower()).find('error') >= 0 ]
    Warnings = [ Str for Str in ErrorsAndWarnings if (Str.lower()).find('error') < 0 ]
    return ( Errors, Warnings )

# Format the lines in a main context page
def format_hyperlinked_text_file_lines(SplitList, PageName, Params):
    ( HyperlinkedChunkStrings, AllRepresentations, Errors, AllSentAudioFiles ) = format_hyperlinked_text_file_lines1(SplitList, PageName, Params)
    HyperlinkedChunkString = ''.join(HyperlinkedChunkStrings)
    HyperlinkedLines = HyperlinkedChunkString.split('\n')
    HTMLLines = hyperlinked_lines_to_html_lines(HyperlinkedLines)
    return ( HTMLLines, AllRepresentations, Errors, AllSentAudioFiles )

# Iterate through the chunks in the list
def format_hyperlinked_text_file_lines1(SplitList, PageName, Params):
    ( N, TextSoFar, AllStrings, AllRepresentations, AllErrors, AllSentAudioFiles, ThisPageAudioFileUsedAll ) = ( 1, [], [], [], [], [], False )
    for Chunk in SplitList:
        Context = lara_audio.text_so_far_to_context(TextSoFar)
        ( String, Representation, Errors, SentAudioFile, ThisPageAudioFileUsed ) = format_hyperlinked_text_file_line(Chunk, Context, Params, PageName, N)
        #lara_utils.print_and_flush(f'--- ( {String}, {Representation}, {Errors}, {SentAudioFile}, {ThisPageAudioFileUsed} ) = format_hyperlinked_text_file_line({Chunk}, {Context}, Params, {PageName}, {N})')
        TextSoFar += Chunk[1].split()
        AllStrings += [String]
        AllRepresentations += [Representation]
        AllErrors += Errors
        if SentAudioFile != False:
            AllSentAudioFiles += [ SentAudioFile ]
        if ThisPageAudioFileUsed != False:
            ThisPageAudioFileUsedAll = True
        N += 1
    if ThisPageAudioFileUsedAll == False:
        AllSentAudioFiles = False
    return ( AllStrings, AllRepresentations, AllErrors, AllSentAudioFiles )

# Format a single chunk
# Format the words, then insert the formatted versions into the raw text.
def format_hyperlinked_text_file_line(Chunk, Context, Params0, PageName, N):
    (Raw, MinimallyCleaned, AnnotatedWords0, CorpusIdTag) = Chunk
    AnnotatedWords = [ (Surface, Lemma) for (Surface, Lemma) in AnnotatedWords0 if Lemma != '' ]
    Params = lara_utils.add_corpus_id_tag_to_params(Params0, CorpusIdTag)
    #lara_translations.maybe_add_word_token_translations_to_params(Params, AnnotatedWords)
    lara_translations.maybe_add_word_type_or_token_translations_to_params(Params, AnnotatedWords)
    lara_audio.maybe_add_word_breakpoints_to_params(Params, MinimallyCleaned, Context)
    Translation = lara_extra_info.get_translation_for_line_or_add_to_errors(MinimallyCleaned, Params)[0]
    Index = [PageName, N]
    Anchor = anchor_for_index(Index, Params)
    # We use AnnotatedWords0 since the prosodic boundaries are marked in the non-content items
    lara_forced_alignment.maybe_add_prosodic_boundary_list_to_params(Params, Raw, AnnotatedWords0)
    #( AnnotatedWords1, ThisPageAudioFileUsed ) = process_img_and_audio_tags_for_annotated_words(AnnotatedWords0, MinimallyCleaned, Params)
    ( WordsAndHyperlinkedVersions, WordRepresentations, ThisPageAudioFileUsed ) = words_and_hyperlinked_versions_in_list(AnnotatedWords0, MinimallyCleaned, Params)
    #lara_utils.print_and_flush(f'--- ( {WordsAndHyperlinkedVersions}, {WordRepresentations}, {ThisPageAudioFileUsed} ) = words_and_hyperlinked_versions_in_list({AnnotatedWords0}, {MinimallyCleaned}, Params)')
    #HyperlinkedRaw0 = add_hyperlinking_to_raw_text(AnnotatedWords0, Params, WordsAndHyperlinkedVersions)
    HyperlinkedRaw0 = add_hyperlinking_to_raw_text(WordsAndHyperlinkedVersions, Params)
    #lara_utils.print_and_flush(f'--- {HyperlinkedRaw0} = add_hyperlinking_to_raw_text({WordsAndHyperlinkedVersions}, Params)') 
    #HyperlinkedRaw1 = remove_intra_word_separators_in_string(HyperlinkedRaw0)
    HyperlinkedRaw1 = lara_replace_chars.restore_reserved_chars(HyperlinkedRaw0)
    HyperlinkedRaw2 = lara_forced_alignment.remove_prosodic_phrase_boundaries_from_string(HyperlinkedRaw1)
    HyperlinkedRaw = remove_comment_markers(HyperlinkedRaw2)
    ( HyperlinkedRawWithAudio, Errors ) = lara_extra_info.add_audio_and_translation_to_line(HyperlinkedRaw, MinimallyCleaned, Context, Params)
    HyperlinkedText = add_anchor_to_line(HyperlinkedRawWithAudio, Index, Params)
    store_toc_for_html( Index, Anchor, HyperlinkedRawWithAudio, Params )
    store_index_for_chunk(Index, MinimallyCleaned)
    SentAudioFile0 = lara_audio.get_audio_url_for_chunk_or_word(MinimallyCleaned, Context, 'segments', Params)
    SentAudioFile = lara_utils.base_name_for_pathname(SentAudioFile0) if SentAudioFile0 != False else False
    SegmentRepresentation = make_segment_representation(MinimallyCleaned, WordRepresentations, Translation, SentAudioFile, Anchor, PageName, Params)
    return ( HyperlinkedText, SegmentRepresentation, Errors, SentAudioFile, ThisPageAudioFileUsed )

def make_segment_representation(MinimallyCleaned, WordRepresentations, Translation, AudioFile, Anchor, PageName, Params):
    if Params.abstract_html == 'plain_html_only':
        return False
    return { 'plain_text': MinimallyCleaned,
             'words': WordRepresentations,
             'translation': Translation,
             'audio': { 'file':AudioFile, 'corpus_name': Params.id },
             'anchor': Anchor,
             'corpus_name': Params.id,
             'page': PageName }
        

# Format examples for the word pages: use code for formatting main text, slightly customised
# Mark the head word on the current page in red and don't use color to mark frequencies
def format_line_for_word_page(Raw, MinimallyCleaned, AnnotatedWordsWithSpaces, CurrentWord, Params):
    AnnotatedWords = [ ( Surface, Lemma ) for ( Surface, Lemma ) in AnnotatedWordsWithSpaces if Lemma != '' ]
    lara_translations.maybe_add_word_type_or_token_translations_to_params(Params, AnnotatedWords)
    lara_audio.maybe_add_word_breakpoints_to_params(Params, MinimallyCleaned, '')
    # We use AnnotatedWordsWithSpaces since the prosodic boundaries are marked in the non-content items
    lara_forced_alignment.maybe_add_prosodic_boundary_list_to_params(Params, Raw, AnnotatedWordsWithSpaces)
    #lara_utils.print_and_flush(f'lara_forced_alignment.maybe_add_prosodic_boundary_list_to_params(Params, "{MinimallyCleaned}", {AnnotatedWordsWithSpaces})')
    ( WordHyperlinkedWordPairs, WordRepresentations ) = words_and_hyperlinked_versions_in_list_for_word_page(AnnotatedWordsWithSpaces, CurrentWord, Params)
    #Line0 = add_hyperlinking_to_raw_text(AnnotatedWordsWithSpaces, Params, WordHyperlinkedWordPairs)
    Line0 = add_hyperlinking_to_raw_text(WordHyperlinkedWordPairs, Params)
    #Line1 = lara_parse_utils.remove_hashtag_annotations_from_string(Line0) if Params.keep_comments != 'yes' else Line0
    Line1 = lara_forced_alignment.remove_prosodic_phrase_boundaries_from_string(Line0)
    if Params.abstract_html in ( 'abstract_html_only', 'plain_via_abstract_html' ):
        ExampleText = ''
    else:
        ExampleText = lara_replace_chars.restore_reserved_chars(lara_parse_utils.regularise_spaces(Line1))
    return ( ExampleText, WordRepresentations )

def remove_comment_markers(Str):
    return Str.replace('/*', '').replace('*/', '')

# Format the words
##def words_and_hyperlinked_versions_in_list(AnnotatedWords, Params):
##    return [ ( Word, format_hyperlinked_text_file_line_word(Word, Lemma, Params) ) for ( Word, Lemma ) in AnnotatedWords
##             if not lara_parse_utils.is_punctuation_string(Lemma) ]

def words_and_hyperlinked_versions_in_list(WordLemmaPairs, MinimallyCleaned, Params):
    # Index is to count the non-filler words, since they're the ones that have associated translations
    ( Index, ThisPageAudioFileUsed ) = ( 0, False )
    ( WordAnnotatedWordPairs, WordRepresentations ) = ( [], [] )
    for ( Word, Lemma ) in WordLemmaPairs:
        ( AnnotatedWord, WordRepresentation, ThisPageAudioFileUsedCurrent ) = format_hyperlinked_text_file_line_word(Word, Lemma, MinimallyCleaned, Index, Params)
        #lara_utils.print_and_flush(f'( {AnnotatedWord}, {WordRepresentation}, {ThisPageAudioFileUsedCurrent} ) = format_hyperlinked_text_file_line_word({Word}, {Lemma}, {MinimallyCleaned}, {Index}, Params)')

        WordAnnotatedWordPairs += [ ( Word, AnnotatedWord ) ]
        WordRepresentations += [ WordRepresentation ]
        ThisPageAudioFileUsed = ThisPageAudioFileUsed or ThisPageAudioFileUsedCurrent
        if Lemma != '':
            Index += 1
    return ( WordAnnotatedWordPairs, WordRepresentations, ThisPageAudioFileUsed )

def words_and_hyperlinked_versions_in_list_for_word_page(WordLemmaPairs, CurrentWord, Params):
    # Index is to count the non-filler words, since they're the ones that have associated translations
    Index = 0
    ( WordAnnotatedWordPairs, WordRepresentations ) = ( [], [] )
    for ( Word, Lemma ) in WordLemmaPairs:
        ( AnnotatedWord, WordRepresentation ) = format_hyperlinked_text_file_line_word_for_word_page(Word, Lemma, Index, CurrentWord, Params)
        WordAnnotatedWordPairs += [ ( Word, AnnotatedWord ) ]
        WordRepresentations += [ WordRepresentation ]
        if Lemma != '':
            Index += 1
    return ( WordAnnotatedWordPairs, WordRepresentations )

def format_hyperlinked_text_file_line_word(Word, Lemma0, MinimallyCleaned, Index, Params):
    if is_multimedia_tag(Word):
        ( AnnotatedWord, ThisPageAudioFileUsed ) = process_img_and_audio_tags_in_string(Word, MinimallyCleaned, Params)
        WordRepresentation = multimedia_tag_to_representation(Word, Params)
        return ( AnnotatedWord, WordRepresentation, ThisPageAudioFileUsed )
    if Lemma0 == '':
        CleanedUpWord = clean_up_string_for_word_representation(Word)
        ThisPageAudioFileUsed = False
        return ( Word, { 'word': CleanedUpWord }, ThisPageAudioFileUsed )
    Lemma = lara_translations.regularise_lemma(Lemma0)
    ( FileName, Count ) = file_name_for_word(Lemma)
    Params.word_token_index = Index
    Translation = lara_translations.translation_for_word_or_lemma(Word, Lemma, Params)
    Colour = colour_for_main_text_word(Word, Lemma, Count, Params)
    WordContext = '*main_text_word*'
    WordRepresentation = word_to_word_representation(Word, Lemma, Translation, WordContext, Params)
    AnnotatedWord = add_translation_audio_and_colour_annotations_to_word(Word, Lemma, Translation, Colour, WordContext, Params)
    ThisPageAudioFileUsed = False
    return ( AnnotatedWord, WordRepresentation, ThisPageAudioFileUsed )

##def is_multimedia_tag(Str):
##    return lara_images.is_img_tag(Str) or lara_audio.is_audio_tag(Str)
##
##def multimedia_tag_to_representation(Str):
    
def format_hyperlinked_text_file_line_word_for_word_page(Word, Lemma0, Index, CurrentWord, Params):
    if Lemma0 == '':
        CleanedUpWord = clean_up_string_for_word_representation(Word)
        return ( Word, { 'word': CleanedUpWord, 'lemma': Lemma0 } )
    Lemma = lara_translations.regularise_lemma(Lemma0)
    Params.word_token_index = Index
    Translation = lara_translations.translation_for_word_or_lemma(Word, Lemma, Params)
    ( Colour, WordContext ) = ( 'red', '*current_word_on_word_page*' ) if Lemma == CurrentWord else ( 'black', '*non_current_word_on_word_page*' )
    WordRepresentation = word_to_word_representation(Word, Lemma, Translation, WordContext, Params)
    AnnotatedWord =  add_translation_audio_and_colour_annotations_to_word(Word, Lemma, Translation, Colour, WordContext, Params)
    return ( AnnotatedWord, WordRepresentation )

def word_to_word_representation(Word, Lemma, Translation, WordContext, Params):
    if Params.abstract_html == 'plain_html_only':
        return False
    AudioFile0 = lara_extra_info.audio_url_for_word_and_word_context(Word, WordContext, Params)
    AudioFile = lara_utils.base_name_for_pathname(AudioFile0) if AudioFile0 != False else False
    CleanedUpWord = clean_up_string_for_word_representation(Word)
    return { 'word': CleanedUpWord,
             'lemma': Lemma,
             'translation': Translation,
             'audio': { 'file':AudioFile, 'corpus_name': Params.id } }

def clean_up_string_for_word_representation(Str):
    Str1 = lara_replace_chars.restore_reserved_chars(Str)
    Str2 = lara_forced_alignment.remove_prosodic_phrase_boundaries_from_string(Str1)
    #Str3 = remove_comment_markers(Str2)
    Str3 = Str2
    return Str3

def add_translation_audio_and_colour_annotations_to_word(Word, Lemma, Translation, Colour, WordContext, Params):
    global word_annotation_caching
    global word_to_annotated_word
    if not word_annotation_caching:
        return add_translation_audio_and_colour_annotations_to_word1(Word, Lemma, Translation, Colour, Params)
    # We need to include Params.segment_audio_for_word_audio and Params.word_token_index in the Key, since it may determine the audio.
    # Really we should include the index too.
    # We include Params.audio_on_click because words may have different audio in the main text and in the
    # concordance pages
    Key = ( Word, Lemma, Translation, Params.segment_audio_for_word_audio, Params.word_token_index, Colour, Params.audio_on_click )
    if Key in word_to_annotated_word:
        #lara_utils.print_and_flush(f'--- Found for "{Key}": "{word_to_annotated_word[Key]}"')
        return word_to_annotated_word[Key]
    else:
        Result = add_translation_audio_and_colour_annotations_to_word1(Word, Lemma, Translation, Colour, WordContext, Params)
        if Params.switch_off_caching != 'yes':
            word_to_annotated_word[Key] = Result
            #lara_utils.print_and_flush(f'--- Saved for "{Key}": "{word_to_annotated_word[Key]}"')
        return Result

def add_translation_audio_and_colour_annotations_to_word1(Word, Lemma, Translation, Colour, WordContext, Params):
    if Params.plain_text == 'yes':
        return Word
    AnnotatedWord = lara_extra_info.maybe_add_translation_and_or_audio_mouseovers_to_word(Word, Lemma, Translation, WordContext, Params)
    ColouredWord = add_colour_to_word(AnnotatedWord, Colour)
    ( FileName, Count ) = file_name_for_word(Lemma)
    ScreenName = lara_utils.split_screen_pane_name_for_word_page_screen(Params)
    if WordContext == '*current_word_on_word_page*':
        Result = ColouredWord
    elif Params.html_style != 'social_network':
        Result = f'<a href="{FileName}" target="{ScreenName}">{ColouredWord}</a>'
    # <span onclick="load_word_concordance('Hello_world_editedvocabpages/word_hello.html');">(...)</span>
    else:
        Result = f'<span onclick="load_word_concordance(\'{Params.relative_compiled_directory}/{FileName}\');">{ColouredWord}</span>'
    #Result = f'<a href="{FileName}" target="{ScreenName}">{ColouredWord}</a>' if not WordContext == '*current_word_on_word_page*' else ColouredWord
    #Result = f'<a href="{FileName}" target="{ScreenName}">{ColouredWord}</a>'
    return Result

word_annotation_caching = True
#word_annotation_caching = False

word_to_annotated_word = {}

def init_word_to_annotated_word():
    global word_to_annotated_word
    word_to_annotated_word = {}

def add_colour_to_word(Word, Colour):
    return f'<span class="{Colour}">{Word}</span>' if Colour != 'black' else Word

## If we aren't using colour for frequencies, we might want to use it to mark audio words or notes or MWEs
def colour_for_main_text_word(Word, Lemma, Count, Params):
    if Params.audio_words_in_colour != 'no' and Params.audio_mouseover != 'no' and Params.coloured_words == 'no' and \
       lara_audio.get_audio_url_for_word(Word, Params):
        return Params.audio_words_in_colour
    elif Params.note_words_in_colour != 'no' and Params.coloured_words == 'no' and len(lara_translations.all_notes_for_word(Lemma)) > 0:
        return 'red'
    elif Params.image_dict_words_in_colour != 'no' and Params.coloured_words == 'no' and len(lara_translations.all_images_for_word(Lemma)) > 0:
        return 'red'
    elif Params.translated_words_in_colour != 'no' and Params.coloured_words == 'no' and \
         lara_translations.word_has_translation(Word, Lemma, Params) != False:
        return 'red'
    elif Params.mwe_words_in_colour != 'no' and Params.coloured_words == 'no' and lemma_looks_like_multiword(Lemma, Params):
        return 'red'
    elif Params.coloured_words == 'no':
        return 'black'
    else:
        return colour_id_for_count(Count)

def lemma_looks_like_multiword(Lemma, Params):
    return ' ' in Lemma or \
           looks_like_an_italian_reflexive(Lemma, Params) or \
           looks_like_a_french_reflexive(Lemma, Params)

# This is a hack, need a better way to identify MWEs with no spaces

def looks_like_an_italian_reflexive(Lemma, Params):
    return Params.language == 'italian' and Lemma.endswith('rsi')

def looks_like_a_french_reflexive(Lemma, Params):
    return Params.language == 'french' and Lemma.startswith("s'")

def colour_id_for_count(Count):
    if Count <= 1:
        return 'red'
    elif 2 <= Count and Count <= 3:
        return 'green'
    elif 4 <= Count and Count <= 5:
        return 'blue'
    else:
        return 'black'

##def process_img_and_audio_tags_for_annotated_words(AnnotatedWords, MinimallyCleaned, Params):
##    ( AnnotatedWords1, ThisPageAudioFileUsed ) = ( [], False )
##    for ( Surface, Lemma ) in AnnotatedWords:
##        ( Surface1, ThisPageAudioFileUsed ) = process_img_and_audio_tags_in_string(Surface, MinimallyCleaned, Params) 
##        AnnotatedWords1 += [ ( Surface1, Lemma ) ]
##    return ( AnnotatedWords1, ThisPageAudioFileUsed )

# Iterate down the list of words we're going to substitute
##def add_hyperlinking_to_raw_text(AnnotatedWords, Params, WordHyperlinkedWordPairs):
##    ( HyperlinkedStr, I ) = ( '', 0 )
##    for ( Surface, Lemma ) in AnnotatedWords:
##        # If Lemma == '', then it's a piece of filler text. Just add it.
##        if Lemma == '':
##            #HyperlinkedStr += Surface
##            PossiblyModifiedSurface = WordHyperlinkedWordPairs[I][0]
##            HyperlinkedStr += PossiblyModifiedSurface
##        # Otherwise, it's a content word, so it will be in the WordHyperlinkedWordPairs
##        else:
##            HyperlinkedSurface = WordHyperlinkedWordPairs[I][1]
##            HyperlinkedStr += HyperlinkedSurface
##        I += 1
##    return HyperlinkedStr

def add_hyperlinking_to_raw_text(WordsAndHyperlinkedVersions, Params):
    return ''.join([ Item[1] for Item in WordsAndHyperlinkedVersions ])

def is_multimedia_tag(Str):
    return lara_images.is_img_tag(Str) or lara_audio.is_audio_tag(Str)

def multimedia_tag_to_representation(Str, Params):
    if not is_multimedia_tag(Str):
        lara_utils.print_and_flush(f'*** Error: bad call to multimedia_tag_to_representation: "{Str}" is not a multimedia tag')
        return False
    if lara_images.is_img_tag(Str):
        Representation = lara_images.img_tag_to_representation(Str)
    elif lara_audio.is_audio_tag(Str):
        Representation = lara_audio.audio_tag_to_representation(Str)
    Representation['corpus_name'] = Params.id
    return Representation

# Adjust the img and audio tags
def process_img_and_audio_tags_in_string(Str, MinimallyCleaned, Params):
    # Should perhaps perform a more careful check?
    if Str.find('<') < 0:
        return ( Str, False )
    Str1 = lara_images.process_img_tags_in_string(Str, Params)[0]
    ( Str2, Errors, ThisPageAudioFileUsed ) = lara_audio.process_audio_tags_in_string(Str1, MinimallyCleaned, Params)
    return ( Str2, ThisPageAudioFileUsed )

# Add an anchor. Put it in a place where highlighting will work well            
def add_anchor_to_line(Line, Index, Params):
    #return f'<a id="{anchor_for_index(Index)}"></a>{Line}'
    return insert_before_first_real_text(f'<a id="{anchor_for_index(Index, Params)}"></a>', Line)

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
def add_context_link_to_line(Line, Index, Params):
    MainTextPage = formatted_main_text_file_for_word_pages_short(Index[0])
    Anchor = anchor_for_index(Index, Params)
    ScreenName = lara_utils.split_screen_pane_name_for_main_text_screen(Params)
    if Params.html_style != 'social_network':
        return f'<a href="{MainTextPage}#{Anchor}" target="{ScreenName}"><b>{lara_extra_info.arrow_html_code(Params)}</b></a> {Line}'
    else:
        return f'<span onclick="load_main_text(\'{Params.relative_compiled_directory}/{MainTextPage}#{Anchor}\');"><b>&larr;</b></span> {Line}'
        #return f'<span href="{MainTextPage}#{Anchor}" target="{ScreenName}"><b>{lara_extra_info.arrow_html_code(Params)}</b></a> {Line}'

# Target for back-arrows in examples
def anchor_for_index(Index, Params):
    ( PageName, N ) = Index
    return f'{Params.id}_page_{PageName}_segment_{N}'

# Turn lines into HTML by adding <p> tags
def hyperlinked_lines_to_html_lines(HyperlinkedLines):
    return [ word_page_line_to_html_line(HyperlinkedLine) for HyperlinkedLine in HyperlinkedLines ]

def word_page_line_to_html_line(HyperlinkedLine):
    if HyperlinkedLine.isspace() or HyperlinkedLine == '':
        HyperlinkedLine1 = '&nbsp;'
    else:
        HyperlinkedLine1 = HyperlinkedLine
    if line_starts_with_tag_not_needing_paragraph(HyperlinkedLine1):
        return HyperlinkedLine1
    else:
        return f'<p>{HyperlinkedLine1}</p>'

tags_not_needing_paragraph = ['<h1', '<h2',
                              '<img', '<video' '<audio',
                              '<table', '</table>',
                              '<tr', '<td', '</tr', '</td']

# Don't wrap a <p> around headers, images, embedded audio and table elements
def line_starts_with_tag_not_needing_paragraph(Line):
    Line1 = Line.lstrip().lower()
    for Tag in tags_not_needing_paragraph:
        if Line1.startswith(Tag):
            return True
    return False

# --------------------------------------

# Name of word page file for a given word
def file_name_for_word(Word0):
    Word = lara_mwe.strip_off_mwe_part_tag_returning_lemma_and_length(Word0)[0]
    wordCount = get_word_count_info(Word)
    if not wordCount:
        #lara_utils.print_and_flush(f'*** Error: unable to find word count info for "{Word}"')
        #return False
        lara_utils.print_and_flush(f'*** Warning: unable to find word count info for "{Word}"')
        ( Count, LogCount) = ( 1, 0.0 )
    else:
        ( Count, LogCount) = wordCount
    Word1 = lara_split_and_clean.clean_up_word_for_files(Word)
    return ( f'word_{Word1}.html', Count )

def full_file_name_for_word(Word, MultimediaDir):
    ( FileName, Count ) = file_name_for_word(Word)
    return f'{MultimediaDir}/{FileName}'

# --------------------------------------

# Make all the word pages out of the dict created by collect_word_page_info
def make_word_pages1(Assoc, ChangedWordsAssoc, MultimediaDir, Params):
    StartTime = time.time()
    lara_utils.print_and_flush(f'\n--- Printing word pages for {len(ChangedWordsAssoc.keys())} words')
    return make_word_pages2(Assoc, ChangedWordsAssoc, MultimediaDir, Params)
    #lara_utils.print_and_flush(f'\n--- Created word pages in {MultimediaDir}')
    if StartTime is not None:
        lara_utils.print_and_flush('\n')
        lara_utils.print_and_flush_with_elapsed_time(f'--- Created word pages in {MultimediaDir}', StartTime)

# Iterate through the assoc. Print an update every 500 pages
def make_word_pages2(Assoc, ChangedWordsAssoc, MultimediaDir, Params):
    ( I, RepresentationsAssoc ) = ( 0, {} )
    for Word in ChangedWordsAssoc:
        PageRepresentation = make_word_page(Word, Assoc[Word], MultimediaDir, Params)
        RepresentationsAssoc[Word] = PageRepresentation
        I += 1
        if I%500 == 0:
            lara_utils.print_and_flush_no_newline(f'({I}) ')
    return RepresentationsAssoc

# Making one word page: make lines, then convert to HTML as with main content pages
def make_word_page(Word, Examples, MultimediaDir, Params):
    ( HTMLLines, Representation ) = word_page_lines(Word, Examples, Params)
    if not Params.abstract_html in ( 'abstract_html_only', 'plain_via_abstract_html' ):
        FileName = full_file_name_for_word(Word, MultimediaDir)
        lara_utils.write_unicode_text_file('\n'.join(HTMLLines), FileName)
    return Representation

# Add header and footer into, format examples which constitute main content
def word_page_lines(Word, Examples, Params):
    Intro = lara_html.word_page_lines_header(Word, Params)
    ( ExtraInfoTopLines, Images ) = lara_extra_info.word_page_lines_extra_info_top(Word, Params)
    ImageLines = [ lara_extra_info.format_image_for_extra_info(Image, Params) for Image in Images ]
    ( Examples, ExamplesRepresentations0 ) = word_page_lines_to_html_lines1(Examples, Params)
    ExamplesRepresentations = lara_utils.remove_duplicates(ExamplesRepresentations0)
    ExtraInfoBottom = lara_extra_info.word_page_lines_extra_info_bottom(Word, Params)
    Closing = lara_html.word_page_lines_closing(formatted_count_file_for_word_pages_short(),
                                                formatted_alphabetical_file_for_word_pages_short(),
                                                formatted_notes_file_for_word_pages_short(),
                                                Params)
    HTMLLines = Intro + ImageLines + ExtraInfoTopLines + Examples + ExtraInfoBottom + Closing
    if Params.abstract_html != 'plain_html_only':
        ImageRepresentations = [ { 'corpus_name': Params.id, 'file': Image, 'multimedia': 'img' } for Image in Images ]
        Representation = { 'lemma': Word,
                           'examples': ExamplesRepresentations,
                           'extra_info': ExtraInfoTopLines,
                           'images': ImageRepresentations }
    else:
        Representation = False
    return ( HTMLLines, Representation )

def word_page_lines_to_html_lines1(Examples, Params):
    LinesAndRepresentations = [ example_to_html_line(Example, Params) for Example in Examples ]
    Lines = [ Item[0] for Item in LinesAndRepresentations ]
    Representations = [ Item[1] for Item in LinesAndRepresentations ]
    return ( Lines, Representations )

# Add audio for the whole line + back-arrow pointing to context in main text
def example_to_html_line(Example, Params0):
    #lara_utils.print_and_flush(f'--- Example: {Example}')
    ( Score, FormattedLine, WordsRepresentation, MinimallyCleaned, CorpusIdTag ) = Example
    Params = lara_utils.add_corpus_id_tag_to_params(Params0, CorpusIdTag)
    if not Params.abstract_html in ( 'abstract_html_only', 'plain_via_abstract_html' ):
        Example = add_audio_and_link_to_line(FormattedLine, MinimallyCleaned, Params)
        FormattedLine = word_page_line_to_html_line(Example)
    else:
        FormattedLine = ''
    if Params.abstract_html != 'plain_html_only':
        LineRepresentation = add_audio_translation_and_link_to_words_representation(WordsRepresentation, MinimallyCleaned, Params)
    else:
        LineRepresentation = False
    #lara_utils.print_and_flush(f'--- FormattedLine: {FormattedLine}')
    return ( FormattedLine, LineRepresentation )

def add_audio_and_link_to_line(FormattedLine, MinimallyCleaned, Params):
    Index = index_for_chunk(MinimallyCleaned)
    # Hard to add a context here.
    ( FormattedLineWithAudio, Errors) = lara_extra_info.add_audio_and_translation_to_line(FormattedLine, MinimallyCleaned, '', Params)
    return add_context_link_to_line(FormattedLineWithAudio, Index, Params)

def add_audio_translation_and_link_to_words_representation(WordsRepresentations, MinimallyCleaned, Params):
    Index = index_for_chunk(MinimallyCleaned)
    Anchor = anchor_for_index(Index, Params)
##    Translation = lara_extra_info.get_translation_for_line_or_add_to_errors(MinimallyCleaned, Params)[0]
##    SentAudioFile0 = lara_audio.get_audio_url_for_chunk_or_word(MinimallyCleaned, '', 'segments', Params)
##    SentAudioFile = lara_utils.base_name_for_pathname(SentAudioFile0) if SentAudioFile0 != False else False
##    return make_segment_representation(MinimallyCleaned, WordsRepresentations, Translation, SentAudioFile, Anchor, Params)
    return Anchor
