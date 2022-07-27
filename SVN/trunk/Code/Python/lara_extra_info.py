
import lara_audio
import lara_translations
import lara_drama
import lara_html
import lara_utils
import lara_parse_utils

def add_audio_and_translation_to_line(Line, MinimallyCleaned, Context, Params):
    #lara_utils.print_and_flush(f'--- add_audio_and_translation_to_line((...), "{MinimallyCleaned}", (...))')
    if Params.plain_text == 'yes' or Line.isspace():
        return ( Line, [] )
    else:
        LoudspeakerIcon = loudspeaker_icon_html_code(Params)
        TranslationIcon = translation_icon_html_code(Params)
        ( AudioURL, AudioErrors ) = get_audio_url_for_line_or_add_to_errors(MinimallyCleaned, Context, Params)
        ( Translation, TranslationErrors) = get_translation_for_line_or_add_to_errors(MinimallyCleaned, Params)
        Control = audio_and_translation_control_for_line(LoudspeakerIcon, TranslationIcon, AudioURL, MinimallyCleaned, Translation, Params)
        #lara_utils.print_and_flush(f'{Control} = audio_and_translation_control_for_line({LoudspeakerIcon}, {Line}, {TranslationIcon}, {AudioURL}, {Translation}, <Params>')
        Result = ( f'{Line} {Control}', AudioErrors + TranslationErrors )
        #lara_utils.print_and_flush(f'--- {Result}')
        return Result

def get_audio_url_for_line_or_add_to_errors(MinimallyCleaned, Context, Params):
    if MinimallyCleaned.isspace() or MinimallyCleaned == '':
        return ( '*no_audio_url*', [] )
    elif Params.audio_segments == 'no' or lara_audio.no_audio('segments', Params):
        return ( '*no_audio_url*', [] )
    else:
        AudioURL = lara_audio.get_audio_url_for_chunk_or_word(MinimallyCleaned, Context, 'segments', Params)
        if AudioURL and Params.video_annotations == 'yes':
            PopupURL = create_signed_video_popup_page(AudioURL, Params)
            return ( PopupURL, [] )
        elif AudioURL:
            return ( AudioURL, [] )
        elif lara_drama.is_non_spoken_line(MinimallyCleaned, Params) == True:
            return ( '*no_audio_url*', [] )
        elif Context == '':
            return ( '*no_audio_url*', [ f'*** Warning: unable to add audio for "{MinimallyCleaned}"' ] )
        else:
            return ( '*no_audio_url*', [ f'*** Warning: unable to add audio for "{MinimallyCleaned}" (context: "{Context}"' ] )

def get_translation_for_line_or_add_to_errors(MinimallyCleaned, Params):
    if MinimallyCleaned.isspace() or MinimallyCleaned == '':
        return ( '*no_translation*', [] )
    elif Params.segment_translation_mouseover == 'no':
        return ( '*no_translation*', [] )
    elif lara_translations.no_segment_translations(lara_utils.get_corpus_id_from_params(Params)):
        return ( '*no_translation*', [] )
    else:
        CorpusId = lara_utils.get_corpus_id_from_params(Params)
        if lara_translations.translation_for_segment(MinimallyCleaned, CorpusId):
            return ( lara_translations.translation_for_segment(MinimallyCleaned, CorpusId), [] )
        else:
            return ( '*no_translation*', [ f'*** Warning: unable to add translation for "{MinimallyCleaned}"' ] )

