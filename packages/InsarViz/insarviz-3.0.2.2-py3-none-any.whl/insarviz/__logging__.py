import logging
import pathlib
import os

logger = logging.getLogger('insarviz')

INSARVIZ_ROOT = str(pathlib.Path(__file__).parent.parent) + os.sep

class InsarvizFilter:
    def filter(self, record):
        return record.name.startswith("insarviz")
logger.addFilter(InsarvizFilter())
logger.setLevel(logging.DEBUG)

class InsarvizFormatter(logging.Formatter):
    def __init__(self):
        super().__init__('%(asctime)s.%(msecs)03d %(levelname)s %(modulepath)s:%(lineno)d: %(message)s',
                         datefmt = '%Y-%m-%d %H:%M:%S')
    def format(self, record):
        record.modulepath = record.pathname.removeprefix(INSARVIZ_ROOT).removesuffix(".py").replace(os.sep, ".")
        return super().format(record)

log_handler = logging.StreamHandler()
log_handler.setFormatter(InsarvizFormatter())
logger.addHandler(log_handler)
