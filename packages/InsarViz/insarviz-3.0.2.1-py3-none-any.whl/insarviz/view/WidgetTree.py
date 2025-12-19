from .__prelude__ import Qt, Matrix

class WidgetTree:
    def __init__(self, id = None):
        self._id = id
    def create(self, widget_ids):
        raise NotImplementedError
    def register(self, widget_ids, w):
        if self._id is not None and not hasattr(widget_ids, self._id):
            setattr(widget_ids, self._id, w)
class Container(WidgetTree):
    def __init__(self, layout_class, layout_args, children, widget_class = Qt.QWidget, id = None):
        super().__init__(id)
        self._widget_class = widget_class
        self._layout_class = layout_class
        self._layout_args = layout_args
        self._children = children

    def create(self, widget_ids):
        ret = self._widget_class()
        self.create_in(ret, widget_ids)
        return ret
    def create_in(self, w, widget_ids):
        layout = self._layout_class(*self._layout_args)
        w.setLayout(layout)
        for child in self._children:
            if isinstance(child, tuple):
                layout.addWidget(child[0].create(widget_ids), **child[1])
            else:
                layout.addWidget(child.create(widget_ids))
        self.register(widget_ids, w)
class Leaf(WidgetTree):
    def __init__(self, widget_class, widget_args, widget_kwargs = {}, id = None):
        self._widget_class = widget_class
        self._widget_args = widget_args
        self._widget_kwargs = widget_kwargs
        self._id = id
    def create(self, widget_ids):
        ret = self._widget_class(*self._widget_args, **self._widget_kwargs)
        self.register(widget_ids, ret)
        return ret
