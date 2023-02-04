import lara_config
import lara_parse_utils
import lara_utils

_trace = 'off'

def test(Id):
    if Id == 'eng1':
        ConfigFile = '$LARA/Content/the_little_prince/corpus/local_config_abc2_examples.json'
        Letters = 'art'
        Phonemes = 'ɑːt'
    elif Id == 'eng2':
        ConfigFile = '$LARA/Content/the_little_prince/corpus/local_config_abc2_examples.json'
        Letters = 'calories'
        Phonemes = 'kæləɹiz'
    else:
        lara_utils.print_and_flush(f'*** Error: unknown ID "{Id}"')
        return
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if Params != False:
        Result = dp_phonetic_align(Letters, Phonemes, Params)
        lara_utils.print_and_flush(f'Aligning "{Letters}" with "{Phonemes}": {Result}')

def test_eval(Id):
    if Id == 'lpp_eng':
        EditedLexicon = '$LARA/Content/the_little_prince/corpus/the_little_prince_phonetic_aligned_lexicon_edited.json'
        RawLexicon = '$LARA/Content/the_little_prince/corpus/the_little_prince_phonetic_aligned_lexicon_original.json'
    elif Id == 'lpp_fre':
        EditedLexicon = '$LARA/Content/le_petit_prince/corpus/le_petit_prince_phonetic_aligned_lexicon_edited.json'
        RawLexicon = '$LARA/Content/le_petit_prince/corpus/le_petit_prince_phonetic_aligned_lexicon_raw.json'
    elif Id == 'lpp_fre_ait_unchanged':
        EditedLexicon = '$LARA/Content/le_petit_prince/corpus/le_petit_prince_phonetic_aligned_lexicon_edited_ait.json'
        RawLexicon = '$LARA/Content/le_petit_prince/corpus/le_petit_prince_phonetic_aligned_lexicon_raw.json'
    else:
        lara_utils.print_and_flush(f'*** Error: unknown ID "{Id}"')
        return
    evaluate_aligned_lexicon(EditedLexicon, RawLexicon)

def test_edit(Id):
    if Id == 'lpp_fre_ait':
        RawLexicon = '$LARA/Content/le_petit_prince/corpus/le_petit_prince_phonetic_aligned_lexicon_edited.json'
        Edits = [ ( ( 'ai|t', 'ɛ|' ), ( 'ait', 'ɛ' ) ) ]
        EditLexicon = '$LARA/Content/le_petit_prince/corpus/le_petit_prince_phonetic_aligned_lexicon_edited_ait.json'
    edit_aligned_lexicon(RawLexicon, Edits, EditLexicon)

def test_align(Lang, Letters, Phonemes):
    global _loaded_aligned_lexicon
    _loaded_aligned_lexicon = {}
    if Lang == 'eng':
        ConfigFile = '$LARA/Content/the_little_prince/corpus/local_config_abc2_examples.json'
    elif Lang == 'fre':
        ConfigFile = '$LARA/Content/le_petit_prince/corpus/local_config_abc2_examples.json'
    else:
        lara_utils.print_and_flush(f'*** Error: unsupported language {Lang}"')
        return
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if Params != False:
        Result = dp_phonetic_align(Letters, Phonemes, Params)
        lara_utils.print_and_flush(f'Aligning "{Letters}" with "{Phonemes}": {Result}')

def random_test(Lang, N):
    global _loaded_aligned_lexicon
    _loaded_aligned_lexicon = {}
    if Lang == 'eng':
        ConfigFile = '$LARA/Content/the_little_prince/corpus/local_config_abc2_examples.json'
    elif Lang == 'fre':
        ConfigFile = '$LARA/Content/le_petit_prince/corpus/local_config_abc2_examples.json'
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if Params != False:
        random_test1(Lang, Params, N)

