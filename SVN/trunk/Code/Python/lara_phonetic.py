
import lara_phonetic_align
import lara_mwe
import lara_config
import lara_abstract_html
import lara_picturebook
import lara_number_words
import lara_parse_utils
import lara_utils
import re

def test(Id):
##    if Id == 'father_william':
##        ConfigFile = '$LARA/Content/father_william_ipa/corpus/local_config.json' 
##        NewCorpusFile = '$LARA/Content/father_william_ipa/corpus/father_william_ipa2.txt'
##        make_word_translations_into_lemmas(ConfigFile, NewCorpusFile)
    if Id == 'le_petit_prince_abc':
        PhoneticCorpusFile = '$LARA/tmp_resources/le_petit_prince_abc_phonetic.txt'
        TmpAlignedTextFile = '$LARA/tmp_resources/le_petit_prince_abc_tmp_phonetic_annotations_aligned.json'
        TmpAlignedLexiconFile = '$LARA/tmp_resources/le_petit_prince_abc_tmp_phonetic_lexicon_aligned.json'
        ConfigFile = '$LARA/Content/le_petit_prince/corpus/local_config_abc.json'
        make_phonetic_version_of_corpus_file_and_tmp_files(PhoneticCorpusFile, TmpAlignedTextFile, TmpAlignedLexiconFile, ConfigFile)
    elif Id == 'le_petit_prince_abc2':
        PhoneticCorpusFile = '$LARA/tmp_resources/le_petit_prince_abc2_phonetic.txt'
        TmpAlignedTextFile = '$LARA/tmp_resources/le_petit_prince_abc2_tmp_phonetic_annotations_aligned.json'
        TmpAlignedLexiconFile = '$LARA/tmp_resources/le_petit_prince_abc2_tmp_phonetic_lexicon_aligned.json'
        ConfigFile = '$LARA/Content/le_petit_prince/corpus/local_config_abc2.json'
        make_phonetic_version_of_corpus_file_and_tmp_files(PhoneticCorpusFile, TmpAlignedTextFile, TmpAlignedLexiconFile, ConfigFile)
    elif Id == 'le_petit_prince_ch1':
        PhoneticCorpusFile = '$LARA/tmp_resources/le_petit_prince_ch1_phonetic.txt'
        TmpAlignedTextFile = '$LARA/tmp_resources/le_petit_prince_ch1_tmp_phonetic_annotations_aligned.json'
        TmpAlignedLexiconFile = '$LARA/tmp_resources/le_petit_prince_ch1_tmp_phonetic_lexicon_aligned.json'
        ConfigFile = '$LARA/Content/le_petit_prince/corpus/local_config_ch1.json'
        make_phonetic_version_of_corpus_file_and_tmp_files(PhoneticCorpusFile, TmpAlignedTextFile, TmpAlignedLexiconFile, ConfigFile)
    elif Id == 'arabic_abc':
        PhoneticCorpusFile = '$LARA/tmp_resources/arabic_abc_phonetic.txt'
        TmpAlignedTextFile = '$LARA/tmp_resources/arabic_abc_tmp_phonetic_annotations_aligned.json'
        TmpAlignedLexiconFile = '$LARA/tmp_resources/arabic_abc_tmp_phonetic_lexicon_aligned.json'
        ConfigFile = '$LARA/Content/arabic_alphabet_book/corpus/local_config.json'
        make_phonetic_version_of_corpus_file_and_tmp_files(PhoneticCorpusFile, TmpAlignedTextFile, TmpAlignedLexiconFile, ConfigFile)
    elif Id == 'le_petit_prince_merge':
        OldLexicon = '$LARA/Code/LinguisticData/french/fr_FR_pronunciation_dict_aligned.json'
        NewLexicon = '$LARA/Content/le_petit_prince/corpus/le_petit_prince_abc2_examples_tmp_phonetic_aligned_lexicon.json'
        merge_aligned_phonetic_lexica(OldLexicon, NewLexicon)
    elif Id == 'the_little_prince_merge':
        OldLexicon = '$LARA/Code/LinguisticData/english/en_UK_pronunciation_dict_aligned.json'
        NewLexicon = '$LARA/tmp_resources/the_little_prince_abc2_examples_tmp_phonetic_aligned_lexicon.json'
        merge_aligned_phonetic_lexica(OldLexicon, NewLexicon)
    elif Id == 'le_petit_prince_ipa_metadata':
        Dir = '$LARA/Content/french_ipa/audio/ipa_reader_celine'
        TmpMetadataFile = 'metadata_help_tmp.json'
        create_metadata_for_ipa_reader_audio(Dir, TmpMetadataFile)
    elif Id == 'le_petit_prince_ipa_metadata_reduced':
        Dir = '$LARA/Content/french_ipa/audio/ipa_reader_celine_reduced'
        TmpMetadataFile = 'metadata_help.json'
        create_metadata_for_ipa_reader_audio(Dir, TmpMetadataFile)
    else:
        lara_utils.print_and_flush(f'*** Error: unknown id "{Id}"')

