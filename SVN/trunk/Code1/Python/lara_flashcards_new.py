# Revised version of flashcard-generation code

import lara_flashcards_resources
import lara_flashcards_order
import lara_top
import lara_config
import lara_parse_utils
import lara_utils
import random
from nltk.metrics import distance
import lara_treetagger
import lara_translations
import lara_audio
import lara_mwe

# Comment in the 'True' line and comment out the 'False' line to print trace information.
#_flashcard_trace = True
_flashcard_trace = False

# Test on a few LARA texts in the repository
def test_make_flashcards(Id):
    # Barngarla
    if Id == 'barngarla_audio':
        ConfigFile = '$LARA/Content/barngarla_alphabet/corpus/local_config.json'
        FlashcardType = 'lemma_translation_ask_l2_audio'
        NCards = 10
        Level = 'intermediate'
        POS = 'any'
        OutFile = '$LARA/tmp_resources/barngarla_flashcards_audio_new.json'
    # Barngarla
    elif Id == 'barngarla_translation':
        ConfigFile = '$LARA/Content/barngarla_alphabet/corpus/local_config.json'
        FlashcardType = 'lemma_translation_ask_l2'
        NCards = 10
        Level = 'beginner'
        POS = 'any'
        OutFile = '$LARA/tmp_resources/barngarla_flashcards_translation_new.json'
    # Genesis in Swedish, lemma translations
    elif Id == 'genesis_swedish':
        ConfigFile = '$LARA/Content/sample_swedish/corpus/local_config.json'
        FlashcardType = 'lemma_translation_ask_l2'
        NCards = 10
        Level = 'intermediate'
        POS = 'any'
        OutFile = '$LARA/tmp_resources/genesis_swedish_lemma_translations_flashcards_new.json'
    # Völuspá token translation
    elif Id == 'völuspá_translation_nouns':
        ConfigFile = '$LARA/Content/völuspá/corpus/local_config.json'
        FlashcardType = 'token_translation_ask_l2'
        NCards = 10
        Level = 'beginner'
        POS = 'nouns'
        OutFile = '$LARA/tmp_resources/völuspá_translation_flashcards_new.json'
    # Völuspá token translation
    elif Id == 'völuspá_translation_anyPOS':
        ConfigFile = '$LARA/Content/völuspá/corpus/local_config.json'
        FlashcardType = 'token_translation_ask_l2'
        NCards = 10
        Level = 'intermediate'
        POS = 'any'
        OutFile = '$LARA/tmp_resources/völuspá_translation_flashcards_new.json'
    # Völuspá sentences with gaps
    elif Id == 'völuspá_gaps_adjectives':
        ConfigFile = '$LARA/Content/völuspá/corpus/local_config.json'
        FlashcardType = 'sentence_with_gap'
        NCards = 10
        Level = 'intermediate'
        POS = 'adjectives'
        OutFile = '$LARA/tmp_resources/völuspá_gaps_flashcards_new.json'
    # Le petit prince
    elif Id == 'le_petit_prince_verbs':
        ConfigFile = '$LARA/Content/le_petit_prince/corpus/local_config.json'
        FlashcardType = 'token_translation_ask_l2'
        NCards = 20
        Level = 'intermediate'
        POS = 'verbs'
        OutFile = '$LARA/tmp_resources/le_petit_prince_flashcards_new.json'
    # Hur gick det sen
    elif Id == 'hur_gick_det_sen_advanced_prepositions':
        ConfigFile = '$LARA/Content/hur_gick_det_sen/corpus/local_config.json'
        FlashcardType = 'token_translation_ask_l2'
        NCards = 20
        Level = 'advanced'
        POS = 'prepositions'
        OutFile = '$LARA/tmp_resources/hur_gick_det_sen_flashcards_advanced.json'
    # Hur gick det sen
    elif Id == 'hur_gick_det_sen_beginner_nouns':
        ConfigFile = '$LARA/Content/hur_gick_det_sen/corpus/local_config.json'
        FlashcardType = 'token_translation_ask_l2'
        NCards = 20
        Level = 'beginner'
        POS = 'nouns'
        OutFile = '$LARA/tmp_resources/hur_gick_det_sen_flashcards_beginner.json'
    # Hur gick det sen
    elif Id == 'hur_gick_det_sen_multiwords':
         ConfigFile = '$LARA/Content/hur_gick_det_sen/corpus/local_config.json'
         FlashcardType = 'token_translation_ask_l2'
         NCards = 5
         Level = 'multiword_expressions'
         POS = 'any'
         OutFile = '$LARA/tmp_resources/hur_gick_det_sen_flashcards_multiwords.json'
    # Huis clos translation
    elif Id == 'huis_clos_translation':
        ConfigFile = '$LARA/Content/huis_clos/corpus/local_config.json'
        FlashcardType = 'token_translation_ask_l2'
        NCards = 20
        Level = 'intermediate'
        OutFile = '$LARA/tmp_resources/huis_clos_translation_flashcards_new.json'
    # Le petit prince audio
    elif Id == 'le_petit_prince_audio':
        ConfigFile = '$LARA/Content/le_petit_prince/corpus/local_config.json'
        FlashcardType = 'token_translation_ask_l2_audio'
        NCards = 20
        Level = 'intermediate'
        POS = 'numerals'
        OutFile = '$LARA/tmp_resources/le_petit_prince_audio_flashcards_new.json'
    # Huis clos gaps
    elif Id == 'huis_clos_gaps':
        ConfigFile = '$LARA/Content/huis_clos/corpus/local_config.json'
        FlashcardType = 'sentence_with_gap'
        NCards = 20
        Level = 'intermediate'
        POS = 'any'
        OutFile = '$LARA/tmp_resources/huis_clos_translation_flashcards_new.json'
    # Antigone
    elif Id == 'antigone':
        ConfigFile = '$LARA/Content/antigone/corpus/local_config_nahed_marta_chadi.json'
        FlashcardType = 'token_translation_ask_l2'
        NCards = 20
        Level = 'intermediate'
        POS = 'any'
        OutFile = '$LARA/tmp_resources/antigone_flashcards_new.json'
    # Antigone EN
    elif Id == 'antigone_en':
        ConfigFile = '$LARA/Content/antigone_en/corpus/local_config_rosa_kirsten.json'
        FlashcardType = 'token_translation_ask_l2'
        NCards = 20
        Level = 'intermediate'
        POS = 'any'
        OutFile = '$LARA/tmp_resources/antigone_en_flashcards_new.json'
    # Peter Rabbit translation
    elif Id == 'peter_rabbit_ask_l2':
        ConfigFile = '$LARA/Content/peter_rabbit/corpus/local_config.json'
        FlashcardType = 'lemma_translation_ask_l2'
        NCards = 10
        Level = 'intermediate'
        POS = 'pronouns'
        OutFile = '$LARA/tmp_resources/peter_rabbit_ask_l2_flashcards_new.json'
    # Peter Rabbit reverse_translation
    elif Id == 'peter_rabbit_ask_l1':
        ConfigFile = '$LARA/Content/peter_rabbit/corpus/local_config.json'
        FlashcardType = 'lemma_translation_ask_l1'
        NCards = 10
        Level = 'intermediate'
        POS = 'adverbs'
        OutFile = '$LARA/tmp_resources/peter_rabbit_ask_l1_flashcards_new.json'
    # Polly's McColley text, token translations
    elif Id == 'mc_colley':
        ConfigFile = '$LARA/Content/mccolley_philodendron/corpus/local_config.json'
        FlashcardType = 'token_translation_ask_l2'
        NCards = 20
        Level = 'intermediate'
        POS = 'any'
        OutFile = '$LARA/tmp_resources/mc_colley_token_flashcards_new.json'
    # Tina with ÍTM annotations
    elif Id == 'tina_signed':
        ConfigFile = '$LARA/Content/tina_signed/corpus/local_config.json'
        FlashcardType = 'signed_video_ask_l2'
        NCards = 10
        Level = 'intermediate'
        POS = 'any'
        OutFile = '$LARA/tmp_resources/tina_signed_flashcards_new.json'
    else:
        lara_utils.print_and_flush(f'Error: unknown test ID {Id}')
        return False
    UserId = 'larauser'
    Strategy = 'default'
    ContentId = 'ContentName'
    make_flashcards(ConfigFile, FlashcardType, NCards, Level, POS, UserId, Strategy, ContentId, OutFile)

