
import lara_top
import lara_reading_portal
import lara_import_export
import lara_config
import lara_split_and_clean
import lara_utils
import time

def run_test1():
    Items = [ { 'config_file': '$LARA/Content/lorem_ipsum/corpus/local_config.json' },
              { 'config_file': '$LARA/Content/mary_had_a_little_lamb/corpus/mary_had_a_little_lamb.json' },
              { 'config_file': '$LARA/Content/peter_rabbit/corpus/local_config.json' }
             ]
    run_lara_test(Items, 'resources_and_word_pages')
              

def run_test2():
    Items  = [   { 'config_file': '$LARA/Content/lorem_ipsum/corpus/local_config.json' },
                 { 'config_file': '$LARA/Content/mary_had_a_little_lamb/corpus/mary_had_a_little_lamb.json' },
                 { 'config_file': '$LARA/Content/peter_rabbit/corpus/local_config.json' },
                 { 'config_file': '$LARA/Content/hyakumankai_ikita_neko/corpus/local_config.json' },
                 { 'config_file': '$LARA/Content/hur_gick_det_sen/corpus/local_config.json' },
                 { 'config_file': '$LARA/Content/alice_in_wonderland/corpus/local_config.json' },
                 { 'config_file': '$LARA/Content/tina_fer_i_fri/corpus/local_config.json' },
                 { 'config_file': '$LARA/Content/ungaretti/corpus/local_config.json' },
                 { 'config_file': '$LARA/Content/dante/corpus/local_config.json' },
                 { 'config_file': '$LARA/Content/revivalistics/corpus/local_config.json' },
                 { 'config_file': '$LARA/Content/EbneSina/corpus/local_config.json' },
                 { 'config_file': '$LARA/Content/the_boy_who_cried_wolf/corpus/local_config.json' },
                 { 'config_file': '$LARA/Content/Arash/corpus/local_config.json' },
                 { 'config_file': '$LARA/Content/bozboz_ghandi/corpus/local_config.json' },
                 { 'config_file': '$LARA/Content/molana/corpus/local_config.json' },
                 { 'config_file': '$LARA/Content/le_petit_prince_small/corpus/local_config.json' },
                 { 'config_file': '$LARA/Content/texs_french_course/corpus/local_config.json' },
                 { 'config_file': '$LARA/Content/edward_lear/corpus/local_config.json' },
                 { 'config_file': '$LARA/Content/ogden_nash/corpus/local_config.json' },
                 { 'config_file': '$LARA/Content/litli_prinsinn/corpus/local_config.json' },
                 { 'config_file': '$LARA/Content/barngarla_alphabet/corpus/local_config.json' },
                 { 'config_file': '$LARA/Content/wilhelmbusch/corpus/wilhelmbusch.json' },
                 { 'config_file': '$LARA/Content/the_rime_of_the_ancient_mariner/corpus/local_config.json' },
                 { 'config_file': '$LARA/Content/animal_farm/corpus/local_config.json' },
                 { 'config_file': '$LARA/Content/le_chien_jaune/corpus/local_config.json' },
                 { 'config_file': '$LARA/Content/kallocain/corpus/local_config.json' },
                 { 'config_file': '$LARA/Content/the_conversation/corpus/local_config.json' },
                 { 'config_file': '$LARA/Content/the_conversation_french/corpus/local_config.json' }
             ]
    run_lara_test(Items, 'resources_and_word_pages')

def run_test3():
    Items = [{ 'config_file': '$LARA/Content/mary_had_a_little_lamb/corpus/mary_had_a_little_lamb.json' }
             ]
    run_lara_test(Items, 'tagging')

def run_test4():
    Items = [{ 'config_file': '$LARA/Content/reader1_english/distributed_config.json',
               'corpus_id': 'alice_in_wonderland',
               'language_resource_id': 'english_geneva' }
             ]
    run_lara_test(Items, 'distributed')