# ------------------------------------------

def make_phonetic_version_of_corpus_file_and_tmp_files(PhoneticCorpusFile, TmpAlignedTextFile, TmpAlignedLexiconFile, ConfigFile):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    #if Params == False or Params.aligned_phonetic_annotations_file == '':
    if Params == False:
        return
    PhoneticAlignementsForSegments = read_aligned_phonetic_annotations_file(Params)
    PageOrientedSplitList = lara_mwe.read_split_file_applying_mwes_if_possible(Params)
    if PageOrientedSplitList == False:
        return False
    load_phonetic_lexicons_if_available(Params)
    ( PageOrientedSplitList1, TmpAlignments ) = add_phonetic_alignments_to_split_list(PageOrientedSplitList, PhoneticAlignementsForSegments, Params)
    make_tmp_aligned_phonetic_text_file(PageOrientedSplitList1, TmpAlignedTextFile)
    make_tmp_aligned_phonetic_lexicon_file(TmpAlignments, TmpAlignedLexiconFile)
    split_list_with_phonetic_alignments_to_corpus_file(PageOrientedSplitList1, PhoneticCorpusFile, Params)

def read_aligned_phonetic_annotations_file(Params):
    File = Params.aligned_phonetic_annotations_file
    if File == '' or not lara_utils.file_exists(File):
        return False
    Data = lara_utils.read_json_file(File)
    return aligned_phonetic_annotations_file_data_to_dict(Data)

def aligned_phonetic_annotations_file_data_to_dict(Data):
    if not isinstance(Data, ( list, tuple )):
        return False
    Dict = {}
    for Record in Data:
        Key = tuple([ Tuple[0] for Tuple in Record ])
        Dict[Key] = Record
    return Dict

def load_phonetic_lexicons_if_available(Params):
    if Params.phonetic_lexicon_aligned != '':
        load_aligned_phonetic_lexicon(Params.phonetic_lexicon_aligned)
    if Params.phonetic_lexicon_plain != '':
        load_plain_phonetic_lexicon(Params.phonetic_lexicon_plain)

_aligned_phonetic_lexicon = {}

def aligned_phonetic_pair_for_word(Word):
    return _aligned_phonetic_lexicon[Word] if Word in _aligned_phonetic_lexicon else False

_plain_phonetic_lexicon = {}

def phonetic_entry_for_word(Word):
    if Word in _plain_phonetic_lexicon:
        return _plain_phonetic_lexicon[Word]
    Word1 = normalise_word_for_phonetic_lex(Word)
    if Word1 in _plain_phonetic_lexicon:
        return _plain_phonetic_lexicon[Word1]
    else:
        return False

def load_aligned_phonetic_lexicon(File):
    global _aligned_phonetic_lexicon
    if not lara_utils.file_exists(File):
        lara_utils.print_and_flush(f'*** Warning: {File} not found, not loading aligned phonetic lexicon')
        return
    LexiconData = lara_utils.read_json_file(File)
    if isinstance(LexiconData, dict):
        _aligned_phonetic_lexicon = LexiconData
        lara_utils.print_and_flush(f'--- Loaded aligned phonetic lexicon from {File}, {len(list(LexiconData.keys()))} records')
    else:
        lara_utils.print_and_flush(f'*** Warning: unable to read aligned phonetic lexicon file {File}')

