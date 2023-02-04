import lara_config
import lara_audio
import lara_utils

def test(Id):
    if Id == 'recueillement':
        AudioFile = '$LARA/Content/recueillement_tmp/audio/litteratureaudio_src/Charles_Baudelaire_-_Les_Fleurs_du_mal_P8_104_Recueillement.mp3'
        LengthThreshold = 0.5
        dBThreshold = 30
        LabelFile = '$LARA/Content/recueillement_tmp/corpus/LabelTrack_from_ffmpeg.txt'
        ConfigFile = '$LARA/Content/recueillement_tmp/corpus/local_config.json'
        make_silence_label_file(AudioFile, LengthThreshold, dBThreshold, LabelFile, ConfigFile)
    elif Id == 'candide':
        AudioFile = '$LARA/Content/candide/audio/litteratureaudio_src/Voltaire_-_Candide_Chap01.mp3'
        LengthThreshold = 0.60
        dBThreshold = 30
        LabelFile = '$LARA/Content/candide/corpus/LabelTrack_from_ffmpeg_60.txt'
        ConfigFile = '$LARA/Content/candide/corpus/local_config.json'
        make_silence_label_file(AudioFile, LengthThreshold, dBThreshold, LabelFile, ConfigFile)
    elif Id == 'combray_ch2':
        AudioFile = '$LARA/Content/combray/audio/MoniqueVincens_src/Marcel_Proust_-_Du_Cote_de_chez_Swann_L1_Combray_Chap02.mp3'
        LengthThreshold = 0.40
        dBThreshold = 27
        LabelFile = '$LARA/Content/combray/corpus/LabelTrack_from_ffmpeg_ch2.txt'
        ConfigFile = '$LARA/Content/combray/corpus/local_config_segmented_by_audio.json'
        make_silence_label_file(AudioFile, LengthThreshold, dBThreshold, LabelFile, ConfigFile)
    elif Id == 'combray_small':
        AudioFile = '$LARA/Content/combray/audio/MoniqueVincens_src/Marcel_Proust_-_Du_Cote_de_chez_Swann_L1_Combray_small.mp3'
        LengthThreshold = 0.40
        dBThreshold = 27
        LabelFile = '$LARA/Content/combray/corpus/LabelTrack_from_ffmpeg_small.txt'
        ConfigFile = '$LARA/Content/combray/corpus/local_config_segmented_by_audio.json'
        make_silence_label_file(AudioFile, LengthThreshold, dBThreshold, LabelFile, ConfigFile)
    elif Id == 'combray_ch1':
        AudioFile = '$LARA/Content/combray/audio/MoniqueVincens_src/Marcel_Proust_-_Du_Cote_de_chez_Swann_L1_Combray_Chap01.mp3'
        LengthThreshold = 0.40
        dBThreshold = 27
        LabelFile = '$LARA/Content/combray/corpus/LabelTrack_from_ffmpeg_ch1.txt'
        ConfigFile = '$LARA/Content/combray/corpus/local_config_ch1_double_align.json'
        make_silence_label_file(AudioFile, LengthThreshold, dBThreshold, LabelFile, ConfigFile)
    elif Id == 'trim_pitj_1':
        Params = lara_config.default_params()
        InFile = '$LARA/Content/pitjantjatjara_course/audio/pitjantjatjara_voice/extracted_file_ch1_18.mp3'
        OutFile = '$LARA/Content/pitjantjatjara_course/audio/pitjantjatjara_voice_trimmed/extracted_file_ch1_18.mp3'
        dBthreshold = 20
        IgnoreAtEnd = 0.1
        trim_mp3(InFile, dBthreshold, IgnoreAtEnd, OutFile, Params)
    elif Id == 'trim_pitj_all':
        ConfigFile = '$LARA/Content/pitjantjatjara_course/corpus/local_config.json'
        trim_all_sentence_audio(ConfigFile, dBthreshold, IgnoreAtEnd)


def make_silence_label_file_from_config(ConfigFile, AudioId):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if Params == False:
        return False
    CuttingUpParameters = Params.audio_cutting_up_parameters
    if CuttingUpParameters == None:
        lara_utils.print_and_flush(f'*** Error: audio_cutting_up_parameters is not defined')
        return False
    if not isinstance(CuttingUpParameters, list):
        lara_utils.print_and_flush(f'*** Error: bad value for audio_cutting_up_parameters, {CuttingUpParameters}. Needs to be a list')
        return False
    for Item in CuttingUpParameters:
        if not isinstance(Item, dict):
            lara_utils.print_and_flush(f'*** Error: bad item in audio_cutting_up_parameters, {Item}. Needs to be a dict')
            return False
        if 'id' in Item and Item['id'] == AudioId:
            Result = get_cutting_up_parameters_for_audio_cutting_up_parameters_item(Item)
            if Result == False:
                return
            ( AudioFile, LengthThreshold, dBThreshold, LabelFile ) = Result
            make_silence_label_file(AudioFile, LengthThreshold, dBThreshold, LabelFile, ConfigFile)
            return
    lara_utils.print_and_flush(f'*** Error: no entry for {AudioId} in audio_cutting_up_parameters')
    return False