def random_test1(Lang, Params, N):
    Lexicon = Params.phonetic_lexicon_plain
    if Lexicon == '':
        lara_utils.print_and_flush(f'*** Error: no phonetic lexicon defined"')
        return
    LexiconData = lara_utils.read_json_file(Lexicon)
    if not isinstance(LexiconData, dict):
        lara_utils.print_and_flush(f'*** Error: unable to read phonetic lexicon {Lexicon}"')
        return
    Words = list(LexiconData.keys())
    lara_utils.print_and_flush(f'--- Read {Lexicon} ({len(Words)} entries)')
    ( OutList, OutDict ) = ( [], {} )
    lara_utils.print_and_flush(f'--- Aligning {N} random items')
    for I in range(0, N):
        Letters = lara_utils.random_choose_from_list(Words)
        Phonemes = remove_accents_from_phonetic_string(LexiconData[Letters])
        Result = dp_phonetic_align(Letters, Phonemes, Params)
        lara_utils.print_and_flush_no_newline('.')
        OutList += [ f'Aligning "{Letters}" with "{Phonemes}": {Result}' ]
        if isinstance(Result, ( list, tuple )) and len(Result) == 2:
            OutDict[Letters] = [ Result[0], Result[1] ]
    lara_utils.print_and_flush('\n\n----------------------')
    for Line in sorted(OutList):
        lara_utils.print_and_flush(Line)
    lara_utils.write_json_to_file_plain_utf8(OutDict, f'$LARA/tmp_resources/random_aligned_{Lang}.json')

def dp_phonetic_align(Letters, Phonemes, Params):
    NLoadedPairs = load_aligned_lexicon_if_necessary(Params)
    if NLoadedPairs == 0:
        return False
    if Letters == '' and Phonemes == '':
        return ( '', '' )
    ( N, N1 ) = ( len(Letters), len(Phonemes) )
    DPDict = {}
    DPDict[(0, 0)] = ( 0, [], [] )
    for TotalMatchLength in range(0, N + N1 ):
        for MatchLengthL in range(0, TotalMatchLength + 1):
            MatchLengthR = TotalMatchLength - MatchLengthL
            extend(Letters, Phonemes, MatchLengthL, MatchLengthR, N, N1, DPDict)
    if ( N, N1 ) in DPDict:
        ( BestCost, BestAlignedLetters, BestAlignedPhonemes ) = DPDict[( N, N1 )]
        return ( '|'.join(BestAlignedLetters), '|'.join(BestAlignedPhonemes) )
    else:
        lara_utils.print_and_flush(f'*** Error: unable to do DP match between "{Letters}" and "{Phonemes}"')
        return False

def extend(Letters, Phonemes, MatchLengthL, MatchLengthP, NL, NP, DPDict):
    if _trace == 'on':
        lara_utils.print_and_flush(f'--- extend({Letters}, {Phonemes}, {MatchLengthL}, {MatchLengthP}, {NL}, {NP}, DPDict)')
        lara_utils.prettyprint(DPDict)
    if MatchLengthL > NL or MatchLengthP > NP:
        if _trace == 'on': lara_utils.print_and_flush(f'--- Length exceeded')
        return
    KeysL = [ '' ] if MatchLengthL == NL else [ '', Letters[MatchLengthL], 'skip' ]
    KeysP = [ '' ] if MatchLengthP == NP else [ '', Phonemes[MatchLengthP], 'skip' ]
    if _trace == 'on': lara_utils.print_and_flush(f'--- KeysL = {KeysL}, KeysP = {KeysP}')
    for KeyL in KeysL:
        for KeyP in KeysP:
            if _trace == 'on': lara_utils.print_and_flush(f'--- KeyL = "{KeyL}", KeyP = "{KeyP}"')
            # If we extend using a known match loaded from the aligned lexicon, we charge 2 if a null string is used, otherwise 1
            if KeyL != 'skip' and KeyP != 'skip':
                Key = ( KeyL, KeyP )
                if Key in _loaded_aligned_lexicon:
                    PossibleAlignments = _loaded_aligned_lexicon[Key]
                    for ( AlignedLetters, AlignedPhonemes ) in PossibleAlignments:
                        Cost = 2 if '' in ( AlignedLetters, AlignedPhonemes ) else 1
                        extend1(Letters, Phonemes, MatchLengthL, MatchLengthP, AlignedLetters, AlignedPhonemes, Cost, DPDict)
            # If we extend by skipping a character in either Letters or Phonemes, we charge 5 
            elif KeyL == 'skip' and KeyP == '':
                ( AlignedLetters, AlignedPhonemes, Cost ) = ( Letters[MatchLengthL], '', 5 )
                extend1(Letters, Phonemes, MatchLengthL, MatchLengthP, AlignedLetters, AlignedPhonemes, Cost, DPDict)
            elif KeyL == '' and KeyP == 'skip':
                ( AlignedLetters, AlignedPhonemes, Cost ) = ( '', Phonemes[MatchLengthP], 5 )
                extend1(Letters, Phonemes, MatchLengthL, MatchLengthP, AlignedLetters, AlignedPhonemes, Cost, DPDict)

