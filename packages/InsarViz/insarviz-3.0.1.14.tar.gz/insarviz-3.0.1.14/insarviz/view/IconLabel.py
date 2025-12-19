from .__prelude__ import Qt

class IconLabel(Qt.QLabel):
    def __init__(self, icon, size = Qt.QSize(16,16)):
        super().__init__()
        self.setPixmap(icon.pixmap(size))
