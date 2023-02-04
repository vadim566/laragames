
import lara_translations
import lara_audio
import lara_config
import lara_split_and_clean
import lara_picturebook
import lara_utils
import csv
import os

def convert_csv_from_quotes_to_no_quotes(InFile, OutFile):
    Content = lara_utils.read_lara_csv_specifying_quoting(InFile, 'quotes')
    lara_utils.write_lara_csv(Content, OutFile)

def convert_all_lara_csvs_from_quotes_to_no_quotes():
    RootDir = '$LARA/Content'
    for SubDir in lara_utils.directory_files(RootDir):
        FullSubDir = f'{RootDir}/{SubDir}'
        if lara_utils.directory_exists(FullSubDir):
            convert_all_lara_csvs_from_quotes_to_no_quotes1(FullSubDir)

def convert_all_lara_csvs_from_quotes_to_no_quotes1(Dir):
    if 'translations' in lara_utils.directory_files(Dir):
        TranslationDir = f'{Dir}/translations'
        convert_all_lara_csvs_from_quotes_to_no_quotes2(TranslationDir)

def convert_all_lara_csvs_from_quotes_to_no_quotes2(Dir):
    for CSVFile in lara_utils.directory_files(Dir):
        File = f'{Dir}/{CSVFile}'
        if lara_utils.extension_for_file(f'{Dir}/{CSVFile}') == 'csv':
            convert_csv_from_quotes_to_no_quotes(File, File)
            lara_utils.print_and_flush(f'--- Converted {File}')

def convert_völuspá_notes():
    SurfaceCSV = '$LARA/Content/völuspá/corpus/notes_surface.csv'
    LemmasWordsJSON = '$LARA/Content/völuspá/corpus/headword_word.json'
    BlankLemmaCSV = '$LARA/tmp_resources/völuspá_tmp_notes.csv'
    LemmaCSV = '$LARA/Content/völuspá/corpus/notes.csv'
    convert_surface_csv_to_lemma_csv(SurfaceCSV, LemmasWordsJSON, BlankLemmaCSV, LemmaCSV)

def convert_surface_csv_to_lemma_csv(SurfaceCSV, LemmasWordsJSON, BlankLemmaCSV, LemmaCSV):
    SurfaceContent = lara_utils.read_lara_csv(SurfaceCSV)
    BlankLemmaContent = lara_utils.read_lara_csv(BlankLemmaCSV)
    SurfaceContentDict = { Line[0]: Line[1] for Line in SurfaceContent if Line[1] != '' }
    LemmasSurfaceDict = lara_utils.read_json_file(LemmasWordsJSON)
    FilledLemmaContent = [ convert_blank_lemma_line(Line, LemmasSurfaceDict, SurfaceContentDict) for Line in BlankLemmaContent ]
    lara_utils.write_lara_csv(FilledLemmaContent, LemmaCSV)

def convert_blank_lemma_line(Line, LemmasSurfaceDict, SurfaceContentDict):
    Lemma = Line[0]
    Note = ''
    if Lemma in LemmasSurfaceDict:
        SurfaceWords = LemmasSurfaceDict[Lemma]
        for SurfaceWord in SurfaceWords:
            RegularisedSurfaceWord = lara_translations.regularise_word(SurfaceWord)
            if RegularisedSurfaceWord in SurfaceContentDict:
                Note = SurfaceContentDict[RegularisedSurfaceWord]
    return [ Lemma, Note ]

def extract_phrasal_verbs():
    InFile = '$LARA/Content/english/corpus/phrasal_verbs_raw.txt'
    OutFile = '$LARA/Content/english/corpus/phrasal_verbs.txt'
    InList = lara_utils.read_lara_text_file(InFile).split('\n')
    lara_utils.print_and_flush(f'--- Read raw file ({len(InList)} lines) {InFile}')
    OutList = []
    for Line in InList:
        if is_phrasal_verb_definition(Line):
            OutList += [ line_to_lara_phrasal_verb(Line) ]
    OutList.sort()
    SortedOutList = lara_utils.remove_duplicates(OutList)
    lara_utils.write_lara_text_file('\n'.join(SortedOutList), OutFile)
    lara_utils.print_and_flush(f'--- Written file ({len(OutList)} lines) {OutFile}')

