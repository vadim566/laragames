# Initial minimal version of flashcard-generation code

import lara_top
import lara_config
import lara_parse_utils
import lara_utils
import random
from nltk.metrics import distance
import lara_treetagger
import lara_translations
import lara_mwe

# Test on a few LARA texts in the repository (add more later)
def test_make_flashcards(Id):
    # Barngarla
    if Id == 'barngarla':
        ConfigFile = '$LARA/Content/barngarla_alphabet/corpus/local_config.json'
        FlashcardType = 'lemma_translation_ask_l2_audio'
        NCards = 10
        OutFile = '$LARA/tmp_resources/barngarla_flashcards.json'
    # Völuspá old with kenningar
    elif Id == 'völuspá_kenningar':
        ConfigFile = '$LARA/Content/völuspá_20210412/corpus/local_config_kenningar.json'
        FlashcardType = 'token_translation_ask_l2'
        NCards = 20
        OutFile = '$LARA/tmp_resources/völuspá_kenningar_flashcards.json'
    # Völuspá new (downloaded from portal)
    elif Id == 'völuspá':
        ConfigFile = '$LARA/Content/völuspá_new/corpus/local_config.json'
        FlashcardType = 'token_translation_ask_l2'
        NCards = 20
        OutFile = '$LARA/tmp_resources/völuspá_flashcards.json'
    # Völuspá with kenningar, audio question
    elif Id == 'völuspá_kenningar_audio':
        ConfigFile = '$LARA/Content/völuspá/corpus/local_config_kenningar.json'
        FlashcardType = 'token_translation_ask_l2_audio'
        NCards = 10
        OutFile = '$LARA/tmp_resources/völuspá_kenningar_audio_flashcards.json'
    # Small version of Tina with signed video
    elif Id == 'tina_signed_small':
        ConfigFile = '$LARA/Content/tina_signed_small/corpus/local_config.json'
        FlashcardType = 'signed_video_ask_l2'
        NCards = 10
        OutFile = '$LARA/tmp_resources/tina_signed_small_flashcards.json'
    # Tina, plain questions
    elif Id == 'tina':
        ConfigFile = '$LARA/Content/tina_fer_i_fri/corpus/local_config.json'
        FlashcardType = 'lemma_translation_ask_l2'
        NCards = 10
        OutFile = '$LARA/tmp_resources/tina_flashcards.json'
    # Tina, sentences with gaps
    elif Id == 'tina_gaps':
        ConfigFile = '$LARA/Content/tina_fer_i_fri/corpus/local_config.json'
        FlashcardType = 'sentence_with_gap'
        NCards = 10
        OutFile = '$LARA/tmp_resources/tina_with_gaps_flashcards.json'
    # Genesis in Swedish, lemma translations
    elif Id == 'genesis_swedish':
        ConfigFile = '$LARA/Content/sample_swedish/corpus/local_config.json'
        FlashcardType = 'lemma_translation_ask_l2'
        NCards = 10
        OutFile = '$LARA/tmp_resources/genesis_swedish_lemma_translations_flashcards.json'
    # Le petit prince
    elif Id == 'le_petit_prince':
        ConfigFile = '$LARA/Content/le_petit_prince/corpus/local_config.json'
        FlashcardType = 'token_translation_ask_l2'
        NCards = 20
        OutFile = '$LARA/tmp_resources/le_petit_prince_flashcards.json'
    # Antigone
    elif Id == 'antigone':
        ConfigFile = '$LARA/Content/antigone/corpus/local_config_nahed_marta_chadi.json'
        FlashcardType = 'token_translation_ask_l2'
        NCards = 20
        OutFile = '$LARA/tmp_resources/antigone_flashcards.json'
    # Antigone EN
    elif Id == 'antigone_en':
        ConfigFile = '$LARA/Content/antigone_en/corpus/local_config_rosa_kirsten.json'
        FlashcardType = 'token_translation_ask_l2'
        NCards = 20
        OutFile = '$LARA/tmp_resources/antigone_en_flashcards.json'
    # Polly's McColley text, token translations
    elif Id == 'mc_colley':
        ConfigFile = '$LARA/Content/mccolley_philodendron/corpus/local_config.json'
        FlashcardType = 'token_translation_ask_l2'
        NCards = 20
        OutFile = '$LARA/tmp_resources/mc_colley_token_flashcards.json'
    else:
        lara_utils.print_and_flush(f'Error: unknown test ID {Id}')
        return False
    make_flashcards(ConfigFile, FlashcardType, NCards, OutFile)

# Make NCards flashcards
# from the LARA corpus defined by ConfigFile, with the flashcard tyoe defined by the config
# writing result to OutFile
def make_flashcards_for_config_file(ConfigFile, NCards, OutFile):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if not Params:
        lara_utils.print_and_flush(f'Error: unable to read config file {ConfigFile}')
        return False
    FlashcardType = Params.flashcard_type
    if not FlashcardType in lara_config._known_flashcard_types:
        lara_utils.print_and_flush(f'Error: flashcard type "{FlashcardType}" needs to be one of "{" ,".join(lara_config._known_flashcard_types)}"')
        return False
    return make_flashcards(ConfigFile, FlashcardType, NCards, OutFile)

