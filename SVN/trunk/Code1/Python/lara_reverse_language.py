
import lara_top
import lara_config
import lara_split_and_clean
import lara_transform_tagged_file
import lara_translations
import lara_parse_utils
import lara_utils

def test_reverse_language(Id):
    if Id == 'antigone':
        ConfigFile = '$LARA/Content/antigone/corpus/local_config.json'
        CorpusFileNew = '$LARA/Content/antigone_en/corpus/Segmented_Antigone_en.docx'
        SegmentTranslationFileNew = '$LARA/Content/antigone_en/translations/english_french.csv'
    else:
        lara_utils.print_and_flush(f'*** Error: unknown ID {Id}')
        return False
    reverse_language(ConfigFile, CorpusFileNew, SegmentTranslationFileNew)

def reverse_language_from_config_file(ConfigFile):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if not Params:
        return False
    if not Params.reversed_corpus_file or not Params.reversed_segment_translation_file:
        lara_utils.print_and_flush('*** Error: "reversed_corpus_file" and "reversed_segment_translation_file" must be defined')
    return reverse_language(ConfigFile, Params.reversed_corpus_file, Params.reversed_segment_translation_file)

def reverse_language(ConfigFile, CorpusFileNew, SegmentTranslationFileNew):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if not Params:
        return False
    return reverse_language1(Params, CorpusFileNew, SegmentTranslationFileNew)

def reverse_language1(Params, CorpusFileNew, SegmentTranslationFileNew):
    SegmentTranslationFile = Params.segment_translation_spreadsheet
    if SegmentTranslationFile == '':
        lara_utils.print_and_flush('*** Error: no segment translation file')
        return False
    else:
        SegmentTranslations = lara_utils.read_lara_csv(SegmentTranslationFile)[1:]
        SegmentTranslationsDict = { Line[0]: Line[1] for Line in SegmentTranslations }
        ReverseSegmentTranslations = [ [ Line[1], Line[0] ] for Line in SegmentTranslations ]                       
    lara_top.compile_lara_local_clean(Params)
    SplitFile = lara_top.lara_tmp_file('split', Params)
    PageOrientedSplitList = lara_split_and_clean.read_split_file(SplitFile, Params)
    PageOrientedSplitList1 = reverse_page_oriented_split_list(PageOrientedSplitList, SegmentTranslationsDict)
    lara_transform_tagged_file.split_file_content_to_text_file(PageOrientedSplitList1, CorpusFileNew)
    Header = ['Segment', 'Translation']
    lara_translations.write_translation_csv(Header, ReverseSegmentTranslations, SegmentTranslationFileNew)
    return True

def reverse_page_oriented_split_list(PageOrientedSplitList, Dict):
    return [ ( PageInfo, reverse_chunk_list(Chunks, Dict) ) for ( PageInfo, Chunks ) in PageOrientedSplitList ]

def reverse_chunk_list(Chunks, Dict):
    return [ reverse_chunk(Chunk, Dict) for Chunk in Chunks ]

def reverse_chunk(Chunk, Dict):
    ( Raw, Clean, Pairs, Tag ) = Chunk
    RawNoTags = clean_raw_lara_text(Raw)
    if Clean == '':
        return ( Raw, Clean, Pairs, Tag )
    if not Clean in Dict:
        lara_utils.print_and_flush(f'*** Warning: no translation for "{Clean}"')
        return ( RawNoTags, Clean, Pairs, Tag )
    Translation = Dict[Clean]
    if RawNoTags.find(Clean) < 0:
        RawNoTags = lara_parse_utils.replace_nonbreaking_spaces_with_spaces_in_string(RawNoTags)
        Clean = lara_parse_utils.replace_nonbreaking_spaces_with_spaces_in_string(Clean)
        Translation = lara_parse_utils.replace_nonbreaking_spaces_with_spaces_in_string(Translation)
        # Common problem is that we have a final punctuation mark broken by HTML formatting, try to fix
        if lara_parse_utils.is_punctuation_char(Clean[-1]):
            Clean1 = Clean[:-1]
            Translation1 = Translation[:-1] if lara_parse_utils.is_punctuation_char(Translation[-1]) else Translation
        else:
            ( Clean1, Translation1 ) = ( Clean, Translation )
        if RawNoTags.find(Clean1) < 0:
            lara_utils.print_and_flush(f'*** Warning: unable to find "{Clean1}" in "{RawNoTags}"')
            Raw1 = f'<b>(Warning: probably missing formatting)</b> {Translation}'
        else:
            Raw1 = RawNoTags.replace(Clean1, Translation1)
    else:
        Raw1 = RawNoTags.replace(Clean, Translation)
    return ( Raw1, Clean, Pairs, Tag )

def clean_raw_lara_text(Raw):
    return lara_parse_utils.remove_hashtag_annotations_from_string(Raw).replace('|', '')

