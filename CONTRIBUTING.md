
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

