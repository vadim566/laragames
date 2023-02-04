
import lara_config
import lara_images
import lara_mwe
import lara_replace_chars
import lara_parse_utils
import lara_utils
import time
import requests

#_picturebook_select_tool_url = 'https://pure-bastion-46301.herokuapp.com/api/books/'
_picturebook_select_tool_url = 'https://lara-picturebooks-backend.herokuapp.com/api/books/'

def test(Id):
    if Id == 1:
        ConfigFile = '$LARA/Content/mary_manuscript/corpus/local_config.json'
        SplitFile = '$LARA/tmp_resources/mary_manuscript_split.json'
        TmpWordLocationFile = '$LARA/tmp_resources/mary_manuscript_tmp_word_locations.json'
        Params = lara_config.read_lara_local_config_file(ConfigFile)
        make_tmp_picturebook_word_location_file(SplitFile, TmpWordLocationFile, Params)
    elif Id == 'resize_poster':
        InFile = '$LARA/Content/ítm_picturebook/corpus/ítm_poster_word_locations.json'
        Factor = 0.67
        OutFile = '$LARA/Content/ítm_picturebook/corpus/ítm_poster_word_locations67.json'
        change_scale_in_locations_file(InFile, Factor, OutFile)

def make_tmp_picturebook_word_location_file_and_word_location_zipfile(SplitFile, TmpWordLocationFile, TmpZipfile, Params):
    ImagesAndWords0 = picturebook_words_images_and_locations(SplitFile, Params)
    ImagesAndWords = restore_reserved_chars_in_images_words_and_locations(ImagesAndWords0)
    write_out_word_location_file(ImagesAndWords, TmpWordLocationFile)
    write_out_word_location_zipfile(ImagesAndWords, TmpWordLocationFile, TmpZipfile, Params)

def maybe_copy_picturebook_data_to_selector_tool_directory(TmpZipfile, Dir, Params):
    if not lara_utils.file_exists(TmpZipfile):
        lara_utils.print_and_flush(f'--- Zipfile {TmpZipfile} does not exist, not copying to SelectorTool directory')
        return
    if not lara_utils.directory_exists(Dir):
        lara_utils.create_directory(Dir)
        lara_utils.print_and_flush(f'--- Selector tool directory {Dir} not found, creating')
    copy_picturebook_data_to_selector_tool_directory(TmpZipfile, Dir, Params)

def picturebook_words_images_and_locations(SplitFile, Params):
    #if Params.picturebook == 'no' or Params.picturebook_word_locations_file == '':
    #if Params.picturebook_word_locations_file == '':
    #    return {}
    ImagesWordsAndLocations = read_picturebook_word_locations_file(Params)
    if ImagesWordsAndLocations == False:
        return False
    PageOrientedSplitList = lara_mwe.read_split_file_applying_mwes_if_possible(Params)
    ImagesAndWords = page_oriented_split_list_to_images_and_words(PageOrientedSplitList, Params)
    if ImagesAndWords == False:
        return False
    add_locations_to_pages_images_and_words(ImagesAndWords, ImagesWordsAndLocations)
    return ImagesAndWords

## We want to edit the 'segments' component, e.g.
##
## "segments": {
##        "mary_manuscript_page_1_segment_1": {
##            "anchor": "mary_manuscript_page_1_segment_1",
##            "corpus_name": "mary_manuscript",
##            "page": 1,
##            "plain_text": "Mary had a little lamb",
##            "words": [
##                {
##                    "word": "\n"
##                },
##                {
##                    "corpus_name": "mary_manuscript",
##                    "file": "page1.jpg",
##                    "height": 791,
##                    "multimedia": "img",
##                    "width": 717
##                },
##                {
##                    "word": "\n\n"
##                },
##                {
##                    "audio": {
##                        "corpus_name": "mary_manuscript",
##                        "file": "118812_190719_183034441.mp3"
##                    },
##                    "lemma": "Mary",
##                    "word": "Mary"
##                },
##                ...
##
## by adding locations to the "words" fields
    
def maybe_add_locations_to_representation(Representation, PageOrientedSplitList, Params):
    if Params.picturebook_word_locations_file == '':
        return Representation
    WordLocationsDict = read_picturebook_word_locations_file(Params)
    PagesToImagesDict = page_oriented_split_list_to_pages_and_images(PageOrientedSplitList, Params)
    if not isinstance(WordLocationsDict, dict):
        lara_utils.print_and_flush(f'*** Warning: no data read from word locations file')
        return Representation
    if not isinstance(PagesToImagesDict, dict) and Params.picturebook == 'yes':
        lara_utils.print_and_flush(f'*** Warning: unable to create page-to-image dict for picturebook document')
        return Representation
    return add_locations_to_representation(Representation, WordLocationsDict, PagesToImagesDict, Params)

