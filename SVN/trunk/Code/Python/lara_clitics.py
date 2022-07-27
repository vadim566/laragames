
import lara_utils

# Data adapted from TreeTagger preprocessing script:
# French
# $PClitic = '[dcjlmnstDCJLNMST][\'’]|[Qq]u[\'’]|[Jj]usqu[\'’]|[Ll]orsqu[\'’]';
# $FClitic = '-t-elles?|-t-ils?|-t-on|-ce|-elles?|-ils?|-je|-la|-les?|-leur|-lui|-mmes?|-m[\'’]|-moi|-nous|-on|-toi|-tu|-t[\'’]|-vous|-en|-y|-ci|-l';
# English
# $FClitic = '[\'’](s|re|ve|d|m|em|ll)|n[\'’]t';
# Italian
# $PClitic = '[dD][ae]ll[\'’]|[nN]ell[\'’]|[Aa]ll[\'’]|[cClLDd][\'’]|[Ss]ull[\'’]|[Qq]uest[\'’]|[Uu]n[\'’]|[Ss]enz[\'’]|[Tt]utt[\'’]';

clitics = { ('english', 'post' ): {'APOSTROPHEs': ( 'be or have or s', 'V or POSS' ),
                                   'APOSTROPHEre': ( 'be', 'V' ),
                                   'APOSTROPHEve': ( 'have', 'V' ),
                                   'APOSTROPHEd': ( 'have/would', 'V' ),
                                   'APOSTROPHEm': ( 'be', 'V' ),
                                   'APOSTROPHEem': ( 'them', 'PRO' ),
                                   'APOSTROPHEll': ( 'will', 'N' ),
                                   'nAPOSTROPHEt': ( 'not', 'NEG' )
                                   },
            ('italian', 'pre'): {'dAPOSTROPHE': ( 'di', 'P' ),
                                 'dalAPOSTROPHE': ( 'dalla', 'P+DET' ),
                                 'delAPOSTROPHE': ( 'della', 'P+DET' ),
                                 'cAPOSTROPHE': ( 'ci', 'DET' ),
                                 'nellAPOSTROPHE': ( 'nella', 'P+DET' ),
                                 'allAPOSTROPHE': ( 'alla', 'P+DET' ),
                                 'lAPOSTROPHE': ( 'lo', 'DET' ),
                                 'sullAPOSTROPHE': ( 'sulla', 'P+DET' ),
                                 'questAPOSTROPHE': ( 'questo', 'DET' ),
                                 'unAPOSTROPHE': ( 'uno', 'DET' ),
                                 'senzAPOSTROPHE': ( 'senza', 'P' ),
                                 'tuttAPOSTROPHE': ( 'tutte', 'DET' )
                                },
            ('italian', 'post_final'):{'mi': ('mi', 'P'),
                                       'ti': ('ti', 'P'),
                                       'lo': ('lo', 'P'),
                                       'la': ('la', 'P'),
                                       'si': ('si', 'P'),
                                       'gli': ('gli', 'P'),
                                       'ci': ('ci', 'P'),
                                       'vi': ('vi', 'P'),
                                       'li': ('li', 'P'),
                                       'le': ('le', 'P'),
                                       'loro': ('loro', 'P')
                                       },
            ('italian', 'post_non_final'):{'me': ('mi', 'P'),
                                           'te': ('ti', 'P'),
                                           'lo': ('lo', 'P'),
                                           'la': ('la', 'P'),
                                           'se': ('si', 'P'),
                                           'glie': ('gli', 'P'),
                                           'ce': ('ci', 'P'),
                                           've': ('vi', 'P'),
                                           'lie': ('li', 'P'),
                                           'le': ('le', 'P'),
                                           'loro': ('loro', 'P')
                                           },
            ('catalan', 'pre'): {'dAPOSTROPHE': ( 'de', 'DET' ),
                                 'lAPOSTROPHE': ( 'el', 'DET' ),
                                 'mAPOSTROPHE': ( 'mi', 'PRO' ),
                                 'nAPOSTROPHE': ( 'ne', 'NEG' ),
                                 'sAPOSTROPHE': ( 'si', 'ADJ' ),
                                 'tAPOSTROPHE': ( 'tu', 'PRO' ),
                                 'quAPOSTROPHE': ( 'que', 'CONJ' )
                                },
            ('french', 'pre'): {'cAPOSTROPHE': ( 'ce', 'DET' ),
                                'dAPOSTROPHE': ( 'de', 'P' ),
                                'jAPOSTROPHE': ( 'je', 'PRO' ),
                                'lAPOSTROPHE': ( 'le', 'DET or PRO' ),
                                'mAPOSTROPHE': ( 'me', 'PRO' ),
                                'nAPOSTROPHE': ( 'ne', 'ADV' ),
                                'sAPOSTROPHE': ( 'se', 'PRO' ),
                                'tAPOSTROPHE': ( 'te', 'PRO' ),
                                'quAPOSTROPHE': ( 'que', 'CONJ' ),
                                'jusquAPOSTROPHE': ( 'jusque', 'P' ),
                                'lorsquAPOSTROPHE': ( 'lorsque', 'P' )
                                },
            ('french', 'post'): {'HYPHENt-elles': ( 'ils', 'PRO' ),
                                 'HYPHENt-ils': ( 'ils', 'PRO' ),
                                 'HYPHENt-on': ( 'on', 'PRO' ),
                                 'HYPHENce': ( 'ce', 'PRO' ),
                                 'HYPHENils': ( 'ils', 'PRO' ),
                                 'HYPHENje': ( 'je', 'PRO' ),
                                 'HYPHENla': ( 'le', 'PRO' ),
                                 'HYPHENles': ( 'le', 'PRO' ),
                                 'HYPHENleur': ( 'le', 'PRO' ),
                                 'HYPHENlui': ( 'lui', 'PRO' ),
                                 'HYPHENmoi': ( 'moi', 'PRO' ),
                                 'HYPHENnous': ( 'nous', 'PRO' ),
                                 'HYPHENon': ( 'on', 'PRO' ),
                                 'HYPHENtoi': ( 'toi', 'PRO' ),
                                 'HYPHENtu': ( 'tu', 'PRO' ),
                                 'HYPHENvous': ( 'vous', 'PRO' ),
                                 'HYPHENen': ( 'en', 'PRO' ),
                                 'HYPHENy': ( 'y', 'PRO' ),
                                 'HYPHENci': ( 'ci', 'PRO' )
                                }
            }