def load_plain_phonetic_lexicon(File):
    global _plain_phonetic_lexicon
    if not lara_utils.file_exists(File):
        lara_utils.print_and_flush(f'*** Warning: {File} not found, not loading plain phonetic lexicon')
        return
    LexiconData = lara_utils.read_json_file(File)
    if isinstance(LexiconData, dict):
        _plain_phonetic_lexicon = LexiconData
        lara_utils.print_and_flush(f'--- Loaded plain phonetic lexicon from {File}, {len(list(LexiconData.keys()))} records')
    else:
        lara_utils.print_and_flush(f'*** Warning: unable to read plain phonetic lexicon file {File}')
                                
def add_phonetic_alignments_to_split_list(PageOrientedSplitList, PhoneticAlignementsForSegments, Params):
    PageOrientedSplitList1 = []
    TmpAlignments = {}
    for ( PageInfo, Segments ) in PageOrientedSplitList:
        Segments1 = []
        for Segment in Segments:
            if lara_picturebook.is_annotated_image_segment(Segment):
                Segment1 = ( '*annotated_image*', Segment )
            else:
                ( Raw, Clean, Pairs, Tag ) = Segment
                Words = [ Pair[0] for Pair in Pairs if Pair[1] != '' ] 
                Key = tuple(Words)
                if isinstance(PhoneticAlignementsForSegments, dict) and Key in PhoneticAlignementsForSegments:
                    Segment1 = add_existing_phonetic_alignment_to_pairs(Pairs, PhoneticAlignementsForSegments[Key])
                elif is_heading_string(Raw) and Params.phonetic_headings_are_comments == 'yes':
                    Segment1 = make_phonetic_heading_segment( ( Raw, Clean, Pairs, Tag ) )
                # If we've got phonetic_headings_are_comments = no and there is just one word in the heading, we can make it real text
                elif is_heading_string(Raw) and len( [ Pair for Pair in Pairs if Pair[1] != '' ] ) == 1:
                    Segment1 = make_first_content_word_as_heading(add_new_phonetic_alignments_to_pairs(Pairs, TmpAlignments, Params))
                # If we've got phonetic_headings_are_comments = no and more than one word in the heading, something is wrong
                elif is_heading_string(Raw):
                    lara_utils.print_and_flush(f'*** Warning: phonetic_headings_are_comments = no, but more than one word in heading: {Raw}')
                    Segment1 = add_new_phonetic_alignments_to_pairs(Pairs, TmpAlignments, Params)
                else:
                    Segment1 = add_new_phonetic_alignments_to_pairs(Pairs, TmpAlignments, Params)
            Segments1 += [ Segment1 ]
        PageOrientedSplitList1 += [ Segments1 ]
    return ( PageOrientedSplitList1, TmpAlignments)

def make_first_content_word_as_heading(Triples):
    if not isinstance(Triples, ( list, tuple ) ):
        lara_utils.print_and_flush(f'*** Error: arg to make_first_content_word_as_heading not a list: {Triples}')
        return False
    if len(Triples) == 0:
        return Triples
    ( First, Rest ) = ( Triples[0], Triples[1:] )
    # We mark the first content word as *heading_body* so that we can treat it specially in segment_item_to_phonetic_text
    if First[2] != '':
        return [ [ '*heading_body*', First[1], First[2] ] ] + Rest
    else:
        return [ First ] + make_first_content_word_as_heading(Rest)

# We treat headings specially: in the phonetic version, they are formatted with comments around the body
# and a segment break afterwards. This is needed to get tables of contents right.
def is_heading_string(Raw):
    Match = re.search("<(h[12])>([^<]*)", Raw, flags=re.DOTALL)
    return Match is not None 

def make_phonetic_heading_segment(Segment):
    ( Raw, Clean, Pairs, Tag ) = Segment
    Text = ''.join([ Pair[0] for Pair in Pairs ])
    # Remove any existing comments
    Text = Text.replace('/*', '')
    Text = Text.replace('*/', '')
    # Add new comments after the initial tag and at the end
    Match = re.search("(<h[12]>)(.*)", Text, flags=re.DOTALL)
    HeaderTag = Match.group(1)
    # We mark the body as *heading* so that we can treat it specially in segment_item_to_phonetic_text
    return [ [ '*heading*', Text.replace(HeaderTag, f'{HeaderTag}/*') + '*/', '' ] ]

def add_existing_phonetic_alignment_to_pairs(Pairs, ExistingPhoneticAlignments):
    Segment1 = []
    for Pair in Pairs:
        ( Word, Lemma ) = Pair[:2]
        if Lemma == '':
            Segment1 += [ Pair[:2] ]
        else:
            Segment1 += [ ExistingPhoneticAlignments[0] ]
            ExistingPhoneticAlignments = ExistingPhoneticAlignments[:1]
    return Segment1

