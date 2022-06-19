from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_login import LoginManager
from cadpsr.funcoes import formata_data

UPLOAD_FOLDER = 'cadpsr/static/img_pessoas'
#ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


app = Flask(__name__)
app.config.from_object(Config)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
login.login_message = 'Ops! Para acessar o sistema é necessário efetuar o Login.'

#app.jinja_env.globals.update(formata_data=formata_data)
from cadpsr import routes
