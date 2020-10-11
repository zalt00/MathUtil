
class A:
    def __init__(self, b):
        self.b = b
        
    def __getattribute__(self, key):
        return getattr(object.__getattribute__(self, 'b'), key)


class B:
    def __init__(self):
        self.t = 4
        self.p = 8
        self.l = 78
        return NotImplemented
