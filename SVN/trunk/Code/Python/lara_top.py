
import lara
import lara_config
import lara_abstract_html
import lara_distributed
import lara_download_metadata
import lara_segment
import lara_treetagger
import lara_minimal_tag
import lara_mwe
import lara_mwe_ml
import lara_split_and_clean
import lara_images
import lara_audio
import lara_translations
import lara_drama
import lara_picturebook
import lara_chinese
import lara_japanese
import lara_utils
import lara_parse_utils
import lara_format_word_token_file
#import lara_align_from_audio
import time
import copy

## Sample config files for testing
config_files = {'minimal': '$LARA/Content/minimal/corpus/local_config.json',
                'lorem_ipsum': '$LARA/Content/lorem_ipsum/corpus/local_config.json',
                'peter_rabbit': '$LARA/Content/peter_rabbit/corpus/local_config.json',
                'peter_rabbit_abstract_html': '$LARA/Content/peter_rabbit/corpus/local_config_abstract_html.json',
                'peter_rabbit_small': '$LARA/Content/peter_rabbit/corpus/local_config_small.json',
                'alice_in_wonderland': '$LARA/Content/alice_in_wonderland/corpus/local_config.json',
                'alice_in_wonderland_pos': '$LARA/Content/alice_in_wonderland/corpus/local_config_POS.json',
                'tina': '$LARA/Content/tina_fer_i_fri/corpus/local_config.json',
                'ungaretti': '$LARA/Content/ungaretti/corpus/local_config.json',
                'dante': '$LARA/Content/dante/corpus/local_config.json',
                'edda': '$LARA/Content/edda/corpus/local_config.json',
                'hyakumankai_ikita_neko': '$LARA/Content/hyakumankai_ikita_neko/corpus/local_config.json',
                'abba': '$LARA/Content/abba/corpus/local_config.json',
                'revivalistics': '$LARA/Content/revivalistics/corpus/local_config.json',
                'revivalistics_small': '$LARA/Content/revivalistics/corpus/local_config_small.json',
                'EbneSina': '$LARA/Content/EbneSina/corpus/local_config.json',
                'Choopan': '$LARA/Content/the_boy_who_cried_wolf/corpus/local_config.json',
                'Arash': '$LARA/Content/Arash/corpus/local_config.json',
                'bozboz_ghandi': '$LARA/Content/bozboz_ghandi/corpus/local_config.json',
                'molana': '$LARA/Content/molana/corpus/local_config.json',
                'le_petit_prince': '$LARA/Content/le_petit_prince_small/corpus/local_config.json',
                'mary': '$LARA/Content/mary_had_a_little_lamb/corpus/local_config.json',
                'mary_abstract_html': '$LARA/Content/mary_had_a_little_lamb/corpus/local_config_abstract_html.json',
                'mary_social_network': '$LARA/Content/mary_had_a_little_lamb/corpus/local_config_social_network.json',
                'tex': '$LARA/Content/texs_french_course/corpus/local_config.json',
                'edward_lear': '$LARA/Content/edward_lear/corpus/local_config.json',
                'ogden_nash': '$LARA/Content/ogden_nash/corpus/local_config.json',
                'hur_gick_det_sen': '$LARA/Content/hur_gick_det_sen/corpus/local_config.json',
                'hur_gick_det_sen_small': '$LARA/Content/hur_gick_det_sen/corpus/local_config_small.json',
                'litli_prinsinn': '$LARA/Content/litli_prinsinn/corpus/local_config.json',
                'barngarla_alphabet': '$LARA/Content/barngarla_alphabet/corpus/local_config.json',
                'wilhelmbusch': '$LARA/Content/wilhelmbusch/corpus/wilhelmbusch.json',    
                'animal_farm': '$LARA/Content/animal_farm/corpus/local_config.json',
                'le_chien_jaune': '$LARA/Content/le_chien_jaune/corpus/local_config.json',
                'kallocaine': '$LARA/Content/kallocaine/corpus/local_config.json',
                'nasreddin_small': '$LARA/Content/turkish_toy/corpus/local_config.json',
                'genesis_icelandic': '$LARA/Content/sample_icelandic/corpus/local_config.json',
                'genesis_english_tokens': '$LARA/Content/sample_english_tokens/corpus/local_config.json',
                'deneme': '$LARA/Content/deneme/corpus/local_config.json',
                'havamal': '$LARA/Content/hávamál/corpus/local_config.json',
                'voluspa': '$LARA/Content/völuspá/corpus/local_config.json',
                'voluspa_kenningar': '$LARA/Content/völuspá/corpus/local_config_kenningar.json',
                'sample_english': '$LARA/Content/sample_english/corpus/local_config.json',
                'sample_english_read_all': '$LARA/Content/sample_english/corpus/local_config_read_all.json',
                'sample_english_surface': '$LARA/Content/sample_english_surface/corpus/local_config.json',
                'sample_english_tokens': '$LARA/Content/sample_english_tokens/corpus/local_config.json',
                'sample_french': '$LARA/Content/sample_french/corpus/local_config.json',
                'hashtags': '$LARA/Content/hashtags/corpus/local_config.json',
                'sample_sign': '$LARA/Content/sample_sign/corpus/local_config.json',
                'tina_ítm': '$LARA/Content/tina_ítm/corpus/local_config.json',
                'maly_ksiaze_14': '$LARA/Content/maly_ksiaze_14/corpus/local_config.json',
                'bear_rabbits': '$LARA/Content/chinese_test1/corpus/local_config.json',
                'antigone': '$LARA/Content/antigone/corpus/local_config.json',
                'le_bonheur_prosodic_small': '$LARA/Content/le_bonheur/corpus/local_config_audio_extraction_prosodic_groups_small.json',
                'japanese_little_prince': '$LARA/Content/japanese_little_prince/corpus/local_config.json',
                'picturebook_toy_mixed': '$LARA/Content/picturebook_examples/corpus/local_config_mixed_toy.json',
                'arabic_alphabet': '$LARA/Content/arabic_alphabet_book/corpus/local_config.json',
                'arabic_alphabet_phonetic': '$LARA/Content/arabic_alphabet_book/corpus/local_config_phonetic.json',
                # Distributed
                'reader1_english': '$LARA/Content/reader1_english/distributed_config.json',
                'reader1_english_small': '$LARA/Content/reader1_english/distributed_config_small.json',
                'reader1_english_small_surface': '$LARA/Content/reader1_english/distributed_config_small_surface.json',
                'reader1_english_trans': '$LARA/Content/reader1_english/distributed_config_trans.json',
                'reader1_german': '$LARA/Content/reader1_german/distributed_config_german.json',
                }

## Test functions
def lara_do_segment(Id):
    if Id in config_files:
        segment_unsegmented_corpus(config_files[Id])
    else:
        lara_utils.print_and_flush(f'*** Error: unknown ID: {Id}')

def lara_treetag(Id):
    if Id in config_files:
        treetag_untagged_corpus(config_files[Id])
    else:
        lara_utils.print_and_flush(f'*** Error: unknown ID: {Id}')

def lara_treetag_add_pos(Id):
    if Id in config_files:
        treetag_tagged_corpus_add_pos(config_files[Id])
    else:
        lara_utils.print_and_flush(f'*** Error: unknown ID: {Id}')

def lara_minimaltag_spreadsheet(Id):
    if Id in config_files:
        lara_make_minimaltag_spreadsheet(config_files[Id])
    else:
        lara_utils.print_and_flush(f'*** Error: unknown ID: {Id}')

def lara_minimaltag(Id):
    if Id in config_files:
        minimal_tag_untagged_corpus(config_files[Id])
    else:
        lara_utils.print_and_flush(f'*** Error: unknown ID: {Id}')

def lara_compile_local1(Id):
    if Id in config_files:
        compile_lara_local_resources(config_files[Id])
    else:
        lara_utils.print_and_flush(f'*** Error: unknown ID: {Id}')

def lara_compile_local2(Id):
    if Id in config_files:
        compile_lara_local_word_pages(config_files[Id])
    else:
        lara_utils.print_and_flush(f'*** Error: unknown ID: {Id}')

def lara_compile_distributed(Id):
    if Id in config_files:
        compile_lara_reading_history_from_config_file(config_files[Id])
    else:
        lara_utils.print_and_flush(f'*** Error: unknown ID: {Id}')

# --------------------------------------------------------

