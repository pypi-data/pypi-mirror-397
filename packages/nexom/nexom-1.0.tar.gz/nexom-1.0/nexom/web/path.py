import re, json, os
from mimetypes import guess_type

from ..core.error import PathNotFoundError, PathlibTypeError, PathInvalidHandlerTypeError, PathHandlerMissingArgError

from .request import Request
from .response import Response

class Path:
    def __init__(self, path:str, handler, name:str):
        self.handler:Response = handler
        self.name:str = name

        p_s = path.strip("/").split("/")
        pp_i = 0
        p_args = {}

        for p_i, p_arg in enumerate(p_s):
            m = re.match(r"{(.*?)}" ,p_arg)
            if m:
                if pp_i == 0:
                    pp_i = p_i
                p_args[p_i] = m.group(1)
            if (len(p_s) == p_i+1) and (pp_i == 0):
                pp_i = p_i + 1

        self.path = "/".join(p_s[:pp_i])
        self.detection_range = pp_i
        self.pathArgments = p_args
        self.args = {}

    def _readArgs(self, requestPath:str) -> None:
        rp_s = requestPath.strip("/").split("/")

        for p_i, p_a in self.pathArgments.items():

            if len(rp_s) > p_i:
                val = rp_s[p_i]
            else:
                val = None

            self.args[p_a] = val

    def callHandler(self, request:Request) -> Response:
        try:
            self._readArgs(request.path)
            res = self.handler(request, self.args)
            if isinstance(res, dict):
                b = json.dumps(res).encode("utf-8")
                return Response( b, headers=[("Content-Type", "application/json; charset=utf-8")] )

            if not isinstance(res, Response):
                raise PathInvalidHandlerTypeError(self.handler)

            return res
        except TypeError as e:
            if bool(re.search(r"takes \d+ positional arguments? but \d+ were given", str(e))):
                raise PathHandlerMissingArgError()
            else:
                raise e
        except Exception as e:
            raise e

class Static(Path):
    def __init__(self, path:str, static_directory:str, name:str):
        self.static_directory = static_directory.rstrip("/")
        super().__init__(path, self._access, name)

    def _access(self, request:Request, args:dict) -> Response:
        try:
            ap_s = request.path.split("/")
            ix = self.detection_range
            if len(ap_s) == 1:
                ap = ""
            else:
                ap = os.path.join(*ap_s[ix:])
            cp = os.path.abspath(os.path.join(self.static_directory, ap))

            if os.path.isdir(cp):
                cp = os.path.join(cp, "index.html")
            if not os.path.exists(cp) or not cp.startswith(os.path.abspath(self.static_directory)):
                raise PathNotFoundError(request.path)

            with open(cp, "rb") as c:
                cb = c.read()

            mime_, enc_ = guess_type(cp)
            mime = mime_ or "application/octet-stream"

            return Response(cb, headers=[("Content-Type", mime)])
        except Exception as e:
            raise e



class Pathlib(list):
    def __init__(self, *args):
        for p in args:
            self._check(p)

        super().__init__(args)

        self.raise_if_not_exist = True

    def _check(self, arg:object):
        if not isinstance(arg, Path):
            raise PathlibTypeError

    def get(self, requestPath:str) -> Path | None:
        rp_s = requestPath.rstrip("/").split("/")
        for p in self:
            detection_path = "/".join(rp_s[:p.detection_range])
            if detection_path == p.path:
                return p

        if self.raise_if_not_exist:
            raise PathNotFoundError(requestPath)
        else:
            return None