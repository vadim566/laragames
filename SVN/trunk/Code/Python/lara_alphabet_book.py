
import lara_audio
import lara_install_audio_zipfile
import lara_translations
import lara_config
import lara_parse_utils
import lara_utils

#letter	letter sound file	letter image file   word1   soundword1	            image word1	                word2	soundword2	            image word2																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																							
#א	sounds/letters/1.m4a	letters/alef.png    אמא     sounds/words/אמא.m4a    wordImages/mother.jpeg	ארנב	sounds/words/אמאארנב.m4a    wordImages/rabbit.gif																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																							

def test(Id):
    if Id == 'hebrew':
        CSVFile = '$LARA/Content/hebrew_alphabet/source/HebrewAlphabetBook.csv'
        SourceDir = '$LARA/Content/hebrew_alphabet/source'
        TargetDir = '$LARA/Content/hebrew_alphabet'
        Args = { 'id': 'hebrew_abc',
                 'language': 'hebrew',
                 'format': 'letter_word_word_no_translations',
                 'text_direction': 'rtl',
                 'image_height': 200 }
        LanguageDirection = 'rtl'
        make_alphabet_book(CSVFile, SourceDir, TargetDir, Args)
    elif Id == 'arabic':
        CSVFile = '$LARA/Content/arabic_alphabet_book/source/ArabicAlphabetBook.csv'
        SourceDir = '$LARA/Content/arabic_alphabet_book/source'
        TargetDir = '$LARA/Content/arabic_alphabet_book'
        Args = { 'id': 'arabic_abc',
                 'language': 'arabic',
                 'format': 'letter_word_word_word_translations',
                 'text_direction': 'rtl',
                 'image_height': 200 }
        LanguageDirection = 'rtl'
        make_alphabet_book(CSVFile, SourceDir, TargetDir, Args)
    elif Id == 'farsi':
        CSVFile = '$LARA/Content/farsi_alphabet_book/source/FarsiAlphabetBook.csv'
        SourceDir = '$LARA/Content/farsi_alphabet_book/source/alphabet_book_images'
        TargetDir = '$LARA/Content/farsi_alphabet_book'
        Args = { 'id': 'farsi_abc',
                 'language': 'farsi',
                 'format': 'letter_word_word_word_translations',
                 'text_direction': 'rtl',
                 'image_height': 200 }
        LanguageDirection = 'rtl'
        make_alphabet_book(CSVFile, SourceDir, TargetDir, Args)
    elif Id == 'slovak':
        CSVFile = '$LARA/Content/slovak_abc2/corpus/slovak_abc_content.csv'
        ImageDir = '$LARA/Content/slovak_abc2/images'
        GeneratedCorpusFile = '$LARA/Content/slovak_abc2/corpus/slovak_abc_generated.txt'
        make_simple_alphabet_book(CSVFile, ImageDir, GeneratedCorpusFile)
    elif Id == 'icelandic':
        CSVFile = '$LARA/Content/icelandic_abc/corpus/icelandic_abc_content.csv'
        ImageDir = '$LARA/Content/icelandic_abc/images'
        GeneratedCorpusFile = '$LARA/Content/icelandic_abc/corpus/icelandic_abc_generated.txt'
        make_simple_alphabet_book(CSVFile, ImageDir, GeneratedCorpusFile)

def make_alphabet_book(CVSFile, SourceDir, TargetDir, Args):
    if check_args(Args) == False:
        return
    Data0 = lara_utils.read_lara_csv(CVSFile)
    if Data0 == False:
        return
    Data = Data0[1:]
    make_config_file(Args, TargetDir)
    make_corpus_file(Data, Args, SourceDir, TargetDir)
    make_word_locations_file(Data, Args, SourceDir, TargetDir)
    make_word_translation_file(Data, Args, SourceDir, TargetDir)
    make_image_dir(Data, Args, SourceDir, TargetDir)
    make_audio_dirs(Data, Args, SourceDir, TargetDir)

def check_args(Args):
    for Key in ( 'id', 'language' ):
        if not Key in Args:
            lara_utils.print_and_flush(f'*** Error: {Key} not defined in args')
            return False
    return True

