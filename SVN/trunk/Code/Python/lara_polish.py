# Code to access the Polish tools for LARA tagging and lemmatisation. Used in lara_treetagger.py

import lara_config
import lara_parse_utils
import lara_utils
import os
import sys

def morfeusz_and_concraft_are_available():
    # Comment this in to make Morfeusz and Concraft unavailable
    #return False
    M = morfeusz_is_available()
    C = concraft_is_available()
    return M and C

def morfeusz_is_available():
    # We might be calling Morfeusz through another version of Python
    if 'MORFEUSZPYTHON' in os.environ:
        return True
    else:
        try:
            from morfeusz2 import Morfeusz
            return True
        except Exception as e:
            lara_utils.print_and_flush(f'*** Warning: Morpheusz not found')
            lara_utils.print_and_flush(f'*** Warning: If you are using Polish, you are advised to install Morpheusz and Concraft')
            return False

def concraft_is_available():
    try:
        from concraft_pl2 import Concraft, Server
        return True
    except Exception as e:
        lara_utils.print_and_flush(f'*** Warning: Concraft Python module not found')
        lara_utils.print_and_flush(f'*** Warning: If you are using Polish, you are advised to install Morpheusz and Concraft')
        return False

def check_concraft_server_status(ConfigFile, ReplyFile):
    Status = get_concraft_server_status(ConfigFile)
    lara_utils.write_lara_text_file(Status, ReplyFile)

def get_concraft_server_status(ConfigFile):
    if not morfeusz_and_concraft_are_available():
        return '*** Error: not installed'
    if not init_polish_resources_if_necessary():
        return '*** Error: unable to initialise'
    Str = 'tak'
    try:
        Params = lara_config.read_lara_local_config_file(ConfigFile)
        dag = invoke_morfeusz_on_string(Str, Params)
    except Exception as e:
        return '*** Error: unable to run Morfeusz2'
    try:
        if dag == False:
            return '*** Error: unable to run Morfeusz2'
        disamb = concraft.disamb(dag)
        return 'Okay'
    except Exception as e:
        return '*** Error: Concraft server appears to be down'

def invoke_polish_pipeline_for_lara_tagging_and_lemmatisation(FileIn, FileOut, Params):
    try:
        return invoke_polish_pipeline_for_lara_tagging_and_lemmatisation1(FileIn, FileOut, Params)
    except Exception as e:
        lara_utils.print_and_flush(f'*** Error: something went wrong when sending {FileIn} for Polish tagging and lemmatisation')
        lara_utils.print_and_flush(str(e))
        return False
        
def invoke_polish_pipeline_for_lara_tagging_and_lemmatisation1(FileIn, FileOut, Params):
    lara_utils.delete_file_if_it_exists(FileOut)
    Str = lara_utils.read_lara_text_file(FileIn)
    Dag = invoke_morpheusz_concraft_pipeline_on_string(Str, Params)
    if Dag != False:
        format_concraft_dag_to_file(Dag, FileOut)
        lara_utils.print_and_flush(f'--- Sent {FileIn} ({len(Str)} chars) for Polish tagging and lemmatisation, producing {FileOut}')
        return FileOut
    else:
        lara_utils.print_and_flush(f'*** Error: something went wrong when sending {FileIn} for Polish tagging and lemmatisation')
        return False

##    >>> from morfeusz2 import Morfeusz
##    >>> from concraft_pl2 import Concraft, Server
##    >>> morfeusz = Morfeusz(expand_tags=True)
##    >>> concraft = Concraft()
##    >>> dag = morfeusz.analyse('W Szczebrzeszynie chrząszcz brzmi w trzcinie.')
##    >>> dag_disamb = concraft.disamb(dag)

morfeusz = False
concraft = False