# Make NCards flashcards
# from the LARA corpus defined by ConfigFile, with the flashcard tyoe defined by the config
# writing result to OutFile
def make_flashcards_for_config_file(ConfigFile, NCards, Level, POS, UserId, Strategy, ContentId, OutFile):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if not Params:
        lara_utils.print_and_flush(f'Error: unable to read config file {ConfigFile}')
        return False
    FlashcardType = Params.flashcard_type
    return make_flashcards(ConfigFile, FlashcardType, NCards, Level, POS, UserId, Strategy, ContentId, OutFile)

# Make NCards flashcards
# of type FlashcardType
# from the LARA corpus defined by ConfigFile
# writing result to OutFile
def make_flashcards(ConfigFile, FlashcardType, NCards, Level, POS, UserId, Strategy, ContentId, OutFile):
    if not FlashcardType in lara_config._known_flashcard_types:
        lara_utils.print_and_flush(f'*** Error: unknow flashcard type {FlashcardType}')
        return False
    if not Level in lara_config._known_flashcard_levels:
        lara_utils.print_and_flush(f'*** Error: unknow flashcard level {Level}')
        return False
    # Call lara_flashcards_resources to make all the LARA resources we need 
    Resources = lara_flashcards_resources.make_flashcard_resources(ConfigFile)
    if not isinstance(Resources, dict):
        lara_utils.print_and_flush(f'*** Error: unable to generate flashcard resources')
        return False
    # Make the candidate records
    UnorderedCandidates = make_flashcard_candidate_records(FlashcardType, Resources)
    # Print some debugging information if trace is on.
    if _flashcard_trace == True:
        lara_utils.print_and_flush('--- Unordered candidates:')
        lara_utils.prettyprint(UnorderedCandidates[:5])
    Candidates = lara_flashcards_order.order_candidates(UnorderedCandidates, Level, POS, UserId, Strategy, ContentId, Resources, FlashcardType)
    # Print some debugging information if trace is on.
    if _flashcard_trace == True:
        lara_utils.print_and_flush('--- Ordered candidates:')
        lara_utils.prettyprint(Candidates[:5])
    # Now walk down the shuffled list of candidates and try to make NCards flashcards.
    # Discard ones where we fail to make the flashcard or repeat a question/answer.
    ( FlashcardRecords, FlashcardQuestions, FlashcardAnswers, Index, NCandidates ) = ( [], [], [], 0, len(Candidates) )
    while len(FlashcardRecords) < NCards and Index < NCandidates:
        Flashcard = make_flashcard(FlashcardType, Candidates, Index, FlashcardQuestions)
        if not Flashcard == False and \
           not Flashcard['question']['value'] in FlashcardQuestions and \
           not Flashcard['answer']['value'] in FlashcardAnswers:
            FlashcardRecords += [ Flashcard ]
            FlashcardQuestions += [ Flashcard['question']['value'] ]
            FlashcardAnswers += [ Flashcard['answer']['value'] ]
        Index += 1
    if len(FlashcardRecords) < NCards:
            lara_utils.print_and_flush(f'*** Warning: only created {len(FlashcardRecords)} Flashcards')
    #lara_utils.write_json_to_file(FlashcardRecords, OutFile)
    lara_utils.write_json_to_file_plain_utf8(FlashcardRecords, OutFile)

