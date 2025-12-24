import json

from PySide6.QtCore import Qt, QMimeData, QSize
from PySide6.QtGui import QColor, QBrush, QPen
from PySide6.QtWidgets import QColorDialog, QDialog
from .Schema import Schema

class ColorSchema(Schema):
    class ColorNode(Schema.Node):
        def __init__(self, item_model, schema, model):
            super().__init__(item_model, schema)
            self.set_model(model)

        def flags(self):
            return Qt.ItemFlags.ItemIsEditable | super().flags()
        def data(self, role):
            if role == Qt.ItemDataRole.DisplayRole:
                return self.model
            if role == Qt.ItemDataRole.EditRole:
                return self.model
            if role == Qt.ItemDataRole.SizeHintRole:
                return QSize(0, 20)
            return None
        def setData(self, value, role):
            if role == Qt.ItemDataRole.EditRole:
                self.requestModelChange.emit(value)
                return True
            return False

        def createEditor(self, parent):
            ret = QColorDialog(parent)
            ret.setModal(True)
            ret.setSizeGripEnabled(True)
            return ret
        def destroyEditor(self):
            return True
        def setEditorData(self, editor):
            editor.setCurrentColor(self.model)
            return True
        def setModelData(self, editor):
            if editor.result() == QDialog.DialogCode.Accepted:
                self.requestModelChange.emit(editor.currentColor())
            return True

        def paint(self, painter, option):
            painter.save()
            brush = QBrush(self.model)
            painter.setBrush(brush)
            painter.setPen(QPen(Qt.GlobalColor.black, 1, Qt.PenStyle.SolidLine))
            painter.drawRoundedRect(option.rect.adjusted(5,2,-6,-2), 7, 7)
            painter.restore()
            return True

        def set_model(self, model):
            super().set_model(model)
            self.dataChanged.emit([])

    def make_node(self, item_model, model):
        return self.ColorNode(item_model,self,model)

    def supported_mime_types(self):
        return set(["application/x-insarviz-color"])
    def can_model_from_mime(self, mimeData):
        return mimeData.hasFormat("application/x-insarviz-color")
    def model_from_mime(self, mimeData):
        data_bytes = mimeData.data("application/x-insarviz-color").data()
        [r,g,b,a] = json.loads(bytearray(data_bytes))
        return QColor(r,g,b,a)
    def can_mime_from_model(self, model):
        return True
    def mime_from_model(self, model):
        mimeData = QMimeData()
        dic = [model.red(), model.green(), model.blue(), model.alpha()]
        mimeData.setData("application/x-insarviz-color", bytes(json.dumps(dic), "utf-8"))
        return mimeData
