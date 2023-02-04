
import lara_top
import lara_abstract_html
import lara_treetagger
import lara_mwe
import lara_add_metadata
import lara_audio
import lara_install_audio_zipfile
import lara_new_content
import lara_reverse_language
import lara_edit
import lara_open_in_browser
import lara_offline_test
import lara_utils
import lara_gui
import lara_generic_tts
import lara_tts
import lara_tts_human_eval
import lara_drama
import lara_split_audio_on_silence
# Import following on demand
#import lara_align_adjust
#import lara_align_postedit
#import lara_align_eval
import lara_partitioned_text_files
import lara_correct_accents
import sys
import time

def print_usage():
    print(f'Usage: {lara_utils.python_executable()} $LARA/Code/Python/lara_run.py <Mode> [ <ConfigFile> ]')
    print(f'       where <Mode> is "segment", "treetagger", "treetagger_add_pos", "treetagger_remove_mwe", "minimaltagger", "minimaltagger_spreadsheet"')
    print(f'                       "resources", "word_pages", "distributed",')
    print(f'                       "mwe_annotate", "mwe_judgements_from_text", "apply_mwe_annotations", "mwe_ml_data"')
    print(f'                       "abstract_html", "word_pages_from_abstract_html",')
    print(f'                       "combine_play_segment_audio", "list_unrecorded_play_lines" "make_language_reversed_version"')
    print(f'                       "make_phonetic_corpus", "correct_accents", "correct_accents_and_hashtags"')
    print(f'                       "cut_up_audio", "cut_up_audio_without_text", "trim_sentence_audio"')
    print(f'                       "expand_source_and_target_files", "merge_double_alignment",')
    print(f'                       "align_postediting_files", "align_statistics"')
    print(f'                       "word_alignment_file", "align_word_audio"')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run.py silences_label_file <ConfigFile> <Id>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run.py cut_up_audio <ConfigFile> <Id>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run.py cut_up_audio_without_text <ConfigFile> <Id>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run.py recognise_segment_audio <ConfigFile> <NFiles>')
    print(f'       where <NFiles> is a positive integer or "all"')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run.py add_tmx_segmentation <ConfigFile> <Id>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run.py align_segment_audio <ConfigFile> <Id> <MatchFunction> <Mode>')
    print(f'       where <Id> is a partitioned file Id')
    print(f'       and <MatchFunction> is match function Id')
    print(f'       and <Mode> is "create" or "evaluate"')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run.py merge_double_alignment <ConfigFile> <Id>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run.py update_from_align_postediting_file <ConfigFile> <Id>')
    print(f'       where <Id> is an annotator Id')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run.py update_from_aligned_file <ConfigFile> <Id>')
    print(f'       where <Id> is is a partitioned file Id')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run.py word_pages_from_abstract_html_multiple <MasterConfigFile> <ConfigFile1> <ConfigFile2> ...')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run.py change_volume_for_play_part <ConfigFile> <PartName> <Factor>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run.py create_tts_audio <RecordingScript> <ConfigFile> <Zipfile>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run.py abstract_html_zipfile <ConfigFile> <Format> <Zipfile>')
    print(f'       where <Format> is "pickle" or "json"')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run.py install_ldt_zipfile <Zipfile> <RecordingScript> <Type> <ConfigFile> [ <BadMetadataFile> ]')
    print(f'       where <Type> is "words" or "segments"')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run.py add_metadata <ResourcesDir> <Type>')
    print(f'       where <Type> is "corpus" or "language"')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run.py audio_dir_to_mp3 <AudioDir> [ <ConfigFile> ]')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run.py human_tts_eval_data <MetadataFile> <LanguageId>')
    print(f'       where <Mode> is "csv" or "json"')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run.py newcontent <ContentID>')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run.py edit <FileID> [ <ConfigFile> ]')
    print(f'       where <FileID> is one of {", ".join(lara_edit.valid_fileids())}')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run.py open_in_browser [ <ConfigFile> ]')
    print(f'or     {lara_utils.python_executable()} $LARA/Code/Python/lara_run.py batch <MetadataFile> <Mode>')
    print(f'       where <MetadataFile> is a JSON file containing a list of test items')
    print(f'       and <Mode> is "resources_and_word_pages", "tagging", "distributed" or "export_import"')