## TOP-LEVEL CALLS

def segment_unsegmented_corpus(ConfigFile):
    ConfigData = lara_config.read_lara_local_config_file(ConfigFile)
    if ConfigData:
        segment_unsegmented_corpus1(ConfigData)

def segment_unsegmented_corpus_explicit(UnsegmentedCorpus, SegmentedCorpus, L2):
    # We fill in default values for the params, which means the Chinese tokeniser is Jieba and
    # we can't use another one from the portal. But it's very unlikely we'd ever want to.
    ConfigData = lara_config.default_params()
    ConfigData.language = L2
    segment_unsegmented_corpus1_explicit(UnsegmentedCorpus, SegmentedCorpus, ConfigData)

# Treetag the untagged corpus file
def treetag_untagged_corpus(ConfigFile):
    ConfigData = lara_config.read_lara_local_config_file(ConfigFile)
    if ConfigData:
        treetag_untagged_corpus_file1(ConfigData)

def treetag_tagged_corpus_add_pos(ConfigFile):
    ConfigData = lara_config.read_lara_local_config_file(ConfigFile)
    if ConfigData:
        treetag_tagged_corpus_file_add_pos1(ConfigData)

def treetag_tagged_corpus_remove_mwe(ConfigFile):
    ConfigData = lara_config.read_lara_local_config_file(ConfigFile)
    if ConfigData:
        treetag_tagged_corpus_file_remove_mwe1(ConfigData)

# Create a "blank" minimaltag spreadsheet
def lara_make_minimaltag_spreadsheet(ConfigFile):
    ConfigData = lara_config.read_lara_local_config_file(ConfigFile)
    if ConfigData:
        compile_lara_local_make_lemma_dictionary_spreadsheet(ConfigData)

# Create a "blank" minimaltag spreadsheet and copy it to a designated location
def lara_make_minimaltag_spreadsheet_and_copy(ConfigFile, SpreadsheetFile):
    ConfigData = lara_config.read_lara_local_config_file(ConfigFile)
    if ConfigData:
        ResultFile = lara_tmp_file('lemma_dictionary_file', ConfigData)
        if compile_lara_local_make_lemma_dictionary_spreadsheet(ConfigData) and lara_utils.file_exists(ResultFile):
            lara_utils.copy_file(ResultFile, SpreadsheetFile)
            lara_utils.print_and_flush(f'--- Copied new version of lemma spreadsheet to {SpreadsheetFile}')

# Minimal-tag the untagged corpus file
def minimal_tag_untagged_corpus(ConfigFile):
    ConfigData = lara_config.read_lara_local_config_file(ConfigFile)
    if ConfigData:
        minimal_tag_untagged_corpus_file1(ConfigData)

# Treetag without using config file
def treetag_lara_file_main(Language, InFile, Params, OutFile):
    lara_treetagger.treetag_lara_file_main(Language, InFile, Params, OutFile)

# Create file associating words and POS tags
def make_word_pos_file(ConfigFile):
    ConfigData = lara_config.read_lara_local_config_file(ConfigFile)
    if not ConfigData:
        return False
    Language = ConfigData.language
    InFile = ConfigData.corpus
    WordPOSFile = lara_tmp_file('word_pos_file', ConfigData)
    return lara_treetagger.make_word_pos_file(Language, InFile, ConfigData, WordPOSFile)

# Local compile (i.e. all resources on local machine), part 1
def compile_lara_local_resources(ConfigFile):
    ConfigData = lara_config.read_lara_local_config_file(ConfigFile)
    if ConfigData:
        lara_utils.init_warnings()
        ConfigData.local_files = 'yes'
        return compile_lara_local_resources1(ConfigData)

##def compile_lara_local_resources_full_only(ConfigFile):
##    ConfigData = lara_config.read_lara_local_config_file(ConfigFile)
##    if ConfigData:
##        compile_lara_local_resources_full_only1(ConfigData)

# Version for portal

def compile_lara_local_resources_and_copy(ConfigFile, BaseFile):
    compile_lara_local_resources(ConfigFile)
    copy_local_resources(ConfigFile, BaseFile)

def compile_lara_local_resources_and_copy_and_log_zipfile(ConfigFile, BaseFile, LogDir):
    compile_lara_local_resources_and_copy(ConfigFile, BaseFile)
    log_local_resources_to_timestamped_zipfile(ConfigFile, LogDir)

def log_local_resources_to_timestamped_zipfile(ConfigFile, LogDir):
    try:
        Params = lara_config.read_lara_local_config_file(ConfigFile)
        TimestampedZipfile = f'{LogDir}/resources_{Params.id}_{lara_utils.timestamp()}.zip'
        lara_utils.create_directory_if_it_doesnt_exist(LogDir)
        TmpDir = lara_utils.get_tmp_directory(Params)
        copy_local_resources(ConfigFile, f'{TmpDir}/')
        lara_utils.make_zipfile(TmpDir, TimestampedZipfile)
        lara_utils.delete_directory_if_it_exists(TmpDir)
        if not lara_utils.file_exists(TimestampedZipfile):
            lara_utils.print_and_flush(f'*** Error: something went wrong while trying to create log zipfile {TimestampedZipfile}')
    except Exception as e:
        lara_utils.print_and_flush(f'*** Error: something went wrong when trying to create log zipfile')
        print_and_flush(str(e))
        return False

def copy_local_resources(ConfigFile, BaseFile):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    copy_tmp_files_if_they_exist(ConfigFile,
                                 { 'split': f'{BaseFile}split.json',
                                   'split_mwe': f'{BaseFile}split_mwe.json',

                                   'ldt_word_recording_file': f'{BaseFile}ldt_word_recording.txt',
                                   'ldt_word_recording_file_json': f'{BaseFile}ldt_word_recording.json',

                                   'ldt_segment_recording_file': f'{BaseFile}ldt_segment_recording.txt',
                                   'ldt_segment_recording_file_json': f'{BaseFile}ldt_segment_recording.json',
                                   
                                   'ldt_word_recording_file_full': f'{BaseFile}ldt_word_recording_full.txt',
                                   'ldt_word_recording_file_full_json': f'{BaseFile}ldt_word_recording_full.json',

                                   'ldt_segment_recording_file_full': f'{BaseFile}ldt_segment_recording_full.txt',
                                   'ldt_segment_recording_file_full_json': f'{BaseFile}ldt_segment_recording_full.json',

                                   'tmp_segment_translation_spreadsheet': f'{BaseFile}segment_translations.csv',
                                   'tmp_segment_translation_spreadsheet_json': f'{BaseFile}segment_translations.json',

                                   'tmp_note_spreadsheet': f'{BaseFile}notes.csv',
                                   'tmp_note_spreadsheet_json': f'{BaseFile}notes.json',

                                   'tmp_image_dict_spreadsheet': f'{BaseFile}image_dict.csv',
                                   'tmp_image_dict_spreadsheet_json': f'{BaseFile}image_dict.json',

                                   'tmp_word_locations_file': f'{BaseFile}word_locations.json',
                                   'tmp_word_locations_zipfile': f'{BaseFile}word_locations_zipfile.zip',

                                   'tmp_segment_audio_word_breakpoint_file': f'{BaseFile}tmp_segment_audio_word_breakpoints.csv'
                                   })
    FullWordCSVLemma = lara_utils.get_tmp_csv_file(Params)
    FullWordCSVSurface = lara_utils.get_tmp_csv_file(Params)
    copy_tmp_files_if_they_exist(ConfigFile,
                                 {'tmp_translation_spreadsheet': FullWordCSVLemma,
                                  'tmp_translation_spreadsheet_json': f'{BaseFile}word_translations.json',
                                  'tmp_translation_spreadsheet_surface_type': FullWordCSVSurface,
                                  'tmp_translation_spreadsheet_surface_type_json': f'{BaseFile}word_translations_surface_type.json',
                                  'tmp_translation_spreadsheet_token': f'{BaseFile}word_translations_tokens.csv',
                                  'tmp_translation_spreadsheet_token_json': f'{BaseFile}word_translations_tokens.json'
                                 })
    lara_translations.make_current_only_csv(FullWordCSVLemma, f'{BaseFile}word_translations.csv')
    lara_translations.make_current_only_csv(FullWordCSVSurface, f'{BaseFile}word_translations_surface_type.csv')
    
