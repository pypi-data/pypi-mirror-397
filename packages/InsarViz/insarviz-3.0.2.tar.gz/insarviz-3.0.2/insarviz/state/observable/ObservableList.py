from typing import Any

from .__prelude__ import Qt, logger
from .Dynamic import Dynamic
from .Lens import Lens

class ObservableList[T](Qt.QObject):
    """A basic wrapper over raw Python lists (arrays), that provides
    signals to notify when and how the list's contents change.

    beginRemoveRange(start, stop): emitted before removing the range (start,stop).
    endRemoveRange(start, stop): emitted after removing the range (start,stop)
    beginReplaceRange(start, stop): emitted before replacing elements between 'start' and 'stop'
    endReplaceRange(start, stop): emitted after replacing elements between 'start' and 'stop'
    beginInsertRange(start, length): emitted before inserting 'length' elements at index 'start'
    endInsertRange(start, length): emitted after inserting 'length' elements at index 'start'
    """

    beginRemoveRange = Qt.Signal(int, int)
    endRemoveRange = Qt.Signal(int, int)
    beginReplaceRange = Qt.Signal(int, int)
    endReplaceRange = Qt.Signal(int, int)
    beginInsertRange = Qt.Signal(int, int)
    endInsertRange = Qt.Signal(int, int)

    def __init__(self, *elems: T):
        super().__init__()
        self._values: list[T] = [e for e in elems]

    def __len__(self):
        return len(self._values)
    def __getitem__(self, i):
        return self._values[i]
    def __setitem__(self, i, v):
        if isinstance(i, slice):
            start, stop, _ = i.indices(len(self._values))
            values = v
        else:
            start, stop = i,i+1
            values = [v]
        stop_after = start+len(values)
        inserted = max(0, stop_after-stop)
        replaced = len(values)-inserted
        if replaced > 0:
            self.beginReplaceRange.emit(start, start+replaced)
            self._values[start:start+replaced] = values[:replaced]
            self.endReplaceRange.emit(start, start+replaced)
        if stop > stop_after:
            self.beginRemoveRange.emit(stop_after, stop)
            self._values[stop_after:stop] = []
            self.endRemoveRange.emit(stop_after, stop)
        if inserted > 0:
            self.beginInsertRange.emit(stop, inserted)
            self._values[stop:stop] = values[replaced:]
            self.endInsertRange.emit(stop, inserted)

    def __iter__(self):
        return iter(self._values)
    def __repr__(self):
        return repr(self._values)
    def map(self, func, delete_func = None):
        return MapList(func, self, delete_func)
    def map_lens(self, lens):
        return MapList(lens.__getitem__, self)
    def sequence(self):
        return SequenceList(self)

    def append(self, elem):
        self[len(self):] = [elem]

    def import_context(self) -> dict:
        return {}

class MapList(ObservableList):
    beginRemoveRange = Qt.Signal(int, int)
    endRemoveRange = Qt.Signal(int, int)
    beginReplaceRange = Qt.Signal(int, int)
    endReplaceRange = Qt.Signal(int, int)
    beginInsertRange = Qt.Signal(int, int)
    endInsertRange = Qt.Signal(int, int)

    def __init__(self, func, l, delete_func = None):
        super().__init__(*(func(e) for e in l))
        self.__list = l
        self.__func = func
        self.__delete_func = delete_func
        self.__list.beginRemoveRange.connect(self.__begin_remove_range)
        self.__list.endRemoveRange.connect(self.__end_remove_range)
        self.__list.beginInsertRange.connect(self.__begin_insert_range)
        self.__list.endInsertRange.connect(self.__end_insert_range)
        self.__list.beginReplaceRange.connect(self.__begin_replace_range)
        self.__list.endReplaceRange.connect(self.__end_replace_range)

    @Qt.Slot(int, int)
    def __begin_remove_range(self, start, end):
        self.beginRemoveRange.emit(start,end)
    @Qt.Slot(int, int)
    def __end_remove_range(self, start, end):
        if self.__delete_func is not None:
            for i in range(start, end):
                self.__delete_func(i, self._values[i])
        self._values[start:end] = []
        self.endRemoveRange.emit(start,end)
    @Qt.Slot(int, int)
    def __begin_insert_range(self, start, size):
        self.beginInsertRange.emit(start,size)
    @Qt.Slot(int, int)
    def __end_insert_range(self, start, size):
        self._values[start:start] = [self.__func(e) for e in self.__list[start:start+size]]
        self.endInsertRange.emit(start,size)
    @Qt.Slot(int, int)
    def __begin_replace_range(self, start, end):
        self.beginReplaceRange.emit(start,end)
    @Qt.Slot(int, int)
    def __end_replace_range(self, start, end):
        if self.__delete_func is not None:
            for i in range(start, end):
                self.__delete_func(i, self._values[i])
        self._values[start:end] = [self.__func(e) for e in self.__list[start:end]]
        self.endReplaceRange.emit(start,end)