# Make NCards flashcards
# of type FlashcardType
# from the LARA corpus defined by ConfigFile
# writing result to OutFile
def make_flashcards(ConfigFile, FlashcardType, NCards, OutFile):
    if not FlashcardType in lara_config._known_flashcard_types:
        lara_utils.print_and_flush(f'Error: unknow flashcard type {FlashcardType}')
        return False
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if not Params:
        lara_utils.print_and_flush(f'Error: unable to read config file {ConfigFile}')
        return False
    # Get POS information
    if lara_treetagger.tagger_is_available_for_language(Params.language):
        lara_top.make_word_pos_file(ConfigFile)
        WordPosFile = lara_top.lara_tmp_file('word_pos_file', Params)
        WordPOSData = lara_utils.read_json_file(WordPosFile)
    else:
        WordPOSData = False
    # Make the resources for this corpus in case they are out of date
    if not lara_top.compile_lara_local_resources(ConfigFile):
        lara_utils.print_and_flush(f'Error: unable make resources for {ConfigFile}')
        return False
    SegmentAudioFile = lara_top.lara_tmp_file('ldt_segment_recording_file_full_json', Params)
    SegmentAudio = lara_utils.read_json_file(SegmentAudioFile)
    lara_utils.print_and_flush('\n======================\nCREATING FLASHCARDS\n======================\n')
    if FlashcardType == 'lemma_translation_ask_l2':
        return make_lemma_translation_ask_l2_flashcards(Params, NCards, OutFile, WordPOSData, SegmentAudio)
    elif FlashcardType == 'lemma_translation_ask_l1':
        return make_lemma_translation_ask_l1_flashcards(Params, NCards, OutFile, WordPOSData)
    elif FlashcardType == 'token_translation_ask_l2':
        return make_token_translation_ask_l2_flashcards(Params, NCards, OutFile, WordPOSData, SegmentAudio)
    elif FlashcardType == 'token_translation_ask_l2_audio':
        return make_token_translation_ask_l2_audio_flashcards(Params, NCards, OutFile, WordPOSData, SegmentAudio)
    elif FlashcardType == 'signed_video_ask_l2':
        return make_signed_video_ask_l2_flashcards(Params, NCards, OutFile, WordPOSData, SegmentAudio)
    elif FlashcardType == 'sentence_with_gap':
        return make_sentence_with_gap_flashcards(Params, NCards, OutFile, WordPOSData, SegmentAudio)
    elif FlashcardType == 'lemma_translation_ask_l2_audio':
        return make_lemma_translation_ask_l2_audio_flashcards(Params, NCards, OutFile, WordPOSData, SegmentAudio)

# Question is an uninflected L2 word (lemma), e.g. 'að halda'
# Possible answers are L1 translations of lemma, e.g. 'hold; keep; believe; suppose'
#
# We get the information from the lemma translation resource file.
# A typical record (taken from "tina") looks like this:
#
# ['að halda',
#   'hold; keep; believe; suppose',
#   10,
#   ['Tína heldur að pabbi segi já. "Ég fæ að vera þar ein, ekki með ykkur.',
#    'Áður en Tína fer upp í rútuna spyr mamma: "Heldurðu að þér leiðist nokkuð hjá Elsu frænku?"',
#    'Hann tekur ekki eftir því að hún er orðin föl. Rósa er bílveik. Henni er illt í maganum. Hún þarf að kasta upp. Hún heldur hendinni fyrir munninn og hleypur til Bóa.',
#    'Hún hellur ávöxtunum úr pokanum og heldur honum opnum við munninn á Rósu.',
#    'Tómas kemur aftur í til Rósu. Tína heldur pokanum enn þá við munninn á henni.',
#    'Þær ganga heim til Elsu frænku. Elsa frænka heldur á töskunni hennar Tínu.',
#    'En Tína heldur fast í handlegginn á Rósu. Hún sér að rauða rútan er hinum megin við götuna.',
#    'Nú fyrst tekur Rósa eftir því að það er Tína sem heldur henni og þá hættir hún að gráta. "Hvar er Bói?" spyr Tína aftur.',
#    'Fyrst hélt ég að það væri loft rétt fyrir ofan mig. Anna, heyrirðu hvað ég er að segja?"']]

def make_lemma_translation_ask_l2_flashcards(Params, NCards, OutFile, WordPOSData, SegmentAudio):
    LemmaTranslationResourceFile = lara_top.lara_tmp_file('tmp_translation_spreadsheet_json', Params)
    Data = lara_utils.read_json_file(LemmaTranslationResourceFile)
    if Data == False:
        lara_utils.print_and_flush(f'Error: unable to read lemma translations file {LemmaTranslationResourceFile}')
        return False
    if len(Data) < 4:
        lara_utils.print_and_flush(f'Error: not enough examples in {LemmaTranslationResourceFile} to be able to create flashcards')
        return False
    TranslationPairsWithPOS = make_lemma_translation_pairs_with_POS_and_context(Data, WordPOSData, SegmentAudio)
    # Randomly shuffle the data from the file
    random.shuffle(TranslationPairsWithPOS)
    FlashcardRecords = []
    FlashcardQuestions = []
    LoopCounter = 0
    while len(FlashcardRecords) < NCards:
        LoopCounter += 1
        Flashcard = make_ask_l2_flashcard(TranslationPairsWithPOS, FlashcardQuestions)
        if not Flashcard or LoopCounter > 1000:
                lara_utils.print_and_flush(f'*** Error: failed to create {NCards} Flashcards')
                return False
        else:
            FlashcardRecords += [ Flashcard ]
            FlashcardQuestions += [ Flashcard['question']['value'] ]
    lara_utils.write_json_to_file(FlashcardRecords, OutFile)

# Makes translation pairs with POS and context
def make_lemma_translation_pairs_with_POS_and_context(Data, WordPOSData, SegmentAudio):
    if WordPOSData:
        NoDuplicatePOS = []
        [ NoDuplicatePOS.append(w) for w in WordPOSData if w not in NoDuplicatePOS ]

    TranslationPairsWithPOS = []
    for Record in Data:
        if not null_translation_in_translation_record(Record):
            if WordPOSData:
                for Word in NoDuplicatePOS:
                    if Word[1] == Record[0] or Word[1] == 'að ' + Record[0]:
                        TranslationPairsWithPOS.append(add_audio_context(Word[1], Record[1], Word[2], Record[3][0], SegmentAudio))
                        break
            else:
                TranslationPairsWithPOS.append(add_audio_context(Record[0], Record[1], '', Record[3][0], SegmentAudio))
    return TranslationPairsWithPOS