# Answer back: Reply impertinently; to talk back

def is_phrasal_verb_definition(Line):
    ColonIndex = Line.find(':')
    return ColonIndex > 0 and \
           ColonIndex + 5 < len(Line) and \
           Line[0].isupper()

def line_to_lara_phrasal_verb(Line):
    ColonIndex = Line.find(':')
    VerbText = Line[:ColonIndex]
    Words = VerbText.split()
    return ' '.join( [ Words[0].upper() ] + Words[1:] )

def remove_duplicates_from_phrasal_verb_file():
    InFile = '$LARA/Content/english/corpus/phrasal_verbs.txt'
    OutFile = '$LARA/Content/english/corpus/phrasal_verbs_no_dups.txt'
    InList = lara_utils.read_lara_text_file(InFile).split('\n')
    lara_utils.print_and_flush(f'--- Read raw file ({len(InList)} lines) {InFile}')
    OutList = lara_utils.remove_duplicates(InList)
    lara_utils.write_lara_text_file('\n'.join(OutList), OutFile)
    lara_utils.print_and_flush(f'--- Written file ({len(OutList)} lines) {OutFile}')

# ---------------------------

def remove_nul_chars_from_file(InFile, OutFile):
    Content = lara_utils.read_lara_text_file(InFile)
    lara_utils.write_lara_text_file(Content.replace('\0', ''), OutFile)

# ---------------------------

def reformat_file_with_audio_timings():
    InFile = '$LARA/Content/völuspá/corpus/völuspá_audio_tracking_imba.txt'
    AudioTrackingFile = '$LARA/Content/völuspá/audio/Imba/audio_tracking.json'
    OutFile = '$LARA/Content/völuspá/corpus/völuspá_audio_tracking_with_timings_imba.txt'
    reformat_file_with_audio_timings1(InFile, AudioTrackingFile, OutFile)

##   <tr><td><audio id="audio_1" src="this segment"/><br/></td><td>/**/</td></tr>
##   <tr><td>/*v.Vsp.1*/</td><td>/**/</td></tr>
##   <tr><td class="audio_1_line">Hljóðs#hljóð# bið#biðja# ek</td><td>/*Hliods bið ec*/</td></tr>
##   <tr><td class="audio_1_line">allar#allr# kindir#kind#,</td><td>/*allar kindir*/</td></tr>
##   <tr><td class="audio_1_line">meiri ok minni</td><td>/*meiri oc miNi*/</td></tr>
##   <tr><td class="audio_1_line">mögu#mögr# Heimdalar#Heimdallr#;</td><td>/*mavgo ¦ heimdallar*/</td></tr>
##   <tr><td class="audio_1_line">vildu#vilja# að#at# ek, Valföðr#Valföðr#,</td><td>/*vilðo at ec ualfa/þr*/</td></tr>
##   <tr><td class="audio_1_line">vel fram telja</td><td>/*uel fyr telia*/</td></tr>
##   <tr><td class="audio_1_line">forn spjöll#spjall# fira#firar#,</td><td>/*forn ¦ spioll fíra*/</td></tr>
##   <tr><td class="audio_1_line">þau#sá# er fremst#framr# um man#muna#.||</td><td>/*þa/ er fremst um man.*/</td></tr>   <tr><td></td><td>/**/</td></tr>

##{ 
##"audio_1": [ 0, 3.0, 4.0, 5.5, 7.0, 9.2, 10.8, 12.8, 15.0 ],
##"audio_2": [ 0, 2, 4.5, 6.5, 7.5, 10.5, 12.5, 15.0, 17.5 ],

def reformat_file_with_audio_timings1(InFile, AudioTrackingFile, OutFile):
    TrackingData = lara_utils.read_json_file(AudioTrackingFile)
    ( CurrentAudioId, CurrentTimings, OutLines ) = ( '', [], [] )
    for Line in lara_utils.read_lara_text_file(InFile).split('\n'):
        ( Type, AudioId ) = get_audio_line_type_and_id(Line)
        if Type == 'id':
            CurrentAudioId = AudioId
            if AudioId in TrackingData: 
                CurrentTimings = TrackingData[AudioId][1:]
            else:
                lara_utils.print_and_flush(f'*** Warning: no tracking data for {AudioId}')
                CurrentTimings = []
            OutLine = Line.replace(f'id="{AudioId}"', 'tracking="yes"')
        elif Type == 'class':
            ( Time, CurrentTimings) = ( CurrentTimings[0], CurrentTimings[1:] ) if len(CurrentTimings) > 0 else ( 0.0, [] )
            OutLine = Line.replace(f'class="{AudioId}_line"', f'end_time="{Time}"')
        else:
            OutLine = Line
        OutLines += [ OutLine ]
    lara_utils.write_lara_text_file('\n'.join(OutLines), OutFile)

