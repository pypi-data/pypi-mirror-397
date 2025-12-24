from .http_status_codes import http_status_codes
import importlib.resources as r

class Response:
    def __init__(self, body, status:int=200, headers:list[tuple]=..., cookie:str=...):
        if headers == Ellipsis :
            headers = None
        if cookie == Ellipsis :
            cookie = None

        self.body = body.encode() if isinstance(body, str) else body
        self.status = status
        self.status_text = http_status_codes.get(status)
        self.headers = headers or [("Content-Type", "text/html")]
        
        if cookie:
            self.headers.append(("Set-Cookie", str(cookie)))

class Redirect(Response):
    def __init__(self, location:str):
        headers = [
            ("Location", location)
        ]
        super().__init__("", status=302, headers=headers)

class ErrorResponse(Response):
    def __init__(self, status:int, message:str):
        status = f"{status} {http_status_codes.get(status)}"

        d_ = self._open()
        d = d_.replace("__STATUS__", status).replace("__MESSAGE__", message)

        super().__init__(d, status)

    def _open(self):
        return r.files("nexom.assets.error_page").joinpath("error.html").read_text(encoding="utf-8")

