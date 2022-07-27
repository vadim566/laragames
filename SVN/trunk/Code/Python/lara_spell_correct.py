# Simple spelling correction routines

import lara_utils
import wagnerfischer as w
import math

_oov_shortlist_length = 50

domain_vocabulary = {}
guessed_oov_words = {}
all_words_and_vectors = {}
oov_initialised = False

def init_domain_vocabulary_if_necessary(DomainId, Vocabulary):
    if not DomainId in domain_vocabulary:
        init_domain_vocabulary(DomainId, Vocabulary)

def init_domain_vocabulary(DomainId, Vocabulary):
    global domain_vocabulary
    global guessed_oov_words
    global oov_initialised
    guessed_oov_words[DomainId] = {}
    domain_vocabulary[DomainId] = {}
    for Word in Vocabulary:
        domain_vocabulary[DomainId][Word] = word_to_vector(Word)
    init_all_words_and_vectors_table(DomainId)
    oov_initialised = True
    print(f'--- Initialised OOV word guessing for domain = "{DomainId}"')

def init_all_words_and_vectors_table(DomainId):
    global all_words_and_vectors
    all_words_and_vectors[DomainId] = find_all_words_and_vectors(DomainId)
        
def find_all_words_and_vectors(DomainId):
    global domain_vocabulary
    return [ (Word, domain_vocabulary[DomainId][Word] ) for Word in domain_vocabulary[DomainId] ]

def get_all_words_and_vectors(DomainId):
    global all_words_and_vectors
    if DomainId in all_words_and_vectors :
        return all_words_and_vectors[DomainId]
    else:
        return []

def guess_word(Word, Threshold, DomainId):
    global domain_vocabulary
    global oov_initialised
    if not oov_initialised:
        return Word
    elif not DomainId in domain_vocabulary:
        return Word
    elif ( Word == '' ):
        return Word
    elif in_vocabulary(Word, DomainId):
        return Word
    elif guessed_oov_word(Word, DomainId):
        return guessed_oov_word(Word, DomainId)
    else:
        ( GuessedWord, Score ) = guess_oov_word(Word, DomainId)
        if ( Score >= Threshold ):
            store_guessed_oov_word(Word, DomainId, GuessedWord)
            return GuessedWord
        else:
            return Word

def in_vocabulary(Word, DomainId):
    global domain_vocabulary
    return DomainId in domain_vocabulary and Word in domain_vocabulary[DomainId]

def guessed_oov_word(Word, DomainId):
    global guessed_oov_words
    if DomainId in guessed_oov_words and Word in guessed_oov_words[DomainId] :
        return guessed_oov_words[DomainId][Word]
    else:
        return False

def store_guessed_oov_word(Word, DomainId, GuessedWord):
    global guessed_oov_words
    guessed_oov_words[DomainId][Word] = GuessedWord

def guess_oov_word(Word, DomainId):
    AllWordsAndVectors = get_all_words_and_vectors(DomainId)
    Shortlist = get_oov_shortlist(Word, AllWordsAndVectors)
    return guess_oov_word1(Word, Shortlist)

def get_oov_shortlist(Word, AllWordsAndVectors):
    N = _oov_shortlist_length
    Vector = word_to_vector(Word)
    ScoredWords = [ [ Word1, inner_product(Vector, Vector1) ]
                    for (Word1, Vector1) in AllWordsAndVectors ]
    SortedScoredWords = sorted(ScoredWords, key=lambda x: x[1], reverse=True)
    return SortedScoredWords[:N]

def guess_oov_word1(Word, Shortlist):
    ScoredWords = [ [ Word1, string_match_score(Word, Word1) ] for
                    ( Word1, CosineScore ) in Shortlist ]
    SortedScoredWords = sorted(ScoredWords, key=lambda x: x[1], reverse=True)
    return SortedScoredWords[0]

def string_match_score(Word, Word1):
    Length = len(Word)
    if ( Length == 0 ):
        return 0
    else:
        return ( Length - w.WagnerFischer(Word, Word1).cost ) / Length

# -----------------------------------------

# Representing words as sparse vectors so we can do cosine distance efficiently

def word_to_vector(Word):
    return normalise_vector(list_to_vector(word_features(Word), {}))

def word_features(Word):
    return list(Word) + char_bigrams(Word)

def list_to_vector(List, Vec):
    if ( List == [] ):
        return Vec
    else:
        inc_count(Vec, List[0])
        return list_to_vector(List[1:], Vec)

def inc_count(Vec, Key):
    if ( Key in Vec ):
        Vec[Key] = Vec[Key] + 1
    else:
        Vec[Key] = 1

def normalise_vector(Vec):
    VecLength = vector_length(Vec)
    if ( VecLength == 0 ):
        VecLengthInverse = 1
    else:
        VecLengthInverse = 1.0 / VecLength
    return scalar_multiply(VecLengthInverse, Vec)

def vector_length(Vec):
    return math.sqrt(sum([ Vec[Key] * Vec[Key] for Key in Vec ]))

def scalar_multiply(K, Vec):
    return { Key:( K * Vec[Key]) for Key in Vec }

def inner_product(Vec1, Vec2):
    return sum([ Vec1[Key] * Vec2[Key] for Key in Vec1 if Key in Vec2 ] )

def char_bigrams(Word):
    if ( len(Word) < 2 ):
        return []
    else:
        return [ tuple([ Word[I], Word[I+1] ]) for I in range(0, len(Word)-1) ]
    
