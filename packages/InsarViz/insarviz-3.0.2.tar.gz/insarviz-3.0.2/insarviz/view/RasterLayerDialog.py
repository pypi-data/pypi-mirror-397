from .__prelude__ import Qt
from .WidgetTree import Container, Leaf

class RasterLayerDialog(Qt.QDialog):
    class ChildrenOfInterest:
        def __init__(self):
            self.band_chooser: Qt.QComboBox
            self.ok_button: Qt.QPushButton

    def __init__(self, dataset, parent = None):
        super().__init__(parent)

        self._dataset = dataset
        self.widgets = self.ChildrenOfInterest()
        wtree = Container(Qt.QVBoxLayout, (), [
            Leaf(Qt.QLabel, ("Choose band", )),
            Leaf(Qt.QComboBox, (), id="band_chooser"),
            Leaf(Qt.QPushButton, ("OK",), id="ok_button")
        ])
        wtree.create_in(self, self.widgets)
        self.setSizePolicy(Qt.QSizePolicy.Policy.Fixed, Qt.QSizePolicy.Policy.Fixed)

        self.setWindowTitle(f"Open dataset : {dataset.file}")
        self.setModal(True)
        for i, description in enumerate(dataset.descriptions):
            self.widgets.band_chooser.addItem(f"{i}: {description}", i)

        self.widgets.ok_button.clicked.connect(self.accept)

        self.setFixedSize(self.sizeHint())

    @property
    def band_number(self):
        return self.widgets.band_chooser.currentData()