# We need to make the candidate records differently for the different kinds of flashcards                                                                                               
def make_flashcard_candidate_records(FlashcardType, Resources):
    if FlashcardType == 'lemma_translation_ask_l2':
        return make_lemma_translation_ask_l2_candidate_records(Resources)
    elif FlashcardType == 'lemma_translation_ask_l1':
        return make_lemma_translation_ask_l1_candidate_records(Resources)
    elif FlashcardType == 'token_translation_ask_l2':
        return make_token_translation_ask_l2_candidate_records(Resources)
    elif FlashcardType == 'token_translation_ask_l2_audio':
        return make_token_translation_ask_l2_audio_candidate_records(Resources)
    elif FlashcardType == 'signed_video_ask_l2':
        return make_signed_video_ask_l2_candidate_records(Resources)
    elif FlashcardType == 'sentence_with_gap':
        return make_sentence_with_gap_candidate_records(Resources)
    elif FlashcardType == 'lemma_translation_ask_l2_audio':
        return make_lemma_translation_ask_l2_audio_candidate_records(Resources)

# Lemma translation with L2 question.
# The candidate contains a lemma (question), its translation (answer), POS, and context.
def make_lemma_translation_ask_l2_candidate_records(Resources):
    Lemma2TranslationAndContextDict = Resources['lemma2translation_and_context_dict']
    Lemma2PosDict = Resources['lemma2POS_dict']
    Segment2MultimediaDict = Resources['segment2multimedia_dict']
    Records = []
    for Lemma in Lemma2TranslationAndContextDict:
        TranslationAndContext = Lemma2TranslationAndContextDict[Lemma]
        Context = TranslationAndContext['context']
        Record = { 'lemma': Lemma,
                   'translation': TranslationAndContext['translation'],
                   'text_context': TranslationAndContext['context'],
                   'pos': look_up(Lemma2PosDict, Lemma),
                   'multimedia_context': look_up(Segment2MultimediaDict, Context)
                   }
        Records += [ Record]
    return Records