def null_translation_in_translation_record(Record):
    return isinstance(Record, list) and len(Record) >= 2 and lara_translations.null_translation(Record[1])

def add_audio_context(Word, Translation, POS, TextContext, SegmentAudio):
    for S in SegmentAudio:
        if TextContext == S['text']:
            return (Word, Translation, POS, TextContext, f"{S['file'].replace('.wav', '.mp3')}")
    return (Word, Translation, POS, TextContext, '')

def make_lemma_translation_ask_l1_flashcards(Params, NCards, OutFile, WordPOSData):
    LemmaTranslationResourceFile = lara_top.lara_tmp_file('tmp_translation_spreadsheet_json', Params)
    Data = lara_utils.read_json_file(LemmaTranslationResourceFile)
    if Data == False:
        lara_utils.print_and_flush(f'Error: unable to read lemma translations file {LemmaTranslationResourceFile}')
        return False
    if len(Data) < 4:
        lara_utils.print_and_flush(f'Error: not enough examples in {LemmaTranslationResourceFile} to be able to create flashcards')
        return False
    FlashcardRecords = []
    if WordPOSData:
        NoDuplicatePOS = []
        [NoDuplicatePOS.append(w) for w in WordPOSData if w not in NoDuplicatePOS]
        for I in range(0, NCards):
            FlashcardRecords += [ make_POS_lemma_translation_ask_l1_flashcard(Data, NoDuplicatePOS) ]
    else:
        for I in range(0, NCards):
            FlashcardRecords += [ make_distance_lemma_translation_ask_l1_flashcard(Data) ]
    lara_utils.write_json_to_file(FlashcardRecords, OutFile)

# Makes a flashcard with an l1 word as the question and distractors that have the same POS and shortest edit distance.
def make_POS_lemma_translation_ask_l1_flashcard(Data, WordPOSData):
    # Pick question at random
    random.shuffle(Data)
    QuestionRecord = Data[0]
    ( Question, CorrectAnswer ) = ( QuestionRecord[1], QuestionRecord[0] )
    # Find the POS tag for the question. The 'að ' + part is a quick fix for inconsistencies in the data. 
    # Lemmas for Icelandic verbs sometimes have the word 'að' in front of them and sometimes don't.
    AnswerPOS = [w[2] for w in WordPOSData if w[1] == CorrectAnswer or 'að ' + w[1] == CorrectAnswer]
    # If the POS tag isn't found, remove that word and try again.
    if len(AnswerPOS) < 1:
        Data.pop(0)
        return make_POS_lemma_translation_ask_l1_flashcard(Data, WordPOSData)
    else:
        AnswerPOS = AnswerPOS[0]
    possibleDistractors = []
    # Loop through the records and find words that have the same POS tag as the question and calculate the edit distance
    # between the words and the question.
    for i in range(1, len(Data)):
        for j in WordPOSData:
            if j[2] == AnswerPOS and (Data[i][0] == j[1] or Data[i][0] == 'að ' + j[1]):
                possibleDistractors.append((distance.edit_distance(CorrectAnswer, Data[i][0]), Data[i][0]))
                break
    # Pick the three possible distractors that have the shortest edit distance.
    possibleDistractors.sort()
    Distractors = [{'value': d[1], 'type':'raw_text'} for d in possibleDistractors[:3]]
    return { 'question': {'value': Question, 'type' : 'raw_text'} ,
             'answer': {'value': CorrectAnswer, 'type' : 'raw_text'},
             'distractors': Distractors,
             'text_context': '',
             'multimedia_context': '',
             'type': 'raw_text'
             }

# Makes a flashcard with an l1 lemma as the question and distractors that have the shortest edit distance.
def make_distance_lemma_translation_ask_l1_flashcard(Data):
    # Pick question at random
    random.shuffle(Data)
    QuestionRecord = Data[0]
    ( Question, CorrectAnswer ) = ( QuestionRecord[1], QuestionRecord[0] )
    possibleDistractors = []
    # Loop through the records and find words that have the same POS tag as the question and calculate the edit distance
    # between the words and the question.
    for i in range(1, len(Data)):
            possibleDistractors.append((distance.edit_distance(CorrectAnswer, Data[i][0]), Data[i][0]))
    # Pick the three possible distractors that have the shortest edit distance.
    possibleDistractors.sort()
    Distractors = [d[1] for d in possibleDistractors[:3]]
    return { 'question': Question,
             'answer': CorrectAnswer,
             'distractors': Distractors,
             'text_context': '',
             'multimedia_context': '',
             'type': 'raw_text'
             }

# Question is an inflected L2 word, e.g. 'bið'
# Possible answers are L1 translations of lemma, e.g. 'ask; those; tales; men'
#
# We get the information from the word token translation resource file.
# A typical record (taken from "völuspá_kenningar") looks like this:
#
# [
#   [ "Hljóðs", "bið", "ek", "allar", "kindir", "meiri", "ok", "minni", "mögu", "Heimdalar", 
#     "vildu", "að", "ek", "Valföðr", "vel", "fram", "telja", "forn", "spjöll", "fira", "þau", "er", "fremst", "um", "man" ],
#   [ "Hearing", "ask", "I", "all", "mankind", "of more status", "and", "of less status", "relatives-", "of Heimdal", 
#     "want-you", "that", "I", "Valfather", "will", "go on", "talking", "ancient", "tales", "of men", "those", "are", "one of the first", "", "I remember" ],
#   [ "Hearing", "I", "ask", "from", "the", "holy", "races", "From", "Heimdall's", "sons", "both", "high", "and", "low",
#     "Thou", "wilt", "Valfather", "that", "well", "I", "relate", "Old", "tales", "I", "remember", "of", "men", "long", "ago" ]
# ]

