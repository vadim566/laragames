from flask import render_template, request, flash, redirect, url_for

from SVN.trunk.Code.Python import lara_utils
from config.config import mypath, slash_clean
from db.db import tbl_game12
from functions.functions import dirinDir, clean_word, check_if_finished, user_message
import random

from app import db




def game12(story_name, file=None):


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
    rand_i = random.sample(range(0, size_of_story), 4)

    true_match=['tmp','tmp']
    while len(true_match[0].split()) <5 :
        true_match = [sentance[rand_index], sounds[rand_index]]

    true_word = ['', '']
    # count the words in the sentance
    words_ct = true_match[0].count(" ")
    # pick random word between word set
    rand_ct = random.sample(range(1, words_ct), 1)
    # swap the word into [-------]
    words_arr = true_match[0].split(' ')
    # true_word=words_arr[rand_ct[0]]#right answer

    if rand_ct[0] + 1 >= words_ct and rand_ct[0] - 1 >= 0:
        true_word = clean_word(words_arr[rand_ct[0] - 1]) + ' ' + clean_word(words_arr[rand_ct[0]])
        words_arr[rand_ct[0]] = "[--------]"
        words_arr[rand_ct[0] - 1] = "[--------]"
    else:
        true_word = clean_word(words_arr[rand_ct[0]]) + ' ' + clean_word(words_arr[rand_ct[0] + 1])
        words_arr[rand_ct[0]] = "[--------]"
        words_arr[rand_ct[0] + 1] = "[--------]"

    missing_sent = " ".join(words_arr)  # missing sentance to question
    # pick random words from  the wrong sentance


    # send the right missing word and wrong words

    print("q:" + missing_sent)
    print("t_a:" + true_word)


    return true_word, missing_sent, true_match[1],  story_name


def generate_game12(story_name,g_number=0,g_wins=0):
    g_number = int(g_number)
    g_wins = int(g_wins)
    t_w,m_s,t_m,s_name=game12(story_name)
    if g_number > 9:
        return check_if_finished(g_wins, g_number)
    else:
        return render_template('game12_template.html', t_answer=t_w, question0=m_s, question1=t_m,  name=s_name, g_number=g_number, wins=g_wins)


def submit_g12(option=0,answer=0,g_number=0,wins=0):
    wins = int(wins)
    g_number = int(g_number)

    default_value = 0
    name = request.form.get('storyname', default_value)
    option = request.form.get('option', default_value)
    answer = request.form.get('answer', default_value)
    uid = request.form.get('uid', default_value)

    print("name: ", name)
    print("option: ", option)
    print("answer: ", answer)

    if option.lower() == answer.lower():
        item = tbl_game12(score=1, user_id=uid,question=name)
        user_message('right_answer')

        wins += 1
    else:
        item = tbl_game12(score=0, user_id=uid,question=name)

        user_message('bad_answer')
    db.session.add(item)
    db.session.commit()
    g_number += 1
    values_s = [name, g_number, wins]

    return redirect(url_for('app.generate_game12', values=values_s))