def add_new_phonetic_alignments_to_pairs(Pairs, TmpAlignments, Params):
    Segment1 = []
    for Pair in Pairs:
        ( Word, Lemma ) = Pair[:2]
        if Lemma == '':
            Segment1 += [ [ Word, Word, '' ] ]
        else:
            Word1 = normalise_word_for_phonetic_lex(Word)
            ( AlignedWord, AlignedPhonetic ) = guess_alignment_for_word(Word1, TmpAlignments, Params)
            AlignedWord1 = AlignedWord if Word == Word1 else transfer_casing_to_aligned_word(Word, AlignedWord)
            Segment1 += [ [ Word, AlignedWord1, AlignedPhonetic ] ]
            if not Word1 in TmpAlignments and aligned_phonetic_pair_for_word(Word1) == False:
                TmpAlignments[Word1] = [ AlignedWord, AlignedPhonetic ]
    return Segment1

def transfer_casing_to_aligned_word(Word, AlignedWord):
    try:
        return transfer_casing_to_aligned_word1(Word, AlignedWord)
    except:
        lara_utils.print_and_flush(f'*** Error: bad call: transfer_casing_to_aligned_word({Word}, {AlignedWord})')
        return AlignedWord

def transfer_casing_to_aligned_word1(Word, AlignedWord):
    AlignedWord1 = ''
    for Letter in AlignedWord:
        if Letter == '|':
            AlignedWord1 += Letter
        else:
            Letter1 = Word[0]
            AlignedWord1 += Letter1
            Word = Word[1:]
    return AlignedWord1

def guess_alignment_for_word(Word, TmpAlignments, Params):
    if Word in TmpAlignments:
        return TmpAlignments[Word]
    AlignedPair = aligned_phonetic_pair_for_word(Word)
    if AlignedPair != False and check_aligned_pair(Word, AlignedPair):
        return aligned_phonetic_pair_for_word(Word)
    Word1 = lara_parse_utils.remove_disambiguation_annotation_from_word(Word)
    # If we can interpret the number as a word and convert it to text, do that
    NumberWord = lara_number_words.spell_out_number_word(Word1, Params.language)
    if NumberWord != False:
        return guess_alignment_for_word(NumberWord, TmpAlignments, Params)
    # If we have a word that can be broken into pieces at spaces or hyphens, do that
    if len(Word1.split()) != 1 or len(Word1.split('-')) != 1:
        ( Components, Separator ) = ( Word1.split(), ' ' ) if len(Word1.split()) != 1 else ( Word1.split('-'), '-' )
        AlignedPairs = [ guess_alignment_for_word(Component, TmpAlignments, Params) for Component in Components ]
        return [ f'|{Separator}|'.join( [ AlignedPair[0] for AlignedPair in AlignedPairs ] ),
                 '||'.join( [ AlignedPair[1] for AlignedPair in AlignedPairs ] ) ]
    if phonetically_spelled_language(Params.language):
        return alignment_for_phonetically_spelled_language(Word, Params.language)
    PhoneticEntry = phonetic_entry_for_word(Word)
    if PhoneticEntry != False and Params.phonetic_lexicon_aligned != '':
        PhoneticEntry1 = lara_phonetic_align.remove_accents_from_phonetic_string(PhoneticEntry)
        GuessedPair = lara_phonetic_align.dp_phonetic_align(Word1, PhoneticEntry1, Params)
        if isinstance(GuessedPair, ( list, tuple )) and len(GuessedPair) == 2:
            return [ GuessedPair[0], GuessedPair[1] ]
        else:
            return [ Word1, PhoneticEntry ]
    else:
        lara_utils.print_and_flush(f'*** Warning: no phonetic entry found for "{Word}"')
        return [ Word, Word ]

def check_aligned_pair(Word, AlignedPair):
    if not isinstance(AlignedPair, ( list, tuple )) and not len(AlignedPair) == 2:
        lara_utils.print_and_flush(f'*** Error: bad aligned phonetic pair for "{Word}", not a pair')
        lara_utils.print_and_flush(f'*** Error: {AlignedPair}')
        return False
    if len(AlignedPair[0].split('|')) != len(AlignedPair[1].split('|')):
        lara_utils.print_and_flush(f'*** Error: bad aligned phonetic pair for "{Word}", not aligned')
        lara_utils.print_and_flush(f'*** Error: {AlignedPair}')
        return False
    return True

