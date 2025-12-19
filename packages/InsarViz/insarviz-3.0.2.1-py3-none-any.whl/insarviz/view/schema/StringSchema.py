from typing import Any
from PySide6.QtCore import Qt, QMimeData
from .Schema import Schema

class StringSchema(Schema):
    class StringNode(Schema.Node):
        def __init__(self, item_model, schema, model):
            super().__init__(item_model, schema)
            self.set_model(model)
        def flags(self):
            ret = Qt.ItemFlag.ItemIsEnabled | super().flags()
            if self._schema.is_editable:
                ret = ret | Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsDragEnabled | Qt.ItemFlag.ItemIsDropEnabled | Qt.ItemFlag.ItemIsSelectable
            return ret

        def data(self, role: Qt.ItemDataRole) -> Any:
            if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.ToolTipRole):
                return self.model
            if role == Qt.ItemDataRole.EditRole and self._schema.is_editable:
                return self.model
            return None
        def setData(self, value: Any, role: Qt.ItemDataRole) -> bool:
            if role == Qt.ItemDataRole.EditRole and self._schema.is_editable:
                self.requestModelChange.emit(value)
                return True
            return False
        def set_model(self, model):
            super().set_model(model)
            self.dataChanged.emit([])

    def __init__(self, is_editable = True):
        super().__init__()
        self._is_editable = is_editable
    @property
    def is_editable(self):
        return self._is_editable

    def make_node(self, item_model, model):
        return self.StringNode(item_model,self,model)

    def supported_mime_types(self):
        return set(["application/x-insarviz-string"])
    def can_model_from_mime(self, mimeData: QMimeData) -> bool:
        return mimeData.hasFormat("application/x-insarviz-string")
    def model_from_mime(self, mimeData: QMimeData):
        data_bytes = bytes(mimeData.data("application/x-insarviz-string").data())
        return data_bytes.decode("utf-8")
    def can_mime_from_model(self, __model__):
        return True
    def mime_from_model(self, model):
        mimeData = QMimeData()
        mimeData.setData("application/x-insarviz-string", bytes(model, "utf-8"))
        return mimeData