def extend1(Letters, Phonemes, MatchLengthL, MatchLengthP, AlignedLetters, AlignedPhonemes, ExtraCost, DPDict):
    if _trace == 'on':
        lara_utils.print_and_flush(f'--- extend1({Letters}, {Phonemes}, {MatchLengthL}, {MatchLengthP}, "{AlignedLetters}", "{AlignedPhonemes}", {ExtraCost}, DPDict)')
    if Letters[MatchLengthL:].startswith(AlignedLetters) and Phonemes[MatchLengthP:].startswith(AlignedPhonemes):
        ( CurrentCost, CurrentMatchL, CurrentMatchP ) = DPDict[ ( MatchLengthL, MatchLengthP ) ]
        ( NewCost, NewMatchL, NewMatchP ) = ( CurrentCost + ExtraCost, CurrentMatchL + [ AlignedLetters ], CurrentMatchP + [ AlignedPhonemes ] )
        NewKey = ( MatchLengthL + len(AlignedLetters), MatchLengthP + len(AlignedPhonemes) )
        if not NewKey in DPDict or DPDict[NewKey][0] > NewCost:
            DPDict[NewKey] = ( NewCost, NewMatchL, NewMatchP )

_loaded_aligned_lexicon = {}

## "came": [
##        "c|a|m|e",
##        "k|e‍ɪ|m|"
##    ]

def load_aligned_lexicon_if_necessary(Params):
    global _loaded_aligned_lexicon
    LexiconFile = Params.phonetic_lexicon_aligned
    if Params.phonetic_lexicon_aligned == '':
        # There is no aligned lexicon
        return 0
    if len(_loaded_aligned_lexicon) > 0:
        # Lexion is already loaded
        return len(_loaded_aligned_lexicon)
    Data = lara_utils.read_json_file(LexiconFile)
    if Data == False:
        # Couldn't read aligned lexicon
        return 0
    Count = 0
    for Word in Data:
        Value = Data[Word]
        if not isinstance(Value, list) or not len(Value) == 2 or not isinstance(Value[0], str) or not isinstance(Value[1], str):
            lara_utils.print_and_flush(f'*** Error: bad entry in aligned lexicon, not a pair, "{Word}"')
        ( Letters, Phonemes0 ) = Value
        Phonemes = remove_accents_from_phonetic_string(Phonemes0)
        ( LetterComponents, PhonemeComponents ) = ( Letters.split('|'), Phonemes.split('|') )
        if not len(LetterComponents) == len(PhonemeComponents):
            lara_utils.print_and_flush(f'*** Error: bad entry in aligned lexicon, not aligned, "{Word}"')
        for ( LetterGroup, PhonemeGroup ) in zip( LetterComponents, PhonemeComponents ):
            Key = ( '' if LetterGroup == '' else LetterGroup[0], '' if PhonemeGroup == '' else PhonemeGroup[0] )
            Current = _loaded_aligned_lexicon[Key] if Key in _loaded_aligned_lexicon else []
            Correspondence = ( LetterGroup, PhonemeGroup )
            if not Correspondence in Current:
                _loaded_aligned_lexicon[Key] = Current + [ Correspondence ]
                Count += 1
    lara_utils.print_and_flush(f'--- Loaded aligned lexicon, {Count} different letter/phoneme correspondences')
    return Count
        
def remove_accents_from_phonetic_string(Str):
    return Str.replace('ˈ', '').replace('ˌ', '').replace('\u200d', '')

#-------------------------

# Sample edit: ( ( 'ai|t', 'ɛ|' ), ( 'ait', 'ɛ' ) )

def edit_aligned_lexicon(LexiconFile, Edits, LexiconFile1):
    Lexicon = lara_utils.read_json_file(LexiconFile)
    InternalisedEdits = internalise_lexicon_edits(Edits)
    if Lexicon == False or False in InternalisedEdits:
        return
    Lexicon1 = { Key: apply_lexicon_edits(Lexicon[Key], InternalisedEdits) for Key in Lexicon }
    if False in [ Lexicon1[Key] for Key in Lexicon1 ]:
        return
    lara_utils.write_json_to_file_plain_utf8(Lexicon1, LexiconFile1)

def internalise_lexicon_edits(Edits):
    return [ internalise_lexicon_edit(Edit) for Edit in Edits ]