##   <tr><td><audio id="audio_1" src="this segment"/><br/></td><td>/**/</td></tr>
##   <tr><td>/*v.Vsp.1*/</td><td>/**/</td></tr>
##   <tr><td class="audio_1_line">Hljóðs#hljóð# bið#biðja# ek</td><td>/*Hliods bið ec*/</td></tr>

def get_audio_line_type_and_id(Line):
    IdStr = 'audio id="'
    Start = Line.find(IdStr)
    if Start > 0:
        End = Line.find('"', Start + len(IdStr))
        if End < 0:
            lara_utils.print_and_flush(f'*** Error: bad line {Line}')
            return False
        else:
            return ( 'id', Line[Start + len(IdStr):End] )
    ClassStr = 'class="'
    Start = Line.find(ClassStr)
    if Start > 0:
        End = Line.find('_line"', Start + len(ClassStr))
        if End < 0:
            lara_utils.print_and_flush(f'*** Error: bad line {Line}')
            return False
        else:
            return ( 'class', Line[Start + len(ClassStr):End] )
    return ( 'other', '' )

def merge_vsp_audio_tracking():
    OldTimingFile = '$LARA/Content/völuspá/audio/Imba/audio_tracking_old.json'
    NewTimingFile = '$LARA/Content/völuspá/audio/Imba/audio_tracking_branislav.json'
    MergedTimingFile = '$LARA/Content/völuspá/audio/Imba/audio_tracking.json'
    merge_audio_tracking(OldTimingFile, NewTimingFile, MergedTimingFile)

def merge_audio_tracking(OldTimingFile, NewTimingFile, MergedTimingFile):
    OldData = lara_utils.read_json_file(OldTimingFile)
    lara_utils.print_and_flush(f'--- Read old timing data, {len(OldData)} records')
    NewData = lara_utils.read_json_file(NewTimingFile)
    lara_utils.print_and_flush(f'--- Read new timing data, {len(NewData)} records')
    for Key in OldData:
        if not Key in NewData:
            NewData[Key] = OldData[Key]
    lara_utils.write_json_to_file(NewData, MergedTimingFile)
    lara_utils.print_and_flush(f'--- Written merged timing data, {len(NewData)} records')

def add_markup_to_hebrew_palindrome():
    #InFile = '$LARA/Content/revivalistics/corpus/palindrome.txt'
    InFile = '$LARA/Content/revivalistics/corpus/GZ_Palindrome.docx'
    OutFile = '$LARA/Content/revivalistics/corpus/palindrome_annotated.txt'
    InStr = lara_utils.read_lara_text_file(InFile)
    OutStr = add_markup_to_hebrew_palindrome_str(InStr)
    lara_utils.write_lara_text_file(OutStr, OutFile)

def add_markup_to_hebrew_palindrome_str(InStr):
    ( OutStr, I, N, State ) = ( '', 0, len(InStr), 'not_in_sentence' )
    while True:
        if I >= N:
            return OutStr
        c = InStr[I]
        if c == '.': 
            OutStr += '}}||\n'
            State = 'not_in_sentence'
            I += 1
        elif State == 'not_in_sentence' and not c.isspace():
            State = 'in_sentence'
            OutStr += '{{'
            OutStr += c
            I += 1
        elif c == '\n' and State == 'in_sentence':
            OutStr += ' '
            I += 1
        elif c.isspace() and State == 'not_in_sentence':
            I += 1
        else:
            OutStr += c
            I += 1

def find_config_files_for_treetagger_testing():
    InFile = '$LARA/Content/config_files_large.json'
    OutFile = '$LARA/Content/config_files_large_treetagging.json'
    extract_config_files_for_treetagger_testing(InFile, OutFile)

