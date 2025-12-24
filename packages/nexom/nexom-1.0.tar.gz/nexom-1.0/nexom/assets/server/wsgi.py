from nexom.web.request import Request
from nexom.web.response import Response
from rooter import conf

from nexom.core.error import PathNotFoundError

def Server(environ, _response):
    try:
        request = Request(environ)
        rp = request.path

        p = conf.get(rp)
        res = p.callHandler(request)

    except PathNotFoundError as e:
        res = Response("This page is not found", 404)
    except Exception as e:
        res = Response(str(e), 500)
    
    finally:
        status_line = f"{res.status} {res.status_text}"
        _response(status_line, res.headers)

        return [res.body]