def make_config_file(Args, TargetDir):
    ConfigFile = config_file(TargetDir)
    CorpusFile = corpus_file(Args, TargetDir)
    ImageDir = image_dir(TargetDir)
    WordAudioDir = word_audio_dir(Args, TargetDir)
    SegmentAudioDir = segment_audio_dir(Args, TargetDir)
    SegmentTranslationSpreadsheet = segment_translation_spreadsheet(Args, TargetDir)
    WordTranslationSpreadsheet = word_translation_spreadsheet(Args, TargetDir)
    WordLocationFile = word_locations_file(TargetDir)
    Id = Args['id']
    Language = Args['language']
    TextDirection = Args['text_direction'] if 'text_direction' in Args else 'ltr'
    Params = {  'allow_table_of_contents': 'yes',
                'audio_mouseover': 'yes',
                'audio_segments': 'yes',
                'coloured_words': 'no',
                'corpus': CorpusFile,
                'css_file': 'picturebook_style.css',
                'font': 'serif',
                'font_size': 'xx-large',
                'phonetic_headings_are_comments': 'no',
                'id': Id,
                'image_directory': ImageDir,
                'language': Language,
                'max_examples_per_word_page': 10,
                'picturebook_word_locations_file': WordLocationFile,
                'segment_audio_directory': SegmentAudioDir,
                'segment_translation_character': '\u270e',
                'segment_translation_mouseover': 'yes',
                'segment_translation_spreadsheet': SegmentTranslationSpreadsheet,
                'text_direction': TextDirection,
                'translation_mouseover': 'yes',
                'translation_spreadsheet_surface': WordTranslationSpreadsheet,
                'word_audio_directory': WordAudioDir,
                'word_translations_on': 'surface_word_type'
        }
    lara_utils.write_json_to_file_plain_utf8(Params, ConfigFile)
    return

def make_word_locations_file(Data, Args, SourceDir, TargetDir):
    WordLocationsFile = word_locations_file(TargetDir)
    WordLocationsData = {}
    for Line in Data:
        ( BaseImageFile, LocationData ) = word_locations_data_for_line(Line, Args, SourceDir)
        WordLocationsData[BaseImageFile] = LocationData
    lara_utils.write_json_to_file_plain_utf8(WordLocationsData, WordLocationsFile)
    return

def word_locations_data_for_line(Line, Args, SourceDir):
    ( Letter, LetterSound, LetterImage ) = Line[:3]
    ( LetterImageWidth, LetterImageHeight ) = lara_utils.size_of_image(f'{SourceDir}/{LetterImage}')
    BaseImageFile = base_part_of_pathname(LetterImage)
    WordLocationData = [ [ [ Letter, [ 1, 1 ], [ LetterImageWidth, LetterImageHeight ] ],
                           [ 'SPEAKER-CONTROL', [ '', '' ], [ '', '' ] ],
                           [ 'TRANSLATION-CONTROL', [ '', '' ], [ '', '' ] ] ] ]
    return ( BaseImageFile, WordLocationData )
    
def make_word_translation_file(Data, Args, SourceDir, TargetDir):
    WordTranslationsSpreadsheet = word_translation_spreadsheet(Args, TargetDir)
    WordTranslationPairs = []
    for Line in Data:
        TranslationPairs = get_word_translation_pairs_from_line(Line, Args)
        WordTranslationPairs += TranslationPairs
    if len(WordTranslationPairs) != 0:
        Header = [ 'Word', 'Translation' ]
        lara_translations.write_translation_csv(Header, WordTranslationPairs, WordTranslationsSpreadsheet)

def get_word_translation_pairs_from_line(Line, Args):
    if Args['format'] != 'letter_word_word_word_translations':
        return []
    ( Letter, LetterSound, LetterImage,
      Word1, Word1Trans, Word1Sound, Word1Image,
      Word2, Word2Trans, Word2Sound, Word2Image,
      Word3, Word3Trans, Word3Sound, Word3Image ) = Line
    return [ [ Word1, Word1Trans ],
             [ Word2, Word2Trans ],
             [ Word3, Word3Trans ] ]

