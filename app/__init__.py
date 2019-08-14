from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from rq import Queue

from config import config
from redis import Redis


app = Flask(__name__)
app.config.update(config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
app.redis = Redis.from_url(app.config['REDIS_URL'])
app.task_queue = Queue('asynctasks-tasks', connection=app.redis)

from app import models, routes, errors
