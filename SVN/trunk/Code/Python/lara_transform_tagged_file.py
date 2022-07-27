# Transform a tagged file
#
# Operations currently supported:
# - join_short_segments: make sure that segments are at least Parameter long
# - rescale_images: multiply sizes of images by Parameter

import lara_top
import lara_images
import lara_config
import lara_split_and_clean
import lara_utils

def test(Id):
    if Id == 'animal_farm':
        transform_tagged_file('$LARA/Content/animal_farm/corpus/local_config.json',
                              '$LARA/Content/animal_farm/corpus/TaggedAndCleaned_AnimalFarm_resegmented.docx',
                              'join_short_segments',
                              15)
    if Id == 'genesis':
        transform_tagged_file('$LARA/Content/sample_english/corpus/local_config.json',
                              '$LARA/Content/sample_english/corpus/Tagged_sample_resegmented.txt',
                              'join_short_segments',
                              20)

def transform_tagged_file(ConfigFile, OutFile, Operation, Parameter):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if not Params:
        lara_utils.print_and_flush('*** Error: cannot read config file: {ConfigFile}')
        return False
    try:
        lara_utils.print_and_flush(f'--- Resegmenting {Params.corpus}')
        lara_top.compile_lara_local_clean(Params)
        SplitFile = lara_top.lara_tmp_file('split', Params)
        PageOrientedSplitList = lara_split_and_clean.read_split_file(SplitFile, Params)
        OutStr = transform_split_file_content(PageOrientedSplitList, Operation, Parameter, Params)
        if not OutStr:
            lara_utils.print_and_flush(f'*** Error: when trying to transform LARA tagged file')
            return False
        lara_utils.write_lara_text_file(OutStr, OutFile)
        lara_utils.print_and_flush(f'--- Resegmented {Params.corpus} to {OutFile}')
    except Exception as e:
        lara_utils.print_and_flush(f'*** Error: when trying to transform LARA tagged file')
        lara_utils.print_and_flush(str(e))
        return False

_valid_operations = ( 'join_short_segments', 'rescale_images' )

def valid_operation_and_parameter(Operation, Parameter):
    if not Operation in _valid_operations:
        lara_utils.print_and_flush('*** Error: unknown operation in "{Operation}" in transform_tagged_file')
        return False
    if Operation == 'join_short_segments':
        if not isinstance(Parameter, int) or isinstance(Parameter, bool) or Parameter <= 0:
            lara_utils.print_and_flush('*** Error: bad argument {Parameter} to "{Operation}" in transform_tagged_file')
            return False
    if Operation == 'rescale_images':
        if not isinstance(Parameter, ( int, float )) or isinstance(Parameter, bool) or Parameter <= 0:
            lara_utils.print_and_flush('*** Error: bad argument {Parameter} to "{Operation}" in transform_tagged_file')
            return False
    return True

def transform_split_file_content(PageOrientedSplitList, Operation, Parameter, Params):
    if Operation == 'join_short_segments':
        return join_short_segments_in_split_file_content(PageOrientedSplitList, Parameter, Params)
    if Operation == 'rescale_images':
        return lara_images.rescale_image_tags_in_split_file_content(PageOrientedSplitList, Parameter, Params)

def join_short_segments_in_split_file_content(PageOrientedSplitList, MinLength, Params):
    OutStr = ''
    for ( PageInfo, Chunks ) in PageOrientedSplitList:
        PageStr = page_info_to_page_str(PageInfo)
        if not PageStr:
            return False
        OutStr += f'{PageStr}\n'
        ( CurrentSegment, CurrentLength ) = ( '', 0 )
        for ( Raw, Clean, Pairs, Tag ) in Chunks:
            CurrentSegment += Raw
            CurrentLength += len(Pairs)
            if CurrentLength >= MinLength:
                OutStr += f'{CurrentSegment}||'
                ( CurrentSegment, CurrentLength ) = ( '', 0 )
        if CurrentLength > 0:
            OutStr += f'{CurrentSegment}||'
    return OutStr

def split_file_content_to_text_file_no_separators(PageOrientedSplitList, File):
    return split_file_content_to_text_file1(PageOrientedSplitList, File, '')

def split_file_content_to_text_file(PageOrientedSplitList, File):
    return split_file_content_to_text_file1(PageOrientedSplitList, File, '||')

def split_file_content_to_text_file1(PageOrientedSplitList, File, SeparatorStr):
    OutStr = ''
    for ( PageInfo, Chunks ) in PageOrientedSplitList:
        PageStr = page_info_to_page_str(PageInfo)
        if not PageStr:
            return False
        OutStr += f'{PageStr}'
        for ( Raw, Clean, Pairs, Tag ) in Chunks:
            OutStr += f'{Raw}{SeparatorStr}'
    lara_utils.write_lara_text_file(OutStr, File)

def page_info_to_page_str(PageInfo):
    if not isinstance(PageInfo, dict):
        lara_utils.print_and_flush('*** Error: bad page info {PageInfo}')
        return False
    if 'css_file' in PageInfo:
        CSSFile = PageInfo['css_file']
        return f'<page css_file="{CSSFile}">'
    else:
        return '<page>'

         
    
