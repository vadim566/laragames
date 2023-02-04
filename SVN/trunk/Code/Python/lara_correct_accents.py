
import lara_config
import lara_split_and_clean
import lara_picturebook
import lara_parse_utils
import lara_utils

def test(Id):
    if Id == 'pitjanjatjara':
        ConfigFile = '$LARA/Content/pitjantjatjara_course/corpus/local_config.json'
        try_to_correct_accents(ConfigFile)
    if Id == 'pitjanjatjara_full':
        ConfigFile = '$LARA/Content/pitjantjatjara_course/corpus/local_config.json'
        try_to_correct_accents_and_hashtags(ConfigFile)
    else:
        lara_utils.print_and_flush(f'*** Error: unknown ID "{Id}"')

def try_to_correct_accents(ConfigFile):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if Params == False:
        return
    CorpusFile = Params.corpus
    CorrectedFile = corrected_accents_file(CorpusFile)
    PageOrientedSplitList = lara_split_and_clean.read_split_file('', Params)
    AccentsCorrectionDict = make_accents_correction_dict(PageOrientedSplitList)
    correct_accents(PageOrientedSplitList, AccentsCorrectionDict)
    page_oriented_split_list_to_text_file(PageOrientedSplitList, CorrectedFile)

def try_to_correct_accents_and_hashtags(ConfigFile):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if Params == False:
        return
    CorpusFile = Params.corpus
    CorrectedFile = corrected_accents_and_hashtags_file(CorpusFile)
    PageOrientedSplitList = lara_split_and_clean.read_split_file('', Params)
    AccentsCorrectionDict = make_accents_correction_dict(PageOrientedSplitList)
    LemmaCorrectionDict = make_lemma_correction_dict(PageOrientedSplitList)
    correct_accents_and_lemmas(PageOrientedSplitList, AccentsCorrectionDict, LemmaCorrectionDict)
    page_oriented_split_list_to_text_file(PageOrientedSplitList, CorrectedFile)

def corrected_accents_file(CorpusFile):
    ( Base, Extension ) = lara_utils.file_to_base_file_and_extension(CorpusFile)
    return f'{Base}_corrected_accents.{Extension}'

def corrected_accents_and_hashtags_file(CorpusFile):
    ( Base, Extension ) = lara_utils.file_to_base_file_and_extension(CorpusFile)
    return f'{Base}_corrected_accents_and_hashtags.{Extension}'

def make_accents_correction_dict(PageOrientedSplitList):
    ( WordsDict, NonAccentedToAccentedDict ) = ( {}, {} )
    for ( PageInfo, Segments ) in PageOrientedSplitList:
        for Segment in Segments:
            update_accent_dicts_for_segment(Segment, WordsDict, NonAccentedToAccentedDict)
    KeysToDelete = []
    for NonAccentedWord in NonAccentedToAccentedDict:
        AccentedWords = NonAccentedToAccentedDict[NonAccentedWord]
        # Delete non unique mappings
        if len(AccentedWords) != 1:
            lara_utils.print_and_flush(f'*** Warning: several accented words match "{NonAccentedWord}": {AccentedWords}')
            KeysToDelete += [ NonAccentedWord ]
        # Delete irrelevant mappings
        elif not NonAccentedWord in WordsDict:
            KeysToDelete += [ NonAccentedWord ]
        else:
            NonAccentedToAccentedDict[NonAccentedWord] = AccentedWords[0]
    for Key in KeysToDelete:
        del NonAccentedToAccentedDict[Key]
    lara_utils.print_and_flush(f'--- Found {len(NonAccentedToAccentedDict)} non-accented words mapping to accented words')
    lara_utils.print_and_flush(f'--- {list(NonAccentedToAccentedDict.items())}')
    return NonAccentedToAccentedDict

