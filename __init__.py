from flask import Flask
from config import Config
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config.from_object(Config)
app.config['MONGO_URI'] = 'mongodb://drumrelab1:drumre2018@ds237363.mlab.com:37363/drumrelab1'
app.config['MONGO_DBNAME'] = 'drumrelab1'
lm = LoginManager(app)
lm.login_view = 'login'
lm.init_app(app) # ?????
bootstrap = Bootstrap(app)
baza = PyMongo(app)

