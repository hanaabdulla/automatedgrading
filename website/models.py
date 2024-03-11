from . import db 
from flask_login import UserMixin
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView


 

class Register(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    register_number = db.Column(db.Integer)
    dob = db.Column(db.DateTime)
    sex = db.Column(db.String(200), nullable=False)
    semester = db.Column(db.String(200))
    department = db.Column(db.String(200))
    password = db.Column(db.String(200), nullable=False)
    status = db.Column(db.Integer)
    userrole =db.Column(db.Integer)




    






