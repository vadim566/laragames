# Code that will be used by different taggers

import lara_mwe
import lara_utils
import lara_top
import lara_parse_utils
import lara_replace_chars
import lara_postags
import lara_clitics

## Now go down the original LARA file, which has been turned into a string,
## matching each surface word from the tagging triples in turn and
## if necessary adding hashtags and/or multiword markers
def annotate_lara_string_from_tagging_triples(TagTuples, InString, Params):
    ( Index, N, OutString, Errors, NErrors ) = ( 0, len(InString), '', [], 0 )
    AddPosTagsToLemma = Params.add_postags_to_lemma == 'yes' and Params.language != '' 
    for ( SurfaceWordsList, Tag, Lemma ) in TagTuples:
        Lemma = maybe_fix_strange_treetagger_characters(Lemma, Params)
        SurfaceWord = ' '.join(SurfaceWordsList)
        # Get the tag from lara_clitics.is_clitic, since some TreeTagger clitic tags (e.g. French) are very unreliable.
        ( Clitic, CliticTag, CliticType ) = lara_clitics.is_clitic(SurfaceWord, Params.language)
        ( Lemma, Tag ) = ( Clitic, CliticTag ) if Clitic else ( Lemma, Tag )
        if AddPosTagsToLemma:
            Tag = lara_postags.map_postag(Tag, Params)
        ( NewStartIndex, NewEndIndex, MatchedString ) = match_surface_words(SurfaceWordsList, InString, Index)
        if not MatchedString or dubious_skipped_string(InString, Index, NewStartIndex, Params):
            Sample = f'{InString[Index:Index+100]}...' if Index + 100 < N else InString[Index:]
            Error = f'*** Warning: unable to find "{str(SurfaceWord)}" in "{Sample}"'
            lara_utils.print_and_flush(Error)
            Errors += [ Error ]
            NErrors += 1
            if NErrors > 100:
                break
        # It's possible that we've got inside a close hashtag, if so restart from there
        elif skipped_inside_hashtag(InString, Index, NewStartIndex):
            SkippedString = InString[Index:NewEndIndex]
            OutString += SkippedString
            Index = NewEndIndex
        else:
            if InString[NewStartIndex-1] == '@' and NewEndIndex + 1 < N and InString[NewEndIndex + 1] == '@' :
                ( NewStartIndex, NewEndIndex ) = ( NewStartIndex - 1, NewEndIndex + 1 )
            SkippedString = InString[Index:NewStartIndex]
            ( OldHTMLTag, OldAnnotation, NewEndIndex ) = read_annotation(InString, NewEndIndex, N)
            SubstituteString = get_substitute_string(OldHTMLTag, OldAnnotation, MatchedString, SurfaceWordsList, SurfaceWord,
                                                     Lemma, Tag, CliticType, AddPosTagsToLemma, Params.retagging_strategy, Params.language)
            if NewEndIndex < N and \
               not InString[NewEndIndex].isspace() and not lara_parse_utils.is_punctuation_char(InString[NewEndIndex]) and InString[NewEndIndex] != '|' and \
               not lara_parse_utils.is_punctuation_string(SubstituteString) and not SubstituteString[-1] == '|':
                   SubstituteString += '|'
            if SubstituteString.startswith('|') and OutString.endswith('|'):
                SubstituteString = SubstituteString[1:]
            OutString += ( SkippedString + SubstituteString )
            Errors += [ report_match_and_substitute(SurfaceWordsList, SkippedString, SubstituteString) ]
            Index = NewEndIndex
    save_tagging_errors(Errors, Params)
    return OutString + InString[Index:]

def report_match_and_substitute(SurfaceWordsList, SkippedString, SubstituteString):
    return f'Match: {truncate_strs(SurfaceWordsList)}, Skipped: {truncate_str(SkippedString)}, substituted: {truncate_str(SubstituteString)}'

def truncate_strs(List):
    List1 = [ truncate_str(X) for X in List ]
    return f"[ {', '.join(List1)} ]"

def truncate_str(Str):
    Len = len(Str)
    return f'{Str[:200]}... ({Len} chars)' if Len > 200 else Str

def save_tagging_errors(Errors, Params):
    File = lara_top.lara_tmp_file('tagging_errors_file', Params)
    lara_utils.write_lara_text_file('\n'.join(Errors), File)

