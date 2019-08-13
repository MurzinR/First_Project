import os
from logging.config import dictConfig

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

if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    dictConfig({
        "version": 1,
        "formatters": {
            "simple": {
                "format": '%(asctime)s - %(levelname)s - %(message)s'
            }
        },
        "handlers": {
                "file": {
                    "class": "logging.FileHandler",
                    "level": "INFO",
                    "formatter": "simple",
                    "filename": "logs/asynctasks.log"
                }
        },
        "root": {
                "level": "INFO",
                "handlers": ["file"]
        }
    })

from app import models, routes, errors
