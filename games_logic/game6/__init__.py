from flask import render_template, request, flash, redirect, url_for

from SVN.trunk.Code.Python import lara_utils
from config.config import mypath, slash_clean
from db.db import tbl_game6
from functions.functions import dirinDir, clean_word
import random

from lara_games_app import db


def generate_game6(story_name, file=None):


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

    return render_template('game6_template.html', t_answer=true_word, question0=missing_sent, question1=true_match[1],
                           fake_answer_0=bad_words[0], fake_answer_1=bad_words[1], fake_answer_2=bad_words[2],
                           fake_answer_3=bad_words[3], name=story_name)



def submit_g6(option=0,answer=0,default_value=0):

    name = request.form.get('storyname', default_value)
    option = request.form.get('option', default_value)
    answer = request.form.get('answer', default_value)
    uid = request.form.get('uid', default_value)

    print("name: ", name)
    print("option: ", option)
    print("answer: ", answer)

    if option.lower() == answer.lower():
        item = tbl_game6(score=1, user_id=uid,question=name)
        flash('Right answer', 'success')
    else:
        item = tbl_game6(score=0, user_id=uid,question=name)
        flash('bad answer', 'danger')
    db.session.add(item)
    db.session.commit()
    return redirect(url_for('app.generate_game6', story_name=name))

