import numpy as np
from numpy.ma import MaskedArray

from .__prelude__ import Matrix, DEMTexture, inOpenGLContext, ComputedValue, Qt, logger

from .observable import ObservableStruct, dynamic, SELF, Unique

def with_derivs(image_masked):
    h, w = image_masked.shape
    image_dx = (np.float32(w) * 0.5) * (np.roll(image_masked, (0,-1), (0,1)) - np.roll(image_masked, (0,1), (0,1)))
    yield 0.33
    image_dy = (np.float32(h) * 0.5) * (np.roll(image_masked, (-1,0), (0,1)) - np.roll(image_masked, (1,0), (0,1)))
    yield 0.66
    mask = np.where(image_masked.mask, np.float32(0.0), np.float32(1.0))
    return np.reshape(
        np.stack([image_masked.data, image_dx, image_dy, mask], axis=-1),
        (h, w, 4))

def destroy_in_context(texture):
    if texture is not None:
        def run():
            texture.destroy()
        inOpenGLContext(run)

DEFAULT_BAND_IMAGE = (np.reshape(np.array([0,0,0,0]), (1,1,4)), [1], [1])

class SelectedBand(ObservableStruct):
    reference_band_number  = dynamic.external()
    band_number            = dynamic.external()
    dataset                = dynamic.external()

    def __init__(self, dynamic_dataset, dynamic_band_number, dynamic_reference_band_number):
        super().__init__()
        self._dynamic_band_number = dynamic_band_number
        self._dynamic_dataset = dynamic_dataset
        self._dynamic_reference_band_number = dynamic_reference_band_number

        self.__image = ComputedValue(DEFAULT_BAND_IMAGE)
        self.__image.ready.connect(self.__image_ready)
        self.__reference_image = ComputedValue(DEFAULT_BAND_IMAGE)
        self.__reference_image.ready.connect(self.__reference_image_ready)

        self.__image_cache = { }
        self.dynamic_attribute("dataset").value_changed.connect(self.__clear_image_cache)
        self.dynamic_attribute("band_number").value_changed.connect(self.__recompute_image)
        self.dynamic_attribute("reference_band_number").value_changed.connect(self.__recompute_reference_image)

    @dynamic.memo()
    def current_computed_image(self):
        return self.__image.latest()
    @Qt.Slot()
    def __image_ready(self):
        self.dynamic_attribute("current_computed_image").invalidate()
    @dynamic.memo()
    def current_computed_reference_image(self):
        return self.__reference_image.latest()
    @Qt.Slot()
    def __reference_image_ready(self):
        self.dynamic_attribute("current_computed_reference_image").invalidate()

    @property
    def computed_image(self):
        return self.__image

    @dynamic.memo(SELF.image, destroy = destroy_in_context)
    def texture(self) -> DEMTexture:
        def run():
            texture = DEMTexture(self.image)
            texture.create()
            return texture
        return inOpenGLContext(run)
    @dynamic.memo(SELF.reference_image, destroy = destroy_in_context)
    def reference_texture(self) -> DEMTexture:
        def run():
            texture = DEMTexture(self.reference_image)
            texture.create()
            return texture
        return inOpenGLContext(run)

    @dynamic.memo(SELF.current_computed_image)
    def histogram(self):
        _, hist, bins = self.current_computed_image
        return hist, bins

    @dynamic.memo(SELF.dataset, SELF.band_number)
    def timestamp(self):
        return self.dataset.band_timestamps[self.band_number]
    @dynamic.memo(SELF.dataset, SELF.reference_band_number)
    def reference_timestamp(self):
        if self.reference_band_number is None:
            return None
        else:
            return self.dataset.band_timestamps[self.reference_band_number]

    @dynamic.memo(SELF.dataset, SELF.band_number)
    def nodata(self):
        if self.band_number is not None:
            return np.float32(self.dataset.nodatavals[self.band_number])
        return np.nan
    @dynamic.memo(SELF.current_computed_image)
    def image(self):
        return self.current_computed_image[0]
    @dynamic.memo(SELF.current_computed_reference_image)
    def reference_image(self):
        return self.current_computed_reference_image[0]

    @dynamic.memo(SELF.dataset)
    def size(self):
        return (self.dataset.width, self.dataset.height)

    @dynamic.memo(SELF.size)
    def image_to_crs(self):
        w, h = self.size
        return Matrix.product(
            self.dataset.pixel_to_crs,
            Matrix.scale((w, h, 1.0))
        )

    def band_title(self):
        if self.band_number is None:
            return None
        title = self.dataset.file
        if self.band_number is not None:
            title = f"{title} - Band {self.band_number+1} of {self.dataset.count}"
        return title

    def __compute_image_function(self, band):
        def compute_image():
            if band in self.__image_cache:
                pass
            else:
                yield "Loading band #%s : %%p%%" % (band+1), 0.0
                band_img = self.dataset.read(band+1, masked=True)
                yield "Compute band normals : %p%", 0.33
                image = yield from map(
                    lambda img_progress: 0.33+0.33*img_progress,
                    with_derivs(band_img))
                yield "Compute band histogram : %p%", 0.66

                vals = band_img.data[~band_img.mask]
                yield 0.8333
                # Friedman-Diaconis estimator for the number of bins
                hist, bins = np.histogram(vals, bins = 'fd', density=True)
                self.__image_cache[band] = (image, hist, bins)
            yield 1.0
            return self.__image_cache[band]
        return compute_image

    @Qt.Slot()
    def __recompute_image(self):
        self.__image.recompute(self.__compute_image_function(self.band_number))
    @Qt.Slot()
    def __recompute_reference_image(self):
        if self.reference_band_number is None:
            self.__reference_image.set_value(DEFAULT_BAND_IMAGE)
        else:
            self.__reference_image.recompute(self.__compute_image_function(self.reference_band_number))
    @Qt.Slot()
    def __clear_image_cache(self):
        self.__image_cache = {}
        self.__recompute_image()
        self.__recompute_reference_image()
