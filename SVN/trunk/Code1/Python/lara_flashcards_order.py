import lara_utils
import random
import re
#import lara_flashcards_mysql_connection_staging
import lara_flashcards_mysql_connection_from_config

# Order the flashcards candidates
#
# UnorderedCandidates is a list of flashcard candidates
# A flashcard candidate is a dict containing some of the following keys:
#
# 'lemma'
# 'word'
# 'pos'
# 'text_context'
# 'multimedia_context'
# 'translation'
# 'word_audio'
# 'word_video'
#
# All the candidates in the list will have the same keys.
#
# This function sorts list of dicts UndorderedCandidates according to chosen content by frequency and into 3 levels: beginner, intermediate and advanced.
# The fourth option sorts out a list of candidates for 'multiword expressions' MWE.
# Finally, the selected ordered candidates for Level are shuffled randomly.
def order_candidates_default(UnorderedCandidates, Level, POS, UserId, Strategy, Resources):
    LemmaFreqDict = Resources['lemma2freq_dict']
    TokenTranslationDict = Resources['word2tokentranslation_and_context_dict']
    CandidatesBeginner = list()
    CandidatesIntermediate = list()
    CandidatesAdvanced = list()
    CandidatesMWE = list()
    
    # get list of candidates for multiword expressions:
    if Level.lower() == 'multiword_expressions':
        multiwordExpressions = get_list_of_MWE(TokenTranslationDict)               
        for i in range(0, len(UnorderedCandidates)-1):
            key = ''
            try:
                key = UnorderedCandidates[i]['lemma']
            except:
                key = UnorderedCandidates[i]['word']
            try:
                for multiRecord in multiwordExpressions:
                    if key in multiRecord:
                        CandidatesMWE.insert(-1, UnorderedCandidates[i])
            except:
                pass
        random.shuffle(CandidatesMWE)
        return(CandidatesMWE)
    
    # discard candidates where question (value to key 'word' or 'lemma') is exactly the same 
    # as answer (value to key 'translation')
    SortedCandidates = list()
    for Candidate in UnorderedCandidates:
        # try:
        if 'lemma' in Candidate.keys() and 'translation' in Candidate.keys():
            if Candidate['lemma'] != Candidate['translation']:
                SortedCandidates.insert(-1, Candidate)
        # except:
        elif 'word' in Candidate.keys() and 'translation' in Candidate.keys():
            if Candidate['word'] != Candidate['translation']:
                SortedCandidates.insert(-1, Candidate)
        elif 'sentence_with_gap' in Candidate.keys():
            SortedCandidates.insert(-1, Candidate)        
                
    # get lists of candidates according to lemma/word frequency:     
    for i in range(0, len(SortedCandidates)-1):
        keyFrequency = ''
        key = ''
        try:
            key = SortedCandidates[i]['lemma']
        except: 
            key = SortedCandidates[i]['word']
        try:                        
            keyFrequency = LemmaFreqDict[key.lower()]
            # sort into three lists of dicts according to frequency:
            if keyFrequency > 3:
                SortedCandidates[i]['level'] = 'beginner'
                CandidatesBeginner.insert(-1, SortedCandidates[i])
            elif keyFrequency == 1:
                SortedCandidates[i]['level'] = 'advanced'
                CandidatesAdvanced.insert(-1, SortedCandidates[i])
            else:
                SortedCandidates[i]['level'] = 'intermediate'
                CandidatesIntermediate.insert(-1, SortedCandidates[i])
        except: #this exception ignores dict entries that don't have a match (mistakes made by the content creator)
            pass
        
    if Level.lower() == 'beginner':
        random.shuffle(CandidatesBeginner)
        CandidatesPOSBeginner = order_candidates_single_POS_regex(CandidatesBeginner, POS)
        return(CandidatesPOSBeginner)
    if Level.lower() == 'intermediate':
        random.shuffle(CandidatesIntermediate)
        CandidatesPOSIntermediate = order_candidates_single_POS_regex(CandidatesIntermediate, POS)
        return(CandidatesPOSIntermediate)
    if Level.lower() == 'advanced':
        random.shuffle(CandidatesAdvanced)
        CandidatesPOSAdvanced = order_candidates_single_POS_regex(CandidatesAdvanced, POS)
        return(CandidatesPOSAdvanced)   
    return

