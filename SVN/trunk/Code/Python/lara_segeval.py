
import segeval
import lara_split_and_clean
import lara_config
import lara_utils

def test(Id):
    if Id == 'rimbaud_gold_standard':
        AlignmentFile = '$LARA/Content/les_poètes_de_sept_ans/corpus/les_poètes_de_sept_ans_alignments_gold_standard.json'
        CorpusFile = '$LARA/Content/les_poètes_de_sept_ans/corpus/les_poètes_de_sept_ans_segmented_gold_standard.txt'
        alignment_file_gold_standard_items_to_corpus_file(AlignmentFile, CorpusFile)
    if Id == 'rimbaud_similarity':
        CorpusFile1 = '$LARA/Content/les_poètes_de_sept_ans/corpus/les_poètes_de_sept_ans_segmented.txt'
        CorpusFile2 = '$LARA/Content/les_poètes_de_sept_ans/corpus/les_poètes_de_sept_ans_segmented_gold_standard.txt'
        corpus_file_segmentation_similarity(CorpusFile1, CorpusFile2)
    if Id == 'maupassant_gold_standard':
        AlignmentFile = '$LARA/Content/la_parure2/corpus/la_parure_alignments_gold_standard.json'
        CorpusFile = '$LARA/Content/la_parure2/corpus/la_parure_segmented_gold_standard.txt'
        alignment_file_gold_standard_items_to_corpus_file(AlignmentFile, CorpusFile)
    if Id == 'maupassant_similarity':
        CorpusFile1 = '$LARA/Content/la_parure2/corpus/la_parure_segmented.txt'
        CorpusFile2 = '$LARA/Content/la_parure2/corpus/la_parure_segmented_gold_standard.txt'
        corpus_file_segmentation_similarity(CorpusFile1, CorpusFile2)
    if Id == 'flaubert_gold_standard':
        AlignmentFile = '$LARA/Content/un_coeur_simple2/corpus/un_coeur_simple_alignments_gold_standard.json'
        CorpusFile = '$LARA/Content/un_coeur_simple2/corpus/un_coeur_simple_segmented_gold_standard.txt'
        alignment_file_gold_standard_items_to_corpus_file(AlignmentFile, CorpusFile)
    if Id == 'flaubert_similarity':
        CorpusFile1 = '$LARA/Content/un_coeur_simple2/corpus/un_coeur_simple_segmented.txt'
        CorpusFile2 = '$LARA/Content/un_coeur_simple2/corpus/un_coeur_simple_segmented_gold_standard.txt'
        corpus_file_segmentation_similarity(CorpusFile1, CorpusFile2)
    if Id == 'proust_gold_standard':
        AlignmentFile = '$LARA/Content/combray/corpus/combray_align_postediting_gold_standard.json'
        CorpusFile = '$LARA/Content/combray/corpus/combray_segmented_gold_standard.txt'
        alignment_file_gold_standard_items_to_corpus_file(AlignmentFile, CorpusFile)
    if Id == 'proust_similarity':
        CorpusFile1 = '$LARA/Content/combray/corpus/combray_segmented_from_aligner_segmented.txt'
        CorpusFile2 = '$LARA/Content/combray/corpus/combray_segmented_gold_standard.txt'
        corpus_file_segmentation_similarity(CorpusFile1, CorpusFile2)

##  Format for Chris Fournier's segeval package.
##  https://buildmedia.readthedocs.org/media/pdf/segeval/stable/segeval.pdf
##
##    {
##        'items": {
##            "stargazer": {
##                "1": [2,3,3,1,3,6,3],
##                "2": [2,8,2,4,2,3],
##                "3": [2,1,2,3,1,3,1,3,2,2,1],
##                "4": [2,1,4,1,1,3,1,4,3,1],
##                "5": [3,2,4,3,5,4],
##                "6": [2,3,4,2,2,5,3],
##                "7": [2,3,2,2,3,1,3,2,3]
##                }
##            },
##        "segmentation_type": "linear"
##        }

def corpus_file_segmentation_similarity(CorpusFile1, CorpusFile2):
    Params = lara_config.default_params()
    TmpFile = lara_utils.get_tmp_json_file(Params)
    AbsTmpFile = lara_utils.absolute_file_name(TmpFile)
    Segmentation1 = corpus_file_to_segmentation_sequence(CorpusFile1, Params)
    Segmentation2 = corpus_file_to_segmentation_sequence(CorpusFile2, Params)
    if Segmentation1 == False or Segmentation2 == False:
        return
    lara_utils.print_and_flush(f'--- Internalised {CorpusFile1}, {len(Segmentation1)} segments')
    lara_utils.print_and_flush(f'--- Internalised {CorpusFile2}, {len(Segmentation2)} segments')
    SegEvalData = { 'items': {
                        'data_id': {
                            '1': Segmentation1,
                            '2': Segmentation2
                            }
                        },
                    'segmentation_type': 'linear' }
    lara_utils.write_json_to_file(SegEvalData, TmpFile)
    SegevalDataset = segeval.input_linear_mass_json(TmpFile)
    SegevalSegmentation1 = SegevalDataset['data_id']['1']
    SegevalSegmentation2 = SegevalDataset['data_id']['2']
    Score = float(segeval.boundary_similarity(SegevalSegmentation1, SegevalSegmentation2))
    lara_utils.print_and_flush(f'--- Segeval boundary similarity score: {Score:.3f}')
    return Score

def corpus_file_to_segmentation_sequence(CorpusFile, Params):
    Text = lara_utils.read_lara_text_file(CorpusFile)
    if Text == False:
        return False
    Segments = Text.split('||')
    Result = [ segment_to_number_of_words(Segment) for Segment in Segments ]
    if len(Result) != 0:
        AvLength = sum(Result) / len(Result)
        lara_utils.print_and_flush(f'--- Av. segment length: {AvLength:5.1f} ({CorpusFile})')
    return Result

def segment_to_number_of_words(Segment):
    Pairs = lara_split_and_clean.string_to_annotated_words(Segment)[0]
    return len( [ Pair for Pair in Pairs if Pair[1] != '' ] )

# ------------------------------------------

def alignment_file_gold_standard_items_to_corpus_file(AlignmentFile, CorpusFile):
    Items = get_gold_standard_items(AlignmentFile)
    if Items == False:
        return
    AnnotatedSegments = [ Item['text'] for Item in Items ]
    Text = '||'.join(AnnotatedSegments)
    lara_utils.write_lara_text_file(Text, CorpusFile)
    return

def get_gold_standard_items(AlignmentFile):
    Content = lara_utils.read_json_file(AlignmentFile)
    if Content == False or not isinstance(Content, ( dict )):
        lara_utils.print_and_flush(f'*** Error: could not read {AlignmentFile} as dict')
        return False
    if not 'gold_standard' in Content:
        lara_utils.print_and_flush(f'*** Error: "gold_standard" item not found in {AlignmentFile}')
        return False
    if not isinstance(Content['gold_standard'], ( list )):
        lara_utils.print_and_flush(f'*** Error: "gold_standard" item in {AlignmentFile} not a list')
        return False
    Items = Content['gold_standard']
    for Item in Items:
        if not isinstance(Item, dict) \
           or not 'audio_file' in Item or not 'text' in Item or not 'translation' in Item:
            lara_utils.print_and_flush(f'*** Error: bad item {Item} in {AlignmentFile}')
            return False
    return Items
