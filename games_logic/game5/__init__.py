from flask import render_template, request, flash, redirect, url_for

from SVN.trunk.Code.Python import lara_utils
from config.config import mypath, slash_clean
from db.db import tbl_game5
from functions.functions import dirinDir, check_if_finished
import random

from app import db

def game5(story_name, file=None):


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

    """get random sentance"""
    size_of_story = len(sentance)
    rand_index = random.randint(0, size_of_story)

    """gather 4 random index for 4 wrong answers """
    rand_i = [rand_index, rand_index, rand_index, rand_index]

    while rand_index in rand_i:#make sure there is no duplicate words
        rand_i = random.sample(range(0, size_of_story), 4)

    true_match = [sentance[rand_index], sounds[rand_index]]
    bad_match = [sounds[rand_i[0]], sounds[rand_i[1]], sounds[rand_i[2]], sounds[rand_i[3]]]

    print(true_match)
    print(bad_match)

    return  true_match[1], true_match[0], bad_match[0],bad_match[1], bad_match[2], bad_match[3], story_name




def generate_game5(story_name ,g_number=0,g_wins=0):

    g_number=int(g_number)
    g_wins=int(g_wins)
    t_a ,t_q,f_a0,f_a1,f_a2,f_a3,s_name =game5(story_name)

    if g_number > 9:
        return check_if_finished(g_wins, g_number)
    else:
        return render_template('game5_template.html', t_answer=t_a, question=t_q,fake_answer_0=f_a0, fake_answer_1=f_a1, fake_answer_2=f_a2,fake_answer_3=f_a3, name=s_name,g_number=g_number,wins=g_wins)


def submit_g5(option=0,answer=0, default_value=0,g_number=0,wins=0):

    name = request.form.get('storyname', default_value)
    option = request.form.get('option', default_value)

    uid = request.form.get('uid', default_value)

    print("name: ", name)
    print("option: ", option)
    g_number=int(g_number)
    wins=int(wins)
    if option == '1':
        item = tbl_game5(score=1, user_id=uid,question=name)
        flash('Right answer', 'success')
        wins += 1
    else:
        item = tbl_game5(score=0, user_id=uid,question=name)
        flash('bad answer', 'danger')
    db.session.add(item)
    db.session.commit()
    g_number += 1
    values_s = [name, g_number, wins]
    return redirect(url_for('app.generate_game5', values=values_s))