# When we are retagging, it's possible to get strange situations where a word from the tagger
# doesn't match the word it really belongs to, which has been split up by annotation, but instead
# matches something completely different much later in the text. 
def dubious_skipped_string(InString, Index, NewStartIndex, Params):
    # If we've skipped less than 5 characters (the usual case), we're probably okay unless we've
    # got inside a close hashtag
    if NewStartIndex - Index < 5:
        return False
    # We could have skipped a longer chunk because of comments or complex HTML markup,
    # so see what it looks like when we delete them.
    SkippedString = InString[Index:NewStartIndex]
    ( ReducedStr, Errors ) = lara_parse_utils.remove_hashtag_comment_and_html_annotations1(SkippedString.replace('@', ''), 'delete_comments')
    # If the call returned an error, we've matched something inside a tag and things are definitely wrong.
    if len(Errors) > 0:
        lara_utils.print_and_flush(f'Dubious skipped string (errors): {truncate_str(SkippedString)}')
        return True
    # If we're doing Japanese or Chinese and we have more than 5 single vertical bars in the skipped string, things are probably wrong.
    if Params.language in ( 'japanese', 'mandarin' ) and count_single_vertical_bars(ReducedStr) > 5:
        lara_utils.print_and_flush(f'Dubious skipped string (too many vertical bars): {truncate_str(SkippedString)}')
        return True
    # If we've skipped less than 200 characters once comments and markup are taken into account,
    # we should be okay
    if len(ReducedStr) < 200:
        return False
    # Otherwise, something could well be wrong
    else:
        lara_utils.print_and_flush(f'Dubious skipped string (long): {truncate_str(SkippedString)}')
        return True

def count_single_vertical_bars(Str):
    Str1 = Str.replace('||', '')
    return Str1.count('|')

def skipped_inside_hashtag(InString, Index, NewStartIndex):
    # If we haven't passed a <, we can't have got inside a hashtag
    if not InString.find('<', Index, NewStartIndex):
        return False
    SkippedString = InString[Index:NewStartIndex]
    ( ReducedStr, Errors ) = lara_parse_utils.remove_hashtag_comment_and_html_annotations1(SkippedString, 'delete_comments')
    if len(Errors) > 0:
        return True
    else:
        return False

def read_annotation(InString, Index, N):
    if Index >= N:
        return ( '', False, Index )
    # We might have an HTML tag before the hashtag
    if InString[Index] != '<' or \
       ( InString[Index] == '<' and ( Index == 0 or InString[Index - 1] != '\\' ) ):
        ( HTMLTag, Index1 ) = ( '', Index )
    else:
        StartHTMLTagIndex = Index
        EndHTMLTagIndex0 = InString.find('>', Index)
        if EndHTMLTagIndex0 < 0:
            lara_utils.print_and_flush(f'*** Error: open HTML tag at "{InString[Index + 1:Index + 100]}"')
            return ( '', False, Index )
        else:
            EndHTMLTagIndex = EndHTMLTagIndex0 + len('>')
            ( HTMLTag, Index1 ) = ( InString[StartHTMLTagIndex:EndHTMLTagIndex], EndHTMLTagIndex )
    if Index1 >= N or InString[Index1] != '#':
        return ( '', False, Index )
    StartHashIndex = Index1 + len('#')
    #EndHashIndex = InString.find('#', StartHashIndex)
    EndHashIndex = lara_parse_utils.find_next_non_escaped_hash_index(InString, StartHashIndex)
    if EndHashIndex < 0:
        lara_utils.print_and_flush(f'*** Error: open hashtag at "{InString[Index1 + 1:Index1 + 100]}"')
        return ( '', False, Index )
    else:
        Hashtag = InString[StartHashIndex:EndHashIndex]
        return ( HTMLTag, Hashtag, EndHashIndex + len('#') )