def make_image_dir(Data, Args, SourceDir, TargetDir):
    ImageDir = image_dir(TargetDir)
    lara_utils.create_directory_if_it_doesnt_exist(ImageDir)
    ( NFiles, NCopied ) = ( 0, 0 )    
    for Line in Data:
        #( Letter, LetterSound, LetterImage, Word1, Word1Sound, Word1Image, Word2, Word2Sound, Word2Image ) = Line
        #for File in ( LetterImage, Word1Image, Word2Image ):
        Images = get_images_from_line(Line, Args)
        for File in get_images_from_line(Line, Args):
            if not lara_utils.is_null_string_or_spaces(File):
                NFiles += 1
                ToFile = File.split('/')[-1]
                Result = lara_utils.copy_file(f'{SourceDir}/{File}', f'{ImageDir}/{ToFile}')
                if Result == False:
                    lara_utils.print_and_flush(f'*** Warning: unable to copy image file {File}')
                else:
                    NCopied += 1
    lara_utils.print_and_flush(f'--- Copied {NCopied}/{NFiles} files')
    return

#letter	letter sound file	letter image file	word1	tr1	soundword1	image word1	word2		soundword2	image word2	word3		soundword3	image word3																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																	
#ا	Sounds/Letters/1.m4a	LetterIndex/'alif.jpeg	أَسَد	lion	Sounds/Words/أسد.m4a	WordImages/lion.jpeg	غُراب	crow	Sounds/words/غراب.m4a	WordImages/crow.jpeg	بانْدا	panda	Sounds/Words/.m4a	WordImages/panda.jpeg																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																	

def get_images_from_line(Line, Args):
    Format = Args['format']
    if Format == 'letter_word_word_no_translations':
        ( Letter, LetterSound, LetterImage, Word1, Word1Sound, Word1Image, Word2, Word2Sound, Word2Image ) = Line
        return ( LetterImage, Word1Image, Word2Image )
    elif Format == 'letter_word_word_word_translations':
        ( Letter, LetterSound, LetterImage,
          Word1, Word1Trans, Word1Sound, Word1Image,
          Word2, Word2Trans, Word2Sound, Word2Image,
          Word3, Word3Trans, Word3Sound, Word3Image ) = Line
        return ( LetterImage, Word1Image, Word2Image, Word3Image )
    else:
        lara_utils.print_and_flush(f'*** Error: unknown format: "{Format}"')
        return False

def make_audio_dirs(Data, Args, SourceDir, TargetDir):
    Format = Args['format']
    WordAudioDir = word_audio_dir(Args, TargetDir)
    lara_utils.create_directory_if_it_doesnt_exist(WordAudioDir)
    ( MetadataToInstall, NFiles, NCopied ) = ( [], 0, 0 )
    NMissing = check_for_missing_audio_files(Data, Args, SourceDir)
    #if NMissing != 0: return
    Warnings = []
    for Line in Data:
        TextsAndAudioFiles = get_texts_and_audio_files_from_line(Line, Args)
        for ( Text, File ) in TextsAndAudioFiles:
            if lara_utils.is_null_string_or_spaces(File):
                continue
            NFiles += 1
            if not lara_utils.file_exists(f'{SourceDir}/{File}'):
                lara_utils.print_and_flush(f'*** Warning: file not found: {File}')
                Warnings += [ f'*** Warning: file not found: {File}' ]
            else:
                Result = copy_or_transform_audio_file(File, SourceDir, WordAudioDir)
                if Result == False:
                    lara_utils.print_and_flush(f'*** Warning: unable to transform audio file {File}')
                    Warnings += [ f'*** Warning: unable to transform audio file {File}' ]
                else:
                    NCopied += 1
                    MetadataToInstall += [ { 'text': Text, 'file': base_mp3_version_of_file(File) } ]
    lara_utils.print_and_flush(f'--- Copied/transformed {NCopied}/{NFiles} files')