def compile_lara_local_resources_explicit(ConfigFile, WordRecordingFile, SegmentRecordingFile, WordCSV, SegmentCSV):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    compile_lara_local_resources(ConfigFile)
    FullWordCSV = lara_utils.get_tmp_csv_file(Params)
    copy_tmp_files_if_they_exist(ConfigFile,
                                 {'ldt_word_recording_file_full': WordRecordingFile,
                                  'ldt_segment_recording_file_full': SegmentRecordingFile,
                                  'tmp_translation_spreadsheet': FullWordCSV,
                                  'tmp_segment_translation_spreadsheet': SegmentCSV
                                  })
    lara_translations.make_current_only_csv(FullWordCSV, WordCSV)

def compile_lara_local_resources_explicit_tokens(ConfigFile, WordCSV, WordJSON):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if Params.word_translations_on != 'surface_word_token':
        lara_utils.print_and_flush(f'*** Error: translation mode is not surface_word_token')
        return False
    compile_lara_local_resources(ConfigFile)
    copy_tmp_files_if_they_exist(ConfigFile,
                                {'tmp_translation_spreadsheet_token': WordCSV,
                                 'tmp_translation_spreadsheet_token_json': WordJSON
                                 })
    return True

def compile_lara_local_resources_and_copy_just_tokens_from_types(ConfigFile, BaseFile):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    CleanOK = compile_lara_local_clean(Params)
    if not CleanOK:
        return False
    compile_lara_local_make_word_token_translation_spreadsheet_from_word_type(Params)
    copy_tmp_files_if_they_exist(ConfigFile,
                                {'tmp_translation_spreadsheet_token': f'{BaseFile}word_translations_tokens.csv',
                                 'tmp_translation_spreadsheet_token_json': f'{BaseFile}word_translations_tokens.json'
                                 })
    return True

def upload_picturebook_data(ConfigFile, TmpZipfile, Dir):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if Params == False:
        return False
    lara_picturebook.copy_picturebook_data_to_selector_tool_directory(TmpZipfile, Dir, Params)
    return True

def check_mwe_defs_file(File):
    if lara_mwe.load_mwe_file(File):
        lara_utils.print_and_flush(f'--- MWE definitions file {File} appears to be syntactically correct')
    else:
        lara_utils.print_and_flush(f'*** Error: MWE definitions file {File} appears to be syntactically incorrect')

def mwe_annotate_file_and_copy(ConfigFile, AnnotationsFile):
    Result = mwe_annotate_file(ConfigFile)
    if Result:
        copy_tmp_files_if_they_exist(ConfigFile,
                                     {'tmp_mwe_annotations': AnnotationsFile }
                                     )

def mwe_annotate_file(ConfigFile):
    #mwe_annotate_file1(ConfigFile)
    try:
        return mwe_annotate_file1(ConfigFile)
    except Exception as e:
        lara_utils.print_and_flush(f'*** Error: failed to obtain candidate MWE annotations')
        lara_utils.print_and_flush(str(e))
        return False

def mwe_annotate_file1(ConfigFile):
    ConfigData = lara_config.read_lara_local_config_file(ConfigFile)
    if not ConfigData:
        return False
    if ConfigData.mwe_file == '':
        lara_utils.print_and_flush(f'*** Error: mwe_file is not defined in {ConfigFile}')
        return False
    if not lara_mwe.load_mwe_file(ConfigData.mwe_file):
        return False
    InFile = ConfigData.corpus
    MWEAnnotationsFile = ConfigData.mwe_annotations_file if ConfigData.mwe_annotations_file != '' else False
    if not compile_lara_local_clean(ConfigData):
        return False
    SplitFile = lara_tmp_file('split', ConfigData)
    TraceFile = lara_tmp_file('tmp_mwe_annotations', ConfigData)
    SummaryFile = lara_tmp_file('tmp_mwe_annotations_summary', ConfigData)
    Result = lara_mwe.mark_mwes_in_split_file(SplitFile, MWEAnnotationsFile, TraceFile, ConfigData)
    if Result == False:
        return False
    lara_mwe.mwe_matches_file_to_summary(TraceFile, SummaryFile)
    return Result

def apply_mwe_annotations_and_copy(ConfigFile, TransformedCorpusFile, TraceFile):
    Result = apply_mwe_annotations(ConfigFile)
    if Result:
        copy_tmp_files_if_they_exist(ConfigFile,
                                     { 'mwe_processed_corpus': TransformedCorpusFile,
                                       'mwe_trace': TraceFile }
                                     )
                                 
def apply_mwe_annotations(ConfigFile):
    try:
        return apply_mwe_annotations1(ConfigFile)
    except Exception as e:
        lara_utils.print_and_flush(f'*** Error: failed to apply MWE annotations')
        lara_utils.print_and_flush(str(e))
        return False

def apply_mwe_annotations1(ConfigFile):
    ConfigData = lara_config.read_lara_local_config_file(ConfigFile)
    if not ConfigData:
        return False
    InFile = ConfigData.corpus
    JSONTraceFile = ConfigData.mwe_annotations_file
    if JSONTraceFile == '' or not lara_utils.file_exists(JSONTraceFile):
        lara_utils.print_and_flush(f'*** Error: mwe_annotations_file "{JSONTraceFile}" not found')
        return False
    compile_lara_local_clean(ConfigData)
    SplitFile = lara_tmp_file('split', ConfigData)
    HTMLTraceFile = lara_tmp_file('mwe_trace', ConfigData)
    OutFile0 = lara_tmp_file('mwe_processed_corpus', ConfigData)
    OutFile = change_extension_to_be_same_as_corpus_file(OutFile0, ConfigData)
    return lara_mwe.apply_marked_mwes_in_split_file(SplitFile, JSONTraceFile, OutFile, HTMLTraceFile, ConfigData)

def mwe_annotations_to_ml_data(ConfigFile):
    ConfigData = lara_config.read_lara_local_config_file(ConfigFile)
    if not ConfigData:
        return False
    JSONTraceFile = ConfigData.mwe_annotations_file
    if JSONTraceFile == '' or not lara_utils.file_exists(JSONTraceFile):
        lara_utils.print_and_flush(f'*** Error: mwe_annotations_file "{JSONTraceFile}" not found')
        return False
    MLDataFile = lara_tmp_file('mwe_ml_data', ConfigData)
    return lara_mwe_ml.mwe_annotations_file_to_ml_data(JSONTraceFile, MLDataFile)

##def compile_lara_local_resources_explicit_full(ConfigFile, FullWordRecordingFile, FullSegmentRecordingFile):
##    compile_lara_local_resources_full_only(ConfigFile)
##    copy_tmp_files_if_they_exist(ConfigFile,
##                                 {'ldt_word_recording_file_full': FullWordRecordingFile,
##                                  'ldt_segment_recording_file_full': FullSegmentRecordingFile
##                                  })

# Extract lists of CSS files, script files, img files and audio files used in a corpus file
# and write them out

def find_css_img_and_audio_files(ConfigFile, DataFile):
    ConfigData = lara_config.read_lara_local_config_file(ConfigFile)
    if ConfigData and 'corpus' in ConfigData:
        Data = lara_split_and_clean.extract_css_img_and_audio_files(ConfigData['corpus'], ConfigData)
        if ConfigData['css_file'] and  'css_files' in Data:
            Data['css_files'] += [ ConfigData['css_file'] ]
        if ConfigData['script_file']:
            Data['script_files'] = [ ConfigData['script_file'] ]
        else:
            Data['script_files'] = []
        lara_utils.write_json_to_file(Data, DataFile)                           

# Explicit version for portal: only extract img and audio files,
# since the rest of it needs to come from the config file, which won't exist yet
def find_css_img_and_audio_files_explicit(CorpusFile, DataFile):
    ConfigData = lara_config.default_params()
    Data = lara_split_and_clean.extract_css_img_and_audio_files(CorpusFile, ConfigData)
    Data['script_files'] = []
    lara_utils.write_json_to_file(Data, DataFile)                           
	
## After doing this, you will typically have to record on LDT, add translations, etc

# Local compile (i.e. all resources on local machine), part 2. Makes word pages
def compile_lara_local_word_pages(ConfigFile):
    ConfigData = lara_config.read_lara_local_config_file(ConfigFile)
    if ConfigData:
        lara_utils.init_warnings()
        compile_lara_local_word_pages1(ConfigData)
    if ConfigData.abstract_html == 'plain_via_abstract_html':
        lara_utils.print_and_flush(f'--- CREATING HTML PAGES FROM ABSTRACT HTML FILE')
        lara_abstract_html.abstract_html_to_html(ConfigFile, 'from_config')

