'''
This package provides a web client interface to virtual data lakes.
It has a main module - vdl - that provides the functionality, and
a supporting module - parts - that handles the extraction of parts from 
multipart/form-data-encoded HTTP content.

'''

from . import vdlcopy
from . import vdl
from . import parts

__all__ = ["vdl", "vdlcopy", "parts"]