def run_test5():
    Items = [ { 'config_file': '$LARA/Content/lorem_ipsum/corpus/local_config.json' },
              { 'config_file': '$LARA/Content/mary_had_a_little_lamb/corpus/mary_had_a_little_lamb.json' }
             ]
    run_lara_test(Items, 'export_import')

def run_lara_test_from_list_in_file(MetadataFile, TestType):
    Items = lara_utils.read_json_file(MetadataFile)
    if not Items:
        lara_utils.print_and_flush('*** Error: unable to read list of test items from {MetadataFile}')
        return False
    for Item in Items:
        if not valid_offline_test_item(Item, TestType):
            return False
    run_lara_test(Items, TestType)

def valid_offline_test_item(Item, TestType):
    if not isinstance(Item, dict):
        lara_utils.print_and_flush(f'*** Error: offline test item not a dict: {Item}')
        return False
    if not 'config_file' in Item:
        lara_utils.print_and_flush(f'*** Error: offline test item does not define a config file: {Item}')
        return False
    File = Item['config_file']
    if not lara_utils.file_exists(File):
        lara_utils.print_and_flush(f'*** Error: config file not found: {File}')
        return False
    if TestType == 'distributed' and ( not 'corpus_id' in Item or not 'language_resource_id' in Item ):
        lara_utils.print_and_flush(f'*** Error: distributed offline test item must define "corpus_id" and "language_resource_id": {Item}')
        return False
    return True

def run_lara_test(Items, TestType):
    RecentResults = recent_results_pairs()
    StartTime = time.time()
    lara_utils.print_and_flush(f'--- Running test with {len(Items)} texts\n')
    Results = {}
    for Item in Items:
        run_single_lara_test(Item, TestType, Results, RecentResults)
    print_result_summary(Results)
    if StartTime is not None: 
        lara_utils.print_and_flush_with_elapsed_time('--- Done', StartTime)

def run_single_lara_test(Item, TestType, Results, RecentResults):
    lara_utils.print_and_flush(f'\n==========================================================\n')
    lara_utils.print_and_flush(f"--- Running test ({TestType}) for {Item['config_file']}\n")
    StartTime = time.time()
    if TestType != 'distributed':
        Params = lara_config.read_lara_local_config_file(Item['config_file'])
    else:
        Params = lara_config.read_lara_distributed_config_file(Item['config_file'])
    if TestType == 'resources_and_word_pages':
        run_resources_and_word_pages(Item['config_file'], Results, RecentResults)
    elif TestType == 'tagging':
        run_tagging_and_resources(Item['config_file'], Results, RecentResults)
    elif TestType == 'distributed':
        run_distributed(Item['config_file'], Item['corpus_id'], Item['language_resource_id'], Results, RecentResults)        
    # Not yet implemented
    elif TestType == 'export_import':
        run_export_import_resources_and_word_pages(Item['config_file'], Results, RecentResults)
    # Not yet implemented
    elif TestType == 'add_metadata':
        run_add_metadata(Item['config_file'], Results, RecentResults)
    EndTime = time.time()
    mark_time_taken(Results, StartTime, EndTime, Params)
    mark_comparison_with_previous_results(Results, RecentResults, Item['config_file'], Params, TestType)

def run_resources_and_word_pages(ConfigFile, Results, RecentResults):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if not Params:
        mark_bad_config_file(Results, ConfigFile)
        return
    ResourcesOK = run_resources_step(ConfigFile, Params, Results)
    if ResourcesOK:
        run_word_pages_step(ConfigFile, Params, Results)

def run_tagging_and_resources(ConfigFile, Results, RecentResults):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if not Params:
        mark_bad_config_file(Results, ConfigFile)
        return
    TaggingOK = run_tagging_step(ConfigFile, Params, Results)
    if TaggingOK:
        run_resources_step_on_tagged_file(ConfigFile, Params, Results)

