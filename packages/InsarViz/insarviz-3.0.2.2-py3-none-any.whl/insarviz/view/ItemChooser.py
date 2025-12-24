from typing import Any
from .__prelude__ import (Qt, color_icon, SELF, EACH)

class ItemChooser(Qt.QComboBox):
    current_item_changed = Qt.Signal(int, Any)

    def __init__(self, items):
        super().__init__()
        self._items = items
        self._item_names = EACH(SELF.name)[items]
        self._item_names.value_changed.connect(self._on_items_changed)
        self._item_colors = EACH(SELF.color)[items]
        self._item_colors.value_changed.connect(self._on_items_changed)

        self.addItem('(none)', None)
        for i, p in enumerate(self._items):
            self.addItem(color_icon(p.color), p.name, i)
        self.currentIndexChanged.connect(self._on_index_changed)
        self.__current_item = None

    @Qt.Slot(int)
    def _on_index_changed(self, index):
        item_data = self.itemData(index)
        if item_data is None or index == -1:
            self.__current_item = None
            self.current_item_changed.emit(-1, None)
        else:
            self.__current_item = self._items[item_data]
            self.current_item_changed.emit(item_data, self._items[item_data])

    @Qt.Slot(int, str)
    def _on_items_changed(self):
        current = self.__current_item
        current_index = None
        self.clear()
        self.addItem('(none)', None)
        for i, item in enumerate(self._items):
            self.addItem(color_icon(item.color), item.name, i)
            if id(item) == id(current):
                current_index = i
        if current_index is not None:
            self.setCurrentIndex(current_index+1)