def audio_and_translation_control_for_line(LoudspeakerIcon, TranslationIcon, AudioURL, Line, Translation, Params):
    QuotLine = Line.replace("\"", "&quot;")
    QuotTranslation = Translation.replace("\"", "&quot;")
    if TranslationIcon:
        return separate_audio_and_translation_controls_for_line(LoudspeakerIcon, TranslationIcon, AudioURL, QuotLine, QuotTranslation, Params)
    # No audio, no translation
    if lara_audio.null_audio_url(AudioURL) and Translation == '*no_translation*':
        return ''
    # No audio, translation
    if lara_audio.null_audio_url(AudioURL):
        if Params.segment_translation_as_popup == 'no':
            Page = page_for_non_popup_segment_translation_create_if_necessary(QuotLine, QuotTranslation, Params)
            LinkTag = link_tag_for_non_popup_segment_translation(Page, Params)
            return f'{LinkTag}{LoudspeakerIcon}</a>'
        else:
            return f'<span title="{QuotTranslation}">{LoudspeakerIcon}</span>'
    # No translation, audio
    if Translation == '*no_translation*' and Params.video_annotations != 'yes':
        return f'<span onclick="playSound(\'{AudioURL}\');" onmouseover="" style="cursor: pointer;">{LoudspeakerIcon}</span>'
    # No translation, popup video
    if Translation == '*no_translation*' and Params.video_annotations == 'yes':
        return f"<span style=\"cursor: pointer;\" onclick=\"window.open('{AudioURL}','newWin','width=640,height=480')\">{LoudspeakerIcon}</span>"
    # Popup video and translation
    if Params.video_annotations == 'yes':
        return f"<span style=\"cursor: pointer;\" title=\"{QuotTranslation}\" onclick=\"window.open('{AudioURL}','newWin','width=640,height=480')\">{LoudspeakerIcon}</span>"
    # Audio and translation
    else:
        if Params.segment_translation_as_popup == 'no':
            Page = page_for_non_popup_segment_translation_create_if_necessary(QuotLine, QuotTranslation, Params)
            LinkTag = link_tag_for_non_popup_segment_translation(Page, Params)
            return f'{LinkTag}<span class="sound" onclick="playSound(\'{AudioURL}\');">{LoudspeakerIcon}</span></a>'
        return f'<span class="sound" onclick="playSound(\'{AudioURL}\');" title="{QuotTranslation}">{LoudspeakerIcon}</span>'

def separate_audio_and_translation_controls_for_line(LoudspeakerIcon, TranslationIcon, AudioURL, Line, Translation, Params):
    QuotTranslation = Translation.replace("\"", "&quot;")
    if lara_audio.null_audio_url(AudioURL) or Params.audio_segments == 'no':
        AudioControl = '' 
    elif Params.video_annotations != 'yes':
        AudioControl = f'<span onclick="playSound(\'{AudioURL}\');" onmouseover="" style="cursor: pointer;">{LoudspeakerIcon}</span>'
    else:
        AudioControl= f"<span onclick=\"window.open('{AudioURL}','newWin','width=640,height=480')\" style=\"cursor: pointer;\">{LoudspeakerIcon}</span>"
    if Translation == '*no_translation*' or Params.segment_translation_mouseover == 'no':
        TranslationControl = ''
    elif Params.segment_translation_as_popup == 'no':
        Page = page_for_non_popup_segment_translation_create_if_necessary(Line, Translation, Params)
        LinkTag = link_tag_for_non_popup_segment_translation(Page, Params)
        TranslationControl = f'{LinkTag}{TranslationIcon}</a>'
    else:
        TranslationControl = f'<span title="{QuotTranslation}">{TranslationIcon}</span>'
    Result = f'{AudioControl}{TranslationControl}'
    return Result

non_popup_segment_translations = {}

def init_pages_for_non_popup_segment_translations():
    non_popup_segment_translations = {}

def page_for_non_popup_segment_translation_create_if_necessary(Line, Translation, Params):
    # Remove punctuation marks and take first five words
    Translation1 = ' '.join(lara_parse_utils.remove_punctuation_marks(Translation).split()[:5])
    Index = 0
    while True:
        Suffix = '' if Index == 0 else f'_{Index}'
        ShortFile = f'{Translation1}{Suffix}'
        if not ShortFile in non_popup_segment_translations or non_popup_segment_translations[ShortFile] == Translation:
            non_popup_segment_translations[ShortFile] = Translation
            #MediumFile = f'multimedia/{ShortFile}.html'
            MediumFile = f'{lara_utils.relative_multimedia_dir(Params)}/{ShortFile}.html'
            FullFile = f'{Params.word_pages_directory}/{MediumFile}'
            write_out_non_popup_segment_translation_file(Line, Translation, FullFile, Params)
            return MediumFile
        else:
            Index += 1

