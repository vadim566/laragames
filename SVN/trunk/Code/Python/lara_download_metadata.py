
import lara_install_audio_zipfile
import lara_utils 

import os.path
from pathlib import Path
import json
import time

##This is the top-level function. Collect all metadata for a given reading progress and put it in TmpDir
##Finally, it creates a file called metametadata.json which lists all the metadata
##
##LaraResourcesFile is the JSON file associates corpus and language IDs with URLs
##                  e.g. $LARA/Content/all_resources.json
##ReadingHistory is a list of reading history items of the form [ CorpusId, LanguageId, [From, To] ]
##
##Params is a set of config file values

def download_metadata(LaraResourcesFile, ReadingHistory, Params):
    StartTime = time.time()
    AllResources = get_all_lara_resources(LaraResourcesFile)
    MetadataRequests = get_metadata_requests(ReadingHistory, AllResources)
    Requests = lara_utils.concatenate_lists([ download_metadata_item(Request, Params) for Request in MetadataRequests ])
    create_metametadata_file(Requests, Params.metadata_directory)
    if StartTime is not None: 
        lara_utils.print_and_flush_with_elapsed_time('--- Downloaded data from web', StartTime)

##Typical audio metadata
##[
##    "cathyc"
##]
##
##Typical voice metadata
##{
##    "french": "english_french.csv",
##    "french_reader1": "english_french_reader1.csv",
##    "russian": "english_russian.csv"
##}

def get_voices_and_l1s_for_resource_file(LaraResourcesFile):
    AllResources = get_all_lara_resources(LaraResourcesFile)
    if not isinstance(AllResources, dict):
        return False
    return { ResourceId: get_voices_and_l1s_for_resource(ResourceId, LaraResourcesFile) for ResourceId in AllResources }

def get_voices_and_l1s_for_resource(ResourceId, LaraResourcesFile):
    AllResources = get_all_lara_resources(LaraResourcesFile)
    if not ResourceId in AllResources:
        lara_utils.print_and_flush(f'*** Error: {ResourceId} not defined in {LaraResourcesFile}')
        ( Voices, L1s ) = ( [], [] )
    else:
        URL = AllResources[ResourceId][0]
        VoiceMetadata = lara_utils.read_json_from_url(f'{URL}/audio/metadata.json')
        TranslationMetadata = lara_utils.read_json_from_url(f'{URL}/translations/metadata.json')
        Voices = VoiceMetadata if VoiceMetadata else []
        if TranslationMetadata and isinstance(TranslationMetadata, dict):
            L1s = lara_utils.remove_duplicates([ Key.split('_')[0] for Key in TranslationMetadata ])
        else:
            L1s = []
    return { 'voices': Voices, 'l1s': L1s }

def get_all_lara_resources(LaraResourcesFile):
    return lara_utils.read_json_file(LaraResourcesFile)

def get_metadata_requests(ReadingHistory, AllResources): 
    CorpusRequests = [ ( 'corpus', Resource, Type, AllResources[Resource][0] )
                       for ( Resource, L2Id, Range ) in ReadingHistory
                       if Resource in AllResources
                       for Type in [ 'config', 'corpus', 'notes', 'css', 'script', 'audio', 'images', 'translation' ] ]
    LanguageRequests = [ ( 'language', L2Id, Type, AllResources[L2Id][0] )
                         for ( Resource, L2Id, Range ) in ReadingHistory
                         if L2Id in AllResources
                         for Type in [ 'audio', 'translation' ] ]
    return lara_utils.remove_duplicates( CorpusRequests + LanguageRequests )
                    
##def download_metadata_item(Request, Params):
##    ( RequestType, ResourceOrL2, MetadataType, URL ) = Request
##    ( TmpDir, Recompile ) = ( Params.metadata_directory, Params.recompile )
##    if MetadataType == 'config':
##        ( URL1, File ) = download_config(URL, ResourceOrL2, TmpDir, Recompile)
##    elif MetadataType == 'corpus':
##        ( URL1, File ) = download_corpus(URL, ResourceOrL2, TmpDir, Recompile)
##    elif MetadataType == 'audio':
##        ( URL1, File ) = download_audio_metadata(URL, ResourceOrL2, Params, TmpDir, Recompile)
##    elif RequestType == 'corpus' and MetadataType == 'images':
##        ( URL1, File ) = download_corpus_images_metadata(URL, ResourceOrL2, Params, TmpDir, Recompile)
##    elif MetadataType == 'translation':
##        ( URL1, File ) = download_translation_metadata(URL, ResourceOrL2, Params, TmpDir, Recompile)
##    else:
##        ( URL1, File ) = ( False, False )
##    if ( URL1 == False or File == False ):
##        ( URL2, File1 ) = ( '*no_url*', '*no_file*' )
##    else:
##        ( URL2, File1 ) = ( URL1, File )
##    return [ RequestType, ResourceOrL2, MetadataType, URL2, File1  ]

