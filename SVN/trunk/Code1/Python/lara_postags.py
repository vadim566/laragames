
import lara_utils
from functools import lru_cache

PosTagsRepository = False
_EmptyPosTagsRepository = { "map" : dict(), "translation" : dict() } 

def translate_postag( Tag, Params ):
    _load_repository( Params )
    return _translate_postag1( Tag )

@lru_cache(maxsize=256, typed=False)
def _translate_postag1( Tag ):
    if 'use_unchanged' in PosTagsRepository and PosTagsRepository['use_unchanged'] == 'yes':
        return Tag # return unchanged if language is marked as 'use_unchanged'
    if not 'translation' in PosTagsRepository:
        return ''
    for Key in PosTagsRepository['translation']:
        if Tag[:len(Key)] == Key:
            return PosTagsRepository['translation'][Key]
    return ''

def map_postag( Tag, Params ):
    _load_repository( Params )
    return _map_postag1( Tag )

@lru_cache(maxsize=256, typed=False)
def _map_postag1( Tag ):
    if 'map' in PosTagsRepository:
        for Key in PosTagsRepository['map'].keys():
            if Tag in PosTagsRepository['map'][Key]:
                return Key
    if 'translation' in PosTagsRepository and Tag in PosTagsRepository['translation'].keys():
        return Tag # return unchanged if it's in the "translation" part
    if 'use_unchanged' in PosTagsRepository and PosTagsRepository['use_unchanged'] == 'yes':
        return Tag # return unchanged if language is marked as 'use_unchanged'
    return '' # don't use it!

def _load_repository( Params ):
    global PosTagsRepository
    if not PosTagsRepository:
        globalPosRepository = _load_global_repository( Params )
        if Params.postags_file != '':
            # load from configured file
            lara_utils.print_and_flush( f'--- loading local PoS-tags from {Params.postags_file}' )
            PosTagsRepository = _merge_repositories( lara_utils.read_json_file(Params.postags_file), globalPosRepository )
        else:
            PosTagsRepository = globalPosRepository
        if not type(PosTagsRepository) is dict:
            lara_utils.print_and_flush('*** Warning: could not load PoS-tags repository or language not supported')
            PosTagsRepository = dict()

def _load_global_repository( Params ):
    repofile = lara_utils.absolute_filename_in_python_directory('lara_postags.json')
    lara_utils.print_and_flush(f'--- loading global PoS-tags from {repofile}')
    allPosTags = lara_utils.read_json_file(repofile)
    if Params.language in allPosTags:
        return allPosTags[ Params.language ]
    return _EmptyPosTagsRepository # return empty repo for unkn lang

def _merge_repositories( repo1, repo2 ):
    # add entries from repo2's "map" and "translation" to the end of repo1
    if not type(repo1) is dict:
        repo1 = _EmptyPosTagsRepository
    if not type(repo2) is dict:
        repo2 = _EmptyPosTagsRepository
    for Section in [ 'map', 'translation' ]:
        if Section in repo2:
            if not Section in repo1:
                repo1[Section] = dict()
            for Key in repo2[Section].keys():
                if not Key in repo1[Section]:
                    repo1[Section][Key] = repo2[Section][Key]
    return repo1