def run_distributed(ConfigFile, CorpusId, LanguageResourceId, Results, RecentResults):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if not Params:
        mark_bad_config_file(Results, ConfigFile)
        return
    FullDistributedOK = run_full_distributed_step(ConfigFile, Params, Results)
    if FullDistributedOK:
        run_distributed_next_page_step(ConfigFile, CorpusId, LanguageResourceId, Params, Results)

def run_export_import_resources_and_word_pages(ConfigFile, Results, RecentResults):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if not Params:
        mark_bad_config_file(Results, ConfigFile)
        return
    TmpZipfile = '$LARA/tmp/tmp_export_zipfile.zip'
    TmpImportDir = '$LARA/tmp/tmp_import_dir'
    lara_utils.delete_file_if_it_exists(TmpZipfile)
    lara_utils.delete_directory_if_it_exists_try_n_times(3, TmpImportDir)
    if lara_utils.file_exists(TmpZipfile):
        lara_utils.print_and_flush(f'*** Error: unable to delete old zipfile {TmpZipfile}')
        return False
    if lara_utils.directory_exists(TmpImportDir):
        lara_utils.print_and_flush(f'*** Error: unable to delete old import directory {TmpImportDir}')
        return False
    ExportOK = run_export_step(ConfigFile, TmpZipfile, Params, Results, RecentResults)
    if not ExportOK:
        return False
    ImportOK = run_import_step(ConfigFile, TmpZipfile, TmpImportDir, Params, Results, RecentResults)
    if not ImportOK:
        return False
    ImportedConfigFile = f'{TmpImportDir}/corpus/local_config.json'
    AddTmp = add_tmp_suffix_to_id_name_in_config_file(ImportedConfigFile)
    if not AddTmp:
        lara_utils.print_and_flush(f'*** Error: unable to adjust id in {ImportedConfigFile}')
        return False
    run_resources_and_word_pages(ImportedConfigFile, Results, RecentResults)

def add_tmp_suffix_to_id_name_in_config_file(ConfigFile):
    Content = lara_utils.read_json_file(ConfigFile)
    if not Content or not isinstance(Content, dict) or not 'id' in Content:
        return False
    Content['id'] = add_tmp_suffix(Content['id'])
    lara_utils.write_json_to_file(Content, ConfigFile)
    lara_utils.print_and_flush(f'--- Adjusted id in {ConfigFile}')
    return True

def run_tagging_step(ConfigFile, Params, Results):
    UntaggedFile = Params.untagged_corpus
    TaggedFile = Params.tagged_corpus
    if UntaggedFile == '' or TaggedFile == '':
        mark_bad_tagging_step(Results, Params)
        return False
    lara_utils.delete_file_if_it_exists(TaggedFile)
    try:
        lara_top.treetag_untagged_corpus(ConfigFile)
    except:
        mark_bad_tagging_step(Results, Params)
        return False
    if not lara_utils.file_exists(TaggedFile):
        mark_bad_tagging_step(Results, Params)
        return False
    return True

def run_resources_step(ConfigFile, Params, Results):
    SplitFile = lara_top.lara_tmp_file('split', Params)
    SplitMWEFile = lara_top.lara_tmp_file('split_mwe', Params)
    lara_utils.delete_file_if_it_exists(SplitFile)
    lara_utils.delete_file_if_it_exists(SplitMWEFile)
    try:
        lara_top.compile_lara_local_resources(ConfigFile)
    except:
        mark_bad_resources_step(Results, Params)
        return False
    if not lara_utils.file_exists(SplitFile):
        mark_bad_resources_step(Results, Params)
        return False
    return True

def run_resources_step_on_tagged_file(ConfigFile, Params, Results):
    SplitFile = lara_top.lara_tmp_file('tagged_split', Params)
    lara_utils.delete_file_if_it_exists(SplitFile)
    try:
        lara_top.compile_lara_local_clean_on_tagged_file(Params)
    except:
        mark_bad_resources_step(Results, Params)
        return False
    if not lara_utils.file_exists(SplitFile):
        mark_bad_resources_step(Results, Params)
        return False
    mark_good_tagged_resources_result(Results, Params)
    return True

