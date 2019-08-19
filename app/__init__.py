import os
from logging.config import dictConfig

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from rq import Queue

from config import config, log_config
from redis import Redis

app = Flask(__name__)
app.config.update(config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
app.task_queue = Queue('asynctasks-tasks', connection=Redis.from_url(app.config['REDIS_URL']))

if not os.path.exists('logs'):
    os.mkdir('logs')
dictConfig(log_config)

from app import models, routes, errors
