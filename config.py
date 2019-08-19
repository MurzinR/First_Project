import os
from logging.config import dictConfig

basedir = os.path.abspath(os.path.dirname(__file__))
config = {'SECRET_KEY': os.environ.get('SECRET_KEY') or 'you-will-never-guess',
          'SQLALCHEMY_DATABASE_URI': os.environ.get('DATABASE_URL', 'postgres+psycopg2://postgres:mysecretpassword@127.0.0.1:5434/mytestdb'),
          'SQLALCHEMY_TRACK_MODIFICATIONS': False,
          'REDIS_URL': os.environ.get('REDIS_URL') or 'redis://'}
log_config = {
    "version": 1,
    "formatters": {
        "simple": {
            "format": '%(asctime)s - %(levelname)s - %(message)s'
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "simple",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.FileHandler",
            "level": "INFO",
            "formatter": "simple",
            "filename": "logs/asynctasks.log"
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file"]
    }
}