def internalise_lexicon_edit(Edit):
    if not isinstance(Edit, ( list, tuple ) ) or not len(Edit) == 2 or not is_edit_component(Edit[0]) or not is_edit_component(Edit[1]):
        lara_utils.print_and_flush(f'*** Error: malformed edit: {Edit}')
        return False
    ( From, To ) = Edit
    ( From1, To1 ) = ( internalise_lexicon_edit_component(From), internalise_lexicon_edit_component(To) )
    return False if False in ( From1, To1 ) else ( From1, To1 )

def is_edit_component(Edit):
    if not isinstance(Edit, ( list, tuple ) ) or not len(Edit) == 2 or not isinstance(Edit[0], ( str )) or not isinstance(Edit[0], ( str )):
        lara_utils.print_and_flush(f'*** Error: malformed edit component: {Edit}')
        return False
    if len(Edit[0].split('|')) != len(Edit[1].split('|')):
        return False
    else:
        return True

def internalise_lexicon_edit_component(EditComponent):
    ( Graph, Phon ) = EditComponent
    return list(zip(Graph.split('|'), Phon.split('|')))
    

def apply_lexicon_edits(Entry, InternalisedEdits):
    if not isinstance(Entry, ( list, tuple ) ) or not len(Entry) == 2 or not isinstance(Entry[0], ( str )) or not isinstance(Entry[0], ( str )):
        lara_utils.print_and_flush(f'*** Error: malformed lexicon entry: {Entry}')
        return False
    ( Graph, Phon ) = Entry
    ComponentPairs = list(zip( Graph.split('|'), Phon.split('|') ))
    for ( From, To ) in InternalisedEdits:
        ComponentPairs = apply_lexicon_edit(ComponentPairs, From, To)
    # zip(*X) is the inverse of zip (cf https://stackoverflow.com/questions/19339/transpose-unzip-function-inverse-of-zip)
    ( GraphComponents1, PhonComponents1 ) = list(zip(*ComponentPairs))
    return [ '|'.join(GraphComponents1), '|'.join(PhonComponents1) ]

##    [
##        "a|d|m|i|r|es",
##        "a|d|m|i|ʁ|"
##    ]

def apply_lexicon_edit(ComponentPairs, From, To):
    if len(ComponentPairs) == 0:
        return []
    elif component_pairs_start_with(ComponentPairs, From):
        return list(To) + apply_lexicon_edit(ComponentPairs[len(From):], From, To)
    else:
        return ComponentPairs[:1] + apply_lexicon_edit(ComponentPairs[1:], From, To)

def component_pairs_start_with(ComponentPairs, From):
    if len(From) == 0:
        return True
    elif len(ComponentPairs) == 0:
        return False
    elif ComponentPairs[0][0] == From[0][0] and ComponentPairs[0][1] == From[0][1]:
        return component_pairs_start_with(ComponentPairs[1:], From[1:])
    else:
        return False

#-------------------------

def evaluate_aligned_lexicon(EditedLexicon, RawLexicon):
    lara_utils.print_and_flush(f'Comparing {EditedLexicon} (edited) against {RawLexicon} (unedited)')
    lara_utils.print_and_flush(f'------------------------------')
    lara_utils.print_and_flush(f'ALL WORDS')
    evaluate_aligned_lexicon1(EditedLexicon, RawLexicon, [])
    lara_utils.print_and_flush(f'------------------------------')
    lara_utils.print_and_flush(f'EXCLUDE HOMONYMS')
    evaluate_aligned_lexicon1(EditedLexicon, RawLexicon, ['homonyms'])
    lara_utils.print_and_flush(f'------------------------------')
    lara_utils.print_and_flush(f'EXCLUDE WORDS NOT IN PRONUNCIATION LEXICON')
    evaluate_aligned_lexicon1(EditedLexicon, RawLexicon, ['unknown_words'])

