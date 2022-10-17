from flask import render_template, request, flash, redirect, url_for

from SVN.trunk.Code.Python import lara_utils
from config.config import mypath, slash_clean
from db.db import tbl_game10
from functions.functions import dirinDir, clean_word, check_if_finished, user_message, get_story_sounds_sentance
import random

from app import db

def game10(story_name, file=None):
    sentance, sounds= get_story_sounds_sentance(story_name)
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
            generate_game10(story_name, file)

    # pick random word between word set
    rand_ct = random.sample(range(1, words_ct), 2)
    # swap the word into [-------]
    words_arr = true_match[0].split(' ')
    # true_word=words_arr[rand_ct[0]]#right answer

    true_word = clean_word(words_arr[rand_ct[0]]) + ',' + clean_word(words_arr[rand_ct[1]])

    words_arr[rand_ct[0]] = "[--------]"
    words_arr[rand_ct[1]] = "[--------]"

    missing_sent = " ".join(words_arr)  # missing sentance to question
    # pick random words from  the wrong sentance
    bad_words = []
    for i in range(len(bad_match)):
        bad_words_arr = bad_match[i].split(' ')
        words_ct = bad_match[i].count(" ")
        bad_rand_ct = random.sample(range(0, words_ct), 2)

        bad_words.append(clean_word(bad_words_arr[bad_rand_ct[0]]) + ',' + clean_word(bad_words_arr[bad_rand_ct[1]]))

    # send the right missing word and wrong words

    print("q:" + missing_sent)
    print("t_a:" + true_word)
    print(bad_words)

    return true_word, missing_sent, true_match[1],bad_words[0],bad_words[1],bad_words[2],bad_words[3],story_name

def generate_game10(story_name,g_number=0,g_wins=0):
    g_number = int(g_number)
    g_wins = int(g_wins)

    t_w,m_s,t_m,b_w0,b_w1,b_w2,b_w3,s_name=game10(story_name)
    if g_number > 9:
        return check_if_finished(g_wins, g_number)
    else:
        return render_template('game10_template.html', t_answer=t_w, question0=m_s, question1=t_m,
                           fake_answer_0=b_w0, fake_answer_1=b_w1, fake_answer_2=b_w2,
                           fake_answer_3=b_w3, name=s_name, g_number=g_number, wins=g_wins)



def submit_g10(option=0,answer=0,default_value=0,g_number=0,wins=0):

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
        item = tbl_game10(score=1, user_id=uid, question=name)
        user_message('right_answer')

        wins += 1
    else:
        item = tbl_game10(score=0, user_id=uid, question=name)

        user_message('bad_answer')
    db.session.add(item)
    db.session.commit()
    g_number += 1
    values_s = [name, g_number, wins]

    return redirect(url_for('app.generate_game10', values=values_s))