# type: ignore[reportIncompatibleMethodOverride]
from typing import Optional, Any

from .__prelude__ import Qt

from .Schema import Schema

class SchemaItemModel(Qt.QAbstractItemModel):
    def __init__(self, schema: Schema, model: Any):
        super().__init__(None)
        self._schema: Schema = schema
        self._mime_types: list[str] = [typ for typ in schema.supported_mime_types()]
        self._root_node: Schema.Node = schema.make_node(self, model)
        self._root_node.set_links(Qt.QModelIndex(), Qt.QModelIndex())

    def node_at(self, index: Qt.QModelIndex) -> Schema.Node:
        if index.isValid():
            ret = index.internalPointer()
        else:
            ret = self._root_node
        return ret

    def rowCount(self, index: Qt.QModelIndex = Qt.QModelIndex()) -> int:
        node = self.node_at(index)
        return node.rowCount()
    def columnCount(self, index = Qt.QModelIndex()) -> int:
        node = self.node_at(index)
        return node.columnCount()

    def removeRows(self, row: int, count: int, parent: Qt.QModelIndex):
        node = self.node_at(parent)
        return node.removeRows(row, count)

    def data(self, index: Qt.QModelIndex, role: Qt.Qt.ItemDataRole):
        node = self.node_at(index)
        return node.data(role)
    def setData(self, index: Qt.QModelIndex, value: Any, role: Qt.Qt.ItemDataRole):
        node = self.node_at(index)
        return node.setData(value, role)
    def flags(self, index: Qt.QModelIndex) -> Qt.Qt.ItemFlag:
        node = self.node_at(index)
        return node.flags()

    def supportedDropActions(self) -> Qt.Qt.DropAction:
        return Qt.Qt.DropAction.CopyAction | Qt.Qt.DropAction.MoveAction
    def supportedDragActions(self) -> Qt.Qt.DropAction:
        return Qt.Qt.DropAction.CopyAction | Qt.Qt.DropAction.MoveAction

    def mimeTypes(self) -> list[str]:
        return self._mime_types
    def mimeData(self, indices: list[Qt.QModelIndex]) -> Optional[Qt.QMimeData]:
        index_list = [index for index in indices]
        if len(index_list) != 1:
            # No multiple drags yet
            return None
        [index] = index_list
        node = self.node_at(index)
        return node.mime_export()
    def canDropMimeData(self, mimeData: Qt.QMimeData, action: Qt.Qt.DropAction, row: int, column: int, parent: Qt.QModelIndex) -> bool:
        node = self.node_at(parent)
        if row == -1 and column == -1:
            return node.can_mime_import_self(mimeData, action)
        else:
            return node.can_mime_import_child(mimeData, action, row, column)
    def dropMimeData(self, mimeData: Qt.QMimeData, action: Qt.Qt.DropAction, row: int, column: int, parent: Qt.QModelIndex):
        node = self.node_at(parent)
        if row == -1 and column == -1:
            return node.mime_import_self(mimeData, action)
        else:
            return node.mime_import_child(mimeData, action, row, column)

    def parent(self, index: Qt.QModelIndex) -> Qt.QModelIndex:
        node = self.node_at(index)
        return node.parent_index()
    def index(self, row: int, column: int, parent: Qt.QModelIndex = Qt.QModelIndex()) -> Qt.QModelIndex:
        node = self.node_at(parent)
        return node.child(row, column).self_index()

class SchemaItemDelegate(Qt.QStyledItemDelegate):
    needPersistent = Qt.Signal(Qt.QModelIndex)

    def __init__(self, item_model: SchemaItemModel, parent = None):
        super().__init__(parent)
        self._item_model: SchemaItemModel = item_model

    def createEditor(self, parent: Qt.QWidget, option: Qt.QStyleOptionViewItem, index: Qt.QModelIndex) -> Optional[Qt.QWidget]:
        node = self._item_model.node_at(index)
        editor = node.createEditor(parent)
        if editor is not None:
            return editor
        return super().createEditor(parent, option, index)

    def setEditorData(self, editor: Qt.QWidget, index: Qt.QModelIndex) :
        node = self._item_model.node_at(index)
        if not node.setEditorData(editor):
            super().setEditorData(editor, index)
    def setModelData(self, editor: Qt.QWidget, model: Qt.QAbstractItemModel, index: Qt.QModelIndex):
        node = self._item_model.node_at(index)
        if not node.setModelData(editor):
            super().setModelData(editor, model, index)

    def destroyEditor(self, editor: Qt.QWidget, index: Qt.QModelIndex):
        if self._item_model.node_at(index).destroyEditor():
            super().destroyEditor(editor, index)

    def eventFilter(self, editor, event):
        if isinstance(editor, Qt.QDialog):
            if event.type() in (Qt.QEvent.Type.Hide, Qt.QEvent.Type.Destroy):
                return super().eventFilter(editor, event)
            if editor.event(event):
                return True
        return super().eventFilter(editor, event)

    def sizeHint(self, option: Qt.QStyleOptionViewItem, index: Qt.QModelIndex) -> Qt.QSize:
        editor = self._item_model.node_at(index).editor()
        if editor is not None:
            return editor.sizeHint()
        return super().sizeHint(option, index)

    def paint(self, painter: Qt.QPainter, option: Qt.QStyleOptionViewItem, index: Qt.QModelIndex):
        node = self._item_model.node_at(index)
        if node.data(Qt.Qt.ItemDataRole.DisplayRole) is None:
            self.needPersistent.emit(index)
        else:
            if not node.paint(painter, option):
                super().paint(painter, option, index)

class SchemaView(Qt.QTreeView):
    selection_changed = Qt.Signal(Any)

    def __init__(self, schema: Schema, model: Any, **kwargs):
        super().__init__(**kwargs)
        self.setHeaderHidden(True)
        self.setDragDropMode(self.DragDropMode.DragDrop)
        self.setDefaultDropAction(Qt.Qt.DropAction.MoveAction)
        self.setContextMenuPolicy(Qt.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._make_custom_context_menu)
        self.showDropIndicator()

        self._item_model: SchemaItemModel = SchemaItemModel(schema, model)
        self.setModel(self._item_model)
        item_delegate = SchemaItemDelegate(self._item_model, self)
        self.setItemDelegate(item_delegate)
        item_delegate.needPersistent.connect(lambda index: self.openPersistentEditor(index))

        self._item_model.rowsAboutToBeRemoved.connect(lambda *__args__: self.selectionModel().clear())
        self.selectionModel().currentChanged.connect(self.__on_current_changed)

    @Qt.Slot(Any, Any)
    def __on_current_changed(self, current, previous):
        current = self._item_model.node_at(current)
        return self.selection_changed.emit(current)

    @Qt.Slot(Qt.QPoint) # type: ignore
    def _make_custom_context_menu(self, position):
        item_index = self.indexAt(position)
        node = self._item_model.node_at(item_index)
        menu = node.context_menu(self)
        if menu is not None:
            menu.exec_(self.mapToGlobal(position))
