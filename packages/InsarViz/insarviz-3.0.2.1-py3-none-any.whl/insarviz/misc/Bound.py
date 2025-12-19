"""
TODO_DOC
"""
class Bound:
    def __init__(self, bindable, *args):
        self.bindable = bindable
        self.args = args
    def __enter__(self):
        if self.bindable is not None:
            self.bindable.bind(*self.args)
    def __exit__(self, *__args__):
        if self.bindable is not None:
            self.bindable.release()
