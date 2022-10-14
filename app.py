

from flask import Flask
# crypt passwords
from flask_bcrypt import bcrypt, Bcrypt
from flask_login import LoginManager
# db
from flask_sqlalchemy import SQLAlchemy


from secret.secret import secret_db_key
db=SQLAlchemy()
bcrypt = Bcrypt()

login_manager = LoginManager()
login_manager.login_view = 'app.login'
login_manager.login_message_category = 'info'

def init_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = secret_db_key
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    return app


