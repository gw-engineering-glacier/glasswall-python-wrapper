

import logging
import os
from datetime import datetime

import glasswall

fmt = "%(asctime)s.%(msecs)03d %(name)-9s %(levelname)-8s %(funcName)-25s %(message)s"
# datefmt "2020-06-25 15:04:59"
datefmt = "%Y-%m-%d %H:%M:%S"
# log_file_path "2020-06-25 150459.txt"
log_file_path = os.path.join(glasswall._TEMPDIR, "logs", f'{datetime.now().strftime("%Y-%m-%d %H%M%S")}.txt')
# Create log directory
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

# Logging to file
logging.basicConfig(
    level=logging.INFO,
    format=fmt,
    datefmt=datefmt,
    filename=log_file_path,
    filemode="w",
)
log = logging.getLogger("glasswall")

# Logging to console
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter(fmt, datefmt=datefmt))
logging.getLogger("").addHandler(console)