##    if len(Warnings) != 0:
##        lara_utils.print_and_flush(f'*** {len(Warnings)} warnings:')
##        for Line in Warnings:
##            lara_utils.print_and_flush(Line)
    OldMetadata = lara_audio.read_ldt_metadata_file(WordAudioDir)
    UpdatedMetadata = lara_install_audio_zipfile.clean_audio_metadata(OldMetadata + MetadataToInstall)
    lara_audio.write_ldt_metadata_file(UpdatedMetadata, WordAudioDir)
    lara_utils.print_and_flush(f'--- Updated metadata file in {WordAudioDir} from downloaded metadata file')
    return

def check_for_missing_audio_files(Data, Args, SourceDir):
    Missing = 0
    ExistingFiles = existing_base_audio_files(Data, Args, SourceDir)
    lara_utils.print_and_flush(f'--- Found {len(ExistingFiles)} audio files')
    for Line in Data:
        for ( Text, File ) in get_texts_and_audio_files_from_line(Line, Args):
            if not lara_utils.is_null_string_or_spaces(File):
                BaseFile = base_part_of_pathname(File)
                if not BaseFile in ExistingFiles:
                    Missing += 1
                    ClosestFile = closest_match_in_list(BaseFile, ExistingFiles)
                    lara_utils.print_and_flush(f'--- Warning: "{File}" not found. Closest match: "{ClosestFile}"')
    return Missing

def existing_base_audio_files(Data, Args, SourceDir):
    Dirs = lara_utils.remove_duplicates([ f'{SourceDir}/{directory_part_of_pathname(File)}' 
                                          for Line in Data
                                          for ( Text, File ) in get_texts_and_audio_files_from_line(Line, Args)
                                          if lara_utils.is_null_string_or_spaces(File) ])
    return lara_utils.remove_duplicates( [ File for Dir in Dirs for File in lara_utils.file_members_of_directory(Dir) ] )

def base_part_of_pathname(File):
    return File.split('/')[-1]

def directory_part_of_pathname(File):
    Components = File.split('/')
    return '' if len(Components) == 1 else '/'.join(Components[:-1])

def closest_match_in_list(Str, Strs):
    StrsAndDistances = [ ( Str1, lara_utils.word_edit_distance(Str, Str1) ) for Str1 in Strs ]
    StrsAndDistancesSorted = sorted(StrsAndDistances, key=lambda x: x[1])
    return StrsAndDistancesSorted[0][0]

def get_texts_and_audio_files_from_line(Line, Args):
    Format = Args['format']
    if Format == 'letter_word_word_no_translations':
        ( Letter, LetterSound, LetterImage, Word1, Word1Sound, Word1Image, Word2, Word2Sound, Word2Image ) = Line
        return ( ( Letter, LetterSound ), ( Word1, Word1Sound ), ( Word2, Word2Sound ) )
    elif Format == 'letter_word_word_word_translations':
        ( Letter, LetterSound, LetterImage,
          Word1, Word1Trans, Word1Sound, Word1Image,
          Word2, Word2Trans, Word2Sound, Word2Image,
          Word3, Word3Trans, Word3Sound, Word3Image ) = Line
        return ( ( Letter, LetterSound ), ( Word1, Word1Sound ), ( Word2, Word2Sound ), ( Word3, Word3Sound ) )
    else:
        lara_utils.print_and_flush(f'*** Error: unknown format: "{Format}"')
        return False

def base_mp3_version_of_file(File):
    BaseFile = File.split('/')[-1]
    ( Plain, Ext ) = lara_utils.file_to_base_file_and_extension(BaseFile)
    return f'{Plain}.mp3'

def copy_or_transform_audio_file(File, SourceDir0, WordAudioDir):
    Params = lara_config.default_params()
    FileComponents = File.split('/')
    if len(FileComponents) == 1:
        ( SourceDir, BaseFile ) = ( SourceDir0, File )
    else:
        ( FileDir, BaseFile ) = ( '/'.join(FileComponents[:-1]), FileComponents[-1] )
        SourceDir = f'{SourceDir0}/{FileDir}'
    ( AbsSourceDir, AbsWordAudioDir ) = ( lara_utils.absolute_file_name(SourceDir), lara_utils.absolute_file_name(WordAudioDir) )
    return lara_install_audio_zipfile.convert_lara_audio_directory_file_to_mp3(BaseFile, AbsSourceDir, AbsWordAudioDir, Params)

