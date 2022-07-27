
import lara_images
import lara_split_and_clean
import lara_audio
import lara_translations
import lara_config
import lara_utils
import lara_parse_utils
import time

def store_downloaded_metadata(MetaMetaData):
    lara_images.init_stored_downloaded_image_metadata()
    lara_audio.init_stored_downloaded_audio_metadata()
    lara_translations.init_stored_downloaded_translations_metadata()
    store_downloaded_metadata1(MetaMetaData)

def store_downloaded_metadata1(MetaMetaData):
    I = 0
    for MetaMetaDataItem in MetaMetaData:
        if store_downloaded_metadata_item(MetaMetaDataItem):
            I += 1
    lara_utils.print_and_flush(f'--- Stored content for {I} metadata files')

def store_downloaded_metadata_item(MetaMetaDataItem):
    ( CorpusOrLanguage, CorpusId, Type, URL, File ) = MetaMetaDataItem
    if not File or not URL or File == '*no_file*':
        return False
    elif CorpusOrLanguage == 'corpus' and Type == 'config':
        return False
    elif CorpusOrLanguage == 'corpus' and Type == 'corpus':
        return False
    elif CorpusOrLanguage == 'corpus' and Type == 'images':
        lara_images.store_downloaded_image_metadata(CorpusId, URL, File)
        return True
    elif CorpusOrLanguage == 'corpus' and isinstance(Type, list) and Type[0] == 'audio':
        Voice = Type[1]
        lara_audio.store_downloaded_audio_metadata('segments', Voice, CorpusId, URL, File)
        return True
    elif CorpusOrLanguage == 'language' and isinstance(Type, list) and Type[0] == 'audio':
        Voice = Type[1]
        lara_audio.store_downloaded_audio_metadata('words', Voice, CorpusId, URL, File)
        return True
    elif CorpusOrLanguage == 'corpus' and isinstance(Type, list) and Type[0] == 'translation':
        ( MetadataType, L1, UserId, LemmaOrSurface ) = Type
        if LemmaOrSurface == 'surface_word_token':
            lara_translations.store_downloaded_word_token_translations(CorpusId, File)
        else:
            lara_translations.store_downloaded_segment_translations(CorpusId, File)
        return True
    elif CorpusOrLanguage == 'language' and isinstance(Type, list) and Type[0] == 'translation':
        ( MetadataType, L1, UserId, LemmaOrSurface ) = Type
        lara_translations.store_downloaded_word_translations(L1, UserId, LemmaOrSurface, File)
        return True
    elif CorpusOrLanguage == 'corpus' and isinstance(Type, list) and len(Type) == 2 and Type[0] == 'notes':
        # We store notes by language - though maybe we shouldn't.
        Language = Type[1]
        lara_translations.store_downloaded_notes(Language, File)
        return True

# -----------------------------------------------

# [ "peter_rabbit", "english_geneva", [ 1, 26 ] ],
# [ "alice_in_wonderland", "english_geneva", [ 1, 49 ] ]

def make_split_corpus_from_downloaded_metadata(ReadingHistory, MetaMetaData, SplitFile, ConfigData):
    if not ConfigData:
        lara_utils.print_and_flush('*** Error: cannot internalise corpus since unable to read config file')
        return False
    StartTime = time.time()
    ( SplitCorpusContent, AudioTrackingData ) = make_split_corpus_from_downloaded_metadata1(ReadingHistory, MetaMetaData, ConfigData)
    lara_utils.print_and_flush('\n--------------------------------------~')
    lara_utils.print_and_flush('STATISTICS FOR COMBINED CORPUS')
    lara_split_and_clean.print_split_file_statistics(SplitCorpusContent)
    lara_utils.print_and_flush('\n--------------------------------------~')
    lara_utils.write_json_to_file(SplitCorpusContent, SplitFile)
    lara_utils.print_and_flush_with_elapsed_time(f'--- Written split corpus ({len(SplitCorpusContent)} segments) to {SplitFile}', StartTime)
    lara_audio.write_audio_tracking_data_to_tmp_resources(AudioTrackingData, ConfigData)
    return True
 
