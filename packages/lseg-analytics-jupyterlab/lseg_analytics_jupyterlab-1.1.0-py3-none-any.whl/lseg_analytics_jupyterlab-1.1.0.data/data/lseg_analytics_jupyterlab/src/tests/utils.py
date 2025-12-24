# type: ignore
from io import BytesIO as IO


class MockRequest(object):
    query = None

    def __init__(self, query):
        self.query = query

    def makefile(self, *args, **kwargs):
        return IO(self.query)