def make_tmp_aligned_phonetic_text_file(PageOrientedSplitList1, TmpAlignedTextFile):
    PhoneticTextList = phonetic_page_oriented_split_list_to_aligned_phonetic_text_list(PageOrientedSplitList1)
    lara_utils.write_json_to_file_plain_utf8(PhoneticTextList, TmpAlignedTextFile)

def phonetic_page_oriented_split_list_to_aligned_phonetic_text_list(PageOrientedSplitList):
    OutList = []
    for Page in PageOrientedSplitList:
        for Segment in Page:
            if not is_annotated_image_in_phonetic_page_oriented_split_list(Segment):
                Segment1 = [ Item for Item in Segment if Item[2] != '' ]
                if len(Segment1) != 0:
                    OutList += [ Segment1 ]
    return OutList
                                
def make_tmp_aligned_phonetic_lexicon_file(TmpAlignments, TmpAlignedLexiconFile):
    lara_utils.write_json_to_file_plain_utf8(TmpAlignments, TmpAlignedLexiconFile)

def split_list_with_phonetic_alignments_to_corpus_file(PageOrientedSplitList1, PhoneticCorpusFile, Params):
    PageStrings = [ page_to_phonetic_text(Page, Params) for Page in PageOrientedSplitList1 ]
    FullText = '<page>\n'.join(PageStrings)
    lara_utils.write_lara_text_file(FullText, PhoneticCorpusFile)

def page_to_phonetic_text(Page, Params):
    SegmentStrings = [ segment_to_phonetic_text(Segment, Params) for Segment in Page ]
    return ''.join(SegmentStrings)

def segment_to_phonetic_text(Segment, Params):
    if is_annotated_image_in_phonetic_page_oriented_split_list(Segment):
        AnnotatedImageSegment = Segment[1]
        return lara_picturebook.annotated_image_segment_to_string(AnnotatedImageSegment)
    else:
        SegmentItemStrings = [ segment_item_to_phonetic_text(Item, Params) for Item in Segment ]
        return ''.join(SegmentItemStrings)

def is_annotated_image_in_phonetic_page_oriented_split_list(Segment):
    return isinstance(Segment, ( list, tuple )) and len(Segment) == 2 and Segment[0] == '*annotated_image*'

def segment_item_to_phonetic_text(Item, Params):
    if not isinstance(Item, ( list, tuple )) and not len(Item) == 3:
        lara_utils.print_and_flush(f'*** Error: bad segment item {Item}: not a triple')
        return False
    # If it's a comment heading, start a new segment
    elif Item[0] == '*heading*' and Item[2] == '':
        return f'{Item[0]}||'
    elif Item[2] == '':
        return Item[0]
    else:
        ( Word, SegmentedWord, SegmentedPhonetic ) = Item
        ( SegmentedWordComponents, SegmentedPhoneticComponents ) = ( SegmentedWord.split('|'), SegmentedPhonetic.split('|') )
        WordComponentPhoneticComponentPairs = zip( SegmentedWordComponents, SegmentedPhoneticComponents )
        PhoneticWordComponents = [ word_component_phonetic_component_pair_to_phonetic_text_string(Item, Params) for
                                   Item in WordComponentPhoneticComponentPairs ]
        Body = '|'.join(PhoneticWordComponents)
        return f'||{Body}||' if Word != '*heading_body*' else f'{Body}||'

def word_component_phonetic_component_pair_to_phonetic_text_string(Item, Params):
    ( WordComponent, PhoneticComponent ) = Item
    # Half-spaces in Arabic script languages should be more or less invisible, so don't add phonetic annotation
    if WordComponent == _half_space:
        return _half_space
    WordComponent1 = representation_of_unwritten_component_in_word(Params) if WordComponent == '' else WordComponent
    PhoneticComponent1 = representation_of_silent_component_in_word(Params) if PhoneticComponent == '' else PhoneticComponent
    return f'@{WordComponent1}@#{PhoneticComponent1}#' if WordComponent1 != '' else ''

def representation_of_unwritten_component_in_word(Params):
    return ''