def get_cutting_up_parameters_for_audio_cutting_up_parameters_item(Item):
    if not 'audio_file' in Item:
        lara_utils.print_and_flush(f'*** Error: bad item in audio_cutting_up_parameters, {Item}. "audio_file" not defined.')
        return False
    if not lara_utils.file_exists(Item["audio_file"]):
        lara_utils.print_and_flush(f'*** Error: {Item["audio_file"]} not found.')
        return False
    if not 'audio_labels_file' in Item:
        lara_utils.print_and_flush(f'*** Error: bad item in audio_cutting_up_parameters, {Item}. "audio_labels_file" not defined.')
        return False
    if not 'length_threshold' in Item:
        lara_utils.print_and_flush(f'*** Error: bad item in audio_cutting_up_parameters, {Item}. "length_threshold" not defined.')
        return False
    if not isinstance(Item['length_threshold'], ( int, float )):
        lara_utils.print_and_flush(f'*** Error: bad value for "length_threshold" in {Item}. Must be a number.')
        return False
    if not 'db_threshold' in Item:
        lara_utils.print_and_flush(f'*** Error: bad item in audio_cutting_up_parameters, {Item}. "db_threshold" not defined.')
        return False
    if not isinstance(Item['db_threshold'], ( int )):
        lara_utils.print_and_flush(f'*** Error: bad value for "db_threshold" in {Item}. Must be an integer.')
        return False
    return ( Item['audio_file'], Item['length_threshold'], Item['db_threshold'],Item['audio_labels_file'] )

# Creates a label file in Audacity format marking midpoints of silences.
def make_silence_label_file(AudioFile, LengthThreshold, dBThreshold, LabelFile, ConfigFile):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if Params == False:
        return False
    TmpFile = lara_utils.get_tmp_trace_file(Params)
    Command = ffmpeg_find_silences_command(AudioFile, LengthThreshold, dBThreshold, TmpFile)
    if Command == False:
        return False
    Result = execute_ffmpeg_command(Command, TmpFile, Params)
    if Result == False:
        lara_utils.print_and_flush(f'*** Error: command failed: "{Command}"')
        return False
    LengthOfFileInSeconds = lara_utils.length_of_mp3(AudioFile)
    return ffmpeg_silence_trace_file_to_audacity_label_file(TmpFile, LabelFile, LengthThreshold, LengthOfFileInSeconds)

# ffmpeg -i Charles_Baudelaire_-_Les_Fleurs_du_mal_P8_104_Recueillement.mp3 -af silencedetect=noise=-40dB:d=0.5 -f null - 2> vol.txt

def ffmpeg_find_silences_command(AudioFile, LengthThreshold, dBThreshold, TraceFile):
    if not isinstance(LengthThreshold, ( int, float )) or LengthThreshold <= 0.0:
        lara_utils.print_and_flush(f'*** Error in call to ffmpeg_find_silences_command: bad length threshold "{LengthThreshold}": needs to be a positive number')
        return False
    if not isinstance(dBThreshold, ( int, float )) or dBThreshold <= 0.0:
        lara_utils.print_and_flush(f'*** Error in call to ffmpeg_find_silences_command: bad dB threshold "{dBThreshold}": needs to be a positive number')
        return False
    if not lara_utils.file_exists(AudioFile):
        lara_utils.print_and_flush(f'*** Error in call to ffmpeg_find_silences_command: audio file not found "{AudioFile}"')
        return False
    ( AbsAudioFile, AbsTraceFile ) = ( lara_utils.absolute_file_name(AudioFile), lara_utils.absolute_file_name(TraceFile) )
    return f'ffmpeg -i "{AbsAudioFile}" -af silencedetect=noise=-{dBThreshold}dB:d={LengthThreshold} -f null - 2> {AbsTraceFile}'

def execute_ffmpeg_command(Command, TraceFile, Params):
    lara_utils.delete_file_if_it_exists(TraceFile)
    lara_utils.print_and_flush(f'--- Detecting silences: {Command}')
    Status = lara_utils.execute_lara_os_call(Command, Params)
    lara_utils.print_and_flush(f'--- Done, result = {Status}')
    return True if Status == 0 else False

##    [silencedetect @ 000001fe6eb79d40] silence_start: 0.763628
##    [silencedetect @ 000001fe6eb79d40] silence_end: 2.7241 | silence_duration: 1.96048
##    [silencedetect @ 000001fe6eb79d40] silence_start: 4.11261
##    [silencedetect @ 000001fe6eb79d40] silence_end: 4.72444 | silence_duration: 0.611837

