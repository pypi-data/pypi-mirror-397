"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

PROJECT_NAME = "PCA-B-Stream"
APP_NAME = "pca_b_stream"
NAME_MEANING = "Byte Stream Representation of Piecewise-Constant Array"
SHORT_DESCRIPTION = (
    "Generation of a printable byte stream representation of a piecewise-constant Numpy array, "
    "and re-creation of the array from the byte stream."
)

DETAILS_LEGEND = {
    "m": "Max. value in array (= number of sub-streams)",
    "c": "Compressed",
    "e": "Byte order (a.k.a. endianness)",
    "t": "dtype code",
    "T": "dtype name",
    "o": "Enumeration order",
    "v": "First value per sub-stream (0: 0 or False, 1: non-zero or True)",
    "d": "Array dim.",
    "l": "Lengths per dim.",
}
