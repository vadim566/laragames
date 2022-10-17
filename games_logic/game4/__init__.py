import json

from flask import render_template, request, flash, redirect, url_for, jsonify

import app
from SVN.trunk.Code.Python import lara_utils
from config.config import mypath, slash_clean
from db.db import tbl_game4
from functions.functions import dirinDir, check_if_finished, user_message, get_story_sounds_sentance
import random

from app import db



def game4(story_name,file=None):
    sentance, sounds = get_story_sounds_sentance(story_name)

    """get random sentance"""
    size_of_story =  len(sentance)-1
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
    if g_number > 9:
        return check_if_finished(g_wins, g_number)
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
        user_message('right_answer')
        wins+=1
    else:
        item = tbl_game4(score=0, user_id=uid, question=name)

        user_message('bad_answer')
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
