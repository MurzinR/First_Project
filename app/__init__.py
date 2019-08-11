import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from rq import Worker, Queue

from config import Config
from redis import Redis

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
app.redis = Redis.from_url(app.config['REDIS_URL'])
app.task_queue = Queue('asynctasks-tasks', connection=app.redis)
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/asynctasks.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('AsyncTasks')

from app import models, routes, errors