def make_token_translation_ask_l2_flashcards(Params, NCards, OutFile, WordPOSData, SegmentAudio):
    TokenTranslationResourceFile = lara_top.lara_tmp_file('tmp_translation_spreadsheet_token_json', Params)
    Data = lara_utils.read_json_file(TokenTranslationResourceFile)
    if Data == False:
        lara_utils.print_and_flush(f'Error: unable to read token translations file {TokenTranslationResourceFile}')
        return False
    #SplitFile = lara_top.lara_tmp_file('split', Params)
    #TranslationPairs = lara_mwe.split_file_and_token_translation_file_to_translation_context_triples_taking_account_of_mwes(SplitFile, TokenTranslationResourceFile)
    TranslationPairs = lara_mwe.split_file_and_token_translation_file_to_translation_context_triples_taking_account_of_mwes(Params, TokenTranslationResourceFile)
    if len(TranslationPairs) < 4:
        lara_utils.print_and_flush(f'Error: not enough examples in {TokenTranslationResourceFile} to be able to create flashcards')
        return False
    if Params.language == 'oldnorse':
        TranslationPairsWithPOS = add_oldnorse_POS_and_context(TranslationPairs, SegmentAudio)
    else:
        TranslationPairsWithPOS = make_token_translation_pairs_with_POS_and_context(TranslationPairs, WordPOSData, SegmentAudio)
    # Randomly shuffle the data from the file
    random.shuffle(TranslationPairsWithPOS)
    LoopCounter = 0
    FlashcardRecords = []
    FlashcardQuestions = []
    while len(FlashcardRecords) < NCards:
        LoopCounter += 1
        Flashcard = make_ask_l2_flashcard(TranslationPairsWithPOS, FlashcardQuestions)
        if not Flashcard or LoopCounter > 1000:
            lara_utils.print_and_flush(f'*** Error: failed to create {NCards} Flashcards')
            return False
        else:
            FlashcardRecords += [ Flashcard ]
            FlashcardQuestions += [ Flashcard['question']['value'] ]
    lara_utils.write_json_to_file(FlashcardRecords, OutFile)

# Adds POS information and context to a list of Old Norse translation pairs
def add_oldnorse_POS_and_context(TranslationPairs, SegmentAudio):
    edda_words2lemmas_file = '$LARA/Content/oldnorse/corpus/edda_words2lemmas.json'
    onp_index_file = '$LARA/Content/oldnorse/corpus/onp_index.json'
    EddaWordsAndLemmasDict = lara_utils.read_json_file(edda_words2lemmas_file)
    ONPDict = lara_utils.read_json_file(onp_index_file)
    
    NoDuplicatePairs = []
    [NoDuplicatePairs.append(w) for w in TranslationPairs if w not in NoDuplicatePairs]
    TranslationPairsWithPOS = []
    
    for Pair in NoDuplicatePairs:
        Word = Pair[0]
        if Word not in EddaWordsAndLemmasDict:
            TranslationPairsWithPOS.append(add_audio_context(Pair[0], Pair[1], 'None', Pair[2], SegmentAudio))
            continue
        Lemma = EddaWordsAndLemmasDict[Word][0]
        if Lemma not in ONPDict:
            TranslationPairsWithPOS.append(add_audio_context(Pair[0], Pair[1], 'None', Pair[2], SegmentAudio))
            continue
        ONPInfo = ONPDict[Lemma]
        TranslationPairsWithPOS.append(add_audio_context(Pair[0], Pair[1], ONPInfo[0]['pos'], Pair[2], SegmentAudio))
    return TranslationPairsWithPOS

def make_token_translation_pairs_with_POS_and_context(TranslationPairs, WordPOSData, SegmentAudio):
    if(WordPOSData):
        NoDuplicatePOS = []
        [NoDuplicatePOS.append(w) for w in WordPOSData if w not in NoDuplicatePOS]
    NoDuplicatePairs = []
    [NoDuplicatePairs.append(w) for w in TranslationPairs if w not in NoDuplicatePairs and '(-)' not in w[1]]
    TranslationPairsWithPOS = []

    for Pair in NoDuplicatePairs:
        if WordPOSData:
            for Word in NoDuplicatePOS:
                if Word[0] == Pair[0]:
                    TranslationPairsWithPOS.append(add_audio_context(Word[0], Pair[1], Word[2], Pair[2], SegmentAudio))
                    break
        else:
            TranslationPairsWithPOS.append(add_audio_context(Pair[0], Pair[1], '', Pair[2], SegmentAudio))
    return TranslationPairsWithPOS

# Makes a flashcard with distractors that have the same POS and shortest edit distance.
def make_ask_l2_flashcard(TranslationPairsWithPOS, PreviousQuestions):
    if len(TranslationPairsWithPOS) < 4:
        return False
    # Find the first usable record to get the question and the correct answer
    Found = False
    ( QuestionRecord, Distractors ) = fresh_valid_question_record_and_distractors(TranslationPairsWithPOS, PreviousQuestions)
    if QuestionRecord == False:
        return False
    ( Question, CorrectAnswer, QuestionPOS, TextContext, MultimediaContext ) = QuestionRecord
    return { 'question': {'value': Question.capitalize(), 'type' : 'raw_text'} ,
             'answer': {'value': CorrectAnswer.capitalize(), 'type' : 'raw_text'},
             'distractors': Distractors,
             'text_context': {'value':TextContext, 'type':'raw_text'},
             'multimedia_context': {'value': MultimediaContext, 'type':'audio_file_name'}
             }

