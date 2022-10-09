
import random
from datetime import datetime
from os import listdir
from os.path import join, isdir, isfile

from flask import Flask, render_template, send_from_directory, redirect, url_for, flash, request
# crypt passwords
from flask_bcrypt import bcrypt, Bcrypt
from flask_login import LoginManager, login_user, current_user, logout_user, login_required, UserMixin
# db
from flask_sqlalchemy import SQLAlchemy
# forms
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

import SVN.trunk.Code.Python.lara_utils as lara_utils

# to install
# pip install requests
# pip install python-docx
# pip install nltk
# compiled from lara -html folder

'''init vars'''
# define LARA
LARA = './SVN/trunk/'
mypath = LARA + 'Content'
compiled_path = LARA + 'Content'
onlydir = [f for f in listdir(mypath) if isdir(join(mypath, f))]
global language

html_path = './SVN/trunk/compiled/'
content_loc = './SVN/trunk/Content/'
corpus_suffix = '/corpus/local_config.json'
lara_builder = LARA + 'Code/Python/lara_run.py '
lara_builder_creator = 'word_pages '
compiled_loc = LARA + 'compiled/'
folder_sufix = 'vocabpages'
index_folder_sufix = 'vocabpages'
multimedia_folder = "/multimedia/"
py_ver = 'python '
py_ver_w = 'python'
main_page_hyper = '_from_abstract_htmlvocabpages/_hyperlinked_text_.html'
hyper_page_html = '_hyperlinked_text_.html'
pic_loc = html_path + 'pic'
slash = '/'
slash_clean = '/'

'''FLASK app config for _init'''
app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

"""TODO extarct from meta data JASON the right language"""
alphaBet = "'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','r','s','t','u','v','x','w','z','a','á','b','d','ð','e','é','f','g','h','i','í','j','k','l','m','n','o','ó','p','r','s','t','u','ú','v','x','y','ý','þ','æ','ö','ð'"

'''functions'''

def clean_word(word :str) ->str:
    clean_word = "".join(c for c in word if c.isalpha())
    return clean_word


# get the language of each story
def get_language():
    global language
    language = []
    for s in onlydir:
        conf_file = compiled_path + slash + str(s) + str(corpus_suffix)
        language.append(lara_utils.read_json_file(conf_file)['language'])


# returning a list with files in dir_path
def filesinDir(dir_path):
    try:
        files_in_dir = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]
    except:
        "something wrong with the directory, put in the full path"
    finally:
        return files_in_dir


# returning a list with sub dir to dir_path
def dirinDir(dir_path):
    try:
        dir_in_dir = [f for f in listdir(dir_path) if isdir(join(dir_path, f))]
    except:
        "something wrong with the directory, put in the full path"
    finally:
        return dir_in_dir


def getWords(dir_path, prefix_word):
    try:
        files_in_dir = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]
    except:
        "something wrong with the directory, put in the full path"
    finally:
        word_list = []
        for file_name in files_in_dir:
            if prefix_word in file_name:
                word = file_name.split('_')[1].split('.')[0]
                word_list.append(word)
        return word_list


def calculate_rate(gametbl):
    total_games = len(gametbl)
    win = 0
    for item in gametbl:
        win += item.score
    return win / total_games


'''forms'''


# forms
class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


def game_lists(game):
    date_list = ['']
    game_ct = ['']
    wins_ct = ['']
    for g in game:

        if (date_list[-1] == str(g.date_created.date())):
            game_ct[-1] = game_ct[-1] + 1
            wins_ct[-1] = wins_ct[-1] + g.score
        else:
            date_list.append(str(g.date_created.date()))
            game_ct.append(1)
            wins_ct.append(g.score)
    return date_list, game_ct, wins_ct


def analayzeGame(game, wr):
    if (len(game) > 0):
        wr[0] = calculate_rate(game)
        dates, games_perDay, wins_perDay = game_lists(game)
        wr.append(dates)
        wr.append(games_perDay)
        wr.append(wins_perDay)
    else:
        wr.append(str(datetime.now().date()))
        wr.append(['',0])
        wr.append(['',0])

    return wr


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


'''db tables'''