def add_locations_to_representation(Representation, WordLocationsDict, PagesToImagesDict, Params):
    if not 'segments' in Representation:
        lara_utils.print_and_flush(f'*** Warning: abstract HTML representation does not contain a "segments" field')
        return Representation
    Segments = Representation['segments']
    NLocationsAdded = 0
    for SegmentKey in Segments:
        SegmentRepresentation = Segments[SegmentKey]
        if 'words' in SegmentRepresentation and 'page' in SegmentRepresentation and 'version_in_page' in SegmentRepresentation:
            WordsRepresentation = SegmentRepresentation['words']
            Page = SegmentRepresentation['page']
            Version = SegmentRepresentation['version_in_page']
            ForAnnotatedImage = SegmentRepresentation['for_annotated_image']
            if not Page in PagesToImagesDict and Params.picturebook == 'yes':
                lara_utils.print_and_flush(f'*** Warning: cannot find image for page "{Page}"')
                return Representation
            Image = ForAnnotatedImage if ForAnnotatedImage != False else PagesToImagesDict[Page] if Page in PagesToImagesDict else False
            WordsWithLemmas0 = [ Item['word'] for Item in WordsRepresentation
                                 if isinstance(Item, dict) and 'lemma' in Item and 'word' in Item ]
            WordsWithLemmas = make_list_of_words_canonical_for_word_locations_info(WordsWithLemmas0)
            WordsKey = tuple( WordsWithLemmas + [ 'SPEAKER-CONTROL', 'TRANSLATION-CONTROL' ] + [ Version ] )
            if Image in WordLocationsDict and WordsKey in WordLocationsDict[Image]:
                WordLocationsForSegment = WordLocationsDict[Image][WordsKey][:-2]
                # Last two elements in the word locations  list are the speaker control location and the translation control location
                SegmentRepresentation['speaker_control_location'] = WordLocationsDict[Image][WordsKey][-2][1:]
                SegmentRepresentation['translation_control_location'] = WordLocationsDict[Image][WordsKey][-1][1:]
                for Item in WordsRepresentation:
                    if isinstance(Item, dict) and 'lemma' in Item and 'word' in Item:
                        if len(WordLocationsForSegment) == 0:
                            lara_utils.print_and_flush(f'*** Warning: mismatch with word location information in line "{WordsKey}"')
                            return Representation
                        WordLocationsForFirstWord = WordLocationsForSegment[0]
                        WordLocationWord = WordLocationsForFirstWord[0]
                        WordCoords = WordLocationsForFirstWord[1:]
                        WordLocationsForSegment = WordLocationsForSegment[1:]
                        if WordLocationWord != Item['word']:
                            lara_utils.print_and_flush(f'*** Warning: mismatch with word location information in line "{WordsKey}"')
                        Item['location'] = WordCoords
                        NLocationsAdded += 1
    lara_utils.print_and_flush(f'--- Added {NLocationsAdded} word locations')
    return Representation

def read_picturebook_word_locations_file(Params):
    File = Params.picturebook_word_locations_file 
    if File == '':
        #lara_utils.print_and_flush(f'*** Warning: picturebook_word_locations_file not defined in config file')
        return {}
    if not lara_utils.file_exists(File):
        lara_utils.print_and_flush(f'*** Warning: picturebook_word_locations_file {File} not found')
        return {}
    Data = lara_utils.read_json_file(File)
    if Data == False:
        lara_utils.print_and_flush(f'*** Error: unable to read picturebook_word_locations_file {File}')
        return False
    InternalisedData = internalise_picturebook_images_words_locations_data(Data)
    lara_utils.print_and_flush(f'--- Read picturebook_word_locations_file {File}')
    return InternalisedData

# Picturebook image file data is a dict with items of form
#
#   ImageName: [ [ [ Word11, CoordsA11, CoordsB11], [ Word12, CoordsA12, CoordsB12], ... ],
#                [ [ Word21, CoordsA21, CoordsB21], [ Word22, CoordsA22, CoordsB22], ... ],
#                ... ]
#
# We store this indexing on the word lists, i.e. as
#   ImageName: { ( Word11, Word12, ... ): [ [ Word11, CoordsA11, CoordsB11], [ Word12, CoordsA12, CoordsB12], ... ],
    #                ( Word21, Word22, ... ): [ [ Word21, CoordsA21, CoordsB21], [ Word22, CoordsA22, CoordsB22], ... ],
#                ... ]


def internalise_picturebook_images_words_locations_data(Data):
    if not isinstance(Data, dict):
        lara_utils.print_and_flush(f'*** Error: picturebook location file data is not a dict')
        return False
    Dict = {}
    for Image in Data:
        DataForImage0 = Data[Image]
        DataForImage = try_to_clean_up_data_for_image(DataForImage0, Image)
        if not valid_location_data_for_image(DataForImage):
            lara_utils.print_and_flush(f'*** Error: picturebook location file data for {Image} is invalid')
            return False
        Subdict0 = {}
        Subdict = {}
        for Item0 in DataForImage:
            Item = [ internalise_word_and_coords(Tuple) for Tuple in Item0 ]
            Words = [ Triple[0] for Triple in Item ]
            Key0 = tuple(Words)
            VersionInPage = Subdict0[Key0] + 1 if Key0 in Subdict0 else 1
            Subdict0[Key0] = VersionInPage
            Key = tuple(Words + [VersionInPage])
            Subdict[Key] = Item
        Dict[Image] = Subdict
    return Dict

