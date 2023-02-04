import lara_align_from_audio
import lara_utils

def test(Id):
    if Id == 'candide_all_chs':
        for I in range(1, 31):
            lara_utils.print_and_flush(f'---------------------------------')
            lara_utils.print_and_flush(f'CHAPTER {I}')
            test(f'candide_ch{I}')
    elif Id == 'candide_ch1':
        AudioId = 'ch1'
        AudioFile = '$LARA/Content/candide/audio/litteratureaudio_src/Voltaire_-_Candide_Chap01.mp3'
        AudioLabelsFile = '$LARA/Content/candide/corpus/LabelTrack_ch1.txt'
        SourceTextFile = '$LARA/Content/candide/corpus/candide_segmented_for_audio.txt'
        TargetTextFile = False
        ConfigFile = '$LARA/Content/candide/corpus/local_config_segmented_by_audio.json'
        StartLabel = 1
        EndLabel = 31
        lara_align_from_audio.create_aligned_files(AudioFile, AudioId, AudioLabelsFile, SourceTextFile, TargetTextFile, ConfigFile, StartLabel, EndLabel)
    elif Id == 'candide_ch2':
        AudioId = 'ch2'
        AudioFile = '$LARA/Content/candide/audio/litteratureaudio_src/Voltaire_-_Candide_Chap02.mp3'
        AudioLabelsFile = '$LARA/Content/candide/corpus/LabelTrack_ch2.txt'
        SourceTextFile = '$LARA/Content/candide/corpus/candide_segmented_for_audio.txt'
        TargetTextFile = False
        ConfigFile = '$LARA/Content/candide/corpus/local_config_segmented_by_audio.json'
        StartLabel = 32
        EndLabel = 84
        lara_align_from_audio.create_aligned_files(AudioFile, AudioId, AudioLabelsFile, SourceTextFile, TargetTextFile, ConfigFile, StartLabel, EndLabel)
    elif Id == 'candide_ch3':
        AudioId = 'ch3'
        AudioFile = '$LARA/Content/candide/audio/litteratureaudio_src/Voltaire_-_Candide_Chap03.mp3'
        AudioLabelsFile = '$LARA/Content/candide/corpus/LabelTrack_ch3.txt'
        SourceTextFile = '$LARA/Content/candide/corpus/candide_segmented_for_audio.txt'
        TargetTextFile = False
        ConfigFile = '$LARA/Content/candide/corpus/local_config_segmented_by_audio.json'
        StartLabel = 85
        EndLabel = 124
        lara_align_from_audio.create_aligned_files(AudioFile, AudioId, AudioLabelsFile, SourceTextFile, TargetTextFile, ConfigFile, StartLabel, EndLabel)
    elif Id == 'candide_ch4':
        AudioId = 'ch4'
        AudioFile = '$LARA/Content/candide/audio/litteratureaudio_src/Voltaire_-_Candide_Chap04.mp3'
        AudioLabelsFile = '$LARA/Content/candide/corpus/LabelTrack_ch4.txt'
        SourceTextFile = '$LARA/Content/candide/corpus/candide_segmented_for_audio.txt'
        TargetTextFile = False
        ConfigFile = '$LARA/Content/candide/corpus/local_config_segmented_by_audio.json'
        StartLabel = 125
        EndLabel = 201
        lara_align_from_audio.create_aligned_files(AudioFile, AudioId, AudioLabelsFile, SourceTextFile, TargetTextFile, ConfigFile, StartLabel, EndLabel)
    elif Id == 'candide_ch5':
        AudioId = 'ch5'
        AudioFile = '$LARA/Content/candide/audio/litteratureaudio_src/Voltaire_-_Candide_Chap05.mp3'
        AudioLabelsFile = '$LARA/Content/candide/corpus/LabelTrack_ch5.txt'
        SourceTextFile = '$LARA/Content/candide/corpus/candide_segmented_for_audio.txt'
        TargetTextFile = False
        ConfigFile = '$LARA/Content/candide/corpus/local_config_segmented_by_audio.json'
        StartLabel = 202
        EndLabel = 264
        lara_align_from_audio.create_aligned_files(AudioFile, AudioId, AudioLabelsFile, SourceTextFile, TargetTextFile, ConfigFile, StartLabel, EndLabel)
    elif Id == 'candide_ch6':
        AudioId = 'ch6'
        AudioFile = '$LARA/Content/candide/audio/litteratureaudio_src/Voltaire_-_Candide_Chap06.mp3'
        AudioLabelsFile = '$LARA/Content/candide/corpus/LabelTrack_ch6.txt'
        SourceTextFile = '$LARA/Content/candide/corpus/candide_segmented_for_audio.txt'
        TargetTextFile = False
        ConfigFile = '$LARA/Content/candide/corpus/local_config_segmented_by_audio.json'
        StartLabel = 265
        EndLabel = 282
        lara_align_from_audio.create_aligned_files(AudioFile, AudioId, AudioLabelsFile, SourceTextFile, TargetTextFile, ConfigFile, StartLabel, EndLabel)
    elif Id == 'candide_ch7':
        AudioId = 'ch7'
        AudioFile = '$LARA/Content/candide/audio/litteratureaudio_src/Voltaire_-_Candide_Chap07.mp3'
        AudioLabelsFile = '$LARA/Content/candide/corpus/LabelTrack_ch7.txt'
        SourceTextFile = '$LARA/Content/candide/corpus/candide_segmented_for_audio.txt'
        TargetTextFile = False
        ConfigFile = '$LARA/Content/candide/corpus/local_config_segmented_by_audio.json'
        StartLabel = 283
        EndLabel = 340
        lara_align_from_audio.create_aligned_files(AudioFile, AudioId, AudioLabelsFile, SourceTextFile, TargetTextFile, ConfigFile, StartLabel, EndLabel)
    elif Id == 'candide_ch8':
        AudioId = 'ch8'
        AudioFile = '$LARA/Content/candide/audio/litteratureaudio_src/Voltaire_-_Candide_Chap08.mp3'
        AudioLabelsFile = '$LARA/Content/candide/corpus/LabelTrack_ch8.txt'
        SourceTextFile = '$LARA/Content/candide/corpus/candide_segmented_for_audio.txt'
        TargetTextFile = False
        ConfigFile = '$LARA/Content/candide/corpus/local_config_segmented_by_audio.json'
        StartLabel = 341
        EndLabel = 391
        lara_align_from_audio.create_aligned_files(AudioFile, AudioId, AudioLabelsFile, SourceTextFile, TargetTextFile, ConfigFile, StartLabel, EndLabel)
    elif Id == 'candide_ch9':
        AudioId = 'ch9'
        AudioFile = '$LARA/Content/candide/audio/litteratureaudio_src/Voltaire_-_Candide_Chap09.mp3'
        AudioLabelsFile = '$LARA/Content/candide/corpus/LabelTrack_ch9.txt'
        SourceTextFile = '$LARA/Content/candide/corpus/candide_segmented_for_audio.txt'
        TargetTextFile = False
        ConfigFile = '$LARA/Content/candide/corpus/local_config_segmented_by_audio.json'
        StartLabel = 392
        EndLabel = 430
        lara_align_from_audio.create_aligned_files(AudioFile, AudioId, AudioLabelsFile, SourceTextFile, TargetTextFile, ConfigFile, StartLabel, EndLabel)
    elif Id == 'candide_ch10':
        AudioId = 'ch10'
        AudioFile = '$LARA/Content/candide/audio/litteratureaudio_src/Voltaire_-_Candide_Chap10.mp3'
        AudioLabelsFile = '$LARA/Content/candide/corpus/LabelTrack_ch10.txt'
        SourceTextFile = '$LARA/Content/candide/corpus/candide_segmented_for_audio.txt'
        TargetTextFile = False
        ConfigFile = '$LARA/Content/candide/corpus/local_config_segmented_by_audio.json'
        StartLabel = 431
        EndLabel = 486
        lara_align_from_audio.create_aligned_files(AudioFile, AudioId, AudioLabelsFile, SourceTextFile, TargetTextFile, ConfigFile, StartLabel, EndLabel)
    elif Id == 'candide_ch11':
        AudioId = 'ch11'
        AudioFile = '$LARA/Content/candide/audio/litteratureaudio_src/Voltaire_-_Candide_Chap11.mp3'
        AudioLabelsFile = '$LARA/Content/candide/corpus/LabelTrack_ch11.txt'
        SourceTextFile = '$LARA/Content/candide/corpus/candide_segmented_for_audio.txt'
        TargetTextFile = False
        ConfigFile = '$LARA/Content/candide/corpus/local_config_segmented_by_audio.json'
        StartLabel = 487
        EndLabel = 547
        lara_align_from_audio.create_aligned_files(AudioFile, AudioId, AudioLabelsFile, SourceTextFile, TargetTextFile, ConfigFile, StartLabel, EndLabel)
    elif Id == 'candide_ch12':
        AudioId = 'ch12'
        AudioFile = '$LARA/Content/candide/audio/litteratureaudio_src/Voltaire_-_Candide_Chap12.mp3'
        AudioLabelsFile = '$LARA/Content/candide/corpus/LabelTrack_ch12.txt'
        SourceTextFile = '$LARA/Content/candide/corpus/candide_segmented_for_audio.txt'
        TargetTextFile = False
        ConfigFile = '$LARA/Content/candide/corpus/local_config_segmented_by_audio.json'
        StartLabel = 548
        EndLabel = 609
        lara_align_from_audio.create_aligned_files(AudioFile, AudioId, AudioLabelsFile, SourceTextFile, TargetTextFile, ConfigFile, StartLabel, EndLabel)
    elif Id == 'candide_ch13':
        AudioId = 'ch13'
        AudioFile = '$LARA/Content/candide/audio/litteratureaudio_src/Voltaire_-_Candide_Chap13.mp3'
        AudioLabelsFile = '$LARA/Content/candide/corpus/LabelTrack_ch13.txt'
        SourceTextFile = '$LARA/Content/candide/corpus/candide_segmented_for_audio.txt'
        TargetTextFile = False
        ConfigFile = '$LARA/Content/candide/corpus/local_config_segmented_by_audio.json'
        StartLabel = 610
        EndLabel = 656
        lara_align_from_audio.create_aligned_files(AudioFile, AudioId, AudioLabelsFile, SourceTextFile, TargetTextFile, ConfigFile, StartLabel, EndLabel)
    elif Id == 'candide_ch14':
        AudioId = 'ch14'
        AudioFile = '$LARA/Content/candide/audio/litteratureaudio_src/Voltaire_-_Candide_Chap14.mp3'
        AudioLabelsFile = '$LARA/Content/candide/corpus/LabelTrack_ch14.txt'
        SourceTextFile = '$LARA/Content/candide/corpus/candide_segmented_for_audio.txt'
        TargetTextFile = False
        ConfigFile = '$LARA/Content/candide/corpus/local_config_segmented_by_audio.json'
        StartLabel = 657
        EndLabel = 753
        lara_align_from_audio.create_aligned_files(AudioFile, AudioId, AudioLabelsFile, SourceTextFile, TargetTextFile, ConfigFile, StartLabel, EndLabel)
    elif Id == 'candide_ch15':
        AudioId = 'ch15'
        AudioFile = '$LARA/Content/candide/audio/litteratureaudio_src/Voltaire_-_Candide_Chap15.mp3'
        AudioLabelsFile = '$LARA/Content/candide/corpus/LabelTrack_ch15.txt'
        SourceTextFile = '$LARA/Content/candide/corpus/candide_segmented_for_audio.txt'
        TargetTextFile = False
        ConfigFile = '$LARA/Content/candide/corpus/local_config_segmented_by_audio.json'
        StartLabel = 754
        EndLabel = 800
        lara_align_from_audio.create_aligned_files(AudioFile, AudioId, AudioLabelsFile, SourceTextFile, TargetTextFile, ConfigFile, StartLabel, EndLabel)
    elif Id == 'candide_ch16':
        AudioId = 'ch16'
        AudioFile = '$LARA/Content/candide/audio/litteratureaudio_src/Voltaire_-_Candide_Chap16.mp3'
        AudioLabelsFile = '$LARA/Content/candide/corpus/LabelTrack_ch16.txt'
        SourceTextFile = '$LARA/Content/candide/corpus/candide_segmented_for_audio.txt'
        TargetTextFile = False
        ConfigFile = '$LARA/Content/candide/corpus/local_config_segmented_by_audio.json'
        StartLabel = 801
        EndLabel = 883
        lara_align_from_audio.create_aligned_files(AudioFile, AudioId, AudioLabelsFile, SourceTextFile, TargetTextFile, ConfigFile, StartLabel, EndLabel)
    elif Id == 'candide_ch17':
        AudioId = 'ch17'
        AudioFile = '$LARA/Content/candide/audio/litteratureaudio_src/Voltaire_-_Candide_Chap17.mp3'
        AudioLabelsFile = '$LARA/Content/candide/corpus/LabelTrack_ch17.txt'
        SourceTextFile = '$LARA/Content/candide/corpus/candide_segmented_for_audio.txt'
        TargetTextFile = False
        ConfigFile = '$LARA/Content/candide/corpus/local_config_segmented_by_audio.json'
        StartLabel = 884
        EndLabel = 961
        lara_align_from_audio.create_aligned_files(AudioFile, AudioId, AudioLabelsFile, SourceTextFile, TargetTextFile, ConfigFile, StartLabel, EndLabel)
    elif Id == 'candide_ch18':
        AudioId = 'ch18'
        AudioFile = '$LARA/Content/candide/audio/litteratureaudio_src/Voltaire_-_Candide_Chap18.mp3'
        AudioLabelsFile = '$LARA/Content/candide/corpus/LabelTrack_ch18.txt'
        SourceTextFile = '$LARA/Content/candide/corpus/candide_segmented_for_audio.txt'
        TargetTextFile = False
        ConfigFile = '$LARA/Content/candide/corpus/local_config_segmented_by_audio.json'
        StartLabel = 962
        EndLabel = 1062
        lara_align_from_audio.create_aligned_files(AudioFile, AudioId, AudioLabelsFile, SourceTextFile, TargetTextFile, ConfigFile, StartLabel, EndLabel)
    elif Id == 'candide_ch19':
        AudioId = 'ch19'
        AudioFile = '$LARA/Content/candide/audio/litteratureaudio_src/Voltaire_-_Candide_Chap19.mp3'
        AudioLabelsFile = '$LARA/Content/candide/corpus/LabelTrack_ch19.txt'
        SourceTextFile = '$LARA/Content/candide/corpus/candide_segmented_for_audio.txt'
        TargetTextFile = False
        ConfigFile = '$LARA/Content/candide/corpus/local_config_segmented_by_audio.json'
        StartLabel = 1063
        EndLabel = 1185
        lara_align_from_audio.create_aligned_files(AudioFile, AudioId, AudioLabelsFile, SourceTextFile, TargetTextFile, ConfigFile, StartLabel, EndLabel)
    elif Id == 'candide_ch20':
        AudioId = 'ch20'
        AudioFile = '$LARA/Content/candide/audio/litteratureaudio_src/Voltaire_-_Candide_Chap20.mp3'
        AudioLabelsFile = '$LARA/Content/candide/corpus/LabelTrack_ch20.txt'
        SourceTextFile = '$LARA/Content/candide/corpus/candide_segmented_for_audio.txt'
        TargetTextFile = False
        ConfigFile = '$LARA/Content/candide/corpus/local_config_segmented_by_audio.json'
        StartLabel = 1186
        EndLabel = 1250
        lara_align_from_audio.create_aligned_files(AudioFile, AudioId, AudioLabelsFile, SourceTextFile, TargetTextFile, ConfigFile, StartLabel, EndLabel)
    elif Id == 'candide_ch21':
        AudioId = 'ch21'
        AudioFile = '$LARA/Content/candide/audio/litteratureaudio_src/Voltaire_-_Candide_Chap21.mp3'
        AudioLabelsFile = '$LARA/Content/candide/corpus/LabelTrack_ch21.txt'
        SourceTextFile = '$LARA/Content/candide/corpus/candide_segmented_for_audio.txt'
        TargetTextFile = False
        ConfigFile = '$LARA/Content/candide/corpus/local_config_segmented_by_audio.json'
        StartLabel = 1251
        EndLabel = 1297
        lara_align_from_audio.create_aligned_files(AudioFile, AudioId, AudioLabelsFile, SourceTextFile, TargetTextFile, ConfigFile, StartLabel, EndLabel)
    elif Id == 'candide_ch22':
        AudioId = 'ch22'
        AudioFile = '$LARA/Content/candide/audio/litteratureaudio_src/Voltaire_-_Candide_Chap22.mp3'
        AudioLabelsFile = '$LARA/Content/candide/corpus/LabelTrack_ch22.txt'
        SourceTextFile = '$LARA/Content/candide/corpus/candide_segmented_for_audio.txt'
        TargetTextFile = False
        ConfigFile = '$LARA/Content/candide/corpus/local_config_segmented_by_audio.json'
        StartLabel = 1298
        EndLabel = 1539
        lara_align_from_audio.create_aligned_files(AudioFile, AudioId, AudioLabelsFile, SourceTextFile, TargetTextFile, ConfigFile, StartLabel, EndLabel)
    elif Id == 'candide_ch23':
        AudioId = 'ch23'
        AudioFile = '$LARA/Content/candide/audio/litteratureaudio_src/Voltaire_-_Candide_Chap23.mp3'
        AudioLabelsFile = '$LARA/Content/candide/corpus/LabelTrack_ch23.txt'
        SourceTextFile = '$LARA/Content/candide/corpus/candide_segmented_for_audio.txt'
        TargetTextFile = False
        ConfigFile = '$LARA/Content/candide/corpus/local_config_segmented_by_audio.json'
        StartLabel = 1540
        EndLabel = 1582
        lara_align_from_audio.create_aligned_files(AudioFile, AudioId, AudioLabelsFile, SourceTextFile, TargetTextFile, ConfigFile, StartLabel, EndLabel)
    elif Id == 'candide_ch24':
        AudioId = 'ch24'
        AudioFile = '$LARA/Content/candide/audio/litteratureaudio_src/Voltaire_-_Candide_Chap24.mp3'
        AudioLabelsFile = '$LARA/Content/candide/corpus/LabelTrack_ch24.txt'
        SourceTextFile = '$LARA/Content/candide/corpus/candide_segmented_for_audio.txt'
        TargetTextFile = False
        ConfigFile = '$LARA/Content/candide/corpus/local_config_segmented_by_audio.json'
        StartLabel = 1583
        EndLabel = 1703
        lara_align_from_audio.create_aligned_files(AudioFile, AudioId, AudioLabelsFile, SourceTextFile, TargetTextFile, ConfigFile, StartLabel, EndLabel)
    elif Id == 'candide_ch25':
        AudioId = 'ch25'
        AudioFile = '$LARA/Content/candide/audio/litteratureaudio_src/Voltaire_-_Candide_Chap25.mp3'
        AudioLabelsFile = '$LARA/Content/candide/corpus/LabelTrack_ch25.txt'
        SourceTextFile = '$LARA/Content/candide/corpus/candide_segmented_for_audio.txt'
        TargetTextFile = False
        ConfigFile = '$LARA/Content/candide/corpus/local_config_segmented_by_audio.json'
        StartLabel = 1704
        EndLabel = 1832
        lara_align_from_audio.create_aligned_files(AudioFile, AudioId, AudioLabelsFile, SourceTextFile, TargetTextFile, ConfigFile, StartLabel, EndLabel)
    elif Id == 'candide_ch26':
        AudioId = 'ch26'
        AudioFile = '$LARA/Content/candide/audio/litteratureaudio_src/Voltaire_-_Candide_Chap26.mp3'
        AudioLabelsFile = '$LARA/Content/candide/corpus/LabelTrack_ch26.txt'
        SourceTextFile = '$LARA/Content/candide/corpus/candide_segmented_for_audio.txt'
        TargetTextFile = False
        ConfigFile = '$LARA/Content/candide/corpus/local_config_segmented_by_audio.json'
        StartLabel = 1833
        EndLabel = 1901
        lara_align_from_audio.create_aligned_files(AudioFile, AudioId, AudioLabelsFile, SourceTextFile, TargetTextFile, ConfigFile, StartLabel, EndLabel)
    elif Id == 'candide_ch27':
        AudioId = 'ch27'
        AudioFile = '$LARA/Content/candide/audio/litteratureaudio_src/Voltaire_-_Candide_Chap27.mp3'
        AudioLabelsFile = '$LARA/Content/candide/corpus/LabelTrack_ch27.txt'
        SourceTextFile = '$LARA/Content/candide/corpus/candide_segmented_for_audio.txt'
        TargetTextFile = False
        ConfigFile = '$LARA/Content/candide/corpus/local_config_segmented_by_audio.json'
        StartLabel = 1902
        EndLabel = 2025
        lara_align_from_audio.create_aligned_files(AudioFile, AudioId, AudioLabelsFile, SourceTextFile, TargetTextFile, ConfigFile, StartLabel, EndLabel)
    elif Id == 'candide_ch28':
        AudioId = 'ch28'
        AudioFile = '$LARA/Content/candide/audio/litteratureaudio_src/Voltaire_-_Candide_Chap28.mp3'
        AudioLabelsFile = '$LARA/Content/candide/corpus/LabelTrack_ch28.txt'
        SourceTextFile = '$LARA/Content/candide/corpus/candide_segmented_for_audio.txt'
        TargetTextFile = False
        ConfigFile = '$LARA/Content/candide/corpus/local_config_segmented_by_audio.json'
        StartLabel = 2026
        EndLabel = 2072
        lara_align_from_audio.create_aligned_files(AudioFile, AudioId, AudioLabelsFile, SourceTextFile, TargetTextFile, ConfigFile, StartLabel, EndLabel)
    elif Id == 'candide_ch29':
        AudioId = 'ch29'
        AudioFile = '$LARA/Content/candide/audio/litteratureaudio_src/Voltaire_-_Candide_Chap29.mp3'
        AudioLabelsFile = '$LARA/Content/candide/corpus/LabelTrack_ch29.txt'
        SourceTextFile = '$LARA/Content/candide/corpus/candide_segmented_for_audio.txt'
        TargetTextFile = False
        ConfigFile = '$LARA/Content/candide/corpus/local_config_segmented_by_audio.json'
        StartLabel = 2073
        EndLabel = 2095
        lara_align_from_audio.create_aligned_files(AudioFile, AudioId, AudioLabelsFile, SourceTextFile, TargetTextFile, ConfigFile, StartLabel, EndLabel)
    elif Id == 'candide_ch30':
        AudioId = 'ch30'
        AudioFile = '$LARA/Content/candide/audio/litteratureaudio_src/Voltaire_-_Candide_Chap30.mp3'
        AudioLabelsFile = '$LARA/Content/candide/corpus/LabelTrack_ch30.txt'
        SourceTextFile = '$LARA/Content/candide/corpus/candide_segmented_for_audio.txt'
        TargetTextFile = False
        ConfigFile = '$LARA/Content/candide/corpus/local_config_segmented_by_audio.json'
        StartLabel = 2096
        EndLabel = 2193
        lara_align_from_audio.create_aligned_files(AudioFile, AudioId, AudioLabelsFile, SourceTextFile, TargetTextFile, ConfigFile, StartLabel, EndLabel)
        