# DB init
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    game4Rel = db.relationship('tbl_game4', backref='author', lazy=True)
    game5Rel = db.relationship('tbl_game5', backref='author', lazy=True)
    game6Rel = db.relationship('tbl_game6', backref='author', lazy=True)
    game7Rel = db.relationship('tbl_game7', backref='author', lazy=True)
    game8Rel = db.relationship('tbl_game8', backref='author', lazy=True)
    game9Rel = db.relationship('tbl_game9', backref='author', lazy=True)
    game10Rel = db.relationship('tbl_game10', backref='author', lazy=True)
    game11Rel = db.relationship('tbl_game11', backref='author', lazy=True)
    game12Rel = db.relationship('tbl_game12', backref='author', lazy=True)

    def __repr__(self):
        return '<User %r>' % self.username


class tbl_game4(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question=db.Column(db.String)
    counter = db.Column(db.Integer, default=1)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return f"game 4('{self.score}', '{self.date_created}')"


class tbl_game5(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question = db.Column(db.String, nullable=False)
    counter = db.Column(db.Integer, default=1)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"game 5('{self.score}', '{self.date_created}')"


class tbl_game6(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question = db.Column(db.String)
    counter = db.Column(db.Integer, default=1)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"game 6('{self.score}', '{self.date_created}')"


class tbl_game7(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question = db.Column(db.String)
    counter = db.Column(db.Integer, default=1)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"game 7('{self.score}', '{self.date_created}')"


class tbl_game8(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question = db.Column(db.String)
    counter = db.Column(db.Integer, default=1)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"game 8('{self.score}', '{self.date_created}')"


class tbl_game9(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question = db.Column(db.String)
    counter = db.Column(db.Integer, default=1)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"game 9('{self.score}', '{self.date_created}')"


class tbl_game10(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question = db.Column(db.String)
    counter = db.Column(db.Integer, default=1)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"game 10('{self.score}', '{self.date_created}')"


class tbl_game11(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question = db.Column(db.String)
    counter = db.Column(db.Integer, default=1)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"game 11('{self.score}', '{self.date_created}')"


class tbl_game12(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question = db.Column(db.String)
    counter = db.Column(db.Integer, default=1)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"game 11('{self.score}', '{self.date_created}')"


# load the language before any request to the site
get_language()



# routing


@app.route('/home')
@app.route('/')
def home():
    return render_template('index.html', content=zip(onlydir, language), lang=language, link_html=main_page_hyper)


# registration and login
@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/account")
@login_required
def account():
    user = User.query.filter_by(id=current_user.id).first()

    games = []
    games.append(user.game4Rel)
    games.append(user.game5Rel)
    games.append(user.game6Rel)
    games.append(user.game7Rel)
    games.append(user.game8Rel)
    games.append(user.game9Rel)
    games.append(user.game10Rel)
    games.append(user.game11Rel)
    games.append(user.game12Rel)
    total_games=0
    total_wins=0
    game_sets = []

    for i in range(len(games)):
        game_sets.append([0])
        game_sets[i] = analayzeGame(games[i], game_sets[i])
        game_sets[i].append(str(i))
        total_games=total_games+game_sets[i][2][1]#add the wins  per day
        total_wins=total_wins+game_sets[i][3][1]

    levels=[0,10,20,50,100,200,400,800,1000,1500,2000]
    total_exprience=(total_games-total_wins)*0.3+total_wins
    exprience_next_level=0
    level=int(total_exprience)
    for i in range(len(levels)):
        if level < levels[i] :
            level=i
            exprience_next_level=levels[i]-total_exprience
            break;

    print(total_wins)
    return render_template('account.html', title='Account', games=game_sets, wins=total_wins ,gametotal=total_games,p_level=level,exp_level=exprience_next_level)


@app.route('/index/<name>', methods=['GET', 'POST'])
def index(name):
    flag = 0

    # compile only if it is not existed in compiled folder
    for dir in dirinDir(content_loc):
        if name in dir:
            if '_hyperlinked_text_.html' in filesinDir(content_loc + slash + dir):
                flag = 1
                break
        else:
            pass
    if flag == 0:
        ful_loc = content_loc + name + corpus_suffix
        #  try:
        # os.system("python "+ lara_builder + lara_builder_creator + ful_loc)
        #  except:
        #  subprocess.call(py_ver+ lara_builder + lara_builder_creator + ful_loc)
        # finally:
        return redirect(url_for('surf', story_name=name, name=name))


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


@app.route('/game1/<story_name>', methods=['GET'])
def generate_game1(story_name):
    story_dir = compiled_loc + story_name + folder_sufix
    words = getWords(story_dir, 'word_')
    # TODO find NOUNS
    return render_template('game1_template.html', alphabet=alphaBet, alphabet_full=alphaBet, words1=words)
    # return render_template('game1_template.html', alphabet=alphaBet,alphabet_full=alphaBet,words1=words[0:3],words2=words[4:7],words3=words[8:11],words4=words[12:15])


@app.route('/game1/<path:filename>', methods=['GET'])
def loading_file_pic_g1(filename):
    return send_from_directory(html_path, filename)


@app.route('/game1/index.html', methods=['GET'])
def g1_back_home():
    return redirect(url_for('home'))


@app.route('/game2/<story_name>', methods=['GET'])
def generate_game2(story_name):
    story_dir = compiled_loc + story_name + folder_sufix
    words = getWords(story_dir, 'word_')

    # TODO find NOUNS
    return render_template('game2_template.html', words1=words[:4], words2=words[4:8], words3=words[3:10],
                           words4=words[4:11])


@app.route('/game2/<path:filename>', methods=['GET'])
def loading_file_pic_g2(filename):
    return send_from_directory(html_path, filename)


@app.route('/game2/index.html', methods=['GET'])
def g2_back_home():
    return redirect(url_for('home'))


"""GAME 3"""


@app.route('/game3/<story_name>', methods=['GET', 'POST'])
def generate_game3(story_name):
    story_dir = compiled_loc + story_name + folder_sufix
    words = getWords(story_dir, 'word_')

    # TODO find NOUNS
    return render_template('game3_template.html', alphabet=alphaBet, alphabet_full=alphaBet, words1=words)


@app.route('/game3/<path:filename>', methods=['GET'])
def loading_file_pic_g3(filename):
    return send_from_directory(html_path, filename)


@app.route('/game3/index.html', methods=['GET'])
def g3_back_home():
    return redirect(url_for('home'))


"""IMAGE SCRAPER"""

"""
@app.route('/game3/<story_name>',methods=['GET'])
def generate_game3(story_name):
    story_dir=compiled_loc + story_name+folder_sufix
    words=getWords(story_dir,'word_')
    #TODO find NOUNS
    #get_pic(words)#image scrapper
    return render_template('game3_template.html',words=words)

@app.route('/game3/<pic_name>/<path:filename>', methods=['GET'])
def loading_file_pic_g3(filename,pic_name):
    return send_from_directory(pic_loc+'/'+pic_name,filename)

"""
"""pic scrapper"""
'''def get_pic(words):
    webdriver_path = os.path.normpath(os.path.join(os.getcwd(), 'webdriver', webdriver_executable()))
    image_path = pic_loc

    # Add new search key into array ["cat","t-shirt","apple","orange","pear","fish"]
    search_keys = words

    # Parameters
    number_of_images = 1
    headless = False
    min_resolution = (0, 0)
    max_resolution = (9999, 9999)

    # Main program
    for search_key in search_keys:
        # TODO if its already exist then skip
        image_scrapper = GoogleImageScraper(webdriver_path, image_path, search_key, number_of_images, headless,
                                            min_resolution, max_resolution)
        image_urls = image_scrapper.find_image_urls()
        image_scrapper.save_images(image_urls)

    # Release resources
    del image_scrapper
'''
"""GAME 4"""


@app.route('/game4/<story_name>', methods=['GET'])
def generate_game4(story_name, file=None):
    # TODO add template game 4
    # TODO add redirecter to game4
    # TODO print build dic from metadata file
    # TODO get the metadata folder, random of all of these that inside the folder

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
    bad_match = [sentance[rand_i[0]], sentance[rand_i[1]], sentance[rand_i[2]], sentance[rand_i[3]]]

    print(true_match)
    print(bad_match)

    return render_template('game4_template.html', t_answer=true_match[0], question=true_match[1],
                           fake_answer_0=bad_match[0], fake_answer_1=bad_match[1], fake_answer_2=bad_match[2],
                           fake_answer_3=bad_match[3], name=story_name)
    # return render_template('game4_template.html',meta_dic=meta_dic,alphabet=alphaBet,name=story_name)


@app.route('/game4/<story_name>/<path:filename>', methods=['GET', 'POST'])
def loading_file_pic_g4(filename, story_name):
    metaDataAudioDir = mypath + slash_clean + story_name + slash_clean + 'audio' + slash_clean
    audioVersions = dirinDir(metaDataAudioDir)
    # TODO add expectaion
    # File = metaDataAudioDir + audioVersions[0] + '/'+filename
    return send_from_directory(metaDataAudioDir + slash_clean + audioVersions[0], filename)


@app.route('/game4Submit/', methods=['GET', 'POST'])
def submit_g4(option=0,answer=0,default_value=0):
    option = request.form.get('option')

    name = request.form.get('storyname', default_value)
    answer = request.form.get('answer', default_value)
    uid = request.form.get('uid', default_value)
    print("name: ", name)
    print("option: ", option)
    print("answer: ", answer)

    if option == answer:
        item = tbl_game4(score=1, user_id=uid,question=name)
        flash('Right answer', 'success')
    else:
        item = tbl_game4(score=0, user_id=uid,question=name)
        flash('bad answer', 'danger')
    db.session.add(item)
    db.session.commit()
    return redirect(url_for('generate_game4', story_name=name))


"""GAME 5"""


@app.route('/game5/<story_name>', methods=['GET'])
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


@app.route('/game4/index.html', methods=['GET'])
def g4_back_home():
    return redirect(url_for('home'))


@app.route('/game5/<story_name>/<path:filename>', methods=['GET', 'POST'])
def loading_file_pic_g5(filename, story_name):
    metaDataAudioDir = mypath + slash_clean + story_name + slash_clean + 'audio' + slash_clean
    audioVersions = dirinDir(metaDataAudioDir)
    # TODO add expectaion
    # File = metaDataAudioDir + audioVersions[0] + '/'+filename
    return send_from_directory(metaDataAudioDir + slash_clean + audioVersions[0], filename)


@app.route('/game5/index.html', methods=['GET'])
def g5_back_home():
    return redirect(url_for('home'))


@app.route('/game5Submit/', methods=['GET', 'POST'])
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

    return redirect(url_for('generate_game5', story_name=name))


"""GAME 6"""


@app.route('/game6/<story_name>', methods=['GET'])
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
        bad_words.append(bad_words_arr[bad_rand_ct[0]])  # bad answer

    # send the right missing word and wrong words

    print("q:" + missing_sent)
    print("t_a:" + true_word)
    print(bad_words)

    return render_template('game6_template.html', t_answer=true_word, question0=missing_sent, question1=true_match[1],
                           fake_answer_0=bad_words[0], fake_answer_1=bad_words[1], fake_answer_2=bad_words[2],
                           fake_answer_3=bad_words[3], name=story_name)


@app.route('/game6/<story_name>/<path:filename>', methods=['GET', 'POST'])
def loading_file_pic_g6(filename, story_name):
    metaDataAudioDir = mypath + slash_clean + story_name + slash_clean + 'audio' + slash_clean
    audioVersions = dirinDir(metaDataAudioDir)
    # TODO add expectaion
    # File = metaDataAudioDir + audioVersions[0] + '/'+filename
    return send_from_directory(metaDataAudioDir + slash_clean + audioVersions[0], filename)


@app.route('/game6Submit/', methods=['GET', 'POST'])
def submit_g6(option=0,answer=0,default_value=0):

    name = request.form.get('storyname', default_value)
    option = request.form.get('option', default_value)
    answer = request.form.get('answer', default_value)
    uid = request.form.get('uid', default_value)

    print("name: ", name)
    print("option: ", option)
    print("answer: ", answer)

    if option == answer:
        item = tbl_game6(score=1, user_id=uid,question=name)
        flash('Right answer', 'success')
    else:
        item = tbl_game6(score=0, user_id=uid,question=name)
        flash('bad answer', 'danger')
    db.session.add(item)
    db.session.commit()
    return redirect(url_for('generate_game6', story_name=name))


"""GAME 7"""


@app.route('/game7/<story_name>', methods=['GET'])
def generate_game7(story_name, file=None):


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

    return render_template('game7_template.html', t_answer=true_word, question0=missing_sent, question1=true_match[1], name=story_name)


@app.route('/game7/<story_name>/<path:filename>', methods=['GET', 'POST'])
def loading_file_pic_g7(filename, story_name):
    metaDataAudioDir = mypath + slash_clean + story_name + slash_clean + 'audio' + slash_clean
    audioVersions = dirinDir(metaDataAudioDir)
    # TODO add expectaion
    # File = metaDataAudioDir + audioVersions[0] + '/'+filename
    return send_from_directory(metaDataAudioDir + slash_clean + audioVersions[0], filename)


@app.route('/game7Submit/', methods=['GET', 'POST'])
def submit_g7(option=0,answer=0,default_value=0):

    name = request.form.get('storyname', default_value)
    option = request.form.get('option', default_value)
    answer = request.form.get('answer', default_value)
    uid = request.form.get('uid', default_value)

    print("name: ", name)
    print("option: ", option)
    print("answer: ", answer)

    if option == answer:
        item = tbl_game7(score=1, user_id=uid,question=name)
        flash('Right answer', 'success')
    else:
        item = tbl_game7(score=0, user_id=uid,question=name)
        flash('bad answer', 'danger')
    db.session.add(item)
    db.session.commit()
    return redirect(url_for('generate_game7', story_name=name))


"""GAME 8"""


@app.route('/game8/<story_name>', methods=['GET'])
def generate_game8(story_name, file=None):


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

    # split the sentance
    split_setance = true_match[0].split(" ", 4)
    print(split_setance)
    random.shuffle(split_setance)

    return render_template('game8_template.html', t_answer=true_match[0], question1=true_match[1],
                           split_a0=split_setance[0], split_a1=split_setance[1], split_a2=split_setance[2],
                           split_a3=split_setance[3], split_a4=split_setance[4], name=story_name)


@app.route('/game8/<story_name>/<path:filename>', methods=['GET', 'POST'])
def loading_file_pic_g8(filename, story_name):
    metaDataAudioDir = mypath + slash_clean + story_name + slash_clean + 'audio' + slash_clean
    audioVersions = dirinDir(metaDataAudioDir)
    # TODO add expectaion
    # File = metaDataAudioDir + audioVersions[0] + '/'+filename
    return send_from_directory(metaDataAudioDir + slash_clean + audioVersions[0], filename)


@app.route('/game8Submit/', methods=['GET', 'POST'])
def submit_g8(option=0,answer=0,default_value=0):

    name = request.form.get('storyname', default_value)
    option = request.form.get('option', default_value)
    answer = request.form.get('answer', default_value)
    uid = request.form.get('uid', default_value)

    print("name: ", name)
    print("option: ", option)
    print("answer: ", answer)

    if option == answer:
        item = tbl_game8(score=1, user_id=uid,question=name)
        flash('Right answer', 'success')
    else:
        item = tbl_game8(score=0, user_id=uid,question=name)
        flash('bad answer', 'danger')
    db.session.add(item)
    db.session.commit()
    return redirect(url_for('generate_game8', story_name=name))


"""GAME 9"""


@app.route('/game9/<story_name>', methods=['GET'])
def generate_game9(story_name, file=None):


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

    true_word = ['', '']
    # count the words in the sentance
    words_ct = true_match[0].count(" ")
    # pick random word between word set
    rand_ct = random.sample(range(1, words_ct), 1)
    # swap the word into [-------]
    words_arr = true_match[0].split(' ')
    # true_word=words_arr[rand_ct[0]]#right answer

    if rand_ct[0] + 1 >= words_ct and rand_ct[0] - 1 >= 0:
        true_word = words_arr[rand_ct[0] - 1] + ' ' + words_arr[rand_ct[0]]
        words_arr[rand_ct[0]] = "[--------]"
        words_arr[rand_ct[0] - 1] = "[--------]"
    else:
        true_word = words_arr[rand_ct[0]] + ' ' + words_arr[rand_ct[0] + 1]
        words_arr[rand_ct[0]] = "[--------]"
        words_arr[rand_ct[0] + 1] = "[--------]"

    missing_sent = " ".join(words_arr)  # missing sentance to question
    # pick random words from  the wrong sentance
    bad_words = []
    for i in range(len(bad_match)):
        bad_words_arr = bad_match[i].split(' ')
        words_ct = bad_match[i].count(" ")
        bad_rand_ct = random.sample(range(0, words_ct), 1)
        if bad_rand_ct[0] + 1 >= words_ct and bad_rand_ct[0] - 1 >= 0:
            bad_words.append(bad_words_arr[bad_rand_ct[0] - 1] + ' ' + bad_words_arr[bad_rand_ct[0]])
        else:
            bad_words.append(bad_words_arr[bad_rand_ct[0]] + ' ' + bad_words_arr[bad_rand_ct[0] + 1])

    # send the right missing word and wrong words

    print("q:" + missing_sent)
    print("t_a:" + true_word)
    print(bad_words)

    return render_template('game9_template.html', t_answer=true_word, question0=missing_sent, question1=true_match[1],
                           fake_answer_0=bad_words[0], fake_answer_1=bad_words[1], fake_answer_2=bad_words[2],
                           fake_answer_3=bad_words[3], name=story_name)


@app.route('/game9/<story_name>/<path:filename>', methods=['GET', 'POST'])
def loading_file_pic_g9(filename, story_name):
    metaDataAudioDir = mypath + slash_clean + story_name + slash_clean + 'audio' + slash_clean
    audioVersions = dirinDir(metaDataAudioDir)
    # TODO add expectaion
    # File = metaDataAudioDir + audioVersions[0] + '/'+filename
    return send_from_directory(metaDataAudioDir + slash_clean + audioVersions[0], filename)


@app.route('/game9Submit/', methods=['GET', 'POST'])
def submit_g9(option=0,answer=0,default_value=0):

    name = request.form.get('storyname', default_value)
    option = request.form.get('option', default_value)
    answer = request.form.get('answer', default_value)
    uid = request.form.get('uid', default_value)

    print("name: ", name)
    print("option: ", option)
    print("answer: ", answer)

    if option == answer:
        item = tbl_game9(score=1, user_id=uid,question=name)
        flash('Right answer', 'success')
    else:
        item = tbl_game9(score=0, user_id=uid,question=name)
        flash('bad answer', 'danger')
    db.session.add(item)
    db.session.commit()
    return redirect(url_for('generate_game9', story_name=name))


"""GAME 10"""


@app.route('/game10/<story_name>', methods=['GET'])
def generate_game10(story_name, file=None):


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

    true_word = words_arr[rand_ct[0]] + ',' + words_arr[rand_ct[1]]

    words_arr[rand_ct[0]] = "[--------]"
    words_arr[rand_ct[1]] = "[--------]"

    missing_sent = " ".join(words_arr)  # missing sentance to question
    # pick random words from  the wrong sentance
    bad_words = []
    for i in range(len(bad_match)):
        bad_words_arr = bad_match[i].split(' ')
        words_ct = bad_match[i].count(" ")
        bad_rand_ct = random.sample(range(0, words_ct), 2)

        bad_words.append(bad_words_arr[bad_rand_ct[0]] + ',' + bad_words_arr[bad_rand_ct[1]])

    # send the right missing word and wrong words

    print("q:" + missing_sent)
    print("t_a:" + true_word)
    print(bad_words)

    return render_template('game10_template.html', t_answer=true_word, question0=missing_sent, question1=true_match[1],
                           fake_answer_0=bad_words[0], fake_answer_1=bad_words[1], fake_answer_2=bad_words[2],
                           fake_answer_3=bad_words[3], name=story_name)


@app.route('/game10/<story_name>/<path:filename>', methods=['GET', 'POST'])
def loading_file_pic_g10(filename, story_name):
    metaDataAudioDir = mypath + slash_clean + story_name + slash_clean + 'audio' + slash_clean
    audioVersions = dirinDir(metaDataAudioDir)
    # TODO add expectaion
    # File = metaDataAudioDir + audioVersions[0] + '/'+filename
    return send_from_directory(metaDataAudioDir + slash_clean + audioVersions[0], filename)


@app.route('/game10Submit/', methods=['GET', 'POST'])
def submit_g10(option=0,answer=0,default_value=0):

    name = request.form.get('storyname', default_value)
    option = request.form.get('option', default_value)
    answer = request.form.get('answer', default_value)
    uid = request.form.get('uid', default_value)

    print("name: ", name)
    print("option: ", option)
    print("answer: ", answer)

    if option == answer:
        item = tbl_game10(score=1, user_id=uid,question=name)
        flash('Right answer', 'success')
    else:
        item = tbl_game10(score=0, user_id=uid,question=name)
        flash('bad answer', 'danger')
    db.session.add(item)
    db.session.commit()
    return redirect(url_for('generate_game10', story_name=name))


"""GAME 11"""


@app.route('/game11/<story_name>', methods=['GET'])
def generate_game11(story_name, file=None):


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


    return render_template('game11_template.html', t_answer0=true_word[0], t_answer1=true_word[1], question0=missing_sent, question1=true_match[1], name=story_name)


@app.route('/game11/<story_name>/<path:filename>', methods=['GET', 'POST'])
def loading_file_pic_g11(filename, story_name):
    metaDataAudioDir = mypath + slash_clean + story_name + slash_clean + 'audio' + slash_clean
    audioVersions = dirinDir(metaDataAudioDir)
    # TODO add expectaion
    # File = metaDataAudioDir + audioVersions[0] + '/'+filename
    return send_from_directory(metaDataAudioDir + slash_clean + audioVersions[0], filename)


@app.route('/game11Submit/', methods=['GET', 'POST'])
def submit_g11(option0=0,answer0=0,option1=0,answer1=0,default_value=0):

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

    if option0 == answer0 and option1 == answer1:
        item = tbl_game11(score=1, user_id=uid,question=name)
        flash('Right answer', 'success')
    else:
        item = tbl_game11(score=0, user_id=uid,question=name)
        flash('bad answer', 'danger')
    db.session.add(item)
    db.session.commit()
    return redirect(url_for('generate_game11', story_name=name))


"""GAME 12"""


@app.route('/game12/<story_name>', methods=['GET'])
def generate_game12(story_name, file=None):
    # TODO add template game 4
    # TODO add redirecter to game4
    # TODO print build dic from metadata file
    # TODO get the metadata folder, random of all of these that inside the folder

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

    true_match = [sentance[rand_index], sounds[rand_index]]
    bad_match = [sentance[rand_i[0]], sentance[rand_i[1]], sentance[rand_i[2]], sentance[rand_i[3]]]

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


    return render_template('game12_template.html', t_answer=true_word, question0=missing_sent, question1=true_match[1],  name=story_name)


@app.route('/game12/<story_name>/<path:filename>', methods=['GET', 'POST'])
def loading_file_pic_g12(filename, story_name):
    metaDataAudioDir = mypath + slash_clean + story_name + slash_clean + 'audio' + slash_clean
    audioVersions = dirinDir(metaDataAudioDir)
    # TODO add expectaion
    # File = metaDataAudioDir + audioVersions[0] + '/'+filename
    return send_from_directory(metaDataAudioDir + slash_clean + audioVersions[0], filename)


@app.route('/game12Submit/', methods=['GET', 'POST'])
def submit_g12(option=0,answer=0):
    default_value = 0
    name = request.form.get('storyname', default_value)
    option = request.form.get('option', default_value)
    answer = request.form.get('answer', default_value)
    uid = request.form.get('uid', default_value)

    print("name: ", name)
    print("option: ", option)
    print("answer: ", answer)

    if option == answer:
        item = tbl_game12(score=1, user_id=uid,question=name)
        flash('Right answer', 'success')
    else:
        item = tbl_game12(score=0, user_id=uid,question=name)
        flash('bad answer', 'danger')
    db.session.add(item)
    db.session.commit()
    return redirect(url_for('generate_game12', story_name=name))

def create_app():
    app.run(host='0.0.0.0', threaded=True)


def create_app_tests():
    app.run(host='127.0.0.1')

if __name__ == '__main__':
    create_app()
