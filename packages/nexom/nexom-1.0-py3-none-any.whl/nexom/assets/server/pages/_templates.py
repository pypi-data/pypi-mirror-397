from pathlib import Path
from nexom.web.template import Templates

templates_directory = Path(__file__).joinpath("../../templates").resolve()

template = Templates(templates_directory,  

    #templatesフォルダ内のhtmlファイルを指定
    "default", 
    "document" 
)