def extract_config_files_for_treetagger_testing(InFile, OutFile):
    InItems = lara_utils.read_json_file(InFile)
    lara_utils.print_and_flush(f'--- Found {len(InConfigFiles)} test items in {InFile}')
    OutItems = [ Item for Item in InItems if
                 is_item_for_treetagger_testing(Item) ]
    lara_utils.write_json_to_file(OutItems, OutFile)
    lara_utils.print_and_flush(f'--- Written {len(OutItems)} config files to {OutFile}')

def is_item_for_treetagger_testing(Item):
    if not isinstance(Item, dict) or not 'config_file' in Item:
        return False
    try:
        Params = lara_config.read_lara_local_config_file(Item['config_file'])
        return Params and \
               lara_utils.file_exists(Params.untagged_corpus) and \
               Params.tagged_corpus != ''
    except:
        return False

def read_csv(pathname, encoding, delimiter, Quotes):
    abspathname = lara_utils.absolute_file_name(pathname)
    try:
        with open(abspathname, 'r', encoding=encoding) as f:
            if Quotes == 'quotes':
                reader = csv.reader(f, delimiter=delimiter, quotechar='"')
            else:
                reader = csv.reader(f, delimiter=delimiter, quotechar='"', quoting=csv.QUOTE_MINIMAL)
            List = list(reader)
        f.close()
        lara_utils.print_and_flush(f'--- Read CSV spreadsheet as {encoding} ({len(List)} lines) {abspathname}')
        return List
    except Exception as e:
        lara_utils.print_and_flush(f'*** Error: when trying to read CSV {abspathname} as {encoding}')
        lara_utils.print_and_flush(str(e))
        return False 

def copy_farsi_doc_imgs():
    ImgList = ["Start.jpg", "Signup.jpg", "LPPortalTopLevel.jpg",
               "CrowdsourcingDashboard.jpg", "AvailableTasks1.jpg",
               "AvailableTasks2.jpg", "MyLARATexts.jpg", "LPChapterProject.jpg",
               "CreateResourcesSucceeded.jpg", "LPFillOutResourcesTranslation.jpg",
               "LPSegmentTranslation.jpg", "LPSegmentTranslationControls.jpg",
               "LPFillOutResourcesTranslation.jpg", "LPTokenTranslation.jpg",
               "AssignRecordingVoice.jpg", "Recording1.jpg", "Recording2.jpg",
               "LogInToLDT.jpg", "LDT1.jpg", "LDT2.jpg", "LDTRecordingSegments.jpg",
               "LPCreatePages1.jpg", "LPCreatePages2.jpg", "LPPreview.jpg",
               "LPPTranslationAudioNoteSettings1.jpg", "LPPTranslationAudioNoteSettings2.jpg",
               "LPPTranslationAudioNoteSettings3.jpg", "LPReturningTask.jpg"]
    Dir = '$LARA/Doc/LARAFarsiLPDoc/source/_static'
    Dir1 = '$LARA/Doc/LARAFarsiLPDoc/source/_static1'
    for Img in ImgList:
        lara_utils.copy_file(f'{Dir}/{Img}', f'{Dir1}/{Img}')

def combray_pairs_file_to_text_file():
    PairsFile = '$LARA/Content/combray/corpus/combray_full_word_pairs.json'
    TextFile = '$LARA/Content/combray/corpus/combray_for_alignment.txt'
    pairs_file_to_text_for_alignment(PairsFile, TextFile)
    
        
def pairs_file_to_text_for_alignment(PairsFile, TextFile):
    PairsData = lara_utils.read_json_file(PairsFile)
    Text = ''
    for ( PageInfo, Pairs ) in PairsData:
        #Text += '<page>'
        Text += ''.join([ Pair[1] for Pair in Pairs ])
    lara_utils.write_lara_text_file(Text, TextFile)

def remove_ch1_from_pitj_audio():
    File = '$LARA/Content/pitjantjatjara_course/audio/pitjantjatjara_voice/metadata_help.json'
    FileNoCh1 = '$LARA/Content/pitjantjatjara_course/audio/pitjantjatjara_voice/metadata_help_no_ch1.json'
    Metadata = lara_utils.read_json_file(File)
    MetadataNoCh1 = [ Item for Item in Metadata if not '_ch1_' in Item['file'] ]
    lara_utils.write_json_to_file_plain_utf8(MetadataNoCh1, FileNoCh1)
    
