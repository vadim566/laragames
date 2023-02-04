
import lara_partitioned_text_files
import lara_split_and_clean
import lara_config
import lara_utils
from translate.storage.tmx import tmxfile

def test(Id):
    if Id == 'combray_ch1':
        TMXFile = '$LARA/Content/combray/translations/combray_ch1_FRA-ENG_BT.tmx'
        SourceLang = 'fr'
        TargetLang = 'en'
        JSONFile = '$LARA/Content/combray/translations/combray_ch1_FRA-ENG_BT.json'
        convert_tmx_to_json(TMXFile, SourceLang, TargetLang, JSONFile)
    elif Id == 'split_un_amour_de_swann':
        ConfigFile = '$LARA/Content/un_amour_de_swann/corpus/local_config.json'
        TMXFile = '$LARA/Content/un_amour_de_swann/translations/un_amour_de_swann_all_FRA-ENG_BT.tmx'
        SourceLang = 'fr'
        TargetLang = 'en'
        split_tmx_file_to_match_source_file(ConfigFile, TMXFile, SourceLang, TargetLang)
    elif Id == 'split_jeunes_filles':
        ConfigFile = '$LARA/Content/a_l_ombre_des_jeunes_filles/corpus/local_config.json'
        TMXFile = '$LARA/Content/a_l_ombre_des_jeunes_filles/translations/a_l_ombre_des_jeunes_filles_FRA-ENG_BT.tmx'
        SourceLang = 'fr'
        TargetLang = 'en'
        split_tmx_file_to_match_source_file(ConfigFile, TMXFile, SourceLang, TargetLang)
    else:
        lara_utils.print_and_flush(f'*** Error: unknown Id: {Id}')


def convert_tmx_to_json(TMXFile, SourceLang, TargetLang, JSONFile):
    Out = []
    try:
        with open(lara_utils.absolute_file_name(TMXFile), 'rb') as f:
            tmx_file = tmxfile(f, SourceLang, TargetLang)
            for node in tmx_file.unit_iter():
                Out += [ { 'source': node.source,
                           'target': node.target } ]
            # First unit gives the names of the files
            Out1 = Out[1:]
            lara_utils.write_json_to_file_plain_utf8(Out1, JSONFile)
            lara_utils.print_and_flush(f'--- Converted {TMXFile} to JSON ({len(Out1)} units)')
    except Exception as e:
        lara_utils.print_and_flush(f'*** Warning: unable to convert TMX file {TMXFile} to JSON')
        lara_utils.print_and_flush(str(e))

def split_tmx_file_to_match_source_file(ConfigFile, TMXFile, SourceLang, TargetLang):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if Params == False:
        return
    SourceFile = Params.source_file
    if SourceFile == '':
        lara_utils.print_and_flush(f'*** Error: "source_file" is not defined')
        return
    ParsedSourceFile = lara_partitioned_text_files.parse_partitioned_text_file(SourceFile)
    if ParsedSourceFile == False:
        return
    TmpJSONFile = lara_utils.get_tmp_json_file(Params)
    convert_tmx_to_json(TMXFile, SourceLang, TargetLang, TmpJSONFile)
    TMXContent = lara_utils.read_json_file(TmpJSONFile)
    BreakIndicesAndLabels = match_parsed_source_file_to_tmx_content(ParsedSourceFile, TMXContent)
    split_tmx_content(BreakIndicesAndLabels, TMXContent, TMXFile)

def match_parsed_source_file_to_tmx_content(ParsedSourceFile, TMXContent):
    ( Index, LastIndex, Out ) = ( 0, len(TMXContent), [] )
    NormalisedTMXContent = normalise_tmx_content(TMXContent)
    for ( Label, Text ) in ParsedSourceFile:
        NormalisedText = normalise_text(Text)
        BreakIndex = match_text_to_tmx_content(NormalisedText, NormalisedTMXContent, Index, LastIndex)
        if BreakIndex == 'no_match':
           lara_utils.print_and_flush(f'*** Error: unable to match partition "{Label}" to TMX content')
           return 
        Out += [ { 'label': Label, 'index': BreakIndex } ]
        Index = BreakIndex + 1
    return Out

def match_text_to_tmx_content(NormalisedText, NormalisedTMXContent, Index, LastIndex):
    for Index in range(Index, LastIndex):
        NormalisedTMXSource = NormalisedTMXContent[Index]['source']
        if match_normalised_text(NormalisedText, NormalisedTMXSource):
            return Index
    return 'no_match'

def match_normalised_text(NormalisedText, NormalisedTMXSource):
    LengthToMatch = min([len(NormalisedText), len(NormalisedTMXSource), 10])
    return NormalisedText[:LengthToMatch] == NormalisedTMXSource[:LengthToMatch]

def normalise_tmx_content(TMXContent):
    return [ { 'source':normalise_text(Item['source']), 'target':Item['target'] }
             for Item in TMXContent ]

def normalise_text(Str):
    Pairs = lara_split_and_clean.string_to_annotated_words(Str)[0]
    return [ Pair[0] for Pair in Pairs if Pair[1] != '' ]

def split_tmx_content(BreakIndicesAndLabels, TMXContent, TMXFile):
    LastBreakIndicesAndLabelsIndex = len(BreakIndicesAndLabels) - 1
    LastTMXIndex = len(TMXContent) - 1
    for I in range(0, LastBreakIndicesAndLabelsIndex + 1):
        Item = BreakIndicesAndLabels[I]
        ( Label, LowerIndex ) = ( Item['label'], Item['index'] )
        UpperIndex = LastTMXIndex if I == LastBreakIndicesAndLabelsIndex else BreakIndicesAndLabels[I+1]['index']
        SelectedTMXContent = TMXContent[LowerIndex:UpperIndex]
        File = make_split_tmx_file_name(TMXFile, Label)
        lara_utils.write_json_to_file_plain_utf8(SelectedTMXContent, File)

def make_split_tmx_file_name(TMXFile, Label):
    ( Base, Ext ) = lara_utils.file_to_base_file_and_extension(TMXFile)
    return f'{Base}_{Label}.json'

         