def get_config_file_from_args( Args, i = 0 ):
    return lara_top.find_config_file( False if len(Args) <= i else Args[i])

StartTime = None
try:
    
    full_args = sys.argv

    if len(full_args) >= 2:
        StartTime = time.time()
        lara_utils.init_stored_timings()
        ( Mode, Args, NArgs ) = ( full_args[1], full_args[2:], len(full_args[2:]) )

        if Mode == 'help' and NArgs == 1:
            print_usage()
        elif Mode == 'treetagger' and NArgs <= 1:
            configFile = get_config_file_from_args(Args)
            if configFile: lara_top.treetag_untagged_corpus(configFile)
        elif Mode == 'treetagger_add_pos' and NArgs <= 1:
            configFile = get_config_file_from_args(Args)
            if configFile: lara_top.treetag_tagged_corpus_add_pos(configFile)
        elif Mode == 'treetagger_remove_mwe' and NArgs <= 1:
            configFile = get_config_file_from_args(Args)
            if configFile: lara_top.treetag_tagged_corpus_remove_mwe(configFile)
        elif Mode == 'minimaltagger' and NArgs <= 1:
            configFile = get_config_file_from_args(Args)
            if configFile: lara_top.minimal_tag_untagged_corpus(configFile)
        elif Mode == 'minimaltagger_spreadsheet' and NArgs <= 1:
            configFile = get_config_file_from_args(Args)
            if configFile: lara_top.lara_make_minimaltag_spreadsheet(configFile)
        elif Mode == 'segment' and NArgs <= 1:
            configFile = get_config_file_from_args(Args)
            if configFile: lara_top.segment_unsegmented_corpus(configFile)
        elif Mode == 'resources' and NArgs <= 1:
            configFile = get_config_file_from_args(Args)
            if configFile: lara_top.compile_lara_local_resources(configFile)
        elif Mode == 'word_pages' and NArgs <= 1:
            configFile = get_config_file_from_args(Args)
            if configFile: lara_top.compile_lara_local_word_pages(configFile)
        elif Mode == 'abstract_html' and NArgs <= 1:
            configFile = get_config_file_from_args(Args)
            if configFile: lara_top.compile_lara_local_abstract_html(configFile)
        elif Mode == 'make_labelled_corpus' and NArgs <= 1:
            configFile = get_config_file_from_args(Args)
            if configFile: lara_top.make_labelled_corpus_file(configFile)
        elif Mode == 'silences_label_file' and NArgs == 2:
            lara_split_audio_on_silence.make_silence_label_file_from_config(Args[0], Args[1])
        elif Mode == 'add_tmx_segmentation' and NArgs == 2:
            import lara_align_adjust
            lara_align_adjust.add_tmx_segmentation_from_config_file(Args[0], Args[1])
        elif Mode == 'expand_source_and_target_files' and NArgs <= 1:
            configFile = get_config_file_from_args(Args)
            if configFile: lara_partitioned_text_files.expand_source_and_target_files(configFile)
        elif Mode == 'cut_up_audio' and NArgs <= 1:
            configFile = get_config_file_from_args(Args)
            if configFile: lara_top.cut_up_audio(configFile, '')
        elif Mode == 'cut_up_audio' and NArgs == 2:
            lara_top.cut_up_audio(Args[0], Args[1])
        elif Mode == 'cut_up_audio_without_text' and NArgs <= 1:
            configFile = get_config_file_from_args(Args)
            if configFile: lara_top.cut_up_audio_without_text(configFile, '')
        elif Mode == 'cut_up_audio_without_text' and NArgs == 2:
            lara_top.cut_up_audio_without_text(Args[0], Args[1])
        elif Mode == 'trim_sentence_audio' and NArgs <= 1:
            configFile = get_config_file_from_args(Args)
            if configFile: lara_split_audio_on_silence.trim_all_sentence_audio(configFile)
        elif Mode == 'recognise_segment_audio' and NArgs <= 1:
            import lara_asr
            configFile = get_config_file_from_args(Args)
            if configFile: lara_asr.recognise_and_store_in_segment_audio_dir(configFile, 'all')
        elif Mode == 'merge_double_alignment' and NArgs == 2:
            import lara_align_adjust
            lara_align_adjust.make_corpus_audio_and_translations_for_double_aligned_file_from_config(Args[0], Args[1])
        elif Mode == 'recognise_segment_audio' and NArgs == 2:
            import lara_asr
            lara_asr.recognise_and_store_in_segment_audio_dir(Args[0], Args[1])
        elif Mode == 'align_segment_audio' and NArgs == 4:
            import lara_align_from_audio
            lara_align_from_audio.align_rec_results_to_text_from_config(Args[0], Args[1], Args[2], Args[3])
        elif Mode == 'update_from_aligned_file' and NArgs == 2:
            import lara_align_from_audio
            lara_align_from_audio.update_segmented_text_and_metadata_from_aligned_file(Args[0], Args[1])
        elif Mode == 'align_postediting_files' and NArgs <= 1:
            import lara_align_postedit
            configFile = get_config_file_from_args(Args)
            if configFile: lara_align_postedit.make_align_postediting_files(configFile)
        elif Mode == 'align_statistics' and NArgs <= 1:
            import lara_align_eval
            configFile = get_config_file_from_args(Args)
            if configFile: lara_align_eval.print_alignment_statistics(configFile)
        elif Mode == 'word_alignment_file' and NArgs <= 1:
            import lara_align_words
            configFile = get_config_file_from_args(Args)
            if configFile: lara_align_words.make_manual_word_alignment_file(configFile)
        elif Mode == 'align_word_audio' and NArgs <= 1:
            import lara_align_words
            configFile = get_config_file_from_args(Args)
            if configFile: lara_align_words.extract_word_audio(configFile)
        elif Mode == 'update_from_align_postediting_file' and NArgs == 2:
            import lara_align_postedit
            lara_align_postedit.update_from_postediting_file(Args[0], Args[1])
        elif Mode == 'abstract_html_zipfile' and NArgs == 3:
            configFile = get_config_file_from_args(Args)
            if configFile: lara_top.compile_lara_local_abstract_html_zipfile(configFile, Args[1], Args[2])
        elif Mode == 'word_pages_from_abstract_html' and NArgs <= 1:
            configFile = get_config_file_from_args(Args)
            if configFile: lara_abstract_html.abstract_html_to_html(configFile, 'from_config')
        elif Mode == 'word_pages_from_abstract_html_multiple' and NArgs >= 2:
            MasterConfigFile = Args[0]
            ComponentConfigFiles = Args[1:]
            lara_abstract_html.abstract_html_to_html_multiple(MasterConfigFile, ComponentConfigFiles)
        elif Mode == 'create_tts_audio' and NArgs == 3:
            lara_generic_tts.create_tts_audio(Args[0], Args[1], Args[2])
        elif Mode == 'install_ldt_zipfile' and NArgs == 4:
            lara_install_audio_zipfile.install_audio_zipfile(Args[0], Args[1], Args[2], Args[3], 'default')
        elif Mode == 'install_ldt_zipfile' and NArgs == 5:
            lara_install_audio_zipfile.install_audio_zipfile(Args[0], Args[1], Args[2], Args[3], Args[4])
        elif Mode == 'mwe_annotate' and NArgs <= 1:
            configFile = get_config_file_from_args(Args)
            if configFile: lara_top.mwe_annotate_file(configFile)
        elif Mode == 'mwe_judgements_from_text' and NArgs <= 1:
            configFile = get_config_file_from_args(Args)
            if configFile: lara_mwe.update_mwes_from_text_file(configFile)
        elif Mode == 'apply_mwe_annotations' and NArgs <= 1:
            configFile = get_config_file_from_args(Args)
            if configFile: lara_top.apply_mwe_annotations(configFile)
        elif Mode == 'mwe_ml_data' and NArgs <= 1:
            configFile = get_config_file_from_args(Args)
            if configFile: lara_top.mwe_annotations_to_ml_data(configFile)
        elif Mode == 'combine_play_segment_audio' and NArgs <= 1:
            configFile = get_config_file_from_args(Args)
            if configFile: lara_top.combine_play_segment_audio(configFile)
        elif Mode == 'list_unrecorded_play_lines' and NArgs <= 1:
            configFile = get_config_file_from_args(Args)
            if configFile: lara_top.find_unrecorded_play_lines(configFile)
        elif Mode == 'format_word_token_spreadsheet' and NArgs <= 1:
            configFile = get_config_file_from_args(Args)
            if configFile: lara_top.format_word_token_spreadsheet_as_html(configFile)
        elif Mode == 'change_volume_for_play_part' and NArgs == 3:
            lara_drama.change_volume_for_play_part(Args[0], Args[1], Args[2])
        elif Mode == 'make_language_reversed_version' and NArgs <= 1:
            configFile = get_config_file_from_args(Args)
            if configFile: lara_reverse_language.reverse_language_from_config_file(configFile)
        elif Mode == 'make_phonetic_corpus' and NArgs <= 1:
            configFile = get_config_file_from_args(Args)
            if configFile: lara_top.make_phonetic_version_of_corpus(configFile)
        elif Mode == 'correct_accents' and NArgs <= 1:
            configFile = get_config_file_from_args(Args)
            if configFile: lara_correct_accents.try_to_correct_accents(configFile)
        elif Mode == 'correct_accents_and_hashtags' and NArgs <= 1:
            configFile = get_config_file_from_args(Args)
            if configFile: lara_correct_accents.try_to_correct_accents_and_hashtags(configFile)
        elif Mode == 'add_metadata' and NArgs == 2:
            lara_add_metadata.add_metadata_to_lara_resource_directory(Args[0], Args[1])
        elif Mode == 'distributed' and NArgs == 1:
            lara_top.compile_lara_reading_history_from_config_file(Args[0])
        elif Mode == 'audio_dir_to_mp3' and NArgs <= 2:
            configFile = get_config_file_from_args(Args, 1)
            lara_audio.convert_lara_audio_directory_to_mp3_format(Args[0], configFile)
        elif Mode == 'human_tts_eval_data' and NArgs == 2:
            lara_tts_human_eval.make_eurocall_evaluation_form(Args[0], Args[1])
        elif Mode == 'newcontent' and NArgs == 1:
            lara_new_content.main(Args[0])
        elif Mode == 'edit' and NArgs > 0 and NArgs <= 2:
            lara_edit.main(Args)
        elif Mode == 'open_in_browser' and NArgs <= 1:
            configFile = get_config_file_from_args(Args)
            if configFile: lara_open_in_browser.main(Args)
        elif Mode == 'batch' and NArgs == 2:
            lara_offline_test.run_lara_test_from_list_in_file(Args[0], Args[1])
        elif Mode == "ttt": # "Test TreeTagger"
            configFile = get_config_file_from_args([])
            import lara_config
            if configFile:
                ConfigData = lara_config.read_lara_local_config_file(configFile)
                if ConfigData:
                    text = " ".join(Args)
                    lara_utils.print_and_flush( f'--- guessed language={lara_treetagger.guess_treetagger_language_from_text( text, False )}' )
                    lara_utils.print_and_flush( f'--- tagged text = "{lara_treetagger.treetag_text( text, False, ConfigData)}"' )
        elif Mode == 'gui':
            StartTime = None
            lara_gui.main(Args)
        else:
            StartTime = None
            print_usage()
    else:
        print_usage()
except Exception as e:
    import traceback
    lara_utils.print_and_flush(f'*** Error: An internal exception occurred and the program was aborted!')
    lara_utils.print_and_flush(f'*** Error: Exception message: {str(e)}')
    lara_utils.print_and_flush(f'Traceback (most recent call last):')
    lara_utils.print_and_flush(''.join(traceback.format_tb(e.__traceback__)))
finally:
    lara_utils.cleanup_temp_files_and_directories()
    if StartTime is not None: 
        lara_utils.print_and_flush_with_elapsed_time('--- Done', StartTime)
    lara_utils.print_stored_timings()