# Get a list of multiword expression dicts from TokenTranslationDict
def get_list_of_MWE(TokenTranslationDict):
    filteredMWE = list()
    for k in TokenTranslationDict:
        if TokenTranslationDict[k]['is_mwe']:
            MWEKey = dict()
            MWEKey[k] = TokenTranslationDict[k]
            filteredMWE.insert(-1, MWEKey)            
    return(filteredMWE)

# this function selects flashcards for single POS
# the selection is based on regular expressions (regex below cover special tags for Old Norse, Swedish 
# and standard tags for English + French)
def order_candidates_single_POS_regex(CandidatesForLevel, POS):
    CandidatesVerb = list()
    CandidatesNoun = list()
    CandidatesAdj = list()
    CandidatesAdv = list()
    CandidatesPronoun = list()
    CandidatesPrep = list()
    CandidatesNum = list()
    
    for Candidate in CandidatesForLevel:
        if re.fullmatch(r'^N$|^NN.*$|^noun.*$', Candidate['pos']):
            CandidatesNoun.insert(-1, Candidate)
        elif re.fullmatch(r'^PN.*$|^PRO$|^pron\.$', Candidate['pos']):
            CandidatesPronoun.insert(-1, Candidate)
        elif re.fullmatch(r'^J+.*$|^ADJ$|^adj\.$', Candidate['pos']):
            CandidatesAdj.insert(-1, Candidate)
        elif re.fullmatch(r'^V+.*$|^verb$', Candidate['pos']):
            CandidatesVerb.insert(-1, Candidate)
        elif re.fullmatch(r'^ADV$|^adv\.|^AB$', Candidate['pos']):
            CandidatesAdv.insert(-1, Candidate)   
        elif re.fullmatch(r'^P+$|^prep\.$]', Candidate['pos']):
            CandidatesPrep.insert(-1, Candidate)
        elif re.fullmatch(r'^NUM$|^num\.$|^RG.*$|^RO.*$', Candidate['pos']):
            CandidatesNum.insert(-1, Candidate)
    
    if POS.lower() == 'nouns':
        random.shuffle(CandidatesNoun)
        return(CandidatesNoun)
    if POS.lower() == 'pronouns':
        random.shuffle(CandidatesPronoun)
        return(CandidatesPronoun)
    if POS.lower() == 'adjectives':
        random.shuffle(CandidatesAdj)
        return(CandidatesAdj)
    if POS.lower() == 'verbs':
        random.shuffle(CandidatesVerb)
        return(CandidatesVerb)
    if POS.lower() == 'adverbs':
        random.shuffle(CandidatesAdv)
        return(CandidatesAdv)
    if POS.lower() == 'prepositions':
        random.shuffle(CandidatesPrep)
        return(CandidatesPrep)
    if POS.lower() == 'numerals':
        random.shuffle(CandidatesNum)
        return(CandidatesNum)
    if POS.lower() == 'any' or POS.lower() == '':
        return(CandidatesForLevel)
    return

#  select data with incorrect answers for a user and given content
def get_user_incorrect_history(DatabaseData):
    UserIncorrectHistory = list()
    for item in DatabaseData:
        if item[9] == 'incorrect':
            UserIncorrectHistory.insert(-1, item)            
    return(UserIncorrectHistory)

# now make lists of answers for different types of flashcards
def get_questions_for_incorrect_answers(UserIncorrectHistory, FlashcardType):
    sentence_with_gap_list = list()
    token_translation_ask_l2_list = list()
    lemma_translation_ask_l1_list = list()
    lemma_translation_ask_l2_list = list()
    token_translation_ask_l2_audio_list = list()
    lemma_translation_ask_l2_audio_list = list()
    signed_video_ask_l2_list = list()
    Questions = list()
    
    for item in UserIncorrectHistory:
        if item[6] == 'sentence_with_gap':
            sentence_with_gap_list.insert(-1, item[7])
        elif item[6] == 'token_translation_ask_l2':
            token_translation_ask_l2_list.insert(-1, item[7])
        elif item[6] == 'lemma_translation_ask_l1':
            lemma_translation_ask_l1_list.insert(-1, item[7])
        elif item[6] == 'lemma_translation_ask_l2':
            lemma_translation_ask_l2_list.insert(-1, item[7])
        elif item[6] == 'token_translation_ask_l2_audio':
            token_translation_ask_l2_audio_list.insert(-1, item[7])
        elif item[6] == 'lemma_translation_ask_l2_audio':
            lemma_translation_ask_l2_audio_list.insert(-1, item[7])
        elif item[6] == 'signed_video_ask_l2':
            signed_video_ask_l2_list.insert(-1, item[7])
    
    if FlashcardType == 'sentence_with_gap':
        Questions = sentence_with_gap_list
    elif FlashcardType == 'token_translation_ask_l2':
        Questions = token_translation_ask_l2_list
    elif FlashcardType == 'lemma_translation_ask_l1':
        Questions = lemma_translation_ask_l1_list
    elif FlashcardType == 'lemma_translation_ask_l2':
        Questions = lemma_translation_ask_l2_list
    elif FlashcardType == 'token_translation_ask_l2_audio':
        Questions = token_translation_ask_l2_audio_list
    elif FlashcardType == 'lemma_translation_ask_l2_audio':
        Questions = lemma_translation_ask_l2_audio_list
    elif FlashcardType == 'signed_video_ask_l2':
        Questions = signed_video_ask_l2_list

    return(Questions)

