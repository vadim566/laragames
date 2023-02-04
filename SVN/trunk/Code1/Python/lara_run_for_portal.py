
import lara_reading_portal
import lara_top
import lara_treetagger
import lara_add_metadata
import lara_config
import lara_audio
import lara_install_audio_zipfile
import lara_segment
import lara_merge_resources
import lara_download_resource
import lara_import_export
import lara_translations
import lara_mwe
import lara_generic_tts
import lara_tts
import lara_crowdsource
#import lara_flashcards
import lara_flashcards_new
import lara_polish
import lara_play_all
import lara_utils
import sys
import time

def print_usage():
    print(f'Usage: {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py <Mode> <ConfigFile>')
    print(f'       where <Mode> is "segment", "treetagger", "treetagger_remove_mwe", "minimaltagger", "minimaltagger_spreadsheet"')
    print(f'                       "resources", "word_pages", "distributed", "mwe_annotate" or "apply_mwe_annotations"')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py extract_css_img_and_audio_files <ConfigFile> <ResultFile>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py extract_css_img_and_audio_files_basic <CorpusFile> <ResultFile>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run.py create_tts_audio <RecordingScript> <ConfigFile> <Zipfile>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run.py get_tts_engines <Lang> <ResultFile>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py install_ldt_zipfile <Zipfile> <RecordingScript> <Type> <ConfigFile> [ <BadMetadataFile> ]')
    print(f'       where <Type> is "words" or "segments"')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py install_non_ldt_audio_zipfile <Zipfile> [ <ConfigFile> ]')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py add_metadata <ResourcesDir> <Type>')
    print(f'       where <Type> is "corpus" or "language"')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py audio_dir_to_mp3 <AudioDir> <ConfigFile> <BadItemsFile>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py treetagger_basic <Language> <InFile> <OutFile>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py resources_basic <ConfigFile> <WordRecordingFile>')
    print('                                                        <SegmentRecordingFile> <WordTranslationCSV> <SegmentTranslationCSV>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py resources_basic_tokens <ConfigFile> <WordTokenTranslationCSV> <WordTokenTranslationJSON>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py resources_and_copy <ConfigFile> <BaseFile>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py resources_and_copy_and_log_zipfile <ConfigFile> <BaseFile> <LogDir>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py tokens_from_types_and_copy <ConfigFile> <BaseFile>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py mwe_annotate <ConfigFile>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py apply_mwe_annotations <ConfigFile>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py check_mwe_defs <MWEDefsFile>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py mwe_txt_defs_to_json <MWEDefsFileTxt> <MWEDefsFileJSON>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py mwe_json_defs_to_txt <MWEDefsFileJSON> <MWEDefsFileTxt>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py mwe_annotate_and_copy <ConfigFile> <MWEAnnotationsFile>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py merge_update_mwe_defs <MWEDefsFileMain> <MWEDefsFileUpdateMaterial> <ConfigFile>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py apply_mwe_annotations_and_copy <ConfigFile> <TransformedCorpusFile> <TraceFile>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py get_possible_flashcard_types <ReplyFile>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py make_flashcards <ConfigFile> <FlashcardType> <NCards> <Level> <POS> <UserId> <Strategy> <ContentId> <OutFile>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py minimaltagger_spreadsheet_and_copy <ConfigFile> <SpreadsheetFile>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py segment_file <InFile> <OutFile> [<L2>]')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py merge_language_resources <Dir1> <Dir2> <DirMerged> <ConfigFile>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py merge_translation_spreadsheets <CSVOld> <CSVNew> <CSVUpdated>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py merge_update_translation_spreadsheet <CSVMain> <CSVUpdateMaterial>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py find_deleted_lines_in_translation_spreadsheets <CSVOld> <CSVNew> <AnswerFile>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py find_deleted_lines_in_word_token_spreadsheets <CSVOld> <CSVNew> <AnswerFile>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py get_voices_and_l1s_for_resource <ResourceId> <ConfigFile> <ResultFile>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py get_voices_and_l1s_for_resource_file <ConfigFile> <ResultFile>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py count_audio_and_translation_files <ConfigFile> <ResultFile>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py check_config_file <ConfigFile> <Type> <ReplyFile>')
    print(f'       where <Type> is "local" or "distributed"')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py check_lara_id <IdString> <ReplyFile>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py download_resource <URL> <Dir>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py make_export_zipfile <SourceConfigFile> <TargetZipfile>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py cut_up_project <ConfigFile> <ZipfileForCrowdsourcing>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py stick_together_projects <FileWithListOfConfigFiles> <TargetConfigFile>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py import_zipfile <Zipfile> <CorpusDir> <LanguageRootDir> <ConfigFile>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py unzip <Zipfile> <Target>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py streamed_download_binary_file <URL> <Target>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py csv_to_json <CSVFile> <JSONFile>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py json_to_csv <JSONFile> <CSVFile>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py word_token_csv_to_json <CSVFile> <JSONFile>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py word_token_json_to_csv <JSONFile> <CSVFile>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py word_type_or_lemma_json_to_csv <JSONFile> <CSVFile>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py diff_tagged_corpus <OldTaggedCorpus> <ConfigFile> <Zipfile>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py check_concraft_server_status <ConfigFile> <ReplyFile>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py copy_audio_dir_with_uniform_sampling_rate <Dir> <Dir1> <ConfigFile>')
    # Operations for reader portal
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py get_page_names_for_resource <ResourceId> <ConfigFile> <ReplyFile>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py compile_reading_history <ConfigFile> <ReplyFile>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py compile_next_page_in_history <ResourceId> <LanguageResourceId> <ConfigFile> <ReplyFile>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run_for_portal.py clean_reading_portal_cache <ConfigFile>')

