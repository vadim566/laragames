
import lara_utils
import lara_parse_utils

stored_downloaded_image_urls = {}

def init_stored_downloaded_image_metadata():
    global stored_downloaded_image_urls
    stored_downloaded_image_urls = {}

def store_downloaded_image_url(FileName, FullURL, CorpusId):
    global stored_downloaded_image_urls
    if not FileName:
        return False
    if CorpusId in stored_downloaded_image_urls:
        SubDict = stored_downloaded_image_urls[CorpusId]
    else:
        SubDict = {}
    SubDict[FileName] = FullURL
    stored_downloaded_image_urls[CorpusId] = SubDict
    return True

def get_downloaded_image_url(FileName, CorpusId):
    global stored_downloaded_image_urls
    if CorpusId in stored_downloaded_image_urls:
        SubDict = stored_downloaded_image_urls[CorpusId]
        if FileName in SubDict:
            return SubDict[FileName]
        else:
            lara_utils.prettyprint(['failed', 'get_downloaded_image_url', FileName, CorpusId, stored_downloaded_image_urls])
            return False
    else:
        return False

def store_downloaded_image_metadata(CorpusId, URL, File):
    if not File:
        return True
    if lara_utils.file_exists(File):
        List = lara_utils.read_unicode_text_file_to_lines(File)
        lara_utils.print_and_flush(f'--- Read image metadata file ({len(List)} lines) {File}')
        for Line in List:
            store_downloaded_image_metadata_line(Line, CorpusId, URL)
        lara_utils.print_and_flush(f'Stored {len(List)} image URLs')
    else:
        lara_utils.print_and_flush(f'*** Error: image metadata file {File} not found')
        return False

def store_downloaded_image_metadata_line(Line, CorpusId, URL):
    Components = Line.split()
    if len(Components) == 1:
        FileName = Components[0]
        FullURL = f'{URL}/{FileName}'
        store_downloaded_image_url(FileName, FullURL, CorpusId)
    elif len(Components) > 1:
        lara_utils.print_and_flush(f'*** Warning: unknown line "{Line}" in image metadata file for "{CorpusId}"')

# ------------------------------------------------------

def process_image_directory(Params):
    if Params.image_directory != '' and lara_utils.directory_exists(Params.image_directory):
        ImageDir = lara_utils.absolute_file_name(Params.image_directory)
        MultimediaDir = lara_utils.get_multimedia_dir_from_params(Params)
        copy_image_directory(ImageDir, MultimediaDir, Params)
    else:
        lara_utils.print_and_flush('--- No image directory defined, skipping image file processing')

def copy_image_directory(ImageDir, MultimediaDir, Params):
    if Params.abstract_html in ( 'abstract_html_only', 'plain_via_abstract_html' ):
        lara_utils.print_and_flush(f'--- Producing abstract HTML only, not copying image files')
        return
    if lara_utils.directory_exists(ImageDir):
        Command = f'cp -r {ImageDir}/* {MultimediaDir}'
        lara_utils.print_and_flush('--- Copying image files')
        Code = lara_utils.execute_lara_os_call(Command, Params)
        if Code == 0:
            lara_utils.print_and_flush('--- done')
        else:
            lara_utils.print_and_flush(f'*** Warning: Copying of whole directory failed, trying to copy files one at a time')
            lara_utils.copy_directory_one_file_at_a_time(ImageDir, MultimediaDir, 'all')

def process_img_tags_in_string(RawStr, Params):
    #if lara_utils.no_corpus_id_in_params(Params):
    #    return ( RawStr, [] )
    if Params.local_files == 'yes' and Params.image_directory == '':
        return ( RawStr, [] )
    if Params.local_files == 'yes' and Params.image_directory != '':
        Dir = lara_utils.absolute_file_name(Params.image_directory)
    else:
        #lara_utils.print_and_flush(f'Params.local_files == "{Params.local_files}" and Params.image_directory = "{Params.image_directory}"')
        Dir = '*no_dir*'
    return process_img_tags_in_string1(RawStr, Params, Dir)