def make_corpus_file(Data, Args, SourceDir, TargetDir):
    CorpusDir = corpus_dir(TargetDir)
    lara_utils.create_directory_if_it_doesnt_exist(CorpusDir)
    CorpusFile = corpus_file(Args, TargetDir)
    ImageDir = image_dir(TargetDir)
    PageTexts = [ make_corpus_page(Line, Args, SourceDir) for Line in Data ]
    AllText = '\n\n<page>'.join(PageTexts)
    lara_utils.write_lara_text_file(AllText, CorpusFile)
    lara_utils.print_and_flush(f'--- Created corpus file ({len(PageTexts)} letters) {CorpusFile}')                   
    return

def make_corpus_page(Line, Args, SourceDir):
    Format = Args['format']
    if Format == 'letter_word_word_no_translations':
        return make_corpus_page_letter_word_word_no_translations(Line, Args, SourceDir)
    elif Format == 'letter_word_word_word_translations':
        return make_corpus_page_letter_word_word_word_translations(Line, Args, SourceDir)

def make_corpus_page_letter_word_word_no_translations(Line, Args, SourceDir):
    ( Letter, LetterSound, LetterImage, Word1, Word1Sound, Word1Image, Word2, Word2Sound, Word2Image ) = Line
    ( LetterImageWidth, LetterImageHeight ) = lara_utils.size_of_image(f'{SourceDir}/{LetterImage}')
    ( Word1ImageWidth, Word1ImageHeight ) = image_size_for_layout(f'{SourceDir}/{Word1Image}', Args)
    ( Word2ImageWidth, Word2ImageHeight ) = image_size_for_layout(f'{SourceDir}/{Word2Image}', Args)
    ( LetterImage1, Word1Image1, Word2Image1 ) = ( LetterImage.split('/')[-1], Word1Image.split('/')[-1], Word2Image.split('/')[-1] )
    Lines = [ f'<h2>{Letter}||</h2>',
              f'<img src="{LetterImage1}" width="{LetterImageWidth}" height="{LetterImageHeight}"/>||\n',
              f'<img src="{Word1Image1}" width="{Word1ImageWidth}" height="{Word1ImageHeight}"/> @{Word1}@||\n',
              f'<img src="{Word2Image1}" width="{Word2ImageWidth}" height="{Word2ImageHeight}"/> @{Word2}@||' ]
    return '\n'.join(Lines)

def make_corpus_page_letter_word_word_word_translations(Line, Args, SourceDir):
    ( Letter, LetterSound, LetterImage,
      Word1, Word1Sound, Word1Trans, Word1Image,
      Word2, Word2Trans, Word2Sound, Word2Image,
      Word3, Word3Trans, Word3Sound, Word3Image ) = Line
    ( LetterImageWidth, LetterImageHeight ) = lara_utils.size_of_image(f'{SourceDir}/{LetterImage}')
    ImageAndWord1 = make_image_and_word_for_page(Word1, Word1Image, Args, SourceDir)
    ImageAndWord2 = make_image_and_word_for_page(Word2, Word2Image, Args, SourceDir)
    ImageAndWord3 = make_image_and_word_for_page(Word3, Word3Image, Args, SourceDir)
    LetterImage1 = LetterImage.split('/')[-1]
    Lines = [ f'<h2>{Letter}||</h2><table>',
              f'   <tr>',
              f'       <td><annotated_image><img src="{LetterImage1}" width="{LetterImageWidth}" height="{LetterImageHeight}"/> @{Letter}@||</annotated_image></td>',
              f'       <td>{ImageAndWord1}</td>',
              f'   </tr>',
              f'   <tr>',
              f'       <td>{ImageAndWord2}</td>',
              f'       <td>{ImageAndWord3}</td>',
              f'   </tr>',
              f'</table>' ]
    return '\n'.join(Lines)

