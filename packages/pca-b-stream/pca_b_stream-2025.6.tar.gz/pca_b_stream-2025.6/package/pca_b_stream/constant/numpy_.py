"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import numpy as nmpy

# See also: nmpy.sctypes and nmpy.sctypeDict
# /!\ Some types have several codes (e.g., "l" = "p" = numpy.int64; see mpy.sctypeDict)
VALID_NUMPY_TYPES = "?" + nmpy.typecodes["AllInteger"] + nmpy.typecodes["Float"]
