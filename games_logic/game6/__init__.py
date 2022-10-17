from flask import render_template, request, flash, redirect, url_for

from SVN.trunk.Code.Python import lara_utils
from config.config import mypath, slash_clean
from db.db import tbl_game6
from functions.functions import dirinDir, clean_word, check_if_finished, user_message, get_story_sounds_sentance
import random

from app import db



def game6(story_name, file=None):
    sentance, sounds = get_story_sounds_sentance(story_name)
    """get random sentance"""
    size_of_story = len(sentance)
    rand_index = random.randint(0, size_of_story)

    """gather 4 random index for 4 wrong answers """
    rand_i = random.sample(range(0, size_of_story), 4)

    true_match = [sentance[rand_index], sounds[rand_index]]
    bad_match = [sentance[rand_i[0]], sentance[rand_i[1]], sentance[rand_i[2]], sentance[rand_i[3]]]

    # count the words in the sentance
    words_ct = true_match[0].count(" ")
    # pick random word between word set
    rand_ct = random.sample(range(1, words_ct), 1)
    # swap the word into [-------]
    words_arr = true_match[0].split(' ')
    true_word = words_arr[rand_ct[0]]  # right anwser
    words_arr[rand_ct[0]] = "[--------]"
    missing_sent = " ".join(words_arr)  # missing sentance to question
    # pick random words from  the wrong sentance
    bad_words = []
    for i in range(len(bad_match)):
        bad_words_arr = bad_match[i].split(' ')  # split where is white space
        words_ct = bad_match[i].count(" ")
        bad_rand_ct = random.sample(range(0, words_ct), 1)
        bad_words.append(clean_word(bad_words_arr[bad_rand_ct[0]]))  # bad answer

    # send the right missing word and wrong words
    true_word=clean_word(true_word)
    print("q:" + missing_sent)
    print("t_a:" + true_word)
    print(bad_words)

    return  true_word,  missing_sent,  true_match[1],bad_words[0],  bad_words[1], bad_words[2], bad_words[3], story_name





def generate_game6(story_name ,g_number=0,g_wins=0):
    g_number = int(g_number)
    g_wins = int(g_wins)
    t_w, t_q,t_m, f_a0, f_a1, f_a2, f_a3, s_name = game6(story_name)

    if g_number > 9:
        return check_if_finished(g_wins, g_number)
    else:
        return render_template('game6_template.html', t_answer=t_w, question0=t_q, question1=t_m,fake_answer_0=f_a0, fake_answer_1= f_a1, fake_answer_2= f_a2,fake_answer_3= f_a3, name=s_name \
                               ,g_number=g_number,wins=g_wins)



def submit_g6(option=0, answer=0, default_value=0,g_number=0,wins=0):
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
        item = tbl_game6(score=1, user_id=uid, question=name)
        user_message('right_answer')

        wins+=1
    else:
        item = tbl_game6(score=0, user_id=uid, question=name)

        user_message('bad_answer')

    db.session.add(item)
    db.session.commit()
    g_number+=1
    values_s=[name,g_number,wins]
    return redirect(url_for('app.generate_game6', values=values_s))