def compile_lara_local_abstract_html(ConfigFile):
    ConfigData = lara_config.read_lara_local_config_file(ConfigFile)
    if ConfigData:
        ConfigData.abstract_html = 'abstract_html_only'
        compile_lara_local_word_pages1(ConfigData)

def compile_lara_local_abstract_html_specific_format(ConfigFile, Format):
    if not Format in ( 'pickle', 'json' ):
        lara_utils.print_and_flush(f'*** Error: abstract HTML format "{Format}" needs to be "pickle" or "json"')
        return False
    AbstractHTMLFormat = 'pickle_only' if Format == 'pickle' else 'json_only'
    ConfigData = lara_config.read_lara_local_config_file(ConfigFile)
    if ConfigData:
        ConfigData.abstract_html = 'abstract_html_only'
        ConfigData.abstract_html_format = AbstractHTMLFormat
        compile_lara_local_word_pages1(ConfigData)

def compile_lara_local_abstract_html_zipfile(ConfigFile, Format, Zipfile):
    if not Format in ( 'pickle', 'json' ):
        lara_utils.print_and_flush(f'*** Error: abstract HTML format "{Format}" needs to be "pickle" or "json"')
        return False
    compile_lara_local_abstract_html_specific_format(ConfigFile, Format)
    lara_abstract_html.abstract_html_to_html_zipfile(ConfigFile, Format, Zipfile)

# Distributed compile (i.e. resources spread out on web)
#
# AllLARAResourcesFile   JSON file with URLs for resources
# ReaderDataFile         JSON file with reading progress and preferences for user
# DistributedConfigFile  JSON file with default config values for distributed LARA
# ReaderId               Which reader 
# L2                     Which L2
#
# Compile LARA pages for ReaderId's reading progress in L2
def compile_lara_reading_history_from_config_file(ConfigFile):
    ConfigData = lara_config.read_lara_distributed_config_file(ConfigFile)
    if ConfigData:
        return compile_lara_reading_history(ConfigData)
    else:
        return False

def compile_lara_reading_history(ConfigData):
	return compile_lara_reading_history1(ConfigData)

# Plain version for reading portal: recompile everything, but produce pages in reading portal format
def compile_lara_reading_history_for_portal(ConfigData):
	ConfigData.for_reading_portal = 'yes'
	return compile_lara_reading_history1(ConfigData)

# 'Recompile' version for reading portal: reuse cached data where possible

def recompile_lara_reading_history_for_portal(ConfigData, NewPage):
	ConfigData.for_reading_portal = 'yes'
	ConfigData.recompile = NewPage
	return compile_lara_reading_history1(ConfigData)

# --------------------------------------------------------

def count_audio_and_translation_files_and_print(ConfigFile, AnswerFile):
    lara_utils.write_json_to_file(count_audio_and_translation_files(ConfigFile), AnswerFile)

def count_audio_and_translation_files(ConfigFile):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if not Params:
        return False
    if Params.corpus == '':
        lara_utils.print_and_flush(f'*** Error: unable to internalise corpus data since "corpus" not defined in {ConfigFile}')
        return False
    return count_audio_and_translation_files_for_params(Params)

def count_audio_and_translation_files_for_params(Params):
    Params.split_file = lara_tmp_file('split', Params)
    AudioData = lara_audio.count_recorded_files(Params)
    TransData = lara_translations.count_translations(Params)
    if not AudioData or not isinstance(AudioData, dict) or \
       not 'words' in AudioData or not 'recorded' in AudioData['words'] or not 'not_recorded' in AudioData['words'] or \
       not 'segments' in AudioData or not 'recorded' in AudioData['segments'] or not 'not_recorded' in AudioData['segments']:
        lara_utils.print_and_flush(f'*** Error: malformed response from lara_audio.count_recorded_files')
        lara_utils.prettyprint(AudioData)
        return False
    if not TransData or not isinstance(TransData, dict) or \
       not 'words' in TransData or not 'translated' in TransData['words'] or not 'not_translated' in TransData['words'] or \
       not 'segments' in TransData or not 'translated' in TransData['segments'] or not 'not_translated' in TransData['segments']:
        lara_utils.print_and_flush(f'*** Error: malformed response from lara_translations.count_audio_and_translation_files_for_params')
        lara_utils.prettyprint(TransData)
        return False
    return {'words': {'recorded': AudioData['words']['recorded'],
                      'not_recorded': AudioData['words']['not_recorded'],
                      'translated': TransData['words']['translated'],
                      'not_translated': TransData['words']['not_translated']
                      },
            'segments': {'recorded': AudioData['segments']['recorded'],
                         'not_recorded': AudioData['segments']['not_recorded'],
                         'translated': TransData['segments']['translated'],
                         'not_translated': TransData['segments']['not_translated']
                      }
            }

# --------------------------------------------------------

def segment_unsegmented_corpus1(ConfigData):
    if ConfigData.unsegmented_corpus != '':
        UnsegmentedCorpusFile = ConfigData.unsegmented_corpus        
    else:
        lara_utils.print_and_flush(f'*** Error: "unsegmented_corpus" not defined in config data')
        return False
    if not lara_utils.file_exists(UnsegmentedCorpusFile):
        lara_utils.print_and_flush(f'*** Error: unable to find unsegmented corpus file {UnsegmentedCorpusFile}')
        return False
    if ConfigData.untagged_corpus != '':
        UntaggedCorpusFile = ConfigData.untagged_corpus        
    else:
        lara_utils.print_and_flush('*** Error: "untagged_corpus" not defined in config data')
        return False
    segment_unsegmented_corpus1_explicit(UnsegmentedCorpusFile, UntaggedCorpusFile, ConfigData)

def segment_unsegmented_corpus1_explicit(UnsegmentedCorpusFile, UntaggedCorpusFile, ConfigData):
    Language = ConfigData.language
    ## Chinese and Japanese are different
    if lara_chinese.is_chinese_language(Language):
        lara_chinese.segment_file_using_chinese_tokeniser(UnsegmentedCorpusFile, UntaggedCorpusFile, ConfigData)
    elif Language == 'japanese':
        lara_japanese.sentence_segment_japanese_file(UnsegmentedCorpusFile, UntaggedCorpusFile)
    else:
        lara_segment.segment_file(UnsegmentedCorpusFile, UntaggedCorpusFile)

# --------------------------------------------------------

## Do a structured diff between the corpus file that ConfigFile points to and an earlier version OldTaggedFile,
## and write everything out as Zipfile
def diff_tagged_corpus(OldTaggedFile, ConfigFile, Zipfile):
    import lara_compare_split_files
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if not Params:
        return False
    OldConfigFile = make_config_file_with_variant_corpus(ConfigFile, OldTaggedFile, Params)
    if not OldConfigFile:
        return False
    OldSplitFile = make_split_file(OldConfigFile)
    CurrentSplitFile = make_split_file(ConfigFile)
    if not OldSplitFile or not CurrentSplitFile:
        return False
    TmpDir = lara_utils.get_tmp_directory(Params)
    SurfaceDiffFile = f'{TmpDir}/surface_diff.txt'
    LemmaDiffFile = f'{TmpDir}/lemma_diff.txt'
    SurfaceAndLemmaDiffFile = f'{TmpDir}/surface_and_lemma_diff.txt'
    SummaryFile = f'{TmpDir}/summary.json'
    SurfaceChanged = lara_compare_split_files.split_files_diff(OldSplitFile, CurrentSplitFile, 'surface', SurfaceDiffFile)
    LemmaChanged = lara_compare_split_files.split_files_diff(OldSplitFile, CurrentSplitFile, 'lemma', LemmaDiffFile)
    lara_compare_split_files.split_files_diff(OldSplitFile, CurrentSplitFile, 'surface_and_lemma', SurfaceAndLemmaDiffFile)
    Summary = {'surface_changed': SurfaceChanged, 'lemma_changed': LemmaChanged}
    lara_utils.write_json_to_file(Summary, SummaryFile)
    lara_utils.make_zipfile(TmpDir, Zipfile)
    lara_utils.delete_file_if_it_exists(OldConfigFile)
    lara_utils.delete_directory_if_it_exists(TmpDir)
    lara_utils.print_and_flush(f'\nSUMMARY\n')
    lara_utils.print_and_flush(f'Surface words changed: {SurfaceChanged}')
    lara_utils.print_and_flush(f'Lemmas changed:        {LemmaChanged}')
    lara_utils.print_and_flush(f'Full details:          {Zipfile}')
    return True

