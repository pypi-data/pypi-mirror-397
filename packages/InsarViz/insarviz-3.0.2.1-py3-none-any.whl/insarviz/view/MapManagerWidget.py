import os

from .__prelude__ import (
    logger, Qt,
    WindowState, MaybeBandNumber, MapPoint, MapProfile,
    SwipeLayer, PointsLayer, SelectedBandLayer, RasterLayer, RasterRGBLayer, Layer,
    Dataset,
)
from .schema import (
    SchemaView, StructSchema, MaybeStructSchema, StructRoles, IntSchema, IntSliderSchema,
    ColorSchema, ListSchema, ListRoles, ListIconRoles, UnionSchema,
    FloatSliderSchema, FloatSchema, StringSchema, ColorMapSchema,
    TileProviderSchema
)
from .GLWidget import GLWidget
from .RasterLayerDialog import RasterLayerDialog
from .WidgetTree import Container, Leaf

class MapPointRoles(StructRoles):
    @staticmethod
    def flags():
        return Qt.Qt.ItemFlag.ItemIsEnabled | Qt.Qt.ItemFlag.ItemIsEditable | Qt.Qt.ItemFlag.ItemIsUserCheckable
    @staticmethod
    def field_roles(field):
        if field == "color":
            return [Qt.Qt.ItemDataRole.DecorationRole]
        if field == "name":
            return [Qt.Qt.ItemDataRole.DisplayRole]
        if field == "show_in_map":
            return [Qt.Qt.ItemDataRole.CheckStateRole]
        return None

    @staticmethod
    def get_role(model, role):
        if role == Qt.Qt.ItemDataRole.DisplayRole:
            return model.name
        if role == Qt.Qt.ItemDataRole.DecorationRole:
            return model.color
        if role == Qt.Qt.ItemDataRole.CheckStateRole:
            return Qt.Qt.CheckState.Checked if model.show_in_map else Qt.Qt.CheckState.Unchecked
    @staticmethod
    def set_role(model, role, value):
        if role == Qt.Qt.ItemDataRole.EditRole:
            model.name = value
            return True
        if role == Qt.Qt.ItemDataRole.CheckStateRole:
            model.show_in_map = (value == Qt.Qt.CheckState.Checked.value)
            return True
        return False

    @staticmethod
    def context_menu(parent_widget, node):
        ret = Qt.QMenu()
        node._action1 = Qt.QAction("Remove")
        def remove_self():
            me = node.self_index()
            if me.isValid():
                me.model().removeRow(me.row(), node.parent_index())
        node._action1.triggered.connect(remove_self)
        ret.addAction(node._action1)
        return ret

point_schema = StructSchema(MapPoint, MapPointRoles,
                            ("color", ColorSchema()),
                            ("r", IntSliderSchema("Radius")))

class MapProfileRoles(StructRoles):
    @staticmethod
    def flags():
        return Qt.Qt.ItemFlag.ItemIsEnabled | Qt.Qt.ItemFlag.ItemIsEditable | Qt.Qt.ItemFlag.ItemIsUserCheckable
    @staticmethod
    def field_roles(field):
        if field == "color":
            return [Qt.Qt.ItemDataRole.DecorationRole]
        if field == "name":
            return [Qt.Qt.ItemDataRole.DisplayRole]
        if field == "show_in_map":
            return [Qt.Qt.ItemDataRole.CheckStateRole]
        return None

    @staticmethod
    def get_role(model, role):
        if role == Qt.Qt.ItemDataRole.DisplayRole:
            return model.name
        if role == Qt.Qt.ItemDataRole.DecorationRole:
            return model.color
        if role == Qt.Qt.ItemDataRole.CheckStateRole:
            return Qt.Qt.CheckState.Checked if model.show_in_map else Qt.Qt.CheckState.Unchecked
    @staticmethod
    def set_role(model, role, value):
        if role == Qt.Qt.ItemDataRole.EditRole:
            model.name = value
            return True
        if role == Qt.Qt.ItemDataRole.CheckStateRole:
            model.show_in_map = (value == Qt.Qt.CheckState.Checked.value)
            return True
        return False

    @staticmethod
    def context_menu(parent_widget, node):
        ret = Qt.QMenu(parent_widget)
        node._action1 = Qt.QAction("Remove")
        def remove_self():
            me = node.self_index()
            if me.isValid():
                me.model().removeRow(me.row(), node.parent_index())
        node._action1.triggered.connect(remove_self)
        ret.addAction(node._action1)
        return ret