def process_img_tags_in_css_or_script_file(FileIn, FileOut, Params):
    StrIn = lara_utils.read_lara_text_file(FileIn)
    if not StrIn:
        lara_utils.print_and_flush(f'*** Error: unable to convert image tags in {FileIn}')
        return False
    ( StrOut, Errors ) = process_img_tags_in_css_or_script_string(StrIn, Params)
    if Errors != []:
        lara_utils.print_and_flush('\n'.join(Errors))
        return False
    lara_utils.write_lara_text_file(StrOut, FileOut)
    return StrOut

def process_img_tags_in_css_or_script_string(RawStr, Params):
    #if lara_utils.no_corpus_id_in_params(Params):
    #    return ( RawStr, [] )
    if Params.local_files == 'yes' and Params.image_directory == '':
        return ( RawStr, [] )
    if Params.local_files == 'yes' and Params.image_directory != '':
        Dir = lara_utils.absolute_file_name(Params.image_directory)
    else:
        Dir = '*no_dir*'
    return process_img_tags_in_css_or_script_string1(RawStr, Params, Dir)

def img_files_referenced_in_string(Str):
    img_tag_starts = ( ('img', '<img'), ('video', '<video') )
    img_tag_end = '/>'
    ( Index, N, ImgFiles ) = ( 0, len(Str), [] )
    while True:
        if Index >= N:
            return ImgFiles
        FoundImgFile = False
        for ( ImgTagType, img_tag_start ) in img_tag_starts:
            if not FoundImgFile and lara_parse_utils.substring_found_at_index(Str, Index, img_tag_start) > 0:
                EndOfTagIndex = Str.find(img_tag_end, Index+len(img_tag_start))
                if EndOfTagIndex > 0:
                    ( Components, Errors ) = parse_img_tag_body(Str[Index+len(img_tag_start):EndOfTagIndex], ImgTagType)
                    Index = EndOfTagIndex + len(img_tag_end)
                    if 'src' in Components:
                        FoundImgFile = True
                        ImgFiles += [ Components['src'] ]
                else:
                    # We have an open img tag, but try to carry on anyway
                    return ImgFiles
        if not FoundImgFile:
            Index += 1

def process_img_tags_in_string1(Str, Params, Dir):
    if Str.find('<') < 0:
        return ( Str, [] )
    img_tag_starts = ( ('img', '<img'), ('video', '<video') )
    img_tag_end = '/>'
    ( Index, N, OutStr, AllErrors ) = ( 0, len(Str), '', [] )
    while True:
        if Index >= N:
            return ( OutStr, AllErrors )
        FoundImgFile = False
        for ( ImgTagType, img_tag_start ) in img_tag_starts:
            if not FoundImgFile and lara_parse_utils.substring_found_at_index(Str, Index, img_tag_start) > 0:
                EndOfTagIndex = Str.find(img_tag_end, Index+len(img_tag_start))
                if EndOfTagIndex > 0:
                    FoundImgFile = True
                    ( ImgTagText1, Errors ) = process_img_tag(Str[Index+len(img_tag_start):EndOfTagIndex], ImgTagType, Params, Dir)
                    OutStr += ImgTagText1
                    Index = EndOfTagIndex + len(img_tag_end)
                    AllErrors += Errors
                else:
                    return ( OutStr, [f'*** Error: open img tag: "{Str[Index:Index+100]}"'] )
        if not FoundImgFile:
            OutStr += Str[Index]
            Index += 1

