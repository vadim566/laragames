# Initial minimal version of flashcard-generation code

import lara_top
import lara_config
import lara_parse_utils
import lara_utils
import random

# Test on a few LARA texts in the repository (add more later)
def test_make_flashcards(Id):
    # Original Tina
    if Id == 'tina':
        ConfigFile = '$LARA/Content/tina_fer_i_fri/corpus/local_config.json'
        FlashcardType = 'lemma_translation_ask_l2'
        NCards = 10
        OutFile = '$LARA/tmp_resources/tina_flashcards.json'
    # Völuspá with kenningar
    elif Id == 'völuspá_kenningar':
        ConfigFile = '$LARA/Content/völuspá/corpus/local_config_kenningar.json'
        FlashcardType = 'token_translation_ask_l2'
        NCards = 10
        OutFile = '$LARA/tmp_resources/völuspá_kenningar_flashcards.json'
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
    # Tina, sentences with gaps
    elif Id == 'tina_gaps':
        ConfigFile = '$LARA/Content/tina_fer_i_fri/corpus/local_config.json'
        FlashcardType = 'sentence_with_gap'
        NCards = 10
        OutFile = '$LARA/tmp_resources/tina_with_gaps_flashcards.json'
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
    if not FlashcardType in _known_flashcard_types:
        lara_utils.print_and_flush(f'Error: flashcard type "{FlashcardType}" needs to be one of "{" ,".join(_known_flashcard_types)}"')
        return False
    return make_flashcards(ConfigFile, FlashcardType, NCards, OutFile)

# Make NCards flashcards
# of type FlashcardType
# from the LARA corpus defined by ConfigFile
# writing result to OutFile
def make_flashcards(ConfigFile, FlashcardType, NCards, OutFile):
    if not FlashcardType in _known_flashcard_types:
        lara_utils.print_and_flush(f'Error: unknow flashcard type {FlashcardType}')
        return False
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if not Params:
        lara_utils.print_and_flush(f'Error: unable to read config file {ConfigFile}')
        return False
    # Make the resources for this corpus in case they are out of date
    if not lara_top.compile_lara_local_resources(ConfigFile):
        lara_utils.print_and_flush(f'Error: unable make resources for {ConfigFile}')
        return False
    lara_utils.print_and_flush('\n======================\nCREATING FLASHCARDS\n======================\n')
    if FlashcardType == 'lemma_translation_ask_l2':
        return make_lemma_translation_ask_l2_flashcards(Params, NCards, OutFile)
    elif FlashcardType == 'token_translation_ask_l2':
        return make_token_translation_ask_l2_flashcards(Params, NCards, OutFile)
    elif FlashcardType == 'token_translation_ask_l2_audio':
        return make_token_translation_ask_l2_audio_flashcards(Params, NCards, OutFile)
    elif FlashcardType == 'signed_video_ask_l2':
        return make_signed_video_ask_l2_flashcards(Params, NCards, OutFile)
    elif FlashcardType == 'sentence_with_gap':
        return make_sentence_with_gap_flashcards(Params, NCards, OutFile)

# We will have more kinds of flashcards later, start with the following
_known_flashcard_types = (
    'lemma_translation_ask_l2',
    'token_translation_ask_l2',
    'token_translation_ask_l2_audio',
    'signed_video_ask_l2',
    'sentence_with_gap'
    )

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

def make_lemma_translation_ask_l2_flashcards(Params, NCards, OutFile):
    LemmaTranslationResourceFile = lara_top.lara_tmp_file('tmp_translation_spreadsheet_json', Params)
    Data = lara_utils.read_json_file(LemmaTranslationResourceFile)
    if Data == False:
        lara_utils.print_and_flush(f'Error: unable to read lemma translations file {LemmaTranslationResourceFile}')
        return False
    if len(Data) < 4:
        lara_utils.print_and_flush(f'Error: not enough examples in {LemmaTranslationResourceFile} to be able to create flashcards')
        return False
    # Initial strategy is very simple: choose random records to make the cards, choose random translations for the distractors.
    FlashcardRecords = []
    for I in range(0, NCards):
        FlashcardRecords += [ make_random_lemma_translation_ask_l2_flashcard(Data) ]
    lara_utils.write_json_to_file(FlashcardRecords, OutFile)