def init_polish_resources_if_necessary():
    global morfeusz
    global concraft
    try:
        if morfeusz != False:
            lara_utils.print_and_flush(f'--- Morpheusz appears to be available')
        elif 'MORFEUSZPYTHON' in os.environ:
            morfeusz = 'run_externally'
            lara_utils.print_and_flush(f"--- Morpheusz will be run under {os.environ['MORFEUSZPYTHON']}")
        else:
            from morfeusz2 import Morfeusz
            morfeusz = Morfeusz(expand_tags=True)

        if concraft != False:
            lara_utils.print_and_flush(f'--- Concraft appear to be loaded')
        else:
            from concraft_pl2 import Concraft, Server
            concraft = Concraft()
        
        if morfeusz != False and concraft != False:
            return True
        else:                       
            if morfeusz == False or concraft == False:
                lara_utils.print_and_flush(f'*** Error: unable to initiate Morpheusz and Concraft')
                return False
            else:
                return True
    except Exception as e:
        lara_utils.print_and_flush(f'*** Error: something went wrong when trying to initiate Morpheusz and Concraft')
        lara_utils.print_and_flush(str(e))
        return False

def invoke_morpheusz_concraft_pipeline_on_string(Str, Params):
    global morfeusz
    global concraft
    Initiated = init_polish_resources_if_necessary()
    if not Initiated:
        return False
    dag = invoke_morfeusz_on_string(Str, Params)
    return concraft.disamb(dag)

def invoke_morfeusz_on_string(Str, Params):
    if morfeusz == 'run_externally':
        return invoke_morfeusz_on_string_externally(Str, Params)
    else:
        return morfeusz.analyse(Str, Params)

def invoke_morfeusz_on_string_externally(Str, Params):
    Python = os.environ['MORFEUSZPYTHON']
    InFile = lara_utils.get_tmp_trace_file(Params)
    OutFile = lara_utils.get_tmp_json_file(Params)
    lara_utils.write_lara_text_file(Str, InFile)
    Command = f'{Python} $LARA/Code/Python/lara_run_morfeusz.py {InFile} {OutFile}'
    Code = lara_utils.execute_lara_os_call(Command, Params)
    if Code == 0 and lara_utils.file_exists(OutFile):
        Result = lara_utils.read_json_file(OutFile)
        lara_utils.print_and_flush(f'--- Successfully called Morfeusz through {Python}')
        return Result
    else:
        lara_utils.print_and_flush(f'*** Error: something went wrong when calling Morfeusz through {Python}')
        return False
    

##    [(0, 1, ('W', 'w', 'prep:acc:nwok', [], []), '0.0000', None, None),
##     (0, 1, ('W', 'w', 'prep:loc:nwok', [], []), '1.0000', None, 'disamb'),
##     (1,
##      2,
##      ('Szczebrzeszynie',
##       'Szczebrzeszyn',
##       'subst:sg:loc:m3',
##       ['nazwa_geograficzna'],
##       []),
##      '1.0000',
##      None,
##      'disamb'),
##     (1,
##      2,
##      ('Szczebrzeszynie',
##       'Szczebrzeszyn',
##       'subst:sg:voc:m3',
##       ['nazwa_geograficzna'],
##       []),
##      '0.0000',
##      None,
##      None),
##     (2,
##      3,
##      ('chrząszcz', 'chrząszcz', 'subst:sg:nom:m2', ['nazwa_pospolita'], []),
##      '1.0000',
##      None,
##      'disamb'),
##     (3,
##      4,
##      ('brzmi', 'brzmieć:v1', 'fin:sg:ter:imperf', [], []),
##      '1.0000',
##      None,
##      'disamb'),

def format_concraft_dag_to_file(Dag, File):
    SelectedRecords = select_disambiguated_records_from_dag(Dag)
    CompactedRecords = join_past_tenses_to_agglutinative_affixes_where_possible(SelectedRecords)
    format_concraft_dag_to_file1(CompactedRecords, File)

