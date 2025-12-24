from nexom.web.request import Request
from nexom.web.response import Response

from ._templates import template

def main(request:Request, args:dict):
    return Response( template.default( title="Nexom Default Page") )