def make_config_file_with_variant_corpus(ConfigFile, OldTaggedFile, Params):
    Content = lara_utils.read_json_file(ConfigFile)
    if not 'id' in Content:
        return False
    Id = Content['id']
    Content['id'] = f'{Id}_old'
    Content['corpus'] = OldTaggedFile
    VariantConfigFile = lara_utils.get_tmp_file_with_extension(Params, 'json')
    lara_utils.write_json_to_file(Content, VariantConfigFile)
    return VariantConfigFile
    

def make_split_file(ConfigFile):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if not Params:
        return False
    if not compile_lara_local_clean(Params):
        return False
    SplitFile = lara_tmp_file('split', Params)
    if SplitFile and lara_utils.file_exists(SplitFile):
        return SplitFile
    else:
        return False

# --------------------------------------------------------

def treetag_untagged_corpus_file1(ConfigData):
    tag_untagged_corpus_file1(ConfigData, 'treetag')

def minimal_tag_untagged_corpus_file1(ConfigData):
    tag_untagged_corpus_file1(ConfigData, 'minimal_tag')

def tag_untagged_corpus_file1(ConfigData, Mode):
    if  ConfigData.language:
        Language = ConfigData.language
    else:
        lara_utils.print_and_flush('*** Error: "language" not defined in config data')
        return False
    if ConfigData.untagged_corpus:
        UntaggedCorpusFile = lara_config_file('untagged_corpus', ConfigData)        
    else:
        lara_utils.print_and_flush('*** Error: "untagged_corpus" not defined in config data')
        return False
    if ConfigData.tagged_corpus:
        TaggedCorpusFile = lara_config_file('tagged_corpus', ConfigData)
    else:
        TaggedCorpusFile = lara_config_file('corpus', ConfigData)
    if Mode == 'treetag':
        lara_treetagger.treetag_lara_file_main(Language, UntaggedCorpusFile, ConfigData, TaggedCorpusFile)
    elif Mode == 'minimal_tag':
        lara_minimal_tag.minimal_tag_lara_file_main(UntaggedCorpusFile, ConfigData, TaggedCorpusFile)
    else:
        lara_utils.print_and_flush(f'*** Error: unknown tagging mode {Mode}')

def treetag_tagged_corpus_file_add_pos1(ConfigData):
    if  ConfigData.language:
        Language = ConfigData.language
    else:
        lara_utils.print_and_flush(f'*** Error: "language" not defined in config data')
        return False
    CorpusFile = ConfigData.corpus
    if not lara_utils.file_exists(CorpusFile):
        lara_utils.print_and_flush(f'*** Error: corpus file {CorpusFile} not found')
        return False
    ( Base, Extension ) = lara_utils.file_to_base_file_and_extension(ConfigData.corpus)
    RetaggedCorpusFile = f'{Base}_with_POS.{Extension}'
    ConfigData.add_postags_to_lemma = 'yes'
    ConfigData.retagging_strategy = 'replace_pos'
    lara_treetagger.treetag_lara_file_main(Language, CorpusFile, ConfigData, RetaggedCorpusFile)

def treetag_tagged_corpus_file_remove_mwe1(ConfigData):
    if  ConfigData.language:
        Language = ConfigData.language
    else:
        lara_utils.print_and_flush(f'*** Error: "language" not defined in config data')
        return False
    CorpusFile = ConfigData.corpus
    if not lara_utils.file_exists(CorpusFile):
        lara_utils.print_and_flush(f'*** Error: corpus file {CorpusFile} not found')
        return False
    ( Base, Extension ) = lara_utils.file_to_base_file_and_extension(ConfigData.corpus)
    RetaggedCorpusFile = f'{Base}_without_mwe.{Extension}'
    ConfigData.retagging_strategy = 'remove_mwe'
    lara_treetagger.treetag_lara_file_main(Language, CorpusFile, ConfigData, RetaggedCorpusFile)

# --------------------------------------------------------  

def compile_lara_local_resources1(ConfigData):
    CleanOK = compile_lara_local_clean(ConfigData)
    if CleanOK:
        ConfigData.count_file = lara_tmp_file('count', ConfigData)
        ConfigData.surface_count_file = lara_tmp_file('surface_count', ConfigData)
        compile_lara_local_count_file(ConfigData)
        compile_lara_local_surface_count_file(ConfigData)
        compile_lara_local_make_segment_recording_file(ConfigData)
        compile_lara_local_segment_audio_word_breakpoint_file(ConfigData)
        compile_lara_local_make_word_recording_file(ConfigData)
        compile_lara_local_make_translation_spreadsheet(ConfigData)
        compile_lara_local_make_segment_translation_spreadsheet(ConfigData)
        compile_lara_local_make_note_spreadsheet(ConfigData)
        compile_lara_local_make_image_dict_spreadsheet(ConfigData)
        compile_lara_local_make_word_locations_file(ConfigData)
        return True
    else:
        lara_utils.print_and_flush('*** Error: something went wrong when reading corpus file')
        return False

##def compile_lara_local_resources_full_only1(ConfigData):
##    CleanOK = compile_lara_local_clean(ConfigData)
##    if CleanOK:
##        compile_lara_local_count_file(ConfigData)
##        compile_lara_local_make_segment_and_word_recording_files_full(ConfigData)

def compile_lara_local_word_pages1(ConfigData):
    compile_lara_local_make_word_pages(ConfigData)

def compile_lara_reading_history1(ConfigData):
    if not ConfigData:
        lara_utils.print_and_flush('*** Error: unable to internalise config file')
        return False
    # Create an empty word pages directory, where the results will go
    compile_lara_reading_history_initialise_word_pages_dir(ConfigData)
    # Call Python to download the metadata (audio, images, translations) and also the corpora
    MetaMetaData = compile_lara_reading_history_download_metadata(ConfigData)
    if not MetaMetaData:
        return False
    # Store the downloaded metadata so that we can use it later
    compile_lara_reading_history_store_metadata(MetaMetaData)
    # Combine the downloaded corpus metadata into a single corpus that's split into segments
    CorpusOK = compile_lara_reading_history_make_split_corpus(ConfigData, MetaMetaData)
    if not CorpusOK:
        return False
    # Get some frequency statistics and save them
    compile_lara_reading_history_count_file(ConfigData)
    # And finally, build the web pages and return the result
    return compile_lara_reading_history_make_word_pages(ConfigData)

# --------------------------------------------------------

def delete_metadata_directory(ConfigFile):
    ConfigData = lara_config.read_lara_distributed_config_file(ConfigFile)
    TmpMetadataDir = lara_tmp_dir('metadata_dir', ConfigData)
    lara_utils.delete_directory_if_it_exists(TmpMetadataDir)

# --------------------------------------------------------

def compile_lara_reading_history_initialise_word_pages_dir(ConfigData):
    WordPagesDir = lara_compiled_dir('word_pages_directory', ConfigData)
    if ConfigData.recompile:
        # If we're recompiling, try to use the existing directory 
        lara_utils.create_directory_if_it_doesnt_exist(WordPagesDir)
    else:
        # If we're compiling, create a new directory directory 
        lara_utils.create_directory_deleting_old_if_necessary(WordPagesDir)        

def compile_lara_reading_history_download_metadata(ConfigData):
    ResourcesFile = ConfigData.resource_file
    ReadingHistory = ConfigData.reading_history
    TmpMetadataDir = lara_tmp_dir('metadata_dir', ConfigData)
    ConfigData.metadata_directory = TmpMetadataDir
    if ConfigData.recompile:
        # If we're recompiling, try to use the existing directory 
        lara_utils.create_directory_if_it_doesnt_exist(TmpMetadataDir)
    else:
        # If we're compiling, create a new directory  
        lara_utils.create_directory_deleting_old_if_necessary(TmpMetadataDir)    
    lara_download_metadata.download_metadata(ResourcesFile, ReadingHistory, ConfigData)
    return get_metametadata(TmpMetadataDir)

