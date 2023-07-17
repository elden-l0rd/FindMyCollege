from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy import JSON



class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class RIASEC_Scores(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    r_score=db.Column(db.Integer)
    i_score=db.Column(db.Integer)
    a_score=db.Column(db.Integer)
    s_score=db.Column(db.Integer)
    e_score=db.Column(db.Integer)
    c_score=db.Column(db.Integer)
    completed=db.Column(db.Boolean) #To check if user has completed the test before logging out
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    completed=db.Column(db.Boolean)
    notes = db.relationship('Note')
    qualification=db.relationship('Qualification')
    subject_interests=db.relationship('Subject_interests')
    riasec_scores=db.relationship('RIASEC_Scores')
    users_courses=db.relationship('users_courses')
    

class Qualification(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    curriculum=db.Column(db.String(150))
    alevel_score=db.Column(db.String(50))
    ib_score=db.Column(db.Integer)
    polytechnic_score=db.Column(db.Float)
    completed=db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    
class Subject_interests(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    subject1=db.Column(db.String(50))
    subject2=db.Column(db.String(50))
    subject3=db.Column(db.String(50))
    completed=db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Degrees(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    school=db.Column(db.String(150))
    degree=db.Column(db.String(150))
    alevel_igp=db.Column(db.String(150))
    polytechnic_igp=db.Column(db.Float)
    employability=db.Column(db.Float)
    salary=db.Column(db.Integer)
    riasec_code=db.Column(db.String(10))
    related_subject1=db.Column(db.String(50))
    related_subject2=db.Column(db.String(50))
    related_subject3=db.Column(db.String(50))
    additional_information=db.Column(db.String(500))
    a_level_prerequisite_subjects=db.Column(db.String(100))
    a_level_prerequisites=db.Column(db.String(100))

class Holland_Codes(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    r=db.Column(db.String(320))
    i=db.Column(db.String(320))
    a=db.Column(db.String(320))
    s=db.Column(db.String(320))
    e=db.Column(db.String(320))
    c=db.Column(db.String(320))


class users_courses(db.Model):
    # __table__='my_table'
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'))
    by_school_data=db.Column(JSON)
    general_data=db.Column(JSON)
    top_3_codes=db.Column(db.String(10))