def download_metadata_item(Request, Params):
    ( RequestType, ResourceOrL2, MetadataType, URL ) = Request
    ( TmpDir, Recompile ) = ( Params.metadata_directory, Params.recompile )
    ResourceOrL2Etc = ( RequestType, ResourceOrL2, MetadataType )
    if MetadataType == 'config':
        return download_config(URL, ResourceOrL2Etc, TmpDir, Recompile, Params)
    elif MetadataType == 'corpus':
        return download_corpus(URL, ResourceOrL2Etc, TmpDir, Recompile, Params)
    elif MetadataType == 'notes':
        return download_notes(URL, ResourceOrL2Etc, TmpDir, Recompile, Params)
    elif MetadataType == 'css':
        return download_css(URL, ResourceOrL2Etc, TmpDir, Recompile, Params)
    elif MetadataType == 'script':
        return download_script(URL, ResourceOrL2Etc, TmpDir, Recompile, Params)
    elif MetadataType == 'audio':
        return download_audio_metadata(URL, ResourceOrL2Etc, Params, TmpDir, Recompile)
    elif RequestType == 'corpus' and MetadataType == 'images':
        return download_corpus_images_metadata(URL, ResourceOrL2Etc, Params, TmpDir, Recompile)
    elif MetadataType == 'translation':
        return download_translation_metadata(URL, ResourceOrL2Etc, Params, TmpDir, Recompile)
    else:
        return []

def download_config(URL, ResourceOrL2Etc, TmpDir, Recompile, Params):
    ( RequestType, ResourceOrL2, MetadataType ) = ResourceOrL2Etc 
    CorpusMetadataURL = URL + '/corpus/metadata.json'
    CorpusMetadataTargetFile = f'{TmpDir}/{ResourceOrL2}_corpus_metadata.json'
    CorpusMetadata = read_json_from_url_or_reuse_cached(CorpusMetadataURL, CorpusMetadataTargetFile, Recompile)
    if CorpusMetadata and 'config' in CorpusMetadata:
        ConfigFileName = CorpusMetadata['config']
        ConfigFileURL = f'{URL}/corpus/{ConfigFileName}'
        TargetFile = f'{TmpDir}/{ResourceOrL2}_{ConfigFileName}'
        ConfigFile = read_file_from_url_or_reuse_cached(ConfigFileURL, TargetFile, Recompile)
        return [ ( RequestType, ResourceOrL2, MetadataType, ConfigFileURL, ConfigFile ) ]
    else:
        lara_utils.print_and_flush('*** Warning: unable to find config file metadata at {URL}.'.format(URL=CorpusMetadataURL))
        return []

def download_corpus(URL, ResourceOrL2Etc, TmpDir, Recompile, Params):
    ( RequestType, ResourceOrL2, MetadataType ) = ResourceOrL2Etc 
    CorpusMetadataURL = URL + '/corpus/metadata.json'
    CorpusMetadataTargetFile = f'{TmpDir}/{ResourceOrL2}_corpus_metadata.json'
    CorpusMetadata = read_json_from_url_or_reuse_cached(CorpusMetadataURL, CorpusMetadataTargetFile, Recompile)
    if CorpusMetadata and 'corpus' in CorpusMetadata:
        CorpusFileName = CorpusMetadata['corpus']
        CorpusFileURL = f'{URL}/corpus/{CorpusFileName}'
        TargetFile = f'{TmpDir}/{ResourceOrL2}_{CorpusFileName}'
        CorpusFile = read_file_from_url_or_reuse_cached(CorpusFileURL, TargetFile, Recompile)
        return [ ( RequestType, ResourceOrL2, MetadataType, CorpusFileURL, CorpusFile ) ]
    else:
        lara_utils.print_and_flush(f'*** Warning: unable to find corpus metadata at {CorpusMetadataURL}.')
        return []