# A valid question record has a non-null answer different from the question and enough valid distractors
def fresh_valid_question_record_and_distractors(TranslationPairsWithPOS, PreviousQuestions):
    for i in range(0, len(TranslationPairsWithPOS) ):
        QuestionRecord = TranslationPairsWithPOS[i]
        ( Question, CorrectAnswer, QuestionPOS, TextContext, MultimediaContext ) = QuestionRecord
        if Question != CorrectAnswer and not Question.capitalize() in PreviousQuestions and not lara_translations.null_translation(CorrectAnswer):
            Distractors = find_distractors(Question, QuestionPOS, CorrectAnswer, TranslationPairsWithPOS)
            if Distractors != False:
                return ( QuestionRecord, Distractors )
    return ( False, False )    

def find_distractors(Question, QuestionPOS, CorrectAnswer, TranslationPairsWithPOS):
    possibleDistractors = []
    possibleFullDistractors = []
    # A potential distractor has a different answer and the same POS
    for i in range(0, len(TranslationPairsWithPOS) ):
        ( Question1, Answer1, QuestionPOS1, TextContext1, MultimediaContext1 ) = TranslationPairsWithPOS[i]
        if Answer1.capitalize() != CorrectAnswer.capitalize() and \
           not lara_translations.null_translation(Answer1) and \
           not Answer1.capitalize() in possibleDistractors and \
           QuestionPOS == QuestionPOS1:
            possibleDistractors += [ Answer1.capitalize() ]
            possibleFullDistractors += [ ( distance.edit_distance(Question, Question1), Answer1 ) ]
    # Pick the three possible distractors that have the shortest edit distance.
    if len(possibleFullDistractors) < 3:
        return False
    else:
        SortedPossibleDistractors = sorted(possibleFullDistractors, key=lambda x: x[0])
        return [ {'value': Distractor[1].capitalize(), 'type':'raw_text'} for Distractor in SortedPossibleDistractors[:3] ]

# Makes a flashcard with an l2 token as the question and distractors that have the shortest edit distance
def make_distance_token_translation_ask_l2_flashcard(TranslationPairs):
    NoDuplicatePairs = []
    [NoDuplicatePairs.append(w) for w in TranslationPairs if w not in NoDuplicatePairs]
    # Randomly shuffle the data from the file
    random.shuffle(NoDuplicatePairs)
    # Use the first record to get the question and the correct answer
    QuestionRecord = NoDuplicatePairs[0]
    ( Question, CorrectAnswer ) = ( QuestionRecord[0], QuestionRecord[1] )
    possibleDistractors = []
    for i in range(1, len(NoDuplicatePairs)):
            possibleDistractors.append((distance.edit_distance(Question, NoDuplicatePairs[i][0]), NoDuplicatePairs[i][1]))
    # Pick the three possible distractors that have the shortest edit distance.
    possibleDistractors.sort()
    Distractors = [d[1] for d in possibleDistractors[:3]]
    return { 'question': Question,
             'answer': CorrectAnswer,
             'distractors': Distractors,
             'text_context': '',
             'multimedia_context': '',
             'type': 'raw_text'
             }

# Question is an audio file for an inflected L2 word, e.g. audio file for 'bið'
# Possible answers are L1 translations of lemma, e.g. 'ask; those; tales; men'
#
# We get the translation information from the word token translation resource file.
# A typical record (taken from "völuspá_kenningar") looks like this:
#
# [
#   [ "Hljóðs", "bið", "ek", "allar", "kindir", "meiri", "ok", "minni", "mögu", "Heimdalar", 
#     "vildu", "að", "ek", "Valföðr", "vel", "fram", "telja", "forn", "spjöll", "fira", "þau", "er", "fremst", "um", "man" ],
#   [ "Hearing", "ask", "I", "all", "mankind", "of more status", "and", "of less status", "relatives-", "of Heimdal", 
#     "want-you", "that", "I", "Valfather", "will", "go on", "talking", "ancient", "tales", "of men", "those", "are", "one of the first", "", "I remember" ],
#   [ "Hearing", "I", "ask", "from", "the", "holy", "races", "From", "Heimdall's", "sons", "both", "high", "and", "low",
#     "Thou", "wilt", "Valfather", "that", "well", "I", "relate", "Old", "tales", "I", "remember", "of", "men", "long", "ago" ]
# ]
#
# We get the audio information from the word audio file.
# A typical record (taken from "völuspá_kenningar") looks like this:
#    {
#        "file": "429296_200212_131704681.wav",
#        "text": "bið"
#    },