def make_image_and_word_for_page(Word, WordImage, Args, SourceDir):
    if lara_utils.is_null_string_or_spaces(Word) or lara_utils.is_null_string_or_spaces(WordImage):
        return ''
    else:
        ( WordImageWidth, WordImageHeight ) = image_size_for_layout(f'{SourceDir}/{WordImage}', Args)
        WordImage1 = WordImage.split('/')[-1]
        return f'<img src="{WordImage1}" width="{WordImageWidth}" height="{WordImageHeight}"/><br> @{Word}@||'

def image_size_for_layout(Image, Args):
    ( Width0, Height0 ) = lara_utils.size_of_image(Image)
    if 'image_width' in Args:
        return ( Args['image_width'], int( Height0 * Args['image_width'] / Width0 ) )
    elif 'image_height' in Args:
        return ( int( Width0 * Args['image_height'] / Height0 ), Args['image_height'] )
    else:
        return ( Width0, Height0 )

def image_dir(TargetDir):
    return f'{TargetDir}/images'

def segment_translation_spreadsheet(Args, TargetDir):
    Language = Args['language']
    return f'{TargetDir}/translations/{Language}_english.csv'

def word_translation_spreadsheet(Args, TargetDir):
    Language = Args['language']
    return f'{TargetDir}/translations/{Language}_english_type.csv'

def config_file(TargetDir):
    return f'{TargetDir}/corpus/local_config.json'

def word_audio_dir(Args, TargetDir):
    Language = Args['language']
    Id = Args['id']
    return f'$LARA/Content/{Language}/audio/for_{Id}'

def segment_audio_dir(Args, TargetDir):
    Id = Args['id']
    return f'{TargetDir}/audio/for_{Id}'

def corpus_dir(TargetDir):
    return f'{TargetDir}/corpus'

def corpus_file(Args, TargetDir):
    Id = Args['id']
    return f'{TargetDir}/corpus/{Id}.txt'

def word_locations_file(TargetDir):
    return f'{TargetDir}/corpus/word_locations.json'

# ----------------------------------------------------

def make_simple_alphabet_book(CSVFile, ImageDir, GeneratedCorpusFile):
    Lines = lara_utils.read_lara_csv(CSVFile)
    if Lines == False:
        return
    CoverLine = Lines[0]
    PageLines = Lines[1:]
    CoverText = generate_from_simple_alphabet_book_cover_line(CoverLine, ImageDir)
    PageTexts = [ generate_from_simple_alphabet_book_line(Line, ImageDir) for Line in PageLines
                  if Line[0] != '' and not Line[0].isspace() ]
    MainText = '\n'.join(lara_utils.concatenate_lists([ CoverText ] + PageTexts))
    lara_utils.write_lara_text_file(MainText, GeneratedCorpusFile)
    lara_utils.print_and_flush(f'--- Written generated file ({len(PageTexts)} letters) {GeneratedCorpusFile}')

def generate_from_simple_alphabet_book_cover_line(Line, ImageDir):
    if len(Line) < 3 :
        lara_utils.print_and_flush(f'*** Warning: ignoring bad cover line {Line}')
        return []
    if Line[0] == '' or Line[0].isspace():
        lara_utils.print_and_flush(f'*** Warning: no cover line')
        return []
    ( Title, Subheading, ImageFile ) = Line[:3]
    FullImageFile = f'{ImageDir}/{ImageFile}'
    Size = lara_utils.size_of_image(FullImageFile)
    if Size == False:
        lara_utils.print_and_flush(f'*** Warning: unable to get size of file {FullImageFile}')
        return []
    ( Width, Height ) = Size                                
    return [ f'<h1>/*{Title}*/||</h1>',
             f'<img src="{ImageFile}" width="{Width}" height="{Height}"/>',
             f'/*{Subheading}*/||',
             ''
             ]