def download_notes(URL, ResourceOrL2Etc, TmpDir, Recompile, Params):
    ( RequestType, ResourceOrL2, MetadataType ) = ResourceOrL2Etc 
    CorpusMetadataURL = URL + '/corpus/metadata.json'
    CorpusMetadataTargetFile = f'{TmpDir}/{ResourceOrL2}_corpus_metadata.json'
    CorpusMetadata = read_json_from_url_or_reuse_cached(CorpusMetadataURL, CorpusMetadataTargetFile, Recompile)
    if not CorpusMetadata or not 'notes' in CorpusMetadata:
        return []
    Results = []
    for NotesFileName in CorpusMetadata['notes']:
        NotesFileURL = f'{URL}/corpus/{NotesFileName}'
        TargetFile = downloaded_notes_file_name(Params, ResourceOrL2, NotesFileName)
        ConfigFile = read_file_from_url_or_reuse_cached(NotesFileURL, TargetFile, Recompile)
        # We need the language since we store notes by language - though maybe we shouldn't.
        Results += [ ( RequestType, ResourceOrL2, ( MetadataType, Params.language ), NotesFileURL, TargetFile ) ]
    return Results

def download_css(URL, ResourceOrL2Etc, TmpDir, Recompile, Params):
    ( RequestType, ResourceOrL2, MetadataType ) = ResourceOrL2Etc 
    CorpusMetadataURL = URL + '/corpus/metadata.json'
    CorpusMetadataTargetFile = f'{TmpDir}/{ResourceOrL2}_corpus_metadata.json'
    CorpusMetadata = read_json_from_url_or_reuse_cached(CorpusMetadataURL, CorpusMetadataTargetFile, Recompile)
    if not CorpusMetadata or not 'css' in CorpusMetadata:
        return []
    Results = []
    for CSSFileName in CorpusMetadata['css']:
        CSSFileURL = f'{URL}/corpus/{CSSFileName}'
        TargetFile = downloaded_css_file_name(Params, ResourceOrL2, CSSFileName)
        ConfigFile = read_file_from_url_or_reuse_cached(CSSFileURL, TargetFile, Recompile)
        Results += [ ( RequestType, ResourceOrL2, MetadataType, CSSFileURL, TargetFile ) ]
    return Results

def download_script(URL, ResourceOrL2Etc, TmpDir, Recompile, Params):
    ( RequestType, ResourceOrL2, MetadataType ) = ResourceOrL2Etc 
    CorpusMetadataURL = URL + '/corpus/metadata.json'
    CorpusMetadataTargetFile = f'{TmpDir}/{ResourceOrL2}_corpus_metadata.json'
    CorpusMetadata = read_json_from_url_or_reuse_cached(CorpusMetadataURL, CorpusMetadataTargetFile, Recompile)
    if not CorpusMetadata or not 'js' in CorpusMetadata:
        return []
    Results = []
    for ScriptFileName in CorpusMetadata['js']:
        ScriptFileURL = f'{URL}/corpus/{ScriptFileName}'
        TargetFile = downloaded_script_file_name(Params, ResourceOrL2, ScriptFileName)
        ConfigFile = read_file_from_url_or_reuse_cached(ScriptFileURL, TargetFile, Recompile)
        Results += [ ( RequestType, ResourceOrL2, MetadataType, ScriptFileURL, TargetFile ) ]
    return Results

# We will need these three functions to find the notes, CSS and script file (in lara.py for the last two)
def downloaded_notes_file_name(Params, ResourceOrL2, NotesFileName):
    TmpDir = Params.metadata_directory
    if TmpDir and not TmpDir == '':
        return f'{TmpDir}/{ResourceOrL2}_{NotesFileName}'
    else:
        return False

def downloaded_css_file_name(Params, ResourceOrL2, CSSFileName):
    TmpDir = Params.metadata_directory
    if TmpDir and not TmpDir == '':
        return f'{TmpDir}/{ResourceOrL2}_{CSSFileName}'
    else:
        return False

def downloaded_script_file_name(Params, ResourceOrL2, ScriptFileName):
    TmpDir = Params.metadata_directory
    if TmpDir and not TmpDir == '':
        return f'{TmpDir}/{ResourceOrL2}_{ScriptFileName}'
    else:
        return False

