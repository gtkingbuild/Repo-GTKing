# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# XBMC entry point
# ------------------------------------------------------------


import os
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

from platformcode import config, logger

logger.info("init...")

librerias = os.path.join(config.get_runtime_path(), 'lib')
sys.path.append(librerias)
for module in ['script.module.futures']:
    if PY3: continue
    config.importer(module)

from platformcode import launcher

if sys.argv[2] == "":
    launcher.start()
    launcher.run()
else:
    launcher.run()