# Lemma translation with L1 question.
# The candidate contains a lemma (answer), its translation (question), and POS.
def make_lemma_translation_ask_l1_candidate_records(Resources):
    Translation2LemmaAndContextDict = Resources['translation2lemma_and_context_dict']
    Lemma2PosDict = Resources['lemma2POS_dict']
    Segment2MultimediaDict = Resources['segment2multimedia_dict']
    Records = []
    for Translation in Translation2LemmaAndContextDict:
        LemmaAndContext = Translation2LemmaAndContextDict[Translation]
        Lemma = LemmaAndContext['lemma']
        Record = { 'translation': Translation,
                   'lemma': LemmaAndContext['lemma'],
                   'pos': look_up(Lemma2PosDict, Lemma)
                   }
        Records += [ Record]
    return Records

# Token translation with L2 question.
# The candidate contains a word (question), its translation (answer), POS, and context.
def make_token_translation_ask_l2_candidate_records(Resources):
    Word2TranslationAndContextDict = Resources['word2tokentranslation_and_context_dict']
    Word2PosDict = Resources['word2POS_dict']
    Segment2MultimediaDict = Resources['segment2multimedia_dict']
    Records = []
    for Word in Word2TranslationAndContextDict:
        TranslationAndContext = Word2TranslationAndContextDict[Word]
        Translation = TranslationAndContext['translation']
        Context = TranslationAndContext['context']
        Record = { 'word': Word,
                   'translation': Translation,
                   'text_context': Context,
                   'pos': look_up(Word2PosDict, Word),
                   'multimedia_context': look_up(Segment2MultimediaDict, Context)
                   }
        Records += [ Record]
    return Records

# Token translation with L2 audio question.
# The candidate contains a word, a word audio (question), its translation (answer), POS, and context.
def make_token_translation_ask_l2_audio_candidate_records(Resources):
    Word2TranslationAndContextDict = Resources['word2tokentranslation_and_context_dict']
    Word2PosDict = Resources['word2POS_dict']
    Segment2MultimediaDict = Resources['segment2multimedia_dict']
    Word2MultimediaDict = Resources['word2multimedia_dict']
    Records = []
    for Word in Word2TranslationAndContextDict:
        TranslationAndContext = Word2TranslationAndContextDict[Word]
        Context = TranslationAndContext['context']
        RegularisedWord = lara_audio.make_word_canonical_for_word_recording(Word)
        if RegularisedWord in Word2MultimediaDict:
            Record = { 'word': Word,
                       'word_audio': Word2MultimediaDict[RegularisedWord],
                       'translation': TranslationAndContext['translation'],
                       'text_context': TranslationAndContext['context'],
                       'pos': look_up(Word2PosDict, Word),
                       'multimedia_context': look_up(Segment2MultimediaDict, Context)
                       }
            Records += [ Record]
    return Records

