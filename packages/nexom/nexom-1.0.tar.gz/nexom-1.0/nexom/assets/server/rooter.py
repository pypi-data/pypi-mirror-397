from nexom.web.path import Path, Pathlib

from pages import default, document

conf = Pathlib(
    Path("", default.main, "DefaultPage"),
    Path("doc/", document.main, "DocumentPage")
)