# Complications:
# 1. We might have an HTML tag intervening between the word and the hashtag if we're retagging
# 2. For languages like Italian where clitics get stuck on the end of the verb and TreeTagger can't deal with them,
#    we need to strip them off here, tag them, and stick the tagged versions on the end
def get_substitute_string(HTMLTag, OldAnnotation, MatchedString0, SurfaceWordsList, SurfaceWord,
                          Lemma, Tag, CliticType, AddPosTagsToLemma, RetaggingStrategy, Lang):
    ( Stem, PostverbalClitics, CliticTrace ) = lara_clitics.split_off_post_clitics_from_word(MatchedString0, Lang, Tag)
    #lara_utils.print_and_flush(f"--- split_off_post_clitics_from_word('{MatchedString0}', '{Lang}', '{Tag}')")
    if PostverbalClitics != [] and Stem != '':
        #lara_utils.print_and_flush(f'{CliticTrace}')
        MatchedString = Stem
    else:
        MatchedString = MatchedString0
    if Lemma == '@card@' or \
       MatchedString.lower() == Lemma and ( not AddPosTagsToLemma or AddPosTagsToLemma and Tag == '' ):
        SubstituteString = MatchedString
        if need_multiword_brackets(MatchedString, SurfaceWordsList):
            SubstituteString = f'@{SubstituteString}@'
    elif lara_parse_utils.is_punctuation_string(SurfaceWord):
        SubstituteString = SurfaceWord
    else:
        Annotation = f'{Lemma}/{Tag}' if AddPosTagsToLemma and Tag != '' and Lemma != '' else Lemma
        #lara_utils.print_and_flush(f'Annotation = {Annotation}')
        if RetaggingStrategy != '':
            Annotation = old_annotation_and_annotation_to_annotation(OldAnnotation, Annotation, CliticType, RetaggingStrategy)
        #lara_utils.print_and_flush(f'Annotation = {Annotation}')
        SurfaceWordsString = f'@{MatchedString}@' if need_multiword_brackets(MatchedString, SurfaceWordsList) else MatchedString
        # We may end up with a null annotation, e.g. with retagging of clitics
        SubstituteString = f'{SurfaceWordsString}{HTMLTag}#{Annotation}#' if Annotation != '' else SurfaceWordsString
        #lara_utils.print_and_flush(f'SubstituteString = {SubstituteString}')
    # If it's a clitic and we're adding POS tags, we'll already have the | marker, so don't add it again
    if CliticType == 'pre' and RetaggingStrategy == '':
        SubstituteString = f'{SubstituteString}|'
    elif CliticType == 'post' and RetaggingStrategy == '':
        SubstituteString = f'|{SubstituteString}'
    elif PostverbalClitics != [] and RetaggingStrategy == '':
        PostverbalCliticsString = tagged_postverbal_clitics_string(PostverbalClitics, AddPosTagsToLemma)
        SubstituteString = f'{SubstituteString}{PostverbalCliticsString}'
    return SubstituteString

def tagged_postverbal_clitics_string(PostverbalClitics, AddPosTagsToLemma):
    #lara_utils.print_and_flush(f'--- tagged_postverbal_clitics_string({PostverbalClitics}, {AddPosTagsToLemma})')
    return ''.join( [ tagged_single_postverbal_clitic_string(PostverbalClitic, AddPosTagsToLemma) for PostverbalClitic in PostverbalClitics ] )

def tagged_single_postverbal_clitic_string(PostverbalClitic, AddPosTagsToLemma):
    if not len(PostverbalClitic) == 3:
        lara_utils.print_and_flush(f'*** Error: bad argument to lara_single_generic_tagging.tagged_postverbal_clitics_string: {PostverbalClitic}')
        raise ValueError          
    ( Clitic, CliticLemma, Tag ) = PostverbalClitic
    Annotation = f'{CliticLemma}/{Tag}' if AddPosTagsToLemma else CliticLemma
    return f'|{Clitic}#{Annotation}#' if Clitic != Annotation else f'|{Clitic}'
    