def internalise_word_and_coords(Tuple):
    return [ lara_replace_chars.replace_reserved_chars(Tuple[0]) ] + Tuple[1:]

def try_to_clean_up_data_for_image(Data, Image):
    if not isinstance(Data, ( list, tuple )):
        return Data
    Data1 = []
    for LineItem in Data:
        if not isinstance(LineItem, ( list, tuple )) or len(LineItem) < 3:
            return Data
        LineItem1 = remove_word_items_after_translation_control(LineItem, Image)
        Data1 += [ LineItem1 ]
    return Data1

def remove_word_items_after_translation_control(LineItem, Image):
    N = len(LineItem)
    for I in range(0, N):
        WordItem = LineItem[I]
        if not isinstance(WordItem, ( list )) or len(WordItem) < 3:
            return LineItem
        if not isinstance(WordItem[0], ( str )):
            return LineItem
        if WordItem[0] == 'TRANSLATION-CONTROL' and I < N - 1:
            lara_utils.print_and_flush(f'*** Warning: removed material after TRANSLATION-CONTROL in {LineItem} in {Image}')
            return LineItem[:I+1]
    return LineItem

def valid_location_data_for_image(Data):
    if not isinstance(Data, ( list, tuple )):
        lara_utils.print_and_flush(f'*** Error: data is not a list')
        lara_utils.prettyprint(Data)
        return False
    for LineItem in Data:
        if not isinstance(LineItem, ( list, tuple )) or len(LineItem) < 3:
            lara_utils.print_and_flush(f'*** Error: line data {LineItem} is not a list with at least three element')
            lara_utils.prettyprint(Item)
            return False
        for WordItem in LineItem:
            if not isinstance(WordItem, ( list )) or len(WordItem) < 3:
                lara_utils.print_and_flush(f'*** Error: element {WordItem} in LineItem {LineItem} is not a list with at least three elements')
                return False
            if not isinstance(WordItem[0], ( str )):
                lara_utils.print_and_flush(f'*** Error: first element {WordItem[0]} in WordItem item {WordItem} is not a string')
                return False
            for CoordsItem in WordItem[1:]:
                if not isinstance(CoordsItem, ( list, tuple )) or len(CoordsItem) != 2:
                    lara_utils.print_and_flush(f'*** Error: coordinates item {CoordsItem} in word item {WordItem} is not a list with two elements')
                    return False
                for Coord in CoordsItem:
                    if not isinstance(Coord, ( int )) and Coord != '':
                        lara_utils.print_and_flush(f'*** Error: bad coordinate {Coord} in word item {WordItem}, must be number or empty list')
                        return False
    return True

##[
##    [
##        {
##            "corpus": "local_files",
##            "page": 1
##        },
##        [
##            [
##                "\n<img src=\"page1.jpg\" width=\"717\" height=\"791\"/>\n\nMary#Mary# had#have# a little lamb",
##                "Mary had a little lamb",
##                [
##                    [
##                        "\n",
##                        ""
##                    ],
##                    [
##                        "<img src=\"page1.jpg\" width=\"717\" height=\"791\"/>",
##                        ""
##                    ],
##                    [
##                        "\n\n",
##                        ""
##                    ],
##                    [
##                        "Mary",
##                        "Mary"
##                    ],
##                    [
##                        " ",
##                        ""

def page_oriented_split_list_to_images_and_words(PageOrientedSplitList, Params):
    Result = page_oriented_split_list_to_images_and_words_plus_pages_and_images(PageOrientedSplitList, Params)
    return Result['images_and_words'] if isinstance(Result, dict) and 'images_and_words' in Result else False

def page_oriented_split_list_to_pages_and_images(PageOrientedSplitList, Params):
    Result = page_oriented_split_list_to_images_and_words_plus_pages_and_images(PageOrientedSplitList, Params)
    return Result['pages_and_images'] if isinstance(Result, dict) and 'pages_and_images' in Result else False

def page_oriented_split_list_to_images_and_words_plus_pages_and_images(PageOrientedSplitList, Params):
    if Params.picturebook == 'yes':
        return page_oriented_split_list_to_images_and_words_plus_pages_and_images_picturebook(PageOrientedSplitList, Params)
    else:
        return page_oriented_split_list_to_images_and_words_plus_pages_and_images_annotated_images(PageOrientedSplitList, Params)

