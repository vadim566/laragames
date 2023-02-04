# Stick together crowdsourced Polish Little Prince

import lara_crowdsource
import lara_config
import lara_utils

_PLP_master_config = '/export/data/www/LARA-data/615_Mały_Książe/corpus/local_config.json'
_PLP_spreadsheet = '$LARA/Content/polish_little_prince/corpus/PolishLittlePrince.csv'
_PLP_ordered_list_of_configs_file = '$LARA/Code/Python/polish_little_prince_configs.json'
																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																				
def stick_together_polish_little_prince():
    if not lara_utils.file_exists(_PLP_ordered_list_of_configs_file):
        print_and_flush(f'*** Error: unable to find list of config files {_PLP_ordered_list_of_configs_file}')
        return False
    if not lara_utils.file_exists(_PLP_master_config):
        print_and_flush(f'*** Error: unable to find master config file {_PLP_master_config}')
        return False
    else:
        lara_crowdsource.stick_together_projects(_PLP_ordered_list_of_configs_file, _PLP_master_config)

#UserName  ContentName  WordLdtTaskID  SegmentLdtTaskID  ContentStatus  WebAddress  localConfigFile
    
def make_ordered_list_of_configs_file():
    Lines = lara_utils.read_lara_csv(_PLP_spreadsheet)[1:]
    TaggedLines = [ tag_spreadsheet_line(Line) for Line in Lines ]
    if False in TaggedLines:
        return False
    RelevantLines = [ TaggedLine for TaggedLine in TaggedLines if TaggedLine['WebAddress'] != 'NULL' ]
    SortedLines = sorted(RelevantLines, key=lambda x: chapter_number_for_line(x))
    ListOfChapterNumbers = [ str(chapter_number_for_line(Line)) for Line in SortedLines ]
    OrderedConfigFiles = [ Line['localConfigFile'] for Line in SortedLines ]
    lara_utils.write_json_to_file_plain_utf8(OrderedConfigFiles, _PLP_ordered_list_of_configs_file)
    ChaptersStr = ", ".join(ListOfChapterNumbers)
    NChapters = len(ListOfChapterNumbers)
    lara_utils.print_and_flush(f'--- Written list of config files, chapters {ChaptersStr} ({NChapters} chapters)')
    return True

def tag_spreadsheet_line(Line):
    if len(Line) < 7:
        print_and_flush(f'*** Error: bad line: {Line}')
        return False
    ( UserName, ContentName, WordLdtTaskID, SegmentLdtTaskID, ContentStatus, WebAddress, localConfigFile ) = Line[:7]
    return { 'UserName': UserName,
             'ContentName': ContentName,
             'WordLdtTaskID': WordLdtTaskID,
             'SegmentLdtTaskID': SegmentLdtTaskID,
             'ContentStatus': ContentStatus,
             'WebAddress': WebAddress,
             'localConfigFile': localConfigFile }

# Typical ContentName: Mały Książę-ch22
def chapter_number_for_line(Line):
    ContentName = Line['ContentName']
    DigitsString = ''.join([ Digit for Digit in ContentName if Digit.isdigit() ])
    return lara_utils.safe_string_to_int(DigitsString)
