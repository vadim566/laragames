import lara_utils

# Reading text taken from jesusfellowship.uk/bible
# Typical chapter heading:
#
# Italian, Luca 1 (Luke 1)
#
# Typical verse:
#
# 1   Poiché molti han posto mano a stendere un racconto degli avvenimenti successi tra di noi,

def test(Id):
    if Id == 'luca':
        InFile = '$LARA/Content/luke_jerusalem/corpus/Luke_Italian.docx'
        ChapterMarker = '(Luke'
        OutFile = '$LARA/Content/luke_jerusalem/corpus/Luke_Italian.json'
        read_jesusfellowship_file(InFile, ChapterMarker, OutFile)
    elif Id == 'luca_translations':
        InFile = '$LARA/tmp_resources/Luke_JB_tmp_segment_translations.csv'
        ChapterMarker = 'JB LUKE'
        DictFile = '$LARA/Content/luke_jerusalem/corpus/Luke_Italian.json'
        OutFile = '$LARA/Content/luke_jerusalem/translations/english_italian_updated.csv'
        add_translations_to_csv(InFile, ChapterMarker, DictFile, OutFile)
    elif Id == 'luke_polish':
        InFile = '$LARA/Content/luke_jerusalem/corpus/Luke_Polish.docx'
        ChapterMarker = '(Luke'
        OutFile = '$LARA/Content/luke_jerusalem/corpus/Luke_Polish.json'
        read_jesusfellowship_file(InFile, ChapterMarker, OutFile)
    elif Id == 'luke_polish_translations':
        InFile = '$LARA/tmp_resources/Luke_JB_polish_tmp_segment_translations.csv'
        ChapterMarker = 'JB LUKE'
        DictFile = '$LARA/Content/luke_jerusalem/corpus/Luke_Polish.json'
        OutFile = '$LARA/Content/luke_jerusalem/translations/english_polish.csv'
        add_translations_to_csv(InFile, ChapterMarker, DictFile, OutFile)
        
    elif Id == 'ecclesiastes':
        InFile = '$LARA/Content/ecclesiastes_nrsv/corpus/Ecclesiastes_Italian.docx'
        ChapterMarker = '(Ecclesiastes'
        OutFile = '$LARA/Content/ecclesiastes_nrsv/corpus/Ecclesiastes_Italian.json'
        read_jesusfellowship_file(InFile, ChapterMarker, OutFile)
    elif Id == 'ecclesiastes_translations':
        InFile = '$LARA/tmp_resources/Ecclesiastes_NRSV_tmp_segment_translations.csv'
        ChapterMarker = 'Ecclesiastes'
        DictFile = '$LARA/Content/ecclesiastes_nrsv/corpus/Ecclesiastes_Italian.json'
        OutFile = '$LARA/Content/ecclesiastes_nrsv/translations/english_italian.csv'
        add_translations_to_csv(InFile, ChapterMarker, DictFile, OutFile)
    elif Id == 'ecclesiastes_polish':
        InFile = '$LARA/Content/ecclesiastes_nrsv/corpus/Ecclesiastes_Polish.docx'
        ChapterMarker = '(Ecclesiastes'
        OutFile = '$LARA/Content/ecclesiastes_nrsv/corpus/Ecclesiastes_Polish.json'
        read_jesusfellowship_file(InFile, ChapterMarker, OutFile)
    elif Id == 'ecclesiastes_polish_translations':
        InFile = '$LARA/tmp_resources/Ecclesiastes_NRSV_polish_tmp_segment_translations.csv'
        ChapterMarker = 'Ecclesiastes'
        DictFile = '$LARA/Content/ecclesiastes_nrsv/corpus/Ecclesiastes_Polish.json'
        OutFile = '$LARA/Content/ecclesiastes_nrsv/translations/english_polish.csv'
        add_translations_to_csv(InFile, ChapterMarker, DictFile, OutFile)

    elif Id == 'psalms':
        InFile = '$LARA/Content/psalms_kjv/corpus/Psalms_Italian.docx'
        ChapterMarker = '(Psalms'
        OutFile = '$LARA/Content/psalms_kjv/corpus/Psalms_Italian.json'
        read_jesusfellowship_file(InFile, ChapterMarker, OutFile)
    elif Id == 'psalms_translations':
        InFile = '$LARA/tmp_resources/Psalms_KJV_tmp_segment_translations.csv'
        ChapterMarker = 'Psalm'
        DictFile = '$LARA/Content/psalms_kjv/corpus/Psalms_Italian.json'
        OutFile = '$LARA/Content/psalms_kjv/translations/english_italian.csv'
        add_translations_to_csv(InFile, ChapterMarker, DictFile, OutFile)
    elif Id == 'psalms_polish':
        InFile = '$LARA/Content/psalms_kjv/corpus/Psalms_Polish.docx'
        ChapterMarker = '(Psalms'
        OutFile = '$LARA/Content/psalms_kjv/corpus/Psalms_Polish.json'
        read_jesusfellowship_file(InFile, ChapterMarker, OutFile)
    elif Id == 'psalms_polish_translations':
        InFile = '$LARA/tmp_resources/Psalms_KJV_polish_tmp_segment_translations.csv'
        ChapterMarker = 'Psalm'
        DictFile = '$LARA/Content/psalms_kjv/corpus/Psalms_Polish.json'
        OutFile = '$LARA/Content/psalms_kjv/translations/english_polish.csv'
        add_translations_to_csv(InFile, ChapterMarker, DictFile, OutFile)