def page_oriented_split_list_to_images_and_words_plus_pages_and_images_picturebook(PageOrientedSplitList, Params):
    ( ImagesAndWordsDict, PagesAndImagesDict ) = ( {}, {} )
    for ( PageInfo, Segments ) in PageOrientedSplitList:
        Page = PageInfo['page']
        ImagesAndWords = []
        for Segment in Segments:
            if len(Segment) != 4:
                lara_utils.print_and_flush(f'*** Error: annotated image found but text is declared as pure picturebook')
                return False
            ( Raw, Clean, Pairs, Tag ) = Segment
            Words0 = [ Pair[0] for Pair in Pairs if Pair[1] != '' ] + [ 'SPEAKER-CONTROL', 'TRANSLATION-CONTROL' ]
            Words = make_list_of_words_canonical_for_word_locations_info(Words0)
            Images = [ extract_image_name(Pair[0], Params) for Pair in Pairs
                       if Pair[1] == '' and Pair[0].startswith('<img') and Pair[0].endswith('/>') ]
            if len(Images) > 0 or len(Words) > 2:
                ImagesAndWords += [ { 'images': Images, 'words':Words } ]
        #lara_utils.print_and_flush(f'--- ImagesAndWords for page {Page} (Pairs = {Pairs})')
        #lara_utils.prettyprint(ImagesAndWords)
        AllImagesOnPage = lara_utils.remove_duplicates([ Image for Item in ImagesAndWords for Image in Item['images'] ])
        if False in AllImagesOnPage:
            lara_utils.print_and_flush(f'*** Error: bad image on page {Page}')
            return False
        if not len(AllImagesOnPage) == 1:
            lara_utils.print_and_flush(f'*** Error: {len(AllImagesOnPage)} images on page {Page}')
            return False
        Image = AllImagesOnPage[0]
        ImagesAndWordsDict[Image] = [ Item['words'] for Item in ImagesAndWords if len(Item['words']) > 2 ]
        PagesAndImagesDict[Page] = Image
    lara_utils.print_and_flush(f'--- Converted split list to images and words')
    return { 'images_and_words': ImagesAndWordsDict, 'pages_and_images': PagesAndImagesDict }

def page_oriented_split_list_to_images_and_words_plus_pages_and_images_annotated_images(PageOrientedSplitList, Params):
    ImagesAndWordsDict = {}
    for ( PageInfo, OuterSegments ) in PageOrientedSplitList:
        Page = PageInfo['page']
        for OuterSegment in OuterSegments:
            if is_annotated_image_segment(OuterSegment):
                Segments = annotated_image_segments(OuterSegment)
                ImagesAndWords = []
                for ( Raw, Clean, Pairs, Tag ) in Segments:
                    Words0 = [ Pair[0] for Pair in Pairs if Pair[1] != '' ] + [ 'SPEAKER-CONTROL', 'TRANSLATION-CONTROL' ]
                    Words = make_list_of_words_canonical_for_word_locations_info(Words0)
                    Images = [ extract_image_name(Pair[0], Params) for Pair in Pairs
                               if Pair[1] == '' and Pair[0].startswith('<img') and Pair[0].endswith('/>') ]
                    if len(Images) > 0 or len(Words) > 2:
                        ImagesAndWords += [ { 'images': Images, 'words':Words } ]
                #lara_utils.print_and_flush(f'--- ImagesAndWords for page {Page} (Pairs = {Pairs})')
                #lara_utils.prettyprint(ImagesAndWords)
                AllImagesInAnnotatedImage = lara_utils.remove_duplicates([ Image for Item in ImagesAndWords for Image in Item['images'] ])
                if False in AllImagesInAnnotatedImage:
                    lara_utils.print_and_flush(f'*** Error: bad image on page {Page}')
                    return False
                if not len(AllImagesInAnnotatedImage) == 1:
                    lara_utils.print_and_flush(f'*** Error: {len(AllImagesInAnnotatedImage)} images in annotated image on page {Page} ({AllImagesInAnnotatedImage})')
                    return False
                Image = AllImagesInAnnotatedImage[0]
                ImagesAndWordsDict[Image] = [ Item['words'] for Item in ImagesAndWords if len(Item['words']) > 2 ]
    lara_utils.print_and_flush(f'--- Converted split list to images and words')
    return { 'images_and_words': ImagesAndWordsDict, 'pages_and_images': [] }

def image_names_in_segments_list(Segments, Params):
    AllImages = []
    for Segment in Segments:
        Pairs = Segment[2]
        Images = [ extract_image_name(Pair[0], Params) for Pair in Pairs
                   if Pair[1] == '' and Pair[0].startswith('<img') and Pair[0].endswith('/>') ]
        if len(Images) > 0:
            AllImages += Images
    return lara_utils.remove_duplicates(AllImages)

def extract_image_name(Str, Params):
    ImgRepresentation = lara_images.img_tag_to_representation(Str)
    if ImgRepresentation == False:
        return False
    else:
        return ImgRepresentation['file']

def add_locations_to_pages_images_and_words(ImagesAndWords, ImagesWordsAndLocations):
    for Image in ImagesAndWords:
        ListOfListOfWords = ImagesAndWords[Image]
        ListOfWordAndLocations = []
        VersionDict = {}
        for ListOfWords in ListOfListOfWords:
            Key0 = tuple(ListOfWords)
            Version = VersionDict[Key0] + 1 if Key0 in VersionDict else 1
            VersionDict[Key0] = Version
            Key = tuple(ListOfWords + [ Version ])
            if Image in ImagesWordsAndLocations and Key in ImagesWordsAndLocations[Image]:
                StoredWordsAndLocations = ImagesWordsAndLocations[Image][Key]
            else:
                StoredWordsAndLocations = []
            if len(StoredWordsAndLocations) == len(ListOfWords):
                WordsAndLocations = StoredWordsAndLocations
            else:
                WordsAndLocations = [ [ Word, [ '', ''], [ '', ''] ] for Word in ListOfWords ]
            ListOfWordAndLocations += [ WordsAndLocations ]
        ImagesAndWords[Image] = ListOfWordAndLocations

