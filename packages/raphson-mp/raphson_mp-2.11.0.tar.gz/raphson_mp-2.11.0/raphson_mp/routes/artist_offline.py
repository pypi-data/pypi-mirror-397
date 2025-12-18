from sqlite3 import Connection

from aiohttp import hdrs, web

from raphson_mp.common.image import ImageFormat
from raphson_mp.common.const import RAPHSON_WEBP_PATH
from raphson_mp.server import auth
from raphson_mp.server.decorators import route


@route("/{artist}/image")
async def image(_request: web.Request, _conn: Connection, _user: auth.User):
    return web.FileResponse(RAPHSON_WEBP_PATH, headers={hdrs.CONTENT_TYPE: ImageFormat.WEBP.content_type})

@route("/{artist}/extract")
async def extract(_request: web.Request, _conn: Connection, _user: auth.User):
    raise web.HTTPNoContent()