# filter out duplicates from list of questions
def filter_duplicate_questions(Questions):
    FilteredList = list(dict.fromkeys(Questions))
    return(FilteredList)

# generate new flashcard candidates for different types of old questions
def make_flashcard_candidates_to_repeat(UnorderedCandidates, FilteredQuestionsToRepeat):
    CandidatesToRepeat = list()
    for item in FilteredQuestionsToRepeat:
        for i in range(0, len(UnorderedCandidates)-1):
            if 'lemma' in UnorderedCandidates[i] and item.lower() == UnorderedCandidates[i]['lemma'].lower():
                CandidatesToRepeat.insert(-1, UnorderedCandidates[i])
            if 'sentence_with_gap' in UnorderedCandidates[i] and item.lower() == UnorderedCandidates[i]['sentence_with_gap'].lower():
                CandidatesToRepeat.insert(-1, UnorderedCandidates[i])
            if 'word' in UnorderedCandidates[i] and item.lower() == UnorderedCandidates[i]['word'].lower():
                CandidatesToRepeat.insert(-1, UnorderedCandidates[i])
            if 'word_audio' in UnorderedCandidates[i] and item.lower() == UnorderedCandidates[i]['word_audio'].lower():
                CandidatesToRepeat.insert(-1, UnorderedCandidates[i])
    return(CandidatesToRepeat)

# make new flashcards for selected set of questions from single user's history in LARA database
def make_candidates_from_history_failed_questions(UnorderedCandidates, DatabaseData, FlashcardType):   
    UserIncorrectHistory = get_user_incorrect_history(DatabaseData) 
    QuestionsForIncorrectAnswers = get_questions_for_incorrect_answers(UserIncorrectHistory, FlashcardType)
    FilteredQuestionsToRepeat = filter_duplicate_questions(QuestionsForIncorrectAnswers)
    NewCandidatesToRepeat = make_flashcard_candidates_to_repeat(UnorderedCandidates, FilteredQuestionsToRepeat)
    return(NewCandidatesToRepeat)

# The function below selects flashcard candidates according to chosen strategy. So far, there are 2 of them: default and retry_failed_questions.
    # DatabaseData in retry_failed_questions is a list of lists with the following data:
    # index 0: UserId (string)
    # index 1: ContentId (int)
    # index 2: ContentName (string)
    # index 3: LanguageName (string) 
    # index 4: FlashcardsSetID (int)
    # index 5: FlashcardNo (int)
    # index 6: FlashcardType (string, 7 types: 'sentence_with_gap', 'token_translation_ask_l2', 'token_translation_ask_l1', 
    #           'lemma_translation_ask_l2', 'lemma_translation_ask_l1', 'signed_video_ask_l2', 'lemma_translation_ask_l2_audio')
    # index 7: question (string)
    # index 8: answer (string)
    # index 9: answerStatus (string 'correct' or 'incorrect')

def order_candidates(UnorderedCandidates, Level, POS, UserId, Strategy, ContentId, Resources, FlashcardType):
    if Strategy == 'default':
        Candidates = order_candidates_default(UnorderedCandidates, Level, POS, UserId, Strategy, Resources)
    elif Strategy == 'retry_failed_questions':
        DatabaseData = lara_flashcards_mysql_connection_from_config.get_all_flashcard_db_data(UserId, ContentId)
        Candidates = make_candidates_from_history_failed_questions(UnorderedCandidates, DatabaseData, FlashcardType)
    return(Candidates)












