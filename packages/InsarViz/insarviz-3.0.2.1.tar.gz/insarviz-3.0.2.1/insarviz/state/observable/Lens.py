"""In this module, we introduce Lenses. Lenses are a first-class
representation of plain accessors, but for dynamic values.

Given a lens L and a structure S, L[S] should produce a dynamic value
that corresponds to what L "points to" in S.

A lens by itself does not provide values, only the means to observe
and modify part of a structure.
"""

from typing import Any
from .__prelude__ import Qt
from .Dynamic import Dynamic, PureDynamic, MapDynamic, SwitchDynamic

class Lens[A,B]:
    def __getitem__(self, instance: A) -> Dynamic[B]:
        return PureDynamic(instance)
    def __truediv__[C](self, l: "Lens[B,C]") -> "Lens[A,C]":
        return ComposeLens(self, SELF / l)
    def __getattr__(self, attr):
        if attr.startswith('__'):
            return super().__getattr__(attr)
        else:
            return self / attr
class ComposeLens[A,B,C](Lens[A,C]):
    def __init__(self, l1: Lens[A,B], l2: Lens[B,C]):
        self.__l1: Lens[A,B] = l1
        self.__l2: Lens[B,C] = l2
    def __getitem__(self, instance):
        return self.__l1[instance].then(self.__l2.__getitem__)
    def __str__(self):
        return f"{self.__l1}/{self.__l2}"
class AttributeLens[A,B](Lens[A,B]):
    def __init__(self, field):
        self.__field: str = field
    def __getitem__(self, instance: A):
        if instance is None:
            return None
        return instance.dynamic_attribute(self.__field)
    def __str__(self):
        return self.__field

class Unique(Lens):
    class __UniqueSig(Dynamic):
        def __init__(self, source_sig):
            super().__init__()
            self.__source_sig = source_sig
            self.__source_sig.value_changed.connect(self.__on_value_changed)

        @Qt.Slot(Any)
        def __on_value_changed(self, old):
            if old != self.value:
                self.value_changed.emit(old)

        @property
        def value(self):
            return self.__source_sig.value
        @value.setter
        def value(self, v):
            self.__source_sig.value = v

    def __init__(self, l):
        self.__l = l
    def __getitem__(self, instance):
        return self.__UniqueSig(self.__l[instance])

class SELFClass:
    def __truediv__(self, l):
        if isinstance(l, str):
            l = AttributeLens(l)
        return l
    def __getitem__(self, instance):
        return PureDynamic(instance)
    def __getattr__(self, attr):
        if attr.startswith('__'):
            return super().__getattr__(attr)
        else:
            return AttributeLens(attr)
SELF = SELFClass()
