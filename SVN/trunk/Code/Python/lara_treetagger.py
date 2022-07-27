
import lara_generic_tagging
import lara_split_and_clean
import lara_top
import lara_config
import lara_utils
import lara_parse_utils
import lara_postags
import lara_clitics
import lara_mwe
import lara_turkish
import lara_icelandic
import lara_irish
import lara_polish
import lara_chinese
import copy
import os

##Call TreeTagger to add tags to a LARA file. The file will in general already have some LARA markup in it,
##for example segment boundaries (||), image tags (<img ... />) and other HTML tags like <i> or <h1>.
##The code strips out the markup, calls TreeTagger to guess the lemmas for each word, then uses the
##lemmas to add hashtags to inflected words.

## Test the tagging on some examples
def test_treetag_lara_file(Id):
    Params = lara_config.default_params()
    if Id == 'dante':
        treetag_lara_file('italian', '$LARA/Content/dante/corpus/dante.txt', Params)
    elif Id == 'krolik_peter':
        treetag_lara_file('russian', '$LARA/Content/peter_rabbit_russian/corpus/peter_rabbit_russian.txt', Params)
    elif Id == 'le_petit_prince':
        treetag_lara_file('french', '$LARA/Content/le_petit_prince/corpus/le_petit_prince.txt', Params)
    elif Id == 'polish_sample':
        treetag_lara_file('polish', '$LARA/tmp/polish_sample.txt', Params)
    elif Id == 'maly_ksiaze':
        treetag_lara_file('polish', '$LARA/Content/maly_ksiaze/corpus/Maly_Ksiaze-1-4i.txt', Params)

## Top-level function. Add tags by running TreeTagger in Language to InFile. Params is a dictionary of
## parameters taken from a local config file. The output is the file whose pathname is formed by adding "_tagged"
## to the base name of InFile.

def treetag_lara_file(Language, InFile, Params):
    if lara_utils.file_exists(InFile):
        ( BaseFile, Extension ) = lara_utils.file_to_base_file_and_extension(InFile)
        OutFile = f'{BaseFile}_tagged.{Extension}'
        treetag_lara_file_main(Language, InFile, Params, OutFile)
    else:
        lara_utils.print_and_flush(f'*** Error: unable to find {InFile}')

## Version which doesn't tag the source file, but instead creates a word/POS file
def make_word_pos_file(Language, InFile, Params, WordPOSFile):
    Params.make_word_pos_file_in_treetagging = 'yes'
    treetag_lara_file_main(Language, InFile, Params, WordPOSFile)

## Convert InFile to a list of plain text file by breaking it up and stripping out the formatting, run TreeTagger, add the tags.

def treetag_lara_file_main(Language, InFile, Params, OutFile):
    # We invoke the hazm package differently
    if Language == 'farsi':
        return do_farsi_tagging(InFile, OutFile, Params)
    # The Sharoff tagging package doesn't assign any lemmas, so it's no use to us. We just copy the segmented file.
    if lara_chinese.is_chinese_language(Params.language):
        return lara_utils.copy_file(InFile, OutFile)
    if not lara_utils.check_environment_variable_directory('TREETAGGER') or not check_treetagger_language_is_supported(Language, Params):
        lara_utils.print_and_flush('*** Error: unable to do tagging')
        return False
    PlainFiles = lara_file_to_plain_files(InFile, Params)
    if not PlainFiles:
        lara_utils.print_and_flush('*** Error: unable to do tagging')
        return False
    TreetaggerOutputFiles = treetag_plain_files(PlainFiles, Language, Params)
    if not TreetaggerOutputFiles:
        lara_utils.print_and_flush('*** Error: unable to do tagging')
        return False
    if annotate_lara_file_from_treetagger_output(InFile, TreetaggerOutputFiles, OutFile, Language, Params):
        lara_utils.print_and_flush(f'--- Call to TreeTagger successfully completed (lang = {Language})')
    else:
        lara_utils.print_and_flush('*** Error: unable to do tagging')
        return False
    for File in PlainFiles + TreetaggerOutputFiles:
        lara_utils.delete_file_if_it_exists(File)
    return True