def make_lemma_correction_dict(PageOrientedSplitList):
    ( WordsDict, WordToLemmaDict ) = ( {}, {} )
    for ( PageInfo, Segments ) in PageOrientedSplitList:
        for Segment in Segments:
            update_lemma_dicts_for_segment(Segment, WordsDict, WordToLemmaDict)
    KeysToDelete = []
    for Word in WordToLemmaDict:
        Lemmas = WordToLemmaDict[Word]
        # Delete non unique mappings
        if len(Lemmas) != 1:
            lara_utils.print_and_flush(f'*** Warning: several lemmas for "{Word}": {Lemmas}')
            KeysToDelete += [ Word ]
        # Delete irrelevant mappings
        elif not Word in WordsDict:
            KeysToDelete += [ Word ]
        else:
            WordToLemmaDict[Word] = Lemmas[0]
    for Key in KeysToDelete:
        del WordToLemmaDict[Key]
    lara_utils.print_and_flush(f'--- Found {len(WordToLemmaDict)} words mapping to non-trivial lemmas')
    lara_utils.print_and_flush(f'--- {list(WordToLemmaDict.items())}')
    return WordToLemmaDict

def update_accent_dicts_for_segment(Segment, WordsDict, NonAccentedToAccentedDict):
    if lara_picturebook.is_annotated_image_segment(Segment):
        InnerSegments = lara_picturebook.annotated_image_segments(Segment)
        for Segment1 in InnerSegments:
            update_dicts_for_segment(Segment1, WordsDict, NonAccentedToAccentedDict)
    else:
        Pairs = Segment[2]
        for ( Surface0, Lemma ) in Pairs:
            if Lemma != '':
                Surface = make_surface_word_canonical(Surface0)
                WordsDict[Surface] = True
                SurfaceNoAccents = remove_accents_from_string(Surface)
                if SurfaceNoAccents != Surface:
                    Current = NonAccentedToAccentedDict[SurfaceNoAccents] if SurfaceNoAccents in NonAccentedToAccentedDict else []
                    if not Surface in Current:
                        New = Current + [ Surface ]
                        NonAccentedToAccentedDict[SurfaceNoAccents] = New

def update_lemma_dicts_for_segment(Segment, WordsDict, WordToLemmaDict):
    if lara_picturebook.is_annotated_image_segment(Segment):
        InnerSegments = lara_picturebook.annotated_image_segments(Segment)
        for Segment1 in InnerSegments:
            update_lemma_dicts_for_segment(Segment1, WordsDict, NonAccentedToAccentedDict)
    else:
        Pairs = Segment[2]
        for ( Surface0, Lemma ) in Pairs:
            if Lemma != '':
                Surface = make_surface_word_canonical(Surface0)
                WordsDict[Surface] = True
                if Lemma != Surface:
                    Current = WordToLemmaDict[Surface] if Surface in WordToLemmaDict else []
                    if not Lemma in Current:
                        New = Current + [ Lemma ]
                        WordToLemmaDict[Surface] = New
                            
# Use unidecode package (needs to be installed)
def remove_accents_from_string(Str):
    import unidecode
    return unidecode.unidecode(Str).replace('ː', ':')                     

def correct_accents(PageOrientedSplitList, AccentsCorrectionDict):
    for ( PageInfo, Segments ) in PageOrientedSplitList:
        for Segment in Segments:
            correct_accents_for_segment(Segment, AccentsCorrectionDict)

def correct_accents_and_lemmas(PageOrientedSplitList, AccentsCorrectionDict, LemmaCorrectionDict):
    for ( PageInfo, Segments ) in PageOrientedSplitList:
        for Segment in Segments:
            correct_accents_and_lemmas_for_segment(Segment, AccentsCorrectionDict, LemmaCorrectionDict)

def correct_accents_for_segment(Segment, AccentsCorrectionDict):
    if lara_picturebook.is_annotated_image_segment(Segment):
        InnerSegments = lara_picturebook.annotated_image_segments(Segment)
        for Segment1 in InnerSegments:
            correct_accents_for_segment(Segment1, AccentsCorrectionDict)
    else:
        Pairs = Segment[2]
        for ( Surface0, Lemma ) in Pairs:
            Surface = make_surface_word_canonical(Surface)
            if Lemma != '' and Surface in AccentsCorrectionDict:
                AccentedSurface = AccentsCorrectionDict[Surface]
                Pair[0] = transfer_casing(Surface0, Surface, AccentedSurface)
            if Lemma in AccentsCorrectionDict:
                Pair[1] = AccentsCorrectionDict[Lemma]

