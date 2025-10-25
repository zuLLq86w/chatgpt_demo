
class HTTPBadRequest(Exception):
    def __init__(self, errmsg, detail=None):
        self.errmsg = errmsg
        self.detail = detail

