"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

from pathlib import Path as path_t

import flask as flsk


def URLOfPath(path: path_t, /) -> str:
    """"""
    parts = path.parts

    return flsk.url_for(str(parts[0]), filename=str(path_t(*parts[1:])))