def process_img_tags_in_css_or_script_string1(Str, Params, Dir):
    img_tag_start = 'lara_image("'
    img_tag_end = '")'
    ( Index, N, OutStr, AllErrors ) = ( 0, len(Str), '', [] )
    while True:
        if Index >= N:
            return ( OutStr, AllErrors )
        if lara_parse_utils.substring_found_at_index(Str, Index, img_tag_start) > 0:
            EndOfTagIndex = Str.find(img_tag_end, Index+len(img_tag_start))
            if EndOfTagIndex > 0:
                ( ImgTagText1, Errors ) = process_css_or_script_img_tag(Str[Index+len(img_tag_start):EndOfTagIndex], Params, Dir)
                OutStr += ImgTagText1
                Index = EndOfTagIndex + len(img_tag_end)
                AllErrors += Errors
            else:
                return ( OutStr, [f'*** Error: open img tag: "{Str[Index:Index+100]}"'] )
        else:
            OutStr += Str[Index]
            Index += 1
        
def process_css_or_script_img_tag(Pathname, Params, Dir):
    if Params.hide_images == 'yes':
        return ( '*no_image_file*', [] )
    else:
        #lara_utils.print_and_flush(f'--- url_for_image({Pathname}, {Params}, {Dir})')
        ( URL, Errors ) = url_for_image(Pathname, Params, Dir)
        return ( f'"{URL}"', Errors )

def process_img_tag(ImgTagText, ImgTagType, Params, Dir):
    ( Components, Errors ) = parse_img_tag_body(ImgTagText, ImgTagType)
    if len(Errors) > 0:
        return ( '', Errors )
    elif Params.hide_images == 'yes':
        if 'alt' in Components:
            AltComponent = Components['alt']
            return ( f'\n<i>[{AltComponent}]</i>\n' )
        else:
            return ( '', [] )
    elif ImgTagType == 'video':
        return process_video_tag1(ImgTagText, Components, Params, Dir)
    else:
        return process_img_tag1(ImgTagText, Components, Params, Dir)

## <video width="320" height="240" controls>
##   <source src="movie.webm" type="video/webm">
## Your browser does not support the video tag.
## </video>

def process_video_tag1(ImgTagText, Components, Params, Dir):
    if 'src' in Components:
        ( URL, Errors ) = url_for_image(Components['src'], Params, Dir)
        Extension = lara_utils.extension_for_file(URL)
        if not Extension in ( 'mp4', 'webm' ):
            return ( '', [ '*** Error: video tag "<video {ImgTagText}/>" is not an mp4 or webm file' ] )
        SourceLine = f'  <source src="{URL}" type="video/{Extension}">'
        StartLine = f'<video '
        if 'width' in Components:
            StartLine += f' width="{Components["width"]}"'
        if 'height' in Components:
            StartLine += f' height="{Components["height"]}"'
        StartLine += ' controls/>'
        ErrorLine = f'Your browser does not support the video tag.'
        EndLine = f'</video>'
        AllLines = [ StartLine, SourceLine, ErrorLine, EndLine ]
        return ( ' '.join(AllLines), [] )
    else:
        return ( '', [ '*** Error: malformed video tag "<video {ImgTagText}/>"' ] )

def process_img_tag1(ImgTagText, Components, Params, Dir):
        if 'src' in Components:
            ( URL, Errors ) = url_for_image(Components['src'], Params, Dir)
            imgtag = f'<img src="{URL}"'
            if 'width' in Components:
                imgtag += f' width="{Components["width"]}"'
            if 'height' in Components:
                imgtag += f' height="{Components["height"]}"'
            imgtag += '/>'
            return ( imgtag, [] )
        else:
            return ( '', [ '*** Error: malformed img tag "<img {ImgTagText}/>"' ] )

def url_for_image(ImageName, Params, Dir):
    CorpusId = lara_utils.get_corpus_id_from_params(Params)
    if CorpusId == 'local_files' or CorpusId == '':
        #URL = f'multimedia/{ImageName}'
        URL = f'{lara_utils.relative_multimedia_dir(Params)}/{ImageName}'
        return ( URL, check_if_img_file_exists(Dir, ImageName) )
    else:
        URL = get_downloaded_image_url(ImageName, CorpusId)
        if URL:
            return ( URL, [] )
        # If we are doing distributed LARA and we can't find the image, create a bad reference
	# to the local multimedia directory and don't interrupt compilation.
        else:
            lara_utils.print_and_flush(f'*** Warning: missing image file "{ImageName}" for "{CorpusId}"')
            return ( f'missing_image/{ImageName}', [] )
                         
