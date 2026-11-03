from flask import request
from flask_socketio import emit, join_room, leave_room

from app import db
from app.models import GameRoom, GamePlayer


def register_socket_events(socketio):

    @socketio.on("connect")
    def handle_connect():
        print("Client connected:", request.sid)

    @socketio.on("disconnect")
    def handle_disconnect():
        player = GamePlayer.query.filter_by(sid=request.sid).first()

        if player:
            room_code = player.room.room_code
            player.sid = None
            db.session.commit()

            emit(
                "player_list",
                get_players(player.room),
                to=room_code
            )

        print("Client disconnected:", request.sid)

    @socketio.on("join_game")
    def handle_join_game(data):
        room_code = str(data.get("room_code", "")).upper()
        player_id = data.get("player_id")

        room = GameRoom.query.filter_by(
            room_code=room_code,
            status="waiting"
        ).first()

        player = db.session.get(GamePlayer, player_id)

        if not room or not player or player.room_id != room.id:
            emit("join_error", {"message": "Invalid room or player."})
            return

        player.sid = request.sid
        db.session.commit()

        join_room(room_code)

        emit(
            "player_list",
            get_players(room),
            to=room_code
        )

        emit(
            "joined_success",
            {"nickname": player.nickname}
        )

    @socketio.on("start_game")
    def handle_start_game(data):
        room_code = str(data.get("room_code", "")).upper()

        room = GameRoom.query.filter_by(
            room_code=room_code
        ).first()

        if not room or room.status != "waiting":
            return

        # Host musí být přihlášený a vlastnit místnost.
        from flask_login import current_user

        if not current_user.is_authenticated or current_user.id != room.host_id:
            return

        room.status = "playing"
        db.session.commit()

        emit("game_started", {}, to=room_code)


def get_players(room):
    return [
        {
            "id": player.id,
            "nickname": player.nickname,
            "score": player.score
        }
        for player in room.players
    ]