def get_metametadata(TmpDir):
    File = metametadata_file_in_tmp_directory(TmpDir)
    if lara_utils.file_exists(File):
        MetaMetaData = lara_utils.read_json_file(File)
        lara_utils.print_and_flush(f'--- Read metametadata from {File}')
        return MetaMetaData
    else:
        lara_utils.print_and_flush(f'*** Error: unable to find metametadata file {File}')
        return False                      
                                   
def metametadata_file_in_tmp_directory(TmpDir):
    return f'{TmpDir}/metametadata.json'

def compile_lara_reading_history_store_metadata(MetaMetaData):
    lara_distributed.store_downloaded_metadata(MetaMetaData)

# --------------------------------------------------------

def download_resource(ResourceId, ResourcesFile, TargetDir):
    ResourceData = lara_utils.read_json_file(ResourcesFile)
    if not ResourceData:
        return False
    if not ResourceId in ResourceData:
        lara_utils.print_and_flush(f'*** Error: {ResourceId} is not defined in {ResourcesFile}')
        return False
    URL = ResourceData[ResourceId][0]
    lara_download_resource.download_resource(URL, TargetDir)

# --------------------------------------------------------

def compile_lara_local_clean(ConfigData):
    CorpusFile = lara_config_file('corpus', ConfigData)
    SplitFile = lara_tmp_file('split', ConfigData)
    TaggingFeedbackFile = lara_tmp_file('tagging_feedback', ConfigData)
    PlayPartsFile = lara_tmp_file('recording_string_play_parts', ConfigData)
    MainResult = lara_split_and_clean.clean_lara_file(CorpusFile, ConfigData, SplitFile, TaggingFeedbackFile)
    if MainResult == False:
        return False
    if ConfigData.play_parts == []:
        return True
    return lara_drama.make_play_part_file(SplitFile, ConfigData.play_parts, PlayPartsFile, ConfigData)

# As above, but do it on the tagged file rather than on the corpus file
def compile_lara_local_clean_on_tagged_file(ConfigData):
    CorpusFile = ConfigData.tagged_corpus
    SplitFile = lara_tmp_file('tagged_split', ConfigData)
    TaggingFeedbackFile = lara_tmp_file('tagging_feedback', ConfigData)
    return lara_split_and_clean.clean_lara_file(CorpusFile, ConfigData, SplitFile, TaggingFeedbackFile)

def compile_lara_reading_history_make_split_corpus(ConfigData, MetaMetaData):
    ReadingHistory = ConfigData.reading_history
    SplitFile = lara_tmp_file('split', ConfigData)
    return lara_distributed.make_split_corpus_from_downloaded_metadata(ReadingHistory, MetaMetaData, SplitFile, ConfigData)

# --------------------------------------------------------

def compile_lara_local_count_file(ConfigData):
    SplitFile = lara_tmp_file('split', ConfigData)
    CountFile = lara_tmp_file('count', ConfigData)
    lara.count_file(SplitFile, CountFile, ConfigData)

def compile_lara_local_surface_count_file(ConfigData):
    SplitFile = lara_tmp_file('split', ConfigData)
    CountFile = lara_tmp_file('surface_count', ConfigData)
    lara.surface_count_file(SplitFile, CountFile, ConfigData)

def compile_lara_reading_history_count_file(ConfigData):
    compile_lara_local_count_file(ConfigData)

# --------------------------------------------------------

def compile_lara_local_make_lemma_dictionary_spreadsheet(ConfigData):
    if ConfigData.lemma_dictionary_spreadsheet != '' and ConfigData.untagged_corpus != '':
        UntaggedCorpusFile = ConfigData.untagged_corpus
        LemmaFile = lara_tmp_file('lemma_dictionary_file', ConfigData)
        return lara_minimal_tag.make_lemma_dictionary_file(UntaggedCorpusFile, LemmaFile, ConfigData)
    else:
        return False
    
# --------------------------------------------------------

def combine_play_segment_audio(ConfigFile):
    ConfigData = lara_config.read_lara_local_config_file(ConfigFile)
    if ConfigData == False:
        return False
    CleanOk = compile_lara_local_clean(ConfigData)
    if CleanOk == False:
        return False
    lara_drama.combine_play_segment_audio(ConfigData)

def find_unrecorded_play_lines(ConfigFile):
    ConfigData = lara_config.read_lara_local_config_file(ConfigFile)
    if ConfigData == False:
        return False
    CleanOk = compile_lara_local_clean(ConfigData)
    if CleanOk == False:
        return False
    lara_drama.find_unrecorded_lines_in_play(ConfigData)

# --------------------------------------------------------
   
def compile_lara_local_make_segment_recording_file(ConfigData):
    if 'segment_audio_directory' in ConfigData:
        SplitFile = lara_tmp_file('split', ConfigData)
        LDTFile = lara_tmp_file('ldt_segment_recording_file', ConfigData)
        lara_audio.make_recording_file(SplitFile, LDTFile, 'new_only', ConfigData)
        LDTFileFull = lara_tmp_file('ldt_segment_recording_file_full', ConfigData)
        lara_audio.make_recording_file(SplitFile, LDTFileFull, 'full', ConfigData)

##def compile_lara_local_make_segment_recording_file(ConfigData):
##    if 'segment_audio_directory' in ConfigData:
##        SplitFile = lara_tmp_file('split', ConfigData)
##        LDTFile = lara_tmp_file('ldt_segment_recording_file', ConfigData)
##        lara_audio.make_recording_file(SplitFile, LDTFile, 'full', ConfigData)

# --------------------------------------------------------
    
def compile_lara_local_make_word_recording_file(ConfigData):
    if 'word_audio_directory' in ConfigData:
        SplitFile = lara_tmp_file('split', ConfigData)
        LDTFile = lara_tmp_file('ldt_word_recording_file', ConfigData)
        lara_audio.make_word_recording_file(SplitFile, LDTFile, 'new_only', ConfigData)
        LDTFileFull = lara_tmp_file('ldt_word_recording_file_full', ConfigData)
        lara_audio.make_word_recording_file(SplitFile, LDTFileFull, 'full', ConfigData)

##def compile_lara_local_make_word_recording_file(ConfigData):
##    if 'word_audio_directory' in ConfigData:
##        SplitFile = lara_tmp_file('split', ConfigData)
##        LDTFile = lara_tmp_file('ldt_word_recording_file', ConfigData)
##        lara_audio.make_word_recording_file(SplitFile, LDTFile, 'full', ConfigData)

# --------------------------------------------------------

##def compile_lara_local_make_segment_and_word_recording_files_full(ConfigData):
##    if 'segment_audio_directory' in ConfigData:
##        SplitFile = lara_tmp_file('split', ConfigData)
##        LDTFileFull = lara_tmp_file('ldt_segment_recording_file_full', ConfigData)
##        lara_audio.make_recording_file(SplitFile, LDTFileFull, 'full', ConfigData)
##    if 'word_audio_directory' in ConfigData:
##        SplitFile = lara_tmp_file('split', ConfigData)
##        LDTFileFull = lara_tmp_file('ldt_word_recording_file_full', ConfigData)
##        lara_audio.make_word_recording_file(SplitFile, LDTFileFull, 'full', ConfigData)
    
# --------------------------------------------------------

def compile_lara_local_segment_audio_word_breakpoint_file(ConfigData):
    if 'segment_audio_word_breakpoint_csv' in ConfigData:
        SplitFile = lara_tmp_file('split', ConfigData)
        BreakpointFile = lara_tmp_file('tmp_segment_audio_word_breakpoint_file', ConfigData)
        lara_audio.make_segment_audio_word_breakpoint_csv(SplitFile, BreakpointFile, ConfigData)

# --------------------------------------------------------
    
def compile_lara_local_make_translation_spreadsheet(ConfigData):
    SplitFile = lara_tmp_file('split', ConfigData)
    for ( WordTranslationsOn, TmpSpreadsheetId ) in [ ( 'lemma', 'tmp_translation_spreadsheet' ),
                                                      ( 'surface_word_type', 'tmp_translation_spreadsheet_surface_type' ),
                                                      ( 'surface_word_token', 'tmp_translation_spreadsheet_token' )
                                                      ]:
        ConfigData1 = copy.copy(ConfigData)
        ConfigData1.word_translations_on = WordTranslationsOn
        TmpTranslationFile = lara_tmp_file(TmpSpreadsheetId, ConfigData)
        lara_utils.print_and_flush(f'--- MAKING TMP WORD TRANSLATION FILES ({WordTranslationsOn})')
        lara_translations.make_translation_spreadsheet(SplitFile, TmpTranslationFile, ConfigData1)

