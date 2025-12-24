import rasterio
import rasterio.enums
import datetime
import numpy as np
import numpy.ma as npma
import pathlib
from threading import Lock

from .__prelude__ import Matrix, logger, ComputedValue
from .observable import ObservableStruct, dynamic, SELF

class AbstractDataset(ObservableStruct):
    def read(self, band, masked=False, **kwargs):
        arr = np.reshape(np.array([0], dtype=np.float32), (1,1))
        if masked:
            return npma.array(arr, mask = np.array([[False]]))
        else:
            return arr

    @property
    def file(self):
        return '<none>'
    @property
    def band_dates(self):
        return np.array([0], dtype=int)
    @property
    def count(self):
        return 1
    @property
    def width(self):
        return 1
    @property
    def height(self):
        return 1
    @property
    def band_timestamps(self):
        return np.array([0], dtype=float)
    @property
    def has_band_dates(self):
        return False
    @property
    def is_georeferenced(self):
        return False
    @property
    def size(self):
        return self.width, self.height

    @dynamic.memo()
    def value_units(self):
        return None

    @property
    def descriptions(self):
        return ["Dummy band"]

    @property
    def full_histograms(self):
        return ComputedValue(None)

    def nearest_band_to_timestamp(self, timestamp):
        after = np.searchsorted(self.band_timestamps, timestamp)
        left_i = after-1 if after > 0 else after
        right_i = after if after < self.count else after-1
        if abs(timestamp - self.band_timestamps[left_i]) < abs(timestamp - self.band_timestamps[right_i]):
            return left_i
        else:
            return right_i

    @property
    def nodatavals(self):
        return np.array([np.nan])
    @dynamic.memo()
    def pixel_to_crs(self):
        return Matrix.identity(3)
    @dynamic.memo(SELF.pixel_to_crs)
    def image_to_crs(self):
        w, h = self.width, self.height
        return Matrix.product(
            self.pixel_to_crs,
            Matrix.scale((w, h, 1))
        )

class Dataset(AbstractDataset):
    Interleaving = rasterio.enums.Interleaving

    def __init__(self, path):
        super().__init__()
        logger.info('Opening dataset at %s', path)
        self._dataset = rasterio.open(path)
        # RasterIO crashes when performing reads from multiple threads
        # on the same dataset, so we lock the reads
        self._dataset_lock = Lock()
        self._file = pathlib.Path(path)
        self._pixel_to_crs = Matrix(
            np.reshape(self._dataset.transform, (3,3)),
            np.reshape(~self._dataset.transform, (3,3))
        )
        datestamps = [self._get_date_and_stamps(i) for i in range(self._dataset.count)]
        self._band_dates = [date for _, date, _ in datestamps]
        self._band_timestamps = [stamp for _, _, stamp in datestamps]
        self._has_band_dates = any([has_date for has_date, _, _ in datestamps])
        self._full_histograms = None
        logger.debug('Done opening dataset at %s', path)

    @property
    def full_histograms(self):
        if self._full_histograms is None:
            self._full_histograms = ComputedValue(None)
            self._full_histograms.recompute(self._compute_histograms)
        return self._full_histograms

    def _get_date_and_stamps(self, i):
        tag_date = self._dataset.tags(i+1).get("DATE", None)
        if tag_date is not None:
            date = datetime.datetime.strptime(str(tag_date), "%Y%m%d")
            return True, date, date.timestamp()
        try:
            date = datetime.datetime.strptime(self._dataset.descriptions[i][-8:], "%Y%m%d")
            return True, date, date.timestamp()
        except (TypeError, ValueError):
            return False, i+1, float(i+1)

    def _compute_histograms(self):
        progress = 0.0
        progress_increment = 1.0/self.count

        sample_size = 1000
        samples = [None for _ in range(self.count)]
        fmt = "Full histograms : %p%"
        for band_number in range(self.count):
            band = self.read(band_number+1, masked=True)
            indices_x = np.random.randint(self.width,  size=sample_size)
            indices_y = np.random.randint(self.height, size=sample_size)
            indices_mask = ~band.mask[indices_y, indices_x]
            indices_x = indices_x[indices_mask]
            indices_y = indices_y[indices_mask]
            samples[band_number] = band.data[indices_y, indices_x]
            progress += progress_increment
            yield fmt, progress

        all_samples = np.concatenate(samples)
        hist, bins = np.histogram(all_samples, bins='fd', density=True)
        return hist, bins

    def read(self, band, masked=False, **kwargs):
        with self._dataset_lock:
            raw_img = self._dataset.read(band, masked=masked, **kwargs)
        if masked and len(raw_img.mask.shape) != 2:
            nodata = self._dataset.nodata
            if nodata is None:
                logger.warn(f"Nodata mask not found in {self.file}. Using dark magic to create one")
                # Some datasets use 9999.0 or -9999.0 as indicators of "nodata", without telling us
                mask = np.logical_or(np.logical_or(raw_img.data == 9999.0, raw_img.data == -9999.0),
                                     np.logical_or(raw_img.data == 0.0, np.isnan(raw_img.data)))
                raw_img = npma.array(raw_img.data, mask = mask)
            else:
                if np.isnan(nodata):
                    raw_img = npma.array(raw_img.data, mask = np.isnan(raw_img.data))
                else:
                    raw_img = npma.masked_values(raw_img.data, nodata)

        return raw_img

    @dynamic.memo()
    def metadata(self):
        metafilename = self.file.with_suffix('.meta')
        metadata = {}
        try:
            with open(metafilename, encoding="utf-8") as f:
                for line in f:
                    try:
                        (key, val) = line.split(sep=': ', maxsplit=1)
                        metadata[key] = val.strip()
                    except ValueError:
                        pass
        except FileNotFoundError:
            logger.warn("No metadata file found")

        return metadata

    @dynamic.memo()
    def value_units(self):
        tags = self._dataset.tags()
        if "VALUE_UNITS" in tags:
            units = tags["VALUE_UNIT"]
            logger.info("Found value units '%s' in dataset tags", units)
            return units
        metadata = self.metadata
        if "Value_unit" in metadata:
            units = metadata["Value_unit"]
            logger.info("Found value units '%s' in metadata file", units)
            return units
        return None

    @property
    def interleaving(self):
        return self._dataset.interleaving

    @property
    def is_georeferenced(self):
        return self._dataset.crs is not None

    @property
    def file(self):
        return self._file

    @property
    def band_dates(self):
        return self._band_dates
    @property
    def has_band_dates(self):
        return self._has_band_dates
    @property
    def band_timestamps(self):
        return self._band_timestamps
    @property
    def descriptions(self):
        return self._dataset.descriptions

    @property
    def count(self):
        return self._dataset.count

    @property
    def nodatavals(self):
        return self._dataset.nodatavals
    @property
    def width(self):
        return self._dataset.width
    @property
    def height(self):
        return self._dataset.height

    @property
    def pixel_to_crs(self):
        return self._pixel_to_crs