def restore_reserved_chars_in_images_words_and_locations(ImagesAndWords):
    return { Key: restore_reserved_chars_in_images_words_and_locations1(ImagesAndWords[Key]) for Key in ImagesAndWords }

def restore_reserved_chars_in_images_words_and_locations1(ListOfLists):
    return [ restore_reserved_chars_in_images_words_and_locations2(List) for List in ListOfLists ]

def restore_reserved_chars_in_images_words_and_locations2(WordCoordTuples):
    return [ restore_reserved_chars_in_words_coord_tuple(Tuple) for Tuple in WordCoordTuples ]

def restore_reserved_chars_in_words_coord_tuple(WordCoordTuple):
    return [ lara_replace_chars.restore_reserved_chars(WordCoordTuple[0]) ] + WordCoordTuple[1:] 

def write_out_word_location_file(ImagesAndWords, TmpWordLocationFile):
    #lara_utils.prettyprint(ImagesAndWords)
    lara_utils.write_json_to_file_plain_utf8(ImagesAndWords, TmpWordLocationFile)
    lara_utils.print_and_flush(f'--- Written images and locations file {TmpWordLocationFile}')

def write_out_word_location_zipfile(ImagesAndWords, TmpWordLocationFile, TmpZipfile, Params):
    if not isinstance(ImagesAndWords, dict):
        lara_utils.print_and_flush(f'*** Error: unable to create word location zipfile')
        return
    if len(ImagesAndWords) == 0:
        lara_utils.print_and_flush(f'--- No word location data, not creating word location zipfile')
        return
    TmpDir = lara_utils.get_tmp_directory(Params)
    Images = list(ImagesAndWords.keys())
    lara_utils.copy_file(TmpWordLocationFile, f'{TmpDir}/word_locations.json')
    copy_selected_images_to_dir(Images, TmpDir, Params)
    lara_utils.make_zipfile(TmpDir, TmpZipfile)
    lara_utils.print_and_flush(f'--- Written images and locations zipfile {TmpZipfile}')
    lara_utils.delete_directory_if_it_exists(TmpDir)

##def check_images_exist(Images, Params):
##    Dir = Params.image_directory
##    if not lara_utils.directory_exists(Dir):
##        lara_utils.print_and_flush(f'*** Error: directory not found: {Dir}')
##        return False
##    for Image in Images:
##        FullFile = f'{Dir}/{Image}'
##        if not lara_utils.file_exists(FullFile):
##            lara_utils.print_and_flush(f'*** Error: file not found: {FullFile}')
##            return False
##    return True

def copy_selected_images_to_dir(Images, TmpDir, Params):
    Dir = Params.image_directory
    for Image in Images:
        FromFile = f'{Dir}/{Image}'
        ToFile = f'{TmpDir}/{Image}'
        if not lara_utils.copy_file(FromFile, ToFile):
            lara_utils.print_and_flush(f'*** Warning: unable to copy {FromFile} to {ToFile}')
       

# Call this in lara_split_and_clean to collect lists of segments demarcated as annotated_images

def collect_annotated_images_in_split_list(SplitList, PageNumber, Params):
    ( State, OutList, CurrentAnnotatedImageList ) = ( '*outside_annotated_image*', [], [] )
    for Segment in SplitList:
        if Segment == '*annotated_image_start*' and State == '*outside_annotated_image*':
            ( State, CurrentAnnotatedImageList ) = ( '*inside_annotated_image*', [] )
        elif Segment == '*annotated_image_start*' and State == '*inside_annotated_image*':
            lara_utils.print_and_flush(f'*** Error: nested <annotated_image> tags on page {PageNumber}')
            return []
        elif Segment == '*annotated_image_end*' and State == '*inside_annotated_image*':
            State = '*outside_annotated_image*'
            Images = image_names_in_segments_list(CurrentAnnotatedImageList, Params)
            if len(Images) == 0:
                lara_utils.print_and_flush(f'*** Error: no image in <annotated_image> on page {PageNumber}')
                return []
            elif len(Images) > 1:
                lara_utils.print_and_flush(f'*** Error: multiple images {Images} in <annotated_image> on page {PageNumber}')
                return []
            else:
                OutList += [ make_annotated_image_segment(Images[0], CurrentAnnotatedImageList ) ]
        elif Segment == '*annotated_image_end*' and State == '*outside_annotated_image*':
            lara_utils.print_and_flush(f'*** Error: unmatched </annotated_image> tag on page {PageNumber}')
            return []
        elif State == '*outside_annotated_image*':
            OutList += [ Segment ]
        else:
            CurrentAnnotatedImageList += [ Segment ]
    if State == '*inside_annotated_image*':
        lara_utils.print_and_flush(f'*** Error: unmatched <annotated_image> tag on page {PageNumber}')
        #lara_utils.prettyprint(SplitList)
        return []
    else:
        #lara_utils.print_and_flush(f'--- Output from collect_annotated_images_in_split_list')
        #lara_utils.prettyprint(OutList)
        return OutList

