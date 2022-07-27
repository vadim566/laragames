# lara_onp.py

import lara_config
import lara_spell_correct
import lara_utils

# Extract information from ONP Old Norse online lexicon

# 1. Download the index pages from ONP. These have URLs of form
# 
# https://skaldic.abdn.ac.uk/m.php?p=wordch&i=<Number> 
# 
# for <Number>=1 to 37
# 
# 2. Extract the lines which give lexicon entries. Typical examples look like this:
# 
# <li><a data-ajax="false" href="m.php?p=lemma&i=10510">brauð (noun n.) ‘bread’<span class="ui-li-count">5</span></a></li>
# <li><a data-ajax="false" href="m.php?p=lemma&i=10518">brauðgýgr (noun f.)<span class="ui-li-count">1</span></a></li>
# <li><a data-ajax="false" href="m.php?p=lemma&i=10541">brauðsveigir (noun m.)<span class="ui-li-count">1</span></a></li>
# <li><a data-ajax="false" href="m.php?p=lemma&i=10545">1. braut (noun f.) ‘path, way; away’<span class="ui-li-count">51</span></a></li>
# <li><a data-ajax="false" href="m.php?p=lemma&i=10278">1. brá (noun f.) ‘eyelash, eyebrow’<span class="ui-li-count">10</span></a></li>
# 
# 3. Parse lines into <lemma, POS, lexiconURL> triples and store as a dict.

onp_download_dir = '$LARA/Content/oldnorse/corpus/onp_downloaded_index_files'
onp_index_file = '$LARA/Content/oldnorse/corpus/onp_index.json'
onp_base_url = 'https://skaldic.abdn.ac.uk/'
number_of_onp_index_files = 37
edda_words2lemmas_file = '$LARA/Content/oldnorse/corpus/edda_words2lemmas.json'
edda_onp_guesses_spreadsheet = '$LARA/Content/oldnorse/corpus/edda_onp_best_matches.csv'
edda_onp_guesses_spreadsheet_annotated = '$LARA/Content/oldnorse/corpus/edda_onp_best_matches_annotated.csv'
edda_onp_guesses_file = '$LARA/Content/oldnorse/corpus/edda_onp_best_matches.json'

def download_onp_index_files():
    lara_utils.create_directory_if_it_doesnt_exist(onp_download_dir)
    for I in range(1, number_of_onp_index_files + 1):
        URL = f'https://skaldic.abdn.ac.uk/m.php?p=wordch&i={I}'
        File = f'{onp_download_dir}/onp_index_file_{I}.html'
        Result = lara_utils.read_file_from_url(URL, File)
        if Result == False:
            lara_utils.print_and_flush(f'*** Warning: unable to download index file {I} from ONP')
            return
    lara_utils.print_and_flush(f'--- Downloading {number_of_onp_index_files} index files from ONP')
    

def create_onp_index():
    DownloadedFiles = [ f'{onp_download_dir}/{File}' for File in lara_utils.file_members_of_directory(onp_download_dir) ]
    RawIndexLines = extract_index_lines_from_onp_files(DownloadedFiles)
    Dict = raw_index_lines_to_onp_dict(RawIndexLines)
    lara_utils.write_json_to_file(Dict, onp_index_file)

def extract_index_lines_from_onp_files(Files):
    List = []
    for File in Files:
        Lines = lara_utils.read_lara_text_file(File).split('\n')
        for Line in Lines:
            if Line.find('<li><a data-ajax="false" href="m.php?p=lemma') >= 0:
                List += [ Line ]
    lara_utils.print_and_flush(f'--- Extracted {len(List)} index lines from {len(Files)} files')
    return List

# <li><a data-ajax="false" href="m.php?p=lemma&i=10510">brauð (noun n.) ‘bread’<span class="ui-li-count">5</span></a></li>
# <li><a data-ajax="false" href="m.php?p=lemma&i=10518">brauðgýgr (noun f.)<span class="ui-li-count">1</span></a></li>
# <li><a data-ajax="false" href="m.php?p=lemma&i=10541">brauðsveigir (noun m.)<span class="ui-li-count">1</span></a></li>
# <li><a data-ajax="false" href="m.php?p=lemma&i=10545">1. braut (noun f.) ‘path, way; away’<span class="ui-li-count">51</span></a></li>
# <li><a data-ajax="false" href="m.php?p=lemma&i=10278">1. brá (noun f.) ‘eyelash, eyebrow’<span class="ui-li-count">10</span></a></li>

def raw_index_lines_to_onp_dict(RawIndexLines):
    Dict = {}
    for Line in RawIndexLines:
        Result = parse_onp_index_line(Line)
        if Result != False:
            ( URL, Lemma, POS, Def ) = Result
            List = Dict[Lemma] if Lemma in Dict else []
            List += [ { 'url': URL, 'pos': POS, 'def': Def } ]
            Dict[Lemma] = List
    return Dict