def compile_lara_local_make_word_token_translation_spreadsheet_from_word_type(ConfigData):
    SplitFile = lara_tmp_file('split', ConfigData)
    ConfigData1 = copy.copy(ConfigData)
    # We are going to discard the existing word token data and fill in everything fresh from the word type files
    ConfigData1.ignore_existing_word_token_data = 'yes'
    ConfigData1.word_translations_on = 'surface_word_token'
    TmpTranslationFile = lara_tmp_file('tmp_translation_spreadsheet_token', ConfigData)
    lara_utils.print_and_flush(f'--- MAKING TMP WORD TOKEN TRANSLATION FILES FROM WORD TYPE TRANSLATION FILES')
    lara_translations.make_translation_spreadsheet(SplitFile, TmpTranslationFile, ConfigData1)

# --------------------------------------------------------
    
def compile_lara_local_make_segment_translation_spreadsheet(ConfigData):
    SplitFile = lara_tmp_file('split', ConfigData)
    TmpTranslationFile = lara_tmp_file('tmp_segment_translation_spreadsheet', ConfigData)
    lara_utils.print_and_flush(f'--- MAKING TMP SEGMENT TRANSLATION FILES')
    lara_translations.make_segment_translation_spreadsheet(SplitFile, TmpTranslationFile, ConfigData)

# --------------------------------------------------------
    
def compile_lara_local_make_note_spreadsheet(ConfigData):
    SplitFile = lara_tmp_file('split', ConfigData)
    TmpTranslationFile = lara_tmp_file('tmp_note_spreadsheet', ConfigData)
    lara_utils.print_and_flush(f'--- MAKING NOTE FILE')
    lara_translations.make_note_spreadsheet(SplitFile, TmpTranslationFile, ConfigData)

# --------------------------------------------------------
    
def compile_lara_local_make_image_dict_spreadsheet(ConfigData):
    SplitFile = lara_tmp_file('split', ConfigData)
    TmpTranslationFile = lara_tmp_file('tmp_image_dict_spreadsheet', ConfigData)
    lara_utils.print_and_flush(f'--- MAKING IMAGE DICT FILE')
    lara_translations.make_image_dict_spreadsheet(SplitFile, TmpTranslationFile, ConfigData)

# --------------------------------------------------------

def compile_lara_local_make_word_locations_file(ConfigData):
    SplitFile = lara_tmp_file('split', ConfigData)
    TmpWordLocationFile = lara_tmp_file('tmp_word_locations_file', ConfigData)
    TmpZipfile = lara_tmp_file('tmp_word_locations_zipfile', ConfigData)
    lara_utils.print_and_flush(f'--- MAKING WORD LOCATIONS FILE AND WORD LOCATIONS ZIPFILE')
    lara_picturebook.make_tmp_picturebook_word_location_file_and_word_location_zipfile(SplitFile, TmpWordLocationFile, TmpZipfile, ConfigData)

# --------------------------------------------------------

def make_phonetic_version_of_corpus(ConfigFile):
    import lara_phonetic
    ConfigData = lara_config.read_lara_local_config_file(ConfigFile)
    if ConfigData == False:
        return
    if ConfigData.phonetic_text == 'yes':
        lara_utils.print_and_flush(f'*** Error: already marked as a phonetic corpus, nothing to do')
    TmpPhoneticCorpusFile = lara_tmp_file('tmp_phonetic_corpus', ConfigData)
    TmpPhoneticAlignedTextFile = lara_tmp_file('tmp_phonetic_aligned_text', ConfigData)
    TmpPhoneticAlignedLexiconFile = lara_tmp_file('tmp_phonetic_aligned_lexicon', ConfigData)
    lara_phonetic.make_phonetic_version_of_corpus_file_and_tmp_files(TmpPhoneticCorpusFile, TmpPhoneticAlignedTextFile,
                                                                     TmpPhoneticAlignedLexiconFile, ConfigFile)

# --------------------------------------------------------

def make_labelled_corpus_file(ConfigFile):
    import lara_align_from_audio
    ConfigData = lara_config.read_lara_local_config_file(ConfigFile)
    if ConfigData == False:
        return
    LabelledFile = ConfigData.labelled_source_corpus
    if LabelledFile == '':
        lara_utils.print_and_flush(f'*** Error: "labelled_corpus_source" not defined in config file')
    lara_align_from_audio.create_corpus_with_numbered_labels(ConfigFile, LabelledFile)

# --------------------------------------------------------

def cut_up_audio(ConfigFile, AudioId):
    import lara_align_from_audio
    lara_align_from_audio.create_aligned_files_from_config_file(ConfigFile, AudioId)

def cut_up_audio_without_text(ConfigFile, AudioId):
    import lara_align_from_audio
    lara_align_from_audio.cut_up_audio_without_text_from_config_file(ConfigFile, AudioId)

# --------------------------------------------------------

def compile_lara_local_make_word_pages(ConfigData):
    SplitFile = lara_tmp_file('split', ConfigData)
    CountFile = lara_tmp_file('count', ConfigData)
    WordPageDir = lara_compiled_dir('word_pages_directory', ConfigData)
    ConfigData.local_files = 'yes'
    ConfigData.split_file = SplitFile
    ConfigData.count_file = CountFile
    ConfigData.word_pages_directory = WordPageDir
    lara.make_word_pages(ConfigData)
    
# --------------------------------------------------------

def compile_lara_reading_history_make_word_pages(ConfigData):
    SplitFile = lara_tmp_file('split', ConfigData)
    CountFile = lara_tmp_file('count', ConfigData)
    CompileCacheFile = lara_tmp_file('compile_cache', ConfigData)
    WordPageDir = lara_compiled_dir('word_pages_directory', ConfigData)
    ConfigData.split_file = SplitFile
    ConfigData.count_file = CountFile
    ConfigData.compile_cache_file = CompileCacheFile
    ConfigData.word_pages_directory = WordPageDir
    return lara.make_word_pages(ConfigData)

# --------------------------------------------------------

def format_word_token_spreadsheet_as_html(ConfigFile):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if Params == False:
        return False
    if Params.translation_spreadsheet_tokens == '':
        lara_utils.print_and_flush(f'*** Error: translation_spreadsheet_tokens not define in config file')
        return False
    WordCSV = Params.translation_spreadsheet_tokens
    ( Base, Extension ) = lara_utils.file_to_base_file_and_extension(WordCSV)
    HTMLFile = f'{Base}.html'
    LinesPerPage = 5
    MaxLineLength = 10
    lara_format_word_token_file.format_word_token_spreadsheet_as_html(WordCSV, LinesPerPage, MaxLineLength,
                                                                      ConfigFile, HTMLFile)
    return True

# --------------------------------------------------------

def copy_tmp_files_if_they_exist(ConfigFile, Dict):
    lara_utils.print_and_flush('--- COPYING GENERATED RESOURCE FILES')
    ConfigData = lara_config.read_lara_local_config_file(ConfigFile)
    if not ConfigData:
        lara_utils.print_and_flush(f'*** Error: unable to read config file {ConfigFile}, so can\'t copy anything')
        return False
    for Key in Dict:
        FromFile = lara_tmp_file(Key, ConfigData)
        ToFile = Dict[Key]
        if lara_utils.file_exists(FromFile):
            lara_utils.copy_file(FromFile, ToFile)
            lara_utils.print_and_flush(f'--- Copied "{Key}" file to {ToFile}')
        else:
            lara_utils.print_and_flush(f'*** Warning: tmp file "{FromFile}" not found, so cannot copy to {ToFile}')

def lara_config_file_defined(Key, ConfigData):
    return Key in ConfigData

def lara_config_file(Key, ConfigData):
    if Key in ConfigData:
        return ConfigData[Key]
    else:
        lara_utils.print_and_flush(f'*** Error: key "{Key}" not defined in config data')
        return False

def lara_config_dir(Key, ConfigData):
    if Key in ConfigData:
        return ConfigData[Key]
    else:
        lara_utils.print_and_flush(f'*** Error: key "{Key}" not defined in config data')
        return False

def lara_config_value(Key, ConfigData):
    if Key in ConfigData:
        return ConfigData[Key]
    else:
        lara_utils.print_and_flush(f'*** Error: key "{Key}" not defined in config data')
        return False