profile_schema = StructSchema(MapProfile, MapProfileRoles,
                              ("color", ColorSchema()),
                              ("r", IntSliderSchema("Radius")),
                              ("focus_point", FloatSliderSchema("Focus")))

class LayerRoles(StructRoles):
    @staticmethod
    def flags():
        return Qt.Qt.ItemFlag.ItemIsEnabled | Qt.Qt.ItemFlag.ItemIsUserCheckable
    @staticmethod
    def field_roles(field):
        if field == "is_enabled":
            return [Qt.Qt.ItemDataRole.CheckStateRole]
        return None
    @staticmethod
    def get_role(model, role):
        if role == Qt.Qt.ItemDataRole.CheckStateRole:
            return Qt.Qt.Checked if model.is_enabled else Qt.Qt.Unchecked
        return None
    @staticmethod
    def set_role(model, role, value):
        if role == Qt.Qt.ItemDataRole.CheckStateRole:
            model.is_enabled = value == Qt.Qt.Checked.value
            return True
        return False

class PointsLayerRoles(LayerRoles):
    @staticmethod
    def get_role(model, role):
        if role == Qt.Qt.ItemDataRole.DisplayRole:
            return "Points Layer"
        if role == Qt.Qt.ItemDataRole.DecorationRole:
            return Qt.QIcon('insarviz:points.png')
        return LayerRoles.get_role(model, role)

points_layer_schema = StructSchema(PointsLayer, PointsLayerRoles,
                                   ("opacity", FloatSliderSchema("Opacity")))

class SelectedBandLayerRoles(LayerRoles):
    @staticmethod
    def get_role(model, role):
        if role == Qt.Qt.ItemDataRole.DisplayRole:
            return "Selected band layer"
        return LayerRoles.get_role(model, role)

selected_band_layer_schema = StructSchema(SelectedBandLayer, SelectedBandLayerRoles,
                                          ("opacity", FloatSliderSchema("Opacity")),
                                          ("dem_weight", FloatSliderSchema("DEM scale")))

class SwipeLayerRoles(LayerRoles):
    @staticmethod
    def get_role(model, role):
        if role == Qt.Qt.ItemDataRole.DisplayRole:
            return "Swipe layer"
        if role == Qt.Qt.ItemDataRole.DecorationRole:
            return Qt.QIcon('insarviz:swipetool.png')
        return LayerRoles.get_role(model, role)
    @staticmethod
    def context_menu(parent_widget, node):
        ret = Qt.QMenu(parent_widget)
        node._action1 = Qt.QAction("Remove")
        def remove_self():
            me = node.self_index()
            if me.isValid():
                me.model().removeRow(me.row(), node.parent_index())
        node._action1.triggered.connect(remove_self)
        ret.addAction(node._action1)
        return ret
swipe_layer_schema = StructSchema(SwipeLayer, SwipeLayerRoles,
                                  ("cutoff", FloatSliderSchema("Cutoff")))

class RasterLayerRoles(LayerRoles):
    @staticmethod
    def get_role(model, role):
        if role == Qt.Qt.ItemDataRole.DisplayRole:
            return "Raster layer"
        if role == Qt.Qt.ItemDataRole.DecorationRole:
            return Qt.QIcon('insarviz:raster1B.svg')
        return LayerRoles.get_role(model, role)

    @staticmethod
    def context_menu(parent_widget, node):
        ret = Qt.QMenu(parent_widget)
        node._action1 = Qt.QAction("Remove")
        def remove_self():
            me = node.self_index()
            if me.isValid():
                me.model().removeRow(me.row(), node.parent_index())
        node._action1.triggered.connect(remove_self)
        ret.addAction(node._action1)
        return ret
raster_layer_schema = StructSchema(RasterLayer, RasterLayerRoles,
                                   ("description", StringSchema(is_editable=False)),
                                   ("colormap", ColorMapSchema("colormap")),
                                   ("opacity", FloatSliderSchema("Opacity")),
                                   ("dem_weight", FloatSliderSchema("DEM scale")),
                                   )

class RasterRGBLayerRoles(LayerRoles):
    @staticmethod
    def get_role(model, role):
        if role == Qt.Qt.ItemDataRole.DisplayRole:
            return "Raster RGB layer"
        if role == Qt.Qt.ItemDataRole.DecorationRole:
            return Qt.QIcon('insarviz:rasterRGB.svg')
        return LayerRoles.get_role(model, role)

    @staticmethod
    def context_menu(parent_widget, node):
        ret = Qt.QMenu(parent_widget)
        node._action1 = Qt.QAction("Remove")
        def remove_self():
            me = node.self_index()
            if me.isValid():
                me.model().removeRow(me.row(), node.parent_index())
        node._action1.triggered.connect(remove_self)
        ret.addAction(node._action1)
        return ret