def run_word_pages_step(ConfigFile, Params, Results):
    try:
        lara_top.compile_lara_local_word_pages(ConfigFile)
    except:
        mark_bad_word_pages_step(Results, Params)
        return False
    if not files_in_word_pages_directory(Params):
        mark_bad_word_pages_step(Results, Params)
        return False
    mark_good_word_pages_result(Results, Params)
    return True

def run_full_distributed_step(ConfigFile, Params, Results):
    StartTime = time.time()
    try:
        lara_top.compile_lara_reading_history_for_portal(Params)
    except:
        mark_bad_full_distributed_step(Results, Params)
        return False
    if not files_in_word_pages_directory(Params):
        mark_bad_full_distributed_step(Results, Params)
        return False
    EndTime = time.time()
    mark_good_full_distributed_step(Results, Params)
    mark_time_taken_for_full_distributed_step(Results, StartTime, EndTime, Params)
    return True

def run_distributed_next_page_step(ConfigFile, CorpusId, LanguageResourceName, Params, Results):
    lara_utils.print_and_flush(f'\n-----------------------------')
    lara_utils.print_and_flush(f'--- Starting next page step\n')
    StartTime = time.time()
    try:
        lara_reading_portal.update_reading_history_with_next_page(CorpusId, LanguageResourceName, ConfigFile)
    except:
        mark_bad_next_page_step(Results, Params)
        return False
    if not files_in_word_pages_directory(Params):
        mark_bad_next_page_step(Results, Params)
        return False
    mark_good_next_page_step(Results, Params)
    EndTime = time.time()
    mark_time_taken_for_next_page_step(Results, StartTime, EndTime, Params)
    return True

def run_export_step(ConfigFile, TmpZipfile, Params, Results, RecentResults):
    lara_utils.print_and_flush(f'\n-----------------------------')
    lara_utils.print_and_flush(f'--- Starting export step\n')
    try:
        lara_import_export.make_export_zipfile(ConfigFile, TmpZipfile)
    except:
        mark_bad_export_step(Results, Params)
        lara_utils.print_and_flush(f'*** Error: export step failed')
        return False
    if not lara_utils.file_exists(TmpZipfile):
        lara_utils.print_and_flush(f'*** Error: export step failed')
        mark_bad_export_step(Results, Params)
        return False
    return True

def run_import_step(ConfigFile, TmpZipfile, TmpImportDir, Params, Results, RecentResults):
    lara_utils.print_and_flush(f'\n-----------------------------')
    lara_utils.print_and_flush(f'--- Starting import step\n')
    try:
        lara_import_export.import_zipfile(TmpZipfile, TmpImportDir, '$LARA/Content', ConfigFile)
    except:
        mark_bad_import_step(Results, Params)
        lara_utils.print_and_flush(f'*** Error: import step failed')
        return False
    if not lara_utils.directory_exists(TmpImportDir):
        lara_utils.print_and_flush(f'*** Error: import step failed')
        mark_bad_import_step(Results, Params)
        return False
    return True

def mark_bad_config_file(Results, ConfigFile):
    Results[ConfigFile] = 'bad_config_file'

def mark_bad_resources_step(Results, Params):
    mark_normal_data(Results, Params, 'result', 'bad_resources_step')

def mark_bad_word_pages_step(Results, Params):
    mark_normal_data(Results, Params, 'result', 'bad_word_pages_step')

def mark_bad_tagging_step(Results, Params):
    mark_normal_data(Results, Params, 'result', 'bad_tagging_step')

def mark_bad_full_distributed_step(Results, Params):
    mark_normal_data(Results, Params, 'result', 'bad_full_distributed_step')