def old_annotation_and_annotation_to_annotation(OldAnnotation, CurrentAnnotation, CliticType, RetaggingStrategy):
    if RetaggingStrategy == 'replace_all':
        return CurrentAnnotation
    # If it's a clitic and we're retagging, don't replace the annotation - we won't have found anything useful
    #if RetaggingStrategy == 'replace_pos' and CliticType in ['pre', 'post']:
    #    return OldAnnotation if not OldAnnotation == False else ''
    ( OldLemma, OldPos ) = annotation_to_lemma_and_pos(OldAnnotation)
    ( CurrentLemma, CurrentPos ) = annotation_to_lemma_and_pos(CurrentAnnotation)
    if RetaggingStrategy == 'replace_lemma' and OldPos == '':
        return lemma_and_pos_to_annotation(CurrentLemma, CurrentPos)
    if RetaggingStrategy == 'replace_lemma':
        return lemma_and_pos_to_annotation(CurrentLemma, OldPos)
    if RetaggingStrategy == 'remove_mwe':
        return CurrentAnnotation if lara_mwe.is_mwe_lemma(OldLemma) else OldAnnotation
    if RetaggingStrategy == 'replace_pos' and OldLemma == '':
        return lemma_and_pos_to_annotation(CurrentLemma, CurrentPos)
    if RetaggingStrategy == 'replace_pos':
        return lemma_and_pos_to_annotation(OldLemma, CurrentPos)

def annotation_to_lemma_and_pos(Annotation):
    if Annotation == False:
        return ( '', '' )
    Components = Annotation.split('/')
    return Components[:2] if len(Components) > 1 else ( Annotation, '' )

def lemma_and_pos_to_annotation(Lemma, Pos):
    return f'{Lemma}/{Pos}' if Pos != '' else Lemma

def map_postag_and_report(Tag, Params):
    Tag1 = lara_postags.map_postag(Tag, Params)
    print(f'Changed "{Tag}" to "{Tag1}"')
    return Tag1

# TreeTagger mangles the French œ ligature - we may find other similar cases
def maybe_fix_strange_treetagger_characters(Lemma, Params):
    Lang = Params.language
    if Lang == 'french':
        OutStr = ''
        for Char in Lemma:
            OutStr += ( 'œ' if ord(Char) == 156 else Char )
        return OutStr
    else:
        return Lemma

# We need multiword brackets around a string if it consists of several words, or includes punctuation other than hyphens or apostrophes,
# but we don't need it if the word is a single punctuation mark.
def need_multiword_brackets(MatchedString, SurfaceWordsList):
    return not is_single_punctuation_mark(MatchedString) and \
           ( len(SurfaceWordsList) > 1 or string_contains_punctuation_except_hyphen_and_apostrophe(MatchedString) )

def is_single_punctuation_mark(Str):
    return isinstance(Str, str) and len(Str) == 1 and lara_parse_utils.is_punctuation_char(Str[0])

def string_contains_punctuation_except_hyphen_and_apostrophe(Str):
    for Char in Str:
        if lara_parse_utils.is_punctuation_char(Char) and not Char in "-" and not lara_parse_utils.is_apostrophe_char(Char):
            return True
    return False

def match_surface_words(SurfaceWordsList, InString, Index):
    ( FirstWord, RestWords ) = ( SurfaceWordsList[0], SurfaceWordsList[1:] )
    StartIndex = InString.find(FirstWord, Index)
    if StartIndex < 0:
        return ( False, False, False)
    Index = StartIndex + len(FirstWord)
    for Word in RestWords:
        NewIndex = InString.find(Word, Index)
        if NewIndex < 0:
            return ( False, False, False)
        Index = NewIndex + len(Word)
    return ( StartIndex, Index, InString[StartIndex:Index] )

# If a multiword contains a clitic, we can get hashtags and separator chars inside the tagged version
def remove_hashtags_and_separators_inside_multiwords(Str):
    ( I, N, StrOut ) = ( 0, len(Str), '' )
    while True:
        if I >= N:
            return StrOut
        c1 = Str[I]
        c2 = Str[I:I+2]
        if lara_replace_chars.is_escaped_reserved_char_sequence(c2):
            StrOut += c2
            I += 2
        elif Str[I] == '@':
            #EndOfMultiword = Str.find('@', I + len('@'))
            EndOfMultiword = lara_parse_utils.find_next_non_escaped_at_sign_index(Str, I + len('@'))
            if EndOfMultiword < 0:
                lara_utils.print_and_flush(f'*** Error: open multiword tag "{Str[I:I+32]}" in tagged string')
                return False
            else:
                StrOut += f'@{remove_hashtags_and_separators(Str[I+1:EndOfMultiword])}@'
                I = EndOfMultiword + len('@')
        else:
            StrOut += Str[I]
            I += 1

def remove_hashtags_and_separators(Str):
    return (lara_parse_utils.remove_hashtag_annotations_from_string(Str)).replace('|', '')