raster_rgb_layer_schema = StructSchema(RasterRGBLayer, RasterRGBLayerRoles,
                                      ("description", StringSchema(is_editable=False)),
                                      ("opacity", FloatSliderSchema("Opacity")),
                                      )

class LayerListMenu(Qt.QMenu):
    def __init__(self, parent_widget, layer_list):
        super().__init__(parent_widget)
        self._layer_list = layer_list
        self._add_raster_layer_act = Qt.QAction(Qt.QIcon('insarviz:raster1B.svg'), "Add Raster Layer...")
        self._add_raster_layer_act.triggered.connect(self._add_raster_layer)
        self.addAction(self._add_raster_layer_act)
        self._add_raster_rgb_layer_act = Qt.QAction(Qt.QIcon('insarviz:rasterRGB.svg'), "Add Raster RGB Layer...")
        self._add_raster_rgb_layer_act.triggered.connect(self._add_raster_rgb_layer)
        self.addAction(self._add_raster_rgb_layer_act)
        self._add_swipe_layer_act = Qt.QAction(Qt.QIcon('insarviz:swipetool.png'), "Add Swipe Layer")
        self._add_swipe_layer_act.triggered.connect(self._add_swipe_layer)
        self.addAction(self._add_swipe_layer_act)

    @Qt.Slot()
    def _add_raster_layer(self):
        dataset_file, _ = Qt.QFileDialog.getOpenFileName(self.parent(), "Open Dataset", os.getcwd(), "Dataset (*.tiff *.tif *.h5 depl_cumule)")
        if dataset_file is None or dataset_file == "":
            logger.warn("Raster dataset not provided. Aborting raster layer creation")
            return
        dataset = Dataset(dataset_file)
        dialog = RasterLayerDialog(dataset)
        dialog.exec()
        layer = RasterLayer(dataset, dialog.band_number)
        self._layer_list.append(layer)

    @Qt.Slot()
    def _add_raster_rgb_layer(self):
        dataset_file, _ = Qt.QFileDialog.getOpenFileName(self.parent(), "Open RGB Dataset", os.getcwd(), "Dataset (*.tiff *.tif *.h5 depl_cumule)")
        if dataset_file is None or dataset_file == "":
            logger.warn("Raster RGB dataset not provided. Aborting RGB raster layer creation")
            return
        dataset = Dataset(dataset_file)
        layer = RasterRGBLayer(dataset)
        self._layer_list.append(layer)

    @Qt.Slot()
    def _add_swipe_layer(self):
        self._layer_list.append(SwipeLayer())

class LayerListRoles(ListRoles):
    def __init__(self):
        super().__init__("Layers")

    def context_menu(self, parent_widget, node):
        return LayerListMenu(parent_widget, node.model)

class TileProviderRoles(StructRoles):
    @staticmethod
    def flags():
        return Qt.Qt.ItemFlag.ItemIsEnabled
    @staticmethod
    def get_role(model, role):
        if role == Qt.Qt.ItemDataRole.DisplayRole:
            return "Tile provider: {model.name}"

class MaybeBandNumberRoles(StructRoles):
    @staticmethod
    def flags():
        return Qt.Qt.ItemFlag.ItemIsEnabled
    @staticmethod
    def get_role(model, role):
        if role == Qt.Qt.ItemDataRole.DisplayRole:
            return "Reference band"

window_state_schema = StructSchema(WindowState, StructRoles,
                                   ("band_number", IntSchema("Current band")),
                                   ("maybe_reference_band", MaybeStructSchema(MaybeBandNumber, MaybeBandNumberRoles,
                                                                              ("band_number", IntSchema("band")))),
                                   ("points", ListSchema(ListIconRoles("Points", "insarviz:points.png"), point_schema)),
                                   ("profiles", ListSchema(ListIconRoles("Profiles", "insarviz:profile.png"), profile_schema)),
                                   ("layers", ListSchema(LayerListRoles(), UnionSchema(
                                       (PointsLayer, points_layer_schema),
                                       (SelectedBandLayer, selected_band_layer_schema),
                                       (RasterLayer, raster_layer_schema),
                                       (RasterRGBLayer, raster_rgb_layer_schema),
                                       (SwipeLayer, swipe_layer_schema),
                                   ))),
                                   ("tile_provider", TileProviderSchema()))