def lara_tmp_file(Key, ConfigData):
    File0 = lara_tmp_file_for_id(Key,
                                 lara_config_value('id', ConfigData),
                                 lara_config_value('lara_tmp_directory', ConfigData))
    return maybe_adjust_extension_of_tmp_file(File0, Key, ConfigData)

def maybe_adjust_extension_of_tmp_file(File, Key, ConfigData):
    if Key in tmp_files_that_need_to_have_same_extension_as_corpus_file:
        ExtensionOfCorpusFile = lara_utils.extension_for_file(ConfigData.corpus)
        return lara_utils.change_extension(File, ExtensionOfCorpusFile)
    else:
        return File

# This is needed for passing multimedia file names to web apps, which will add a suitable prefix
def short_multimedia_dir(Params):
    WordPagesDir = lara_short_compiled_dir_for_id('word_pages_directory', Params.id)
    return f'{WordPagesDir}/multimedia'

def lara_tmp_file_for_id(Key, Id, TmpDir):
    return f'{TmpDir}/{Id}_{base_name_for_lara_tmp_file(Key)}'  

def lara_tmp_dir(Key, ConfigData):
    return lara_tmp_dir_for_id(Key,
                               lara_config_value('id', ConfigData),
                                lara_config_value('lara_tmp_directory', ConfigData))

def lara_tmp_dir_for_id(Key, Id, TmpDir):
    return f'{TmpDir}/{Id}_{base_name_for_lara_tmp_dir(Key)}'

def lara_compiled_dir(Key, ConfigData):
    return lara_compiled_dir_for_id(Key,
                                    lara_config_value('id', ConfigData),
                                    lara_config_value('compiled_directory', ConfigData))

def lara_short_compiled_dir(Key, ConfigData):
    return lara_short_compiled_dir_for_id(Key,
                                          lara_config_value('id', ConfigData))

def lara_compiled_dir_for_id(Key, Id, CompiledDir):
    return f'{CompiledDir}/{Id}{base_name_for_lara_compiled_dir(Key)}'   

def lara_short_compiled_dir_for_id(Key, Id):
    return f'{Id}{base_name_for_lara_compiled_dir(Key)}'   

base_names_for_lara_tmp_file = {'lemma_dictionary_file': 'tmp_lemma_dictionary.csv',
                                'split': 'split.json',
                                'tagged_split': 'tagged_split.json',
                                'split_mwe': 'split_mwe.json',
                                'tagging_feedback': 'tagging_feedback.txt',
                                'count': 'count.json',
                                'surface_count': 'surface_count.json',
                                'compile_cache': 'compile_cache.data.gz',
                                'abstract_html_file': 'abstract_html.data.gz',
                                # Only for testing
                                'abstract_html_json_file': 'abstract_html.json',
                                
                                'ldt_segment_recording_file': 'record_segments.txt',
                                'ldt_segment_recording_file_json': 'record_segments.json',
                                
                                'ldt_word_recording_file': 'record_words.txt',
                                'ldt_word_recording_file_json': 'record_words.json',
                                
                                'ldt_segment_recording_file_full': 'record_segments_full.txt',
                                'ldt_segment_recording_file_full_json': 'record_segments_full.json',
                                
                                'ldt_word_recording_file_full': 'record_words_full.txt',
                                'ldt_word_recording_file_full_json': 'record_words_full.json',
                                
                                'tmp_translation_spreadsheet': 'tmp_translations.csv',
                                'tmp_translation_spreadsheet_json': 'tmp_translations.json',
                                
                                'tmp_translation_spreadsheet_surface_type': 'tmp_translations_surface_type.csv',
                                'tmp_translation_spreadsheet_surface_type_json': 'tmp_translations_surface_type.json',

                                'tmp_translation_spreadsheet_token': 'tmp_translations_token.csv',
                                'tmp_translation_spreadsheet_token_json': 'tmp_translations_token.json',
                                
                                'tmp_segment_translation_spreadsheet': 'tmp_segment_translations.csv',
                                'tmp_segment_translation_spreadsheet_json': 'tmp_segment_translations.json',

                                'tmp_note_spreadsheet': 'tmp_notes.csv',
                                'tmp_note_spreadsheet_json': 'tmp_notes.json',

                                'tmp_image_dict_spreadsheet': 'tmp_image_dict.csv',
                                'tmp_image_dict_spreadsheet_json': 'tmp_image_dict.json',

                                'tmp_word_locations_file': 'tmp_word_locations.json',
                                'tmp_word_locations_zipfile': 'tmp_word_locations_zipfile.zip',

                                'tmp_mwe_annotations': 'tmp_mwe_annotations.json',
                                'tmp_mwe_annotations_summary': 'tmp_mwe_annotations_summary.html',
                                'mwe_processed_corpus': 'mwe_processed_corpus.txt',
                                'mwe_trace': 'mwe_trace.html',
                                'mwe_ml_data': 'mwe_ml_data.json',

                                'tmp_phonetic_corpus': 'phonetic_corpus.txt',
                                'tmp_phonetic_aligned_text': 'tmp_phonetic_aligned_text.json',
                                'tmp_phonetic_aligned_lexicon': 'tmp_phonetic_aligned_lexicon.json',

                                'word_pos_file': 'word_pos.json',
                                'tag_tuples_file': 'tag_tuples.json',
                                'tagging_errors_file': 'tagging_errors.txt',

                                'audio_tracking': 'audio_tracking.json',

                                'tmp_segment_audio_word_breakpoint_file': 'tmp_segment_audio_word_breakpoint_file.csv',

                                'recording_string_play_parts': 'recording_string_play_parts.json',

                                'bad_ldt_files': 'bad_ldt_files.json',

                                'all_audio_segments_file': 'all_audio_segments.json',
                                'aligned_file': 'aligned.json',

                                'word_alignment_file': 'word_alignment_data.json',
                                }

# If a file is a processed version of the corpus file, it needs to have the same extension.
tmp_files_that_need_to_have_same_extension_as_corpus_file = [ 'mwe_processed_corpus'
                                                              ]
base_names_for_lara_tmp_dir = {'metadata_dir': 'metadata'}

base_names_for_lara_compiled_dir = {'word_pages_directory': 'vocabpages',
                                    'word_pages_from_abstract_html_directory': '_from_abstract_htmlvocabpages'}

def base_name_for_lara_tmp_file(Key):
    if Key in base_names_for_lara_tmp_file:
        return base_names_for_lara_tmp_file[Key]
    else:
        lara_utils.print_and_flush(f'*** Error: LARA tmp file "{Key}" not defined')
        return False

def base_name_for_lara_tmp_dir(Key):
    if Key in base_names_for_lara_tmp_dir:
        return base_names_for_lara_tmp_dir[Key]
    else:
        lara_utils.print_and_flush(f'*** Error: LARA tmp dir "{Key}" not defined')
        return False

def base_name_for_lara_compiled_dir(Key):
    if Key in base_names_for_lara_compiled_dir:
        return base_names_for_lara_compiled_dir[Key]
    else:
        lara_utils.print_and_flush(f'*** Error: LARA compiled dir "{Key}" not defined')
        return False

def change_extension_to_be_same_as_corpus_file(File, ConfigData):
    return lara_utils.change_extension(File, lara_utils.extension_for_file(ConfigData.corpus))

def find_config_file( filename ):
    if not filename:
        # search for json in directories ./corpus and ./../corpus
        # load the config and check for "id" and "corpus"
        import pathlib
        allConfigFiles = [ str(path) for path in pathlib.Path('./corpus').glob('*.json') ] + [ str(path) for path in pathlib.Path('./../corpus').glob('*.json') ]
        realConfigFiles = []
        for path in allConfigFiles:
            ConfigData = lara_config.read_lara_local_config_file(path)
            if ConfigData and "id" in ConfigData and "corpus" in ConfigData:
                realConfigFiles.append( path )
        if len(realConfigFiles) == 0:
            lara_utils.print_and_flush( '*** Error: cannot determine config file. No files found.')
            return False
        if len(realConfigFiles) > 1:
            lara_utils.print_and_flush( f'*** Error: cannot determine config file. Too many files found: {str(realConfigFiles)}')
            return False
        filename = realConfigFiles[0]    
    configFile = lara_utils.absolute_file_name( filename )
    lara_utils.print_and_flush( f'--- using config file: {configFile}')
    return configFile

 