# Signed word videos.
# The candidate contains a word (answer), a word video (question), a POS, and multimedia context.
# Things are done in a rather non-standard way with sign language.
# The multimedia word directory is indexed on lowercased lemmas rather than words.
def make_signed_video_ask_l2_candidate_records(Resources):
    Lemma2ContextDict = Resources['lemma2context_dict']
    Lemma2PosDict = Resources['lemma2POS_dict']
    Segment2MultimediaDict = Resources['segment2multimedia_dict']
    # For sign-language annotated texts, this is actually a lemma to multimedia dict
    Word2MultimediaDict = Resources['word2multimedia_dict']
    Records = []
    for Lemma in Lemma2ContextDict:
        RegularisedLemma = regularise_lemma_for_sign_language_multimedia_dict(Lemma)
        if RegularisedLemma in Word2MultimediaDict:
            Context = Lemma2ContextDict[Lemma]
            if Context in Segment2MultimediaDict:
                Record = { 'lemma': Lemma,
                           'word_video': Word2MultimediaDict[RegularisedLemma],
                           'pos': look_up(Lemma2PosDict, Lemma),
                           'multimedia_context': Segment2MultimediaDict[Context]
                           }
                Records += [ Record]
    return Records

def regularise_lemma_for_sign_language_multimedia_dict(Lemma):
    return Lemma.lower()

# Sentence with gap
# The candidate contains a word (answer), a sentence with a gap (question), a POS, and context.
def make_sentence_with_gap_candidate_records(Resources):
    SentencesAndWordPairsList = Resources['sentences_and_word_pairs_list']
    Word2PosDict = Resources['word2POS_dict']
    Segment2MultimediaDict = Resources['segment2multimedia_dict']
    Records = []
    SentenceGapFillerList = sentences_and_words_to_sentences_sentences_with_gaps_and_fillers(SentencesAndWordPairsList)
    for SentenceSentenceWithGapAndWord in SentenceGapFillerList:
        Sentence = SentenceSentenceWithGapAndWord['sentence']
        SentenceWithGap = SentenceSentenceWithGapAndWord['sentence_with_gap']
        Word = SentenceSentenceWithGapAndWord['word']
        Record = { 'word': Word,
                   'sentence_with_gap': SentenceWithGap,
                   'text_context': Sentence,
                   'pos': look_up(Word2PosDict, Word),
                   'multimedia_context': look_up(Segment2MultimediaDict, Sentence)
                   }
        Records += [ Record]
    return Records

# Create a list of possible sentence/sentence-with-gap/word objects
def sentences_and_words_to_sentences_sentences_with_gaps_and_fillers(SentencesAndWordPairsList):
    return [ sentence_and_pairs_to_sentence_gap_and_filler(Sentence, Pairs, Index)
             for ( Sentence, Pairs ) in SentencesAndWordPairsList
             for Index in range(0, len(Pairs))
             # If Pairs[Index][1] == '', then the element at that index isn't a word, so we can't replace it with a gap
             if Pairs[Index][1] != '' ]

def sentence_and_pairs_to_sentence_gap_and_filler(Sentence, Pairs, IndexOfGap):
    SentenceWithGap = ''.join([ Pairs[Index][0] if Index != IndexOfGap else '_____'
                                for Index in range(0, len(Pairs)) ])
    return { 'sentence': Sentence,
             'sentence_with_gap': clean_up_newlines_and_spaces(SentenceWithGap),
             'word': Pairs[IndexOfGap][0] }

# Turn newlines into spaces, remove leading and trailing spaces, consolidate spaces
def clean_up_newlines_and_spaces(Sentence):
    Sentence1 = Sentence.replace('\n', ' ').strip()
    return ' '.join(Sentence1.split())

