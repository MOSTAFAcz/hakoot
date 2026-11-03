from app import db
from flask_login import UserMixin
from datetime import datetime


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    quizzes = db.relationship(
        "Quiz",
        backref="owner",
        lazy=True,
        cascade="all, delete-orphan"
    )


class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    questions = db.relationship(
        "Question",
        backref="quiz",
        lazy=True,
        cascade="all, delete-orphan"
    )


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.id"), nullable=False)

    answers = db.relationship(
        "Answer",
        backref="question",
        lazy=True,
        cascade="all, delete-orphan"
    )


class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"), nullable=False)


class GameRoom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_code = db.Column(db.String(6), unique=True, nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.id"), nullable=False)
    host_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    status = db.Column(db.String(20), default="waiting")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    quiz = db.relationship("Quiz")
    host = db.relationship("User")
    players = db.relationship(
        "GamePlayer",
        backref="room",
        cascade="all, delete-orphan"
    )


class GamePlayer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(30), nullable=False)
    score = db.Column(db.Integer, default=0)
    room_id = db.Column(db.Integer, db.ForeignKey("game_room.id"), nullable=False)
    sid = db.Column(db.String(100), nullable=True)