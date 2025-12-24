import qasync
import asyncio
import pathlib
import sys
import rasterio as rio
import pyqtgraph
import argparse
import logging

from .__prelude__ import logger
from .state import WindowState, Dataset
from .view import InsarvizWindow
from .misc import Qt, GLOBAL_THREAD_POOL

def get_args():
    parser = argparse.ArgumentParser(
        prog = "ts_viz",
        description = "InSAR timeseries visualisation"
    )
    parser.add_argument("-l", type=str, default='INFO',
                        help=("set logging level (one of DEBUG, INFO, WARNING, ERROR, CRITICAL) [default INFO]"))
    parser.add_argument("-i", type=str, default=None, help="input filepath")
    return parser.parse_args()
args = get_args()
logger.setLevel(logging.__dict__.get(args.l, logging.INFO))

icon_path = pathlib.Path(__file__).parent / "icons"
logger.info("Setting icon search path to %s", icon_path)
Qt.QDir.addSearchPath('insarviz', icon_path)

class InsarvizApplication:
    def __init__(self):
        default_opengl_format = Qt.QSurfaceFormat.defaultFormat()
         # Necessary for tesselation shaders on Windows where the default OpenGL version is 3.x
        default_opengl_format.setVersion(4, 1)
        default_opengl_format.setProfile(Qt.QSurfaceFormat.OpenGLContextProfile.CoreProfile)
        default_opengl_format.setSwapBehavior(Qt.QSurfaceFormat.SwapBehavior.DoubleBuffer)
        default_opengl_format.setOption(Qt.QSurfaceFormat.FormatOption.DeprecatedFunctions, False)
        Qt.QSurfaceFormat.setDefaultFormat(default_opengl_format)

        Qt.QCoreApplication.setAttribute(Qt.Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
        self.app = Qt.QApplication()
        self.app.setApplicationName("InsarViz")
        self.event_loop = qasync.QEventLoop(self.app)

    def run(self):
        with self.event_loop:
            self.event_loop.run_forever()

logger.info("Initializing Qt Application")
app = InsarvizApplication()
pyqtgraph.setConfigOption("foreground", 'k')
pyqtgraph.setConfigOption("background", 'w')
logger.info("Creating InsarViz window")
win_state = WindowState()
win = InsarvizWindow(win_state)

if args.i is not None:
    # Load the dataset after a small delay, just because we can
    timer = Qt.QTimer()
    timer.setInterval(100)
    timer.setSingleShot(True)
    def load_dataset():
        path = pathlib.Path(args.i)
        logger.debug('Opening file %s', path)
        win.open_file(path)
        logger.debug('Finished opening %s', path)
    timer.timeout.connect(load_dataset)
    timer.start()

win.show()
app.run()
win_state.exit()
logger.info("Exiting InSARViz. Please come back soon !")

GLOBAL_THREAD_POOL.abort_all()