def correct_accents_and_lemmas_for_segment(Segment, AccentsCorrectionDict, LemmaCorrectionDict):
    if lara_picturebook.is_annotated_image_segment(Segment):
        InnerSegments = lara_picturebook.annotated_image_segments(Segment)
        for Segment1 in InnerSegments:
            correct_accents_and_lemmas_for_segment(Segment1, AccentsCorrectionDict, LemmaCorrectionDict)
    else:
        Pairs = Segment[2]
        for Pair in Pairs:
            ( Surface0, Lemma ) = Pair
            Surface = make_surface_word_canonical(Surface0)
            if Lemma != '' and Surface in AccentsCorrectionDict:
                AccentedSurface = AccentsCorrectionDict[Surface]
                Pair[0] = transfer_casing(Surface0, Surface, AccentedSurface)
            if Lemma in AccentsCorrectionDict:
                Pair[1] = AccentsCorrectionDict[Lemma]
            if Pair[1] in LemmaCorrectionDict:
                Pair[1] = LemmaCorrectionDict[Pair[1]]

def transfer_casing(OriginalSurface, NormalisedSurface, AccentedSurface):
    if OriginalSurface == NormalisedSurface.capitalize():
        return AccentedSurface.capitalize()
    elif OriginalSurface == NormalisedSurface.upper():
        return AccentedSurface.upper()
    else:
        return AccentedSurface

def page_oriented_split_list_to_text_file(PageOrientedSplitList, File):
    Out = ''
    for ( PairInfo, Segments ) in PageOrientedSplitList:
        Out += '<page>'
        for Segment in Segments:
            if lara_picturebook.is_annotated_image_segment(Segment):
                InnerSegments = lara_picturebook.annotated_image_segments(Segment)
                Body = '||'.join([ normal_segment_to_string(Segment1) for Segment1 in InnerSegments ])
                Out += f'<annotated_image>{Body}</annotated_image>'
            else:
                Body = normal_segment_to_string(Segment)
                Out += f'{Body}||'
    lara_utils.write_lara_text_file(Out, File)

def normal_segment_to_string(Segment):
    ( Pairs, Out, PreviousSegmentType ) = ( Segment[2], '', False )
    for ( Surface, Lemma ) in Pairs:
        if Lemma == '':
            # If we include / or - as a filler, they need to be enclosed in | ... | otherwise they can be read as part of a word.
            Surface1 = f'|{Surface}|' if Surface in ( '/', '-' ) else Surface
            Out += Surface1
            PreviousSegmentType = 'filler'
        else:
            Body = content_pair_to_string(Surface, Lemma)
            if PreviousSegmentType == 'content':
                Out += '|'
            Out += Body
            PreviousSegmentType = 'content'
    return Out

def content_pair_to_string(Surface, Lemma):
    Surface1 = Surface if not string_contains_space_or_punctuation_char(Surface) else f'@{Surface}@'
    if make_surface_word_canonical(Surface) != Lemma or string_starts_or_end_with_punctuation_char(Surface):
        return f'{Surface1}#{Lemma}#'
    else:
        return Surface1 

def string_contains_space_or_punctuation_char(Str):
    for I in range(0, len(Str)):
        Char = Str[I]
        if Char.isspace() or lara_parse_utils.is_punctuation_char(Char):
            return True
    return False

def string_starts_or_end_with_punctuation_char(Str):
    if len(Str) == 0:
        return False
    if lara_parse_utils.is_punctuation_char(Str[0]) or lara_parse_utils.is_punctuation_char(Str[-1]):
        return True
    return False

def make_surface_word_canonical(Surface):
    return Surface.lower()