def make_token_translation_ask_l2_audio_flashcards(Params, NCards, OutFile, WordPOSData, SegmentAudio):
    WordAudioResourceFile = lara_top.lara_tmp_file('ldt_word_recording_file_full_json', Params)
    AudioData0 = lara_utils.read_json_file(WordAudioResourceFile)
    if AudioData0 == False:
        lara_utils.print_and_flush(f'Error: unable to read word audio file {WordAudioResourceFile}')
        return False
    # Convert the audio information into a dict where the keys are words and the value are full pathnames for audio files
    else:
        AudioData = { Record['text']: f"{Record['file'].replace('.wav', '.mp3')}"
                      for Record in AudioData0
                      if Record['file'] != '' }
    TokenTranslationResourceFile = lara_top.lara_tmp_file('tmp_translation_spreadsheet_token_json', Params)
    #SplitFile = lara_top.lara_tmp_file('split', Params)
    if TokenTranslationResourceFile == False:
        lara_utils.print_and_flush(f'Error: unable to read token translations file {TokenTranslationResourceFile}')
        return False
    #TranslationPairs = lara_mwe.split_file_and_token_translation_file_to_translation_context_triples_taking_account_of_mwes(SplitFile, TokenTranslationResourceFile)
    TranslationPairs = lara_mwe.split_file_and_token_translation_file_to_translation_context_triples_taking_account_of_mwes(Params, TokenTranslationResourceFile)
    if len(TranslationPairs) < 4:
        lara_utils.print_and_flush(f'Error: not enough examples in {TokenTranslationResourceFile} to be able to create flashcards')
        return False
    if Params.language == 'oldnorse':
        PairsWithContextAndPos = add_oldnorse_POS_and_context(TranslationPairs, SegmentAudio)
    else:
        PairsWithContextAndPos = make_token_translation_pairs_with_POS_and_context(TranslationPairs, WordPOSData, SegmentAudio)
    TranslationPairsWithAudio = [ audio_version_of_translation_pair(TranslationPair, AudioData) 
                         for TranslationPair in PairsWithContextAndPos
                         if audio_version_of_translation_pair(TranslationPair, AudioData) ]
    FlashcardRecords = []
    for I in range(0, NCards):
        FlashcardRecords += [ make_token_translation_ask_l2_audio_flashcard(TranslationPairsWithAudio) ]
    lara_utils.write_json_to_file(FlashcardRecords, OutFile)

def audio_version_of_translation_pair(TranslationPair, AudioData):
    ( Word, Translation, POS, TextContext, MultimediaContext) = TranslationPair
    return ( AudioData[Word], Translation, POS, TextContext, MultimediaContext, Word) if Word in AudioData else False

# We pick a random record for the question, then three more random records for the distractors
def make_token_translation_ask_l2_audio_flashcard(TranslationPairs):
    if len(TranslationPairs) < 4:
        return False
    # Randomly shuffle the data from the file
    random.shuffle(TranslationPairs)
    # Use the first record to get the question and the correct answer
    QuestionRecord = TranslationPairs[0]
    ( Question, CorrectAnswer, QuestionPOS, TextContext, MultimediaContext, TextQuestion ) = QuestionRecord
    possibleDistractors = []
    for i in range(1, len(TranslationPairs)):
            if QuestionPOS == TranslationPairs[i][2]:
                	possibleDistractors.append((distance.edit_distance(TextQuestion, TranslationPairs[i][5]), TranslationPairs[i][1]))
    possibleDistractors.sort()
    Distractors = []
    while len(Distractors) < 3:
        if len(possibleDistractors) < 3 - len(Distractors):
            TranslationPairs.pop(0)
            return make_token_translation_ask_l2_audio_flashcard(TranslationPairs)
        Distractor = possibleDistractors.pop(0)
        if Distractor[1].capitalize() not in [D['value'] for D in Distractors] and Distractor[1].capitalize() != CorrectAnswer.capitalize() and Distractor[0] != 0 and Distractor[1] != '':
            Distractors.append({'value': Distractor[1].capitalize(), 'type':'raw_text'})
    return { 'question': {'value': Question, 'type' : 'audio_file_name'} ,
             'answer': {'value': CorrectAnswer.capitalize(), 'type' : 'raw_text'},
             'distractors': Distractors,
             'text_context': {'value':TextContext, 'type':'raw_text'},
             'multimedia_context': {'value': MultimediaContext, 'type':'audio_file_name'}
             }

# Question is an uninflected L2 word (lemma), e.g. 'að fara'
# Possible answers are signed videos for lemmas
#
# We get the information from the word video resource file.
# A typical record (taken from "tina_signed_small") looks like this:
#
# {
#    "text": "að fara",
#    "file": "706007_200612_172549829.webm"
# }

def make_signed_video_ask_l2_flashcards(Params, NCards, OutFile, WordPOSData, SegmentAudio):
    WordSignedVideoResourceFile = lara_top.lara_tmp_file('ldt_word_recording_file_full_json', Params)
    Data = lara_utils.read_json_file(WordSignedVideoResourceFile)
    LemmaTranslationResourceFile = lara_top.lara_tmp_file('tmp_translation_spreadsheet_json', Params)
    LemmaData = lara_utils.read_json_file(LemmaTranslationResourceFile)
    if Data == False:
        lara_utils.print_and_flush(f'Error: unable to read word video file {WordSignedVideoResourceFile}')
        return False
    WordVideoPairs = [ ( Record['text'], f"{Record['file']}" ) for Record in Data if Record['file'] != '' ]
    LemmaContextAndPOS = make_lemma_translation_pairs_with_POS_and_context(LemmaData, WordPOSData, SegmentAudio)
    WordVideoPairsWithContext = []
    for Lemma in LemmaContextAndPOS:
        for Word in WordVideoPairs:
            if Lemma[0] == Word[0].capitalize():
                WordVideoPairsWithContext.append((Lemma[0], Word[1], Lemma[2], Lemma[3], Lemma[4]))
                break
    if len(WordVideoPairs) < 4:
        lara_utils.print_and_flush(f'Error: not enough examples in {WordSignedVideoResourceFile} to be able to create flashcards')
        return False
    # Initial strategy is very simple: choose random records to make the cards, choose random translations for the distractors.
    LoopCounter = 0
    FlashcardRecords = []
    while len(FlashcardRecords) < NCards:
        LoopCounter += 1
        Flashcard = make_signed_video_ask_l2_flashcard(WordVideoPairsWithContext)
        if not Flashcard or LoopCounter > 1000:
            lara_utils.print_and_flush(f'Error: failed to create Flashcards')
            return False
        if Flashcard not in FlashcardRecords:
            FlashcardRecords += [ Flashcard ]
    lara_utils.write_json_to_file(FlashcardRecords, OutFile)

