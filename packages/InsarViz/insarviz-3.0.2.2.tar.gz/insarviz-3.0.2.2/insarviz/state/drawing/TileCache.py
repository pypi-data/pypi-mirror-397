from pathlib import Path
import urllib.request
import urllib.error
import os
from OpenGL import GL
import numpy as np
import math

from .__prelude__ import (
    Qt, logger, insarviz_dirs, ObservableStruct, dynamic, SELF,
    GLProgram, Shader, Matrix, Bound,
)

class TileRequest(Qt.QRunnable):
    class Signals(Qt.QObject):
        tile_downloaded = Qt.Signal(str)

    def __init__(self, tile_path, tile_url, tile_file):
        super().__init__()
        self._tile_path = tile_path
        self._tile_file = tile_file
        self._tile_url = tile_url
        self._signals = TileRequest.Signals()

    @property
    def tile_downloaded(self):
        return self._signals.tile_downloaded

    def run(self):
        tile_file = self._tile_file
        tile_url = self._tile_url
        req = urllib.request.Request(tile_url, headers = {
            "User-Agent": "InsarViz/3.0 map view"
        })
        os.makedirs(tile_file.parent, exist_ok=True)
        try:
            image = urllib.request.urlopen(req).read()
            with tile_file.open(mode="wb") as f:
                f.write(image)
            self.tile_downloaded.emit(self._tile_path)
        except urllib.error.HTTPError:
            logger.warn("Got HTTP error when downloading tile %s", tile_url)

