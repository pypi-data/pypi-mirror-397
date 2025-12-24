# SPDX-FileCopyrightText: 2023 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

"""
h2 tank optimization
"""

from importlib import metadata
from pathlib import Path

from patme import getPyprojectMeta
from patme.service.logger import log

from tankoh2.settings import PychainWrapper

name = Path(__file__).parent.name

try:
    # if full git repo is present, read pyproject.toml
    pkgMeta = getPyprojectMeta(__file__)
    version = str(pkgMeta["version"])
    programDir = str(Path(__file__).parents[2])
    description = str(pkgMeta["description"])
except FileNotFoundError:
    try:
        # package is installed
        version = metadata.version(name)
        programDir = str(Path(__file__).parent)
        description = metadata.version(name)
    except metadata.PackageNotFoundError:
        # We have only the source code or somehow the package is corrupt
        version = str("version not provided")
        programDir = str(Path(__file__).parent)
        description = ""

# create logger file handlers
log.addFileHandlers(programDir, "run.log", "debug.log")

# make mycropychain available
pychainIsLoaded = False
pychain = PychainWrapper()
