from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

db = SQLAlchemy()
DB_NAME = "answer.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] ='adhwaith@123'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)
    admin = Admin(app, name='Control Panel')

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import Register

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login' 
    login_manager.init_app(app)

    @login_manager.user_loader
    #def load_user(id):
        #return Student.query.get(int(id)) 

    def load_user(id):
    
        user = Register.query.get(int(id))
        return user

    # @login_manager.user_loader
    # def load_user(user_id):
    #     user_type, user_id = user_id.split('_')  # Split the prefixed id
    #     user_id = int(user_id)  # Convert the id back to an integer
    #     if user_type == 'Student':
    #         return Student.query.get(user_id)
    #     elif user_type == 'Teacher':
    #         return Teacher.query.get(user_id)
    #     return None
     
    return app

def create_database(app):
    if not path.exists('website/' + DB_NAME):
        with app.app_context():
            db.create_all()
            print('Created database')
