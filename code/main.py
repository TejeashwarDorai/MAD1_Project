from flask import Flask, render_template, request, redirect, url_for, flash, session
from application.config import Config
from application.database import db 
from application.model import *

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        db.create_all()

        if not User.query.filter_by(username='admin').first():
            admin_user = User( username = 'admin', password = 'admin@123', role = 'admin', email = 'admin@gmail.com', address = 'Chennai', mobile_no = '6382569283')
            db.session.add(admin_user)

            db.session.commit()

    return app

app=create_app()

from application.routes import *

if __name__ == '__main__':
    app.run(debug=True)
