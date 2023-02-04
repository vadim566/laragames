
import lara_config
import lara_split_and_clean
import lara_translations
import lara_install_audio_zipfile
import lara_audio
import lara_utils
import urllib.parse

# Create an editable file which
def make_align_postediting_files(ConfigFile):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if check_params_for_align_postediting_file(Params) == False:
        return
    Segments = get_text_segments(Params)
    SegmentAudioDict = get_segment_audio_dict(Params)
    SegmentTranslationDict = get_segment_translation_dict(Params)
    AnnotatedSegments = [ annotate_segment(Segment, SegmentAudioDict, SegmentTranslationDict, Params)
                          for Segment in Segments ]
    write_out_align_postediting_files(AnnotatedSegments, Params)
    save_annotated_segments(AnnotatedSegments, Params, 'raw')

def check_params_for_align_postediting_file(Params):
    if Params.alignment_postediting_file == '':
        lara_utils.print_and_flush(f'*** Error: alignment_postediting_file not defined')
        return False
    if Params.web_multimedia_url == '':
        DefaultURL = default_web_multimedia_url(Params)
        lara_utils.print_and_flush(f'*** Warning: web_multimedia_url not defined. Assuming audio files are at {DefaultURL}')
    return True

def update_from_postediting_file(ConfigFile, AnnotatorId):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if Params == False:
        return
    AnnotatedSegments = read_edited_postediting_file(Params)
    if AnnotatedSegments == False:
        return
    save_annotated_segments(AnnotatedSegments, Params, AnnotatorId)
    update_corpus_from_annotated_segments(AnnotatedSegments, Params)
    update_segment_audio_metadata_from_annotated_segments(AnnotatedSegments, Params)
    update_segment_translations_from_annotated_segments(AnnotatedSegments, Params)
    score_annotations(AnnotatorId, Params)
    
def score_alignment_from_annotations(ConfigFile, AnnotatorId):
    return

def compare_alignment_annotations(ConfigFile, AnnotatorIds):
    return

# ------------------------------------------------

def get_text_segments(Params):
    SegmentedFile = Params.untagged_raw_corpus if Params.untagged_raw_corpus != '' else Params.untagged_corpus
    Text = lara_utils.read_lara_text_file(SegmentedFile)
    return [ Segment for Segment in Text.split('||') if Segment != '' ]

def get_segment_audio_dict(Params):
    Dir = Params.segment_audio_directory
    Metadata = lara_audio.read_ldt_metadata_file(Dir)
    return { Item['text']: Item['file'] for Item in Metadata }

def get_segment_translation_dict(Params):
    File = Params.segment_translation_spreadsheet27
    SourceTargetPairs = lara_utils.read_lara_csv(File)[1:]
    return { Item[0]: Item[1] for Item in SourceTargetPairs }

def annotate_segment(Segment, SegmentAudioDict, SegmentTranslationDict, Params):
    SegmentNormalised = lara_split_and_clean.minimal_clean_lara_string(Segment, Params)[0]
    if SegmentNormalised in SegmentAudioDict:
        AudioFile = SegmentAudioDict[SegmentNormalised]
    else:
        lara_utils.print_and_flush(f'*** Warning: no audio entry found for "{Segment}"')
        AudioFile = False
    if SegmentNormalised in SegmentTranslationDict:
        Translation = SegmentTranslationDict[SegmentNormalised]
    else:
        lara_utils.print_and_flush(f'*** Warning: no translation found for "{Segment}"')
        Translation = False
    return { 'text': Segment, 'audio_file': AudioFile, 'translation': Translation }

def write_out_align_postediting_files(AnnotatedSegments, Params):
    write_out_align_postediting_html_file(AnnotatedSegments, Params)
    write_out_align_postediting_docx_file(AnnotatedSegments, Params)

def write_out_align_postediting_html_file(AnnotatedSegments, Params):
    Intro = postediting_file_html_intro(Params)
    Body = lara_utils.concatenate_lists([ annotated_segment_to_postediting_file_html_text(AnnotatedSegment, Params)
                                          for AnnotatedSegment in AnnotatedSegments ])
    Coda = postediting_file_html_coda(Params)
    Text = '\n'.join( Intro + Body + Coda )
    File = lara_utils.change_extension(Params.alignment_postediting_file, 'html')
    lara_utils.write_lara_text_file(Text, File)

def write_out_align_postediting_docx_file(AnnotatedSegments, Params):
    Body = lara_utils.concatenate_lists([ annotated_segment_to_postediting_file_docx_text(AnnotatedSegment, Params)
                                          for AnnotatedSegment in AnnotatedSegments ])
    Text = '\n'.join( Body )
    File = lara_utils.change_extension(Params.alignment_postediting_file, 'docx')
    lara_utils.write_lara_text_file(Text, File)

def postediting_file_html_intro(Params):
    return [ '<html>',
             '<head>',
             '<meta http-equiv="Content-Type" content="text/html;charset=UTF-8">',
             '</head>'
             '<body>' ]

