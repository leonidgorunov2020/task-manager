from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager
from flask_migrate import Migrate
from flask_session import Session
from flask import Response


app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Remove the import of datetime from here

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:leo123@172.17.0.2/tm'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'super secret key'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
# Configure Flask-Login
login_manager.login_view = 'login'
migrate = Migrate(app, db)

from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

# Import datetime here
from datetime import datetime
