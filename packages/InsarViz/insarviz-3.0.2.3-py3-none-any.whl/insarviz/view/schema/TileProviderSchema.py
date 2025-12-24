import xyzservices.providers

from .__prelude__ import Qt
from .Schema import Schema

PROVIDERS = {
    "OpenStreetMap": xyzservices.providers["OpenStreetMap"]["Mapnik"],
    "USGS": xyzservices.providers["USGS"]["USImagery"],
    "Esri World Topo": xyzservices.providers["Esri"]["WorldTopoMap"],
}
for p in PROVIDERS:
    PROVIDERS[p].name = p

class TileProviderSchema(Schema):
    class TileProviderNode(Schema.Node):
        def __init__(self, item_model, schema, model):
            super().__init__(item_model, schema)
            self.set_model(model)
            self.__editor = Qt.QComboBox()
            for p in PROVIDERS:
                self.__editor.addItem(p, p)
            def on_change(index):
                data = self.__editor.itemData(index)
                self.requestModelChange.emit(PROVIDERS[data])
            self.__editor.currentIndexChanged.connect(on_change)

        def editor(self):
            return self.__editor
        def createEditor(self, parent):
            self.__editor.setParent(parent)
            return self.__editor
        def destroyEditor(self):
            return True
        def setEditorData(self, editor):
            # TODO
            return True
        def setModelData(self, editor):
            data = editor.itemData(editor.currentIndex())
            self.requestModelChange.emit(PROVIDERS[data])
            return True

        def set_model(self, model):
            super().set_model(model)
            self.dataChanged.emit([])

    def make_node(self, item_model, model):
        return self.TileProviderNode(item_model,self,model)

    def supported_mime_types(self):
        return set(["application/x-insarviz-tile_provider"])
    def can_model_from_mime(self, mimeData):
        return mimeData.hasFormat("application/x-insarviz-tile_provider")
    def model_from_mime(self, mimeData):
        data_bytes = mimeData.data("application/x-insarviz-tile_provider").data()
        provider = json.loads(bytearray(data_bytes))
        return PROVIDERS[provider['name']]
    def can_mime_from_model(self, model):
        return True
    def mime_from_model(self, model):
        mimeData = QMimeData()
        dic = {
            "name": model.name
        }
        mimeData.setData("application/x-insarviz-tile_provider", bytes(json.dumps(dic), "utf-8"))
        return mimeData