def postediting_file_html_coda(Params):
    return [ '</body>',
             '</html>' ]

def annotated_segment_to_postediting_file_html_text(AnnotatedSegment, Params):
    ( Text, AudioFile, Translation ) = ( AnnotatedSegment['text'], AnnotatedSegment['audio_file'], AnnotatedSegment['translation'] )
    BaseAudioURL = web_multimedia_url(Params)
    FullAudioFileURL = f'{BaseAudioURL}/{AudioFile}'
    AudioControlLine = f'<p><audio controls="true" preload="none"><source src="{FullAudioFileURL}" type="audio/mp3"></p>'
    AudioFileLine = f'<p>|{AudioFile}|</p>'
    TextLine = f'<p>|{Text}|</p>'
    TranslationLine = f'<p>|{Translation}|</p>'
    return [ AudioControlLine, AudioFileLine, TextLine, TranslationLine ]

def annotated_segment_to_postediting_file_docx_text(AnnotatedSegment, Params):
    ( Text, AudioFile, Translation ) = ( AnnotatedSegment['text'], AnnotatedSegment['audio_file'], AnnotatedSegment['translation'] )
    SeparatorLine = '_______________________'
    AudioFileLine = f'|{AudioFile}|'
    TextLine = f'|{Text}|'
    TranslationLine = f'|{Translation}|'
    return [ SeparatorLine, AudioFileLine, TextLine, TranslationLine ]

def save_annotated_segments(AnnotatedSegments, Params, AnnotatorId):
    File = lara_utils.change_extension(Params.alignment_postediting_file, 'json')
    CurrentContent = lara_utils.read_json_file(File) if lara_utils.file_exists(File) else {}
    if not isinstance(CurrentContent, ( dict )):
        lara_utils.print_and_flush(f'*** Warning: unable to read {File} as JSON file containing dict, discarding current content')
        CurrentContent = {}
    CurrentContent[AnnotatorId] = AnnotatedSegments
    lara_utils.write_json_to_file_plain_utf8(CurrentContent, File)
    lara_utils.print_and_flush(f'--- Written {len(AnnotatedSegments)} annotated segments to {File}')

def score_annotations(AnnotatorId, Params):
    File = lara_utils.change_extension(Params.alignment_postediting_file, 'json')
    CurrentContent = lara_utils.read_json_file(File) if lara_utils.file_exists(File) else {}
    if not isinstance(CurrentContent, ( dict )):
        lara_utils.print_and_flush(f'*** Error: unable to read {File} as JSON file containing dict, discarding current content')
        CurrentContent = {}
        return
    if not 'raw' in CurrentContent:
        lara_utils.print_and_flush(f'*** Error: "raw" data not found in {File}')
        return
    if not AnnotatorId in CurrentContent:
        lara_utils.print_and_flush(f'*** Error: "raw" data not found in {File}')
        return
    ( RawData, EditedData ) = ( CurrentContent['raw'], CurrentContent[AnnotatorId] )
    ( RawDict, EditedDict ) = ( alignment_data_to_words_dict(RawData), alignment_data_to_words_dict(EditedData) )
    ( NSegments, NWords, NTransWords, NErrors, NTransErrors ) = ( 0, 0, 0, 0, 0 )
    for File in RawDict:
        if File in EditedDict:
            ( RawWords, EditedWords ) = ( RawDict[File]['text'], EditedDict[File]['text'] )
            ( RawTransWords, EditedTransWords ) = ( RawDict[File]['translation'], EditedDict[File]['translation'] )
            NewErrors = lara_utils.word_edit_distance(RawWords, EditedWords)
            NewTransErrors = lara_utils.word_edit_distance(RawTransWords, EditedTransWords)
            NSegments += 1
            NWords += len(RawWords)
            NTransWords += len(RawTransWords)
            NErrors += NewErrors
            NTransErrors += NewTransErrors
            if NewErrors != 0 or NewTransErrors != 0:
                print_errors_shown_by_annotations(RawWords, EditedWords, NewErrors, RawTransWords, EditedTransWords, NewTransErrors)
    lara_utils.print_and_flush(f'===========================')
    lara_utils.print_and_flush(f'Segments: {NSegments}')
    lara_utils.print_and_flush(f'   Words: {NWords}')
    lara_utils.print_and_flush(f'  Errors: {NErrors}')
    lara_utils.print_and_flush(f'     WER: {100 * NErrors / NWords:.1f}%')
    lara_utils.print_and_flush(f'  TWords: {NTransWords}')
    lara_utils.print_and_flush(f' TErrors: {NTransErrors}')
    lara_utils.print_and_flush(f'     TER: {100 * NTransErrors / NTransWords:.1f}%')

def print_errors_shown_by_annotations(RawWords, EditedWords, NewErrors, RawTransWords, EditedTransWords, NewTransErrors):
    if NewErrors != 0:
        lara_utils.print_and_flush(f'---------------------------')
        lara_utils.print_and_flush(f'   Original: {RawWords}')
        lara_utils.print_and_flush(f'     Edited: {EditedWords}')
        lara_utils.print_and_flush(f'     Errors: {NewErrors}')
    if NewTransErrors != 0:
        lara_utils.print_and_flush(f'Translation: {RawTransWords}')
        lara_utils.print_and_flush(f'     Edited: {EditedTransWords}')
        lara_utils.print_and_flush(f'     Errors: {NewTransErrors}')

