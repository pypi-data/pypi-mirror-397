
class SMessage:

    def __init__(self, **kwargs):
        self.errors = kwargs.get("errors", None)
        self.result = kwargs.get("result", None)
        self.status = kwargs.get("status", None)
