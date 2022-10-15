
from flask import render_template, request, flash, redirect, url_for

from SVN.trunk.Code.Python import lara_utils
from config.config import mypath, slash_clean
from db.db import tbl_game8
from functions.functions import dirinDir, clean_word, check_if_finished
import random

from app import db

def game8(story_name, file=None):


    metaDataAudioDir = mypath + slash_clean + story_name + slash_clean + 'audio' + slash_clean
    audioVersions = dirinDir(metaDataAudioDir)

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

    """get random sentance"""
    size_of_story = len(sentance)
    rand_index = random.randint(0, size_of_story)

    """gather 4 random index for 4 wrong answers """
    rand_i = random.sample(range(0, size_of_story), 4)

    true_match = [sentance[rand_index], sounds[rand_index]]
    bad_match = [sentance[rand_i[0]], sentance[rand_i[1]], sentance[rand_i[2]], sentance[rand_i[3]]]

    # split the sentance
    split_setance = true_match[0].split(" ", 4)
    print(split_setance)
    random.shuffle(split_setance)

    return true_match[0],true_match[1],split_setance[0],split_setance[1], split_setance[2],split_setance[3],split_setance[4], story_name



def generate_game8(story_name,g_number=0,g_wins=0):
    g_number = int(g_number)
    g_wins = int(g_wins)

    t_m0,t_m1,s_p0,s_p1,s_p2,s_p3,s_p4,s_name=game8(story_name)
    if g_number>9:
       return check_if_finished(g_wins,g_number)
    else:
        return render_template('game8_template.html', t_answer=t_m0, question1=t_m1,
                           split_a0=s_p0, split_a1=s_p1, split_a2=s_p2,
                           split_a3=s_p3, split_a4=s_p4, name=story_name, g_number=g_number, wins=g_wins)


def submit_g8(option=0, answer=0, default_value=0,g_number=0,wins=0):

    name = request.form.get('storyname', default_value)
    option = request.form.get('option', default_value)
    answer = request.form.get('answer', default_value)
    uid = request.form.get('uid', default_value)

    print("name: ", name)
    print("option: ", option)
    print("answer: ", answer)

    wins = int(wins)
    g_number = int(g_number)
    if option.lower() == answer.lower():
        item = tbl_game8(score=1, user_id=uid, question=name)
        flash('Right answer you got 1 point', 'success')
        wins += 1
    else:
        item = tbl_game8(score=0, user_id=uid, question=name)
        flash('bad answer you got 0 point', 'danger')
    db.session.add(item)
    db.session.commit()
    g_number += 1
    values_s = [name, g_number, wins]

    return redirect(url_for('app.generate_game8',  values=values_s))



