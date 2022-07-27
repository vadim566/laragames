# Code to convert Cathy's Lite version of "Tex's French course" into LARA form

import lara_audio
import lara_config
import lara_utils

tex_source = '$REGULUSLITECONTENT/cathy_french_translation/french_dialogue/grammars/french_dialogue.txt'
tex_source_audio_dir = '$REGULUSLITECONTENT/cathy_french_translation/french_dialogue/multimedia/help'

tex_target_corpus = '$LARA/Content/texs_french_course/corpus/texs_french_course.txt'
tex_target_translation_csv = '$LARA/Content/texs_french_course/translations/french_english.csv'
tex_target_audio_dir = '$LARA/Content/texs_french_course/audio/french_speaker/'
tex_target_audio_metadata = '$LARA/Content/texs_french_course/audio/french_speaker/metadata_help.txt'

target_title = '<h1>Tex\'s French Course||</h1>'

def convert_tex():
    LinesIn = read_source_file()
    Lessons = extract_lessons(LinesIn)
    TextLineTriples = extract_text_line_triples(LinesIn)
    AudioMetaDataLines = extract_audio_metadata(LinesIn)
    create_target_corpus(Lessons, TextLineTriples)
    create_translation_csv(TextLineTriples)
    create_audio_metadata(AudioMetaDataLines)
    #convert_and_copy_audio_files()

def read_source_file():
    Result0 = lara_utils.read_ascii_text_file_to_lines(tex_source)
    Result = [ Line for Line in Result0 if not Line.isspace() ]
    lara_utils.print_and_flush(f'--- Read source text file {tex_source}, {len(Result)} lines')
    return Result

## Lesson
## Name dialogue11
## Printname talking about ourselves and others
## Description talking about ourselves and others
## EndLesson

def extract_lessons(Lines):
    ( I, N, Out ) = ( 0, len(Lines), [] )
    while True:
        if I >= N:
            return Out
        if Lines[I].startswith('Lesson') and Lines[I+1].startswith('Name') and Lines[I+2].startswith('Printname'):
            Name = ' '.join(Lines[I+1].split()[1:])
            Printname = ' '.join(Lines[I+2].split()[1:])
            Out += [{'name': Name, 'printname': Printname }]
        I += 1

## ApplyTemplate engfre \
## "dialogue1" \
## "1" \
## "I am Robert's girlfriend." \
## "Je suis la copine de Robert."

def extract_text_line_triples(Lines):
    ( I, N, Out ) = ( 0, len(Lines), [] )
    while True:
        if I >= N:
            return Out
        if Lines[I].startswith('ApplyTemplate'):
            Lesson = extract_material_inside_quotes(Lines[I+1])
            Eng = extract_material_inside_quotes(Lines[I+3])
            Fre = extract_material_inside_quotes(Lines[I+4])
            Out += [{'lesson': Lesson, 'eng': Eng, 'fre': Fre }]
        I += 1

def extract_material_inside_quotes(Str):
    Start = Str.find('"')
    if Start < 0:
        lara_utils.print_and_flush(f'--- Unable to extract material between quotes in \'{Str}\'')
        return False
    End = Str.find('"', Start + 1)
    if End < 0:
        lara_utils.print_and_flush(f'--- Unable to extract material between quotes in \'{Str}\'')
        return False
    return Str[Start+1:End]
    

# AudioOutput help any_speaker help/5572_160617125909.wav Je suis la copine de Robert.

def extract_audio_metadata(Lines):
    ( I, N, Out ) = ( 0, len(Lines), [] )
    while True:
        if I >= N:
            return Out
        if Lines[I].startswith('AudioOutput'):
            Out += [Lines[I]]
        I += 1

def create_target_corpus(LessonDict, TextLineTriples):
    LessonTexts = [ transform_lesson_into_text(Lesson, TextLineTriples) for Lesson in LessonDict ]
    CorpusStrOut = target_title + '\n' + '\n\n'.join(LessonTexts)
    lara_utils.write_unicode_text_file(CorpusStrOut, tex_target_corpus)
    lara_utils.print_and_flush(f'--- Written corpus file {tex_target_corpus}')

# {'name': 'dialogue1', 'printname': 'about me'}
#
# {'lesson': 'dialogue1',
#  'eng': "I am Robert's girlfriend.", 'fre': 'Je suis la copine de Robert.'}

def transform_lesson_into_text(Lesson, TextLineTriples):
    HeaderText = f"/*<h2>{Lesson['printname']}</h2>*/"
    LessonId = Lesson['name']
    Lines = [ f"{Triple['fre']}||" for Triple in TextLineTriples if Triple['lesson'] == LessonId ]
    return '\n'.join([ HeaderText ] + Lines)

def create_translation_csv(TextLineTriples):
    TranslationLines = [ text_triple_to_translation_line(Triple) for Triple in TextLineTriples ]
    lara_utils.write_lara_csv(TranslationLines, tex_target_translation_csv)

def text_triple_to_translation_line(Triple):
    return [ Triple['fre'], Triple['eng'] ]

def create_audio_metadata(AudioMetaDataLines):
    AudioMetaDataLinesOut = [ transform_audio_metadata(Line) for Line in AudioMetaDataLines ]
    ContentOut = '\n'.join(AudioMetaDataLinesOut)
    lara_utils.write_unicode_text_file(ContentOut, tex_target_audio_metadata)
    lara_utils.print_and_flush(f'--- Written audio metadata file {tex_target_audio_metadata}')

# 'AudioOutput help any_speaker help/5572_160617125909.wav Je suis la copine de Robert.\n'
# 'AudioOutput help any_speaker help/12145_161223053529.mp3 Nel mezzo del cammin di nostra vita#|'

def transform_audio_metadata(Line):
    return f'{Line.rstrip().replace(".wav", ".mp3")}#|'

def convert_and_copy_audio_files():
    Params = lara_config.default_params()
    Dir = tex_source_audio_dir
    Dir1 = tex_target_audio_dir
    Files = lara_utils.directory_files(Dir)
    lara_audio.convert_lara_audio_directory_to_mp3_format1(Files, Dir, Dir1, Params)

    
    