def make_split_corpus_from_downloaded_metadata1(ReadingHistory, MetaMetaData, ConfigData):
    ( OutList, AllAudioTrackingData ) = ( [], {} )
    for Item in ReadingHistory:
        ( NewSplitList, NewAudioTrackingData) = make_split_corpus_from_downloaded_metadata2(Item, MetaMetaData, ConfigData)
        if NewSplitList:
            OutList = OutList + NewSplitList
            AllAudioTrackingData = lara_utils.merge_dicts(AllAudioTrackingData, NewAudioTrackingData)
    lara_utils.print_and_flush(f'--- Read total of {len(OutList)} pages')
    return ( OutList, AllAudioTrackingData )

def make_split_corpus_from_downloaded_metadata2(ReadingHistoryItem, MetaMetaData, ConfigData):
    if not valid_reading_history_item(ReadingHistoryItem):
        lara_utils.print_and_flush(f'*** Error: bad item {str(ReadingHistoryItem)} in reading history')
        return ( False, False )
    StartTime = time.time()
    ( CorpusId, LanguageId, Range ) = ReadingHistoryItem
    CachedTaggedPageOrientedSplitList = get_cached_downloaded_split_corpus(CorpusId, ConfigData)
    CachedAudioTrackingData = get_cached_audio_tracking_data(CorpusId, ConfigData)
    #if CachedTaggedPageOrientedSplitList and CachedAudioTrackingData != {}:
    if CachedTaggedPageOrientedSplitList and CachedAudioTrackingData != False:
        TaggedPageOrientedSplitList = CachedTaggedPageOrientedSplitList
        AudioTrackingData = CachedAudioTrackingData
    else:
        ( ConfigFile, CorpusFile ) = ( False, False )
        for ( CorpusOrLanguage, OtherCorpusId, Type, URL, File ) in MetaMetaData:
            if ( CorpusOrLanguage, CorpusId, Type ) == ( 'corpus', OtherCorpusId, 'config' ):
                ConfigFile = File
            elif ( CorpusOrLanguage, CorpusId, Type ) == ( 'corpus', OtherCorpusId, 'corpus' ):
                CorpusFile = File
        if not ConfigFile:
            lara_utils.print_and_flush(f'*** Warning: no config file found for corpus ID {CorpusId}')
            return ( [], {} )
        if not CorpusFile:
            lara_utils.print_and_flush(f'*** Warning: no corpus file found for corpus ID {CorpusId}')
            return ( [], {} )
        Params = lara_config.read_lara_local_config_file_dont_check_directories(ConfigFile)
        # Use 'minimal' version since we probably aren't interested in getting trace feedback here
        ( PageOrientedSplitList, AudioTrackingData, Trace ) = lara_split_and_clean.clean_lara_file_main_minimal(CorpusFile, Params)
        lara_utils.print_and_flush(f'--- Read data for {len(PageOrientedSplitList)} pages from {CorpusFile}')
        Tag = { 'corpus': CorpusId,
                'language': LanguageId,
                'l1': get_l1(Params),
                'word_audio_voice': get_word_audio_voice(Params),
                'word_translations_on': Params.word_translations_on,
                'css_file': Params.css_file,
                'script_file': Params.script_file }
        TaggedPageOrientedSplitList = lara_split_and_clean.add_tags_to_chunks(PageOrientedSplitList, Tag)
        cache_downloaded_split_corpus(CorpusId, TaggedPageOrientedSplitList, ConfigData)
        cache_audio_tracking_data(CorpusId, AudioTrackingData, ConfigData)
    SelectedData = select_range_from_page_oriented_split_list(TaggedPageOrientedSplitList, Range)
    lara_utils.print_and_flush_with_elapsed_time(f'--- Extracted {len(SelectedData)} pages from {CorpusId}', StartTime)
    return ( SelectedData, AudioTrackingData )

# This assumes that the last component of the word_audio_directory will either be the name of the voice or 'audio' if there is none
def get_word_audio_voice(Params):
    if Params.word_audio_directory == '':
        return ''
    LastComponentInDir = Params.word_audio_directory.split('/')[-1]
    return LastComponentInDir if LastComponentInDir != 'audio' else ''

def get_l1(Params):
    if Params.l1 != '':
        return Params.l1
    if Params.translation_spreadsheet != '':
        return translations_spreadsheet_name_to_target_language(Params.translation_spreadsheet)
    if Params.translation_spreadsheet_surface != '':
        return translations_spreadsheet_name_to_target_language(Params.translation_spreadsheet_surface)
    lara_utils.print_and_flush(f'*** Warning: unable to extract L1 (target language) name from "{Params}"')
    return ''

