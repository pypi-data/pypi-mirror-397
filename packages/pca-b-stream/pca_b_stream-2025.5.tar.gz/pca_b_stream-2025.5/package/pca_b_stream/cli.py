"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

"""
Functions for the command line interface of PCA-B-Stream.
Run doctests below with: python cli.py

>>> import pathlib
>>> import sys
>>> from unittest.mock import patch
>>> path = pathlib.Path(".") / "resource" / "pca-0.png"
>>> with patch("sys.argv", new=["fake_cmd_name", path]):
...     PCA2BStream()
FnmHo0tyN+0}BCI
>>> from skimage.io import imread
>>> import numpy
>>> import pathlib
>>> import sys
>>> import tempfile
>>> from unittest.mock import patch
>>> folder = tempfile.mkdtemp()
>>> path = pathlib.Path(folder) / "a.png"
>>> with patch("sys.argv", new=["fake_cmd_name", "FnmHo0tyN+0}BCI", path]):
...     BStream2PCA()
>>> original_path = pathlib.Path(".") / "resource" / "pca-0.png"
>>> original = imread(original_path)
>>> image = imread(path)
>>> print(numpy.array_equal(image, original))
True
"""

import sys as s
from pathlib import Path as path_t

from skimage.io import imread, imsave

import pca_b_stream.main as pcas


def PCA2BStream() -> None:
    """"""
    error_code = -1

    if s.argv.__len__() != 2:
        print(
            f"{PCA2BStream.__name__.lower()}: No image specified or too many arguments"
        )
        s.exit(error_code)
    error_code -= 1

    path = path_t(s.argv[1])
    if not path.is_file():
        print(f"{path}: Specified path is not a(n existing) file")
        s.exit(error_code)
    error_code -= 1

    try:
        image = imread(path)
    except Exception as exception:
        print(exception)
        s.exit(error_code)
    error_code -= 1

    issues = pcas.PCArrayIssues(image)
    if issues.__len__() > 0:
        issues = "\n    ".join(issues)
        print(f"{path}: Not a valid Piecewise-Constant Array:\n    {issues}")
        s.exit(error_code)
    error_code -= 1

    print(pcas.PCA2BStream(image).decode("ascii"))


def BStream2PCA() -> None:
    """"""
    error_code = -1

    if s.argv.__len__() != 3:
        print(
            f"{BStream2PCA.__name__.lower()}: No stream and output file specified, or too many arguments"
        )
        s.exit(error_code)
    error_code -= 1

    stream = s.argv[1]
    if ("'" in stream) or ('"' in stream):
        print(
            f"{stream}: Stream contains ' or \"; "
            f'Note that the stream must not be passed with the "b" string type prefix'
        )
        s.exit(error_code)
    error_code -= 1

    stream = bytes(stream, "ascii")

    path = path_t(s.argv[2])
    if path.exists():
        print(
            f"{path}: Specified file already exists; Please delete first, or use another filename"
        )
        s.exit(error_code)
    error_code -= 1

    try:
        decoded = pcas.BStream2PCA(stream)
    except Exception as exception:
        print(exception)
        s.exit(error_code)
    error_code -= 1

    imsave(path, decoded)


if __name__ == "__main__":
    #
    import doctest

    doctest.testmod()
