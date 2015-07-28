# coding: utf-8

import os

SQLALCHEMY_POOL_SIZE = int(os.getenv('SQLALCHEMY_POOL_SIZE', '100'))
SQLALCHEMY_POOL_TIMEOUT = int(os.getenv('SQLALCHEMY_POOL_TIMEOUT', '10'))
SQLALCHEMY_POOL_RECYCLE = int(os.getenv('SQLALCHEMY_POOL_RECYCLE', '2000'))

MYSQL_HOST = os.getenv('MYSQL_HOST', '127.0.0.1')
MYSQL_PORT = os.getenv('MYSQL_PORT', '3306')
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'mimiron')

ERU_URL = os.getenv('ERU_URL', 'http://127.0.0.1:5000')
ERU_TIMEOUT = int(os.getenv('ERU_TIMEOUT', '10'))
ERU_USER = os.getenv('ERU_USER', '')
ERU_PASSWORD = os.getenv('ERU_PASSWORD', '')

REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))

DEBUG = bool(os.getenv('DEBUG', ''))
SCAN_INTERVAL = int(os.getenv('SCAN_INTERVAL', 30))

USE_MOCK = bool(os.getenv('USE_MOCK', ''))

try:
    from local_config import *
except ImportError:
    pass

SQLALCHEMY_DATABASE_URI = 'mysql://{0}:{1}@{2}:{3}/{4}'.format(
    MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE,
)
