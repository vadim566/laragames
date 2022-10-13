
![Logo](https://i.ibb.co/br8Ztt8/logo-PSDtransferd.png)

#### heroko deployment not working because of exceeding the 500mb, 
#### Who ever want to see a demo should visit (tempory dns)  
#### http://health-elb-2092252127.us-east-1.elb.amazonaws.com/


# LARAGAME



LARA is a platform of studying L1 and L2 community resource
## Roadmap
## Done 
- Learn importing LARA files
- Learn creating abstract html from LARA
- routing to lara story with flask
- Building games
- Building backend
- Building frontend
- creating register/login system
- creating progression dashboard 
- creating level badges

## Future Features
- Improving UI/UX
- creating more Games based on pictures
- working as distrbuted system
- maintaing the full list of working games in LARA
- phrase failed summoning for re training
- bug fixing inside game to handles only words without symbols

## Features

- Learn language in a fun way
- Progression in learning
- Many diffuclties for range of users
- Supporting language that LARA Supporting
- Generating games for each language


## Toplogy
The main content is imported from main LARA SVN , that store each story.
* Because of our system using all content created by LARA original users we will need to semi/auto importsome of these stories into our rep.
* In back end each game will accses file dirs where each story is built and will be generated from the files inside the file dir
* The score of each registrated player will be stored inside the SQL DB
* The front end will be created from JINJA templates based on js,html ,css
![App Screenshot](https://i.ibb.co/V30fPjh/lara-toplogy.png)

## Use case/Sequence diagram
each player can accses into the system whenever he is registrated or not.
* The 3 difficulties  levels  for each language to play game
* Each story can be read as it was on original lara
* In each level there's 3 games of selected language training
* If the user is registrated so his score will be stored in the db and it will show in dashboard and will have also badges and level progress

![App Screenshot](https://i.ibb.co/RTk680Z/LARAGAMES.png)


## DB ERD
Each game will have its own  db when all the games tables connected to user tables,
all queries based on selecting the PK of the user and taking the matching rows from each game table.
![App Screenshot](https://i.ibb.co/Sw8sRTJ/erdlaragames.png)


## Local Installation
1. clone this rep from git , make sure that requirements.txt inside the folder

2. Create venv Install all python modules into venv with cmd/bash

```bash
cd [folder that you cloned the project to]

python -m venv venv

.\venv\Scripts\activate.bat

pip install -r requirements.txt
```

## Run Locally

Run app.py with python After installation
```bash
Python .\app.py
```
## Deployment into heroku

1. create inside the main folder file named Procfile,
and save inside it

```bash
  web: gunicorn app:app
```

2. make sure u installed heroku extention, open bash/cmd and login into heroku

```bash
  heroku login
```

3. After that create a new project in heroku

```bash
  heroku create projectName
```
4. Push the rep into heroku with git

```bash
   git heroku push master
```
## Deployment into AWS
1.create EC2 instance using centos7

2.configure EC2 machine 

3.Use the next script as USER DATA in EC2
```bash
#!/bin/bash

#deployment of LARA_GAMES as Virtual machine

#default os centos7

GIT_URL=https://github.com/vadim566/laragames.git  #git url
DIR_NAME=laragames


yum --help #check if centos
if [ $? -eq 0 ]
then
	#general centos updates
	sudo yum update -y
	
	#install git
	sudo yum install git -y
	
	##get git latest version
	git clone $GIT_URL
	
	##get python
	sudo yum install python3 -y

	##create python virtual enviorment
	cd $DIR_NAME/
 	sudo python3 -m venv venv
	source venv/bin/activate
	
	##upgrade pip
	pip install --upgrade pip
	pip install -r requirements.txt
	
	##run app
	source venv/bin/activate
	python3 lara_games_app.py
else
	echo "The script built for centos7"
	
fi
```
4. Add Availability script inside laragames dir
```bash
vi HA_python3.sh
```
```bash
#!/bin/bash
##get the lara_games_app.py from process ps aux
pid_info=` ps aux|grep python3|grep lara_games_app.py|awk '{print $12}'`
#python_expected="/laragames/lara_games_app.py"
pid_name="app.py"

##if there is process name running 
if [[ $pid_info = $pid_name ]]
then
        echo 'works'
else##if not runing then start ve env and start app
        echo 'not works'
        echo 'starting virtual env'
        source /laragames/venv/bin/activate
        cd /laragames/
        python3 lara_games_app.py

fi
```
5.Go into root user and schedule the health check every 1 min
```bash
crontab -e
```
```bash
#MM HH DOM mm DOW
* * * * * /laragames/HA_python3.sh &>> /var/log/monit_apppy.log
```

## Contributing and adding more games

Contributions are always welcome!

If u want to add more games , you should follow the next steps 



## Adding games
1.Create tbl_db in sql_aclhemy for tracking stats of each user,
first append CLASS user and add the next line:(swap #X# in game name)
```python
class User(db.Model, UserMixin):
.
.
.
game#X#Rel = db.relationship('tbl_game#X#', backref='author', lazy=True)
```
* after it create new tbl:
```python
class tbl_game#X#(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    score=db.Column(db.Integer,default=0)
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)

    counter=db.Column(db.Integer,default=1)
    date_created = db.Column(db.DateTime,nullable=False, default=datetime.utcnow)
```
2.just add a new route and render a template
change the #X# below

```python
@app.route('/game#X#/<story_name>', methods=['GET'])
def generate_game#X#(story_name, file=None):
#logics
return render_template('game#X#_template.html' )


#let you browse the story and etc
@app.route('/game#X#/<story_name>/<path:filename>', methods=['GET','POST'])
def loading_file_pic_g#X#(filename,story_name):
 metaDataAudioDir = mypath + slash_clean + story_name + slash_clean+'audio'+slash_clean
    audioVersions = dirinDir(metaDataAudioDir)
return send_from_directory(metaDataAudioDir+slash_clean+audioVersions[0], filename)

#make sure you creating submit route

@app.route('/game#X#Submit/', methods=['GET','POST'])
def submit_g#X#():

    default_value=0
    name=request.form.get('storyname',default_value)
    option=request.form.get('option',default_value)
    answer=request.form.get('answer',default_value)
    uid=request.form.get('uid',default_value)

    print("name: ",name)
    print("option: " ,option)
    print("answer: ",answer)


    if option == answer:
        item=tbl_game#X#(score=1,user_id=uid)
        flash('Right answer','success')
    else:
        item=tbl_game#X#(score=0, user_id=uid)
        flash('bad answer', 'danger')
    db.session.add(item)
    db.session.commit()
    return redirect(url_for('generate_game#X#',story_name=name))

```


## Environment Variables

To run this project, you will need to install the requirement file as it describe in install section


## Screenshots

* Story Selecting Page
* ![App Screenshot](https://i.ibb.co/sFdyKJQ/1.jpg)

* Matching word to voice game
* ![App Screenshot](https://i.ibb.co/fxghDxJ/2.jpg)


* Filling 2 word to voice game
* ![App Screenshot](https://i.ibb.co/7VQMxS0/3.jpg)

* login page
* ![App Screenshot](https://i.ibb.co/wSYjwHy/4.jpg)

* Registeration
* ![App Screenshot](https://i.ibb.co/xJJ84J3/5.jpg)

* Bad answer reaction inside games
* ![App Screenshot](https://i.ibb.co/zPkzsdm/6.jpg)

* Right answer reaction inside games
* ![App Screenshot](https://i.ibb.co/tJfnRnV/7.jpg)

* Dashboard and level progression with badges
* ![App Screenshot](https://i.ibb.co/V9L3KSL/8.jpg)


## Appendix

#### Original LARA
https://www.issco.unige.ch/en/research/projects/callector/LARADoc/build/html/reader_portal.html

#### LARA SVN
https://sourceforge.net/projects/callector-lara/