def treetag_text( Text, Language, Params ):
    Language = guess_treetagger_language_from_text( Text, Language, Params )
    if not Language:
        lara_utils.print_and_flush( f'*** Warning: unable to tag "{Text[:32]}..."! Returning text as is.')
        return Text
    InFile = lara_utils.get_tmp_trace_file(Params)
    OutFile = lara_utils.get_tmp_trace_file(Params)
    lara_utils.write_lara_text_file( Text, InFile )
    treetag_lara_file_main(Language, InFile, Params, OutFile)
    OutText = False
    if lara_utils.file_exists( OutFile ):
        OutText = lara_utils.read_lara_text_file( OutFile )
    lara_utils.delete_file_if_it_exists( InFile )
    lara_utils.delete_file_if_it_exists( OutFile )
    if not OutText:
        lara_utils.print_and_flush( f'*** Warning: Something went wrong while tagging "{Text[:32]}..."! Returning text as is.')
        return Text
    return OutText

## We can't support all languages, so check
def check_treetagger_language_is_supported(Language, Params):
    if tagger_is_available_for_language(Language, Params):
        return True
    else:
        lara_utils.print_and_flush(f'*** Error: tagging not yet supported for "{Language}"')
        return False

def tagger_is_available_for_language(Language, Params):
    if Params.tag_using_google_cloud == 'yes':
        import lara_google_cloud_syntactic_analysis
        return lara_google_cloud_syntactic_analysis.is_language_supported_by_google_cloud_tagging(Language)
    # We do Icelandic using the Icelandic server
    if Language == 'icelandic':
        return True
    # We do Irish using the Irish server
    if Language == 'irish':
        return True
    # We do Turkish using the Turkish NLP Pipeline
    if Language == 'turkish':
        return True
    # We do Polish using the Morfeusz/Concraft pipeline
    if Language == 'polish':
        return True
    if treetagger_invocation(Language):
        return True
    return False

## If necessary, create several small files rather than one big one
def lara_file_to_plain_files(InFile, Params):
    # Chinese is a bit different
    if lara_chinese.is_chinese_language(Params.language):
        return [ lara_chinese.segmented_file_to_plain_file(InFile, Params) ]
    Params1 = copy.copy(Params)
    Params1.for_treetagger = 'yes'
    ( PageOrientedSplitList, Trace ) = lara_split_and_clean.clean_lara_file_main(InFile, Params1)
    if not PageOrientedSplitList:
        lara_utils.print_and_flush(f'*** Fatal error when reading LARA file {InFile}, giving up:')
        return False
    else:
        ## The second element in each chunk is the 'minimally cleaned string', that's what we need.
        SegmentTexts = [ Unit[1] for (PageInfo, Units) in PageOrientedSplitList for Unit in Units ]
        MaxLength = max_length_for_tagging_request(Params1)
        return segment_texts_to_plain_files(SegmentTexts, MaxLength, Params1)

# Limit the number of characters processed if it's a language which uses a web service
_max_tagging_request_length = { 'icelandic': lara_icelandic._max_chars_in_request,
                                'irish': lara_irish._max_chars_in_request,
                                'turkish': lara_turkish._max_chars_in_request
                                }

def max_length_for_tagging_request(Params):
    Language = Params.language
    return _max_tagging_request_length[Language] if Language in _max_tagging_request_length else 1000000000

def segment_texts_to_plain_files(SegmentTexts, MaxLength, Params):
    SegmentTextGroups = group_segment_texts(SegmentTexts, MaxLength)
    Result = [ segment_texts_to_plain_file(Group, Params) for Group in SegmentTextGroups ]
    return Result if not False in Result else False

def group_segment_texts(SegmentTexts, MaxLength):
    ( Groups, CurrentGroup, CurrentLength ) = ( [], [], 0 )
    for SegmentText in SegmentTexts:
        Length = len(SegmentText)
        if CurrentLength + Length < MaxLength:
            CurrentGroup += [ SegmentText ]
            CurrentLength += ( Length + 1 )
        else:
            Groups += [ CurrentGroup ]
            CurrentGroup = [ SegmentText ]
            CurrentLength = ( Length + 1 )
    if CurrentLength > 0:
        Groups += [ CurrentGroup ]
    return Groups
    
def segment_texts_to_plain_file(SegmentTexts, Params):
    PlainFile = lara_utils.get_tmp_trace_file(Params)
    PlainFileText = '\n'.join(SegmentTexts)
    lara_utils.write_lara_text_file(PlainFileText, PlainFile)
    if lara_utils.file_exists(PlainFile):
        lara_utils.print_and_flush(f'--- Written plain file {PlainFile}')
        return PlainFile
    else:
        lara_utils.print_and_flush(f'*** Error: unable to create plain file {PlainFile}')
        return False

