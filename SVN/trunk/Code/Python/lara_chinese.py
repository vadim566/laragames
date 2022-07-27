
# Only import Jieba if we need it
#import jieba
import lara_config
import lara_parse_utils
import lara_utils

def test(Id):
    if Id == 'bear_rabbits':
        InFile = '$LARA/Content/chinese_test1/corpus/BearRabbits.txt'
        OutFile = '$LARA/Content/chinese_test1/corpus/BearRabbitsSegmented.txt'
    else:
        lara_utils.print_and_flush('*** Error: unknown Id {Id}')
        return False
    Params = lara_config.read_lara_local_config_file('$LARA/Content/peter_rabbit/corpus/local_config.json')
    segment_file_using_zh_tokenise(InFile, OutFile, Params)

def is_chinese_language(LangId):
    return LangId in ( 'mandarin', 'cantonese', 'taiwanese', 'shanghaiese' )

##   Doc for Sharoff tokeniser + TreeTagger packages
##
##   TOKENIZER="perl -I ${CMD} ${CMD}/segment-zh.perl"
##   
##   TAGGER=${BIN}/tree-tagger
##   PARFILE=${LIB}/zh.par
##   
##   # put all on one line
##   cat $* |
##   # do tokenization
##   $TOKENIZER ${CMD}/chinese-3c.utf8 ${CMD}/chinese-2c.utf8 |
##   # tagging
##   $TAGGER $PARFILE -token -sgml
##
##   Compare with e.g. Italian invocation from lara_treetagger.py
##
##   f'perl {tokenize_script} -i -a $TREETAGGER/lib/italian-abbreviations INPUT_FILE | $TREETAGGER/bin/tree-tagger $TREETAGGER/lib/italian.par {treetagger_common_options} > OUTPUT_FILE',

def segmented_file_to_plain_file(InFile, Params):
    PlainFile = lara_utils.get_tmp_trace_file(Params)
    StrIn = lara_utils.read_lara_text_file(InFile)
    # Concatenate all the lines
    Str1 = StrIn.replace('\n', '')
    # Remove all the | characters added by Chinese segmentation
    StrOut = Str1.replace('|', '')
    lara_utils.write_lara_text_file(StrOut, PlainFile)
    return PlainFile

## The first step, putting everying on one line, is done using segmented_file_to_plain_file immediately above.
def treetagger_invocation_for_chinese():
    ZHTokeniseDir = lara_utils.absolute_file_name('$ZHTokenise')
    TokenizeScript = lara_utils.absolute_file_name('$ZHTokenise/segment-zh.perl')
    Lex1 = lara_utils.absolute_file_name('$ZHTokenise/chinese-3c.utf8')
    Lex2 = lara_utils.absolute_file_name('$ZHTokenise/chinese-2c.utf8')
    return f'perl {TokenizeScript} {Lex1} {Lex2} <INPUT_FILE | $TREETAGGER/bin/tree-tagger $TREETAGGER/lib/zh.par -token -sgml > OUTPUT_FILE'

def segment_file_using_chinese_tokeniser(InFile, OutFile, Params):
    Tokeniser = Params.chinese_tokeniser
    if Tokeniser == 'sharoff':
        return segment_file_using_zh_tokenise(InFile, OutFile, Params)
    elif Tokeniser == 'jieba':
        return segment_file_using_jieba(InFile, OutFile, Params)
    else:
        lara_utils.print_and_flush(f'*** Error: unknown Chinese tokeniser {Tokeniser}')
        return False

def segment_file_using_jieba(InFile, OutFile, Params):
    lara_utils.print_and_flush(f'--- Tokenising using Jieba')
    InText = lara_utils.read_lara_text_file(InFile)
    Sentences = sentence_segment_string(InText)
    SegmentedSentences = [ segment_sentence_using_jieba(Sentence) for Sentence in Sentences ]
    Segments = [ Segment for SegmentedSentence in SegmentedSentences for Segment in SegmentedSentence ]
    return apply_tokenise_result(Segments, InFile, OutFile)

