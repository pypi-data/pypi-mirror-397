from .response import Response

from ..core.error import CookieInvalidValueError

class Cookie(dict):
    def __init__(self, name:str, value:str, **kwargs:str):
        super().__init__(kwargs)

        if name is None:
            raise CookieInvalidValueError("None")

        self.name = name
        self.value = value
        self.httpOnly = True

    def __repr__(self) -> str:
        c_s = []
        c_s.append(f"{self.name}={self.value};")
        for key, value in self.items():
            c_s.append(f"{key}={value};")

        if self.httpOnly:
            c_s.append("HttpOnly;")
        c_s.append("Secure")

        c = " ".join(c_s)
        return c
    def __str__(self) -> str:
        return self.__repr__()

    def append(self, key:str, value:str | int) -> None:
        self[key] = value

    def response(self) -> Response:
        res =  Response("OK")
        res.headers.append( ("Set-Cookie", self.__repr__()) )
        return res

class RequestCookies(dict):
    def __init__(self, **kwargs:str):
        super().__init__(kwargs)

        self.default = None
    
    def get(self, key:str) -> str | None:
        return super().get(key, self.default)