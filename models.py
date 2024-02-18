from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import JSON, DATETIME
from database import db

class MercorUsers(db.Model):
    __tablename__ = 'MercorUsers'
    userId = db.Column(db.String(255), primary_key=True,index=True)
    email = db.Column(db.String(255), unique=True, nullable=False,index=True)
    name = db.Column(db.String(255),index=True)
    phone = db.Column(db.String(255),index=True)
    residence = db.Column(JSON)
    profilePic = db.Column(db.Text)
    createdAt = db.Column(DATETIME, nullable=False, server_default=db.func.current_timestamp())
    lastLogin = db.Column(DATETIME, nullable=False, server_default=db.func.current_timestamp())
    notes = db.Column(db.Text)
    referralCode = db.Column(db.String(255), unique=True, default=db.func.uuid())
    isGptEnabled = db.Column(db.Boolean, nullable=False, default=False)
    preferredRole = db.Column(db.String(255),index=True)
    fullTimeStatus = db.Column(db.String(255),index=True)
    workAvailability = db.Column(db.String(255),index=True)
    fullTimeSalaryCurrency = db.Column(db.String(255),index=True)
    fullTimeSalary = db.Column(db.String(255),index=True)
    partTimeSalaryCurrency = db.Column(db.String(255),index=True)
    partTimeSalary = db.Column(db.String(255),index=True)
    fullTime = db.Column(db.Boolean, nullable=False, default=False,index=True)
    fullTimeAvailability = db.Column(db.Integer,index=True)
    partTime = db.Column(db.Boolean, nullable=False, default=False,index=True)
    partTimeAvailability = db.Column(db.Integer,index=True)
    w8BenUrl = db.Column(JSON)
    tosUrl = db.Column(db.Text)
    policyUrls = db.Column(JSON)
    isPreVetted = db.Column(db.Boolean, nullable=False, default=False)
    isActive = db.Column(db.Boolean, nullable=False, default=False)
    isComplete = db.Column(db.Boolean, nullable=False, default=False)
    summary = db.Column(db.Text,index=True)
    preVettedAt = db.Column(DATETIME)
    skills = db.relationship('MercorUserSkills', back_populates='user')  # Corrected relationship
    resume = db.relationship('UserResume', back_populates='user', uselist=False)


class Skills(db.Model):
    __tablename__ = 'Skills'
    skillId = db.Column(db.String(255), primary_key=True,index=True)
    skillName = db.Column(db.String(255), nullable=False,index=True)
    skillValue = db.Column(db.String(255), unique=True, nullable=False,index=True)
    users = db.relationship('MercorUserSkills', back_populates='skill')  # Corrected relationship
    

class MercorUserSkills(db.Model):
    __tablename__ = 'MercorUserSkills'
    userId = db.Column(db.String(255), db.ForeignKey('MercorUsers.userId'), primary_key=True,index=True)
    skillId = db.Column(db.String(255), db.ForeignKey('Skills.skillId'), primary_key=True,index=True)
    isPrimary = db.Column(db.Boolean, nullable=False, default=False,index=True)
    order = db.Column(db.Integer, nullable=False, default=0,index=True)
    user = db.relationship('MercorUsers', back_populates='skills')  # Ensure this matches the MercorUsers relationship name
    skill = db.relationship('Skills', back_populates='users')  # Ensure this matches the Skills relationship name
class UserResume(db.Model):
    __tablename__ = 'UserResume'
    resumeId = db.Column(db.String(255), primary_key=True)
    url = db.Column(db.Text)
    filename = db.Column(db.String(255), nullable=False)
    createdAt = db.Column(DATETIME, nullable=False, server_default=db.func.current_timestamp())
    updatedAt = db.Column(DATETIME, nullable=False, server_default=db.func.current_timestamp(), server_onupdate=db.func.current_timestamp())
    source = db.Column(db.String(255), nullable=False, default='platform')
    ocrText = db.Column(db.Text)
    ocrEmail = db.Column(db.String(255))
    ocrGithubUsername = db.Column(db.String(255))
    resumeBasedQuestions = db.Column(db.Text)
    userId = db.Column(db.String(255), db.ForeignKey('MercorUsers.userId'), unique=True)
    isInvitedToInterview = db.Column(db.Boolean, nullable=False, default=False)
    reminderTasksIds = db.Column(JSON)
    personalInformation = db.relationship('PersonalInformation', backref='UserResume', lazy=True, uselist=False)
    workExperiences = db.relationship('WorkExperience', backref='UserResume', lazy=True)
    educations = db.relationship('Education', backref='UserResume', lazy=True)
    userId = db.Column(db.String(255), db.ForeignKey('MercorUsers.userId'), unique=True)
    user = db.relationship('MercorUsers', back_populates='resume', overlaps="resumes")

class PersonalInformation(db.Model):
    __tablename__ = 'PersonalInformation'
    personalInformationId = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(255))
    location = db.Column(JSON)
    email = db.Column(JSON)
    phone = db.Column(JSON)
    resumeId = db.Column(db.String(255), db.ForeignKey('UserResume.resumeId'))

class WorkExperience(db.Model):
    __tablename__ = 'WorkExperience'
    workExperienceId = db.Column(db.String(255), primary_key=True)
    company = db.Column(db.String(255))
    role = db.Column(db.String(255))
    startDate = db.Column(db.String(255))
    endDate = db.Column(db.String(255))
    description = db.Column(db.Text)
    locationCity = db.Column(db.String(255))
    locationCountry = db.Column(db.String(255))
    resumeId = db.Column(db.String(255), db.ForeignKey('UserResume.resumeId'))

class Education(db.Model):
    __tablename__ = 'Education'
    educationId = db.Column(db.String(255), primary_key=True)
    degree = db.Column(db.String(255))
    major = db.Column(db.String(255))
    school = db.Column(db.String(255))
    startDate = db.Column(db.String(255))
    endDate = db.Column(db.String(255))
    grade = db.Column(db.String(255))
    resumeId = db.Column(db.String(255), db.ForeignKey('UserResume.resumeId'))