# We use a special tagger for Farsi based on the hazm package. This currently requires Python 2.7
def do_farsi_tagging(InFile, OutFile, Params):
    Command = f'python2.7 $LARA/Code/Python/lara_run_farsi_tagging.py {InFile} {OutFile}'
    # In case we want to test under python3
    #Command = f'python3 $LARA/Code/Python/lara_run_farsi_tagging.py {InFile} {OutFile}'
    Status = lara_utils.execute_lara_os_call(Command, Params)
    if Status == 0 and lara_utils.file_exists(OutFile):
        lara_utils.print_and_flush('--- Farsi tagging completed successfully')
        return True
    elif Status != 0:
        lara_utils.print_and_flush(f'*** Error: Farsi tagging failed (status {Status}): "{Command}"')
        return False
    else:
        lara_utils.print_and_flush(f'*** Error: Farsi tagging failed: "{Command}" (output file {OutFile} not found)')
        return False

treetagger_common_options = ''
tokenize_script = ''
treetagger_invocations = {}

# translate language ISO 639-1 codes used by langdetect module to the above treetagger languages
# see: https://pypi.org/project/langdetect/ and  guess_treetagger_language_from_text  below
langid_to_treetagger_language = { 'en':'english', 'fr':'french', 'de':'german', 'it':'italian', 'es':'spanish', 'nl':'dutch', 'ru':'russian' } 

## There is a TreeTagger invocation for Language if it's a key in this dictionary
def treetagger_invocation(Language):
    global treetagger_common_options, tokenize_script, treetagger_invocations
    # Chinese is a bit different from the others, handle separately.
    if lara_chinese.is_chinese_language(Language):
        return lara_chinese.treetagger_invocation_for_chinese()
    treetagger_common_options = '-token -lemma -sgml -no-unknown -quiet'
    tokenize_script = lara_utils.absolute_filename_in_python_directory( 'lara_utf8-tokenize.perl' )
    ## The TreeTagger invocation patterns for the languages we cover
    treetagger_invocations = {'english': f'perl {tokenize_script} -e -a $TREETAGGER/lib/english-abbreviations INPUT_FILE | $TREETAGGER/bin/tree-tagger $TREETAGGER/lib/english-bnc.par {treetagger_common_options} > OUTPUT_FILE',
                'french': f'perl {tokenize_script} -f -a $TREETAGGER/lib/french-abbreviations INPUT_FILE | $TREETAGGER/bin/tree-tagger $TREETAGGER/lib/french.par {treetagger_common_options} > OUTPUT_FILE',
                'german': f'perl {tokenize_script} -a $TREETAGGER/lib/german-abbreviations INPUT_FILE | $TREETAGGER/bin/tree-tagger $TREETAGGER/lib/german.par {treetagger_common_options} > OUTPUT_FILE',
                'middle-high-german': f'perl {tokenize_script} INPUT_FILE | $TREETAGGER/bin/tree-tagger $TREETAGGER/lib/middle-high-german.par {treetagger_common_options} > OUTPUT_FILE',
                'italian': f'perl {tokenize_script} -i -a $TREETAGGER/lib/italian-abbreviations INPUT_FILE | $TREETAGGER/bin/tree-tagger $TREETAGGER/lib/italian.par {treetagger_common_options} > OUTPUT_FILE',
                'spanish': f'perl {tokenize_script} -a $TREETAGGER/lib/spanish-abbreviations INPUT_FILE | $TREETAGGER/bin/tree-tagger $TREETAGGER/lib/spanish.par {treetagger_common_options} > OUTPUT_FILE',
                'dutch': f'perl {tokenize_script} -a $TREETAGGER/lib/dutch-abbreviations INPUT_FILE | $TREETAGGER/bin/tree-tagger $TREETAGGER/lib/dutch.par {treetagger_common_options} > OUTPUT_FILE',
                'russian': f'perl {tokenize_script} INPUT_FILE | $TREETAGGER/bin/tree-tagger $TREETAGGER/lib/russian.par {treetagger_common_options} > OUTPUT_FILE',
                # Added 20190822
                'czech': f'perl {tokenize_script} INPUT_FILE | $TREETAGGER/bin/tree-tagger $TREETAGGER/lib/czech.par {treetagger_common_options} > OUTPUT_FILE',
                'danish': f'perl {tokenize_script} INPUT_FILE | $TREETAGGER/bin/tree-tagger $TREETAGGER/lib/danish.par {treetagger_common_options} > OUTPUT_FILE',
                'finnish': f'perl {tokenize_script} INPUT_FILE | $TREETAGGER/bin/tree-tagger $TREETAGGER/lib/finnish.par {treetagger_common_options} > OUTPUT_FILE',
                'greek': f'perl {tokenize_script} INPUT_FILE | $TREETAGGER/bin/tree-tagger $TREETAGGER/lib/greek.par {treetagger_common_options} > OUTPUT_FILE',
                'korean': f'perl {tokenize_script} INPUT_FILE | $TREETAGGER/bin/tree-tagger $TREETAGGER/lib/korean.par {treetagger_common_options} > OUTPUT_FILE',
                'norwegian': f'perl {tokenize_script} INPUT_FILE | $TREETAGGER/bin/tree-tagger $TREETAGGER/lib/norwegian.par {treetagger_common_options} > OUTPUT_FILE',
                'polish': f'perl {tokenize_script} INPUT_FILE | $TREETAGGER/bin/tree-tagger $TREETAGGER/lib/polish.par {treetagger_common_options} > OUTPUT_FILE',
                'portuguese': f'perl {tokenize_script} INPUT_FILE | $TREETAGGER/bin/tree-tagger $TREETAGGER/lib/portuguese.par {treetagger_common_options} > OUTPUT_FILE',
                'romanian': f'perl {tokenize_script} INPUT_FILE | $TREETAGGER/bin/tree-tagger $TREETAGGER/lib/romanian.par {treetagger_common_options} > OUTPUT_FILE',
                'slovak': f'perl {tokenize_script} INPUT_FILE | $TREETAGGER/bin/tree-tagger $TREETAGGER/lib/slovak2.par {treetagger_common_options} > OUTPUT_FILE',
                'slovenian': f'perl {tokenize_script} INPUT_FILE | $TREETAGGER/bin/tree-tagger $TREETAGGER/lib/slovenian.par {treetagger_common_options} > OUTPUT_FILE',
                'swahili': f'perl {tokenize_script} INPUT_FILE | $TREETAGGER/bin/tree-tagger $TREETAGGER/lib/swahili.par {treetagger_common_options} > OUTPUT_FILE',
                'swedish': f'perl {tokenize_script} INPUT_FILE | $TREETAGGER/bin/tree-tagger $TREETAGGER/lib/swedish.par {treetagger_common_options} > OUTPUT_FILE',
                # Added 20191104
                'catalan': f'perl {tokenize_script} -c INPUT_FILE | $TREETAGGER/bin/tree-tagger $TREETAGGER/lib/catalan.par {treetagger_common_options} > OUTPUT_FILE',
                # Added 20210129
                'ancient-greek': f'perl {tokenize_script} INPUT_FILE | $TREETAGGER/bin/tree-tagger $TREETAGGER/lib/ancient-greek.par {treetagger_common_options} > OUTPUT_FILE',
                }
    if Language in treetagger_invocations:
        return treetagger_invocations[Language]
    else:
        return False

