

# DB init
from datetime import datetime

from flask_login import UserMixin

from functions.functions import get_language
from lara_games_app import login_manager, db


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


