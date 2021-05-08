#!/usr/bin/env python3
"""
! Only static import is esuser.User
"""
from os.path import dirname, basename, isfile, join
import glob
modules = glob.glob(join(dirname(__file__), "*.py"))
__all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]
for module in __all__:
    exec("from everskies import {module}".format(module=module))

#Get these out of the everskies module dir now!
del glob
del dirname
del basename
del isfile
del join

#Get this into the everskies module as it is the primary function of esLib for now
User=esuser.User