def annotated_image_segment_to_string(AnnotatedImage):
    Segments = annotated_image_segments(AnnotatedImage)
    return '<annotated_image>' + '||'.join([ Segment[0] for Segment in Segments ]) + '</annotated_image>'   

# For many operations, we don't care about the annotated_image structure, so use this function to remove it

def expand_annotated_images_in_split_list(PageOrientedSplitList):
    return [ ( PageInfo, expand_annotated_images_in_split_list1(Segments) )
             for ( PageInfo, Segments ) in PageOrientedSplitList ]

def expand_annotated_images_in_split_list1(Segments):
    SegmentsOut = []
    for Segment in Segments:
        if is_annotated_image_segment(Segment):
            SegmentsOut += annotated_image_segments(Segment)
        else:
            SegmentsOut += [ Segment ]
    return SegmentsOut

def is_annotated_image_segment(AnnotatedImage):
    return isinstance(AnnotatedImage, dict ) and 'image' in AnnotatedImage and 'segments' in AnnotatedImage

def annotated_image_image(AnnotatedImage):
    return AnnotatedImage['image']

def annotated_image_segments(AnnotatedImage):
    return AnnotatedImage['segments']

def make_annotated_image_segment(Image, Segments):
    return { 'image':Image, 'segments':Segments }

def is_annotated_image_marker(Object):
    return Object in ( '*annotated_image_start*', '*annotated_image_end*' )

def is_annotated_image_representation(SegmentNameOrImage):
    return isinstance(SegmentNameOrImage, dict ) and 'annotated_image' in SegmentNameOrImage and SegmentNameOrImage['annotated_image'] == 'yes'

# -------------------------------------------------

#  Operations for moving picturebook information to and from the Selector Tool:
#  
#  1. Download data from Selector Tool.
#  
#  get_and_store_selector_tool_data_for_config_file(ConfigFile)
#  
#  Download the data for ConfigFile's id and store it in the picturebook_word_locations_file file.
#  Define this file if it isn't already there.
#  
#  2. Resources step
#  
#  This will create tmp files which merge the downloaded word location data with any new data coming from the text.
#  
#  3. Copy the tmp files into place, in the picturebook_word_locations_file, the Selector Tool directory, and the Selector Tool DB
#
#  copy_tmp_picturebook_data_into_place(ConfigFile, TmpWordLocationsFile, TmpZipfile, Dir)
#
# -------------------------------------------------

# Copy the tmp word location file created by the 'resources' step to
# a) the corpus directory,
# b) the Selector Tool directory
# c) the Selector Tool DB

def copy_tmp_picturebook_data_into_place(ConfigFile, TmpWordLocationsFile, TmpZipfile, Dir):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if Params == False:
        return
    if not params_use_word_locations(Params):
        lara_utils.print_and_flush(f'--- Project does not use word locations, no need to upload data to Selector Tool')
        return
    # Copy tmp word location file file to corpus directory, where it is referenced by Params.picturebook_word_locations_file 
    if Params.picturebook_word_locations_file == '':
        Params.picturebook_word_locations_file = default_picturebook_word_locations_file(Params)
        #lara_utils.write_json_to_file_plain_utf8(dict(Params), ConfigFile)
        lara_config.save_params_as_config_file(Params, ConfigFile)
    lara_utils.copy_file(TmpWordLocationsFile, Params.picturebook_word_locations_file)
    # Copy tmp word locations zipfile to the Selector Tool directory
    copy_picturebook_data_to_selector_tool_directory(TmpZipfile, Dir, Params)
    # Copy Params.picturebook_word_locations_file to the Selector Tool DB
    copy_picturebook_data_to_selector_tool_db(Params)

# -------------------------------------------------

def copy_picturebook_data_to_selector_tool_directory(TmpZipfile, Dir, Params):
    if not lara_utils.file_exists(TmpZipfile):
        lara_utils.print_and_flush(f'*** Warning: picturebook data file {TmpZipfile} does not exist')
        return True
    Id = Params.id
    SubDir = f'{Dir}/{Id}'
    lara_utils.create_directory_if_it_doesnt_exist(SubDir)
    MetadataFile = f'{Dir}/metadata.json'
    Metadata = lara_utils.read_json_file(MetadataFile) if lara_utils.file_exists(MetadataFile) else []
    if Metadata == False:
        lara_utils.print_and_flush(f'*** Warning: metadata file {MetadataFile} could not be read, creating new file')
        Metadata = { 'texts': [] }
    Result = lara_utils.unzip_file(TmpZipfile, SubDir)
    if Result == False:
        lara_utils.print_and_flush(f'*** Error: unable to unzip picturebook data {TmpZipfile} to {SubDir}')
        return False
    NewMetadata = add_id_to_picturebook_metadata(Metadata, Id)
    if NewMetadata == False:
        return False
    Result = lara_utils.unzip_file(TmpZipfile, SubDir)
    lara_utils.write_json_to_file_plain_utf8(NewMetadata, MetadataFile)
    lara_utils.print_and_flush(f'--- Copied picturebook data to {SubDir} and updated metadata ({len(NewMetadata["texts"])} items)')
    return True

