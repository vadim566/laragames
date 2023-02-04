import lara_translations
import lara_html
import lara_config
import lara_utils

def test(Id):
    if Id == 'genesis_french':
        WordCSV = '$LARA/Content/sample_french/translations/token_french_english.csv'
        LinesPerPage = 5
        MaxLineLength = 10
        ConfigFile = '$LARA/Content/sample_french/corpus/local_config.json'
        HTMLFile = '$LARA/Content/sample_french/translations/token_french_english.html'
        format_word_token_spreadsheet_as_html(WordCSV, LinesPerPage, MaxLineLength, ConfigFile, HTMLFile)
    elif Id == 'huis_clos':
        WordCSV = '$LARA/Content/huis_clos/translations/token_french_english.csv'
        LinesPerPage = 5
        MaxLineLength = 10
        ConfigFile = '$LARA/Content/huis_clos/corpus/local_config.json'
        HTMLFile = '$LARA/Content/huis_clos/translations/token_french_english.html'
        format_word_token_spreadsheet_as_html(WordCSV, LinesPerPage, MaxLineLength, ConfigFile, HTMLFile)
    elif Id == 'antigone_en':
        WordCSV = '$LARA/Content/antigone_en/translations/token_english_french.csv'
        LinesPerPage = 5
        MaxLineLength = 10
        ConfigFile = '$LARA/Content/antigone_en/corpus/local_config_rosa_kirsten.json'
        HTMLFile = '$LARA/Content/antigone_en/translations/token_english_french.html'
        format_word_token_spreadsheet_as_html(WordCSV, LinesPerPage, MaxLineLength, ConfigFile, HTMLFile)

def format_word_token_spreadsheet_as_html(WordCSV, LinesPerPage, MaxLineLength, ConfigFile, HTMLFile):
    DataIn = lara_translations.read_word_token_spreadsheet_file(WordCSV, 'remove_csv_markings')
    DataMarked = mark_csv_lines(DataIn, LinesPerPage, MaxLineLength)
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    Caption = f'Word token translations for {Params.id}'
    Header = [ '' ]
    lara_html.print_lara_html_table(Caption, Header, DataMarked, HTMLFile, Params)

def mark_csv_lines(DataIn, LinesPerPage, MaxLineLength):
    ( OutLines, LineNumber ) = ( [], 0 )
    for Line in DataIn:
        OutLines += mark_csv_line(Line, LineNumber, LinesPerPage, MaxLineLength)
        LineNumber += 1
    return OutLines

def mark_csv_line(Line, LineNumber, LinesPerPage, MaxLineLength):
    if LineNumber % LinesPerPage == 0:
        PageNumber = 1 + int(LineNumber / LinesPerPage)
        PageIntro = [ [ f'<b>*** PAGE {PageNumber} ***</b>' ] ]
    else:
        PageIntro = []      
    Basic = [ [ f'<i>{Element}</i>' for Element in Line[0] ],
              [ f'<b>{Element}</b>' for Element in Line[1] ]
              ]
    return PageIntro + shorten_lines(Basic, MaxLineLength)

def shorten_lines(Pair, MaxLineLength):
    if len(Pair[0]) <= MaxLineLength:
        return Pair
    else:
        First = [ Pair[0][:MaxLineLength], Pair[1][:MaxLineLength] ]
        Rest = shorten_lines( [ Pair[0][MaxLineLength:], Pair[1][MaxLineLength:] ],
                              MaxLineLength )
        return First + Rest
    
                 
