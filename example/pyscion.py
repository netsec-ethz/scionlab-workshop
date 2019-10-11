"""Mock pyscion API that you can use to run your code locally.

The API consists of:
- set_log_level(level)
- init()
- addr = local_address()
- paths = paths(destination)
- fd = connect(destination, path)
- fd.close()
- fd.write(buffer)
- fd = listen(port)
- addr, n = fd.read(buffer)
"""


class SCIONException(Exception):
    pass


class Path:
    def __repr__(self):
        return "PathMock()"


class connect:
    def __init__(self, destination, path):
        pass

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def write(self, buffer):
        pass

    def read(self, buffer):
        return '1-ffaa:ffff:ffff,[127.0.0.1]:0', 0

    def close(self):
        pass


def set_log_level(level):
    pass


def init():
    pass


def local_address():
    return '1-ffaa:0:0,[127.0.0.1]'


def paths(destination):
    return [Path(), Path()]


def listen(port):
    return connect(None, None)
