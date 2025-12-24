# ============= BASE ERR CLASS =============
class _Error(Exception):
    def __init__(self, code:str, message:str):
        self.code = code
        self.message = message
    def __str__(self):
        return f"{self.code} -> {self.message}"

# ============= MODULE ERR CLASS =============

# --- command ---
class CommandArgmentsError(_Error):
    def __init__(self):
        super().__init__("CS01", "Missing command arguments.")

# --- path ---
class PathNotFoundError(_Error):
    def __init__(self, path:str):
        super().__init__("P01", f"This path is not found. '{path}'")
class PathInvalidHandlerTypeError(_Error):
    def __init__(self, handler:object):
        super().__init__("P02", f"This handler returns invalid type. returns must be of type Response class or dict. '{handler.__name__}'")
class PathlibTypeError(_Error):
    def __init__(self):
        super().__init__("P03", "This list only accepts Path objects.")
class PathHandlerMissingArgError(_Error):
    def __init__(self):
        super().__init__("P04", "Please provide 'request' and 'args' as handler arguments.")

# --- cookie ---
class CookieInvalidValueError(_Error):
    def __init__(self, value:str):
        super().__init__("C01", f"This value is invalid. '{value}'")

# --- template ---
class TemplateNotFoundError(_Error):
    def __init__(self, name:str):
        super().__init__("T01", f"This template is not found. '{name}'")
class TemplatesInvalidTypeError(_Error):
    def __init__(self):
        super().__init__("T02", f"This list only accepts Template objects.")
class TemplateKeyNotSetError(_Error):
    def __init__(self, key:str):
        super().__init__("T03", f"The required keys for this template are not set. {key}")