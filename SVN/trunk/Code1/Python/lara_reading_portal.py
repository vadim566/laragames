
import lara_top
import lara
import lara_config
import lara_download_metadata
import lara_split_and_clean
import lara_utils
import time
import webbrowser

# OPERATIONS FOR READER PORTAL INTERFACE


##reader1_english_animal_farm_portal_full:
##	${PYTHON3} ${LARA}/Code/Python/lara_run_for_portal.py compile_reading_history
##                   ${LARA}/Content/reader1_english/distributed_config_animal_farm_portal.json
##                   ${LARA}/Content/reader1_english/reply1.json
##
def test_animal_farm_portal_full():
    compile_reading_history('$LARA/Content/reader1_english/distributed_config_animal_farm_portal.json',
                            '$LARA/Content/reader1_english/reply1.json')

##reader1_english_animal_farm_portal_next:
##	${PYTHON3} ${LARA}/Code/Python/lara_run_for_portal.py compile_next_page_in_history animal_farm_portal english_portal
##                 ${LARA}/Content/reader1_english/distributed_config_animal_farm_portal.json
##                 ${LARA}/Content/reader1_english/reply2.json
def test_animal_farm_portal_next():
    compile_next_page_in_history_and_write('animal_farm_portal',
                                           'english_portal',
                                           '$LARA/Content/reader1_english/distributed_config_animal_farm_portal.json',
                                           '$LARA/Content/reader1_english/reply2.json')

##reader1_english_animal_farm_portal_next2:
##	${PYTHON3} ${LARA}/Code/Python/lara_run_for_portal.py compile_next_page_in_history animal_farm_portal english_portal
##                 ${LARA}/Content/reader1_english/distributed_config_animal_farm_portal2.json
##                 ${LARA}/Content/reader1_english/reply2.json
def test_animal_farm_portal_next2():
    compile_next_page_in_history_and_write('animal_farm_portal',
                                           'english_portal',
                                           '$LARA/Content/reader1_english/distributed_config_animal_farm_portal2.json',
                                           '$LARA/Content/reader1_english/reply3.json')

# --------------------------------------------------------------

def tmp_dir_for_portal(Params):
    return f'{Params.working_tmp_directory}/portal_files'

def page_name_cache_file(Params):
    return f'{tmp_dir_for_portal(Params)}/page_name_cache.json'

# --------------------------------------------------------------

def clean_distributed_cache_data(ConfigFile):
    lara_top.delete_metadata_directory(ConfigFile)
    delete_page_name_cache_file(ConfigFile)

def delete_page_name_cache_file(ConfigFile):
    Params = lara_config.read_lara_distributed_config_file(ConfigFile)
    lara_utils.delete_file_if_it_exists(page_name_cache_file(Params))

# --------------------------------------------------------------

# TOP LEVEL

# Compile the whole reading history without using any cached data
def compile_reading_history(ConfigFile, ReplyFile):
    StartTime = time.time()
    Params = lara_config.read_lara_distributed_config_file(ConfigFile)
    if not Params:
        return False
    Result = lara_top.compile_lara_reading_history_for_portal(Params)
    if StartTime is not None: 
        lara_utils.print_and_flush_with_elapsed_time('--- Done', StartTime)
    lara_utils.write_json_to_file(Result, ReplyFile)
    lara_utils.print_and_flush(f'--- Written pathnames of HTML pages to {ReplyFile}')

# Get a displayable HTML page for the next page in a resource and write it out in JSON form to ReplyFile
# Use an incremental compile to create the new page
def compile_next_page_in_history_and_write(ResourceName, LanguageResourceName, ConfigFile, ReplyFile):
    StartTime = time.time()
    Result = update_reading_history_with_next_page(ResourceName, LanguageResourceName, ConfigFile)
    if StartTime is not None: 
        lara_utils.print_and_flush_with_elapsed_time('--- Done', StartTime)
    lara_utils.write_json_to_file(Result, ReplyFile)
    lara_utils.print_and_flush(f'--- Written pathnames of HTML pages to {ReplyFile}')

# Get a list of page names for a resource and write it out in JSON form to ReplyFile
def get_page_names_for_resource_and_write(ResourceName, ConfigFile, ReplyFile):
    Pages = get_page_names_for_resource(ResourceName, ConfigFile)
    lara_utils.write_json_to_file(Pages, ReplyFile)
    lara_utils.print_and_flush(f'--- Written list of pages to {ReplyFile}')