def download_audio_metadata(URL, ResourceOrL2Etc, Params, TmpDir, Recompile):
    ( RequestType, ResourceOrL2, MetadataType ) = ResourceOrL2Etc 
    MetadataURL = URL + '/audio/metadata.json'
    AudioMetadataTargetFile = f'{TmpDir}/{ResourceOrL2}_audio_metadata.json'
    AudioSpeakerMetadata = read_json_from_url_or_reuse_cached(MetadataURL, AudioMetadataTargetFile, Recompile)
    if not AudioSpeakerMetadata:
        lara_utils.print_and_flush(f'*** Warning: unable to find audio metadata at {MetadataURL}.')
        return []
    Results = []
    for Voice in AudioSpeakerMetadata:
        JSONResult = download_audio_metadata_for_voice_and_extension(URL, Voice, TmpDir, ResourceOrL2, Recompile, 'json')
        if JSONResult:
            AudioFile = JSONResult
        else:
            TxtResult = download_audio_metadata_for_voice_and_extension(URL, Voice, TmpDir, ResourceOrL2, Recompile, 'txt')
            AudioFile = TxtResult
        Results += [ ( RequestType, ResourceOrL2, ( MetadataType, Voice ), f'{URL}/audio/{Voice}', AudioFile ) ]
    return Results

def download_audio_metadata_for_voice_and_extension(URL, Voice, TmpDir, ResourceOrL2, Recompile, Extension):
    AudioMetadataURL = f'{URL}/audio/{Voice}/metadata_help.{Extension}'
    TargetFile = f'{TmpDir}/{ResourceOrL2}_{Voice}_audio_metadata.{Extension}'
    JSONTargetFile = lara_utils.change_extension(TargetFile, 'json')
    FileAlreadyExisted = lara_utils.file_exists(JSONTargetFile)
    AudioFile = read_file_from_url_or_reuse_cached(AudioMetadataURL, TargetFile, Recompile)
    # It's possible that the audio metadata contains redundant lines, so clean it up
    # Irrespective of whether the file was txt or JSON, this will produce a JSON file
    # Case 1: no file found, return False
    if AudioFile == False:
        return False
    # Case 2: file already found return JSON version of file
    elif ( Recompile and FileAlreadyExisted ):
        return JSONTargetFile
    # Case 3: clean up file, producing JSON file, and return it
    else:
        lara_install_audio_zipfile.clean_audio_metadata_file(TargetFile)
        return JSONTargetFile

def download_corpus_images_metadata(URL, ResourceOrL2Etc, Params, TmpDir, Recompile):
    ( RequestType, ResourceOrL2, MetadataType ) = ResourceOrL2Etc 
    ImageMetadataURL = f'{URL}/images/metadata.txt'
    TargetFile = f'{TmpDir}/{ResourceOrL2}_images_metadata.txt'
    ImagesFile = read_file_from_url_or_reuse_cached(ImageMetadataURL, TargetFile, Recompile)
    return [ ( RequestType, ResourceOrL2, MetadataType, f'{URL}/images', ImagesFile ) ]

def download_translation_metadata(URL, ResourceOrL2Etc, Params, TmpDir, Recompile):
    ( RequestType, ResourceOrL2, MetadataType ) = ResourceOrL2Etc 
    TranslationMetadataURL = URL + '/translations/metadata.json'
    TranslationMetadataTargetFile = f'{TmpDir}/{ResourceOrL2}_translation_metadata.json'
    TranslationMetadata0 = read_json_from_url_or_reuse_cached(TranslationMetadataURL, TranslationMetadataTargetFile, Recompile)
    if TranslationMetadata0 and type(TranslationMetadata0) == dict and len(TranslationMetadata0) > 0:
        Results = []
        TranslationMetadata = reformat_translation_metadata(TranslationMetadata0)
        for Key in TranslationMetadata:
            ( L1, UserId, LemmaOrSurface ) = Key
            TranslationFileURL = f'{URL}/translations/{TranslationMetadata[Key]}'
            TargetFile = f'{TmpDir}/{ResourceOrL2}_{L1}_{UserId}_{LemmaOrSurface}_translations.csv'
            TranslationFile = read_file_from_url_or_reuse_cached(TranslationFileURL, TargetFile, Recompile)
            Metadata = ( MetadataType, L1, UserId, LemmaOrSurface )
            Results += [ ( RequestType, ResourceOrL2, Metadata, f'{URL}/translations', TranslationFile ) ]
        return Results
    else:
        lara_utils.print_and_flush(f'*** Warning: unable to find translation metadata at {TranslationMetadataURL}.')
        return []