def evaluate_aligned_lexicon1(EditedLexicon, RawLexicon, OmitList):
    EditedDict = read_aligned_lexicon_for_eval(EditedLexicon)
    RawDict = read_aligned_lexicon_for_eval(RawLexicon)
    if EditedDict == False or RawDict == False:
        return
    ( NWords, NChars, NWordsGood, NCharsGood ) = ( 0, 0, 0, 0 )
    for EditedWord in EditedDict:
        RawWord = lara_parse_utils.remove_disambiguation_annotation_from_word(EditedWord)
        if not RawWord in RawDict:
            lara_utils.print_and_flush(f'*** Error: "{EditedWord}" in edited file, but "{RawWord}" not in raw file')
            return
        elif 'homonyms' in OmitList and RawWord != EditedWord:
            lara_utils.print_and_flush(f'--- Ignoring "{EditedWord}" (homonym)')
        else:
            ( RawAlignedGraph, RawAlignedPhon ) = RawDict[RawWord]
            ( EditedAlignedGraph, EditedAlignedPhon ) = EditedDict[EditedWord]
            if 'unknown_words' in OmitList and not '|' in RawAlignedGraph and '|' in EditedAlignedGraph:
                lara_utils.print_and_flush(f'--- Ignoring "{EditedWord}" ("{RawWord}" missing from phonetic lexicon)')
            else:
                NWords += 1
                NChars += len(RawWord)
                if RawAlignedGraph == EditedAlignedGraph and RawAlignedPhon == EditedAlignedPhon:
                    NWordsGood += 1
                    NCharsGood += len(RawWord)
                else:
                    CharsGood = count_correct_aligned_chars(RawAlignedGraph, RawAlignedPhon, EditedAlignedGraph, EditedAlignedPhon)
                    if CharsGood == 'raw_edited_mismatch':
                        lara_utils.print_and_flush(f'*** Error: mismatch between "{RawDict[RawWord]}" and "{EditedDict[EditedWord]}"')
                        return
                    if CharsGood == 'raw_mismatch':
                        lara_utils.print_and_flush(f'*** Error: mismatch between "{RawAlignedGraph}" and "{RawAlignedPhon}" (unedited)')
                        return
                    if CharsGood == 'edited_mismatch':
                        lara_utils.print_and_flush(f'*** Error: mismatch between "{EditedAlignedGraph}" and "{EditedAlignedPhon} (edited)"')
                        return
                    NCharsGood += CharsGood
    print_evaluate_aligned_lexicon(NWords, NChars, NWordsGood, NCharsGood)
                
def read_aligned_lexicon_for_eval(Lexicon):
    return lara_utils.read_json_file(Lexicon)

def count_correct_aligned_chars(RawAlignedGraph, RawAlignedPhon, EditedAlignedGraph, EditedAlignedPhon):
    ( RawAlignedGraphLetters, EditedAlignedGraphLetters ) = ( RawAlignedGraph.replace('|', ''), EditedAlignedGraph.replace('|', '') )
    if RawAlignedGraphLetters != EditedAlignedGraphLetters:
        return 'raw_edited_mismatch'
    ( RawAlignedGraphComponents, RawAlignedPhonComponents ) = ( RawAlignedGraph.split('|'), RawAlignedPhon.split('|') )
    if len(RawAlignedGraphComponents) != len(RawAlignedPhonComponents):
        return 'raw_mismatch'
    ( EditedAlignedGraphComponents, EditedAlignedPhonComponents ) = ( EditedAlignedGraph.split('|'), EditedAlignedPhon.split('|') )
    if len(EditedAlignedGraphComponents) != len(EditedAlignedPhonComponents):
        return 'edited_mismatch'
    AlignmentsForCharsRaw = alignments_for_chars(RawAlignedGraphComponents, RawAlignedPhonComponents)
    AlignmentsForCharsEdited = alignments_for_chars(EditedAlignedGraphComponents, EditedAlignedPhonComponents)
    return count_correct_aligned_chars1(AlignmentsForCharsRaw, AlignmentsForCharsEdited)

def alignments_for_chars(AlignedGraphComponents, AlignedPhonComponents):
    Pairs = zip(AlignedGraphComponents, AlignedPhonComponents)
    return [ Pair for Pair in Pairs for Char in Pair[0] ]

def count_correct_aligned_chars1(AlignmentsForCharsRaw, AlignmentsForCharsEdited):
    PairsOfPairs = zip(AlignmentsForCharsRaw, AlignmentsForCharsEdited)
    return len([ PairOfPairs for PairOfPairs in PairsOfPairs if PairOfPairs[0] == PairOfPairs[1] ])

def print_evaluate_aligned_lexicon(NWords, NChars, NWordsGood, NCharsGood):
    WordsGoodPercentage = 100.0 * NWordsGood / NWords
    CharsGoodPercentage = 100.0 * NCharsGood / NChars
    lara_utils.print_and_flush(f'Words correctly aligned: {NWordsGood}/{NWords} = {WordsGoodPercentage:.1f}%')
    lara_utils.print_and_flush(f'Chars correctly aligned: {NCharsGood}/{NChars} = {CharsGoodPercentage:.1f}%')