# Try to extract the L1/target language name from the translation CSV pathname
# Assume it is of the form 'surface_L2_L1', 'type_L2_L1' or 'L2_L1'
def translations_spreadsheet_name_to_target_language(Pathname):
    ( BaseFile, Extension ) = lara_utils.file_to_base_file_and_extension(Pathname)
    Components = BaseFile.split('/')
    LastComponent = Components[-1]
    LangComponents = LastComponent.split('_')
    if LangComponents[0] in ( 'surface', 'type' ) and len(LangComponents) >= 3:
        return LangComponents[2]
    if len(LangComponents) >= 2:
        return LangComponents[1]
    lara_utils.print_and_flush(f'*** Warning: unable to extract L1 (target language) name from "{Pathname}"')
    return ''

def valid_reading_history_item(ReadingHistoryItem):
    return lara_utils.is_n_item_list(ReadingHistoryItem, 3) and \
           ReadingHistoryItem[2] == 'all' or lara_utils.is_n_item_list(ReadingHistoryItem[2], 2)

def select_range_from_page_oriented_split_list(List, Range):
    if Range == 'all':
        return List
    elif lara_utils.is_n_item_list(Range, 2) and type(Range[0]) == int and type(Range[1]) == int:
        return List[Range[0]-1:Range[1]]
    else:
        lara_utils.print_and_flush(f'*** Warning: bad range {Range} in reading history')
        return []

def cache_downloaded_split_corpus(CorpusId, TaggedPageOrientedSplitList, ConfigData):
    CacheFile = cache_file_for_downloaded_split_corpus(CorpusId, ConfigData)
    if CacheFile:
        lara_utils.save_data_to_pickled_gzipped_file(TaggedPageOrientedSplitList, CacheFile)

def cache_audio_tracking_data(CorpusId, AudioTrackingData, ConfigData):
    CacheFile = cache_file_for_audio_tracking_data(CorpusId, ConfigData)
    if CacheFile:
        lara_utils.save_data_to_pickled_gzipped_file(AudioTrackingData, CacheFile)

def get_cached_downloaded_split_corpus(CorpusId, ConfigData):
    CacheFile = cache_file_for_downloaded_split_corpus(CorpusId, ConfigData)
    if ConfigData.recompile != '' and CacheFile and lara_utils.file_exists(CacheFile):
        #lara_utils.print_and_flush(f'--- Read cached split corpus file {CacheFile}')
        return lara_utils.get_data_from_pickled_gzipped_file(CacheFile)
    elif ConfigData.recompile != '' and CacheFile:
        #lara_utils.print_and_flush(f'--- Unable to find cached split corpus file {CacheFile}')
        return False
    else:
        return False

def get_cached_audio_tracking_data(CorpusId, ConfigData):
    CacheFile = cache_file_for_audio_tracking_data(CorpusId, ConfigData)
    if ConfigData.recompile != '' and CacheFile and lara_utils.file_exists(CacheFile):
        #lara_utils.print_and_flush(f'--- Read cached audio tracking file {CacheFile}')
        return lara_utils.get_data_from_pickled_gzipped_file(CacheFile)
    elif ConfigData.recompile != '' and CacheFile:
        #lara_utils.print_and_flush(f'--- Unable to find cached audio tracking file {CacheFile}')
        return False
    else:
        return False

def cache_file_for_downloaded_split_corpus(CorpusId, ConfigData):
    #( TmpDir, Recompile ) = ( ConfigData.metadata_directory, ConfigData.recompile )
    #return f'{TmpDir}/{CorpusId}_cached.data.gz' if TmpDir and Recompile else False
    ( TmpDir, ForReadingPortal ) = ( ConfigData.metadata_directory, ConfigData.for_reading_portal )
    return f'{TmpDir}/{CorpusId}_cached.data.gz' if TmpDir and ForReadingPortal == 'yes' else False

def cache_file_for_audio_tracking_data(CorpusId, ConfigData):
    ( TmpDir, ForReadingPortal ) = ( ConfigData.metadata_directory, ConfigData.for_reading_portal )
    return f'{TmpDir}/{CorpusId}_audio_tracking_cached.data.gz' if TmpDir and ForReadingPortal == 'yes' else False
   


    
