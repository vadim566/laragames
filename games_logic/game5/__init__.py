from flask import render_template, request, flash, redirect, url_for

from SVN.trunk.Code.Python import lara_utils
from config.config import mypath, slash_clean
from db.db import tbl_game5
from functions.functions import dirinDir
import random

from app import db

def generate_game5(story_name, file=None):


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
    rand_i = rand_index
    fake_answer = []
    for i in range(4):
        rand_i = random.sample(range(0, size_of_story), 4)

    true_match = [sentance[rand_index], sounds[rand_index]]
    bad_match = [sounds[rand_i[0]], sounds[rand_i[1]], sounds[rand_i[2]], sounds[rand_i[3]]]

    print(true_match)
    print(bad_match)

    return render_template('game5_template.html', t_answer=true_match[1], question=true_match[0],
                           fake_answer_0=bad_match[0], fake_answer_1=bad_match[1], fake_answer_2=bad_match[2],
                           fake_answer_3=bad_match[3], name=story_name)

def submit_g5(option=0,default_value=0):

    name = request.form.get('storyname', default_value)
    option = request.form.get('option', default_value)

    uid = request.form.get('uid', default_value)

    print("name: ", name)
    print("option: ", option)

    if option == '1':
        item = tbl_game5(score=1, user_id=uid,question=name)
        flash('Right answer', 'success')
    else:
        item = tbl_game5(score=0, user_id=uid,question=name)
        flash('bad answer', 'danger')
    db.session.add(item)
    db.session.commit()

    return redirect(url_for('app.generate_game5', story_name=name))