def add_id_to_picturebook_metadata(Metadata, Id):
    if isinstance(Metadata, dict) and 'texts' in Metadata and isinstance(Metadata['texts'], list):
        return { 'texts': ( Metadata['texts'] + [ Id ] ) } if not Id in Metadata['texts'] else Metadata
    else:
        lara_utils.print_and_flush(f'*** Error: malformed metadata in {MetadataFile}, {Metadata}')
        return False

# -------------------------------------------------

def copy_picturebook_data_to_selector_tool_db(Params):
    if Params.selector_tool_id == '':
        copy_picturebook_data_to_selector_tool_db_new(Params)
    else:
        copy_picturebook_data_to_selector_tool_db_update(Params, Params.selector_tool_id)

def copy_picturebook_data_to_selector_tool_db_new(Params):
    File = Params.picturebook_word_locations_file
    if File == '':
        lara_utils.print_and_flush(f'*** Warning: no picturebook data file defined for "{Id}"')
        return False
    if not lara_utils.file_exists(File):
        lara_utils.print_and_flush(f'*** Warning: picturebook data file {File} not found')
        return False
    Id = Params.id
    WordLocationData = lara_utils.read_json_file(File)
    if WordLocationData == False:
        lara_utils.print_and_flush(f'*** Error: unable to read picturebook data file {File} not found')
        return False
    Headers = {}
    URI = f'{_picturebook_select_tool_url}'
    # Remove final slash on URI if there
    URI = URI[:-1] if URI[-1] == '/' else URI
    JSONData = { 'data': { 'Title': Id, 'objectCoordinates': WordLocationData } }
    lara_utils.print_and_flush(f'--- Uploading data in {File} to {URI} (new DBID)')
    Response = requests.post(URI, headers=Headers, json=JSONData)
    StatusCode = Response.status_code
    if StatusCode == 200:
        lara_utils.print_and_flush(f'--- Succeeded')
        return True
    else:
        lara_utils.print_and_flush(f'--- Error: status code {StatusCode}')
        return False                
    

# Updates data for a specific DBID
def copy_picturebook_data_to_selector_tool_db_update(Params, DBID):
    Id = Params.id
    File = Params.picturebook_word_locations_file
    if File == '':
        lara_utils.print_and_flush(f'*** Warning: no picturebook data file defined for "{Id}"')
        return False
    if not lara_utils.file_exists(File):
        lara_utils.print_and_flush(f'*** Warning: picturebook data file {File} not found')
        return False
    WordLocationData = lara_utils.read_json_file(File)
    if WordLocationData == False:
        lara_utils.print_and_flush(f'*** Error: unable to read picturebook data file {File} not found')
        return False
    Headers = {}
    URI = f'{_picturebook_select_tool_url}{DBID}'
    JSONData = { 'data': { 'objectCoordinates': WordLocationData } }
    lara_utils.print_and_flush(f'--- Uploading data in {File} to {URI} (existing DBID)')
    Response = requests.put(URI, headers=Headers, json=JSONData)
    StatusCode = Response.status_code
    if StatusCode == 200:
        lara_utils.print_and_flush(f'--- Succeeded')
        return True
    else:
        lara_utils.print_and_flush(f'--- Error: status code {StatusCode}')
        return False                
    
# -------------------------------------------------

def get_and_store_selector_tool_data_for_config_file(ConfigFile):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if Params == False:
        return
    if not params_use_word_locations(Params):
        lara_utils.print_and_flush(f'--- Project does not use word locations, no need to download data from Selector Tool')
        return
    Data = get_picturebook_selector_tool_data_for_lara_id(Params.id)
    if Data == False:
        return
    store_selector_tool_data(Data, ConfigFile, Params)

##    {"data":[{"id":1,
##              "attributes":{"Title":"le_petit_prince_abc",
##                            "objectCoordinates":{"a.jpg":[[["astronome",[244,262],[583,604]],
##                                                           ["SPEAKER-CONTROL",["",""],["",""]],
##                                                           ["TRANSLATION-CONTROL",
##                                                            (...)