def add_translations_to_csv(InFile, ChapterMarker, DictFile, OutFile):
    Dict = lara_utils.read_json_file(DictFile)
    InLines = lara_utils.read_lara_csv(InFile)
    OutLines = add_translations_to_lines(InLines, ChapterMarker, Dict)
    lara_utils.write_lara_csv(OutLines, OutFile)

def add_translations_to_lines(InLines, ChapterMarker, Dict):
    Chapter = False
    OutLines = []
    for Line in InLines:
        if len(Line) >= 2 and not Line[1] == '' and not Line[1].isspace():
            OutLine = Line
        ( LineType, I ) = categorise_line_type(Line[0], ChapterMarker)
        if LineType == 'chapter_heading' and f'chapter_{I}' in Dict:
            Translation = Dict[f'chapter_{I}']
            Chapter = I
            OutLine = [ Line[0], Translation ]
        elif LineType == 'verse' and isinstance(I, str) and ':' in I and I in Dict:
            Translation = f'{I} {Dict[I]}'
            OutLine = [ Line[0], Translation ]
        elif LineType == 'verse' and isinstance(I, int) and f'{Chapter}:{I}' in Dict:
            I1 = f'{Chapter}:{I}'
            Translation = f'{I} {Dict[I1]}'
            OutLine = [ Line[0], Translation ]
        else:
            OutLine = Line
        OutLines += [ OutLine ]
    return OutLines

def read_jesusfellowship_file(InFile, ChapterMarker, OutFile):
    InStr = lara_utils.read_lara_text_file(InFile)
    if InStr == False:
        return
    ( Dict, NChapters, NVerses ) = read_jesusfellowship_text(InStr, ChapterMarker)
    Okay = lara_utils.write_json_to_file(Dict, OutFile)
    if Okay != False:
        lara_utils.print_and_flush(f'--- Written JSON version ({NChapters} chapters, {NVerses} verses)')

def read_jesusfellowship_text(InStr, ChapterMarker):
    ( Lines, Dict, NChapters, NVerses, CurrentChapter ) = ( InStr.split('\n'), {}, 0, 0, False )
    for Line in Lines:
        ( LineType, I ) = categorise_line_type(Line, ChapterMarker)
        if LineType == 'chapter_heading':
            NChapters += 1
            CurrentChapter = I
            Key = f'chapter_{I}'
            Dict[Key] = Line
        elif LineType == 'verse':
            if CurrentChapter == False:
                lara_utils.print_and_flush(f'*** Warning: verse apparently before any chapter heading, discarding')
                lara_utils.print_and_flush(Line)
            else:
                NVerses += 1
                Key = f'{CurrentChapter}:{I}'
                Words = Line.split()
                Dict[Key] = ' '.join(Words[1:])
    return ( Dict, NChapters, NVerses )

def categorise_line_type(Line, ChapterMarker):
    Words = Line.split()
    ( Number, Index ) = find_number_in_word_list(Words)
    if Line.find(ChapterMarker) >= 0 and Number != False:
        return ( 'chapter_heading', Number )
    elif Number != False and Index == 0:
        return ( 'verse', Number )
    else:
        return ( 'other', 0 )

def find_number_in_word_list(Words):
    for Index in range(0, len(Words)):
        Number = safe_string_to_int_or_chapter_and_verse(Words[Index])
        if Number != False:
            return ( Number, Index )
    return ( False, False )

def safe_string_to_int_or_chapter_and_verse(Str):
    Number = lara_utils.safe_string_to_int(Str)
    if Number != False:
        return Number
    ChapterAndVerse = safe_string_to_chapter_and_verse(Str)
    if ChapterAndVerse != False:
        return ChapterAndVerse
    return False

def safe_string_to_chapter_and_verse(Str):
    if ':' in Str:
        Components = Str.split(':')
        if len(Components) == 2:
            ( Chapter, Verse ) = ( lara_utils.safe_string_to_int(Components[0]),
                                   lara_utils.safe_string_to_int(Components[1]) )
            if Chapter != False and Verse != False:
                return Str
    return False
        
                
            
