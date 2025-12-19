from .__prelude__ import Qt
from .Schema import Schema

class FloatSliderSchema(Schema):
    class FloatSliderWidget(Qt.QGroupBox):
        valueChanged = Qt.Signal(float)

        def __init__(self, name, f_min, f_max):
            super().__init__(name)

            layout = Qt.QHBoxLayout(self)
            self._layout = layout
            self._f_min = f_min
            self._f_max = f_max

            slider = Qt.QSlider(Qt.Qt.Orientation.Horizontal)
            slider.setMinimum(0)
            slider.setMaximum(1000)
            slider.valueChanged.connect(self._on_value_changed)
            layout.addWidget(slider, stretch=1)
            self._slider : Qt.QSlider = slider
            layout.setContentsMargins(5,2,5,2)
            self.setLayout(layout)

        @Qt.Slot(int)
        def _on_value_changed(self, __n__):
            self.valueChanged.emit(self.value())

        def value(self):
            return float(self._slider.value()) * 0.001 * (self._f_max - self._f_min) + self._f_min
        def setValue(self, value: float):
            return self._slider.setValue(int((value - self._f_min) * 1000.0 / (self._f_max - self._f_min)))

    class FloatSliderNode(Schema.Node):
        def __init__(self, item_model, schema, model, name):
            super().__init__(item_model, schema)
            self._create_editor()
            self._init_model(model)

        def _create_editor(self):
            self._editor = FloatSliderSchema.FloatSliderWidget(self._schema.name, self._schema.f_min, self._schema.f_max)
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
        def _init_model(self, model):
            super()._init_model(model)
            self.dataChanged.emit([])

        # def data(self, role):
        #     if role == Qt.ItemDataRole.DisplayRole:
        #         return self.model
        #     return None

    def __init__(self, name, f_min = 0.0, f_max = 1.0):
        self.name = name
        self.f_min = f_min
        self.f_max = f_max

    def make_node(self, item_model, model):
        return self.FloatSliderNode(item_model, self, model, self.name)

class FloatSchema(Schema):
    class FloatNode(Schema.Node):
        def __init__(self, item_model, schema, model, name):
            super().__init__(item_model, schema)
            self.name = name
            self._create_editor()
            self._init_model(model)

        def _create_editor(self):
            self._editor = Qt.QDoubleSpinBox()
            self._editor.setPrefix(f"{self.name} : ")
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
        def _init_model(self, model):
            super()._init_model(model)
            self.dataChanged.emit([])

    def __init__(self, name):
        self.name = name

    def make_node(self, item_model, model):
        return self.FloatNode(item_model, self, model, self.name)
