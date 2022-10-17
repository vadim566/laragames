import random

from flask import Flask, render_template, send_from_directory, redirect, url_for, flash, request, Blueprint
# crypt passwords
import operator
from flask_login import LoginManager, login_user, current_user, logout_user, login_required, UserMixin
from flask import render_template, request, Blueprint

from app import db ,bcrypt
from db.db import User
from forms.forms import RegistrationForm, LoginForm
from functions.functions import get_language, analayzeGame, dirinDir, filesinDir, getWords, clean_word, \
    loading_file_pic, story_folder_data, split_values
from config.config import language, onlydir, main_page_hyper, content_loc, slash, corpus_suffix, html_path, \
    index_folder_sufix, folder_sufix, hyper_page_html, multimedia_folder, compiled_loc, alphaBet, mypath, slash_clean
import functions
# db
from flask_sqlalchemy import SQLAlchemy
# forms
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError




import SVN.trunk.Code.Python.lara_utils as lara_utils

# load the languages thats availble in file systems before any request to the site
get_language()



app=Blueprint('app',__name__)

@app.route('/home')
@app.route('/')
def home():
    lg=[]
    dic_lang=dict(zip(onlydir,language))
    for lan in set(language):
        lg.append([])
        for key, val in dic_lang.items():
            if val == lan:
                lg[-1].append(key)
    tmp_lg=list(set(language))
    stories_per_lang=zip(lg,tmp_lg)
    stories_per_lang=list(stories_per_lang)
    stories_per_lang= sorted(stories_per_lang, key=operator.itemgetter(-1))
    return render_template('index.html', content=stories_per_lang, lang=tmp_lg, link_html=main_page_hyper)