def write_out_non_popup_segment_translation_file(Line, Translation, FullFile, Params):
    Header = lara_html.segment_translation_lines_header(Params)
    Arrow = translation_arrow_html_code(Params)
    Body = [ f'{Line} {Arrow} <br>',
             f'{Translation}</p>' ]
    Closing = lara_html.segment_translation_lines_closing(Params)
    AllLines = Header + Body + Closing
    lara_utils.write_lara_text_file('\n'.join(AllLines), FullFile)

def link_tag_for_non_popup_segment_translation(FileName, Params):
    ScreenName = lara_utils.split_screen_pane_name_for_word_page_screen(Params)
    return f'<a href="{FileName}" target="{ScreenName}">'

# --------------------------------------

def create_signed_video_popup_page(VideoURL, Params):
    Extension = lara_utils.extension_for_file(VideoURL)
    Lines = [ '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">',
              '<html>',
              '<head>',
              '<meta content="text/html;charset=ISO-8859-1" http-equiv="Content-Type">',
              '<title>Popup</title>',
              '</head>',
              '<body style="background-color: rgb(256, 256, 256);">',
              '',
              f'<video width="640" height="480" controls autoplay muted/>',
              f'  <source src="{VideoURL}" type="video/{Extension}">',
              f'  Your browser does not support the video tag.',
              f'</video>'
              '</body>',
              '</html>'
              ]
    Text = '\n'.join(Lines)
    RelativePopupFileName = get_video_popup_file_name(VideoURL)
    AbsolutePopupFileName = f'{Params.word_pages_directory}/{RelativePopupFileName}'
    lara_utils.write_lara_text_file(Text, AbsolutePopupFileName)
    return RelativePopupFileName

def get_video_popup_file_name(VideoURL):
    BaseName = lara_utils.base_name_for_pathname(VideoURL)
    return lara_utils.change_extension(BaseName, 'html')

# --------------------------------------

def loudspeaker_icon_html_code(Params):
    if Params.video_annotations == 'yes':
        # movie camera
        return '&#x1f3a5;'
    elif Params.text_direction == 'rtl':
        # left-to-right loudspeaker
        return '&#x1f50a;'
    else:
        # left-to-right loudspeaker
        return '&#x1f50a;'    

def translation_icon_html_code(Params):
    Char = Params.segment_translation_character
    if Char == '':
        return False
    else:
        Codepoint = ord(Char)
        return '&#{:d};'.format(Codepoint)

def arrow_html_code(Params):
    if Params.text_direction == 'rtl':
        # arrow pointing right
        return '&rarr;'
    else:
        # arrow pointing left
        return '&larr;'

def previous_arrow_html_code(Params):
    if Params.text_direction == 'rtl':
        # arrow pointing right
        #return '&#x1F81A;'
        return '&#9654;'
    else:
        # arrow pointing left
        #return '&#x1F818;'
        return '&#9664;'

def next_arrow_html_code(Params):
    if Params.text_direction == 'rtl':
        # arrow pointing right
        #return '&#x1F818;'
        return '&#9664;'
    else:
        # arrow pointing left
        #return '&#x1F81A;'
        return '&#9654;'

def up_arrow_html_code(Params):
        return '&#9650;'

def translation_arrow_html_code(Params):
    if Params.text_direction == 'rtl':
        # arrow pointing left
        return '&larr;'
    else:
        # arrow pointing right
        return '&rarr;'

# --------------------------------------
                        