def mark_bad_next_page_step(Results, Params):
    mark_normal_data(Results, Params, 'result', 'bad_next_page_step')

def mark_bad_export_step(Results, Params):
    mark_normal_data(Results, Params, 'result', 'bad_export_step')

def mark_bad_import_step(Results, Params):
    mark_normal_data(Results, Params, 'result', 'bad_import_step')

def mark_good_tagged_resources_result(Results, Params):
    mark_normal_data(Results, Params, 'result', 'okay')
    mark_normal_data(Results, Params, 'tagged_internalised', data_for_tagged_split_file(Params))

def mark_good_word_pages_result(Results, Params):
    mark_normal_data(Results, Params, 'result', 'okay')
    mark_normal_data(Results, Params, 'word_pages', number_of_files_in_word_pages_directory(Params))
    mark_normal_data(Results, Params, 'audio_and_translation_files', lara_top.count_audio_and_translation_files_for_params(Params))

def mark_good_full_distributed_step(Results, Params):
    mark_normal_data(Results, Params, 'main_text_files_after_full_distributed', number_of_main_text_files_in_word_pages_directory(Params))

def mark_good_next_page_step(Results, Params):
    mark_normal_data(Results, Params, 'result', 'okay')
    mark_normal_data(Results, Params, 'main_text_files_after_next', number_of_main_text_files_in_word_pages_directory(Params))
    
def mark_time_taken(Results, StartTime, EndTime, Params):
    TimeTaken = float('%.2f'%( EndTime - StartTime ))
    mark_normal_data(Results, Params, 'time_taken', TimeTaken)

def mark_time_taken_for_full_distributed_step(Results, StartTime, EndTime, Params):
    TimeTaken = float('%.2f'%( EndTime - StartTime ))
    mark_normal_data(Results, Params, 'time_taken_for_full_distributed_step', TimeTaken)
    
def mark_time_taken_for_next_page_step(Results, StartTime, EndTime, Params):
    TimeTaken = float('%.2f'%( EndTime - StartTime ))
    mark_normal_data(Results, Params, 'time_taken_for_next_page_step', TimeTaken)

def mark_normal_data(Results, Params, Key, Value):
    Id = remove_tmp_suffix_if_necessary(Params.id)
    Record = Results[Id] if Id in Results else {}
    Record[Key] = Value
    Results[Id] = Record

def files_in_word_pages_directory(Params):
    _minimum_plausible_number_of_files_in_word_page_directory = 5
    NFiles = number_of_files_in_word_pages_directory(Params)
    return NFiles >= _minimum_plausible_number_of_files_in_word_page_directory

def number_of_files_in_word_pages_directory(Params):
    WordPageDir = lara_top.lara_compiled_dir('word_pages_directory', Params)
    return len(lara_utils.directory_files(WordPageDir))

def number_of_main_text_files_in_word_pages_directory(Params):
    WordPageDir = lara_top.lara_compiled_dir('word_pages_directory', Params)
    Files = lara_utils.directory_files(WordPageDir)
    return len([ File for File in Files if is_main_text_file(File)])

def is_main_text_file(File):
    return File.find('_main_text') >= 0 

def data_for_tagged_split_file(Params):
    SplitFile = lara_top.lara_tmp_file('tagged_split', Params)
    PageOrientedSplitList = lara_utils.read_json_file(SplitFile)
    return lara_split_and_clean.get_statistics_for_page_oriented_split_list(PageOrientedSplitList)

# ------------------------------------------------

def mark_comparison_with_previous_results(Results, RecentResults, ConfigFile, Params, TestType):
    Id = remove_tmp_suffix_if_necessary(Params.id)
    if not Id in Results:
        return
    Record = Results[Id]
    if not 'result' in Record:
        return
    mark_comparison_with_last_good_result_if_wrong(Record, Id, Results, RecentResults, TestType)
    for Key in ['audio_and_translation_files', 'word_pages', 'tagged_internalised']:
        mark_comparison_with_last_result_if_different(Key, Record, Id, Results, RecentResults, TestType)

