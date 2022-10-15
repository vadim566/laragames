from flask import render_template, request, flash, redirect, url_for

from SVN.trunk.Code.Python import lara_utils
from config.config import mypath, slash_clean
from db.db import tbl_game7
from functions.functions import dirinDir, clean_word
import random

from app import db


def game7(story_name):


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
    if g_number > 0:
        score = (g_wins / g_number) * 100

    if g_number >= 10 and g_wins < 6:
        flash('Game Over! You could better!Try better next time! Your Score is:' + str(score), 'danger')
        return redirect(url_for('app.home'))

    elif g_number >= 10 and g_wins > 5 and g_wins < 8:
        flash('Game Over! Your doing good job! proceed training !Your Score is:' + str(score), 'success')
        return redirect(url_for('app.home'))

    elif g_number >= 10 and g_wins > 7:
        flash('Game Over! Your are Excellent! Try advanced level!' + str(score), 'success')
        return redirect(url_for('app.home'))
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
        flash('Right answer you got 1 point', 'success')
        wins+=1
    else:
        item = tbl_game7(score=0, user_id=uid, question=name)
        flash('bad answer you got 0 point', 'danger')
    db.session.add(item)
    db.session.commit()
    g_number+=1
    values_s=[name,g_number,wins]


    return redirect(url_for('app.generate_game7',  values=values_s))