# This is a hack to use with Barngarla content.
# Omit text context and multimedia context, they aren't good in those texts.
# Also there is no POS, and exploit the fact that words and lemmas are the same.
def make_lemma_translation_ask_l2_audio_candidate_records(Resources):
    Lemma2TranslationAndContextDict = Resources['lemma2translation_and_context_dict']
    Word2MultimediaDict = Resources['word2multimedia_dict']
    Records = []
    for Lemma in Lemma2TranslationAndContextDict:
        TranslationAndContext = Lemma2TranslationAndContextDict[Lemma]
        if Lemma in Word2MultimediaDict:
            Record = { 'lemma': Lemma,
                       'word_audio': Word2MultimediaDict[Lemma],
                       'translation': TranslationAndContext['translation'],
                       'pos': 'None'
                       }
            Records += [ Record]
    return Records

# Try to make a flashcard from the I-th record in Candidates
def make_flashcard(FlashcardType, Candidates, I, FlashcardQuestions):
    ThisCandidate = Candidates[I]
    ThisQuestion = get_question_element_from_candidate(FlashcardType, ThisCandidate)
    ThisAnswer = get_answer_element_from_candidate(FlashcardType, ThisCandidate)
    # Create a list of possible distractors from the candidates,
    # giving the question, the answer, and the edit distance to the current candidate
    DistractorsAndDistances = [ { 'answer': get_answer_element_from_candidate(FlashcardType, Candidates[J]),
                                  'question': get_question_element_from_candidate(FlashcardType, Candidates[J]),
                                  'distance': distance_between_candidates(FlashcardType, ThisCandidate, Candidates[J]) }
                                for J in range(0, len(Candidates))
                                if candidates_have_matching_pos(ThisCandidate, Candidates[J]) ]
    # Sort by distance, closest first
    SortedDistractorsAndDistances = sorted(DistractorsAndDistances, key=lambda x: x['distance'])
    SelectedQuestions = []
    SelectedAnswers = [ ]
    # Walk down the list of candidate distractors to find 3 possibilities
    # Discard ones that have the same question or answer as the current candidate or any previous distractor.
    for DistractorAndDistance in SortedDistractorsAndDistances:
        Question = DistractorAndDistance['question']
        Answer = DistractorAndDistance['answer']
        if not Question in [ ThisQuestion ] + SelectedQuestions and not Answer in [ ThisAnswer ] + SelectedAnswers:
            SelectedQuestions += [ Question ]
            SelectedAnswers += [ Answer ]
            if len(SelectedAnswers) == 3:
                # We have enough distractors
                Distractors = answers_to_distractors(SelectedAnswers)
                return make_flashcard_from_candidate_and_distractors(FlashcardType, ThisCandidate, Distractors)
    # We couldn't find enough distractors! Give up.
    return False

# Convert a list of answer to a list of formatted distractors to include in the flashcard
def answers_to_distractors(Answers):
    return [ { 'value': Answer.capitalize(), 'type': 'raw_text' }
             for Answer in Answers ]

def get_question_element_from_candidate(FlashcardType, Candidate):
    return get_question_element_and_type_from_candidate(FlashcardType, Candidate)[0]

# Find the question element and the type of the question element in a candidate.
def get_question_element_and_type_from_candidate(FlashcardType, Candidate):
    if FlashcardType == 'lemma_translation_ask_l2':
        return ( Candidate['lemma'], 'raw_text' )
    elif FlashcardType == 'lemma_translation_ask_l1':
        return ( Candidate['translation'], 'raw_text' )
    elif FlashcardType == 'token_translation_ask_l2':
        return ( Candidate['word'], 'raw_text' )
    elif FlashcardType == 'token_translation_ask_l2_audio':
        return ( Candidate['word_audio'], 'audio_file_name' )
    elif FlashcardType == 'signed_video_ask_l2':
        return ( Candidate['word_video'], 'video_file_name' )
    elif FlashcardType == 'sentence_with_gap':
        return ( Candidate['sentence_with_gap'], 'raw_text' )
    elif FlashcardType == 'lemma_translation_ask_l2_audio':
        return ( Candidate['word_audio'], 'audio_file_name' )

