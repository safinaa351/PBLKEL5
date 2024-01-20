from app import db
from sqlalchemy.dialects.mysql import MEDIUMBLOB

class Logaccess(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    no_rfid = db.Column(db.String(50), nullable=False)
    waktu = db.Column(db.DateTime,nullable=False)
    access = db.Column(db.String(50), nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique = True, nullable=False)
    nama = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    role = db.Column(db.String(10))
    password = db.Column(db.String(256), nullable=False)

class Uid(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(50), unique=True, nullable=False)
    nama = db.Column(db.String(100), nullable=False)

class Schedule(db.Model):
    __tablename__ = 'tb_roomschedules'

    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(10), nullable=False)
    time = db.Column(db.String(15), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    class_name = db.Column(db.String(30), nullable=False)

class photoEvidence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    access_time = db.Column(db.DateTime, nullable=False)
    file_name =  db.Column(db.String(255), nullable=False)
    image_data = db.Column(MEDIUMBLOB)