import os
import rasterio
import pathlib
import json

from .__prelude__ import Qt, WindowState, Dataset, logger, SELF, version
from .MainWidget import MainWidget
from .MapManagerWidget import MapManagerWidget, LayerListMenu
from .GLWidget import GLWidget
from .plot import SpatialPlotWidget, TemporalPlotWidget
from .HelpWidget import HelpWidget
from .IconDockWidget import IconDockWidget
from .WidgetTree import Container, Leaf
from .IconLabel import IconLabel
from .ComputedProgressBar import ComputedProgressBar

class ActionOn:
    def __init__(self, name, title, callback, shortcut = None, checkable = False):
        self._name = name
        self._title = title
        self._callback = callback
        self._shortcut = shortcut
        self._checkable = checkable
    def create(self, target):
        ret = Qt.QAction(self._title)
        def f():
            self._callback(target)
        if self._shortcut is not None:
            ret.setShortcut(Qt.QKeySequence(self._shortcut))
        ret.setCheckable(self._checkable)
        ret.triggered.connect(f)
        setattr(target, f"{self._name}_action", ret)
def action(title, **kwargs):
    def wrap(f):
        f.__register_action__ = ActionOn(f.__name__, title, f, **kwargs)
        return f
    return wrap

class SetInterleaveRunner(Qt.QRunnable):
    def __init__(self, src_file, dst_file, on_progress):
        super().__init__()
        self._src_file, self._dst_file = pathlib.Path(src_file), pathlib.Path(dst_file)
        self._on_progress = on_progress

    def _run_convert(self):
        with rasterio.open(self._src_file, 'r') as src:
            prof = src.profile
            prof["interleave"] = "band"
            prof["BIGTIFF"] = "YES"

            with rasterio.open(self._dst_file, 'w', **prof) as dst:
                for band in range(src.count):
                    dst.set_band_description(band+1, src.descriptions[band])

                percent = 0
                windows = [*src.block_windows(1)]

                for i, (ji, window) in enumerate(windows):
                    if i*100 > (percent+1)*len(windows):
                        percent = percent+1
                        yield float(percent)/100.0
                    dst.write(src.read(window = window), window = window)

            yield 1.0

    def run(self):
        for progress in self._run_convert():
            self._on_progress(progress)

