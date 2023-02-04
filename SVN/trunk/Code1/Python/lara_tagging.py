
import lara_utils 

import nltk
from nltk import sent_tokenize, word_tokenize, pos_tag
from nltk.stem import WordNetLemmatizer

wnl = WordNetLemmatizer()

def tag_file(infile, outfile):
    instring = lara_utils.read_lara_text_file(infile)
    outstring = tag_string(instring)
    lara_utils.write_lara_text_file(outstring, outfile)

def tag_string(text):
    sents = sent_tokenize(text)
    tagged_sents = [ tag_sent(sent) for sent in sents ]
    return substitute_serial(tagged_sents, text, '||')

def tag_sent(sent):
    #print('Sent: ' + sent)
    tokens = word_tokenize(sent)
    tokens1 = [ correct_clever_quote(token) for token in tokens ]
    tagged_tokens = nltk.pos_tag(tokens1)
    lemmatized_tokens = [ lemmatize_tagged_token(item) for item in tagged_tokens ]
    return ( sent, substitute_serial(lemmatized_tokens, sent, '') )

def correct_clever_quote(token):
    if token in ["``", "''"]:
        return '"'
    else:
        return token

def lemmatize_tagged_token(tagged_token):
    ( word, tag ) = tagged_token
    #if ( word.isupper() and not word in ['I'] ) or ( not intrinsically_capitalised_word(word, tag) ):
    if ( not word.islower() and not word in ['I'] ) or ( not intrinsically_capitalised_word(word, tag) ):
        word1 = word.lower()
    else:
        word1 = word
    pos = tag_to_pos(tag)
    if pos == 'other':
        # It's not a noun, verb, adjective or adverb, so let's assume it doesn't inflect.
        lemma = word1 
    else:
        lemma = wnl.lemmatize(word1, pos=pos)
    if word == lemma:
        return ( word, word )
    else:
        return ( word, word + '#' + lemma + '#' )

def intrinsically_capitalised_word(word, tag):
    return proper_name_tag(tag) or word in ['I']

def proper_name_tag(tag):
    return tag in [ 'NNP', 'NNPS' ] 

def tag_to_pos(tag):
    firstletter = tag.lower()[0]
    if firstletter in 'vn':
        return firstletter
    elif firstletter in 'jr':
        return 'a'
    else:
        return 'other'

def substitute_serial(substList, string, separator):
    instring = string
    outstring = ''
    for subst in substList:
        ( w, w1 ) = subst
        index = instring.find(w)
        if index == -1:
            lara_utils.print_and_flush('--- Unable to find "{w}" in "{string}"'.format(w=w, string=string))
            return outstring
        else:
            outstring = outstring + instring[:index] + w1 + separator
            instring = instring[index + len(w):]
    return outstring + instring


    