## Tag each component file, giving up if any of them fail
def treetag_plain_files(PlainFiles, Language, Params):
    AllResults = []
    for PlainFile in PlainFiles:
        Result = treetag_plain_file(PlainFile, Language, Params)
        if not Result:
            return False
        else:
            AllResults += [ Result ]
    return AllResults

## Running TreeTagger on the plain file: construct the invocation by substituting in the in- and out-files,
## then execute it and check that the status is okay and the output file is there
def treetag_plain_file(PlainFile, Language, Params):
    OutputFile = lara_utils.get_tmp_trace_file(Params)
    if Params.tag_using_google_cloud == 'yes':
        # Only import lara_google_cloud_syntactic_analysis on demand, since it's nontrivial to install
        import lara_google_cloud_syntactic_analysis
        return lara_google_cloud_syntactic_analysis.invoke_pipeline_for_lara_tagging_and_lemmatisation(PlainFile, OutputFile, Params)
    if Language == 'turkish':
        return lara_turkish.invoke_turkish_nlp_pipeline_for_lara_tagging_and_lemmatisation(PlainFile, OutputFile, Params)
    if Language == 'icelandic':
        return lara_icelandic.invoke_icelandic_pipeline_for_lara_tagging_and_lemmatisation(PlainFile, OutputFile, Params)
    if Language == 'irish':
        return lara_irish.invoke_irish_pipeline_for_lara_tagging_and_lemmatisation(PlainFile, OutputFile, Params)
    if Language == 'polish' and lara_polish.morfeusz_and_concraft_are_available():
        return lara_polish.invoke_polish_pipeline_for_lara_tagging_and_lemmatisation(PlainFile, OutputFile, Params)
    AbsPlainFile = lara_utils.absolute_file_name(PlainFile)
    AbsOutputFile = lara_utils.absolute_file_name(OutputFile)
    Invocation = treetagger_invocation(Language)
    Invocation1 = Invocation.replace('INPUT_FILE', AbsPlainFile)
    Command = Invocation1.replace('OUTPUT_FILE', OutputFile)
    Status = execute_treetagger_command(Command, Params)
    if Status == 0 and lara_utils.file_exists(AbsOutputFile):
        lara_utils.print_and_flush('--- Tagging completed successfully')
        #SaveFile = '$LARA/tmp/tmp_tagging_output.txt'
        #lara_utils.copy_file(OutputFile, SaveFile)
        #lara_utils.print_and_flush(f'--- Saved tagging output to {SaveFile}')
        return OutputFile
    elif Status != 0:
        lara_utils.print_and_flush(f'*** Error: tagging call failed (status {Status}): "{Command}"')
        return False
    else:
        lara_utils.print_and_flush(f'*** Error: tagging call failed: "{Command}" (output file {OutputFile} not found)')
        return False