class InsarvizWindow(Qt.QMainWindow):
    def __init__(self, win_state: WindowState):
        super().__init__()
        # Register all actions
        for act in self.__class__.__dict__.values():
            if hasattr(act, '__register_action__'):
                act.__register_action__.create(self)

        self.setWindowTitle("InsarViz")
        self.setWindowIcon(Qt.QIcon('insarviz:logo_insarviz.png'))
        self.setWindowState(Qt.Qt.WindowMaximized)

        self._state: WindowState = win_state
        self._state.fieldChanged.connect(self._on_state_change)

        self._map_manager_widget = MapManagerWidget(self._state)
        self._minimap_widget = GLWidget(self._state.minimap_scene)
        def resize_minimap_viewport(__w__, __h__):
            def set_world_to_clip(ctx):
                ctx.map_world_to_clip = self._dataset_widget.world_to_clip
                self._state.minimap_scene.renderChanged.emit()
            self._minimap_widget.modify_initialized_scene(set_world_to_clip)
        self._temporal_plot_widget = TemporalPlotWidget(self._state.current_band(), self._state.points, self._state.profiles)

        self._spatial_plot_widget = SpatialPlotWidget(self._state.current_band(), self._state.points, self._state.profiles)

        self._dataset_widget = MainWidget(win_state)
        self._dataset_widget.resized_viewport.connect(resize_minimap_viewport)

        win_state.dynamic_attribute("hovered_pixel").drive(self._set_temporal_cursor_point)
        self.setCentralWidget(self._dataset_widget)

        self._map_manager_dock = Qt.QDockWidget("Project", self)
        self._map_manager_dock.setWidget(self._map_manager_widget)
        def on_manager_visible(visible):
            self.show_map_manager_action.setChecked(visible)
        self._map_manager_dock.visibilityChanged.connect(on_manager_visible)
        self.addDockWidget(Qt.Qt.DockWidgetArea.LeftDockWidgetArea, self._map_manager_dock)

        self._minimap_dock = Qt.QDockWidget("Minimap", self)
        self._minimap_dock.setWidget(self._minimap_widget)
        def on_minimap_visible(visible):
            self.show_minimap_action.setChecked(visible)
            if visible:
                # Necesary to redraw OpenGL widgets when floating the dock
                self._minimap_widget.update()
        self._minimap_dock.visibilityChanged.connect(on_minimap_visible)
        self.addDockWidget(Qt.Qt.DockWidgetArea.LeftDockWidgetArea, self._minimap_dock)

        self._geo_map_dock = Qt.QDockWidget("Geo Map", self)
        self._geo_map_dock.setVisible(False)
        self._state.dynamic_attribute("geo_scene").drive(self.__set_geo_widget)

        self.setStatusBar(Qt.QStatusBar())
        def fixedHeightWidget(height):
            def ret():
                w = Qt.QWidget()
                w.setFixedHeight(height)
                return w
            return ret

        self.statusBar().addPermanentWidget(Container(Qt.QHBoxLayout, (), [
            Leaf(Qt.QLabel, ("position", ), id="_position_label"),
            (Leaf(Qt.QWidget, ()), {"stretch":1}),
            (Leaf(ComputedProgressBar, (), id = "_compute_band_progress"), {"stretch":1}),
            Leaf(IconLabel, (Qt.QIcon("insarviz:logo_insarviz.png"),)),
            Leaf(Qt.QLabel, (f"InsarViz v{version}", ))
        ], widget_class = fixedHeightWidget(40)).create(self), stretch = 1)
        win_state.dynamic_attribute("position_info").drive(lambda elements: self._position_label.setText(", ".join(elements)))
        self._compute_band_progress.set_computed_value(self._state.current_band().computed_image)

        def on_plots_visible(visible):
            self.show_plot_action.setChecked(self._spatial_plot_dock.isVisible() or self._temporal_plot_dock.isVisible())

        self._temporal_plot_dock = IconDockWidget("Temporal Plots", self, Qt.QIcon("insarviz:temporal.svg"))
        self._temporal_plot_dock.setWidget(self._temporal_plot_widget)
        self._temporal_plot_dock.visibilityChanged.connect(on_plots_visible)

        self._spatial_plot_dock = IconDockWidget("Spatial Plots", self, Qt.QIcon("insarviz:spatial.svg"))
        self._spatial_plot_dock.setWidget(self._spatial_plot_widget)
        self._spatial_plot_dock.visibilityChanged.connect(on_plots_visible)

        self._help_widget = HelpWidget()
        self._help_dialog = Qt.QDialog(self)
        help_layout = Qt.QVBoxLayout(self._help_dialog)
        help_layout.addWidget(self._help_widget)
        self._help_dialog.setLayout(help_layout)
        self._help_dialog.setWindowTitle("InsarViz help")
        self._help_dialog.setModal(True)
        help_shortcut = Qt.QShortcut("F1", self._help_dialog)
        help_shortcut.activated.connect(self._help_dialog.hide)

        self._project_file_path = None

        menu_bar = Qt.QMenuBar()
        file_menu = Qt.QMenu("File")
        file_menu.addAction(self.open_file_action)
        file_menu.addAction(self.save_project_action)
        file_menu.addAction(self.save_project_as_action)
        file_menu.addAction(self.open_geo_lut_action)
        file_menu.addSeparator()
        file_menu.addAction(self.quit_action)
        menu_bar.addMenu(file_menu)

        layer_menu = Qt.QMenu("Layers")
        for act in self._map_manager_widget.layer_actions.actions():
            layer_menu.addAction(act)
        layer_menu.addSeparator()
        self.__add_layer_menu = LayerListMenu(self, self._state.layers)
        for action in self.__add_layer_menu.actions():
            layer_menu.addAction(action)
        menu_bar.addMenu(layer_menu)

        view_menu = Qt.QMenu("View")
        view_menu.addAction(self.show_minimap_action)
        view_menu.addAction(self.show_map_manager_action)
        view_menu.addAction(self.show_plot_action)
        view_menu.addSeparator()
        view_menu.addAction(self.reset_map_camera_action)
        view_menu.addSeparator()
        view_menu.addAction(self.flip_horizontally_action)
        SELF.map_scene.flip_horizontally[self._state].drive(lambda h_flip: self.flip_horizontally_action.setChecked(h_flip))
        view_menu.addAction(self.flip_vertically_action)
        SELF.map_scene.flip_vertically[self._state].drive(lambda v_flip: self.flip_vertically_action.setChecked(v_flip))
        menu_bar.addMenu(view_menu)

        help_menu = Qt.QMenu("Help")
        help_menu.addAction(self.show_help_action)
        menu_bar.addMenu(help_menu)

        self.setMenuBar(menu_bar)

    @action("Reset Map View")
    def reset_map_camera(self):
        self._state.reset_map_camera()

    def _set_temporal_cursor_point(self, pixel_coords):
        w, h = self._state.image_size
        if pixel_coords is None:
            return None
        x, y = pixel_coords
        if x >= 0 and x < w and y >= 0 and y < h:
            self._temporal_plot_widget.set_cursor_coords(pixel_coords)

    def _set_dock_visible(self, dock, visible, area):
        if visible:
            dock.setFloating(False)
            self.addDockWidget(area, dock)
        else:
            dock.setFloating(True)
        dock.setVisible(visible)

    @action("Show Help", shortcut = "F1")
    def show_help(self):
        self._help_dialog.show()

    @action("Flip Horizontally", checkable=True)
    def flip_horizontally(self):
        checked = self.flip_horizontally_action.isChecked()
        self._state.map_scene.flip_horizontally = checked
    @action("Flip Vertically", checkable=True)
    def flip_vertically(self):
        checked = self.flip_vertically_action.isChecked()
        self._state.map_scene.flip_vertically = checked

    @action("Plot", checkable = True, shortcut = "Ctrl+P")
    def show_plot(self):
        checked = self.show_plot_action.isChecked()
        self._set_dock_visible(self._temporal_plot_dock,
                               checked,
                               Qt.Qt.DockWidgetArea.RightDockWidgetArea)
        self._set_dock_visible(self._spatial_plot_dock,
                               checked,
                               Qt.Qt.DockWidgetArea.RightDockWidgetArea)
        self.tabifyDockWidget(self._spatial_plot_dock, self._temporal_plot_dock)

    @action("Minimap", checkable = True, shortcut = "Ctrl+M")
    def show_minimap(self):
        self._set_dock_visible(self._minimap_dock,
                               self.show_minimap_action.isChecked(),
                               Qt.Qt.DockWidgetArea.LeftDockWidgetArea)
    @action("Project", checkable = True)
    def show_map_manager(self):
        self._set_dock_visible(self._map_manager_dock,
                               self.show_map_manager_action.isChecked(),
                               Qt.Qt.DockWidgetArea.LeftDockWidgetArea)

    def _convert_dataset_interleave(self, path, band_dataset_path):
        progress_dialog = Qt.QDialog()
        progress_dialog.setModal(True)
        progress_dialog.setWindowTitle("Dataset conversion to band interleave")
        layout = Qt.QVBoxLayout()
        label = Qt.QLabel(f"Converting dataset {path}")
        layout.addWidget(label)
        progress_bar = Qt.QProgressBar()
        layout.addWidget(progress_bar)
        progress_dialog.setLayout(layout)
        progress_dialog.setFixedSize(progress_dialog.sizeHint())
        def on_changed():
            if progress_bar.value() > 99:
                progress_dialog.accept()
        progress_bar.valueChanged.connect(on_changed)
        Qt.QThreadPool.globalInstance().start(
            SetInterleaveRunner(path, band_dataset_path,
                                lambda progress: progress_bar.setValue(int(progress*100))))

        ret = progress_dialog.exec()
        return ret == Qt.QDialog.DialogCode.Accepted

    @property
    def __default_open_path(self):
        if self._project_file_path is not None:
            return str(self._project_file_path.parent)
        elif self._state.dataset.file != '<none>':
            return str(self._state.dataset.file.parent)
        else:
            return os.getcwd()

    @action("Load Geo LUT", shortcut = "Ctrl+G")
    def open_geo_lut(self):
        path, filetype = Qt.QFileDialog.getOpenFileName(self, "Open Lookup Table", self.__default_open_path, f"LUT File (*_Lut_*.tiff)")
        if path is None or path == "":
            return
        self._state.geo_lut_dataset = Dataset(pathlib.Path(path))

    def __set_geo_widget(self, geo_scene):
        if geo_scene is None:
            return

        geo_widget = GLWidget(geo_scene)

        def on_position_changed(x_model, y_model):
            x_img, y_img = geo_scene.model_to_image.transform_point((x_model, y_model))
            img = geo_scene.lut_image
            h,w,_ = img.shape
            if x_img >= 0 and x_img <= 1 and y_img >= 0 and y_img <= 1:
                radar_x, radar_y = img[int(y_img*h), int(x_img*w)] * geo_scene.lut_scale
                self._state.map_scene.geo_focus = radar_x, radar_y
            else:
                self._state.map_scene.geo_focus = None
        geo_widget.positionChanged.connect(on_position_changed)

        self._geo_map_dock.setWidget(geo_widget)
        self.addDockWidget(Qt.Qt.DockWidgetArea.RightDockWidgetArea, self._geo_map_dock)
        self._geo_map_dock.setVisible(True)

    @action("Open file", shortcut = "Ctrl+O")
    def open_file(self, path = None):
        DATACUBE_FILES = "Data Cube File (*.tiff *.tif *.h5 *.r4 depl_cumule*)"
        PROJECT_FILES = "InsarViz Project (*.invz)"

        if path is None:
            path, filetype = Qt.QFileDialog.getOpenFileName(self, "Open Data Cube", self.__default_open_path, f"{DATACUBE_FILES};;{PROJECT_FILES}")
            is_dataset = filetype == DATACUBE_FILES
        else:
            match path.suffix:
                case ".invz":
                    is_dataset = False
                case _:
                    is_dataset = True
        if is_dataset:
            path = pathlib.Path(path)
            dataset = Dataset(path)
            if dataset.interleaving != Dataset.Interleaving.band:
                band_dataset_path = path.with_name(path.stem + "_band" + path.suffix)
                if not band_dataset_path.exists():
                    msgBox = Qt.QMessageBox(Qt.QMessageBox.Icon.Warning,
                                            "Suboptimal Interleaving",
                                            f"""
                                            <p>
                                              The dataset at "{path}" has non-band interleaving, which will lead to
                                              (very) slow band loads and computations. It is advised to convert it
                                              to band interleaving before proceeding.
                                            </p>
                                            <p>Do you want to convert this file for a more fluid viewing (this may take up additional disk space) ?</p>
                                            """,
                                            buttons = Qt.QMessageBox.StandardButton.No | Qt.QMessageBox.StandardButton.Save | Qt.QMessageBox.StandardButton.Yes)
                    msgBox.setTextFormat(Qt.Qt.TextFormat.RichText)
                    ret = msgBox.exec()
                    if ret == Qt.QMessageBox.StandardButton.Save:
                        band_dataset_path, _ = Qt.QFileDialog.getSaveFileName(self, "Save Band Dataset", self.__default_open_path, "GeoTiff Dataset (*.tiff)")
                        band_dataset_path = pathlib.Path(band_dataset_path)
                    elif ret != Qt.QMessageBox.StandardButton.Yes:
                        # User wants things to be slow
                        self._state.band_number = 0
                        self._state.dataset = dataset
                        return
                    if not self._convert_dataset_interleave(path, band_dataset_path):
                        return

                self._state.dataset = Dataset(band_dataset_path)
                self._state.band_number = 0
            else:
                self._state.dataset = dataset
                self._state.band_number = 0
        else:
            with open(path, 'r') as project_file:
                self._state.init_from_dict(json.load(project_file))
            self._project_file_path = pathlib.Path(path)

    @action("Save project", shortcut = "Ctrl+S")
    def save_project(self):
        if self._project_file_path is None:
            self.save_project_as()
        else:
            logger.info("Saving project as %s", self._project_file_path)
            json_string = json.dumps(self._state.to_dict(), indent=3)
            with self._project_file_path.open('w') as project_file:
                project_file.write(json_string)
    @action("Save project as...", shortcut = "Ctrl+Shift+S")
    def save_project_as(self):
        path, filetype = Qt.QFileDialog.getSaveFileName(self, "Save Project", self.__default_open_path, "InsarViz Project (*.invz)")
        if path == '':
            return
        path = pathlib.Path(path).with_suffix('.invz')
        self._project_file_path = path
        self.save_project()

    @action("Quit", shortcut = "Ctrl+Q")
    def quit(self):
        super().close()

    def _update_dataset(self):
        self._update_title()
    def _update_title(self):
        title = "InsarViz"
        band_title = self._state.current_band().band_title()
        if band_title is not None:
            title = f"{title} - {band_title}"
        self.setWindowTitle(title)

    def closeEvent(self, event):
        self._minimap_widget.close()
        self._dataset_widget.close()
        event.accept()

    @Qt.Slot(str) # type: ignore
    def _on_state_change(self, field):
        if field in ("dataset", "band_number"):
            self._update_title()