def representation_of_silent_component_in_word(Params):
    return '(silent)'

def normalise_word_for_phonetic_lex(Word):
    #return Word.lower().replace("’", "'").replace("\u200c", "")
    return Word.lower().replace("’", "'")

# ------------------------------------------

def phonetically_spelled_language(Language):
    if not Language in lara_config._phonetically_spelled_languages:
        return False
    Alphabet = lara_config._phonetically_spelled_languages[Language]
    AlphabetInternalised = internalise_alphabet_for_phonetically_spelled_language(Alphabet + _hyphens_and_apostrophes)
    if AlphabetInternalised == False:
        lara_utils.print_and_flush(f'*** Error: malformed phonetic list for "{Language}"')
        return False
    else:
        return True

def alignment_for_phonetically_spelled_language(Word, Language):
    Alphabet = lara_config._phonetically_spelled_languages[Language]
    AccentChars = lara_config._accent_chars[Language] if Language in lara_config._accent_chars else []
    ( DecompositionWord, DecompositionPhonetic ) = greedy_decomposition_of_word(Word, Alphabet, AccentChars)
    if DecompositionWord == False:
        lara_utils.print_and_flush(f'*** Warning: unable to spell out "{Word}" as {Language} word')
        return ( Word, Word )
    WordWithSeparators = '|'.join(DecompositionWord)
    PhoneticWithSeparators = '|'.join(DecompositionPhonetic)
    return ( WordWithSeparators, PhoneticWithSeparators )

_half_space = "\u200c"

_hyphens_and_apostrophes = [ "-", "'", "’", _half_space ]

def greedy_decomposition_of_word(Word, Alphabet, AccentChars):
    ( DecompositionWord, DecompositionPhonetic ) = ( [], [] )
    AlphabetInternalised = internalise_alphabet_for_phonetically_spelled_language(Alphabet + _hyphens_and_apostrophes)
    while True:
        if Word == '':
            return ( DecompositionWord, DecompositionPhonetic )
        PossibleNextComponents = [ Letter for Letter in AlphabetInternalised if Word.startswith(Letter) == True ] 
        if PossibleNextComponents == []:
            lara_utils.print_and_flush(f'*** Warning: unable to match "{Word}" against alphabet')
            return ( False, False )
        SortedPossibleNextComponents = sorted(PossibleNextComponents, key=lambda x: len(x), reverse=True)
        NextComponent = SortedPossibleNextComponents[0]
        Accents = initial_accent_chars(Word[len(NextComponent):], AccentChars)
        NextComponentWithAccents = NextComponent + Accents
        DecompositionWord += [ NextComponentWithAccents ]
        if not NextComponent in _hyphens_and_apostrophes:
            DecompositionPhonetic += [ AlphabetInternalised[NextComponent] ]
        else:
            DecompositionPhonetic += [ '' ]
        Word = Word[len(NextComponentWithAccents):]
    # Shouldn't ever get here, but just in case...
    lara_utils.print_and_flush(f'*** Warning: unable to match "{Word}" against alphabet')
    return ( False, False )

def initial_accent_chars(Str, AccentChars):
    if len(Str) != 0 and Str[0] in AccentChars:
        return Str[0] + initial_accent_chars(Str[1:], AccentChars)
    else:
        return ''

def internalise_alphabet_for_phonetically_spelled_language(Alphabet):
    Internalised = {}
    for Item in Alphabet:
        if isinstance(Item, ( str )):
            Internalised[Item] = Item
        elif isinstance(Item, ( list, tuple )) and len(Item) != 0:
            MainLetter = Item[0]
            for Letter in Item:
                Internalised[Letter] = MainLetter
        else:
            lara_utils.print_and_flush(f'*** Error: bad item in alphabet for phonetically spelled language: {Item}')
            return False
    return Internalised

# ------------------------------------------

