from typing import Any, Optional
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QMenu

from .__prelude__ import ObservableStruct

from .Schema import Schema

class StructRoles:
    @staticmethod
    def flags():
        return Qt.ItemFlag(0)
    @staticmethod
    def field_roles(__field__: str, /) -> Optional[list[Qt.ItemDataRole]]:
        return None
    @staticmethod
    def get_role(__model__: Any, __role__: Qt.ItemDataRole, /) -> Any:
        return None
    @staticmethod
    def set_role(__model__: Any, __role__: Qt.ItemDataRole, __value__: Any, /) -> bool:
        return False
    @staticmethod
    def context_menu(__parent_widget__, __node__, /) -> Optional[QMenu]:
        return None

class StructSchema(Schema):
    class StructNode(Schema.Node):
        def __init__(self, item_model, schema, model):
            super().__init__(item_model, schema)
            self.fieldRows = {name: i for i, (name, _) in zip(range(len(self.fields)), self.fields)}
            self._init_model(model)

        @property
        def fields(self):
            return self._schema.fields
        @property
        def struct_roles(self):
            return self._schema.struct_roles

        @Slot(str) #type: ignore
        def _on_field_changed(self, field):
            roles = self.struct_roles.field_roles(field)
            if roles is not None:
                self.dataChanged.emit(roles)

            if field not in self.fieldRows:
                return
            row = self.fieldRows[field]
            child = self.cached_child(row, 0)
            if child is None:
                return
            child.set_model(getattr(self.model,field))
        def _exit_model(self):
            if hasattr(self, 'model') and isinstance(self.model, ObservableStruct):
                self.model.fieldChanged.disconnect(self._on_field_changed)
            super()._exit_model()
        def _init_model(self, model):
            super()._init_model(model)
            if isinstance(model, ObservableStruct):
                model.fieldChanged.connect(self._on_field_changed)

        def rowCount(self):
            return len(self.fields)
        def flags(self):
            return self.struct_roles.flags() | super().flags()
        def data(self, role):
            return self.struct_roles.get_role(self.model, role)
        def setData(self, value, role):
            return self.struct_roles.set_role(self.model, role, value)
        def context_menu(self, parent_widget):
            return self.struct_roles.context_menu(parent_widget, self)

        def create_child_node(self, row, __column__):
            fieldName, fieldSchema = self.fields[row]
            child = fieldSchema.make_node(self._item_model(), getattr(self.model, fieldName))
            def on_child_edited(child_model):
                setattr(self.model, fieldName, child_model)
            child.requestModelChange.connect(on_child_edited)
            return child

    def __init__(self, klass, struct_roles, *fields):
        self.klass = klass
        self.struct_roles = struct_roles
        self.fields = fields
    def make_node(self, item_model, model):
        return self.StructNode(item_model, self, model)

    def supported_mime_types(self):
        ret = set()
        if self.klass.__mime_type__ is not None:
            ret.add(self.klass.__mime_type__)
        for _, fieldSchema in self.fields:
            ret = ret | fieldSchema.supported_mime_types()
        return ret

    def can_mime_from_model(self, __model__):
        return self.klass.__mime_type__ is not None
    def mime_from_model(self, model):
        return model.to_mime()
    def can_model_from_mime(self, mimeData, **kwargs):
        return self.klass.can_from_mime(mimeData, **kwargs)
    def model_from_mime(self, mimeData, **kwargs):
        return self.klass.from_mime(mimeData, **kwargs)

def MaybeStructRoles(StructRoles):
    class Ret(StructRoles):
        @staticmethod
        def flags():
            return StructRoles.flags() | Qt.ItemFlag.ItemIsUserCheckable
        @staticmethod
        def field_roles(field):
            if field == "is_enabled":
                return [Qt.ItemDataRole.CheckStateRole]
        @staticmethod
        def get_role(model, role):
            if role == Qt.ItemDataRole.CheckStateRole:
                return Qt.Checked if model.is_enabled else Qt.Unchecked
            return StructRoles.get_role(model, role)
        @staticmethod
        def set_role(model, role, value):
            if role == Qt.ItemDataRole.CheckStateRole:
                model.is_enabled = value == Qt.Checked.value
                return True
            return StructRoles.set_role(model, role, value)
    return Ret

class MaybeStructSchema(StructSchema):
    class MaybeStructNode(StructSchema.StructNode):
        def __init__(self, item_model, schema, model):
            super().__init__(item_model, schema, model)

        @Slot(str, Any) #type: ignore
        def _on_field_changed(self, field, old_val):
            if field == "is_enabled":
                count = super().rowCount()
                if old_val != self.model.is_enabled:
                    if self.model.is_enabled:
                        self.beginInsertRows.emit(0, count)
                        self.endInsertRows.emit(0, count)
                    else:
                        self.beginRemoveRows.emit(0, count)
                        self.endRemoveRows.emit(0, count)
                    self.dataChanged.emit([Qt.ItemDataRole.CheckStateRole])
            else:
                if self.model.is_enabled:
                    return super()._on_field_changed(field)

        def rowCount(self):
            return super().rowCount() if self.model.is_enabled else 0

    def __init__(self, klass, struct_roles, *fields):
        super().__init__(klass, MaybeStructRoles(struct_roles), *fields)
    def make_node(self, item_model, model):
        return self.MaybeStructNode(item_model, self, model)