def get_picturebook_selector_tool_data_for_lara_id(Id):
    lara_utils.print_and_flush(f'--- Downloading data from {_picturebook_select_tool_url}...')
    StartTime = time.time()
    AllData = lara_utils.read_json_from_url(_picturebook_select_tool_url)
    if StartTime is not None: 
        lara_utils.print_and_flush_with_elapsed_time('--- Downloaded data', StartTime)
    if not isinstance(AllData, dict) or not 'data' in AllData:
        lara_utils.print_and_flush(f'*** Error: data returned from {_picturebook_select_tool_url} is not a dict with "data" as a key')
        return False
    AllData1 = AllData['data']
    AllKeys = [ Item['attributes']['Title'] for Item in AllData1 if
                isinstance(Item, dict) and 'attributes' in Item and \
                'Title' in Item['attributes'] and 'objectCoordinates' in Item['attributes'] ]
    lara_utils.print_and_flush(f'--- Data for {len(AllKeys)} IDs found')
    for Item in AllData1:
        if isinstance(Item, dict) and 'attributes' in Item and \
           'Title' in Item['attributes'] and 'objectCoordinates' in Item['attributes'] and \
           Item['attributes']['Title'] == Id:
            #return Item['attributes']['objectCoordinates']
            return Item
    lara_utils.print_and_flush(f'*** Warning: no data for {Id} returned from {_picturebook_select_tool_url}. Available IDs = {AllKeys}')
    return False

def store_selector_tool_data(Data, ConfigFile, Params):
    if not well_formed_selector_tool_data(Data):
        return
    DBID = Data['id']
    WordLocationData = Data['attributes']['objectCoordinates']
    Params.selector_tool_id = DBID
    if Params.picturebook_word_locations_file == '':
        Params.picturebook_word_locations_file = default_picturebook_word_locations_file(Params)
        #lara_utils.write_json_to_file_plain_utf8(dict(Params), ConfigFile)
        lara_config.save_params_as_config_file(Params, ConfigFile)
    lara_utils.write_json_to_file_plain_utf8(WordLocationData, Params.picturebook_word_locations_file)
    lara_utils.print_and_flush(f'--- Saved data for selector tool id "{DBID}" in {Params.picturebook_word_locations_file}')

def well_formed_selector_tool_data(Data):
    if 'id' in Data and 'attributes' in Data and 'Title' in Data['attributes'] and 'objectCoordinates' in Data['attributes']:
        return True
    lara_utils.print_and_flush(f'*** Error: malformed selector tool data: {str(Data)[:200]}')
    return False

def default_picturebook_word_locations_file(Params):
    CorpusDir = lara_utils.directory_for_pathname(Params.corpus)
    return f'{CorpusDir}/word_locations.json'                                 

# -------------------------------------------------

def params_use_word_locations(Params):
    if Params.picturebook == 'yes':
        return True
    Text = lara_utils.read_lara_text_file(Params.corpus)
    if Text == False:
        return False
    return Text.find('<annotated_image>') >= 0

# -------------------------------------------------

def make_list_of_words_canonical_for_word_locations_info(Words):
    if not isinstance(Words, ( tuple, list )):
        lara_utils.print_and_flush(f'*** Error: argument to make_list_of_words_canonical_for_word_locations_info, {Words}, is not a list')
        return False
    return [ make_word_canonical_for_word_locations_info(Word) for Word in Words ]

def make_word_canonical_for_word_locations_info(Word):
    return lara_parse_utils.remove_html_annotations_from_string(Word)[0]

# -------------------------------------------------

def is_list_of_lists_of_n_element_lists(List, N):
    if not isinstance(List, ( list, tuple )):
        return False
    for Item in List:
        if not is_list_of_n_element_lists(Item, N):
            return False
    return True

def is_list_of_n_element_lists(List, N):
    if not isinstance(List, ( list, tuple )):
        return False
    for Item in List:
        if not isinstance(Item, ( list, tuple )) or len(Item) != N:
            return False
    return True

# -------------------------------------------------

def change_scale_in_locations_file(InFile, Factor, OutFile):
    InData = lara_utils.read_json_file(InFile)
    if not isinstance(InData, dict):
        lara_utils.print_and_flush(f'*** Error: unable to read data from {InFile}')
        return
    OutData = change_scale_in_locations_data(InData, Factor)
    lara_utils.write_json_to_file_plain_utf8(OutData, OutFile)

def change_scale_in_locations_data(InData, Factor):
    OutData = {}
    for Key in InData:
        OutData[Key] = change_scale_in_locations_data_for_image(InData[Key], Factor)
    return OutData

def change_scale_in_locations_data_for_image(ImageData, Factor):
    return [ change_scale_in_locations_data_for_segment(Segment, Factor) for Segment in ImageData ]

def change_scale_in_locations_data_for_segment(Segment, Factor):
    return [ change_scale_in_locations_data_for_word(Word, Factor) for Word in Segment ]

def change_scale_in_locations_data_for_word(Word, Factor):
    return [ Word[0] ] + [ change_scale_in_coordinate_pair(Pair, Factor) for Pair in Word[1:] ]

def change_scale_in_coordinate_pair(Pair, Factor):
    if isinstance(Pair, list) and len(Pair) == 2 and isinstance(Pair[0], int) and isinstance(Pair[1], int):
        return [ int(Pair[0] * Factor), int(Pair[1] * Factor) ]
    else:
        return Pair
    
