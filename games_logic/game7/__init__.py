from flask import render_template, request, flash, redirect, url_for

from SVN.trunk.Code.Python import lara_utils
from config.config import mypath, slash_clean
from db.db import tbl_game7
from functions.functions import dirinDir, clean_word, check_if_finished, user_message, get_story_sounds_sentance
import random

from app import db


def game7(story_name):
    sentance, sounds = get_story_sounds_sentance(story_name)

    """get random sentance"""
    size_of_story =  len(sentance)-1
    sentence_len_size = 4
    sentence_len = True
    while sentence_len:
        rand_index = random.randint(0, size_of_story)


        """gather 4 random index for 4 wrong answers """
        rand_i = random.sample(range(0, size_of_story), 4)

        true_match = [sentance[rand_index], sounds[rand_index]]
        split_setance = true_match[0].split(" ", sentence_len_size)
        if len(split_setance) >= sentence_len_size:
            sentence_len = False

    # count the words in the sentance
    words_ct = true_match[0].count(" ")
    # pick random word between word set
    rand_ct = random.sample(range(1, words_ct), 1)
    # swap the word into [-------]
    words_arr = true_match[0].split(' ')
    true_word = clean_word(words_arr[rand_ct[0]])  # right anwser
    words_arr[rand_ct[0]] = "[--------]"
    missing_sent = " ".join(words_arr)  # missing sentance to question
    # pick random words from  the wrong sentance


    # send the right missing word and wrong words

    print("q:" + missing_sent)
    print("t_a:" + true_word)

    return true_word, missing_sent, true_match[1],story_name

def generate_game7(story_name,g_number=0,g_wins=0):
    g_number = int(g_number)
    g_wins = int(g_wins)
    t_w,m_s,t_m,s_name = game7(story_name)
    if g_number > 9:
        return check_if_finished(g_wins, g_number)

    else:
        return render_template('game7_template.html', t_answer=t_w, question0=m_s, question1=t_m, name=s_name , g_number=g_number, wins=g_wins)

def submit_g7(option=0, answer=0, default_value=0,g_number=0,wins=0):

    name = request.form.get('storyname', default_value)
    option = request.form.get('option', default_value)
    answer = request.form.get('answer', default_value)
    uid = request.form.get('uid', default_value)

    print("name: ", name)
    print("option: ", option)
    print("answer: ", answer)


    wins=int(wins)
    g_number=int(g_number)
    if option.lower() == answer.lower():
        item = tbl_game7(score=1, user_id=uid, question=name)
        user_message('right_answer')

        wins+=1
    else:
        item = tbl_game7(score=0, user_id=uid, question=name)

        user_message('bad_answer')
    db.session.add(item)
    db.session.commit()
    g_number+=1
    values_s=[name,g_number,wins]


    return redirect(url_for('app.generate_game7',  values=values_s))