# We pick a random record for the question, then three more random records for the distractors
def make_signed_video_ask_l2_flashcard(WordVideoPairs):
    if len(WordVideoPairs) < 4:
        return False
    # Randomly shuffle the data from the file
    random.shuffle(WordVideoPairs)
    # Use the first record to get the question and the correct answer
    QuestionRecord = WordVideoPairs[0]
    ( CorrectAnswer, Question,  QuestionPOS, TextContext, MultimediaContext ) = QuestionRecord
    possibleDistractors = []
    for i in range(1, len(WordVideoPairs)):
            possibleDistractors.append((distance.edit_distance(CorrectAnswer, WordVideoPairs[i][0]), WordVideoPairs[i][0]))
    possibleDistractors.sort()
    Distractors = []
    while len(Distractors) < 3:
        if len(possibleDistractors) < 3 - len(Distractors):
            WordVideoPairs.pop(0)
            return make_signed_video_ask_l2_flashcard(WordVideoPairs)
        Distractor = possibleDistractors.pop(0)
        if Distractor[1] not in [D['value'] for D in Distractors] and Distractor[1] != CorrectAnswer and Distractor[0] != 0 and Distractor[1] != '':
            Distractors.append({'value': Distractor[1], 'type':'raw_text'})
    return { 'question': {'value': Question, 'type' : 'video_file_name'} ,
             'answer': {'value': CorrectAnswer, 'type' : 'raw_text'},
             'distractors': Distractors,
             'text_context': {'value':TextContext, 'type':'raw_text'},
             'multimedia_context': {'value': MultimediaContext, 'type':'video_file_name'}
             }

# Question is a sentence with a gap, e.g. '"Mamma, komdu og ___, ég get gert með tveim boltum."'
# Possible answers are filler words, e.g. 'sjáðu', 'hleri', 'opnar', 'og'

# We get the information from the split file, whose structure is
# <Data> ::= list of <Pages>
# <Page> ::= [ <PageInfo>, list of <Segments> ]
# <Segment> ::= [ <Plain>, <Processed>, list of <TextLemmaPairs>, <Tag> ]
# <TextLemmaPair> ::= [ <Text> <Lemma> ]
# <Text> needs to be cleaned up to remove formatting. <Lemma> is null if <Text> is a non-word.
    
def make_sentence_with_gap_flashcards(Params, NCards, OutFile, WordPOSData, SegmentAudio):
    SplitFile = lara_top.lara_tmp_file('split', Params)
    Data = lara_utils.read_json_file(SplitFile)
    if Data == False:
        lara_utils.print_and_flush(f'Error: unable to split file {SplitFile}')
        return False
    Sentences = extract_clean_sentences_from_split_file_contents(Data)
    GapSentenceFillerPairs = sentences_to_gap_filler_pairs(Sentences)
    SentenceFillerPairsWithContext = [(Pair[0].replace('    ', ' '), Pair[1], Pair[0].replace('_____', Pair[1]).replace('    ', ' ')) for Pair in GapSentenceFillerPairs]
    if len(GapSentenceFillerPairs) < 4:
        lara_utils.print_and_flush(f'Error: not enough examples in {SplitFile} to be able to create flashcards')
        return False
    # Initial strategy is very simple: choose random records to make the cards, choose random translations for the distractors.
    if Params.language == 'oldnorse':
        PairsWithContextAndPos = add_oldnorse_POS_and_context_for_gaps(SentenceFillerPairsWithContext, SegmentAudio)
    else:
        PairsWithContextAndPos = add_pos_and_context(SentenceFillerPairsWithContext, WordPOSData, SegmentAudio)
    FlashcardRecords = []
    for I in range(0, NCards):
        FlashcardRecords += [ make_sentence_with_gap_flashcard(PairsWithContextAndPos) ]
    lara_utils.write_json_to_file(FlashcardRecords, OutFile)

def add_pos_and_context(Pairs, WordPOSData, SegmentAudio):
    if WordPOSData:
        NoDuplicatePOS = []
        [NoDuplicatePOS.append(w) for w in WordPOSData if w not in NoDuplicatePOS]

    TranslationPairsWithPOS = []
    for Pair in Pairs:
        if WordPOSData:
            for Word in NoDuplicatePOS:
                if Word[0] == Pair[1]:
                        TranslationPairsWithPOS.append(add_audio_context(Pair[0], Pair[1], Word[2], Pair[2], SegmentAudio))
                        break
        else:
            TranslationPairsWithPOS.append(add_audio_context(Pair[0], Pair[1], '', Pair[2], SegmentAudio))
    return TranslationPairsWithPOS

def add_oldnorse_POS_and_context_for_gaps(TranslationPairs, SegmentAudio):
    edda_words2lemmas_file = '$LARA/Content/oldnorse/corpus/edda_words2lemmas.json'
    onp_index_file = '$LARA/Content/oldnorse/corpus/onp_index.json'
    EddaWordsAndLemmasDict = lara_utils.read_json_file(edda_words2lemmas_file)
    ONPDict = lara_utils.read_json_file(onp_index_file)
    
    TranslationPairsWithPOS = []
    for Pair in TranslationPairs:
        Word = Pair[1]
        if Word not in EddaWordsAndLemmasDict:
            TranslationPairsWithPOS.append(add_audio_context(Pair[0], Pair[1], 'None', Pair[2], SegmentAudio))
            continue
        Lemma = EddaWordsAndLemmasDict[Word][0]
        if Lemma not in ONPDict:
            TranslationPairsWithPOS.append(add_audio_context(Pair[0], Pair[1], 'None', Pair[2], SegmentAudio))
            continue
        ONPInfo = ONPDict[Lemma]
        TranslationPairsWithPOS.append(add_audio_context(Pair[0], Pair[1], ONPInfo[0]['pos'], Pair[2], SegmentAudio))
    return TranslationPairsWithPOS

