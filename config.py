import os
from logging.config import dictConfig

basedir = os.path.abspath(os.path.dirname(__file__))
config = {'SECRET_KEY': os.environ.get('SECRET_KEY') or 'you-will-never-guess',
          'SQLALCHEMY_DATABASE_URI': os.environ.get('DATABASE_URL'),
          'SQLALCHEMY_TRACK_MODIFICATIONS': False,
          'REDIS_URL': os.environ.get('REDIS_URL') or 'redis://'}

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