# registration and login
@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('app.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('app.login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('app.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('app.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('app.home'))


@app.route("/account")
@login_required
def account():
    from dashboard import account_dashboard as create_board
    return create_board()

@app.route('/index/<name>', methods=['GET', 'POST'])
def index(name):
    return story_folder_data(name)


@app.route('/<path:story_name>/<name>')
def surf(name, story_name):
    lema = '_lemmas'

    if ".html" in name or ".css" in name or ".js" in name:
        return send_from_directory(html_path + story_name + index_folder_sufix + slash, name)
    else:
        return send_from_directory(html_path + story_name + folder_sufix + slash, hyper_page_html)


@app.route('/<story_name>/multimedia/<path:filename>', methods=['GET'])
def loading_file(filename, story_name):
    return send_from_directory(html_path + slash + story_name + index_folder_sufix + multimedia_folder + slash,
                               filename)



@app.route('/game4/<values>', methods=['GET'])
def generate_game4(values):
    values=split_values(values)
    from games_logic.game4 import generate_game4 as game4
    return game4(values[0],values[1],values[2])
    # return render_template('game4_template.html',meta_dic=meta_dic,alphabet=alphaBet,name=story_name)


@app.route('/game4/<story_name>/<path:filename>', methods=['GET', 'POST'])
def loading_file_pic_g4(filename, story_name):
    return loading_file_pic(filename, story_name)


@app.route('/game4Submit/<values>', methods=['GET', 'POST'])
def submit_g4(values):
    option = 0
    answer = 0
    default_value = 0
    values=split_values(values)
    from games_logic.game4 import submit_g4 as submit4
    return submit4(option, answer, default_value,values[1],values[2])

@app.route('/fetch_game4/<values>', methods=['GET', 'POST'])
def fetch_g4(values):
    print(values)
    values=split_values(values)
    from games_logic.game4 import fetch_game4 as f_game4
    return f_game4(values[0],values[1],values[2])


"""GAME 5"""

@app.route('/game5/<values>', methods=['GET'])
def generate_game5(values):
    values = split_values(values)
    from games_logic.game5 import generate_game5 as game5
    return game5(values[0],values[1],values[2])


@app.route('/game5/index.html', methods=['GET'])
def g4_back_home():
    return redirect(url_for('app.home'))


@app.route('/game5/<story_name>/<path:filename>', methods=['GET', 'POST'])
def loading_file_pic_g5(filename, story_name):
    return loading_file_pic(filename, story_name)


@app.route('/game5/index.html', methods=['GET'])
def g5_back_home():
    return redirect(url_for('app.home'))


@app.route('/game5Submit/<values>', methods=['GET', 'POST'])
def submit_g5(values):

    option = 0
    answer = 0
    default_value = 0
    values=split_values(values)
    from games_logic.game5 import submit_g5 as submit5
    return submit5(option, answer, default_value,values[1],values[2])



"""GAME 6"""
@app.route('/game6/<values>', methods=['GET'])
def generate_game6(values, file=None):
    values = split_values(values)
    from games_logic.game6 import generate_game6 as game6
    return game6(values[0], values[1], values[2])

@app.route('/game6/<story_name>/<path:filename>', methods=['GET', 'POST'])
def loading_file_pic_g6(filename, story_name):
    return loading_file_pic(filename, story_name)

@app.route('/game6Submit/<values>', methods=['GET', 'POST'])
def submit_g6(values):
    option = 0
    answer = 0
    default_value = 0
    from games_logic.game6 import submit_g6 as submit6
    values = split_values(values)
    return submit6(option, answer, default_value,values[1],values[2])



"""GAME 7"""


@app.route('/game7/<values>', methods=['GET'])
def generate_game7(values, file=None):
    values = split_values(values)
    from games_logic.game7 import generate_game7 as game7
    return game7(values[0], values[1], values[2])

@app.route('/game7/<story_name>/<path:filename>', methods=['GET', 'POST'])
def loading_file_pic_g7(filename, story_name):
    return loading_file_pic(filename, story_name)


@app.route('/game7Submit/<values>', methods=['GET', 'POST'])
def submit_g7(values):
    option = 0
    answer = 0
    default_value = 0
    from games_logic.game7 import submit_g7 as submit7
    values = split_values(values)
    return submit7(option, answer, default_value, values[1], values[2])


"""GAME 8"""


@app.route('/game8/<values>', methods=['GET'])
def generate_game8 (values, file=None):
    values = split_values(values)
    from games_logic.game8 import generate_game8 as game8
    return game8(values[0], values[1], values[2])


@app.route('/game8/<story_name>/<path:filename>', methods=['GET', 'POST'])
def loading_file_pic_g8(filename, story_name):
    return loading_file_pic(filename, story_name)


@app.route('/game8Submit/<values>', methods=['GET', 'POST'])
def submit_g8(values):
    option = 0
    answer = 0
    default_value = 0
    from games_logic.game8 import submit_g8 as submit8
    values = split_values(values)
    return submit8(option, answer, default_value, values[1], values[2])


"""GAME 9"""


@app.route('/game9/<values>', methods=['GET'])
def generate_game9(values, file=None):
    values = split_values(values)
    from games_logic.game9 import generate_game9 as game9
    return game9(values[0], values[1], values[2])


@app.route('/game9/<story_name>/<path:filename>', methods=['GET', 'POST'])
def loading_file_pic_g9(filename, story_name):
    return loading_file_pic(filename, story_name)


@app.route('/game9Submit//<values>', methods=['GET', 'POST'])
def submit_g9(values):
    option = 0
    answer = 0
    default_value = 0
    from games_logic.game9 import submit_g9 as submit9
    values = split_values(values)
    return submit9(option, answer, default_value, values[1], values[2])



"""GAME 10"""


@app.route('/game10/<values>', methods=['GET'])
def generate_game10(values, file=None):
    values = split_values(values)
    from games_logic.game10 import generate_game10 as game10
    return game10(values[0], values[1], values[2])

@app.route('/game10/<story_name>/<path:filename>', methods=['GET', 'POST'])
def loading_file_pic_g10(filename, story_name):
    return loading_file_pic(filename, story_name)


@app.route('/game10Submit/<values>', methods=['GET', 'POST'])
def submit_g10(values):
    option = 0
    answer = 0
    default_value = 0
    from games_logic.game10 import submit_g10 as submit10
    values = split_values(values)
    return submit10(option, answer, default_value, values[1], values[2])


"""GAME 11"""


@app.route('/game11/<values>', methods=['GET'])
def generate_game11(values):
    from games_logic.game11 import generate_game11 as game11
    values = split_values(values)
    return game11(values[0], values[1], values[2])

@app.route('/game11/<story_name>/<path:filename>', methods=['GET', 'POST'])
def loading_file_pic_g11(filename, story_name):
    return loading_file_pic(filename, story_name)


@app.route('/game11Submit/<values>', methods=['GET', 'POST'])
def submit_g11(values):
    option = 0
    answer = 0
    default_value = 0
    from games_logic.game11 import submit_g11 as submit11
    values = split_values(values)
    return submit11(option, answer, default_value, values[1], values[2])

"""GAME 12"""


@app.route('/game12/<values>', methods=['GET'])
def generate_game12(values):
    from games_logic.game12 import generate_game12 as game12
    values = split_values(values)

    return game12(values[0], values[1], values[2])


@app.route('/game12/<story_name>/<path:filename>', methods=['GET', 'POST'])
def loading_file_pic_g12(filename, story_name):
    return loading_file_pic(filename, story_name)


@app.route('/game12Submit/<values>', methods=['GET', 'POST'])
def submit_g12(values):
    option = 0
    answer = 0
    default_value = 0
    from games_logic.game12 import submit_g12 as submit12
    values = split_values(values)
    return submit12(option, answer, values[1], values[2])
