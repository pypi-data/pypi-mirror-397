import sys, os

from nexom.core.error import CommandArgmentsError

from nexom.setup import build

if __name__ == "__main__":
    try:
        argv = sys.argv[1:]

        control, args = argv[0], argv[1:]

        if control == "test":
            print("Hello Nexom Web FreamWorks!!💩")

        elif control == "build-server":
            server_name = args[0]

            build.server(os.getcwd(), server_name)
    except IndexError:
        raise CommandArgmentsError()
    except Exception as e:
        raise e