# Get the supported voices and L1s for a resource
def get_voices_and_l1s_for_resource_and_write(ResourceId, ConfigFile, ReplyFile):
    Params = lara_config.read_lara_distributed_config_file(ConfigFile)
    if not Params or Params.resource_file == '':
        Data = False
    else:
        Data = lara_download_metadata.get_voices_and_l1s_for_resource(ResourceId, Params.resource_file)
    lara_utils.write_json_to_file(Data, ReplyFile)
    lara_utils.print_and_flush(f'--- Written voicea and L1s to {ReplyFile}')

# Get the supported voices and L1s for all resources in a resource file
def get_voices_and_l1s_for_resource_file_and_write(ConfigFile, ReplyFile):
    Params = lara_config.read_lara_distributed_config_file(ConfigFile)
    if not Params or Params.resource_file == '':
        Data = False
    else:
        Data = lara_download_metadata.get_voices_and_l1s_for_resource_file(Params.resource_file)
    lara_utils.write_json_to_file(Data, ReplyFile)
    lara_utils.print_and_flush(f'--- Written voicea and L1s to {ReplyFile}')
 
# --------------------------------------------------------------

#   Get list of page names for resource (normally page numbers)
#   FOR DATABASE VERSION: write to DB. One insert for each page.

def get_page_names_for_resource(ResourceName, ConfigFile):
    Params = lara_config.read_lara_distributed_config_file(ConfigFile)
    if not Params:
        return False
    return get_page_names_for_resource_and_params(ResourceName, Params)

def get_page_names_for_resource_and_params(ResourceName, Params):
    CachedPages = get_cached_page_names_for_resource(ResourceName, Params)
    if CachedPages:
        return CachedPages
    tmp_dir = tmp_dir_for_portal(Params)
    lara_utils.create_directory_if_it_doesnt_exist(tmp_dir)
    AllResourceData = read_resources_file(Params)
    if not AllResourceData:
        lara_utils.print_and_flush(f'*** Error: resources file not defined')
        return False
    if not ResourceName in AllResourceData:
        lara_utils.print_and_flush(f'*** Error: unknown resource {ResourceName}')
        return False
    URL = AllResourceData[ResourceName][0]
    Type = 'language' if AllResourceData[ResourceName][1] == 'LanguageResource' else 'corpus'
    ConfigData = lara_download_metadata.download_config(URL, ( Type, ResourceName, 'config' ), tmp_dir, False, Params)
    CorpusData = lara_download_metadata.download_corpus(URL, ( Type, ResourceName, 'corpus' ), tmp_dir, False, Params)
    if not ConfigData or len(ConfigData) == 0 or not CorpusData or len(CorpusData) == 0:
        lara_utils.print_and_flush(f'--- Unable to find config and corpus data for {ResourceName}')
        return False
    ( ResourceConfigURL, ResourceConfigFile ) = ( ConfigData[0][3], ConfigData[0][4] )
    ( ResourceCorpusURL, ResourceCorpusFile ) = ( CorpusData[0][3], CorpusData[0][4] )
    ResourceParams = lara_config.read_lara_local_config_file_dont_check_directories(ResourceConfigFile)
    ( PageOrientedSplitList0, Trace ) = lara_split_and_clean.clean_lara_file_main(ResourceCorpusFile, ResourceParams)
    PageOrientedSplitList = lara_split_and_clean.add_tags_to_chunks(PageOrientedSplitList0, ResourceName)
    Pages = [ { 'page_number': PageInfo['page'],
                'html_file': lara.main_text_page_name_for_page_info_and_compiled_dir(PageInfo, Params.compiled_directory),
                'base_file': lara.main_text_page_name_for_page_info_and_compiled_dir(PageInfo, Params.compiled_directory).split('/')[-1]
                }
              for ( PageInfo, Chunks ) in PageOrientedSplitList ]
    cache_page_names_for_resource(ResourceName, Pages, Params)
    lara_utils.print_and_flush(f'--- Found {len(Pages)} pages')
    return Pages

#    Update reading history for user and language with next page from resource
#    Recompiles all relevant pages (in first version, recompiles everything)
#    We use caching to do this efficiently

def update_reading_history_with_next_page(ResourceName, LanguageResourceName, ConfigFile):
    Params = lara_config.read_lara_distributed_config_file(ConfigFile)
    if not Params:
        return False
    NewPage = update_reading_history_with_next_page_in_params(ResourceName, LanguageResourceName, Params)
    if NewPage:
        Result = lara_top.recompile_lara_reading_history_for_portal(Params, NewPage)
    else:
        Result = False
        lara_utils.print_and_flush(f'*** Error: unable to find new page in "{ResourceName}"')
    return Result

