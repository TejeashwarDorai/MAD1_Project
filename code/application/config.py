class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///data.sqlite3'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = 'very secret :)'
    DEBUG = True