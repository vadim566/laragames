import json

from flask import render_template, request, flash, redirect, url_for, jsonify

import app
from SVN.trunk.Code.Python import lara_utils
from config.config import mypath, slash_clean
from db.db import tbl_game4
from functions.functions import dirinDir
import random

from app import db



def game4(story_name,file=None):
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

    while rand_index in rand_i:  # make sure there is no duplicate words
        rand_i = random.sample(range(0, size_of_story), 4)

    true_match = [sentance[rand_index], sounds[rand_index]]
    bad_match = [sentance[rand_i[0]], sentance[rand_i[1]], sentance[rand_i[2]], sentance[rand_i[3]]]

    print(true_match)
    print(bad_match)
    return  true_match[0], true_match[1],bad_match[0], bad_match[1], bad_match[2],bad_match[3], story_name

def generate_game4(story_name,g_number=0,g_wins=0):
    # TODO add template game 4
    # TODO add redirecter to game4
    # TODO print build dic from metadata file
    # TODO get the metadata folder, random of all of these that inside the folder
    g_number=int(g_number)
    g_wins=int(g_wins)
    t_a ,t_q,f_a0,f_a1,f_a2,f_a3,s_name =game4(story_name)
    if g_number>0:
        score=(g_wins/g_number)*100

    if g_number >=10 and g_wins<6:
        flash('Game Over! You could better!Try better next time! Your Score is:'+str(score), 'danger')
        return redirect(url_for('app.home'))

    elif g_number >=10 and g_wins>5 and g_wins <8:
        flash('Game Over! Your doing good job! proceed training !Your Score is:'+str(score), 'success')
        return redirect(url_for('app.home'))

    elif g_number >=10 and g_wins>7 :
        flash('Game Over! Your are Excellent! Try advanced level!'+str(score), 'success')
        return redirect(url_for('app.home'))
    else:
        return render_template('game4_template.html', t_answer=t_a, question=t_q,fake_answer_0=f_a0, fake_answer_1=f_a1, fake_answer_2=f_a2,fake_answer_3=f_a3, name=s_name,g_number=g_number,wins=g_wins)

def submit_g4(option=0, answer=0, default_value=0,g_number=0,wins=0):
    option = request.form.get('option')


    name = request.form.get('storyname', default_value)
    answer = request.form.get('answer', default_value)
    uid = request.form.get('uid', default_value)
    print("name: ", name)
    print("option: ", option)
    print("answer: ", answer)
    wins=int(wins)
    g_number=int(g_number)
    if option.lower() == answer.lower():
        item = tbl_game4(score=1, user_id=uid, question=name)
        flash('Right answer you got 1 point', 'success')
        wins+=1
    else:
        item = tbl_game4(score=0, user_id=uid, question=name)
        flash('bad answer you got 0 point', 'danger')
    db.session.add(item)
    db.session.commit()
    g_number+=1
    values_s=[name,g_number,wins]
    return redirect(url_for('app.generate_game4', values=values_s))


def fetch_game4(story_name,g_number=0,g_wins=0):
    t_a, t_q, f_a0, f_a1, f_a2, fa_3, s_name = game4(story_name)
    if (int(g_number) < 10):
        msg_front=jsonify([t_a ,t_q,f_a0,f_a1,f_a2,fa_3,s_name,str(int(g_number)+1),g_wins ])
        return msg_front
    else:
        t_a=t_q=f_a0=f_a1=f_a2=fa_3='game over'
        msg_front=jsonify([t_a ,t_q,f_a0,f_a1,f_a2,fa_3,s_name,str(g_number+1),g_wins ])
        return msg_front
