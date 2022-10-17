import random
from datetime import datetime
from os import listdir
from os.path import isfile ,join,isdir

from flask import send_from_directory, redirect, url_for, flash

from SVN.trunk.Code.Python import lara_utils
from config.config import language, onlydir, compiled_path, slash, corpus_suffix, slash_clean, mypath, content_loc

'''functions'''
def check_if_finished(g_wins,g_number):
    if g_number > 0:
        score = (g_wins / g_number) * 100

    if g_number >= 10 and g_wins < 6:
        flash('Game Over! You could better!Try better next time! Your Score is:' + str(score), 'danger')
        return redirect(url_for('app.home'))

    elif g_number >= 10 and g_wins > 5 and g_wins < 8:
        flash('Game Over! Your doing good job! Proceed training !Your Score is:' + str(score), 'success')
        return redirect(url_for('app.home'))

    elif g_number >= 10 and g_wins > 7:
        flash('Game Over! Your are Excellent! Try advanced level!Your Score is:' + str(score), 'success')
        return redirect(url_for('app.home'))
    else:
        return

def split_values(values):
    values=values.split("[")
    values=values[1].split("]")
    values=values[0].split(",")
    name=values[0].split("'")[1]
    games=str(int(values[1]))
    wins=str(int(values[2]))
    values=[name,games,wins]
    return values


def clean_word(word :str) ->str:
    clean_word = "".join(c for c in word if c.isalpha())
    return clean_word

#redirect to story folder data
def story_folder_data(name):
    flag = 0

    # compile only if it is not existed in compiled folder
    for dir in dirinDir(content_loc):
        if name in dir:
            if '_hyperlinked_text_.html' in filesinDir(content_loc + slash + dir):
                flag = 1
                break
        else:
            pass
    if flag == 0:
        ful_loc = content_loc + name + corpus_suffix
        #  try:
        # os.system("python "+ lara_builder + lara_builder_creator + ful_loc)
        #  except:
        #  subprocess.call(py_ver+ lara_builder + lara_builder_creator + ful_loc)
        # finally:
        return redirect(url_for('app.surf', story_name=name, name=name))

# get the language of each story
def get_language():
    language

    for s in onlydir:
        conf_file = compiled_path + slash + str(s) + str(corpus_suffix)
        language_tmp=lara_utils.read_json_file(conf_file)['language']
        language.append(language_tmp)

#enable to load picture from directories in flask
def loading_file_pic(filename, story_name):
    metaDataAudioDir = mypath + slash_clean + story_name + slash_clean + 'audio' + slash_clean
    audioVersions = dirinDir(metaDataAudioDir)
    # TODO add expectaion
    # File = metaDataAudioDir + audioVersions[0] + '/'+filename
    return send_from_directory(metaDataAudioDir + slash_clean + audioVersions[0], filename)

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

def user_message(msg_type:str):
    if  msg_type=='right_answer':
        flash('Right answer you got 1 point', 'success')
        good_messages=['Your are Great!','Nice Job!','Excellent!']
        index_mesg=random.randint(0,len(good_messages)-1)
        flash(good_messages[index_mesg], 'info')

    elif msg_type=='bad_answer':
        flash('Bad answer you got 0 point', 'danger')
        get_better_messages = ['Dont Panic, just focus! You can do it!', 'Its ok to make mistakes', 'Mistakes pave the road to excellence!']
        index_mesg = random.randint(0, len(get_better_messages)-1 )
        flash(get_better_messages[index_mesg], 'info')

def get_story_sounds_sentance(story_name):
    metaDataAudioDir = mypath + slash_clean + story_name + slash_clean + 'audio' + slash_clean
    audioVersions = dirinDir(metaDataAudioDir)
    # TODO add expectaion
    File = metaDataAudioDir + audioVersions[0] + slash_clean + 'metadata_help.json'
    Metadata = lara_utils.read_json_file(File)
    meta_dic = [{}]
    for m in Metadata:
        meta_dic[0].update({m['text']: m['file']})
    sentance = []
    sounds = []
    for key, value in meta_dic[0].items():
        sentance.append(key)
        sounds.append(value)
    return sentance ,sounds