from typing import Optional
import pathlib
import numpy as np
import xyzservices.providers
import datetime

from .__prelude__ import Qt, Point, logger, unit_square_to_image, Matrix

from .drawing import MapScene, GeoScene, MinimapScene, PointsLayer, SelectedBandLayer, layer_types
from .observable import ObservableList, ObservableStruct, dynamic, SELF
from .SelectedBand import SelectedBand
from .ColorMap import ColorMap
from .Dataset import Dataset, AbstractDataset
from .MapPoint import MapPoint
from .MapProfile import MapProfile

class LayerList(ObservableList):
    def __init__(self, selected_band, points, profiles, colormap):
        super().__init__()
        self._points = points
        self._profiles = profiles
        self._selected_band = selected_band
        self._colormap = colormap

    def import_context(self):
        return {
            'points': self._points,
            'profiles': self._profiles,
            'selected_band': self._selected_band,
            'colormap': self._colormap
        }

def clamp_band(self, band):
    if self.dataset is None:
        return 0
    else:
        return max(0, min(band, self.dataset.count-1))

class MaybeBandNumber(ObservableStruct):
    band_number = dynamic.variable()
    source_band_number = dynamic.external()
    is_enabled = dynamic.variable(False)

    def __init__(self, dynamic_band_number):
        super().__init__()
        self._dynamic_source_band_number = dynamic_band_number
        self.band_number = self.source_band_number
        self.dynamic_attribute("band_number").value_changed.connect(self.__on_band_change)
        self.dynamic_attribute("is_enabled").value_changed.connect(self.__on_enabled_change)

    def __on_band_change(self):
        if self.is_enabled:
            self.source_band_number = self.band_number
    def __on_enabled_change(self):
        if not self.is_enabled:
            self.source_band_number = None
        else:
            self.source_band_number = self.band_number

