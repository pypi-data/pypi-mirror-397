"""
In this module, we introduce the notion of "dynamic values".

A dynamic value is a value that changes across time, that can be
listened to, read, and sometimes written to.

In this form, dynamic values may be composed to provide more complex
behaviours, such as switching between value sources, or transforming
values on the fly.
"""

from typing import Any
from collections.abc import Callable
from .__prelude__ import Qt
import weakref

class Dynamic[A](Qt.QObject):
    value_changed = Qt.Signal(Any)

    @property
    def value(self) -> A:
        raise NotImplementedError
    @value.setter
    def value(self, v: A):
        raise NotImplementedError

    def drive(self, func):
        self.value_changed.connect(lambda: func(self.value))
        func(self.value)

    def map(self, func, *other_sigs):
        return MapDynamic(func, self, *other_sigs)
    def join(self):
        return SwitchDynamic(self)
    def then(self, func, *other_sigs):
        return self.map(func, *other_sigs).join()

class MapDynamic(Dynamic):
    def __init__(self, f, *sigs):
        super().__init__()
        self.__f = f
        self.__sigs = sigs
        self.__current_value = self.__f(*(sig.value for sig in self.__sigs))
        for sig in self.__sigs:
            sig.value_changed.connect(self.__on_base_changed)

    @property
    def value(self):
        return self.__current_value

    def __on_base_changed(self, _old):
        old = self.__current_value
        self.__current_value = self.__f(*(sig.value for sig in self.__sigs))
        self.value_changed.emit(old)

class PureDynamic[A](Dynamic[A]):
    def __init__(self, initial):
        super().__init__()
        self.__value: A = initial

    @property
    def value(self):
        return self.__value
    @value.setter
    def value(self, v):
        old = self.__value
        self.__value = v
        self.value_changed.emit(old)

    def dynamic_attribute(self, name):
        return self

class SwitchDynamic[A](Dynamic[A]):
    def __init__(self, sig_sig: Dynamic[Dynamic[A]]):
        super().__init__()
        self.__sig_sig: Dynamic[Dynamic[A]] = sig_sig
        self.__current_sig: Dynamic[A] = sig_sig.value
        if self.__current_sig is None:
            self.__current_sig = PureDynamic(None)
        self.__current_sig.value_changed.connect(self.__on_current_changed)
        self.__sig_sig.value_changed.connect(self.__on_signal_changed)

    @property
    def value(self):
        return self.__current_sig.value
    @value.setter
    def value(self, v):
        self.__current_sig.value = v

    def __on_current_changed(self, old: A):
        self.value_changed.emit(old)
    def __on_signal_changed(self, old_sig: Dynamic[A]):
        self.__current_sig.value_changed.disconnect(self.__on_current_changed)
        new_sig = self.__sig_sig.value
        if new_sig is None:
            self.__current_sig = PureDynamic(None)
        else:
            self.__current_sig = new_sig
        self.__current_sig.value_changed.connect(self.__on_current_changed)
        if old_sig is None:
            self.value_changed.emit(None)
        else:
            self.value_changed.emit(old_sig.value)