def select_disambiguated_records_from_dag(Dag0):
    Dag = extract_normal_concraft_records_from_dag(Dag0)
    if not Dag:
        lara_utils.print_and_flush(f'*** Error: Concraft output does not appear to be a well-formed DAG')
        return False
    ( SelectedRecords, CurrentFrom, CurrentTo, CurrentRecord, CurrentRecordDisamb ) = ( [], 0, 0, False, False )
    for Record in Dag:
        ( From, To, MorphInfo, Score, Extra, Disamb ) = Record
        # We've got a new segment which starts at the end of the current one.
        # Add current record to output.
        if From == CurrentTo:
            if CurrentRecord != False:
                SelectedRecords += [ CurrentRecord ]
            ( CurrentFrom, CurrentTo, CurrentRecord ) = ( From, To, Record )
            CurrentRecordDisamb = True if Disamb == 'disamb' else False
        # We have a new version of the current segment marked as 'disamb'. This is the right one.
        elif From == CurrentFrom and Disamb == 'disamb':
            ( CurrentTo, CurrentRecord, CurrentRecordDisamb ) = ( To, Record, True )
        # We have a new version of the current segment not marked as 'disamb',
        # but we haven't seen a 'disamb' yet this segment. Mark this record for now as the one to use.
        elif From == CurrentFrom and CurrentRecordDisamb != True:
            ( CurrentTo, CurrentRecord ) = ( To, Record )
        # Otherwise ignore this record.
    # We've reached the end, add current record to output if there is one.
    if CurrentRecord != False:
        SelectedRecords += [ CurrentRecord ]
    return SelectedRecords

def join_past_tenses_to_agglutinative_affixes_where_possible(Records):
    ( I, N, OutList ) = ( 0, len(Records), [] )
    while True:
        if I >= N:
            return OutList
        elif I == N - 1:
            OutList += [ Records[I] ]
            return OutList
        # 'mógł' + 'by' + 'm' = 'mógłbym'
        elif I + 2 < N and \
             past_tense_record(Records[I]) and \
             by_particle_record(Records[I + 1]) and \
             agglutinative_affix_record(Records[I + 2]):
            NewRecord = combine_past_tense_by_and_affix(Records[I], Records[I + 2])
            OutList += [ NewRecord ]
            I += 3
        # 'miał' + 'by' = 'miałby'
        elif I + 1 < N and \
             past_tense_record(Records[I]) and \
             by_particle_record(Records[I + 1]):
            NewRecord = combine_past_tense_and_affix(Records[I], Records[I + 1])
            OutList += [ NewRecord ]
            I += 2
        # 'miał' + 'em' = 'miałem'  
        elif past_tense_record(Records[I]) and \
             agglutinative_affix_record(Records[I + 1]):
            NewRecord = combine_past_tense_and_affix(Records[I], Records[I + 1])
            OutList += [ NewRecord ]
            I += 2
        else:
            OutList += [ Records[I] ]
            I += 1

##    (1,
##     2,
##      ('miał', 'mieć', 'praet:sg:m1:imperf', [], []),
##      '1.0000',
##      None,
##      'disamb'),
##     (2,
##      3,
##      ('em', 'być', 'aglt:sg:pri:imperf:wok', [], []),
##      '1.0000',
##      None,
##      'disamb'),

def past_tense_record(Record):
    return isinstance(Record, ( list, tuple )) and \
           len(Record) >= 3 and \
           isinstance(Record[2], ( list, tuple )) and \
           len(Record[2]) >= 3 and \
           (  Record[2][2].split(':')[-1] in ( 'imperf', 'perf' ) or \
              Record[2][2].split(':')[-2:] == [ 'imperf', 'nagl' ] )

# (2, 3, ('by', 'by:q', 'part', [], []), '1.0000', None, 'disamb'),
def by_particle_record(Record):
    return isinstance(Record, ( list, tuple )) and \
           len(Record) >= 3 and \
           isinstance(Record[2], ( list, tuple )) and \
           len(Record[2]) >= 3 and \
           Record[2][0] == 'by' and \
           Record[2][2] == 'part'

def agglutinative_affix_record(Record):
    return isinstance(Record, ( list, tuple )) and \
           len(Record) >= 3 and \
           isinstance(Record[2], ( list, tuple )) and \
           len(Record[2]) >= 3 and \
           Record[2][2].split(':')[0] == 'aglt'

def combine_past_tense_and_affix(Record1, Record2):
    return ( Record1[0],                      # 1
             Record2[1],                      # 3
             ( Record1[2][0] + Record2[2][0], # 'miał' + 'em' 
               Record1[2][1],                 # 'mieć'
               Record1[2][2],                 # 'praet:sg:m1:imperf'
               Record1[2][3],                 # []
               Record1[2][4] ),               # []
             Record1[3],                      # '1.0000',
             Record1[4],                      # None
             Record1[5] )                     # 'disamb'
               
