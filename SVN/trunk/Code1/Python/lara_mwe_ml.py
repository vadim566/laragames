
import lara_utils

def test_mwe_annotations_file_to_ml_data(Id):
    if Id == 'alice':
        InFile = '$LARA/Content/alice_in_wonderland/corpus/alice_in_wonderland_mwe_annotations_plain.json'
        OutFile = '$LARA/Content/alice_in_wonderland/corpus/alice_in_wonderland_mwe_ml.json'
        mwe_annotations_file_to_ml_data(InFile, OutFile)

def mwe_annotations_file_to_ml_data(InFile, OutFile):
    if not lara_utils.file_exists(InFile):
        lara_utils.print_and_flush(f'*** Error: file not found: {InFile}')
        return False
    InData = lara_utils.read_json_file(InFile)
    if not InData or not isinstance(InData, list):
        lara_utils.print_and_flush(f'*** Error: unable to read {InFile} as JSON list')
        return False
    else:
        lara_utils.print_and_flush(f'--- Read annotations file, {len(InData)} records: {InFile}')
    OutData = [ mwe_annotation_to_ml_data(Record) for Record in InData ]
    lara_utils.write_json_to_file(OutData, OutFile)
    lara_utils.print_and_flush(f'--- Written ML data file, {len(OutData)} records: {OutFile}')
    return True

def mwe_annotation_to_ml_data(Record):
    if not is_mwe_annotation_record(Record):
        lara_utils.print_and_flush(f'*** Error: file not found: {InFile}')
        return False
    return { Feature: mwe_annotation_record_to_feature(Feature, Record) for Feature in _mwe_features }

_mwe_features = [ 'gloss',
                  'status',
                  'mwe_name',
                  'mwe_pos',
                  'mwe_length',
                  'n_words_skipped',
                  'pos1',
                  'pos2',
                  'pos3',
                  'pos4',
                  'pos5',
                  'pos_before',
                  'pos_skipped1',
                  'pos_skipped2',
                  'pos_skipped3',
                  'pos_after' ]

def mwe_annotation_record_to_feature(Feature, Record):
    if Feature == 'gloss':
        return mwe_record_to_gloss(Record)
    elif Feature == 'status':
        return mwe_record_to_status(Record)
    elif Feature == 'mwe_name' :
        return mwe_record_to_mwe_name(Record)
    elif Feature == 'mwe_pos' :
        return mwe_record_to_mwe_pos(Record)
    elif Feature == 'mwe_length' :
        return mwe_record_to_mwe_length(Record)
    elif Feature == 'n_words_skipped' :
        return mwe_record_to_n_words_skipped(Record)
    elif Feature == 'pos1' :
        return mwe_record_to_pos1(Record)
    elif Feature == 'pos2' :
        return mwe_record_to_pos2(Record)
    elif Feature == 'pos3' :
        return mwe_record_to_pos3(Record)
    elif Feature == 'pos4' :
        return mwe_record_to_pos4(Record)
    elif Feature == 'pos5' :
        return mwe_record_to_pos5(Record)
    elif Feature == 'pos_before' :
        return mwe_record_to_pos_before(Record)
    elif Feature == 'pos_skipped1' :
        return mwe_record_to_pos_skipped1(Record)
    elif Feature == 'pos_skipped2' :
        return mwe_record_to_pos_skipped2(Record)
    elif Feature == 'pos_skipped3' :
        return mwe_record_to_pos_skipped3(Record)
    elif Feature == 'pos_after' :
        return mwe_record_to_pos_after(Record)
    else:
        lara_utils.print_and_flush(f'*** Error: unknown feature {Feature}')
        return False

def is_mwe_annotation_record(Record):
    return isinstance(Record, dict) and \
           'match' in Record and 'mwe' in Record and 'pos' in Record and 'skipped' in Record \
           and 'word_index_list' and 'words' in Record

##    {
##        "match": "So she was considering in her own mind *as* *well* as she could for the hot day made her feel very sleepy and stupid whether the pleasure of making a daisy chain would be worth the trouble of getting up and picking the daisies",
##        "mwe": "as well",
##        "ok": "mwe_not_okay",
##        "pos": "ADV",
##        "skipped": 0,
##        "word_index_list": [
##            8,
##            9
##        ],
##        "words": [
##            [
##                "So",
##                "ADV"
##            ],

def mwe_record_to_gloss(Record):
    return emphasized_words_str_and_index_list_to_gloss(Record['match'], Record['word_index_list'])

def emphasized_words_str_and_index_list_to_gloss(EmphasizedWordsStr, IndexList):
    EmphasizedWords = EmphasizedWordsStr.split()
    FirstIndex = IndexList[0] - 1 if IndexList[0] > 0 else 0
    LastIndex = IndexList[-1] + 2 
    return ' '.join(EmphasizedWords[FirstIndex:LastIndex])
  
def mwe_record_to_status(Record):
    return 'positive' if Record['ok'] == 'mwe_okay' else 'negative'

def mwe_record_to_mwe_name(Record):
    return Record['mwe']

def mwe_record_to_mwe_pos(Record):
    return Record['pos']

def mwe_record_to_mwe_length(Record):
    return len(Record['word_index_list'])

def mwe_record_to_n_words_skipped(Record):
    return Record['skipped']

def mwe_record_to_pos1(Record):
    return mwe_record_to_pos_for_indexed_word(Record, 0)

def mwe_record_to_pos2(Record):
    return mwe_record_to_pos_for_indexed_word(Record, 1)

def mwe_record_to_pos3(Record):
    return mwe_record_to_pos_for_indexed_word(Record, 2)

def mwe_record_to_pos4(Record):
    return mwe_record_to_pos_for_indexed_word(Record, 3)

def mwe_record_to_pos5(Record):
    return mwe_record_to_pos_for_indexed_word(Record, 4)

def mwe_record_to_pos_before(Record):
    IndexList = Record['word_index_list']
    return pos_for_index_in_record(Record, IndexList[0] - 1)

def mwe_record_to_pos_skipped1(Record):
    SkippedIndices = skipped_indices(Record)
    return pos_for_index_in_record(Record, SkippedIndices[0]) if len(SkippedIndices) > 0 else '*null*'

def mwe_record_to_pos_skipped2(Record):
    SkippedIndices = skipped_indices(Record)
    return pos_for_index_in_record(Record, SkippedIndices[1]) if len(SkippedIndices) > 1 else '*null*'

def mwe_record_to_pos_skipped3(Record):
    SkippedIndices = skipped_indices(Record)
    return pos_for_index_in_record(Record, SkippedIndices[2]) if len(SkippedIndices) > 2 else '*null*'

def mwe_record_to_pos_after(Record):
    IndexList = Record['word_index_list']
    return pos_for_index_in_record(Record, IndexList[-1] + 1)

def mwe_record_to_pos_for_indexed_word(Record, I):
    IndexList = Record['word_index_list']
    Words = Record['words']
    return pos_for_index_in_record(Record, IndexList[I]) if len(IndexList) > I else '*null*'

def pos_for_index_in_record(Record, I):
    Words = Record['words']
    return Words[I][1] if 0 <= I and I < len(Words) else '*null*'

def skipped_indices(Record):
    ( Indices, SkippedIndices ) = ( Record['word_index_list'], [] )
    for I in range(0, len(Indices) - 1 ):
        SkippedIndices += list(range(Indices[I] + 1, Indices[I + 1]))
    return SkippedIndices

