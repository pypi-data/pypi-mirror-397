import json
from sqlite3 import Connection

from aiohttp import web

from raphson_mp.common import util
from raphson_mp.common.lyrics import INSTRUMENTAL_TEXT
from raphson_mp.common.typing import PlayerSavedStateDict
from raphson_mp.server.auth import StandardUser, User
from raphson_mp.server.decorators import route
from raphson_mp.server.response import template


@route("", redirect_to_login=True)
async def route_player(request: web.Request, _conn: Connection, user: User):
    """
    Main player page. Serves player.jinja2 template file.
    """
    response = await template(
        "player.jinja2",
        mobile=util.is_mobile(request),
        instrumental=INSTRUMENTAL_TEXT,
    )

    # Refresh token cookie
    if isinstance(user, StandardUser):
        assert user.session
        user.session.set_cookie(request, response)

    return response


@route("/restore_state", method="POST")
async def restore_state(_request: web.Request, conn: Connection, user: User):
    states: list[PlayerSavedStateDict] = []
    for row in conn.execute("SELECT tracks FROM saved_player_state WHERE user = ?", (user.user_id,)):
        states.append(json.loads(row[0]))
    conn.execute("DELETE FROM saved_player_state WHERE user = ?", (user.user_id,))
    return web.json_response(states)
