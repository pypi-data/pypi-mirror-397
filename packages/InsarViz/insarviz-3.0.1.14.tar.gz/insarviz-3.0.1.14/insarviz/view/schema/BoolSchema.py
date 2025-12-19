from .__prelude__ import Qt

from .Schema import Schema

class BoolSchema(Schema):
    class BoolNode(Schema.Node):
        def __init__(self, item_model, schema, model):
            super().__init__(item_model, schema)
            self._init_model(model)

        def flags(self):
            return Qt.Qt.ItemFlag.ItemIsUserCheckable | super().flags()
        def data(self, role):
            if role == Qt.Qt.ItemDataRole.DisplayRole:
                return self._schema._name
            if role == Qt.Qt.ItemDataRole.CheckStateRole:
                return Qt.Qt.CheckState.Checked if self.model else Qt.Qt.CheckState.Unchecked
        def setData(self, value, role):
            if role == Qt.Qt.ItemDataRole.CheckStateRole:
                self.requestModelChange.emit(value == Qt.Qt.CheckState.Checked.value)
                return True
            return False

        def _init_model(self, model):
            super()._init_model(model)
            self.dataChanged.emit([Qt.Qt.ItemDataRole.CheckStateRole])

    def __init__(self, name):
        super().__init__()
        self._name = name

    def make_node(self, item_model, model):
        return BoolSchema.BoolNode(item_model, self, model)
