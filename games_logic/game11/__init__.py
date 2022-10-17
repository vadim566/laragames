from flask import render_template, request, flash, redirect, url_for

from SVN.trunk.Code.Python import lara_utils
from config.config import mypath, slash_clean
from db.db import tbl_game11
from functions.functions import dirinDir, clean_word, check_if_finished, user_message, get_story_sounds_sentance
import random

from app import db


def game11(story_name, file=None):
    sentance, sounds = get_story_sounds_sentance(story_name)
    """get random sentance"""
    size_of_story = len(sentance)
    rand_index = random.randint(0, size_of_story)

    """gather 4 random index for 4 wrong answers """
    rand_i = random.sample(range(0, size_of_story), 4)

    true_match = [sentance[rand_index], sounds[rand_index]]
    bad_match = [sentance[rand_i[0]], sentance[rand_i[1]], sentance[rand_i[2]], sentance[rand_i[3]]]

    true_word = ['', '']
    # count the words in the sentance
    words_ct = true_match[0].count(" ")

    tries = 0
    max_tries = 5
    while (words_ct < 5):
        tries += 1
        rand_index = random.randint(0, size_of_story)
        true_match[0] = sentance[rand_index]
        words_ct = true_match[0].count(" ")

        if (tries > max_tries):
            generate_game11(story_name, file)

    # pick random word between word set
    rand_ct = random.sample(range(1, words_ct), 2)
    # swap the word into [-------]
    words_arr = true_match[0].split(' ')
    # true_word=words_arr[rand_ct[0]]#right answer

    true_word[0] = words_arr[rand_ct[0]]
    true_word[1] = words_arr[rand_ct[1]]

    words_arr[rand_ct[0]] = "[--------]"
    words_arr[rand_ct[1]] = "[--------]"

    missing_sent = " ".join(words_arr)  # missing sentance to question
    # clean the words from special signs
    true_word[0] = clean_word(true_word[0])
    true_word[1] = clean_word(true_word[1])
    # send the right missing word and wrong words

    print("q:" + missing_sent)
    print("t_a:" + true_word[0] + ' ' + true_word[1])


    return true_word[0],true_word[1],missing_sent,true_match[1],story_name


def generate_game11(story_name,g_number=0,g_wins=0):
    g_number = int(g_number)
    g_wins = int(g_wins)
    t_w0,t_w1,m_w,m_s,s_name=game11(story_name)
    if g_number > 9:
        return check_if_finished(g_wins, g_number)
    else:
        return render_template('game11_template.html', t_answer0=t_w0, t_answer1=t_w1, question0=m_w, question1=m_s, name=s_name, g_number=g_number, wins=g_wins)


def submit_g11(option=0,answer=0,default_value=0,g_number=0,wins=0):
    wins = int(wins)
    g_number = int(g_number)

    name = request.form.get('storyname', default_value)
    option0 = request.form.get('option0', default_value)
    option1 = request.form.get('option1', default_value)
    answer0 = request.form.get('answer0', default_value)
    answer1 = request.form.get('answer1', default_value)
    uid = request.form.get('uid', default_value)

    print("name: ", name)
    print("option0: ", option0)
    print("option1: ", option1)
    print("answer0: ", answer0)
    print("answer1: ", answer1)

    if option0.lower() == answer0.lower() and option1.lower() == answer1.lower() :
        item = tbl_game11(score=1, user_id=uid,question=name)
        user_message('right_answer')

        wins += 1
    elif option1.lower() == answer0.lower() and option0.lower() == answer1.lower() :
        item = tbl_game11(score=1, user_id=uid,question=name)
        user_message('right_answer')

    else:
        item = tbl_game11(score=0, user_id=uid,question=name)

        user_message('bad_answer')
    db.session.add(item)
    db.session.commit()
    g_number += 1
    values_s = [name, g_number, wins]
    return redirect(url_for('app.generate_game11', values=values_s))