def execute_treetagger_command(Command, Params):
    if lara_utils.bash_found():
        return lara_utils.execute_lara_os_call(Command, Params)
    else:
        lara_utils.print_and_flush(f'*** Warning: unable to find "bash" in $PATH, trying to recover by calling "tree-tagger" directly')
        Command1 = Command.replace('$TREETAGGER/bin/tree-tagger', 'tree-tagger')
        Command2 = Command1.replace('$TREETAGGER', os.getenv('TREETAGGER'))
        return lara_utils.execute_lara_os_call_direct(Command2)

## Now use the TreeTagger output to put the tags into the original file, and write out the result              
def annotate_lara_file_from_treetagger_output(LARAFile, TreetaggerOutputFiles, TaggedFile, Language, Params):
    InString0 = lara_utils.read_lara_text_file(LARAFile)
    # If we're adding POS tags to an already tagged file, tidy up first by replacing MWEs bracketed by @ with canonical versions
    InString = lara_mwe.make_mwes_canonical_in_string(InString0) if Params.retagging_strategy == 'replace_pos' else InString0
    TagTuples = read_treetagger_output_files(TreetaggerOutputFiles, Language)
    save_tag_tuples(TagTuples, Params)
    # If make_word_pos_file_in_treetagging = 'yes' then we're not doing normal treetagging,
    # rather creating a word/POS file
    if Params.make_word_pos_file_in_treetagging == 'yes':
        return make_word_pos_file1(TagTuples, TaggedFile, Params)
    RawOutString = lara_generic_tagging.annotate_lara_string_from_tagging_triples(TagTuples, InString, Params)
    if not RawOutString:
        lara_utils.print_and_flush(f'*** Error: unable to update LARA file from TreeTagger output')
        return False
    OutString = lara_generic_tagging.remove_hashtags_and_separators_inside_multiwords(RawOutString)
    if OutString:
        lara_utils.write_lara_text_file(OutString, TaggedFile)
        return True
    else:
        lara_utils.print_and_flush(f'*** Error: unable to update LARA file from TreeTagger output')
        return False

def save_tag_tuples(TagTuples, Params):
    File = lara_top.lara_tmp_file('tag_tuples_file', Params)
    lara_utils.write_json_to_file_plain_utf8(TagTuples, File)
    lara_utils.print_and_flush(f'--- {len(TagTuples)} tag tuples produced by tagger, saved to {File}')

def make_word_pos_file1(TagTuples, TaggedFile, Params):
    return lara_utils.write_json_to_file(clean_tag_tuples_for_word_pos_file(TagTuples, Params), TaggedFile)

def clean_tag_tuples_for_word_pos_file(TagTuples, Params):
    return [ clean_tag_tuple_for_word_pos_file(TagTuple, Params) for TagTuple in TagTuples
             if not tag_tuple_irrelevant_for_word_pos_file(TagTuple) ]

def clean_tag_tuple_for_word_pos_file(TagTuple, Params):
    ( WordList, Tag, Lemma ) = TagTuple
    return ( ' '.join(WordList), Lemma, map_postag_if_possible(Tag, Params) )

def map_postag_if_possible(Tag, Params):
    MappedTag = lara_postags.map_postag(Tag, Params)
    return MappedTag if MappedTag != '' else Tag

