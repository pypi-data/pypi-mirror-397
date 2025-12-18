from datetime import datetime


def get_version():
    return datetime.now().strftime("%Y.%m.%d.%H%M%S")
