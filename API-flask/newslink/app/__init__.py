from .config import config_by_name
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import Flask


app = Flask(__name__)
app.config.from_object(config_by_name['dev'])

db = SQLAlchemy(app)
migrate = Migrate(app, db)


from app import models, routes