##    (Tab separated)
##    1.108986	1.108986	2
##    2.008343	2.008343	3

def ffmpeg_silence_trace_file_to_audacity_label_file(TmpFile, LabelFile, LengthThreshold, LengthOfFileInSeconds):
    Lines = lara_utils.read_ascii_text_file_to_lines(TmpFile)
    ( State, CurrentItem, ParsedLines ) = ( 'waiting_for_start', {}, [] )
    for Line in Lines:
        Components = Line.split()
        if State == 'waiting_for_start' and '[silencedetect' in Line and 'silence_start:' in Line:
            CurrentItem['start'] = lara_utils.safe_string_to_number(Components[Components.index('silence_start:') + 1])
            State = 'waiting_for_end'
        elif State == 'waiting_for_end' and '[silencedetect' in Line and 'silence_end:' in Line:
            CurrentItem['end'] = lara_utils.safe_string_to_number(Components[Components.index('silence_end:') + 1])
            ParsedLines += [ CurrentItem ]
            CurrentItem = {}
            State = 'waiting_for_start'
    ParsedLines1 = [ parsed_ffmpeg_line_to_midpoint_and_length(Line) for Line in ParsedLines ]
    summarise_parsed_ffmpeg_trace_and_create_label_file(ParsedLines1, LengthThreshold, LengthOfFileInSeconds, LabelFile)
    return True

def summarise_parsed_ffmpeg_trace_and_create_label_file(ParsedLines0, LengthThreshold, LengthOfFileInSeconds, LabelFile):
    lara_utils.print_and_flush(f'-------------')
    lara_utils.print_and_flush(f'--- Threshold: {LengthThreshold:.2f} secs')
    ParsedLines = [ Item for Item in ParsedLines0 if Item['silence_length'] >= LengthThreshold ]
    ParsedLines1 = maybe_add_silence_item_at_end(ParsedLines, LengthOfFileInSeconds)
    NBreakpoints = len(ParsedLines1)
    if NBreakpoints == 0:
        lara_utils.print_and_flush(f'--- No silences found matching spec')
        return
    AvSilenceLength = sum([ Item['silence_length'] for Item in ParsedLines1 ]) / NBreakpoints
    LongestSilenceLength = sorted(ParsedLines1, key=lambda x: x['silence_length'], reverse=True)[0]['silence_length']
    ( SegmentLengths, CurrentPos ) = ( [], 0.0 )
    for ParsedLine in ParsedLines1:
        NewMidpoint = ParsedLine['silence_midpoint']
        ParsedLine['preceding_segment_length'] = NewMidpoint - CurrentPos
        CurrentPos = NewMidpoint
    AvSegmentLength = sum([ Item['preceding_segment_length'] for Item in ParsedLines1 ]) / NBreakpoints
    SegmentsOver60Secs = len([ Item for Item in ParsedLines1 if Item['preceding_segment_length'] > 60 ])
    SegmentsOver45Secs = len([ Item for Item in ParsedLines1 if Item['preceding_segment_length'] > 45 ])
    SegmentsOver30Secs = len([ Item for Item in ParsedLines1 if Item['preceding_segment_length'] > 30 ])
    LongestSegmentLength = sorted(ParsedLines1, key=lambda x: x['preceding_segment_length'], reverse=True)[0]['preceding_segment_length']
    lara_utils.print_and_flush(f'--- #Silences: {NBreakpoints}')
    lara_utils.print_and_flush(f'--- Average silence length: {AvSilenceLength:.2f} secs')
    lara_utils.print_and_flush(f'--- Average segment length: {AvSegmentLength:.2f} secs')
    lara_utils.print_and_flush(f'--- Longest segment length: {LongestSegmentLength:.2f} secs')
    lara_utils.print_and_flush(f'--- #Segments over 60 secs: {SegmentsOver60Secs}')
    lara_utils.print_and_flush(f'--- #Segments over 45 secs: {SegmentsOver45Secs}')
    lara_utils.print_and_flush(f'--- #Segments over 30 secs: {SegmentsOver30Secs}')
    LabelFileLines = [ parsed_ffmpeg_trace_line_to_audacity_label_line(Item) for Item in ParsedLines1 ]
    if False in LabelFileLines:
        return False
    #LabelFile = label_file_name(LabelFileBase, LengthThreshold)
    lara_utils.write_lara_text_file('\n'.join(LabelFileLines), LabelFile)
    lara_utils.print_and_flush(f'--- Written Audacity labels file ({len(LabelFileLines)} labels) {LabelFile}')

