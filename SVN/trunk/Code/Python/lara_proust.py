
import lara_align_from_audio
import lara_align_adjust
import lara_crowdsource
import lara_count_words
import lara_mwe
import lara_utils

# Processing Combray ch2

# Source files: corpus/combray_ch2.txt and corpus/combray_eng_ch2.txt

_ch1_french_source_file = '$LARA/Content/combray/corpus/combray_ch1.txt'
_ch1_english_source_file = '$LARA/Content/combray/corpus/combray_eng_ch1.txt'

_ch2_french_source_file = '$LARA/Content/combray/corpus/combray_ch1.txt'
_ch2_english_source_file = '$LARA/Content/combray/corpus/combray_eng_ch1.txt'

# Invoke YouAlign

# Result: translations/combray_ch1_FRA-ENG_BT.tmx
# Result: translations/combray_ch2_FRA-ENG_BT.tmx

_ch1_tmx_translation_file = '$LARA/Content/combray/translations/combray_ch1_FRA-ENG_BT.tmx'
_ch2_tmx_translation_file = '$LARA/Content/combray/translations/combray_ch2_FRA-ENG_BT.tmx'

_ch1_translation_alignment_corpus = '$LARA/Content/combray/corpus/combray_ch1_for_translation_alignment.txt'
_ch2_translation_alignment_corpus = '$LARA/Content/combray/corpus/combray_ch2_for_translation_alignment.txt'

def make_ch1_translation_alignment_corpus():
    add_text_to_start_of_file('<file id="ch1">', _ch1_french_source_file, _ch1_translation_alignment_corpus)
def make_ch2_translation_alignment_corpus():
    add_text_to_start_of_file('<file id="ch2">', _ch2_french_source_file, _ch2_translation_alignment_corpus)

def check_ch1_translation_alignment_corpus():
    lara_count_words.compare_text_file_words(_ch1_french_source_file, _ch1_translation_alignment_corpus)
def check_ch2_translation_alignment_corpus():
    lara_count_words.compare_text_file_words(_ch2_french_source_file, _ch2_translation_alignment_corpus)

_ch1_config_file = '$LARA/Content/combray/corpus/local_config_ch1_double_align.json'
_ch1_translation_segmented_file = '$LARA/Content/combray/corpus/combray_ch1_translation_segmented.txt'
_ch1_segment_translations_csv = '$LARA/Content/combray/translations/french_english_from_tmx_ch1.csv'

_ch2_config_file = '$LARA/Content/combray/corpus/local_config_ch2_double_align.json'
_ch2_translation_segmented_file = '$LARA/Content/combray/corpus/combray_ch2_translation_segmented.txt'
_ch2_segment_translations_csv = '$LARA/Content/combray/translations/french_english_from_tmx_ch2.csv'

def make_ch1_translation_aligned_file():
    ConfigFile = _ch1_config_file
    Spec = 'ch1'
    TMXFile = _ch1_tmx_translation_file
    SourceLang = 'fr'
    TargetLang = 'en'
    TMXSegmentedCorpusFile = _ch1_translation_segmented_file
    TranslationsCSV = _ch1_segment_translations_csv
    lara_align_adjust.add_tmx_segmentation_to_corpus(ConfigFile, Spec, TMXFile, SourceLang, TargetLang, TMXSegmentedCorpusFile, TranslationsCSV)
def make_ch2_translation_aligned_file():
    ConfigFile = _ch2_config_file
    Spec = 'ch2'
    TMXFile = _ch2_tmx_translation_file
    SourceLang = 'fr'
    TargetLang = 'en'
    TMXSegmentedCorpusFile = _ch2_translation_segmented_file
    TranslationsCSV = _ch2_segment_translations_csv
    lara_align_adjust.add_tmx_segmentation_to_corpus(ConfigFile, Spec, TMXFile, SourceLang, TargetLang, TMXSegmentedCorpusFile, TranslationsCSV)

def check_ch1_translation_segmented_file():
    lara_count_words.compare_text_file_words(_ch1_french_source_file, _ch1_translation_segmented_file)
def check_ch2_translation_segmented_file():
    lara_count_words.compare_text_file_words(_ch2_french_source_file, _ch2_translation_segmented_file)

_ch1_audio_alignment_corpus = '$LARA/Content/combray/corpus/combray_ch1_for_audio_alignment.txt'
_ch2_audio_alignment_corpus = '$LARA/Content/combray/corpus/combray_ch2_for_audio_alignment.txt'

def make_ch1_audio_alignment_corpus():
    add_text_to_start_of_file('<file id="ch1">', _ch1_translation_segmented_file, _ch1_audio_alignment_corpus)
def make_ch2_audio_alignment_corpus():
    add_text_to_start_of_file('<file id="ch2">', _ch2_translation_segmented_file, _ch2_audio_alignment_corpus)

def check_ch1_audio_alignment_corpus():
    lara_count_words.compare_text_file_words(_ch1_french_source_file, _ch1_audio_alignment_corpus)
def check_ch2_audio_alignment_corpus():
    lara_count_words.compare_text_file_words(_ch2_french_source_file, _ch2_audio_alignment_corpus)

# Perform ch1 audio alignment using command
# python3 $LARA/Code/Python/lara_run.py align_segment_audio local_config_ch1_double_align.json ch1 ngram create
# Perform ch2 audio alignment using command
# python3 $LARA/Code/Python/lara_run.py align_segment_audio local_config_ch2_double_align.json ch2 ngram create

