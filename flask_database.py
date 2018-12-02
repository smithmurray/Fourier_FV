from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pymssql://FE-User:Fourier.01@41.203.23.36/PGAluminium'

app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECURITY_PASSWORD_SALT"] = 'my_precious_two'
db = SQLAlchemy(app)

SQLALCHEMY_TRACK_MODIFICATIONS = False