from typing import Any, Optional, override

from .Schema import Schema
from .__prelude__ import Qt

class IntSchema(Schema):
    class IntNode(Schema.Node):
        def __init__(self, item_model: Qt.QAbstractItemModel, schema: "IntSchema", model: int, name: str):
            super().__init__(item_model, schema)
            self.name: str = name
            self._editor: Optional[Qt.QSpinBox] = None
            self.set_model(model)

        def createEditor(self, parent: Qt.QWidget) -> Optional[Qt.QWidget]:
            if self._editor is None:
                self._editor = Qt.QSpinBox()
                self._editor.setFrame(False)
                self._editor.setMinimum(0)
                self._editor.setMaximum(10000)
                self._editor.valueChanged.connect(lambda value: self.requestModelChange.emit(value))
            self._editor.setPrefix(f"{self.name} : ")
            self._editor.setParent(parent)
            return self._editor
        def destroyEditor(self) -> bool:
            return False
        def editor(self) -> Optional[Qt.QWidget]:
            return self._editor
        def setEditorData(self, editor):
            if self.model is not None:
                editor.setValue(self.model)
            return True

        def flags(self):
            return Qt.Qt.ItemFlag.ItemIsEditable | super().flags()
        def set_model(self, model: int):
            super().set_model(model)
            if self._editor is not None:
                self._editor.setValue(model)
            self.dataChanged.emit([])

    def __init__(self, name):
        self.name = name

    def make_node(self, item_model: Qt.QAbstractItemModel, model: Any) -> "Schema.Node":
        return self.IntNode(item_model, self, model, self.name)

class IntSliderSchema(Schema):
    class IntSliderWidget(Qt.QGroupBox):
        valueChanged = Qt.Signal(int)

        def __init__(self, name):
            super().__init__(name)
            layout = Qt.QHBoxLayout(self)
            self._layout = layout
            self._label = Qt.QLabel(name)
            slider = Qt.QSlider(orientation=Qt.Qt.Orientation.Horizontal)
            slider.valueChanged.connect(self.valueChanged.emit)
            layout.addWidget(slider, stretch=1)
            self._slider : QSlider = slider
            layout.setContentsMargins(5,2,5,2)
            self.setLayout(layout)

        def value(self):
            return self._slider.value()
        def setValue(self, value):
            return self._slider.setValue(value)

    class IntSliderNode(Schema.Node):
        def __init__(self, item_model, schema, model, name):
            super().__init__(item_model, schema)
            self.name = name
            self._create_editor()
            self.set_model(model)

        def _create_editor(self):
            self._editor = IntSliderSchema.IntSliderWidget(self.name)
            self._editor.valueChanged.connect(self.requestModelChange.emit)

        def createEditor(self, parent):
            self._editor.setParent(parent)
            return self._editor
        def destroyEditor(self):
            return False
        def editor(self):
            return self._editor
        def setModelData(self, __editor__):
            return True
        def setEditorData(self, editor):
            editor.setValue(self.model)
            return True

        def flags(self):
            return Qt.Qt.ItemFlag.ItemIsEditable | super().flags()
        def set_model(self, model):
            super().set_model(model)
            self.dataChanged.emit([])

        # def data(self, role):
        #     if role == Qt.ItemDataRole.DisplayRole:
        #         return self.model
        #     return None

    def __init__(self, name):
        self.name = name

    def make_node(self, item_model, model):
        return self.IntSliderNode(item_model, self, model, self.name)
