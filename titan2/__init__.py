#Initialize Flask & SQL, then Import Forms
import os
from flask import Flask, Markup
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)

#Set Configurations for Secret Key and Database (SqlAlchemy)
app.config['SECRET_KEY'] = '8675309JeNnY0'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#Set Value for Database
db = SQLAlchemy(app)
Migrate(app,db)
#Allow for Encryption/Decryption
bcrypt = Bcrypt(app)

#Set Login Manager to allow user logins
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from titan2 import routes
