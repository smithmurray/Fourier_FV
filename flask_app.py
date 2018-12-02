import os
from flask import Flask, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from users import users_file
from report import report_file
from contracts import contracts_file
from datetime import timedelta
import datetime
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/static/reports'
ALLOWED_EXTENSIONS = set(['xlsx'])

app = Flask(__name__)

app.register_blueprint(users_file)
app.register_blueprint(contracts_file)
app.register_blueprint(report_file)

app.secret_key = ';jfjjmLFNDCJGRLsdlCHSA'
app.jinja_env.add_extension('jinja2.ext.loopcontrols')



app.config.update(
    DEBUG=True
)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pymssql://FE-User:Fourier.01@41.203.23.36/PGAluminium'
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECURITY_PASSWORD_SALT"] = 'my_precious_two'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy(app)

SQLALCHEMY_TRACK_MODIFICATIONS = False