def check_if_img_file_exists(Dir, ImageName):
    File = f'{Dir}/{ImageName}'
    if lara_utils.file_exists(File):
        return []
    else:
        Message = f'*** Warning: missing image file "{File}"'
        lara_utils.print_and_flush(Message)
        return [ Message ]

def is_img_tag(Str):
    return ( Str.startswith('<img') or Str.startswith('<video') ) and Str.endswith('/>') 

def img_tag_to_representation(Str):
    if not is_img_tag(Str):
        lara_utils.print_and_flush(f'*** Error: bad call to img_tag_to_representation, "{Str}" is not an img tag')
        return False
##    ( Type, StartIndex ) = ( 'img', len('<img') ) if Str.startswith('<img') else ( 'video', len('<video') )
##    EndIndex = Str.find('/>')
##    Str1 = Str[StartIndex:EndIndex]
    Str1 = img_tag_to_image_tag_body(Str)
    if Str1 == False:
        lara_utils.print_and_flush(f'*** Error: missing closing "/>" in tag "Str"')
        return False
    Type = 'img' if Str.startswith('<img') else 'video'
    ( Representation, Errors ) = parse_img_tag_body(Str1, Type)
    if len(Errors) > 0:
        for Error in Errors:
            lara_utils.print_and_flush(Error)
        return False
    else:
        Representation['multimedia'] = Type
        Representation['file'] = Representation['src']
        del Representation['src']
        return Representation

def img_tag_to_image_tag_body(Str):
    ( Type, StartIndex ) = ( 'img', len('<img') ) if Str.startswith('<img') else ( 'video', len('<video') )
    EndIndex = Str.find('/>')
    if EndIndex >= StartIndex:
        return Str[StartIndex:EndIndex]
    else:
        return False

def parse_img_tag_body(Str, ImgTagType):
    ( Index, N, OutDict ) = ( 0, len(Str), {} )
    while True:
        Index = lara_parse_utils.skip_spaces(Str, Index)
        if Index >= N:
            return ( OutDict, [] )
        else:
            ( Key, Value, Index1, Errors ) = parse_img_tag_component(Str, Index, ImgTagType)
            if len(Errors) > 0:
                return ( OutDict, Errors )
            elif Key:
                OutDict[Key] = Value
                Index = Index1
            elif lara_parse_utils.skip_spaces(Str, Index1) >= N:
                return ( OutDict, [] )
            else:
                return ( OutDict, [ f'*** Error: unknown text in {ImgTagType} tag body: "{Str[Index:]}"' ] )
                

def parse_img_tag_component(Str, Index, ImgTagType):
    for Key in ( 'src', 'alt', 'width', 'height' ):
        if lara_parse_utils.substring_found_at_index(Str, Index, Key + '="'):
            StartOfValueIndex = Index + len(Key) + 2
            EndOfValueIndex = Str.find('"', StartOfValueIndex)
            if EndOfValueIndex >= StartOfValueIndex:
                ValueStr = Str[StartOfValueIndex:EndOfValueIndex]
                if Key in ( 'width', 'height' ):
                    Value = lara_utils.safe_string_to_int(ValueStr)
                    if not Value:
                        return ( False, False, False, [f'*** Error: bad value of "{Key}" in {ImgTagType} tag "<{ImgTagType} {Str}/>"' ] )
                else:
                    Value = ValueStr
                return ( Key, Value, EndOfValueIndex + 1, [] )
            else:
                return ( False, False, False, [f'*** Error: malformed {ImgTagType} tag "<{ImgTagType} {Str}/>"' ] )
    # We didn't find any key/value pair
    return ( False, False, False, [] )
            

