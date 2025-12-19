from .Schema import Schema
from .__prelude__ import ObservableList, Qt

class ListRoles:
    def __init__(self, display):
        self._display = display

    def data(self, role):
        if role == Qt.Qt.ItemDataRole.DisplayRole:
            return self._display
        return None

    def context_menu(self, parent_widget, node):
        return None

class ListIconRoles(ListRoles):
    def __init__(self, display, icon_name):
        super().__init__(display)
        self._icon_name = icon_name
    def data(self, role):
        if role == Qt.Qt.ItemDataRole.DecorationRole:
            return Qt.QIcon(self._icon_name)
        return super().data(role)

class ListSchema(Schema):
    """A schema for lists of objects.

    TODO_DOC
    """
    class ListNode(Schema.Node):
        def __init__(self, item_model, schema, model):
            super().__init__(item_model, schema)
            self._init_model(model)

        @property
        def elemSchema(self):
            return self._schema.elemSchema
        @property
        def list_roles(self):
            return self._schema.list_roles

        @Qt.Slot(int, int) # type: ignore
        def begin_remove_rows(self, start, stop):
            self.beginRemoveRows.emit(start, stop)
        @Qt.Slot(int, int) # type: ignore
        def end_remove_rows(self, start, stop):
            self.endRemoveRows.emit(start, stop)
        @Qt.Slot(int, int) # type: ignore
        def begin_insert_rows(self, start, l):
            self.beginInsertRows.emit(start, l)
        @Qt.Slot(int, int) # type: ignore
        def end_insert_rows(self, start, l):
            self.endInsertRows.emit(start, l)
        @Qt.Slot(int, int) # type: ignore
        def end_replace_rows(self, start, end):
            for i in range(start, end):
                child = self.cached_child(i,0)
                if child is not None:
                    child.set_model(self.model[i])

        def _exit_model(self):
            if hasattr(self, 'model') and isinstance(self.model, ObservableList):
                self.model.beginRemoveRange.disconnect(self.begin_remove_rows)
                self.model.endRemoveRange.disconnect(self.end_remove_rows)
                self.model.beginInsertRange.disconnect(self.begin_insert_rows)
                self.model.endInsertRange.disconnect(self.end_insert_rows)
                self.model.endReplaceRange.disconnect(self.end_replace_rows)
            super()._exit_model()
        def _init_model(self, model):
            super()._init_model(model)
            if isinstance(self.model, ObservableList):
                self.model.beginRemoveRange.connect(self.begin_remove_rows)
                self.model.endRemoveRange.connect(self.end_remove_rows)
                self.model.beginInsertRange.connect(self.begin_insert_rows)
                self.model.endInsertRange.connect(self.end_insert_rows)
                self.model.endReplaceRange.connect(self.end_replace_rows)

        def rowCount(self):
            return len(self.model)
        def columnCount(self):
            return 1
        def removeRows(self, row, count):
            self.model[row:row+count] = []
            return True
        def flags(self):
            return Qt.Qt.ItemFlag.ItemIsDropEnabled | super().flags()
        def data(self, role):
            return self.list_roles.data(role)
        def create_child_node(self, row, __column__):
            child = self.elemSchema.make_node(self._item_model(), self.model[row])
            def on_child_model_change(child_model):
                row = child._self_index.row()
                self.model[row] = child_model
            child.requestModelChange.connect(on_child_model_change)
            return child

        def context_menu(self, parent_widget):
            return self.list_roles.context_menu(parent_widget, self)

        # Drag and drop
        def can_mime_import_self(self, mimeData, __action__, **kwargs):
            # Allow dropping a child onto the list if it is empty
            if len(self.model) == 0:
                return self.elemSchema.can_model_from_mime(mimeData, **kwargs, **self.model.import_context())
            return False
        def mime_import_self(self, mimeData, __action__, **kwargs):
            new_item = self.elemSchema.model_from_mime(mimeData, **kwargs, **self.model.import_context())
            if new_item is None:
                return False
            self.model[0:0] = [new_item]
            return True

        def can_mime_import_child(self, mimeData, __action__, __row__, __column__, **kwargs):
            return self.elemSchema.can_model_from_mime(mimeData, **kwargs, **self.model.import_context())
        def mime_import_child(self, mimeData, __action__, row, __column__, **kwargs):
            new_item = self.elemSchema.model_from_mime(mimeData, **kwargs, **self.model.import_context())
            if new_item is None:
                return False
            self.model[row:row] = [new_item]
            return True

    def __init__(self, display, elemSchema):
        super().__init__()
        if isinstance(display, str):
            self.list_roles = ListRoles(display)
        else:
            self.list_roles = display
        self.elemSchema = elemSchema
    def make_node(self, item_model, model):
        return self.ListNode(item_model, self, model)

    def supported_mime_types(self):
        return self.elemSchema.supported_mime_types()