def update_reading_history_with_next_page_in_params(ResourceName, LanguageResourceName, Params):
    ReadingHistory = Params.reading_history
    NewPageNumber = update_reading_history_list_with_next_page(ReadingHistory, ResourceName, LanguageResourceName, Params)
    if not NewPageNumber:
        return False
    return ( ResourceName, NewPageNumber )

def update_reading_history_list_with_next_page(ReadingHistory, ResourceName, LanguageResourceName, Params):
    PagesAndHTMLPages = get_page_names_for_resource_and_params(ResourceName, Params)
    if not PagesAndHTMLPages:
        lara_utils.print_and_flush(f'*** Error: unable to find list of pages for {ResourceName}')
        return False
    ValidPages = [ Item['page_number'] for Item in PagesAndHTMLPages ]
    ( I, N ) = ( 0, len(ReadingHistory) )
    while True:
        if I >= N:
            ReadingHistory += [[ResourceName, LanguageResourceName, [1, 1]]]
            return 1
        else:
            Item = ReadingHistory[I]
            if not isinstance(Item, list) or len(Item) != 3:
                return False
            (ThisResource, SomeLanguageResourceName, Range) = Item
            if ThisResource == ResourceName:
                if Range == 'all':
                    lara_utils.print_and_flush(f'*** Error: at end of {ResourceName}, unable to get next page')
                    return False
                if not well_formed_real_range(Range):
                    lara_utils.print_and_flush(f'*** Error: invalid range for {ResourceName}, {str(Range)}')
                    return False
                NewPageNumber = Range[1]+1
                if not NewPageNumber in ValidPages:
                    lara_utils.print_and_flush(f'*** Error: at end of {ResourceName}, unable to get next page')
                    return False
                ReadingHistory[I] = [ThisResource, LanguageResourceName, [Range[0], NewPageNumber]]
                return NewPageNumber
            else:
                I += 1

def well_formed_real_range(Range):
    return isinstance(Range, list) and len(Range) == 2 and type(Range[0]) == int and type(Range[1]) == int

#    Get HTML page for user, language, resource, page
def get_distributed_lara_content_page(ResourceName, Page, Params):
    CompiledDir = lara_top.lara_compiled_dir('word_pages_directory', Params)
    FullPageName = lara.full_page_name_for_corpus_and_page(ResourceName, Page)
    PageFile = f'{lara.formatted_main_text_file_for_word_pages_short(FullPageName)}'
    if not lara_utils.file_exists(f'{CompiledDir}/{PageFile}'):
        lara_utils.print_and_flush(f'*** Warning: page {Page} for {ResourceName} not found')
        return False
    lara_utils.print_and_flush(f'--- Found page {Page} for {ResourceName}')
    return PageFile

#    Get HTML top-level page for user and language
def get_distributed_lara_top_level_page(Params):
    CompiledDir = lara_top.lara_compiled_dir('word_pages_directory', Params)
    PageFile = f'{CompiledDir}/{lara.formatted_hyperlinked_text_file_for_word_pages_short()}'
    if not lara_utils.file_exists(PageFile):
        lara_utils.print_and_flush(f'*** Warning: top-level page file for {Params.id} not found')
        return False
    lara_utils.print_and_flush(f'--- found top-level page file for {Params.id}')
    return PageFile

def read_resources_file(Params):
    resources_file = Params.resource_file
    return lara_utils.read_json_file(resources_file) if lara_utils.file_exists(resources_file) else {}

def cache_page_names_for_resource(ResourceName, Pages, Params):
    cache_file = page_name_cache_file(Params)
    CacheData = lara_utils.read_json_file(cache_file) if lara_utils.file_exists(cache_file) else {}
    CacheData[ResourceName] = Pages
    lara_utils.write_json_to_file(CacheData, cache_file)
    lara_utils.print_and_flush(f'--- Updated {cache_file} with pages for {ResourceName}')

def get_cached_page_names_for_resource(ResourceName, Params):
    cache_file = page_name_cache_file(Params)
    CacheData = lara_utils.read_json_file(cache_file) if lara_utils.file_exists(cache_file) else {}
    if ResourceName in CacheData:
        lara_utils.print_and_flush(f'--- Retrieved cached page names from {cache_file}')
        return CacheData[ResourceName]
    else:
        return False

def current_config_data(ReaderId, L2, DefaultConfigFile):
    if not get_reader_data_and_resources_files(DefaultConfigFile):
        return False
    return lara_config.config_data_for_reading_history(resources_file, reader_data_file, DefaultConfigFile, ReaderId, L2)
    