# It's annoying that we're duplicating work done in add_end_of_segment_mark_to_punctuation_token_if_necessary.
# The problem is that Sharoff and Jieba do things differently; Sharoff runs on the whole text, Jieba on sentences.
def sentence_segment_string(InStr):
    ( I, N, Sentences, CurrentSentence ) = ( 0, len(InStr), [], '' )
    while True:
        if I >= N:
            if CurrentSentence != '':
                Sentences += [ CurrentSentence ]
            return Sentences
        c1 = InStr[I]
        c2 = InStr[I+1] if I+1 < N else False
        if is_sentence_final_chinese_punctuation_mark(c1) and c2 != False and is_chinese_close_quote(c2):
            CurrentSentence += f'{c1}{c2}'
            Sentences += [ CurrentSentence ]
            CurrentSentence = ''
            I += 2
        elif is_sentence_final_chinese_punctuation_mark(c1):
            CurrentSentence += f'{c1}'
            Sentences += [ CurrentSentence ]
            CurrentSentence = ''
            I += 1
        else:
            CurrentSentence += c1
            I += 1
    # Should never get here but just in case
    return Sentences

def segment_sentence_using_jieba(Sentence):
    import jieba
    Segments = jieba.cut(Sentence, cut_all=False)
    SegmentsAsList = list(Segments)
    return consolidate_punctuation_tokens(SegmentsAsList)

def consolidate_punctuation_tokens(Segments):
    ( OutSegments, CurrentPunctuation ) = ( [], '' )
    for Segment in Segments:
        if punctuation_token(Segment):
            CurrentPunctuation += Segment
        else:
            if CurrentPunctuation != '':
                OutSegments += [ CurrentPunctuation]
                CurrentPunctuation = ''
            OutSegments += [ Segment ]
    if CurrentPunctuation != '':
        OutSegments += [ CurrentPunctuation]
    return OutSegments

def segment_file_using_zh_tokenise(InFile, OutFile, Params):
    lara_utils.print_and_flush(f"--- Tokenising using Sharoff's ZH-tokenise")
    TmpFile = lara_utils.get_tmp_file_with_extension(Params, 'txt')
    try:
        Result = run_zh_tokenise(InFile, TmpFile, Params)
        if Result != False:
            apply_zh_tokenise_result(TmpFile, InFile, OutFile)
            return True
        else:
            return False
    except Exception as e:
        lara_utils.print_and_flush(f'*** Warning: something went wrong when running ZH-tokenisr:"')
        lara_utils.print_and_flush(str(e))
        return False
    finally:
        lara_utils.delete_file_if_it_exists(TmpFile)

def run_zh_tokenise(InFile, OutFile, Params):
    Executable = lara_utils.absolute_file_name('$ZHTokenise/segment-zh.perl')
    Lex1 = lara_utils.absolute_file_name('$ZHTokenise/chinese-3c.utf8')
    Lex2 = lara_utils.absolute_file_name('$ZHTokenise/chinese-2c.utf8')
    AbsInFile = lara_utils.absolute_file_name(InFile)
    AbsOutFile = lara_utils.absolute_file_name(OutFile)
    Command = f'perl {Executable} {Lex1} {Lex2} <{AbsInFile} >{AbsOutFile}'
    return True if lara_utils.execute_lara_os_call(Command, Params) == 0 else False

def apply_zh_tokenise_result(TmpFile, InFile, OutFile):
    TokenisedLines = lara_utils.read_lara_text_file(TmpFile).split('\n')
    return apply_tokenise_result(TokenisedLines, InFile, OutFile)

def apply_tokenise_result(TokenisedLines, InFile, OutFile):
    InStr = lara_utils.read_lara_text_file(InFile)
    OutStr = apply_tokenise_result_to_string(TokenisedLines, InStr)
    if OutStr != False:
        lara_utils.write_lara_text_file(OutStr, OutFile)
        return True
    else:
        return False

def apply_tokenise_result_to_string(Tokens, InStr):
    ( I, N, OutStr ) = ( 0, len(InStr), '' )
    for Token in Tokens:
        NextI = InStr.find(Token, I)
        if NextI < I:
            lara_utils.print_and_flush('*** Warning: unable to find "{Token}" in text')
            break
        Skipped = InStr[I:NextI]
        I = NextI + len(Token)
        if punctuation_token(Token):
            Token1 = add_end_of_segment_mark_to_punctuation_token_if_necessary(Token)
            OutStr += f'{Skipped}{Token1}'
        else:
            OutStr += f'{Skipped}{Token}|'
    Rest = InStr[I:N]
    OutStr += Rest
    return OutStr

def punctuation_token(Token):        
    for Char in Token:
        if not is_chinese_punctuation_char(Char) and not Char.isspace():
            return False
    return True