def combine_past_tense_by_and_affix(Record1, Record2):
    return ( Record1[0],                             # 1
             Record2[1],                             # 3
             ( Record1[2][0] + 'by' + Record2[2][0], # 'mógł' + 'by' + 'm' = 'mógłbym'
               Record1[2][1],                        # 'mógł'
               Record1[2][2],                        # 'praet:sg:m1:imperf'
               Record1[2][3],                        # []
               Record1[2][4] ),                      # []
             Record1[3],                             # '1.0000',
             Record1[4],                             # None
             Record1[5] )                            # 'disamb'

def extract_normal_concraft_records_from_dag(Dag0):
    if not isinstance(Dag0, list):
        lara_utils.print_and_flush(f'*** Error: Concraft output is not a list')
        return False
    return [ Record for Record in Dag0 if normal_concraft_record(Record) ]

def normal_concraft_record(Record):
    return isinstance(Record, (list, tuple)) and \
           len(Record) == 6 and \
           not lara_parse_utils.is_punctuation_string(Record[0])

def format_concraft_dag_to_file1(SelectedRecords, File):
    FormattedLines = [ format_concraft_record_for_lara(Record) for Record in SelectedRecords ]
    lara_utils.write_lara_text_file('\n'.join(FormattedLines), File)
    return True

##     (3,
##      4,
##      ('brzmi', 'brzmieć:v1', 'fin:sg:ter:imperf', [], []),
##      '1.0000',
##      None,
##      'disamb'),

def format_concraft_record_for_lara(Record):
    if not normal_concraft_record(Record):
        lara_utils.print_and_flush(f'*** Error: unexpected record in Concraft output: {Record}')
        return False
    ( From, To, MorphInfo ) = Record[:3]
    if not isinstance(MorphInfo, (list, tuple)) or len(MorphInfo) < 3:
        lara_utils.print_and_flush(f'*** Error: unexpected morphology info {MorphInfo} in Concraft record: {Record}')
        return False
    ( Surface, Lemma, Tag ) = MorphInfo[:3]
    # If the lemma has a colon in it, discard everything after the colon, e.g. brzmieć:v1 -> brzmieć
    ReducedLemma = Lemma.split(':')[0]
    # Keep only the first part of the morphology tag, e.g. fin:sg:ter:imperf -> fin
    ReducedTag = Tag.split(':')[0]
    return f'{Surface}\t{ReducedTag}\t{ReducedLemma}'

# ------------------------------------------

def reflexive_verb_list_to_mwe_entries(InFile, OutFile):
    Lines = [ Line.lower().strip() for Line in lara_utils.read_lara_text_file(InFile).split('\n')]
    lara_utils.print_and_flush(f'--- Read reflexive verb list, {len(Lines)} unique entries')
    Entries = [ reflexive_verb_line_to_mwe_entry(Line) for Line in Lines ]
    Entries1 = lara_utils.remove_duplicates([ Entry for Entry in Entries if Entry != False ])
    lara_utils.write_lara_text_file('\n'.join(Entries1), OutFile)
    lara_utils.print_and_flush(f'--- Written MWE list, {len(Entries1)} entries')

def reflexive_verb_line_to_mwe_entry(Line):
    Words = Line.split()
    if len(Words) != 2:
        lara_utils.print_and_flush(f'*** Warning: "{Line}" not two words')
        return False
    ( Verb, Particle ) = Words
    Infinitive = polish_verb_to_infinitive(Verb)
    if Infinitive == False:
        return False
    return f'*{Infinitive}* {Particle} | POS:V'

# (0, 1, ('brzmieć', 'brzmieć:v1', 'inf:imperf', [], [])),
        
def polish_verb_to_infinitive(Verb):
    from morfeusz2 import Morfeusz
    morfeusz = Morfeusz(expand_tags=True)
    Dag = morfeusz.analyse(Verb)
    for Record in Dag:
        MorphInfo = Record[2]
        ( Lemma, Tag ) = ( MorphInfo[1], MorphInfo[2] )
        if Tag.split(':')[0] in ( 'fin', 'inf', 'praet' ):
            return Lemma.split(':')[0]
    lara_utils.print_and_flush(f'*** Warning: unable to interpret "{Verb}" as a verb')
    return False