def maybe_add_translation_and_or_audio_mouseovers_to_word(Word, Lemma, Translation, WordContext, Params):
    AudioURL = audio_url_for_word_and_word_context(Word, WordContext, Params)
    if Params.translation_mouseover == 'yes' and Params.audio_mouseover != 'no' and Translation and AudioURL != '*no_audio_url*':
        return add_translation_and_audio_mouseovers_to_word(Word, Translation, AudioURL, Params)
    elif Params.translation_mouseover == 'yes' and Translation:
        return add_translation_mouseover_to_word(Word, Translation)
    elif Params.audio_mouseover != 'no':
        return lara_audio.add_audio_mouseover_to_word(Word, Word, Params)
    else:
        return Word

def audio_url_for_word_and_word_context(Word, WordContext, Params):
    if Params.audio_mouseover == 'no' or \
       lara_audio.params_say_to_use_extracted_audio(Params) and WordContext == '*non_current_word_on_word_page*':
        return '*no_audio_url*'
    else:
        return lara_audio.get_audio_url_for_word(Word, Params) 

def add_translation_and_audio_mouseovers_to_word(Word, Translation, AudioURL, Params):
    AudioMouseover = Params.audio_mouseover
    QuotTranslation = Translation.replace("\"", "&quot;")
    Trigger = 'onclick' if Params.audio_on_click == 'yes' else 'onmouseover'
    #PlaySoundCall = '' if AudioURL == '*no_audio_url*' or AudioURL == False else f'playSound(\'{AudioURL}\');'
    PlaySoundCall = lara_audio.construct_play_sound_call_for_word(AudioURL, Params)
##    if AudioMouseover == 'yes':
##        return f'<span title="{Translation}" onmouseover="{PlaySoundCall}">{Word}</span>'  
##    if AudioMouseover == 'both':
##        return f'<span title="{Translation}" ontouchstart="{PlaySoundCall}" onmouseover="{PlaySoundCall}">{Word}</span>'
    if AudioMouseover != 'no':
        #return f'<span title="{Translation}" {Trigger}="{PlaySoundCall}" ontouchstart="{PlaySoundCall}">{Word}</span>'
        return f'<span class="sound" title="{QuotTranslation}" {Trigger}="{PlaySoundCall}">{Word}</span>'
    else:
        return f'<span title="{QuotTranslation}">{Word}</span>'  

def add_translation_mouseover_to_word(Word, Translation):
    QuotTranslation = Translation.replace("\"", "&quot;")
    return f'<span title="{QuotTranslation}">{Word}</span>'

# --------------------------------------

def word_page_lines_extra_info_top(Word, Params):
    SignLanguageVideoLines = sign_language_video_lines_for_word(Word, Params)
    Notes = lara_translations.all_notes_for_word(Word)
    PencilHTMLChar = pencil_html_char()
    FormattedNotes = [ f'<p>{PencilHTMLChar}&nbsp;{Note}</p>' for Note in Notes ]
    LanguageSpecificExtraInfo = word_page_lines_language_specific_extra_info(Word, Params)
    Images = lara_translations.all_images_for_word(Word)
    #FormattedImages = [ format_image(Image, Params) for Image in Images ]
    Lines = SignLanguageVideoLines + FormattedNotes + [ '' ] + LanguageSpecificExtraInfo
    return ( Lines, Images )

_width_of_image_in_extra_info = 400

def format_image_for_extra_info(Image, Params):
    ImageSize = lara_utils.size_of_image(f'{Params.image_directory}/{Image}')
    if ImageSize == False:
        return f'<p>(Unable to format image {Image})</p>'
    else:
        ( Width, Height ) = ImageSize
        ( Width1, Height1 ) = ( _width_of_image_in_extra_info, int( Height * _width_of_image_in_extra_info / Width ) )
        return f'<img src="multimedia/{Image}" width="{Width1}" height="{Height1}" />'