def parse_onp_index_line(Line):
    Intro = '<li><a data-ajax="false" href="'
    IntroStart = Line.find(Intro)
    if IntroStart < 0:
        return False
    IntroEnd = IntroStart + len(Intro)
    URLFieldEnd = Line.find('">', IntroEnd + 1)
    if URLFieldEnd < 0:
        return False
    URLField = Line[IntroEnd:URLFieldEnd]
    URL = f'{onp_base_url}{URLField}'
    NumberAndWordStart = URLFieldEnd + len('">')
    WordStart = skip_numbers_and_spaces(Line, NumberAndWordStart)
    WordEnd = Line.find(' ', WordStart)
    Word = Line[WordStart:WordEnd]
    LParen = Line.find('(', WordEnd)
    if LParen < 0:
        return False
    POSStart = LParen + len('(')
    RParen = Line.find(')', WordEnd)
    if RParen < 0:
        return False
    POS = Line[POSStart:RParen]
    LQuote = Line.find('‘', RParen + 1)
    RQuote = Line.find('’', RParen + 1)
    Def = Line[LQuote + 1:RQuote] if LQuote > 0 and RQuote > 0 and RQuote > LQuote else ''
    return ( URL, Word, POS, Def )
    
def skip_numbers_and_spaces(Line, Start):
    Index = Start
    while True:
        c = Line[Index]
        if c.isspace() or c == '.' or c in '0123456789':
            Index += 1
        else:
            return Index

# -----------------------------------------

def make_edda_onp_best_guesses_spreadsheet():
    EddaWordsAndLemmasDict = lara_utils.read_json_file(edda_words2lemmas_file)
    ONPDict = lara_utils.read_json_file(onp_index_file)
    EddaWordsWithNoPOS = [ Word for Word in EddaWordsAndLemmasDict
                          if not some_member_of_list_in_dict(EddaWordsAndLemmasDict[Word], ONPDict)]
    EddaLemmas = lara_utils.remove_duplicates([ Lemma for Word in EddaWordsAndLemmasDict for Lemma in EddaWordsAndLemmasDict[Word] ])
    EddaLemmasWithNoPOS = [ Lemma for Lemma in EddaLemmas if not Lemma in ONPDict]
    lara_utils.print_and_flush(f'--- {len(EddaWordsAndLemmasDict)} Edda words')
    lara_utils.print_and_flush(f'--- {len(EddaLemmas)} Edda lemmas')
    lara_utils.print_and_flush(f'--- {len(EddaWordsWithNoPOS)} Edda words with no LP entry')
    lara_utils.print_and_flush(f'--- {len(EddaLemmasWithNoPOS)} Edda lemmas with no LP entry')
    #lara_utils.print_and_flush(EddaLemmasWithNoPOS)
    #lara_utils.prettyprint(EddaWordWithNoPOS)
    init_onp_spell_correct()
    EddaLemmaGuesses = [ [ Lemma ] + list(guess_onp_word(Lemma)) for Lemma in EddaLemmasWithNoPOS ]
    SortedEddaGuesses = sorted(EddaLemmaGuesses, key=lambda x: x[2], reverse=True)
    lara_utils.write_lara_csv(SortedEddaGuesses, edda_onp_guesses_spreadsheet)

def some_member_of_list_in_dict(List, Dict):
    for X in List:
        if X in Dict:
            return True
    return False

def init_onp_spell_correct():
    ONPDict = lara_utils.read_json_file(onp_index_file)
    Vocabulary = [ Key for Key in ONPDict ]
    lara_spell_correct.init_domain_vocabulary_if_necessary('onp', Vocabulary)

def in_onp_vocabulary(Word):
    return lara_spell_correct.in_vocabulary(Word, 'onp')

def guess_onp_word(Word):
    if in_onp_vocabulary(Word):
        return ( Word, 1.0 )
    else:
        return lara_spell_correct.guess_oov_word(Word, 'onp')

# -----------------------------------------

def make_edda_onp_best_guesses_file():
    SpreadsheetData = lara_utils.read_lara_csv(edda_onp_guesses_spreadsheet_annotated)
    Dict = edda_onp_best_guesses_annotated_data_to_dict(SpreadsheetData)
    lara_utils.write_json_to_file(Dict, edda_onp_guesses_file)

# suðrænn	suðrœnn	0.8571428571	yes																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																												
# spágandr	gandr	625	no	c																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																											

def edda_onp_best_guesses_annotated_data_to_dict(SpreadsheetData):
    Dict = {}
    for Line in SpreadsheetData:
        ( Edda, ONP, Score0, Annotation0, Compound0 )  = Line[:5]
        Annotation = normalise_annotation(Annotation0)
        Compound = normalise_compound(Compound0)
        Score = normalise_score(Score0)
        Dict[Edda] = { 'onp_best_match': ONP,
                       'score': float(Score),
                       'correct_match': Annotation,
                       'compound': Compound }
    return Dict

def normalise_annotation(Annotation):
    Annotation1 = Annotation.lower()
    if Annotation1 == 'yes' :
        return 'yes'
    elif Annotation1 == '':
        return 'unclear'
    elif Annotation1 in ( 'no', 'nono', '1no' ):
        return 'no'
    else:
        lara_utils.print_and_flush(f'*** Warning: unknown annotation: "{Annotation}"')
        return 'unclear'

def normalise_compound(Compound):
    if Compound.lower() == 'c':
        return True
    elif Compound == '':
        return False
    else:
        lara_utils.print_and_flush(f'*** Warning: unknown compound annotation: "{Compound}"')
        return False
    
def normalise_score(Score0):
    Score = float(Score0)
    if Score < 1:
        return Score
    elif 100 < Score and Score < 1000:
        lara_utils.print_and_flush(f'*** Warning: suspicious score adjusted: "{Score}"')
        return Score / 1000
    else:
        lara_utils.print_and_flush(f'*** Error: unknown score: "{Score}"')



        