class WindowState(ObservableStruct):
    class CurrentBand(SelectedBand):
        def __init__(self, win_state: "WindowState"):
            super().__init__(win_state.dynamic_attribute("dataset"), win_state.dynamic_attribute("band_number"), win_state.dynamic_attribute("reference_band_number"))

    dataset                = dynamic.variable()
    band_number            = dynamic.filtered_variable(clamp_band)
    reference_band_number  = dynamic.variable(None)
    tile_provider          = dynamic.external()
    map_scene              = dynamic.readonly()
    maybe_reference_band   = dynamic.readonly()
    geo_lut_dataset        = dynamic.variable()
    hovered_model          = dynamic.variable()

    def __init__(self):
        super().__init__()
        self.dataset = AbstractDataset()
        self.band_number = 0
        self._current_band = WindowState.CurrentBand(self)

        self.band_colormap = ColorMap("grey", np.array([[0, 0, 0], [255, 255, 255]]), xzero=-1.0, xone=1.0)
        self.points = ObservableList()
        self.profiles = ObservableList()
        band = self.current_band()
        self.layers = LayerList(band, self.points, self.profiles, self.band_colormap)
        self.layers[:] = [
            PointsLayer(self.dynamic_attribute("dataset"), self.points, self.profiles),
            SelectedBandLayer(band, self.band_colormap)
        ]
        self._map_scene = MapScene(band, self.points, self.profiles, self.layers, self.band_colormap)
        self._dynamic_tile_provider = SELF.map_scene.tile_cache.provider[self]
        self.tile_provider = xyzservices.providers['OpenStreetMap']["Mapnik"]
        self.minimap_scene = MinimapScene(band, self.map_scene, self.band_colormap)

        self._maybe_reference_band = MaybeBandNumber(self.dynamic_attribute("reference_band_number"))

    @dynamic.memo(SELF.geo_lut_dataset)
    def geo_scene(self):
        if self.geo_lut_dataset is None:
            return None
        return GeoScene(
            self.current_band(), self.geo_lut_dataset,
            self.map_scene.dynamic_attribute("overlay_layer"),
            self.map_scene.dynamic_attribute("tile_cache"),
        )

    @dynamic.memo(SELF.dataset.width, SELF.dataset.height)
    def image_size(self):
        if self.dataset is None:
            return 1,1
        else:
            return self.dataset.width, self.dataset.height

    @dynamic.memo(SELF.hovered_model, SELF.image_size,
                  SELF.map_scene.model_to_texture)
    def hovered_pixel(self):
        if self.hovered_model is None:
            return None
        x_model, y_model = self.hovered_model
        img_width, img_height = self.image_size
        x_img, y_img = Matrix.product(
            unit_square_to_image(img_width, img_height),
            Matrix.translate((-1,-1)),
            Matrix.scale((2,2,1)),
            self.map_scene.model_to_texture
        ).transform_point((x_model, y_model))
        return int(x_img*img_width), int(y_img*img_height)

    @dynamic.memo(SELF.hovered_pixel, SELF.dataset.pixel_to_crs)
    def hovered_crs(self):
        if self.hovered_pixel is None:
            return None
        if not self.dataset.is_georeferenced:
            return None
        x_pixel, y_pixel = self.hovered_pixel
        return self.dataset.pixel_to_crs.transform_point((x_pixel, y_pixel))

    @dynamic.memo(SELF.hovered_pixel, SELF.hovered_crs)
    def position_info(self):
        elements = []

        if self.dataset.has_band_dates:
            elements.append(datetime.datetime.fromtimestamp(self._current_band.timestamp).strftime('date: %Y-%m-%d'))

        if self.hovered_crs is not None:
            x_crs, y_crs = self.hovered_crs
            elements.append(f"lon: {x_crs:.03f}")
            elements.append(f"lat: {y_crs:.03f}")

        if self.hovered_pixel is not None:
            x_pixel, y_pixel = self.hovered_pixel

            w,h = self.image_size
            if x_pixel >= 0 and x_pixel < w and y_pixel >= 0 and y_pixel < h:
                try:
                    elements.append(f"x: {x_pixel}")
                    elements.append(f"y: {y_pixel}")
                    elements.append(f"val: {self._current_band.image[y_pixel, x_pixel, 0]:.03f}")
                except:
                    pass


        return elements

    def reset_map_camera(self):
        self.map_scene.yaw = 0.0
        self.map_scene.pitch = 0.0
        self.map_scene.distance = 5.0
        self.map_scene.heightUnits = 0.0
        self.map_scene.center = Point(0,0)

    def init_from_dict(self, dct):
        self.dataset = Dataset(dct['dataset'])
        self.band_number = dct['band_number']
        self.reference_band_number = dct.get('reference_band_number', None)
        self.maybe_reference_band.band_number = self.reference_band_number
        self.maybe_reference_band.is_enabled = self.reference_band_number is not None
        self.points[:] = [MapPoint.from_dict(p) for p in dct['points']]
        self.profiles[:] = [MapProfile.from_dict(p) for p in dct['profiles']]
        if 'layers' in dct:
            def make_layer(mime_type, data):
                for ltype in layer_types:
                    if mime_type == ltype.__mime_type__:
                        return ltype.from_dict(data, **self.layers.import_context())
                return None
            self.layers[:] = [make_layer(**dct) for dct in dct['layers']]
        if 'band_colormap' in dct:
            self.band_colormap.init_from_dict(dct['band_colormap'])
        geo_lut_dataset = dct.get('geo_lut_dataset', None)
        if geo_lut_dataset is not None:
            geo_lut_dataset = Dataset(geo_lut_dataset)
        self.geo_lut_dataset = geo_lut_dataset
        self.map_scene.init_from_dict(dct['map_scene'])
    def to_dict(self):
        return {
            'dataset': str(pathlib.Path(self.dataset.file).resolve()),
            'geo_lut_dataset': str(self.geo_lut_dataset.file.resolve()) if self.geo_lut_dataset is not None else None,
            'band_number': self.band_number,
            'reference_band_number': self.reference_band_number,
            'points': [p.to_dict() for p in self.points],
            'profiles': [p.to_dict() for p in self.profiles],
            'map_scene': self.map_scene.to_dict(),
            'band_colormap': self.band_colormap.to_dict(),
            'layers': [{"mime_type": l.__mime_type__, "data": l.to_dict()} for l in self.layers]
        }

    def exit(self):
        self.map_scene.selected_band.texture.destroy()

    def current_band(self):
        return self._current_band
