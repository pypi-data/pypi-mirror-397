"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import datetime as dttm
import re as regx
import typing as h
from pathlib import Path as path_t

from si_fi_o.session.constants import SESSION_DURATION as MAXIMUM_SERVER_FILE_AGE
from werkzeug.utils import secure_filename as SecureFilenameVersion

NAME_FIELD_SEPARATOR = "-"
TIME_STAMP_SEPARATOR = "_"

_SERVER_FILENAME_FORMAT = (
    "{session_id}"
    + NAME_FIELD_SEPARATOR
    + "{time_stamp}"
    + NAME_FIELD_SEPARATOR
    + "{name}"
)
_NOT_FIELD_SEPARATOR = f"[^{NAME_FIELD_SEPARATOR}]+"
_SERVER_FILENAME_PATTERN = _SERVER_FILENAME_FORMAT.format(
    session_id=_NOT_FIELD_SEPARATOR, time_stamp=f"({_NOT_FIELD_SEPARATOR})", name=".+"
)
_SERVER_FILENAME_PATTERN = regx.compile(_SERVER_FILENAME_PATTERN)

_MAXIMUM_SERVER_FILE_AGE = dttm.timedelta(seconds=MAXIMUM_SERVER_FILE_AGE)
_DATE_TIME_REPLACEMENTS = str.maketrans(
    f"{NAME_FIELD_SEPARATOR}:.", 3 * TIME_STAMP_SEPARATOR
)
# See: https://docs.python.org/3/library/datetime.html#datetime.datetime.isoformat
#     YYYY-MM-DDTHH:MM:SS.ffffff
_DATE_TIME_ISO_FORMAT = "{}-{}-{}T{}:{}:{}.{}"
_DATE_TIME_PATTERN = regx.compile(
    "([0-9]{4})_([0-9]{2})_([0-9]{2})T([0-9]{2})_([0-9]{2})_([0-9]{2})_([0-9]{6})"
)


class file_t(h.NamedTuple):
    client_name: str
    server_path: path_t


def ServerVersionOfFilename(name: str, session_id: str, /) -> str:
    """"""
    time_stamp = (
        dttm.datetime.now()
        .isoformat(timespec="microseconds")
        .translate(_DATE_TIME_REPLACEMENTS)
    )

    return _TimeStampedFilename(name, session_id, time_stamp)


def ServerFilesIterator(
    folder: path_t, session_id: str, /, *, name: str | None = None
) -> h.Iterator[path_t]:
    """
    The default value of "name" could be "*". However, to "simplify" the test in "_TimeStampedFilename", None is used
    instead.
    """
    return folder.glob(_TimeStampedFilename(name, session_id, "*"))


def OutdatedServerFilesIterator(folder: path_t, /) -> h.Iterator[path_t]:
    """"""
    now = dttm.datetime.now()

    for name in folder.glob("*"):
        # Does voluntarily not test matching success since not matching must raise an error
        match = _SERVER_FILENAME_PATTERN.fullmatch(str(name))
        time_stamp = match.group(1)

        # Does voluntarily not test matching success since not matching must raise an error
        match = _DATE_TIME_PATTERN.fullmatch(time_stamp)
        as_tuple = tuple(match.group(_idx) for _idx in range(1, 8))
        iso_date_time = _DATE_TIME_ISO_FORMAT.format(*as_tuple)
        date_time = dttm.datetime.fromisoformat(iso_date_time)

        if date_time + _MAXIMUM_SERVER_FILE_AGE < now:
            yield folder / name


def _TimeStampedFilename(name: str | None, session_id: str, time_stamp: str, /) -> str:
    """"""
    if name is None:
        name = "*"
    else:
        name = SecureFilenameVersion(name)

    return _SERVER_FILENAME_FORMAT.format(
        session_id=session_id, time_stamp=time_stamp, name=name
    )


if TIME_STAMP_SEPARATOR == NAME_FIELD_SEPARATOR:
    raise ValueError("This error should not have happened; Please, contact developer")