# We pick a random record for the question, then three more random records for the distractors
def make_sentence_with_gap_flashcard(GapSentenceFillerPairs):
    if len(GapSentenceFillerPairs) < 4:
        return False
    # Randomly shuffle the data from the file
    random.shuffle(GapSentenceFillerPairs)
    # Use the first record to get the question and the correct answer
    QuestionRecord = GapSentenceFillerPairs[0]
    ( Question, CorrectAnswer, QuestionPOS, TextContext, MultimediaContext ) = QuestionRecord
    # Use the next three records to get the distractors
    possibleDistractors = []
    for i in range(1, len(GapSentenceFillerPairs)):
            if QuestionPOS == GapSentenceFillerPairs[i][2]:
                	possibleDistractors.append((distance.edit_distance(CorrectAnswer, GapSentenceFillerPairs[i][1]), GapSentenceFillerPairs[i][1]))
    possibleDistractors.sort()
    Distractors = []
    while len(Distractors) < 3:
        if len(possibleDistractors) < 3 - len(Distractors):
            GapSentenceFillerPairs.pop(0)
            return make_sentence_with_gap_flashcard(GapSentenceFillerPairs)
        Distractor = possibleDistractors.pop(0)
        if Distractor[1].capitalize() not in [D['value'].capitalize() for D in Distractors] and Distractor[1].capitalize() != CorrectAnswer.capitalize() and Distractor[0] != 0 and Distractor[1] != '':
            Distractors.append({'value': Distractor[1].capitalize(), 'type':'raw_text'})
    return { 'question': {'value': Question, 'type' : 'raw_text'} ,
             'answer': {'value': CorrectAnswer.capitalize(), 'type' : 'raw_text'},
             'distractors': Distractors,
             'text_context': {'value':TextContext, 'type':'raw_text'},
             'multimedia_context': {'value': MultimediaContext, 'type':'audio_file_name'}
            }

def extract_clean_sentences_from_split_file_contents(Data):
    return [ clean_up_text_lemma_pairs(TextLemmaPairs)
             for ( PageInfo, Segments) in Data
             for ( Plain, Processed, TextLemmaPairs, Tag ) in Segments
             if Processed != '' ]

def clean_up_text_lemma_pairs(TextLemmaPairs):
    return [ ( clean_up_text(Text), Lemma ) for ( Text, Lemma ) in TextLemmaPairs ]

def clean_up_text(Text):
    return lara_parse_utils.remove_hashtag_comment_and_html_annotations1(Text, 'delete_comments')[0]

def sentences_to_gap_filler_pairs(Sentences):
    return [ sentence_to_gap_filler_pair(Sentence, Index)
             for Sentence in Sentences
             for Index in range(0, len(Sentence))
             # If Sentence[Index][1] == '', then the element at that index isn't a word, so we can't replace it with a gap
             if Sentence[Index][1] != '' ]

def sentence_to_gap_filler_pair(Sentence, IndexOfGap):
    SentenceWithGap = ''.join([ Sentence[Index][0] if Index != IndexOfGap else '_____'
                                for Index in range(0, len(Sentence)) ])
    return ( clean_up_newlines_and_spaces(SentenceWithGap), Sentence[IndexOfGap][0] )

# Turn newlines into spaces and then remove leading and trailing spaces
def clean_up_newlines_and_spaces(Sentence):
    return Sentence.replace('\n', ' ').strip()

def make_lemma_translation_ask_l2_audio_flashcards(Params, NCards, OutFile, WordPOSData, SegmentAudio):
    WordAudioResourceFile = lara_top.lara_tmp_file('ldt_word_recording_file_full_json', Params)
    AudioData0 = lara_utils.read_json_file(WordAudioResourceFile)
    if AudioData0 == False:
        lara_utils.print_and_flush(f'Error: unable to read word audio file {WordAudioResourceFile}')
        return False
    # Convert the audio information into a dict where the keys are words and the value are full pathnames for audio files
    else:
        AudioData = { Record['text']: f"{Record['file'].replace('.wav', '.mp3')}"
                      for Record in AudioData0
                      if Record['file'] != '' }
    LemmaTranslationResourceFile = lara_top.lara_tmp_file('tmp_translation_spreadsheet_json', Params)
    Data = lara_utils.read_json_file(LemmaTranslationResourceFile)
    if Data == False:
        lara_utils.print_and_flush(f'Error: unable to read lemma translations file {LemmaTranslationResourceFile}')
        return False
    if len(Data) < 4:
        lara_utils.print_and_flush(f'Error: not enough examples in {LemmaTranslationResourceFile} to be able to create flashcards')
        return False
    PairsWithContextAndPos = make_lemma_translation_pairs_with_POS_and_context(Data, WordPOSData, SegmentAudio)
    TranslationPairsWithAudio = [ audio_version_of_translation_pair(TranslationPair, AudioData) 
                         for TranslationPair in PairsWithContextAndPos
                         if audio_version_of_translation_pair(TranslationPair, AudioData) ]
    FlashcardRecords = []
    for I in range(0, NCards):
        FlashcardRecords += [ make_token_translation_ask_l2_audio_flashcard(TranslationPairsWithAudio) ]
    lara_utils.write_json_to_file(FlashcardRecords, OutFile)

# For testing
#test_make_flashcards('tina')
