import os
import glob 
import sys
import re
import lara_utils

def remove_furigana(HTMLInFile, UnicodeOutFile):
    from bs4 import BeautifulSoup
    #from tinysegmenter import *
    import tinysegmenter
    
    # Remove ruby and <rt> <rp> tags from text
    InStr = lara_utils.read_lara_text_file(HTMLInFile)
    #with open(lara_utils.absolute_file_name(HTMLInFile), 'r') as f:
    #    input = f.read()

    soup = BeautifulSoup(InStr, features="lxml")
    tagname = 'rt'
    for tag in soup.findAll(tagname):
        tag.extract()

    tagname = 'rp'
    for tag in soup.findAll(tagname):
        tag.extract()
    
    tagname = 'span'
    for tag in soup.findAll(tagname):
    	tag.extract()
    #nonruby = unicode(soup)
    nonruby = str(soup)

    # Remove all HTML tags and attributes, then write out the file 
    nonruby = re.sub('<[^<]+?>', '', nonruby)
    
    segmenter = tinysegmenter.TinySegmenter() 
    
    tokenized = segmenter.tokenize(nonruby)
    #tokenized = tokenized[0:(tokenized.index(u'底本'))-1]
      
    tokenized = ''.join(tokenized)

    lara_utils.write_lara_text_file(tokenized, UnicodeOutFile)

def sentence_segment_japanese_file(InFile, OutFile):
    InStr = lara_utils.read_lara_text_file(InFile)
    if InStr == False:
        lara_utils.print_and_flush(f'*** Error: unable to segment file')
        return False
    Sentences = sentence_segment_string(InStr)
    OutStr = '||'.join(Sentences)
    lara_utils.write_lara_text_file(OutStr, OutFile)
    lara_utils.print_and_flush(f'--- Written segmented file ({len(Sentences)}) {OutFile}')
    return True

def sentence_segment_string(InStr):
    ( I, N, Sentences, CurrentSentence ) = ( 0, len(InStr), [], '' )
    while True:
        if I >= N:
            if CurrentSentence != '':
                Sentences += [ CurrentSentence ]
            return Sentences
        c1 = InStr[I]
        c2 = InStr[I+1] if I+1 < N else False
        if is_sentence_final_japanese_punctuation_mark(c1) and c2 != False and is_japanese_close_quote(c2):
            CurrentSentence += f'{c1}{c2}'
            Sentences += [ CurrentSentence ]
            CurrentSentence = ''
            I += 2
        elif is_sentence_final_japanese_punctuation_mark(c1):
            CurrentSentence += f'{c1}'
            Sentences += [ CurrentSentence ]
            CurrentSentence = ''
            I += 1
        else:
            CurrentSentence += c1
            I += 1
    # Should never get here but just in case
    return Sentences

def is_japanese_punctuation_char(Char):
    return lara_parse_utils.is_punctuation_char(Char) or Char in '。？！，、：”“「」『』'
    
def is_sentence_final_japanese_punctuation_mark(Char):
    return Char in '。？！'

def is_japanese_close_quote(Char):
    return Char in '”」』'


# Google morphological analysis splits up Japanese verbs, adjectives and adverbs into morphemes
# Try to put Humpty Dumpty together again

_google_verb_affixes = { 'う': 'VERB',
                         'さ': 'VERB',
                         'た': 'VERB',
                         'たい': 'VERB',
                         'たら': 'VERB',
                         'て': 'PRT',
                         'てる': 'VERB',
                         'で': 'PRT',
                         'ない': 'VERB',
                         'なかった': 'VERB',
                         'ながら': 'PRT',
                         'なく': 'VERB',
                         'ば': 'PRT',
                         'まし': 'VERB',
                         'ます': 'VERB'
                         }

_google_adj_affixes = { 'た': 'VERB',
                        'なかった': 'VERB'
                        }

_google_adv_affixes = { 'ない': 'VERB'
                        }

def consolidate_google_tagging_tuples(TaggingTuples):
    if len(TaggingTuples) == 0:
        return TaggingTuples
    ( CurrentWord, CurrentTag, CurrentLemma ) = TaggingTuples[0]
    OutTuples = []
    for ( Word, Tag, Lemma ) in TaggingTuples[1:]:
        ( NewCurrentWord, NewCurrentTag, Merged ) = merge_tagging_tuples(CurrentWord, CurrentTag, Word, Tag )
        if Merged == False:
            OutTuples += [ [ CurrentWord, CurrentTag, CurrentLemma ] ]
            ( CurrentWord, CurrentTag, CurrentLemma ) = ( Word, Tag, Lemma )
        else:
            ( CurrentWord, CurrentTag, CurrentLemma ) = ( NewCurrentWord, NewCurrentTag, CurrentLemma )
    return OutTuples

def merge_tagging_tuples(CurrentWord, CurrentTag, Word, Tag):
    if CurrentTag == 'VERB' and Word in _google_verb_affixes and _google_verb_affixes[Word] == Tag:
        return ( CurrentWord + Word, CurrentTag, True )
    elif CurrentTag == 'ADJ' and Word in _google_adj_affixes and _google_adj_affixes[Word] == Tag:
        return ( CurrentWord + Word, CurrentTag, True )
    elif CurrentTag == 'ADV' and Word in _google_adv_affixes and _google_adv_affixes[Word] == Tag:
        return ( CurrentWord + Word, CurrentTag, True )
    # Weird special case 
    elif CurrentWord == 'ありませ' and Word == 'ん':
        return ( CurrentWord + Word, CurrentTag, True )
    else:
        return ( False, False, False )
    
                                                          

        