def maybe_add_silence_item_at_end(ParsedLines, LengthOfFileInSeconds):
    if len(ParsedLines) != 0 and LengthOfFileInSeconds - ParsedLines[-1]['silence_midpoint'] > 0.5:
        FinalItem = { 'silence_midpoint': ( LengthOfFileInSeconds - 0.05 ),
                      'silence_length': 0.05 }
        return ParsedLines + [ FinalItem ]
    else:
        return ParsedLines

def label_file_name(LabelFileBase, LengthThreshold):
    ( Base, Ext ) = lara_utils.file_to_base_file_and_extension(LabelFileBase)
    Number = int( 100 * LengthThreshold )
    return f'{Base}_{Number}.{Ext}'

def parsed_ffmpeg_trace_line_to_audacity_label_line(Item):
    Middle = Item['silence_midpoint']
    return f'{Middle:.4f}\t{Middle:.4f}\tx'

def parsed_ffmpeg_line_to_midpoint_and_length(Item):
    if not isinstance(Item, dict) or not 'start' in Item or not 'end' in Item:
        lara_utils.print_and_flush(f'*** Error: bad item in parsed ffmpeg trace: {Item}')
        return False
    else:
        ( Start, End ) = ( Item['start'], Item['end'] )
        Middle = ( Start + End ) / 2
        Length = End - Start
        return { 'silence_midpoint': Middle, 'silence_length': Length }
            
# -----------------------------------------------------

def trim_all_sentence_audio(ConfigFile):
    Params = lara_config.read_lara_local_config_file(ConfigFile)
    if Params == False:
        return
    Dir = Params.segment_audio_directory
    if Dir == '':
        lara_utils.print_and_flush(f'*** Error: segment_audio_directory not defined')
        return
    TrimmedDir = f'{Dir}_trimmed'
    ( dBthreshold, IgnoreAtEnd ) = ( Params.trimming_db_threshold, Params.trimming_start_offset )
    lara_utils.create_directory_if_it_doesnt_exist(TrimmedDir)
    Metadata = lara_audio.read_ldt_metadata_file(Dir)
    if Metadata == False:
        lara_utils.print_and_flush(f'*** Error: no usable metadata file found in {Dir}')
        return
    lara_audio.write_ldt_metadata_file(Metadata, TrimmedDir)
    ( NConverted, NSkipped, NFailed ) = ( 0, 0, 0 )
    for Item in Metadata:
        BaseFile = Item['file']
        ( InFile, OutFile ) = ( f'{Dir}/{BaseFile}', f'{TrimmedDir}/{BaseFile}' )
        if not lara_utils.file_exists(InFile):
            lara_utils.print_and_flush(f'*** Warning: file listed in metadata not found {InFile}')
            NFailed += 1
        elif lara_utils.file_exists(OutFile):
            lara_utils.print_and_flush(f'--- Skipping {InFile}, apparently already processed')
            NSkipped += 1
        else:
            Result = trim_mp3(InFile, dBthreshold, IgnoreAtEnd, OutFile, Params)
            if Result:
                NConverted += 1
            else:
                NFailed += 1
    lara_utils.print_and_flush(f'--- Processed files in {Dir}, output in {TrimmedDir}.')
    lara_utils.print_and_flush(f'    {NConverted} converted, {NSkipped} skipped, {NFailed} failed')

# Recipe from https://superuser.com/questions/1362176/how-to-trim-silence-only-from-beginning-and-end-of-mp3-files-using-ffmpeg
# ffmpeg -i in.aac -af silenceremove=start_periods=1:start_silence=0.1:start_threshold=-50dB,
# areverse,silenceremove=start_periods=1:start_silence=0.1:start_threshold=-50dB,areverse out.aac

def trim_mp3(InFile, dBthreshold, IgnoreAtEnd, OutFile, Params):
    ( AbsInFile, AbsOutFile ) = ( lara_utils.absolute_file_name(InFile), lara_utils.absolute_file_name(OutFile) )
    TmpFile = lara_utils.get_tmp_trace_file(Params)
    TrimStartParams = f'silenceremove=start_periods=1:start_silence={IgnoreAtEnd}:start_threshold=-{dBthreshold}dB'
    TrimEndParams = f'areverse,silenceremove=start_periods=1:start_silence={IgnoreAtEnd}:start_threshold=-{dBthreshold}dB,areverse'
    #Command = f'ffmpeg -i "{AbsInFile}" -af "{TrimStartParams},{TrimEndParams}" "{AbsOutFile}"'
    Command = f'ffmpeg -i "{AbsInFile}" -af "{TrimStartParams}" "{AbsOutFile}"'
    Result = execute_ffmpeg_command(Command, TmpFile, Params)
    if Result == False:
        lara_utils.print_and_flush(f'*** Error: command failed: "{Command}"')
        return False
    return True
                                  