def add_end_of_segment_mark_to_punctuation_token_if_necessary(Token):
    ( OutToken, I, N ) = ( '', 0, len(Token) )
    while True:
        if I >= N:
            return OutToken
        c1 = Token[I]
        c2 = Token[I+1] if I+1 < N else False
        if is_sentence_final_chinese_punctuation_mark(c1) and c2 != False and is_chinese_close_quote(c2):
            OutToken += f'{c1}{c2}||'
            I += 2
        elif is_sentence_final_chinese_punctuation_mark(c1):
            OutToken += f'{c1}||'
            I += 1
        else:
            OutToken += c1
            I += 1
    # Should never get here but just in case
    return OutToken

# ----------------------------------------------

# Pinyin-annotated text is created by processing the segmented file on https://www.chineseconverter.com/en/convert/chinese-to-pinyin
# Typical output looks like this:
# 熊(xióng) |和(hé) |兔(tù) 子(zǐ) |的(dí) |故(gù) 事(shì) ||
# 很(hěn) |久(jiǔ) |很(hěn) |久(jiǔ) |以(yǐ) 前(qián) |，有(yǒu) |一(yī) |只(zhī) |懒(lǎn) 惰(duò) |的(dí) |大(dà) |熊(xióng) |，
# 占(zhān) 领(lǐng) |了(liǎo) |大(dà) 片(piàn) |的(dí) |田(tián) 地(dì) |，却(què) |不(bù) 肯(kěn) |耕(gēng) 种(zhǒng) |，
# 整(zhěng) 天(tiān) |睡(shuì) |懒(lǎn) 觉(jué) |。
#
# Convert into a word-pinyin dict

def maybe_add_hanzi_to_pinyin_dict_to_params(Params):
    PinyinCorpusFile = Params.pinyin_corpus
    if PinyinCorpusFile != '' and lara_utils.file_exists(PinyinCorpusFile):
        HanziToPinyinDict = get_pinyin_from_annotated_text(PinyinCorpusFile)
        lara_utils.print_and_flush(f'--- Constructed hanzi-to-pinyin dict ({len(HanziToPinyinDict)} entries) from {PinyinCorpusFile}')
        Params.hanzi_to_pinyin_dict = HanziToPinyinDict

def maybe_add_pinyin_to_translation(Word, Translation, Params):
    if Word in Params.hanzi_to_pinyin_dict:
        Pinyin = Params.hanzi_to_pinyin_dict[Word]
        return f'{Pinyin} ; {Translation}' if not Translation in ( '', False ) else Pinyin
    else:
        return Translation

def get_pinyin_from_annotated_text(File):
    Dict = {}
    Text = lara_utils.read_lara_text_file(File)
    if Text != False:
        Segments = Text.split('|')
        for Segment in Segments:
            get_pinyin_from_annotated_text_segment(Segment, Dict)
    return Dict

def get_pinyin_from_annotated_text_segment(Segment, Dict):
    Pairs = get_hanzi_pinyin_pairs_from_segment(Segment)
    if Pairs != []:
        Hanzi = ''.join([ Pair['hanzi'] for Pair in Pairs ])
        Pinyin = ''.join([ Pair['pinyin'] for Pair in Pairs ])
        Dict[Hanzi] = Pinyin

def get_hanzi_pinyin_pairs_from_segment(Segment):
    ( I, N, Pairs ) = ( 0, len(Segment), [] )
    while True:
        if I >= N:
            return Pairs
        if I + 1 < N and Segment[I + 1] == '(':
            CloseBracketIndex = Segment.find(')', I + 1)
            if CloseBracketIndex < 0:
                lara_utils.print_and_flush(f'*** Warning: mismatched parentheses in {Segment}')
                return Pairs
            Hanzi = Segment[I]
            Pinyin = Segment[I+2:CloseBracketIndex]
            Pairs += [ { 'hanzi': Hanzi, 'pinyin': Pinyin } ]
            I = CloseBracketIndex + 1
        else:
            I += 1

# ----------------------------------------------

def is_chinese_punctuation_char(Char):
    return lara_parse_utils.is_punctuation_char(Char) or Char in '。？！，、：”“'
    
def is_sentence_final_chinese_punctuation_mark(Char):
    return Char in '。？！'

def is_chinese_close_quote(Char):
    return Char in '”'


