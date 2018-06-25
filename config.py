# http://flask-sqlalchemy.pocoo.org/2.3/config/
class Config(object):
    pg_db_username = 'postgres'
    pg_db_password = ''
    pg_db_name = 'mcd_database'
    pg_db_hostname = '192.168.161.18'
    SECRET_KEY = 'RM=#8z2aX^QKXJg'
    
    SQLALCHEMY_DATABASE_URI = "postgresql://{DB_USER}:{DB_PASS}@{DB_ADDR}/{DB_NAME}".format(DB_USER=pg_db_username, DB_PASS=pg_db_password, DB_ADDR=pg_db_hostname, DB_NAME=pg_db_name)
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_POOL_SIZE = 40
    SQLALCHEMY_MAX_OVERFLOW = 100    

class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False

app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}