
import random
import string

from flask import (
    render_template, redirect, url_for,
    request, flash, abort
)

from flask_login import (
    login_user, logout_user,
    login_required, current_user
)

from werkzeug.security import (
    generate_password_hash, check_password_hash
)

from app.models import User, Quiz, Question, Answer, GameRoom, GamePlayer
from app import db


def register_routes(app):

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))

        if request.method == "POST":
            username = request.form.get("username", "").strip()
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")

            if not username or not email or not password:
                flash("Vyplň všechna pole.")
                return redirect(url_for("register"))

            if len(password) < 8:
                flash("Heslo musí mít alespoň 8 znaků.")
                return redirect(url_for("register"))

            if User.query.filter_by(username=username).first():
                flash("Uživatelské jméno již existuje.")
                return redirect(url_for("register"))

            if User.query.filter_by(email=email).first():
                flash("Email již existuje.")
                return redirect(url_for("register"))

            user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password)
            )

            db.session.add(user)
            db.session.commit()

            login_user(user)
            return redirect(url_for("dashboard"))

        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))

        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")

            user = User.query.filter_by(username=username).first()

            if user and check_password_hash(user.password_hash, password):
                login_user(user)
                return redirect(url_for("dashboard"))

            flash("Neplatné přihlašovací údaje.")

        return render_template("login.html")

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("index"))

    @app.route("/dashboard")
    @login_required
    def dashboard():
        quizzes = Quiz.query.filter_by(
            owner_id=current_user.id
        ).all()

        return render_template(
            "dashboard.html",
            quizzes=quizzes
        )

    # CREATE QUIZ
    @app.route("/quiz/create", methods=["GET", "POST"])
    @login_required
    def create_quiz():
        if request.method == "POST":
            title = request.form.get("title", "").strip()
            description = request.form.get("description", "").strip()

            if not title:
                flash("Název kvízu je povinný.")
                return redirect(url_for("create_quiz"))

            quiz = Quiz(
                title=title,
                description=description,
                owner_id=current_user.id
            )

            db.session.add(quiz)
            db.session.commit()

            flash("Kvíz byl vytvořen!")
            return redirect(url_for("edit_quiz", quiz_id=quiz.id))

        return render_template("create_quiz.html")

    # EDIT QUIZ
    @app.route("/quiz/<int:quiz_id>/edit", methods=["GET", "POST"])
    @login_required
    def edit_quiz(quiz_id):
        quiz = db.session.get(Quiz, quiz_id)

        if not quiz or quiz.owner_id != current_user.id:
            abort(404)

        if request.method == "POST":
            question_text = request.form.get("question", "").strip()
            answers = [
                answer.strip()
                for answer in request.form.getlist("answers")
            ]
            correct = request.form.get("correct")

            if (
                not question_text
                or len(answers) != 4
                or any(not answer for answer in answers)
                or correct not in ["0", "1", "2", "3"]
            ):
                flash("Vyplň otázku a všechny čtyři odpovědi.")
                return redirect(url_for("edit_quiz", quiz_id=quiz.id))

            question = Question(
                text=question_text,
                quiz_id=quiz.id
            )

            db.session.add(question)
            db.session.flush()

            for index, answer_text in enumerate(answers):
                answer = Answer(
                    text=answer_text,
                    is_correct=(index == int(correct)),
                    question_id=question.id
                )
                db.session.add(answer)

            db.session.commit()

            flash("Otázka byla přidána!")
            return redirect(url_for("edit_quiz", quiz_id=quiz.id))

        return render_template("edit_quiz.html", quiz=quiz)

    # DELETE QUIZ
    @app.route("/quiz/<int:quiz_id>/delete", methods=["POST"])
    @login_required
    def delete_quiz(quiz_id):
        quiz = db.session.get(Quiz, quiz_id)

        if not quiz or quiz.owner_id != current_user.id:
            abort(404)

        db.session.delete(quiz)
        db.session.commit()

        flash("Kvíz byl smazán.")
        return redirect(url_for("dashboard"))

    # CREATE GAME ROOM
    @app.route("/quiz/<int:quiz_id>/create-room", methods=["POST"])
    @login_required
    def create_room(quiz_id):
        quiz = db.session.get(Quiz, quiz_id)

        if not quiz or quiz.owner_id != current_user.id:
            abort(404)

        room_code = ''.join(
            random.choices(string.ascii_uppercase + string.digits, k=6)
        )

        while GameRoom.query.filter_by(room_code=room_code).first():
            room_code = ''.join(
                random.choices(string.ascii_uppercase + string.digits, k=6)
            )

        room = GameRoom(
            room_code=room_code,
            quiz_id=quiz.id,
            host_id=current_user.id
        )

        db.session.add(room)
        db.session.commit()

        return redirect(url_for("host_room", room_code=room_code))

    # HOST ROOM
    @app.route("/room/<room_code>")
    @login_required
    def host_room(room_code):
        room = GameRoom.query.filter_by(
            room_code=room_code
        ).first_or_404()

        if room.host_id != current_user.id:
            abort(403)

        return render_template("host_room.html", room=room)

    # JOIN GAME
    @app.route("/join", methods=["GET", "POST"])
    def join_game():
        if request.method == "POST":
            room_code = request.form.get("room_code", "").strip().upper()
            nickname = request.form.get("nickname", "").strip()

            room = GameRoom.query.filter_by(
                room_code=room_code,
                status="waiting"
            ).first()

            if not room:
                flash("Místnost neexistuje nebo už hra začala.")
                return redirect(url_for("join_game"))

            if not nickname or len(nickname) > 30:
                flash("Zadej přezdívku (max. 30 znaků).")
                return redirect(url_for("join_game"))

            player = GamePlayer(
                nickname=nickname,
                room_id=room.id
            )

            db.session.add(player)
            db.session.commit()

            return redirect(url_for(
                "player_room",
                room_code=room_code,
                player_id=player.id
            ))

        return render_template("join.html")

    # PLAYER ROOM
    @app.route("/play/<room_code>/<int:player_id>")
    def player_room(room_code, player_id):
        room = GameRoom.query.filter_by(
            room_code=room_code
        ).first_or_404()

        player = db.session.get(GamePlayer, player_id)

        if not player or player.room_id != room.id:
            abort(404)

        return render_template(
            "player_room.html",
            room=room,
            player=player
        )