def mark_comparison_with_last_good_result_if_wrong(Record, Id, Results, RecentResults, TestType):
    Outcome = Record['result']
    if Outcome == 'okay':
        return
    Record['last_good_result'] = last_good_result(RecentResults, Id, TestType)

def mark_comparison_with_last_result_if_different(Key, Record, Id, Results, RecentResults, TestType):
    if not Key in Record:
        return
    Result = Record[Key]
    for ( Timestamp, OldResults ) in RecentResults:
        if Id in OldResults and Key in OldResults[Id] and \
           record_is_appropriate_for_test_type(OldResults[Id], TestType):
            OldResult = OldResults[Id][Key]
            if not results_match(OldResult, Result):
                #lara_utils.print_and_flush(f'--- Different: {OldResult}, {Result}')
                DiffKey = f'{Key}_OLD'
                Record[DiffKey] = ( Timestamp, OldResult )
            return

def last_good_result(RecentResults, Id, TestType):
    for ( Timestamp, Results ) in RecentResults:
        if Id in Results and 'result' in Results[Id] and \
           record_is_appropriate_for_test_type(Results[Id], TestType) and \
           Results[Id]['result'] == 'okay':
            return Timestamp
    return 'never_worked'

def record_is_appropriate_for_test_type(Data, TestType):
    return ( TestType == 'resources_and_word_pages' and ( 'audio_and_translation_files' in Data or 'word_pages' in Data ) ) or \
           ( TestType == 'tagging' and 'tagged_internalised' in Data )

def results_match(X, X1):
    if isinstance(X, str):
        return isinstance(X1, str) and X == X1
    if isinstance(X, int):
        return isinstance(X1, int) and X == X1
    if isinstance(X, list):
        return isinstance(X1, list) and lists_match(X, X1)
    if isinstance(X, dict):
        return isinstance(X1, dict) and dicts_match(X, X1)
    return False

def lists_match(X, X1):
    if len(X) != len(X1):
        return False
    if len(X) == 0:
        return True
    return results_match(X[0], X1[0]) and lists_match(X[1:], X1[1:])

def dicts_match(X, X1):
    if not lists_match(sorted(list(X.keys())), sorted(list(X1.keys()))):
        return False
    for Key in X:
        if not results_match(X[Key], X1[Key]):
            return False
    return True

# ------------------------------------------------

_tmp_suffix = '___tmp'

def add_tmp_suffix(Id):
    return f'{Id}{_tmp_suffix}'

def remove_tmp_suffix_if_necessary(Id):
    Index = Id.find(_tmp_suffix)
    return Id[:Index] if Index > 0 else Id

# ------------------------------------------------    

# How many logfiles to go back when looking for the last time something worked
_how_far_back_to_go = 20

def recent_results_pairs():
    return [ ( logfile_name_to_timestamp(Logfile),
               lara_utils.read_json_file(f'{logfile_dir_create_if_necessary()}/{Logfile}') ) 
             for Logfile in last_logfiles() ]

def last_logfiles():
    Files = lara_utils.directory_files(logfile_dir_create_if_necessary())
    Files.sort(reverse=True)
    return Files[:_how_far_back_to_go]

def logfile_name_to_timestamp(Logfile):
    return Logfile.split('.')[0]

# ------------------------------------------------    

def print_result_summary(Results):
    lara_utils.write_json_to_file(Results, get_timestamped_logfile())

def get_timestamped_logfile():
    return f'{logfile_dir_create_if_necessary()}/{lara_utils.timestamp()}.json'

def logfile_dir_create_if_necessary():
    Dir = '$LARA/logfiles'
    lara_utils.create_directory_if_it_doesnt_exist(Dir)
    return Dir