def sign_language_video_lines_for_word(Word, Params):
    SignLanguageVideoForWord = lara_audio.sign_language_video_for_word(Word, Params)
    if not SignLanguageVideoForWord:
        return []
    else:
        Extension = lara_utils.extension_for_file(SignLanguageVideoForWord)
        return [ f'<video width="640" height="480" controls muted/>',
                 f'  <source src="{SignLanguageVideoForWord}" type="video/{Extension}">',
                 f'  Your browser does not support the video tag.',
                 f'</video>',
                 ''
                 ]
               
def pencil_html_char():
    return '&#9998;'

def word_page_lines_extra_info_bottom(Word, Params):
    return []

def word_page_lines_language_specific_extra_info(Word, Params):
    Word1 = Word.split('/')[0] if '/' in Word else Word
    if Params.extra_page_info == 'yes' and Params.language == 'icelandic':
        return icelandic_extra_info(Word1)
    if Params.extra_page_info == 'yes' and Params.language == 'oldnorse':
        return icelandic_extra_info(Word1) + old_norse_extra_info(Word1)
    if Params.extra_page_info == 'yes' and Params.language == 'japanese':
        return japanese_extra_info(Word1)
    if Params.extra_page_info == 'yes' and Params.language == 'polish':
        return polish_extra_info(Word1)
    if Params.extra_page_info == 'yes' and Params.language == 'german':
        return german_extra_info(Word1)
    else:
        return []

# --------------------------------------

icelandic_uninflected_words_file = '$LARA/Code/LinguisticData/icelandic/icelandic_uninflected_words.txt'

icelandic_info_initialised = 'no'

icelandic_uninflected_words = {}

def icelandic_uninflected_word_info(Word):
    global icelandic_uninflected_words
    maybe_initialise_icelandic_info()
    if Word in icelandic_uninflected_words:
        return icelandic_uninflected_words[Word]
    else:
        return False

def maybe_initialise_icelandic_info():
    global icelandic_info_initialised
    if icelandic_info_initialised == 'no':
        icelandic_uninflected_words = {}
        AllInfo = get_uninflected_word_info()
        initialise_icelandic_info(AllInfo)
        lara_utils.print_and_flush(f'--- Stored information for {len(AllInfo)} uninflected Icelandic words')
        icelandic_info_initialised = 'yes'

def get_uninflected_word_info():
    global icelandic_uninflected_words_file
    File = icelandic_uninflected_words_file
    if not lara_utils.file_exists(icelandic_uninflected_words_file):
        print(f'*** Warning: unable to find file: {icelandic_uninflected_words_file}')
        return []
    try:
        return lara_utils.read_ascii_text_file_to_lines(File)
    except:
        print(f'*** Warning: unable to read file: {icelandic_uninflected_words_file}')
        return []

def initialise_icelandic_info(AllInfo):
    for Line in AllInfo:
        initialise_icelandic_info_for_line(Line)

def initialise_icelandic_info_for_line(Line):
    global icelandic_uninflected_words
    Line1 = lara_parse_utils.remove_initial_and_final_spaces(Line)
    Components = Line1.split()
    ( Word, Categories ) = ( Components[0], Components[1:] )
    Categories1 = [ convert_icelandic_uninflected_word_category(Category) for Category in Categories ]
    Info = ' '.join([ Word, '-'] + Categories1)
    icelandic_uninflected_words[Word] = Info

# The word classes are
# adverbs (ao, atviksorð),
# preposition (fs, forsetning),
# infinitive particle (nhm, nafnháttarmerki),
# conjunction (st, samtenging),
# numeral (töl, töluorð), 
# exclamations (uh, upphrópun).

icelandic_uninflected_word_categories = {'ao': 'adverb',
                                         'fs': 'preposition',
                                         'nhm': 'infinitive-particle',
                                         'st': 'conjunction',
                                         'töl': 'numeral',
                                         'uh': 'exclamation'}

def convert_icelandic_uninflected_word_category(Cat):
    global icelandic_uninflected_word_categories
    if Cat in icelandic_uninflected_word_categories:
        return icelandic_uninflected_word_categories[Cat]
    else:
        return Cat
    
# --------------------------------------

