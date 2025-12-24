from .cookie import RequestCookies

class Request:
    def __init__(self, environ):

        self.method = environ.get("REQUEST_METHOD", "GET")
        self.path = environ.get("PATH_INFO", "").strip("/")
        self.query = environ.get("QUERY_STRING", "")
        self.headers = {k: v for k, v in environ.items() if k.startswith("HTTP_")}
        self.environ = environ

        self.cookie: RequestCookies | None = None

        if "HTTP_COOKIE" in self.headers:
            cookie_string = self.headers.get("HTTP_COOKIE")
            cookies = {}
            for data in cookie_string.split('; '):
                if len(data.split('=')) == 2:
                    key, value = data.split('=')
                cookies[key] = value

            rc = RequestCookies(**cookies)
            rc.default = None
            
            self.cookie = rc

    def read_body(self):
        length = int(self.environ.get("CONTENT_LENGTH", 0) or 0)
        if length == 0:
            return b""
        return self.environ["wsgi.input"].read(length)