# We pick a random record for the question, then three more random records for the distractors
def make_random_lemma_translation_ask_l2_flashcard(Data):
    # Randomly shuffle the data from the file
    random.shuffle(Data)
    # Use the first record to get the question and the correct answer
    QuestionRecord = Data[0]
    ( Question, CorrectAnswer ) = ( QuestionRecord[0], QuestionRecord[1] )
    # Use the next three records to get the distractors
    Distractors = [ Record[1] for Record in Data[1:4] ]
    return { 'question': Question,
             'answer': CorrectAnswer,
             'distractors': Distractors
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

def make_token_translation_ask_l2_flashcards(Params, NCards, OutFile):
    TokenTranslationResourceFile = lara_top.lara_tmp_file('tmp_translation_spreadsheet_token_json', Params)
    Data = lara_utils.read_json_file(TokenTranslationResourceFile)
    if Data == False:
        lara_utils.print_and_flush(f'Error: unable to read token translations file {TokenTranslationResourceFile}')
        return False
    TranslationPairs = [ TranslationPair for Record in Data for TranslationPair in zip(Record[0], Record[1]) ]
    if len(TranslationPairs) < 4:
        lara_utils.print_and_flush(f'Error: not enough examples in {TokenTranslationResourceFile} to be able to create flashcards')
        return False
    # Initial strategy is very simple: choose random records to make the cards, choose random translations for the distractors.
    FlashcardRecords = []
    for I in range(0, NCards):
        FlashcardRecords += [ make_random_token_translation_ask_l2_flashcard(TranslationPairs) ]
    lara_utils.write_json_to_file(FlashcardRecords, OutFile)

# We pick a random record for the question, then three more random records for the distractors
def make_random_token_translation_ask_l2_flashcard(TranslationPairs):
    # Randomly shuffle the data from the file
    random.shuffle(TranslationPairs)
    # Use the first record to get the question and the correct answer
    QuestionRecord = TranslationPairs[0]
    ( Question, CorrectAnswer ) = ( QuestionRecord[0], QuestionRecord[1] )
    # Use the next three records to get the distractors
    Distractors = [ Record[1] for Record in TranslationPairs[1:4] ]
    return { 'question': Question,
             'answer': CorrectAnswer,
             'distractors': Distractors
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

def make_token_translation_ask_l2_audio_flashcards(Params, NCards, OutFile):
    if Params.word_audio_directory == '':
        lara_utils.print_and_flush(f'Error: directory for word audio not defined')
        return False
    else:
        WordAudioDir = Params.word_audio_directory
    WordAudioResourceFile = lara_top.lara_tmp_file('ldt_word_recording_file_full_json', Params)
    AudioData0 = lara_utils.read_json_file(WordAudioResourceFile)
    if AudioData0 == False:
        lara_utils.print_and_flush(f'Error: unable to read word audio file {WordAudioResourceFile}')
        return False
    # Convert the audio information into a dict where the keys are words and the value are full pathnames for audio files
    else:
        AudioData = { Record['text']: f"{WordAudioDir}/{Record['file']}"
                      for Record in AudioData0
                      if Record['file'] != '' }
    TokenTranslationResourceFile = lara_top.lara_tmp_file('tmp_translation_spreadsheet_token_json', Params)
    Data = lara_utils.read_json_file(TokenTranslationResourceFile)
    if Data == False:
        lara_utils.print_and_flush(f'Error: unable to read token translations file {TokenTranslationResourceFile}')
        return False
    TranslationPairs = [ audio_version_of_translation_pair(TranslationPair, AudioData) for Record in Data 
                         for TranslationPair in zip(Record[0], Record[1])
                         if audio_version_of_translation_pair(TranslationPair, AudioData) ]
    if len(TranslationPairs) < 4:
        lara_utils.print_and_flush(f'Error: not enough examples in {TokenTranslationResourceFile} to be able to create flashcards')
        return False
    # Initial strategy is very simple: choose random records to make the cards, choose random translations for the distractors.
    FlashcardRecords = []
    for I in range(0, NCards):
        FlashcardRecords += [ make_random_token_translation_ask_l2_audio_flashcard(TranslationPairs) ]
    lara_utils.write_json_to_file(FlashcardRecords, OutFile)

def audio_version_of_translation_pair(TranslationPair, AudioData):
    ( Word, Translation ) = TranslationPair
    return ( AudioData[Word], Translation ) if Word in AudioData else False

# We pick a random record for the question, then three more random records for the distractors
def make_random_token_translation_ask_l2_audio_flashcard(TranslationPairs):
    # Randomly shuffle the data from the file
    random.shuffle(TranslationPairs)
    # Use the first record to get the question and the correct answer
    QuestionRecord = TranslationPairs[0]
    ( Question, CorrectAnswer ) = ( QuestionRecord[0], QuestionRecord[1] )
    # Use the next three records to get the distractors
    Distractors = [ Record[1] for Record in TranslationPairs[1:4] ]
    return { 'question': Question,
             'answer': CorrectAnswer,
             'distractors': Distractors
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

def make_signed_video_ask_l2_flashcards(Params, NCards, OutFile):
    WordSignedVideoResourceFile = lara_top.lara_tmp_file('ldt_word_recording_file_full_json', Params)
    Data = lara_utils.read_json_file(WordSignedVideoResourceFile)
    if Data == False:
        lara_utils.print_and_flush(f'Error: unable to read word video file {WordSignedVideoResourceFile}')
        return False
    # It's called word_audio_directory because usually it's used for audio, but we use it for signed video too
    if Params.word_audio_directory == '':
        lara_utils.print_and_flush(f'Error: directory for word video not defined')
        return False
    else:
        WordVideoDir = Params.word_audio_directory
    WordVideoPairs = [ ( Record['text'], f"{WordVideoDir}/{Record['file']}" ) for Record in Data if Record['file'] != '' ]
    if len(WordVideoPairs) < 4:
        lara_utils.print_and_flush(f'Error: not enough examples in {WordSignedVideoResourceFile} to be able to create flashcards')
        return False
    # Initial strategy is very simple: choose random records to make the cards, choose random translations for the distractors.
    FlashcardRecords = []
    for I in range(0, NCards):
        FlashcardRecords += [ make_random_make_signed_video_ask_l2_flashcard(WordVideoPairs) ]
    lara_utils.write_json_to_file(FlashcardRecords, OutFile)

# We pick a random record for the question, then three more random records for the distractors
def make_random_make_signed_video_ask_l2_flashcard(WordVideoPairs):
    # Randomly shuffle the data from the file
    random.shuffle(WordVideoPairs)
    # Use the first record to get the question and the correct answer
    QuestionRecord = WordVideoPairs[0]
    ( Question, CorrectAnswer ) = ( QuestionRecord[0], QuestionRecord[1] )
    # Use the next three records to get the distractors
    Distractors = [ Record[1] for Record in WordVideoPairs[1:4] ]
    return { 'question': Question,
             'answer': CorrectAnswer,
             'distractors': Distractors
             }

# Question is a sentence with a gap, e.g. '"Mamma, komdu og ___, ég get gert með tveim boltum."'
# Possible answers are filler words, e.g. 'sjáðu', 'hleri', 'opnar', 'og'

# We get the information from the split file, whose structure is
# <Data> ::= list of <Pages>
# <Page> ::= [ <PageInfo>, list of <Segments> ]
# <Segment> ::= [ <Plain>, <Processed>, list of <TextLemmaPairs>, <Tag> ]
# <TextLemmaPair> ::= [ <Text> <Lemma> ]
# <Text> needs to be cleaned up to remove formatting. <Lemma> is null if <Text> is a non-word.
    
def make_sentence_with_gap_flashcards(Params, NCards, OutFile):
    SplitFile = lara_top.lara_tmp_file('split', Params)
    Data = lara_utils.read_json_file(SplitFile)
    if Data == False:
        lara_utils.print_and_flush(f'Error: unable to split file {SplitFile}')
        return False
    Sentences = extract_clean_sentences_from_split_file_contents(Data)
    GapSentenceFillerPairs = sentences_to_gap_filler_pairs(Sentences)
    if len(GapSentenceFillerPairs) < 4:
        lara_utils.print_and_flush(f'Error: not enough examples in {SplitFile} to be able to create flashcards')
        return False
    # Initial strategy is very simple: choose random records to make the cards, choose random translations for the distractors.
    FlashcardRecords = []
    for I in range(0, NCards):
        FlashcardRecords += [ make_random_sentence_with_gap_flashcard(GapSentenceFillerPairs) ]
    lara_utils.write_json_to_file(FlashcardRecords, OutFile)

# We pick a random record for the question, then three more random records for the distractors
def make_random_sentence_with_gap_flashcard(GapSentenceFillerPairs):
    # Randomly shuffle the data from the file
    random.shuffle(GapSentenceFillerPairs)
    # Use the first record to get the question and the correct answer
    QuestionRecord = GapSentenceFillerPairs[0]
    ( Question, CorrectAnswer ) = ( QuestionRecord[0], QuestionRecord[1] )
    # Use the next three records to get the distractors
    Distractors = [ Record[1] for Record in GapSentenceFillerPairs[1:4] ]
    return { 'question': Question,
             'answer': CorrectAnswer,
             'distractors': Distractors
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

             
test_make_flashcards('tina')