def reformat_translation_metadata(TranslationMetadata):
    return { reformat_translation_metadata_key(Key): TranslationMetadata[Key] for Key in TranslationMetadata }

# Possible types of key:
# 'french'
# 'type_french'
# 'token_french'
# 'french_translator1'
# 'type_french_translator1'
# 'token_french_translator1' 
def reformat_translation_metadata_key(Key):
    Components = Key.split('_')
    if len(Components) == 1:
        L1 = Key
        return ( L1, 'public', 'lemma' )
    elif len(Components) == 2 and Components[0] == 'type':
        ( Surface, L1 ) = Components
        return ( L1, 'public', 'surface_word_type' )
    elif len(Components) == 2 and Components[0] == 'token':
        ( Surface, L1 ) = Components
        return ( L1, 'public', 'surface_word_token' )
    elif len(Components) == 2: 
        ( L1, UserId ) = Components
        return ( L1, UserId, 'lemma' )
    elif len(Components) == 3 and Components[0] == 'type':
        ( Surface, L1, UserId ) = Components
        return ( L1, UserId, 'surface_word_type' )
    elif len(Components) == 3 and Components[0] == 'token':
        ( Surface, L1, UserId ) = Components
        return ( L1, UserId, 'surface_word_token' )
    else:
        lara_utils.print_and_flush(f'*** Error: bad key {Key} in translation metadata')
        return False

def read_json_from_url_or_reuse_cached(URL, CacheFile, Recompile):
    return lara_utils.read_json_file(CacheFile) if read_file_from_url_or_reuse_cached(URL, CacheFile, Recompile) else False

def read_file_from_url_or_reuse_cached(URL, TargetFile, Recompile):
    if Recompile and lara_utils.file_exists(TargetFile):
        if file_shows_recent_attempt_retrieve_from_url_failed(TargetFile):
            AttemptNSecondsAgo = int(lara_utils.file_age_in_seconds(TargetFile))
            lara_utils.print_and_flush(f'--- Failed attempt {AttemptNSecondsAgo} seconds ago to retrieve file from {URL}, not retrying yet')
            return False
        elif file_shows_failed_retrieval_attempt(TargetFile):
            return read_file_from_url_and_maybe_mark_as_failed(URL, TargetFile)
        else:
            return TargetFile
    else:
        return read_file_from_url_and_maybe_mark_as_failed(URL, TargetFile)

def read_file_from_url_and_maybe_mark_as_failed(URL, TargetFile):
    try:
        Result = lara_utils.read_file_from_url(URL, TargetFile)
        if Result == False:
            make_file_show_recent_attempt_retrieve_from_url_failed(URL, TargetFile)
        return Result
    except:
        return False

# If we fail to get a file from a URL, wait at least 3600 seconds before retrying
_url_retry_pause = 3600
_url_retrieval_failed_message = 'Retrieval from URL failed'

def make_file_show_recent_attempt_retrieve_from_url_failed(URL, TargetFile):
    lara_utils.write_lara_text_file(_url_retrieval_failed_message, TargetFile)
    lara_utils.print_and_flush(f'--- Unable to retrieve file from {URL}, will not try again for {_url_retry_pause} seconds')

def file_shows_recent_attempt_retrieve_from_url_failed(TargetFile):
    try:
        return lara_utils.file_age_in_seconds(TargetFile) < _url_retry_pause and \
               lara_utils.file_size_in_bytes(TargetFile) < 100 and \
               lara_utils.read_lara_text_file(TargetFile) == _url_retrieval_failed_message
    except:
        return False

def file_shows_failed_retrieval_attempt(TargetFile):
    try:
        return lara_utils.file_size_in_bytes(TargetFile) < 100 and \
               lara_utils.read_lara_text_file(TargetFile) == _url_retrieval_failed_message
    except:
        return False
    
def create_metametadata_file(Requests, TmpDir):
    MetaMetaDataFile = TmpDir + '/metametadata.json'
    lara_utils.write_json_to_file(Requests, MetaMetaDataFile)

    
