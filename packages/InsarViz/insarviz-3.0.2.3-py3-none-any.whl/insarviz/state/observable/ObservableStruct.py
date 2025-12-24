from typing import Any, Optional
import json

from .__prelude__ import Qt, logger
from .decorators import dynamic

class ObservableStruct(Qt.QObject):
    fieldChanged = Qt.Signal(str, Any)

    def __init__(self):
        super().__init__()
        self.__dict__["__dynamic_attributes__"] = { }

    def dynamic_attribute(self, attr):
        sig = self.__dynamic_attributes__.get(attr, None)
        if sig is None:
            prop = getattr(self.__class__, attr, None)
            if isinstance(prop, dynamic.variable):
                sig = prop.register(self)
                sig.value_changed.connect(lambda old: self.fieldChanged.emit(attr, old))
                self.__dynamic_attributes__[attr] = sig
        return sig

    def __setattr__(self, name: str, value):
        sig = self.dynamic_attribute(name)
        if sig is None:
            old_val = getattr(self, name, None)
            super().__setattr__(name, value)
            self.fieldChanged.emit(name, old_val)
        else:
            sig.value = value

    @classmethod
    def from_dict(cls, dct: dict, /, **kwargs) -> Optional[Any]:
        ret = cls(**kwargs)
        ret.init_from_dict(dct)
        return ret
    def init_from_dict(self, __dct__):
        pass
    def to_dict(self) -> Optional[dict]:
        return None

    __mime_type__ = None
    @classmethod
    def can_from_mime(cls, mimeData, **kwargs):
        __kwargs__ = kwargs
        if cls.__mime_type__ is None:
            return False
        return mimeData.hasFormat(cls.__mime_type__)
    @classmethod
    def from_mime(cls, mimeData: Qt.QMimeData, **kwargs):
        if cls.__mime_type__ is None:
            return None
        bytes_data = mimeData.data(cls.__mime_type__).data()
        return cls.from_dict(json.loads(bytearray(bytes_data)), **kwargs)
    def to_mime(self) -> Optional[Qt.QMimeData]:
        if self.__mime_type__ is None:
            return None
        ret = Qt.QMimeData()
        dct = json.dumps(self.to_dict())
        ret.setData(self.__mime_type__, bytes(dct, "utf-8"))
        return ret
