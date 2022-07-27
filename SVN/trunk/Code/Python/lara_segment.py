
import lara_replace_chars
import lara_utils 

def segment_file(infile, outfile):
    instring = lara_utils.read_lara_text_file(infile)
    if not instring:
        lara_utils.print_and_flush(f'*** Error: unable to segment because unable to read file {infile}')
        return False
    instring1 = lara_replace_chars.try_to_replace_nonstandard_hyphen(instring)
    instring2 = lara_replace_chars.replace_reserved_chars(instring1)
    instring3 = lara_replace_chars.try_to_correct_replaced_html(instring2)
    outstring = segment_string(instring2)
    if not outstring:
        lara_utils.print_and_flush(f'*** Error: sentence segmentation failed')
        return False
    NSegments = len(outstring.split('||'))
    lara_utils.print_and_flush(f'--- Input split into {NSegments} segments')
    lara_utils.write_lara_text_file(outstring, outfile)
    return True

def segment_string(instring):
    ntlk_outstring = nltk_sent_tokenize(instring)
    if ntlk_outstring:
        return ntlk_outstring
    lara_utils.print_and_flush('--- Trying simple segmentation (NLTK not available or did not work)')
    simple_outstring = simple_sent_tokenize(instring)
    if simple_outstring:
        lara_utils.print_and_flush('--- Simple segmentation worked')
    return simple_outstring

def nltk_sent_tokenize(instring):
    try:
        import nltk
        from nltk import sent_tokenize
        sents = sent_tokenize(instring)
        lara_utils.print_and_flush('--- Used NLTK Punkt segmentation')
        if not sents:
            return False
        substList = [ ( sent, sent ) for sent in sents ]
        segmentedString = substitute_serial(substList, instring, '||')
        return add_segment_breaks_after_quotes(segmentedString) 
    except Exception as e:
        print_and_flush(f'*** Error: when trying to do NLTK/Punkt tokenization')
        print_and_flush(str(e))
        return False

# Add segmentation marks after a period, question-mark etc followed by a close quote.
end_of_sentence_marks = '.?!'
end_quote_marks = '"”\'’'

def simple_sent_tokenize(text):
    try:
        sents = simple_sent_tokenize1(text)
        return '||'.join(sents) + '||'
    except Exception as e:
        print_and_flush(f'*** Error: when trying to do simple sent tokenization')
        print_and_flush(str(e))
        return False

def simple_sent_tokenize1(text):
    global abbrevations_table
    if len(text) < 2:
        return [ text ]
    ( i, n, current, out ) = ( 0, len(text), '', [] )
    if not read_and_store_abbreviations_table():
        return False
    relevant_abbreviations = [ word for word in abbrevations_table if text.find(word) >= 0 ]
    while True:
        if i > n-2:
            current += text[i:n]
            return out + [ current ] if len(current) > 0 else out
        abbreviation = starts_with_abbreviation(text[i:], relevant_abbreviations)
        if abbreviation != False:
            current += abbreviation
            i += len(abbreviation)
        elif text[i] in end_of_sentence_marks:
            end_marks = read_end_sentence_marks_plus_optional_quote_mark(text, i)
            out += [ f'{current}{end_marks}' ]
            i += len(end_marks)
            current = ''
        else:
            current += text[i]
            i += 1

def read_end_sentence_marks_plus_optional_quote_mark(text, start):
    ( i, n, out ) = ( start, len(text), '' )
    while True:
        if i >= n:
            return out
        c1 = text[i]
        if c1 in end_quote_marks:
            return out + c1
        if c1 in end_of_sentence_marks:
            out += c1
            i += 1
        else:
            return out
        
abbrevations_table = []

def starts_with_abbreviation(text, relevant_abbreviations):
    for abbreviation in relevant_abbreviations:
        if text.startswith(abbreviation):
            return abbreviation
    return False

def read_and_store_abbreviations_table():
    global abbrevations_table
    abbreviation_file = '$TREETAGGER/lib/english-abbreviations'
    if not lara_utils.file_exists(abbreviation_file):
        lara_utils.print_and_flush('*** Error: unable to find {abbreviation_file}')
        return False
    raw_abbreviations = lara_utils.read_ascii_text_file_to_lines(abbreviation_file)
    abbrevations_table = ['...'] + [ word for word in raw_abbreviations if not word.isspace() and len(word) > 0 ]
    return True

def add_segment_breaks_after_quotes(text):
    if len(text) < 2:
        return text
    ( i, n, out ) = ( 0, len(text)-2, '' )
    while True:
        if i == n:
            return out + text[n] + text[n+1]
        if i > n:
            return out
        ( c1, c2 ) = ( text[i], text[i+1] )
        if c1 in end_of_sentence_marks and c2 in end_quote_marks and not already_broken_at_index(text, i+2):
            out += f'{c1}{c2}||'
            i += 2
        else:
            out += c1
            i += 1

def already_broken_at_index(text, index):
    return len(text) >= index + 2 and text[index:index+2] == '||'

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