def merge_aligned_phonetic_lexica(OldLexicon, NewLexicon):
    OldLexiconData = lara_utils.read_json_file(OldLexicon)
    if not isinstance(OldLexiconData, dict):
        lara_utils.print_and_flush(f'*** Error: unable to read old aligned lexicon file {OldLexicon}, doing nothing')
        return False
    lara_utils.print_and_flush(f'--- Read old aligned lexicon ({len(OldLexiconData)} entries)')
    NewLexiconData = lara_utils.read_json_file(NewLexicon)
    if not isinstance(NewLexiconData, dict):
        lara_utils.print_and_flush(f'*** Error: unable to read new aligned lexicon file {NewLexicon}, doing nothing')
        return False
    lara_utils.print_and_flush(f'--- Read additions to aligned lexicon ({len(NewLexiconData)} entries)')
    NErrors = 0
    for Key in NewLexiconData:
        AlignedPair = NewLexiconData[Key]
        if check_aligned_pair(Key, AlignedPair):
            OldLexiconData[Key] = AlignedPair
        else:
            NErrors += 1
    #OutFile = '$LARA/tmp/merged_aligned_lexicon.json'
    OutFile = OldLexicon
    lara_utils.write_json_to_file_plain_utf8(OldLexiconData, OutFile)
    lara_utils.print_and_flush(f'--- Merged aligned lexica ({len(OldLexiconData)} entries, {NErrors} errors) written to {OutFile}')

# ------------------------------------------

def internalise_french_pronunciation_dict():
    RawDictFile = '$LARA/Content/french/corpus/fr_FR_pronunciation_dict.txt'
    InternalisedDictFile = '$LARA/Code/LinguisticData/french/corpus/fr_FR_pronunciation_dict.json'
    internalise_french_style_pronunciation_dict(RawDictFile, InternalisedDictFile)

def internalise_english_pronunciation_dict():
    RawDictFile = '$LARA/Code/LinguisticData/english/en_UK.txt'
    InternalisedDictFile = '$LARA/Code/LinguisticData/english/en_UK_pronunciation_dict.json'
    internalise_french_style_pronunciation_dict(RawDictFile, InternalisedDictFile)

def internalise_french_style_pronunciation_dict(RawDictFile, InternalisedDictFile):
    Lines = lara_utils.read_unicode_text_file_to_lines(RawDictFile)
    lara_utils.print_and_flush(f'--- Read dict file {RawDictFile}, {len(Lines)} lines')
    Dict = {}
    for Line in Lines:
        Line1 = remove_alternate_pronunciations_from_french_style_dict_line(Line)
        Components = Line1.split()
        if len(Components) == 2 and '/' in Components[1]:
            ( Word, Pronunciation ) = Components
            Word1 = normalise_word_for_phonetic_lex(Word)
            Dict[Word1] = Pronunciation.replace('/', '')
    lara_utils.write_json_to_file_plain_utf8(Dict, InternalisedDictFile)
    lara_utils.print_and_flush(f'--- Written internalised dict file {InternalisedDictFile}, {len(list(Dict.keys()))} lines')

def remove_alternate_pronunciations_from_french_style_dict_line(Line):
    return Line.split(',')[0]

# ------------------------------------------

##    {
##        "file": "",
##        "text": "aj"
##    },

def create_metadata_for_ipa_reader_audio(Dir, TmpMetadataFile):
    if not lara_utils.directory_exists(Dir):
        lara_utils.print_and_flush(f'*** Error: {Dir} not found')
        return
    TmpMetadata = lara_utils.read_json_file(f'{Dir}/{TmpMetadataFile}')
    if TmpMetadata == False:
        lara_utils.print_and_flush(f'*** Error: unable to read {TmpMetadataFile}')
        return
    Metadata = []
    for Item in TmpMetadata:
        if not isinstance(Item, dict) or not 'text' in Item:
            lara_utils.print_and_flush(f'*** Error: bad item in tmp metadata: {Item}')
            return
        Phon = Item['text']
        File = find_audio_file_name_for_phonetic_text(Phon, Dir)
        Item1 = { 'text': Phon, 'file': File }
        Metadata += [ Item1 ]
    MetadataFile = f'{Dir}/metadata_help.json'
    lara_utils.write_json_to_file_plain_utf8(Metadata, MetadataFile)
    
def find_audio_file_name_for_phonetic_text(Phon, Dir):
    # We may try adding ə to some consonants so that the audio is long enough to hear.
    PossibleFiles = ( f'{Phon}.mp3', f'{Phon}ə.mp3' )
    for PossibleFile in PossibleFiles:
        if lara_utils.file_exists(f'{Dir}/{PossibleFile}'):
            return PossibleFile
    lara_utils.print_and_flush(f'*** Warning: no audio found for: "{Phon}"')
    return ''