def get_config_file_from_args( Args, i = 0 ):
    return lara_top.find_config_file( False if len(Args) <= i else Args[i])

full_args = sys.argv
StartTime = time.time()
lara_utils.init_stored_timings()

if len(full_args) >= 2:
    ( Mode, Args, NArgs ) = ( full_args[1], full_args[2:], len(full_args[2:]) )
    if Mode == 'treetagger' and NArgs == 1:
        lara_top.treetag_untagged_corpus(Args[0])
    elif Mode == 'treetagger_remove_mwe' and NArgs <= 1:
            configFile = get_config_file_from_args(Args)
            if configFile: lara_top.treetag_tagged_corpus_remove_mwe(configFile)
    elif Mode == 'treetagger_basic' and NArgs == 3:
        Params = lara_config.default_params()
        Params.language = Args[0]
        lara_top.treetag_lara_file_main(Args[0], Args[1], Params, Args[2])
    elif Mode == 'minimaltagger' and NArgs <= 1:
        configFile = get_config_file_from_args(Args)
        if configFile: lara_top.minimal_tag_untagged_corpus(configFile)
    elif Mode == 'minimaltagger_spreadsheet' and NArgs <= 1:
        configFile = get_config_file_from_args(Args)
        if configFile: lara_top.lara_make_minimaltag_spreadsheet(configFile)
    elif Mode == 'minimaltagger_spreadsheet_and_copy' and NArgs == 2:
        configFile = get_config_file_from_args(Args)
        if configFile: lara_top.lara_make_minimaltag_spreadsheet_and_copy(configFile, Args[1])
    elif Mode == 'resources' and NArgs == 1:
        lara_top.compile_lara_local_resources(Args[0])
    elif Mode == 'resources_and_copy' and NArgs == 2:
        lara_top.compile_lara_local_resources_and_copy(Args[0], Args[1])
    elif Mode == 'resources_and_copy_and_log_zipfile' and NArgs == 3:
        lara_top.compile_lara_local_resources_and_copy_and_log_zipfile(Args[0], Args[1], Args[2])
    elif Mode == 'tokens_from_types_and_copy' and NArgs == 2:
        lara_top.compile_lara_local_resources_and_copy_just_tokens_from_types(Args[0], Args[1])
    elif Mode == 'resources_basic' and NArgs == 5:
        lara_top.compile_lara_local_resources_explicit(Args[0], Args[1], Args[2], Args[3], Args[4])
    elif Mode == 'resources_basic_tokens' and NArgs == 3:
        lara_top.compile_lara_local_resources_explicit_tokens(Args[0], Args[1], Args[2])
    elif Mode == 'mwe_annotate' and NArgs <= 1:
        configFile = get_config_file_from_args(Args)
        if configFile: lara_top.mwe_annotate_file(configFile)
    elif Mode == 'apply_mwe_annotations' and NArgs <= 1:
        configFile = get_config_file_from_args(Args)
        if configFile: lara_top.apply_mwe_annotations(configFile)
    elif Mode == 'check_mwe_defs' and NArgs == 1:
        lara_top.check_mwe_defs_file(Args[0])
    elif Mode == 'mwe_txt_defs_to_json' and NArgs == 2:
        lara_mwe.mwe_txt_file_to_json(Args[0], Args[1])
    elif Mode == 'mwe_json_defs_to_txt' and NArgs == 2:
        lara_mwe.mwe_json_file_to_txt(Args[0], Args[1])
    elif Mode == 'merge_update_mwe_defs' and NArgs == 3:
        lara_merge_resources.safe_merge_and_replace_mwe_defs_file(Args[0], Args[1], Args[2])
    elif Mode == 'mwe_annotate_and_copy' and NArgs == 2:
        lara_top.mwe_annotate_file_and_copy(Args[0], Args[1])
    elif Mode == 'apply_mwe_annotations_and_copy' and NArgs == 3:
        lara_top.apply_mwe_annotations_and_copy(Args[0], Args[1], Args[2])
    elif Mode == 'get_possible_flashcard_types' and NArgs == 1:
        lara_utils.write_json_to_file(lara_config._known_flashcard_types, Args[0])
    elif Mode == 'make_flashcards' and NArgs == 9:
        lara_flashcards_new.make_flashcards(Args[0], Args[1], int(Args[2]), Args[3], Args[4], Args[5], Args[6], Args[7], Args[8])
    elif Mode == 'extract_css_img_and_audio_files' and NArgs == 2:
        lara_top.find_css_img_and_audio_files(Args[0], Args[1])
    elif Mode == 'extract_css_img_and_audio_files_basic' and NArgs == 2:
        lara_top.find_css_img_and_audio_files_explicit(Args[0], Args[1])
    elif Mode == 'word_pages' and NArgs == 1:
        lara_top.compile_lara_local_word_pages(Args[0])
    elif Mode == 'add_metadata' and NArgs == 2:
        lara_add_metadata.add_metadata_to_lara_resource_directory(Args[0], Args[1])
    elif Mode == 'distributed' and NArgs == 1:
        lara_top.compile_lara_reading_history_from_config_file(Args[0])
    elif Mode == 'create_tts_audio' and NArgs == 3:
        lara_generic_tts.create_tts_audio(Args[0], Args[1], Args[2])
    elif Mode == 'get_tts_engines' and NArgs == 2:
        lara_generic_tts.get_tts_engines_for_language(Args[0], Args[1])
    elif Mode == 'install_ldt_zipfile' and NArgs == 4:
        lara_install_audio_zipfile.install_audio_zipfile(Args[0], Args[1], Args[2], Args[3], 'default')
    elif Mode == 'install_ldt_zipfile' and NArgs == 5:
        lara_install_audio_zipfile.install_audio_zipfile(Args[0], Args[1], Args[2], Args[3], Args[4])
    elif Mode == 'install_non_ldt_audio_zipfile' and NArgs == 2:
        lara_install_audio_zipfile.install_audio_zipfile(Args[0], Args[1])
    elif Mode == 'count_audio_and_translation_files' and NArgs == 2:
        lara_top.count_audio_and_translation_files_and_print(Args[0], Args[1])
    elif Mode == 'check_config_file' and NArgs == 3:
        lara_config.check_config_file_and_print(Args[0], Args[1], Args[2])
    elif Mode == 'check_lara_id' and NArgs == 2:
        lara_config.check_lara_id_and_print(Args[0], Args[1])
    elif Mode == 'audio_dir_to_mp3' and NArgs == 3:
        lara_install_audio_zipfile.convert_lara_audio_directory_to_mp3_format(Args[0], Args[1], Args[2])
    elif Mode == 'segment_file' and NArgs == 2:
        lara_segment.segment_file(Args[0], Args[1])
    elif Mode == 'segment_file' and NArgs == 3:
        lara_top.segment_unsegmented_corpus_explicit(Args[0], Args[1], Args[2])
    elif Mode == 'merge_language_resources' and NArgs == 4:
        lara_merge_resources.merge_language_resources(Args[0], Args[1], Args[2], Args[3])
    elif Mode == 'merge_translation_spreadsheets' and NArgs == 3:
        lara_merge_resources.merge_translation_spreadsheets(Args[0], Args[1], Args[2])
    elif Mode == 'merge_update_translation_spreadsheet' and NArgs == 2:
        lara_merge_resources.safe_merge_and_replace_spreadsheet(Args[0], Args[1])
    elif Mode == 'find_deleted_lines_in_translation_spreadsheets' and NArgs == 3:
        lara_merge_resources.find_deleted_lines_in_translation_spreadsheet_and_write(Args[0], Args[1], Args[2])
    elif Mode == 'find_deleted_lines_in_word_token_spreadsheets' and NArgs == 3:
        lara_merge_resources.find_deleted_lines_in_word_token_spreadsheet_and_write(Args[0], Args[1], Args[2])
    elif Mode == 'get_voices_and_l1s_for_resource' and NArgs == 3:
        lara_reading_portal.get_voices_and_l1s_for_resource_and_write(Args[0], Args[1], Args[2])
    elif Mode == 'get_voices_and_l1s_for_resource_file':
        lara_reading_portal.get_voices_and_l1s_for_resource_file_and_write(Args[0], Args[1])
    elif Mode == 'download_resource' and NArgs == 2:
        lara_download_resource.download_resource(Args[0], Args[1])
    elif Mode == 'unzip' and NArgs == 2:
        lara_utils.unzip_file(Args[0], Args[1])
    elif Mode == 'streamed_download_binary_file' and NArgs == 2:
        lara_utils.read_file_from_url_streamed(Args[0], Args[1])
    elif Mode == 'csv_to_json' and NArgs == 2:
        lara_utils.csv_to_json(Args[0], Args[1])
    elif Mode == 'json_to_csv' and NArgs == 2:
        lara_utils.json_to_csv(Args[0], Args[1])
    elif Mode == 'word_token_csv_to_json' and NArgs == 2:
        lara_translations.word_translation_csv_to_json(Args[0], Args[1])
    elif Mode == 'word_token_json_to_csv' and NArgs == 2:
        lara_translations.word_translation_json_to_csv(Args[0], Args[1])
    elif Mode == 'word_type_or_lemma_json_to_csv' and NArgs == 2:
        lara_translations.word_type_or_lemma_json_to_csv(Args[0], Args[1])
    elif Mode == 'make_export_zipfile' and NArgs == 2:
        lara_import_export.make_export_zipfile(Args[0], Args[1])
    elif Mode == 'import_zipfile' and NArgs == 4:
        lara_import_export.import_zipfile(Args[0], Args[1], Args[2], Args[3])
    elif Mode == 'cut_up_project' and NArgs == 2:
        lara_crowdsource.cut_up_project(Args[0], Args[1])
    elif Mode == 'stick_together_projects' and NArgs == 2:
        lara_crowdsource.stick_together_projects(Args[0], Args[1])
    elif Mode == 'diff_tagged_corpus' and NArgs == 3:
        lara_top.diff_tagged_corpus(Args[0], Args[1], Args[2])
    elif Mode == 'check_concraft_server_status' and NArgs == 2:
        lara_polish.check_concraft_server_status(Args[0], Args[1])
    elif Mode == 'copy_audio_dir_with_uniform_sampling_rate' and NArgs == 3:
        lara_play_all.make_copy_of_audio_directory_with_uniform_sampling_rate(Args[0], Args[1], Args[2])
    # Operations for reading portal
    elif Mode == 'get_page_names_for_resource' and NArgs == 3:
        lara_reading_portal.get_page_names_for_resource_and_write(Args[0], Args[1], Args[2])
    elif Mode == 'compile_reading_history' and NArgs == 2:
        lara_reading_portal.compile_reading_history(Args[0], Args[1])
    elif Mode == 'compile_next_page_in_history' and NArgs == 4:
        lara_reading_portal.compile_next_page_in_history_and_write(Args[0], Args[1], Args[2], Args[3])
    elif Mode =='clean_reading_portal_cache' and NArgs == 1:
        lara_reading_portal.clean_distributed_cache_data(Args[0])
    else:
        lara_utils.print_and_flush(f'*** Error: bad call: {" ".join(full_args)}')
        print_usage()
else:
    print_usage()

if StartTime is not None: 
    lara_utils.print_and_flush_with_elapsed_time('--- lara_run_for_portal command executed', StartTime)
lara_utils.print_stored_timings()


