from .Schema import Schema

class UnionSchema(Schema):
    class UnionSchemaNode(Schema.Node):
        def __init__(self, item_model, schema, model):
            super().__init__(item_model, schema)
            self._alt_node: Schema.Node
            self.set_model(model)

        def set_model(self, model):
            classSchema = self._schema._alts.get(model.__class__)
            if classSchema is None:
                self._alt_node = Schema.Node(self.item_model(), self._schema)
            else:
                self._alt_node = classSchema.make_node(self.item_model(), model)
            super().set_model(model)

        def rowCount(self):
            return self._alt_node.rowCount()
        def columnCount(self):
            return self._alt_node.columnCount()
        def removeRows(self, row, count):
            return self._alt_node.removeRows(row, count)
        def flags(self):
            return self._alt_node.flags()
        def data(self, role):
            return self._alt_node.data(role)
        def setData(self, value, role):
            return self._alt_node.setData(value, role)
        def create_child_node(self, row, column):
            return self._alt_node.create_child_node(row, column)

        def createEditor(self, parent):
            return self._alt_node.createEditor(parent)
        def destroyEditor(self):
            return self._alt_node.destroyEditor()
        def editor(self):
            return self._alt_node.editor()
        def setEditorData(self, editor):
            return self._alt_node.setEditorData(editor)
        def setModelData(self, editor):
            return self._alt_node.setModelData(editor)

        def context_menu(self, parent_widget):
            return self._alt_node.context_menu(parent_widget)
        def paint(self, painter, option):
            return self._alt_node.paint(painter, option)

        def set_links(self, parent_index, self_index):
            super().set_links(parent_index, self_index)
            if self._alt_node is not None:
                self._alt_node.set_links(parent_index, self_index)

    def __init__(self, *alts):
        super().__init__()
        self._alts = {klass: schema for klass, schema in alts}

    def make_node(self, item_model, model):
        return self.UnionSchemaNode(item_model, self, model)

    def supported_mime_types(self):
        ret = set()
        for alt in self._alts.values():
            ret = ret | alt.supported_mime_types()
        return ret
    def can_model_from_mime(self, mimeData, /, **kwargs):
        for alt in self._alts.values():
            if alt.can_model_from_mime(mimeData, **kwargs):
                return True
        return False
    def model_from_mime(self, mimeData, /, **kwargs):
        for alt in self._alts.values():
            if alt.can_model_from_mime(mimeData, **kwargs):
                return alt.model_from_mime(mimeData, **kwargs)
        return None
    def can_mime_from_model(self, model):
        for klass, alt in self._alts.items():
            if isinstance(model, klass) and alt.can_mime_from_model(model):
                return True
        return False
    def mime_from_model(self, model):
        for klass, alt in self._alts.items():
            if isinstance(model, klass):
                return alt.mime_from_model(model)
        return None
