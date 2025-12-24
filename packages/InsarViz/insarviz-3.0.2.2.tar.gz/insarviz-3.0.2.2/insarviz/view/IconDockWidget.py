from typing import Optional

from .__prelude__ import Qt

class IconDockStyle(Qt.QProxyStyle):

    # adapted from https://stackoverflow.com/a/3482795

    def __init__(self, icon: Qt.QIcon, style: Optional[Qt.QStyle] = None):
        super().__init__(style)
        self.icon = icon

    def drawControl(self, element: Qt.QStyle.ControlElement, option: Qt.QStyleOption, painter: Qt.QPainter,
                    widget: Optional[Qt.QWidget] = None) -> None:
        if element == Qt.QStyle.ControlElement.CE_DockWidgetTitle:
            # width of the icon
            width: int = self.pixelMetric(Qt.QStyle.PixelMetric.PM_TabBarIconSize)
            # margin of title from frame
            margin: int = self.baseStyle().pixelMetric(Qt.QStyle.PixelMetric.PM_DockWidgetTitleMargin)
            icon_point = Qt.QPoint(margin + option.rect.left(),
                                   margin + option.rect.center().y() - width//2)
            painter.drawPixmap(icon_point, self.icon.pixmap(width, width))
            option.rect = option.rect.adjusted(width, 0, 0, 0)
        self.baseStyle().drawControl(element, option, painter, widget)


def add_icon_to_tab(window: Qt.QMainWindow, tab_name: str, icon: Qt.QIcon):
    # adapted from https://stackoverflow.com/a/46623219
    def f(_):
        try:
            for tabbar in window.findChildren((Qt.QTabBar)):
                for i in range(tabbar.count()):
                    if tabbar.tabText(i) == tab_name:
                        tabbar.setTabIcon(i, icon)
        except RuntimeError:
            # window has been deleted
            pass
    return f


class IconDockWidget(Qt.QDockWidget):

    def __init__(self, name: str, parent: Qt.QWidget, icon: Qt.QIcon):
        assert isinstance(parent, Qt.QMainWindow)
        super().__init__(name, parent)
        self.setStyle(IconDockStyle(icon))
        self.__callback = add_icon_to_tab(parent, name, icon)
        self.visibilityChanged.connect(self.__callback)
        self.topLevelChanged.connect(self.__callback)
        self.dockLocationChanged.connect(self.__callback)
        self.hide()