def remove_ch14_from_pitj_audio():
    File = '$LARA/Content/pitjantjatjara_course/audio/pitjantjatjara_voice/metadata_help.json'
    FileNoCh14 = '$LARA/Content/pitjantjatjara_course/audio/pitjantjatjara_voice/metadata_help_no_ch14.json'
    Metadata = lara_utils.read_json_file(File)
    MetadataNoCh14 = [ Item for Item in Metadata if not 'ch14' in Item['file'] ]
    lara_utils.write_json_to_file_plain_utf8(MetadataNoCh14, FileNoCh14)

def remove_ch12_from_pitj_audio():
    File = '$LARA/Content/pitjantjatjara_course/audio/pitjantjatjara_voice/metadata_help.json'
    FileNoCh12 = '$LARA/Content/pitjantjatjara_course/audio/pitjantjatjara_voice/metadata_help_no_ch12.json'
    Metadata = lara_utils.read_json_file(File)
    MetadataNoCh12 = [ Item for Item in Metadata if not 'ch12' in Item['file'] ]
    lara_utils.write_json_to_file_plain_utf8(MetadataNoCh12, FileNoCh12)

def plain_utf8_pitj_metadata():
    File = '$LARA/Content/pitjantjatjara_course/audio/pitjantjatjara_voice/metadata_help.json'
    Metadata = lara_utils.read_json_file(File)
    lara_utils.write_json_to_file_plain_utf8(Metadata, File)
        
def make_pitj_only_audio_dir():
    ConfigFile = '$LARA/Content/pitjantjatjara_course/corpus/local_config_cover.json'
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    CleanedSegments = get_cleaned_segments(Params)
    lara_utils.print_and_flush(f'--- Found {len(CleanedSegments)} segments')
    CleanedWords = get_cleaned_words(Params)
    lara_utils.print_and_flush(f'--- Found {len(CleanedWords)} surface words')
    CleanedSegmentsAndWordsDict = { Item:True for Item in CleanedSegments + CleanedWords }
    File = '$LARA/Content/pitjantjatjara_course/audio/pitjantjatjara_voice_trimmed/metadata_help.json'
    Metadata = lara_utils.read_json_file(File)
    lara_utils.print_and_flush(f'--- Found {len(Metadata)} items of metadata')
    RelevantMetadata = [ Item for Item in Metadata
                         if Item['text'] in CleanedSegmentsAndWordsDict ]
    lara_utils.print_and_flush(f'--- Found {len(RelevantMetadata)} relevant items of metadata')
    AudioDir = '$LARA/Content/pitjantjatjara_course/audio/pitjantjatjara_voice_trimmed'
    AudioDirFiltered = '$LARA/Content/pitjantjatjara_course/audio/pitjantjatjara_voice_trimmed_filtered'
    lara_utils.create_directory_if_it_doesnt_exist(AudioDirFiltered)
    for Item in RelevantMetadata:
        File = Item['file']
        lara_utils.copy_file(f'{AudioDir}/{File}', f'{AudioDirFiltered}/{File}')
    lara_audio.write_ldt_metadata_file(RelevantMetadata, AudioDirFiltered)

def total_audio_length_pitj():
    File = '$LARA/Content/pitjantjatjara_course/audio/pitjantjatjara_voice_trimmed_filtered/metadata_help.json'
    Metadata = lara_utils.read_json_file(File)
    Dir = '$LARA/Content/pitjantjatjara_course/audio/pitjantjatjara_voice_trimmed_filtered'
    TotalLength = sum([ lara_utils.length_of_mp3(f'{Dir}/{Item["file"]}') for Item in Metadata ]) / 3600
    lara_utils.print_and_flush(f'--- Total length of audio: {TotalLength:.2f} hours')

