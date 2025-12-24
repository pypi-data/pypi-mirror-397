import os, shutil
from importlib import resources

def server(work_dir:str, name:str):

    def _copy_from_package(pkg: str, filename: str, dest: str):
        with resources.files(pkg).joinpath(filename).open('rb') as src:
            with open(dest, 'wb') as dst:
                shutil.copyfileobj(src, dst)

    #create directory
    pages_ = os.path.join(work_dir, "pages")
    templates_ = os.path.join(work_dir, "templates")

    os.mkdir(pages_)
    os.mkdir(templates_)

    #file copy

    #pages
    _copy_from_package("nexom.assets.server.pages", "__init__.py", "./pages/__init__.py")
    _copy_from_package("nexom.assets.server.pages", "_templates.py", "./pages/_templates.py")
    _copy_from_package("nexom.assets.server.pages", "default.py", "./pages/default.py")
    _copy_from_package("nexom.assets.server.pages", "document.py", "./pages/document.py")

    #templates
    _copy_from_package("nexom.assets.server.templates", "base.html", "./templates/base.html")
    _copy_from_package("nexom.assets.server.templates", "header.html", "./templates/header.html")
    _copy_from_package("nexom.assets.server.templates", "footer.html", "./templates/footer.html")
    _copy_from_package("nexom.assets.server.templates", "default.html", "./templates/default.html")
    _copy_from_package("nexom.assets.server.templates", "document.html", "./templates/document.html")

    #app
    _copy_from_package("nexom.assets.server", "gunicorn.conf.py", "./gunicorn.conf.py")
    _copy_from_package("nexom.assets.server", "rooter.py", "./rooter.py")
    _copy_from_package("nexom.assets.server", "wsgi.py", "./wsgi.py")
    _copy_from_package("nexom.assets.server", "config.py", "./config.py")

    #enable settings
    with open("./config.py") as sd:
        cd = sd.read()

    ecd = cd.format(
        pwd_dir = os.getcwd(),
        g_address = "0.0.0.0",
        g_port = 8080,
        g_workers = 4,
        g_reload = False
    )

    with open("./config.py", "w") as sd:
        sd.write(ecd)