internalised_clitics_cache = {}

apostrophes = "'’"

hyphens = "-"

def is_clitic(Word, Lang):
    for PreOrPost in [ 'pre', 'post', 'post_final', 'post_non_final' ]:
        Clitics = internalised_clitics(Lang, PreOrPost)
        if Word in Clitics:
            Data = Clitics[Word]
            return ( Data[0], Data[1], PreOrPost )
    return ( False, False, False )

def internalised_clitics(Lang, PreOrPost):
    global clitics
    global internalised_clitics_cache
    if (Lang, PreOrPost) in internalised_clitics_cache:
        return internalised_clitics_cache[(Lang, PreOrPost)]
    if not ( Lang, PreOrPost ) in clitics:
        return []
    Orig = clitics[( Lang, PreOrPost )]  
    if PreOrPost == 'pre':
        Internalised = { maybe_capitalize(ExpandedClitic, YOrN): Orig[Clitic] for
                         Clitic in Orig for
                         ExpandedClitic in expand_word(Clitic) for
                         YOrN in ['yes', 'no'] for
                         Apostrophe in apostrophes }
    elif PreOrPost in  [ 'post', 'post_final', 'post_non_final' ]:
        Internalised = { ExpandedClitic : Orig[Clitic] for
                         Clitic in Orig for
                         ExpandedClitic in expand_word(Clitic) }
    internalised_clitics_cache[(Lang, PreOrPost)] = Internalised
    return Internalised

def expand_word(Clitic):
    if Clitic.find('APOSTROPHE') >= 0:
        return [ Clitic.replace('APOSTROPHE', Char) for Char in apostrophes ]
    elif Clitic.find('HYPHEN') >= 0:
        return [ Clitic.replace('HYPHEN', Char) for Char in hyphens ]
    else:
        return [ Clitic ]

def maybe_capitalize(Str, YOrN):
    return Str.capitalize() if YOrN == 'yes' else Str

# ------------------------------------

# 
languages_with_affixed_post_clitics = { 'italian': [ 'VER:impe', 'VER:infi' ] }

def split_off_post_clitics_from_word(Word, Lang, Tag):
    #lara_utils.print_and_flush(f'--- split_off_post_clitics_from_word({Word}, {Lang}, {Tag})')
    # Not a language where we have provided data for affixed post-verbal clitics
    if not Lang in languages_with_affixed_post_clitics:
        return ( Word, [], f'{Word}/{Tag} -> {Word}' )
    # Not a verb form which can attach affixed postverbal clitics
    if not Tag in languages_with_affixed_post_clitics[Lang]:
        return ( Word, [], f'{Word}/{Tag} -> {Word}' )
    ( Word1, FinalClitic ) = split_off_one_post_clitic(Word, Lang, Tag, 'post_final')
    ( Word2, PrefinalClitic ) = split_off_one_post_clitic(Word1, Lang, Tag, 'post_non_final') if FinalClitic else ( False, False )
    if PrefinalClitic and possible_stem_for_language_and_tag(Word2, Lang, Tag):
        ( Stem, Clitics ) = ( Word2, [ PrefinalClitic, FinalClitic ] )
    elif FinalClitic and possible_stem_for_language_and_tag(Word1, Lang, Tag):
        ( Stem, Clitics ) = ( Word1, [ FinalClitic ] )
    else:
        ( Stem, Clitics ) = ( Word, [] )
    Trace = f'{Word}/{Tag} -> {Stem}{format_clitics(Clitics)}'
    return ( Stem, Clitics, Trace )

def format_clitics(Clitics):
    return ' + '.join([ '' ] + [ Clitic[0] for Clitic in Clitics ]) if Clitics != [] else ''

def split_off_one_post_clitic(Word, Lang, Tag, PostType):
    for Length in reversed(range(1, len(Word))):
        Suffix = Word[-1*Length:]
        ( CliticLemma, CliticPOS, PreOrPost ) = is_clitic(Suffix, Lang)
        Stem = Word[:-1*Length]
        if PreOrPost == PostType:
            return ( Stem, ( Suffix, CliticLemma, CliticPOS ) )
    return ( False, False )

# ------------------------------------

# Block some impossible things                     
def possible_stem_for_language_and_tag(Stem, Lang, Tag):
    # No null stems
    if Stem == '':
        return False
    # Italian infinitive stems must end in -r
    if Lang == 'italian' and Tag == 'VER:infi' and not Stem.endswith('r'):
        return False
    return True
    

