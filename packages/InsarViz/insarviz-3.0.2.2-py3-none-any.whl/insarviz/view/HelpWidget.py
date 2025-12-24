from .__prelude__ import Qt
from .WidgetTree import Leaf, Container

class HelpWidget(Qt.QWidget):
    class ChildrenOfInterest:
        pass

    def __init__(self):
        super().__init__()

        self.widgets = self.ChildrenOfInterest()
        def mkGroupBox(title):
            ret = Qt.QGroupBox(title)
            ret.setFlat(True)
            return ret
        def separator():
            ret = Qt.QWidget()
            ret.setFixedHeight(1)
            ret.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Fixed)
            ret.setStyleSheet("background-color: #c0c0c0;")
            return ret

        wtree = Container(Qt.QHBoxLayout, (), [
            Container(Qt.QVBoxLayout, (), [
                Leaf(Qt.QLabel, ("F1 : Show/hide this help", )),
                Leaf(separator, ()),
                Leaf(Qt.QLabel, ("Ctrl+S : Save project", )),
                Leaf(Qt.QLabel, ("Ctrl+Shift+S : Save project as...", )),
                Leaf(Qt.QLabel, ("Ctrl+O : Open dataset", )),
                Leaf(separator, ()),
                Leaf(Qt.QLabel, ("Ctrl+P : Show/hide plots", )),
                Leaf(Qt.QLabel, ("Ctrl+M : Show/hide minimap", )),
                (Leaf(Qt.QWidget, ()), {"stretch":1})
            ], widget_class=lambda: mkGroupBox("Global interaction")),
            Container(Qt.QVBoxLayout, (), [
                Leaf(Qt.QLabel, ("Mouse wheel : zoom in/out", )),
                Leaf(Qt.QLabel, ("Ctrl+Mouse wheel : rotate plane", )),
                Leaf(Qt.QLabel, ("Shift+Mouse wheel : tilt plane", )),
                Leaf(Qt.QLabel, ("Ctrl+Shift+Mouse wheel : Increase/decrease height LOS scaling", )),
                Leaf(separator, ()),
                Leaf(Qt.QLabel, ("Mouse drag : drag plane", )),
                Leaf(Qt.QLabel, ("Ctrl+Mouse drag : create point with radius", )),
                Leaf(Qt.QLabel, ("Shift+Mouse drag : create profile (hold Shift for multiple end points)", )),
                Leaf(separator, ()),
                Leaf(Qt.QLabel, ("Ctrl+A : Autorange current band", )),
                Leaf(Qt.QLabel, ("Ctrl+Shift+A : Autorange all bands", )),
            ], widget_class=lambda: mkGroupBox("Map interaction")),
        ])
        wtree.create_in(self, self.widgets)
