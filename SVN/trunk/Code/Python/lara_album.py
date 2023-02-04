import lara_utils
from PIL import Image, ImageDraw, ImageFilter

# Initial exercise: use PIL to manipulate the images in the ÍTM vasaorðabók.

_ITM_book_items = [
    ['detta_sign.jpg', 'detta'],
    ['klæða_sig_sign.jpg', 'klæða sig'],
    ['bíða_sign.jpg', 'bíða'],
    ['gefa_sign.jpg', 'gefa'],
    ['heimsækja_sign.jpg', 'heimsækja'],
    ['lesa_sign.jpg', 'lesa'],
    ['taka_til_sign.jpg', 'taka til'],
    ['synda_sign.jpg', 'synda'],
    ['lalla_sign.jpg', 'lalla'],
    ['fara_sign.jpg', 'fara'],
    ['langa_sign.jpg', 'langa'],
    ['renna_sér_sign.jpg', 'renna sér'],
    ['gera_sign.jpg', 'gera'],
    ['hætta_sign.jpg', 'hætta'],
    ['ná_í_sign.jpg', 'ná í'],
    ['brjóta_sign.jpg', 'brjóta'],
    ['hjóla_sign.jpg', 'hjóla'],
    ['hlaupa_sign.jpg', 'hlaupa'],
    ['róla_sign.jpg', 'róla'],
    ['smakka_sign.jpg', 'smakka'],
    ['sparka_sign.jpg', 'sparka'],
    ['standa_upp_sign.jpg', 'standa upp'],
    ['sitja_sign.jpg', 'sitja'],
    ['ganga_sign.jpg', 'ganga'],
    ['teikna_sign.jpg', 'teikna']
    ]

_ImageDir = '$LARA/Content/ítm_vasaorðabók/images'

_LocationsFileOld = '$LARA/Content/ítm_vasaorðabók/corpus/ítm_vasaorðabók_sign_word_locations.json'

_LocationsFileNew = '$LARA/Content/ítm_vasaorðabók/corpus/ítm_vasaorðabók_combined_word_locations.json'

_PictureScale = 0.4

def make_combined_ITM_files():
    LocationDictOld = lara_utils.read_json_file(_LocationsFileOld)
    LocationDictNew = {}
    for ( SignFileShort, Word ) in _ITM_book_items:
        make_combined_ITM_image(SignFileShort, Word, LocationDictOld, LocationDictNew, _PictureScale)
    lara_utils.write_json_to_file_plain_utf8(LocationDictNew, _LocationsFileNew)

def make_combined_ITM_image(SignFileShort, Word, LocationDictOld, LocationDictNew, PictureScale):
    Dir = lara_utils.absolute_file_name(_ImageDir)
    SignFileBase = lara_utils.base_name_for_pathname(SignFileShort)
    SignName = '_'.join(SignFileBase.split('_')[:-1])
    SignFileShort = f'{SignName}_sign.jpg'
    SignFile = f'{Dir}/{SignFileShort}'
    CombinedFileShort = f'{SignName}_combined.jpg'
    CombinedFile = f'{Dir}/{CombinedFileShort}'
    PictureFile = f'{Dir}/{SignName}_image.jpg'
    BlankFile = f'{Dir}/blank.jpg'
    if not lara_utils.check_files_exist([ SignFile, PictureFile, BlankFile ]):
        return
    SignImage = Image.open(SignFile)
    PictureImage = Image.open(PictureFile)
    BlankImage = Image.open(BlankFile)
    BlankImage1 = BlankImage.copy()

    ( SignWidth, SignHeight ) = SignImage.size
    ( PictureWidth, PictureHeight ) = PictureImage.size

    ( ResizedPictureWidth, ResizedPictureHeight ) = ( int(PictureWidth * PictureScale), int(PictureHeight * PictureScale) )
                        
    PictureImage = PictureImage.resize( ( ResizedPictureWidth, ResizedPictureHeight ) )

    BlankImage1.paste(SignImage, (0, 0))

    ResizedPictureTopLeft = ( int( 0.5 * ( SignWidth - ResizedPictureWidth )), SignHeight + 5)
    ResizedPictureBottomRight = ( ResizedPictureTopLeft[0] + ResizedPictureWidth, ResizedPictureTopLeft[1] + ResizedPictureHeight )

    BlankImage1.paste(PictureImage, ResizedPictureTopLeft)

    BlankImage1.save(CombinedFile, quality=95)
    lara_utils.print_and_flush(f'--- Written file: {CombinedFile}')
    add_combined_location_information(SignFileShort, CombinedFileShort, Word,
                                      ResizedPictureTopLeft, ResizedPictureBottomRight,
                                      LocationDictOld, LocationDictNew)

def add_combined_location_information(SignFileShort, CombinedFileShort, Word,
                                      ResizedPictureTopLeft, ResizedPictureBottomRight,
                                      LocationDictOld, LocationDictNew):
    if not SignFileShort in LocationDictOld:
        lara_utils.print_and_flush(f'*** Warning: no location found for {SignFileShort}')
        return
    LocationInfoOld = LocationDictOld[SignFileShort]
    LocationInfoForPicture = [ [ Word, ResizedPictureTopLeft, ResizedPictureBottomRight ],
                               [ 'SPEAKER-CONTROL', [ "", "" ], [ "", "" ] ],
                               [ 'TRANSLATION-CONTROL', [ "", "" ], [ "", "" ] ] ]
    LocationInfoNew = LocationInfoOld + [ LocationInfoForPicture ]
    LocationDictNew[CombinedFileShort] = LocationInfoNew
    