_ch1_raw_double_aligned_file = '$LARA/Content/combray/corpus/combray_segmented_from_aligner_ch1_double_segmented.txt'
_ch2_raw_double_aligned_file = '$LARA/Content/combray/corpus/combray_segmented_from_aligner_ch2_double_segmented.txt'

def check_ch1_raw_double_aligned_file():
    lara_count_words.compare_text_file_words(_ch1_french_source_file, _ch1_raw_double_aligned_file)
def check_ch2_raw_double_aligned_file():
    lara_count_words.compare_text_file_words(_ch2_french_source_file, _ch2_raw_double_aligned_file)

_ch1_segment_translations_csv_corrected = '$LARA/Content/combray/translations/french_english_from_tmx_ch1_corrected.csv'
_ch1_segment_translations_csv_raw = '$LARA/Content/combray/translations/french_english_from_tmx_ch1_raw.csv'

_ch2_segment_translations_csv_corrected = '$LARA/Content/combray/translations/french_english_from_tmx_ch2_corrected.csv'
_ch2_segment_translations_csv_raw = '$LARA/Content/combray/translations/french_english_from_tmx_ch2_raw.csv'

def correct_ch1_raw_double_aligned_translations():
    lara_align_adjust.correct_segment_translations_for_double_aligned_file(_ch1_raw_double_aligned_file,
                                                                           _ch1_segment_translations_csv,
                                                                           _ch1_segment_translations_csv_corrected,
                                                                           _ch1_config_file)
    lara_utils.copy_file(_ch1_segment_translations_csv, _ch1_segment_translations_csv_raw)
    lara_utils.copy_file(_ch1_segment_translations_csv_corrected, _ch1_segment_translations_csv)
def correct_ch2_raw_double_aligned_translations():
    lara_align_adjust.correct_segment_translations_for_double_aligned_file(_ch2_raw_double_aligned_file,
                                                                           _ch2_segment_translations_csv,
                                                                           _ch2_segment_translations_csv_corrected,
                                                                           _ch2_config_file)
    lara_utils.copy_file(_ch2_segment_translations_csv, _ch2_segment_translations_csv_raw)
    lara_utils.copy_file(_ch2_segment_translations_csv_corrected, _ch2_segment_translations_csv)

_ch1_merged_double_aligned_file = '$LARA/Content/combray/corpus/combray_segmented_from_aligner_ch1_double_align.txt'
_ch2_merged_double_aligned_file = '$LARA/Content/combray/corpus/combray_segmented_from_aligner_ch2_double_align.txt'

def make_ch1_merged_double_aligned_file():
    lara_align_adjust.make_corpus_audio_and_translations_for_double_aligned_file(_ch1_raw_double_aligned_file,
                                                                                 _ch1_segment_translations_csv,
                                                                                 _ch1_config_file)
def make_ch2_merged_double_aligned_file():
    lara_align_adjust.make_corpus_audio_and_translations_for_double_aligned_file(_ch2_raw_double_aligned_file,
                                                                                 _ch2_segment_translations_csv,
                                                                                 _ch2_config_file)

def check_ch1_merged_double_aligned_file():
    lara_count_words.compare_text_file_words(_ch1_french_source_file, _ch1_merged_double_aligned_file)
def check_ch2_merged_double_aligned_file():
    lara_count_words.compare_text_file_words(_ch2_french_source_file, _ch2_merged_double_aligned_file)

# Do treebanker, resources and word_pages for ch1 and ch2

def stick_together_combray_ch1_and_ch2():
    FileWithListOfConfigFiles = '$LARA/tmp/combray_collected_config_files.json'
    ListOfConfigFiles = [ '$LARA/Content/combray/corpus/local_config_ch1_double_align.json',
                          '$LARA/Content/combray/corpus/local_config_ch2_double_align.json' ]
    lara_utils.write_json_to_file(ListOfConfigFiles, FileWithListOfConfigFiles)
    ConfigFile = '$LARA/Content/combray/corpus/local_config_double_align.json'
    lara_crowdsource.stick_together_projects(FileWithListOfConfigFiles, ConfigFile)

# Create MWE annotations using call
# python3 $LARA/Code/Python/lara_run.py mwe_annotate local_config_double_align.json

# Fill in MWE annotations in file $LARA/tmp_resources/combray_double_align_tmp_mwe_annotations_summary.txt
# Process MWE annotations

def process_mwe_annotations_ch1_and_ch2():
    JSONFileIn = '$LARA/tmp_resources/combray_double_align_tmp_mwe_annotations.json'
    TextFile = '$LARA/tmp_resources/combray_double_align_tmp_mwe_annotations_summary.txt'
    JSONFileOut = '$LARA/Content/combray/corpus/mwe_annotations_double_align.json'
    N = 1000000
    lara_mwe.update_mwe_json_file_from_mwe_text_file(JSONFileIn, TextFile, JSONFileOut, N)

# Do resources and word_pages for full combray using calls
# python3 $LARA/Code/Python/lara_run.py resources local_config_double_align.json
# python3 $LARA/Code/Python/lara_run.py word_pages local_config_double_align.json

def add_text_to_start_of_file(Text, File1, File2):
    Str1 = lara_utils.read_lara_text_file(File1)
    if Str1 == False: return
    Str2 = Text + Str1
    lara_utils.write_lara_text_file(Str2, File2)
    
                              