class TileCache(ObservableStruct):
    new_tile_available = Qt.Signal()
    provider = dynamic.variable()

    def __init__(self):
        super().__init__()
        self._tile_cache = { }
        self._tile_requests = { }
        self.provider = None
        self.dynamic_attribute("provider").value_changed.connect(self.__clear_image_cache)

    @dynamic.method(SELF.provider)
    def get_tile(self, x_tile, y_tile, zoom_level):
        tile_path = f"{zoom_level}/{x_tile}/{y_tile}"
        tile_count = 2**zoom_level
        if x_tile < 0 or x_tile >= tile_count:
            return None
        if y_tile < 0 or y_tile >= tile_count:
            return None

        if not tile_path in self._tile_cache:
            tile_file = Path(insarviz_dirs.user_cache_dir) / "tiles" / self.provider.name / f"{tile_path}.png"
            if not tile_path in self._tile_requests:
                if tile_file.exists():
                    self._tile_cache[tile_path] = Qt.QImage(tile_file)
                else:
                    req = TileRequest(tile_path, self.provider.build_url(z=zoom_level, x=x_tile, y=y_tile), tile_file)
                    req.tile_downloaded.connect(self._on_tile_downloaded)
                    self._tile_requests[tile_path] = req
                    logger.debug("Downloading tile %s", tile_path)
                    Qt.QThreadPool.globalInstance().start(req)
                    return None
            else:
                return None
        return self._tile_cache[tile_path]

    @Qt.Slot()
    def __clear_image_cache(self):
        self._tile_cache = { }
        self.new_tile_available.emit()

    def _on_tile_downloaded(self, tile_path):
        del self._tile_requests[tile_path]
        self.new_tile_available.emit()

    def GL_paint_background(self, glfunc, model_to_crs, clip_to_model, model_to_world, world_to_clip, tiles_per_screen):
        tile_program = GLProgram([
            Shader(Qt.QOpenGLShader.ShaderTypeBit.Vertex,"tile/vertex.glsl"),
            Shader(Qt.QOpenGLShader.ShaderTypeBit.Fragment,"tile/fragment.glsl"),
        ])
        tile_mesh = tile_program.create_square_mesh(GL.GL_TRIANGLES, split=0, texture_to_model = Matrix.identity(3))

        def clip_to_crs(x_clip, y_clip):
            x_model, y_model = clip_to_model(x_clip, y_clip)
            return model_to_crs.transform_point((x_model, y_model))
        left_x_crs, left_y_crs = clip_to_crs(-1.0, 0.5)
        right_x_crs, right_y_crs = clip_to_crs(1.0, 0.5)

        d_crs = np.array([
            right_x_crs - left_x_crs,
            right_y_crs - left_y_crs
        ])

        crs_distance = np.sqrt(np.dot(d_crs, d_crs))
        zoom_level = int(- np.ceil(np.log2(crs_distance / (360.0 * tiles_per_screen))))


        topleft_x_crs, topleft_y_crs          = clip_to_crs(-1.0, 1.0)
        topright_x_crs, topright_y_crs        = clip_to_crs(1.0,  1.0)
        bottomleft_x_crs, bottomleft_y_crs    = clip_to_crs(-1.0, -1.0)
        bottomright_x_crs, bottomright_y_crs  = clip_to_crs(1.0,  -1.0)

        def crs_to_tile(x_crs, y_crs):
            n = 2**zoom_level
            x_tile = int(n * ((x_crs + 180.0) / 360.0))
            lat_rad = y_crs * np.pi / 180.0
            while lat_rad > np.pi:
                lat_rad -= 2*np.pi
            while lat_rad <= -np.pi:
                lat_rad += 2*np.pi
            y_tile = int(n * (1 - (np.log(math.tan(lat_rad) + 1/math.cos(lat_rad)) / np.pi)) / 2.0)
            return x_tile, y_tile

        x_start, x_end = (
            min(topleft_x_crs, topright_x_crs, bottomleft_x_crs, bottomright_x_crs),
            max(topleft_x_crs, topright_x_crs, bottomleft_x_crs, bottomright_x_crs)
        )
        y_start, y_end = (
            min(topleft_y_crs, topright_y_crs, bottomleft_y_crs, bottomright_y_crs),
            max(topleft_y_crs, topright_y_crs, bottomleft_y_crs, bottomright_y_crs)
        )
        x_left_tile, y_left_tile = crs_to_tile(x_start, y_start)
        x_right_tile, y_right_tile = crs_to_tile(x_end, y_end)
        x_left_tile, x_right_tile = min(x_left_tile, x_right_tile), max(x_left_tile, x_right_tile)
        y_left_tile, y_right_tile = min(y_left_tile, y_right_tile), max(y_left_tile, y_right_tile)

        def tile_to_lat(y_tile):
            n = float(2 ** zoom_level)
            lat_rad = np.arctan(np.sinh(np.pi * (1 - 2.0 * y_tile / n)))
            lat_deg = lat_rad * 180.0 / np.pi
            return lat_deg
        def tile_to_crs(x_tile, y_tile):
            n = float(2 ** zoom_level)
            lon_deg = x_tile / n * 360.0 - 180.0
            return (lon_deg, tile_to_lat(y_tile))
        def wrap_pi(lon):
            ret = lon
            while ret <= -180.0:
                ret += 360.0
            while ret >= 180.0:
                ret -= 360.0
            return ret

        crs_x_increment = 360.0 / (2**zoom_level)
        start_x_crs, start_y_crs = tile_to_crs(x_left_tile, y_left_tile)

        with tile_program as p:
            p.uniforms.crs_to_model = model_to_crs.inverse()
            p.uniforms.model_to_world = model_to_world
            p.uniforms.world_to_clip = world_to_clip
            p.uniforms.tile_image = int(0)

            for y_tile in range(y_left_tile, y_right_tile+1):

                y_crs = tile_to_lat(y_tile)
                crs_y_increment = tile_to_lat(y_tile+1) - y_crs
                x_crs = wrap_pi(start_x_crs)
                for x_tile in range(x_left_tile, x_right_tile+1):
                    tile_to_crs_mat = Matrix.product(
                        Matrix.translate((x_crs, y_crs)),
                        Matrix.scale((crs_x_increment, crs_y_increment, 1.0))
                    )
                    p.uniforms.tile_to_crs = tile_to_crs_mat

                    tile = self.get_tile(x_tile, y_tile, zoom_level)
                    if tile is not None:
                        tex = Qt.QOpenGLTexture(tile)
                        tex.create()
                        with Bound(tex, 0):
                            tile_mesh.draw()
                        tex.destroy()

                    x_crs += wrap_pi(crs_x_increment)