class LayerActions(Qt.QActionGroup):
    request_selection_change = Qt.Signal(Qt.QModelIndex)

    def __init__(self, parent, layers, points, profiles):
        super().__init__(parent)
        self.__layers = layers
        self.__points = points
        self.__profiles = profiles
        self.__selected_item = None
        self.__item_list = None

        self.__show_all_action = Qt.QAction(Qt.QIcon("insarviz:eye_open.svg"), "Show All", self)
        self.__show_all_action.triggered.connect(self.__show_all_layers)
        self.__hide_all_action = Qt.QAction(Qt.QIcon("insarviz:eye_closed.svg"), "Hide All", self)
        self.__hide_all_action.triggered.connect(self.__hide_all_layers)
        self.__move_up_action = Qt.QAction(Qt.QIcon("insarviz:arrowup.png"), "Move Up", self)
        self.__move_up_action.triggered.connect(lambda: self.__move_item(-1))
        self.__move_down_action = Qt.QAction(Qt.QIcon("insarviz:arrowdown.png"), "Move Down", self)
        self.__move_down_action.triggered.connect(lambda: self.__move_item(1))
        self.__delete_action = Qt.QAction(Qt.QIcon("insarviz:remove.png"), "Remove", self)
        self.__delete_action.triggered.connect(self.__remove_item)

        self.addAction(self.__show_all_action)
        self.addAction(self.__hide_all_action)
        self.addAction(self.__move_up_action)
        self.addAction(self.__move_down_action)
        self.addAction(self.__delete_action)
        self.set_selected_item(None)

    def __show_all_layers(self):
        for l in self.__layers:
            l.is_enabled = True
    def __hide_all_layers(self):
        for l in self.__layers:
            l.is_enabled = False
    def set_selected_item(self, item):
        enable = True
        self.__selected_item = item
        is_removable = True
        if item is not None:
            if isinstance(item.model, Layer):
                self.__item_list = self.__layers
                is_removable = item.model.is_removable
            elif isinstance(item.model, MapPoint):
                self.__item_list = self.__points
            elif isinstance(item.model, MapProfile):
                self.__item_list = self.__profiles
            else:
                enable = False
                self.__selected_item = None
                self.__item_list = None
        else:
            enable = False
        self.__move_up_action.setEnabled(enable)
        self.__move_down_action.setEnabled(enable)
        self.__delete_action.setEnabled(enable and is_removable)

    @Qt.Slot()
    def __remove_item(self):
        item = self.__selected_item
        if item is None:
            return
        index = item.self_index().row()
        self.__item_list[index:index+1] = []

    def __move_item(self, delta):
        item = self.__selected_item
        if item is None:
            return
        parent_list = self.__item_list
        index = item.self_index().row()

        if index+delta < 0 or index+delta >= len(parent_list):
            return
        item_model = item.item_model()
        parent = item.parent_index()

        elem = parent_list[index]
        parent_list[index:index+1] = []
        parent_list[index+delta:index+delta] = [elem]

        new_index = item_model.index(index+delta, 0, parent)
        self.set_selected_item(item_model.node_at(new_index))
        self.request_selection_change.emit(new_index)

class MapManagerWidget(Qt.QWidget):
    class ChildrenOfInterest:
        def __init__(self):
            self.state_widget: SchemaView
            self.toolbar: LayerActions

    def __init__(self, window_state):
        super().__init__()
        self.__layer_actions = LayerActions(self, window_state.layers, window_state.points, window_state.profiles)

        wtree = Container(Qt.QVBoxLayout, (), [
            Leaf(Qt.QToolBar, (), id="toolbar"),
            (Leaf(SchemaView, (window_state_schema, window_state), id="state_widget"), {"stretch":1})
        ])
        self.widgets = self.ChildrenOfInterest()
        wtree.create_in(self, self.widgets)
        self.widgets.state_widget.selection_changed.connect(self.__on_selection_changed)

        self.layer_actions.request_selection_change.connect(self.__request_selection_change)
        for act in self.layer_actions.actions():
            self.widgets.toolbar.addAction(act)

    @property
    def layer_actions(self):
        return self.__layer_actions

    @Qt.Slot()
    def __on_selection_changed(self, item):
        self.layer_actions.set_selected_item(item)
    @Qt.Slot()
    def __request_selection_change(self, index):
        self.widgets.state_widget.selectionModel().select(index, Qt.QItemSelectionModel.Select)