##        {
##            "audio_file": "extracted_file_all_3.mp3",
##            "text": "<file id=\"all\">LES POÈTES DE SEPT ANS",
##            "translation": "POETS AT SEVEN YEARS"
##        },
##        {
##            "audio_file": "extracted_file_all_4.mp3",
##            "text": "\nEt la Mère, fermant le livre du devoir,",
##            "translation": "And the mother, closing the work-book"
##        },

def alignment_data_to_words_dict(AlignmentData):
    return { Item['audio_file']: { 'text': normalise_to_words(Item['text']), 'translation': normalise_to_words(Item['translation']) }
             for Item in AlignmentData }

# ------------------------------------------------

def read_edited_postediting_file(Params):
    File = lara_utils.change_extension(Params.alignment_postediting_file, 'docx')
    if not lara_utils.file_exists(File):
        lara_utils.print_and_flush(f'*** Error: unable to find {File}')
        return False
    Text0 = lara_utils.read_lara_text_file(File)
    lara_utils.print_and_flush(f'--- Read aligned postediting file {File}, {len(Text0)} chars')
    # We might have marked optimal segmentations
    Text = Text0.replace('||', '')
    Components = Text.split('|')
    NonTrivialComponents = [ Component for Component in Components
                             if not ( Component.isspace() or Component == '' ) ]
    ( ComponentsLeft, OutList ) = ( NonTrivialComponents, [] )
    while True:
        if len(ComponentsLeft) == 0:
            lara_utils.print_and_flush(f'--- Found {len(Components)} components')
            return OutList
        if is_separator_line(ComponentsLeft[0]):
            if len(ComponentsLeft) < 4:
                lara_utils.print_and_flush(f'*** Error: file ends anomalously: {ComponentsLeft}')
                return False
            ( AudioFile, TextSegment, Translation ) = ComponentsLeft[1:4]
            OutList += [ { 'audio_file':AudioFile, 'text':TextSegment, 'translation':Translation } ]
            ComponentsLeft = ComponentsLeft[4:]
        else:
            lara_utils.print_and_flush(f'*** Error: expected a separator line but found: {ComponentsLeft[0]}')
            return False
    # Shouldn't get here...
    lara_utils.print_and_flush(f'*** Error: file ends anomalously: {ComponentsLeft}')
    return False

# It's a separator line if it's a line of underscores
def is_separator_line(Line):
    return Line.replace('_', '').strip() == ''

def update_corpus_from_annotated_segments(AnnotatedSegments, Params):
    NewText = '||'.join([ Item['text'] for Item in AnnotatedSegments ])
    lara_utils.write_lara_text_file(NewText, Params.untagged_corpus)
    return

def update_segment_audio_metadata_from_annotated_segments(AnnotatedSegments, Params):
    Dir = Params.segment_audio_directory
    OldMetadata = lara_audio.read_ldt_metadata_file(Dir)
    NewMetadata = [ { 'file':Item['audio_file'], 'text':lara_split_and_clean.minimal_clean_lara_string(Item['text'], Params)[0] }
                    for Item in AnnotatedSegments ]
    UpdatedMetadata = lara_install_audio_zipfile.clean_audio_metadata(OldMetadata + NewMetadata)
    lara_audio.write_ldt_metadata_file(UpdatedMetadata, Dir)
    lara_utils.print_and_flush(f'--- Updated metadata file in {Dir}')
    return

def update_segment_translations_from_annotated_segments(AnnotatedSegments, Params):
    File = Params.segment_translation_spreadsheet
    OldLines = lara_utils.read_lara_csv(File)[1:]
    NewLines = [ [ lara_split_and_clean.minimal_clean_lara_string(Item['text'], Params)[0], Item['translation'] ]
                 for Item in AnnotatedSegments ]
    UpdatedLines = lara_utils.remove_duplicates_general(OldLines + NewLines)
    Header = [ 'Segment', 'Translation' ]
    lara_translations.write_translation_csv(Header, UpdatedLines, File)
    return

# ------------------------------------------------

def web_multimedia_url(Params):
    return Params.web_multimedia_url if Params.web_multimedia_url != '' else default_web_multimedia_url(Params)

def default_web_multimedia_url(Params):
    URLQuoteId = urllib.parse.quote(Params.id)
    return f'https://www.issco.unige.ch/en/research/projects/callector/{URLQuoteId}vocabpages/multimedia'

# ------------------------------------------------

def normalise_to_words(Str):
    if not isinstance(Str, ( str )):
        return []
    Pairs = lara_split_and_clean.string_to_annotated_words(Str)[0]
    return [ Pair[0].lower() for Pair in Pairs if Pair[1] != '' ]
 
