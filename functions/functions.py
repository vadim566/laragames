from datetime import datetime
from os import listdir
from os.path import isfile ,join,isdir




from SVN.trunk.Code.Python import lara_utils
from config.config import language, onlydir, compiled_path, slash, corpus_suffix

'''functions'''

def clean_word(word :str) ->str:
    clean_word = "".join(c for c in word if c.isalpha())
    return clean_word


# get the language of each story
def get_language():
    language

    for s in onlydir:
        conf_file = compiled_path + slash + str(s) + str(corpus_suffix)
        language_tmp=lara_utils.read_json_file(conf_file)['language']
        language.append(language_tmp)


# returning a list with files in dir_path
def filesinDir(dir_path):
    try:
        files_in_dir = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]
    except:
        "something wrong with the directory, put in the full path"
    finally:
        return files_in_dir


# returning a list with sub dir to dir_path
def dirinDir(dir_path):
    try:
        dir_in_dir = [f for f in listdir(dir_path) if isdir(join(dir_path, f))]
    except:
        "something wrong with the directory, put in the full path"
    finally:
        return dir_in_dir


def getWords(dir_path, prefix_word):
    try:
        files_in_dir = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]
    except:
        "something wrong with the directory, put in the full path"
    finally:
        word_list = []
        for file_name in files_in_dir:
            if prefix_word in file_name:
                word = file_name.split('_')[1].split('.')[0]
                word_list.append(word)
        return word_list


def calculate_rate(gametbl):
    total_games = len(gametbl)
    win = 0
    for item in gametbl:
        win += item.score
    return win / total_games


'''forms'''


# forms



def game_lists(game):
    date_list = ['']
    game_ct = ['']
    wins_ct = ['']
    for g in game:

        if (date_list[-1] == str(g.date_created.date())):
            game_ct[-1] = game_ct[-1] + 1
            wins_ct[-1] = wins_ct[-1] + g.score
        else:
            date_list.append(str(g.date_created.date()))
            game_ct.append(1)
            wins_ct.append(g.score)
    return date_list, game_ct, wins_ct


def analayzeGame(game, wr):
    if (len(game) > 0):
        wr[0] = calculate_rate(game)
        dates, games_perDay, wins_perDay = game_lists(game)
        wr.append(dates)
        wr.append(games_perDay)
        wr.append(wins_perDay)
    else:
        wr.append(str(datetime.now().date()))
        wr.append(['',0])
        wr.append(['',0])

    return wr
