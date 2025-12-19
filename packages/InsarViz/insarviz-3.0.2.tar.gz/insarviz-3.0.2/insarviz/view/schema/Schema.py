import weakref
from typing import Any, Optional
from PySide6.QtCore import QMimeData, Qt, QObject, Signal, Slot, QModelIndex, QAbstractItemModel
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QMenu, QStyleOption, QWidget

class Schema:
    """Abtract class for schemas.

    When creating an item model for Qt (to show in QAbstractItemViews),
    you need to provide a way to represent an underlying data
    structure as a QAbstractItemModel.

    A schema is a sort of translation layer between a Python structure
    (a list, a class, or a plain data type) and a
    QAbstractItemModel. It describes the shape of the structure in a
    way that Qt can navigate.

    Qt's tree model is rather simple, albeit a bit cumbersome for
    complex structures : every level of a tree is a node that can
    provide some data (through the 'data' function), and may contain
    sub-nodes. A QModelIndex is a sort of pointer into such a
    tree. From a given QModelIndex, Qt should be able to access its
    data, parent, and children, which allows it access to the whole
    structure.

    A schema, at its core, simply takes values of some type, and for
    each value creates a 'Node' object that provides all the above
    information for that value.
    """

    class Node[Parent : "Schema", Model](QObject):
        """The base Schema.Node class.

        This class provides all the default behaviour of an empty
        QAbstractItemModel tree, as needed by the SchemaItemModel and
        SchemaItemDelegate classes.

        TODO_DOC

        """
        requestModelChange = Signal(Any) # type: ignore

        dataChanged = Signal(list)
        beginRemoveRows = Signal(int, int)
        endRemoveRows = Signal(int, int)
        beginInsertRows = Signal(int, int)
        endInsertRows = Signal(int, int)
        beginReplaceRows = Signal(int, int)
        endReplaceRows = Signal(int, int)

        def __init__(self, item_model: QAbstractItemModel, schema: Parent):
            super().__init__()
            self.model: Model
            self._schema : Parent = schema
            self._parent_index : Optional[QModelIndex] = None
            self._self_index   : Optional[QModelIndex] = None
            self._item_model = weakref.ref(item_model)
            self._children : list[list[Optional["Schema.Node"]]] = []

        @Slot(list) # type: ignore
        def _on_data_changed(self, roles):
            if self._self_index is None:
                return
            if self._self_index.isValid():
                item_model = self._item_model()
                if item_model is not None:
                    item_model.dataChanged.emit(self._self_index, self._self_index, roles)
        @Slot(int, int) # type: ignore
        def _on_begin_remove_rows(self, start, stop):
            if self._self_index is None:
                return
            item_model = self._item_model()
            if item_model is not None:
                item_model.beginRemoveRows(self._self_index, start, stop-1)
        @Slot(int, int) # type: ignore
        def _on_end_remove_rows(self, start, stop):
            if self._self_index is None:
                return
            for i in range(start, stop):
                for child in self._children[i]:
                    if child is not None:
                        child._disconnect_signals()
            self._children[start:stop] = []
            item_model = self._item_model()
            if item_model is not None:
                item_model.endRemoveRows()
        @Slot(int, int) # type: ignore
        def _on_begin_insert_rows(self, start, length):
            if self._self_index is None:
                return
            item_model = self._item_model()
            if item_model is not None:
                item_model.beginInsertRows(self._self_index, start, start+length-1)
        @Slot(int, int) # type: ignore
        def _on_end_insert_rows(self, start, length):
            if self._self_index is None:
                return
            self._children[start:start] = [[None] for _ in range(length)]
            item_model = self._item_model()
            if item_model is not None:
                item_model.endInsertRows()

        def _connect_signals(self):
            if self._self_index is None:
                return
            self.dataChanged.connect(self._on_data_changed)
            self.beginRemoveRows.connect(self._on_begin_remove_rows)
            self.endRemoveRows.connect(self._on_end_remove_rows)
            self.beginInsertRows.connect(self._on_begin_insert_rows)
            self.endInsertRows.connect(self._on_end_insert_rows)
        def _disconnect_signals(self):
            if self._self_index is None:
                return
            self.dataChanged.disconnect(self._on_data_changed)
            self.beginRemoveRows.disconnect(self._on_begin_remove_rows)
            self.endRemoveRows.disconnect(self._on_end_remove_rows)
            self.beginInsertRows.disconnect(self._on_begin_insert_rows)
            self.endInsertRows.disconnect(self._on_end_insert_rows)
        def _init_model(self, model):
            self.model = model
            rowcount_after = self.rowCount()
            if rowcount_after > 0:
                self.beginInsertRows.emit(0, rowcount_after)
            self._children = [[None for _ in range(self.columnCount())]
                              for _ in range(self.rowCount())]
            if rowcount_after > 0:
                self.endInsertRows.emit(0, rowcount_after)
            self._connect_signals()
        def _exit_model(self):
            rowcount_before = self.rowCount()
            if rowcount_before > 0:
                self.beginRemoveRows.emit(0, rowcount_before)
            for childRow in self._children:
                for child in childRow:
                    if child is not None:
                        child._disconnect_signals()
            if rowcount_before > 0:
                self.endRemoveRows.emit(0, rowcount_before)
            self._disconnect_signals()
        def set_model(self, model: Any):
            """Change the underlying model for this node.

            May be reimplemented by subclasses, depending on whether
            the node needs to be connected/disconnected to signals
            from the model.

            Usually, when resetting the model, you'd first disconnect
            from the previous model, then call
            super().set_model(model), and finally connect to the new
            model.
            """
            self._exit_model()
            self._init_model(model)

        # Act as a QAbstractItemModel node
        def rowCount(self) -> int:
            return 0
        def columnCount(self) -> int:
            return 1
        def removeRows(self, __row__: int, __count__: int, /) -> bool:
            return False
        def flags(self):
            flags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsDropEnabled
            if self._schema.can_mime_from_model(self.model):
                flags = flags | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsDragEnabled
            return flags
        def data(self, __role__: Qt.ItemDataRole, /):
            return None
        def setData(self, __value__: Any, __role__: Qt.ItemDataRole, /) -> bool:
            return False
        def create_child_node(self, __row__: int, __column__: int, /) -> "Schema.Node":
            raise NotImplementedError
        def child(self, row: int, column: int) -> "Schema.Node":
            child = self._children[row][column]
            if child is None:
                child = self.create_child_node(row, column)
                self._children[row][column] = child
            model = self.item_model()
            child_index = model.createIndex(row, column, child)
            child.set_links(self.self_index(), child_index)
            return child

        # Create and manage custom editors
        def createEditor(self, __parent__: QWidget, /) -> Optional[QWidget]:
            return None
        def destroyEditor(self) -> bool:
            return True
        def editor(self) -> Optional[QWidget]:
            return None
        def setEditorData(self, __editor__: QWidget, /) -> bool:
            return False
        def setModelData(self, __editor__: QWidget, /) -> bool:
            return False

        # Custom context menus
        def context_menu(self, parent_widget) -> Optional[QMenu]:
            return None

        # Custom painting
        def paint(self, __painter__: QPainter, __option__: QStyleOption, /) -> bool:
            return False

        # Drag and drop
        def mime_export(self) -> Optional[QMimeData]:
            """Produce a QMimeData containing a serialized
            representation of the model, or None if the model can't be
            dragged"""
            return self._schema.mime_from_model(self.model)
        def can_mime_import_self(self, mimeData: QMimeData, __action__: Qt.DropAction, **kwargs) -> bool:
            """Check whether the data is in a suitable format for
            importing into this node"""
            return self._schema.can_model_from_mime(mimeData, **kwargs)
        def mime_import_self(self, mimeData: QMimeData, __action__: Qt.DropAction, **kwargs) -> bool:
            """Import the given data into the model. Return True if the import succeeded"""
            model = self._schema.model_from_mime(mimeData, **kwargs)
            if model is None:
                return False
            self.requestModelChange.emit(model)
            return True
        def can_mime_import_child(self, __mimeData__, __action__, __row__, __column__, /, **kwargs) -> bool:
            """Check whether the data can be inserted as a child of this node"""
            __kwargs__ = kwargs
            return False
        def mime_import_child(self, __mimeData__, __action__, __row__, __column__, / , **kwargs) -> bool:
            """Insert the given data as a child of this node. Return True if the import succeeded"""
            __kwargs__ = kwargs
            return False

        # Internal methods used by SchemaItemModel (do not override in subclasses)
        def item_model(self) -> QAbstractItemModel:
            ret = self._item_model()
            if ret is None:
                raise Exception(f"No valid item model for node {self}")
            return ret
        def set_links(self, parent_index, self_index):
            self._disconnect_signals()
            self._parent_index = parent_index
            self._self_index = self_index
            self._connect_signals()
        def cached_child(self, row, column):
            return self._children[row][column]
        def parent_index(self):
            return self._parent_index
        def self_index(self):
            return self._self_index

    def make_node(self, item_model: QAbstractItemModel, __model__: Any, /) -> "Schema.Node":
        return self.Node[Schema, Any](item_model, self)

    def supported_mime_types(self) -> set[str]:
        return set()
    def can_model_from_mime(self, __mimeData__: QMimeData, /, **kwargs) -> bool:
        __kwargs__ = kwargs
        return False
    def model_from_mime(self, __mimeData__: QMimeData, /, **kwargs) -> Optional[Any]:
        __kwargs__ = kwargs
        return None
    def can_mime_from_model(self, __model__: Any, /) -> bool:
        return False
    def mime_from_model(self, __model__: Any, /) -> Optional[QMimeData]:
        return None