def icelandic_extra_info(Word):
    UninflectedWordInfo = icelandic_uninflected_word_info(Word)
    if UninflectedWordInfo:
        return [f'<p><b>{UninflectedWordInfo}</b></p>']
    else:
        LookupWord = icelandic_lookup_word_for_word(Word)
        Action = f'window.open(\'http://bin.arnastofnun.is/leit/?q={LookupWord}\', \'newWin\', \'width=800, height=600\')'
        return [f'<p><a href="javascript:void(0)" onclick="{Action}"><b><u>Grammar information</u></b></a></p>']

def icelandic_lookup_word_for_word(Word):
    Components = Word.split()
    if len(Components) == 2 and Components[0] == 'að':
        return Components[1]
    else:
        return Word

# --------------------------------------

def old_norse_extra_info(Word):
    return [ onp_lexicon_information_line_for_URL(URL) for URL in onp_lexicon_urls_for_lemma(Word) ]

def onp_lexicon_information_line_for_URL(URL):
    Action = f'window.open(\'{URL}\', \'newWin\', \'width=1000, height=800\')'
    return f'<p><a href="javascript:void(0)" onclick="{Action}"><b><u>Lexicon poeticum entry</u></b></a></p>'

def onp_lexicon_urls_for_lemma(Word):
    maybe_initialise_old_norse_lexicon_info()
    return onp_lexicon_urls_for_lemma1(Word)

onp_dictionary = {}
old_norse_lexicon_initialised = False

def maybe_initialise_old_norse_lexicon_info():
    import lara_onp
    global onp_dictionary
    global old_norse_lexicon_initialised
    if old_norse_lexicon_initialised == True:
        return
    else:
        onp_dictionary = lara_utils.read_json_file(lara_onp.onp_index_file)
        if onp_dictionary != False:
            old_norse_lexicon_initialised = True

##    "bjalfi": [
##        {
##            "def": "[skin, hide]",
##            "pos": "noun m.",
##            "url": "https://skaldic.abdn.ac.uk/m.php?p=lemma&i=8754"
##        }
##    ],

def onp_lexicon_urls_for_lemma1(Word):
    if Word in onp_dictionary:
       return [ ONPEntry['url'] for ONPEntry in onp_dictionary[Word] ]
    else:
        return []

# --------------------------------------

def japanese_extra_info(Word):
    LookupWord = japanese_lookup_word_for_word(Word)
    Action = f'window.open(\'https://jisho.org/search/{LookupWord}\', \'newWin\', \'width=1200, height=800\')'
    return [f'<a href="javascript:void(0)" onclick="{Action}"><b><u>Jisho.org information</u></b></a>']

def japanese_lookup_word_for_word(Word):
    return Word

# --------------------------------------

def polish_extra_info(Word):
    LookupWord = polish_lookup_word_for_word(Word)
    Action = f'window.open(\'http://sgjp.pl/leksemy/#{LookupWord}\', \'newWin\', \'width=1200, height=800\')'
    return [f'<a href="javascript:void(0)" onclick="{Action}"><b><u>Grammatical Dictionary of Polish information</u></b></a>']

def polish_lookup_word_for_word(Word):
    return Word

# --------------------------------------

# https://www.verbformen.com/?w=anfangen

def german_extra_info(Word):
    LookupWord = german_lookup_word_for_word(Word)
    Action = f'window.open(\'https://www.verbformen.com/?w={LookupWord}\', \'newWin\', \'width=1200, height=800\')'
    return [f'<a href="javascript:void(0)" onclick="{Action}"><b><u>verbformen.com information</u></b></a>']

def german_lookup_word_for_word(Word):
    return Word


# -----------------------------------------------
#
# French
#
# Example for écrire: http://www.french-linguistics.co.uk/verbs/table/%E9crire.html
#
#
# -----------------------------------------------
#
#
# English
# 
# Example for go: http://www.french-linguistics.co.uk/verbs/table/%E9crire.html


