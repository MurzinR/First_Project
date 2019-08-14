import os

basedir = os.path.abspath(os.path.dirname(__file__))
config = {'SECRET_KEY': os.environ.get('SECRET_KEY') or 'you-will-never-guess',
          'SQLALCHEMY_DATABASE_URI': os.environ.get('DATABASE_URL'),
          'SQLALCHEMY_TRACK_MODIFICATIONS': False,
          'REDIS_URL': os.environ.get('REDIS_URL') or 'redis://'}