def generate_from_simple_alphabet_book_line(Line, ImageDir):
    if len(Line) < 3 or len(Line) > 4:
        lara_utils.print_and_flush(f'*** Warning: ignoring bad line {Line}')
        return []
    elif len(Line) == 3 or len(Line) == 4 and ( Line[3] == '' or Line[3].isspace() ):
        return generate_from_simple_alphabet_book_3_line(Line, ImageDir)
    else:
        return generate_from_simple_alphabet_book_4_line(Line, ImageDir)

## B	<b>b</b>icykel	bicykel.png																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																													
## 
## <h2>/*B*/||</h2>
## <table>
##    <tr>
##        <td><b>b</b>icykel</td>
##        <td><annotated_image><img src="bicykel.png" width="509" height="366"/>bicykel||</annotated_image></td>
##    </tr>
## </table>
                                 
def generate_from_simple_alphabet_book_3_line(Line, ImageDir):
    ( Letter0, BoldedWord, ImageFile ) = Line[:3]
    Letter = comment_out_one_version_if_letter_in_two_forms(Letter0)
    PlainWord = lara_parse_utils.remove_html_annotations_from_string(BoldedWord)[0]
    FullImageFile = f'{ImageDir}/{ImageFile}'
    Size = lara_utils.size_of_image(FullImageFile)
    if Size == False:
        lara_utils.print_and_flush(f'*** Warning: unable to get size of file {FullImageFile}')
        return ''
    ( Width, Height ) = Size                                
    return [ f'<page><h2>{Letter}||</h2>',
             f'<table>',
             f'   <tr>',
             f'       <td>{BoldedWord}||</td>',
             f'       <td><annotated_image><img src="{ImageFile}" width="{Width}" height="{Height}"/>{PlainWord}||</annotated_image></td>',
             f'   </tr>',
             f'</table>',
             f''
             ]

## Á	pot<b>á</b>pač	potápač.png	Á.png																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																												
## 
## <page>
## <h2>/*Á*/||</h2>
## <table>
##    <tr>
##        <td> </td>
##        <td><annotated_image><img src="Á.png" width="157" height="139"/>Á</annotated_image></td>
##    </tr>
##    <tr>
##        <td>pot<b>á</b>pač</td>
##        <td><annotated_image><img src="potápač.png" width="288" height="150"/>potápač||</annotated_image></td>
##    </tr>
## </table>

def generate_from_simple_alphabet_book_4_line(Line, ImageDir):
    ( Letter, BoldedWord, ImageFile1, ImageFile2 ) = Line[:4]
    Letter = comment_out_one_version_if_letter_in_two_forms(Letter0)
    PlainWord = lara_parse_utils.remove_html_annotations_from_string(BoldedWord)[0]
    FullImageFile1 = f'{ImageDir}/{ImageFile1}'
    Size1 = lara_utils.size_of_image(FullImageFile1)
    if Size1 == False:
        lara_utils.print_and_flush(f'*** Warning: unable to get size of file {FullImageFile1}')
        return ''
    ( Width1, Height1 ) = Size1
    FullImageFile2 = f'{ImageDir}/{ImageFile2}'
    Size2 = lara_utils.size_of_image(FullImageFile2)
    if Size2 == False:
        lara_utils.print_and_flush(f'*** Warning: unable to get size of file {FullImageFile2}')
        return ''
    ( Width2, Height2 ) = Size2     
    return [ f'<page>',
             f'<h2>{Letter}||</h2>',
             f'<table>',
             f'   <tr>',
             f'       <td> </td>',
             f'       <td><annotated_image><img src="{ImageFile2}" width="{Width2}" height="{Height2}"/>{Letter}||</annotated_image></td>',
             f'   </tr>',
             f'   <tr>',
             f'       <td>{BoldedWord}</td>',
             f'       <td><annotated_image><img src="{ImageFile1}" width="{Width1}" height="{Height1}"/>{PlainWord}||</annotated_image></td>',
             f'   </tr>',
             f'</table>',
             f''
             ]

def comment_out_one_version_if_letter_in_two_forms(Letter):
    Components = Letter.split()
    if len(Components) > 1:
        return f'{Components[0]} /*{" ".join(Components[1:])}*/'
    else:
        return Letter
    