def get_cleaned_segments(Params):
    SplitFileData = lara_split_and_clean.read_split_file('', Params)
    CleanedSegments = []
    for ( PageInfo, Segments ) in SplitFileData:
        for Chunk in Segments:
            if lara_picturebook.is_annotated_image_segment(Chunk):
                InnerChunks = lara_picturebook.annotated_image_segments(Chunk)
                for Chunk in InnerChunks:
                    CleanedSegments += [ Chunk[1] ]
            else:
                CleanedSegments += [ Chunk[1] ]
    return lara_utils.remove_duplicates(CleanedSegments)

def get_cleaned_words(Params):
    SplitFileData = lara_split_and_clean.read_split_file('', Params)
    CleanedWords = []
    for ( PageInfo, Segments ) in SplitFileData:
        for Chunk in Segments:
            if lara_picturebook.is_annotated_image_segment(Chunk):
                InnerChunks = lara_picturebook.annotated_image_segments(Chunk)
                for Chunk in InnerChunks:
                    CleanedWords += [ lara_audio.make_word_canonical_for_word_recording(Pair[0])
                                      for Pair in Chunk[2] if Pair[1] != '' ] 
            else:
                CleanedWords += [ lara_audio.make_word_canonical_for_word_recording(Pair[0])
                                  for Pair in Chunk[2] if Pair[1] != '' ] 
    return lara_utils.remove_duplicates(CleanedWords)
  
def rename_mp3s_in_dir_to_include_artist_name(Dir):
    import eyed3
    if not lara_utils.directory_exists(Dir):
        lara_utils.print_and_flush(f'*** Error: unable to find directory {Dir}')
        return
    convert_wmas_to_mp3s(Dir)
    AbsDir = lara_utils.absolute_file_name(Dir)
    Files = lara_utils.file_members_of_directory(Dir)
    N = 0
    for File in Files:
        FullFile = f'{Dir}/{File}'
        if lara_utils.extension_for_file(File) == 'mp3':
            Audiofile = eyed3.load(FullFile)
            ArtistName = Audiofile.tag.artist if Audiofile.tag != None else None
            if ArtistName != None and File.startswith(ArtistName):
                lara_utils.print_and_flush(f'*** Warning "{File}" already starts with "{ArtistName}", not renaming')
            else:
                File1 = f'{ArtistName} {File}'
                FullFile1 = f'{Dir}/{File1}'
                os.rename(FullFile, FullFile1)
                lara_utils.print_and_flush(f'--- Renamed "{File}" to "{File1}"')
                N += 1
    lara_utils.print_and_flush(f'--- Renamed {N} files')

def convert_wmas_to_mp3s(Dir):
    AbsDir = lara_utils.absolute_file_name(Dir)
    Files = lara_utils.file_members_of_directory(Dir)
    N = 0
    for File in Files:
        if lara_utils.extension_for_file(File) == 'wma':
            if convert_wma_to_mp3(Dir, File):
                N += 1
    lara_utils.print_and_flush(f'--- Converted {N} files')
    
def convert_wma_to_mp3(Dir, File):
    ( BaseFile, OldExtension ) = split_pathname_into_base_file_and_extension(File)
    FullFile = f'{Dir}/{File}'
    FullFileTo = f'{Dir}/{BaseFile}.mp3'
    if lara_utils.file_exists(FullFileTo):
        lara_utils.print_and_flush(f'*** Warning: "{FullFile}" already converted to "{FullFileTo}"')
        return True
    Command = f'ffmpeg -i "{FullFile}" -b:a 50k -ar 48000 "{FullFileTo}"'
    Result = execute_ffmpeg_command(Command, FullFileTo, lara_config.default_params())
    if Result:
        lara_utils.print_and_flush(f'--- Converted "{FullFile}" to "{FullFileTo}"')
        return True
    else:
        lara_utils.print_and_flush(f'\n*** Warning: unable to convert {FullFile}')
        lara_utils.print_and_flush(f'*** with command {Command}')
        return False

def execute_ffmpeg_command(Command, OutFile, Params):
    lara_utils.delete_file_if_it_exists(OutFile)
    Status = lara_utils.execute_lara_os_call(Command, Params)
    if Status == 0:
        return True
    else:
        return False

def split_pathname_into_base_file_and_extension(File):
    Components = File.split('.')
    if len(Components) == 1:
        return ( File, '')
    else:
        return ( '.'.join(Components[:-1]), Components[-1] )

            
    