def get_answer_element_from_candidate(FlashcardType, Candidate):
    ( Answer, Type ) = get_answer_element_and_type_from_candidate(FlashcardType, Candidate)
    return Answer.lower() if Type == 'raw_text' else Answer

# Find the answer element and the type of the question element in a candidate.
def get_answer_element_and_type_from_candidate(FlashcardType, Candidate):
    if FlashcardType == 'lemma_translation_ask_l2':
        return ( Candidate['translation'], 'raw_text' )
    elif FlashcardType == 'lemma_translation_ask_l1':
        return ( Candidate['lemma'], 'raw_text' )
    elif FlashcardType == 'token_translation_ask_l2':
        return ( Candidate['translation'], 'raw_text' )
    elif FlashcardType == 'token_translation_ask_l2_audio':
        return ( Candidate['translation'], 'raw_text' )
    elif FlashcardType == 'signed_video_ask_l2':
        return ( Candidate['lemma'], 'raw_text' )
    elif FlashcardType == 'sentence_with_gap':
        return ( Candidate['word'], 'raw_text' )
    elif FlashcardType == 'lemma_translation_ask_l2_audio':
        return ( Candidate['translation'], 'raw_text' )

# Find the edit distance between two candidates of a given type.
def distance_between_candidates(FlashcardType, Candidate1, Candidate2):
    if FlashcardType == 'lemma_translation_ask_l2':
        return distance.edit_distance(Candidate1['lemma'], Candidate2['lemma'])
    elif FlashcardType == 'lemma_translation_ask_l1':
        return distance.edit_distance(Candidate1['lemma'], Candidate2['lemma'])
    elif FlashcardType == 'token_translation_ask_l2':
        return distance.edit_distance(Candidate1['word'], Candidate2['word'])
    elif FlashcardType == 'token_translation_ask_l2_audio':
        return distance.edit_distance(Candidate1['word'], Candidate2['word'])
    elif FlashcardType == 'signed_video_ask_l2':
        return distance.edit_distance(Candidate1['lemma'], Candidate2['lemma'])
    elif FlashcardType == 'sentence_with_gap':
        return distance.edit_distance(Candidate1['word'], Candidate2['word'])
    elif FlashcardType == 'lemma_translation_ask_l2_audio':
        return distance.edit_distance(Candidate1['lemma'], Candidate2['lemma'])

def candidates_have_matching_pos(Candidate1, Candidate2):
    return Candidate1['pos'] == Candidate2['pos'] if 'pos' in Candidate1 else True

# Package up a candidate and a set of distractors as a flashcard dict
def make_flashcard_from_candidate_and_distractors(FlashcardType, Candidate, Distractors):
    ( Question, QuestionType ) = get_question_element_and_type_from_candidate(FlashcardType, Candidate)
    ( Answer, AnswerType ) = get_answer_element_and_type_from_candidate(FlashcardType, Candidate)
    FormattedAnswer = Answer.capitalize() if AnswerType == 'raw_text' else Answer
    FormattedQuestion = Question.capitalize() if QuestionType == 'raw_text' else Question
    if 'text_context' in Candidate and 'multimedia_context' in Candidate:
        TextContext = Candidate['text_context']
        MultimediaContext = Candidate['multimedia_context']
        return { 'question': {'value': FormattedQuestion, 'type': QuestionType} ,
                 'answer': {'value': FormattedAnswer, 'type': AnswerType},
                 'distractors': Distractors,
                 'text_context': {'value':TextContext, 'type': 'raw_text'},
                 'multimedia_context': {'value': MultimediaContext, 'type': 'audio_file_name'}
                 }
    else:
        return { 'question': {'value': FormattedQuestion, 'type' : QuestionType} ,
                 'answer': {'value': FormattedAnswer, 'type' : AnswerType},
                 'distractors': Distractors,
                 'text_context': '',
                 'multimedia_context': ''
                 }

def look_up(Dict, Key):
    return Dict[Key] if Key in Dict else ''