def tag_tuple_irrelevant_for_word_pos_file(TagTuple):
    ( WordList, Tag, Lemma ) = TagTuple
    SurfaceWord = ' '.join(WordList)
    return lara_parse_utils.is_punctuation_string(SurfaceWord)

def read_treetagger_output_files(TreetaggerOutputFiles, Language):
    ListOfTagTupleLists = [ read_treetagger_output(TreetaggerOutputFile, Language) for TreetaggerOutputFile in TreetaggerOutputFiles ]
    return [ TagTuple for TagTupleLists in ListOfTagTupleLists for TagTuple in TagTupleLists ]

## The TreeTagger output file is a bunch of lines like the ones immediately below.
## Read them and convert them into pairs of the form [SurfaceWord, Lemma]
def read_treetagger_output(TreetaggerOutputFile, Language):
    if Language == 'icelandic':
        return read_icelandic_treetagger_output(TreetaggerOutputFile)
    if Language == 'irish':
        return lara_irish.read_irish_tagger_output(TreetaggerOutputFile)
    Lines = (lara_utils.read_lara_text_file(TreetaggerOutputFile)).split('\n')
    return [ treetagger_output_line_to_tag_tuple(Line, Language) for Line in Lines
             if treetagger_output_line_to_tag_tuple(Line, Language) ]

##Update, 20200505: now has {'paragraphs':[ ... ]} wrapped around it.
##
##{'sentences': [[{'expanded tag': {'beyging': 'veik beyging',
##                                  'fall': 'nefnifall',
##                                  'kyn': 'kvenkyn',
##                                  'orðflokkur': 'lýsingarorð',
##                                  'stig': 'efstastig',
##                                  'tala': 'eintala'},
##                 'lemma': 'fyrstur',
##                 'tag': 'lvenve',
##                 'word': 'Fyrsta'},
##                {'expanded tag': {'fall': 'nefnifall',
##                                  'kyn': 'kvenkyn',
##                                  'orðflokkur': 'nafnorð',
##                                  'tala': 'eintala'},
##                 'lemma': 'bók',
##                 'tag': 'nven',
##                 'word': 'bók'},

def read_icelandic_treetagger_output(File):
    try:
        Paragraphs = lara_utils.read_json_file(File)['paragraphs']
        return [ word_tag_and_lemma_for_icelandic_word_rec(WordRec) \
                 for Paragraph in Paragraphs for Sent in Paragraph['sentences'] for WordRec in Sent ]
    except:
        lara_utils.print_and_flush(f'Unable to read read Icelandic result file {File}')
        return False

def word_tag_and_lemma_for_icelandic_word_rec(WordRec):
    Word = WordRec['word'] if 'word' in WordRec else '*unknown_word*'
    Tag = WordRec['expanded tag']['orðflokkur'] if 'expanded tag' in WordRec and 'orðflokkur' in WordRec['expanded tag'] else '*unknown_tag*'
    Lemma = WordRec['lemma'] if 'lemma' in WordRec else '*unknown_lemma*'
    return [ [ Word ], Tag, Lemma ]
    
## Typical TreeTagger output lines
##l'      DET:def il
##altre   ADJ     altro
##cose    NOM     cosa

## Convert a TreeTagger output line into a pair.
## We make the surface word into a one-element list
## to be compatible with the minimal-tagging interface, which can have a multiword as the surface word

def treetagger_output_line_to_tag_tuple(Line, Language):
    Components = Line.split()
    if len(Components) == 3:
        ( SurfaceWord, Tag, Lemmas ) = Components
        LemmaList = Lemmas.split('|')
        return [ [ SurfaceWord ], Tag, LemmaList[0] ]
    else:
        return False

## Guess language from text using the langdetect module if available
def guess_treetagger_language_from_text( Text, Language, Params ):
    if Language and check_treetagger_language_is_supported( Language, Params ):
        # nothing to guess. Take the language as given
        return Language
    try:
        import langdetect
        langdetect.DetectorFactory.seed = 0 # to avoid non-determistic behaviour
        langid = langdetect.detect( Text )
        if langid in langid_to_treetagger_language:
            Language = langid_to_treetagger_language[langid]
            if check_treetagger_language_is_supported( Language, Params ):
                return Language
        lara_utils.print_and_flush( '*** Language Detection Module detected "{langid}", but that\'s not supported by TreeTagger.')
    except ImportError:
        lara_utils.print_and_flush( '*** Language Detection Module not importable. Try "pip install langdetect"')
    return False
