

import logging
import os
from datetime import datetime

import glasswall


# 2021-03-22 17:34:59.428	glasswall.config.logging     	INFO    	__init__		 Loaded Glasswall Editor version 2.0 from C:\Users\AngusRoberts\Documents\Azure\gated-check-in\gated_check_in\data\combined_libraries\gcin\glasswall_core2.dll
fmt = "%(asctime)s.%(msecs)03d\t%(name)-29s\t%(levelname)-8s\t%(funcName)s\t\t %(message)s"

# 2020-06-25 15:04:59
datefmt = "%Y-%m-%d %H:%M:%S"

# %temp%/glasswall/logs/2020-06-25 150459.txt
log_file_path = os.path.join(glasswall._TEMPDIR, "logs", f'{datetime.now().strftime("%Y-%m-%d %H%M%S")}.txt')

# Ensure log directory exists
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

# Logging to file
log = logging.getLogger(__name__)
log_handler = logging.FileHandler(log_file_path, mode="w", delay=True)
log_handler.setFormatter(logging.Formatter(fmt, datefmt))
log.addHandler(log_handler)
log.setLevel(logging.INFO)

# Logging to console
console = logging.StreamHandler()
console.setFormatter(logging.Formatter(fmt, datefmt))
console.setLevel(logging.INFO)
log.addHandler(console)