class SequenceList(Dynamic):
    class __ElemCallback:
        def __init__(self, callback, index):
            self.__callback = callback
            self.index = index
        def __call__(self, *args):
            return self.__callback(self.index, *args)

    def __init__(self, l):
        super().__init__()
        self.__list = l
        self.__callbacks = [self.__ElemCallback(self.__elem_changed,i) for i in range(len(self.__list))]
        for cb in self.__callbacks:
            self.__list[cb.index].value_changed.connect(cb)
        self.__values = [sig.value for sig in l]
        self.__list.beginRemoveRange.connect(self.__begin_remove_range)
        self.__list.endRemoveRange.connect(self.__end_remove_range)
        self.__list.endInsertRange.connect(self.__end_insert_range)
        self.__list.beginReplaceRange.connect(self.__begin_replace_range)
        self.__list.endReplaceRange.connect(self.__end_replace_range)

    @property
    def value(self):
        return self.__values

    def __setitem__(self, i, val):
        self.__list[i].value = val

    @Qt.Slot(int, Any)
    def __elem_changed(self, index, old_val):
        old_values = [*self.__values]
        self.__values[index] = self.__list[index].value
        self.value_changed.emit(old_values)

    @Qt.Slot(int, int)
    def __begin_remove_range(self, start, end):
        for cb in self.__callbacks[start:end]:
            self.__list[cb.index].value_changed.disconnect(cb)
    @Qt.Slot(int, int)
    def __end_remove_range(self, start, end):
        self.__callbacks[start:end] = []
        size = end-start
        for cb in self.__callbacks[start:]:
            cb.index -= size
        old_values = [*self.__values]
        self.__values[start:end] = []
        self.value_changed.emit(old_values)
    @Qt.Slot(int, int)
    def __end_insert_range(self, start, size):
        for cb in self.__callbacks[start:]:
            cb.index += size
        self.__callbacks[start:start] = [self.__ElemCallback(self.__elem_changed, i) for i in range(start, start+size)]
        for i in range(start,start+size):
            cb = self.__callbacks[i]
            self.__list[cb.index].value_changed.connect(cb)
        old_values = [*self.__values]
        self.__values[start:start] = [self.__list[i].value for i in range(start, start+size)]
        self.value_changed.emit(old_values)
    @Qt.Slot(int, int)
    def __begin_replace_range(self, start, end):
        for i in range(start, end):
            self.__list[i].value_changed.disconnect(self.__callbacks[i])
    @Qt.Slot(int, int)
    def __end_replace_range(self, start, end):
        for i in range(start, end):
            self.__list[i].value_changed.connect(self.__callbacks[i])
        old_values = [*self.__values]
        self.__values[start:end] = [self.__list[i].value for i in range(start,end)]
        self.value_changed.emit(old_values)

class EACH(Lens):
    def __init__(self, elem_lens):
        self.__elem_lens = elem_lens
    def __getitem__(self, instance):
        return instance.map_lens(self.__elem_lens).sequence()
