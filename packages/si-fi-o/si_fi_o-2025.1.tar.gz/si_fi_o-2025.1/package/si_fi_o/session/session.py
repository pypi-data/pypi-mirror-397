"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import typing as h
from configparser import ConfigParser as ini_config_t
from pathlib import Path as path_t
from zipfile import ZipFile as zip_file_t

from flask_wtf import FlaskForm as flask_form_t
from si_fi_o.path.server import (
    OutdatedServerFilesIterator,
    ServerFilesIterator,
    ServerVersionOfFilename,
    file_t,
)
from werkzeug.datastructures import FileStorage as file_storage_t

_SESSION_FILENAME = "session.ini"


class file_output_t(h.NamedTuple):
    name: str
    contents: h.Any
    Write: h.Callable[[path_t, h.Any], None]


class session_t(dict):
    """
    To be stored in a Flask session
    """

    session_id: str = None
    form_file_fields: tuple[str, ...] = None
    input_folder: path_t = None  # Used as upload folder
    output_folder: path_t = None  # Also for si-fi-o sessions
    outputs_path: path_t | None = None  # Main, downloadable outputs file
    additional_paths: dict[str, path_t] | None = None  # Additional output files
    outputs: h.Any = None
    ini_section: str = None

    def __init__(
        self, base_folder: path_t, session_id: str, ini_section: str, *args, **kwargs
    ) -> None:
        """"""
        super().__init__(*args, **kwargs)

        self.session_id = session_id
        self.ini_section = ini_section

        self.input_folder = base_folder / "input"
        self.output_folder = base_folder / "output"
        for folder in (self.input_folder, self.output_folder):
            folder.mkdir(parents=True, exist_ok=True)

    def UpdateInputs(
        self, inputs: dict[str, h.Any], file_fields: h.Sequence[str], /
    ) -> None:
        """"""
        if not set(file_fields).issubset(inputs.keys()):
            raise ValueError(
                f"{file_fields}: Form file fields not a subset of form fields {tuple(inputs.keys())}"
            )

        for field, value in inputs.items():
            # Only file field values can be None (see si_fi_o.session.form.form_t.Data). In order to preserve session
            # values, None inputs are disregarded. This means that when deleting input files in DeleteInputFiles,
            # self[field] might not exist.
            if value is not None:
                if isinstance(value, file_storage_t):
                    _DeleteInputFile(self, field)
                    name, path = _SaveInputFile(
                        value, self.input_folder, self.session_id
                    )
                    value = file_t(client_name=name, server_path=path)

                self[field] = value

        self.form_file_fields = tuple(file_fields)

    def InputFilesContents(
        self, LoadInput: h.Callable[[path_t], h.Any], /
    ) -> dict[str, h.Any]:
        """
        Example:
            inputs = session.InputFilesContents(skimage.io.imread)
        """
        return {_inp: LoadInput(self[_inp][1]) for _inp in self.form_file_fields}

    def DeleteInputFiles(self) -> None:
        """"""
        if self.form_file_fields is not None:
            for field in self.form_file_fields:
                _DeleteInputFile(self, field)

    def UpdateOutputs(
        self,
        outputs: h.Any,
        file_outputs: tuple[file_output_t, ...] | None,
        main_outputs: str | tuple[str] | None,
        /,
    ) -> None:
        """"""
        self.outputs = outputs

        _DeleteFile(self.outputs_path)
        if self.additional_paths is not None:
            for path in self.additional_paths.values():
                _DeleteFile(path)

        if file_outputs is None:
            self.outputs_path = None
            self.additional_paths = None
            return

        if main_outputs is None:
            main_outputs = ()
        elif isinstance(main_outputs, str):
            main_outputs = (main_outputs,)

        paths_for_zip = []
        additional_paths = {}
        for file_output in file_outputs:
            path = self.output_folder / ServerVersionOfFilename(
                file_output.name, self.session_id
            )
            file_output.Write(path, file_output.contents)

            if file_output.name in main_outputs:
                paths_for_zip.append(path)
            else:
                additional_paths[file_output.name] = path

        if (n_paths := paths_for_zip.__len__()) == 0:
            self.outputs_path = None
        elif n_paths == 1:
            self.outputs_path = paths_for_zip[0]
        else:
            name = str(path_t(main_outputs[0]).stem) + ".zip"
            path = self.output_folder / name
            with zip_file_t(path, "w") as accessor:
                for for_zip in paths_for_zip:
                    accessor.write(for_zip)
            self.outputs_path = path

        if additional_paths.__len__() == 0:
            self.additional_paths = None
        else:
            self.additional_paths = additional_paths

    def DeleteOutputFiles(self) -> None:
        """"""
        self.UpdateOutputs(None, None, None)

    def DeleteObsoleteFiles(self) -> None:
        """"""
        for folder in (self.input_folder, self.output_folder):
            for path in OutdatedServerFilesIterator(folder):
                _DeleteFile(path)

    def UpdateFromINIContents(self, contents: str, /) -> None:
        """"""
        config = ini_config_t()
        config.read_string(contents)

        # Form file fields are not file_t's then, so the loaded session cannot be used as is
        for field, value in config.items(self.ini_section):
            self[field] = value

    def AsDictionary(self) -> dict[str, h.Any]:
        """"""
        return dict(self)

    def SaveForDownload(self) -> tuple[str, path_t]:
        """
        Does include form file fields but filenames only since paths of input files cannot be stored in a session as
        they are only known by the client.
        """
        config = ini_config_t()

        config[self.ini_section] = {
            _fld: _val.client_name if isinstance(_val, file_t) else _val
            for _fld, _val in self.items()
        }

        name = ServerVersionOfFilename(_SESSION_FILENAME, self.session_id)
        path = self.output_folder / name
        with open(path, "w") as accessor:
            config.write(accessor)

        return name, path

    def DeleteFileForDownload(self) -> None:
        """
        Delete downloadable session file created by SaveForDownload
        """
        for path in ServerFilesIterator(
            self.output_folder, self.session_id, name=_SESSION_FILENAME
        ):
            _DeleteFile(path)

    @property
    def is_empty(self) -> bool:
        """"""
        return self.__len__() == 0

    def IsComplete(self, *, form: flask_form_t = None) -> bool:
        """
        form: Useful when the form has several submission buttons, and thus different completeness definitions
        """
        # Do not use self[_key] below since reference and/or detection files are missing if the form has been submitted
        # without these files (they are not required fields since the session can supply them) and the session has not
        # received these files yet, e.g. on the first run if not selecting these files.
        return (
            (not self.is_empty)
            and all(_val is not None for _val in self.values())
            and (self.form_file_fields is not None)
            and all(
                isinstance(self.get(_key), file_t) for _key in self.form_file_fields
            )
        )


def _SaveInputFile(
    file: file_storage_t, folder: path_t, session_id: str, /
) -> tuple[str, path_t]:
    """"""
    client_name = file.filename
    server_path = folder / ServerVersionOfFilename(client_name, session_id)

    file.save(server_path)

    return client_name, server_path


def _DeleteFile(path: path_t | None, /) -> None:
    """"""
    if (path is not None) and path.is_file():
        path.unlink()


def _DeleteInputFile(session: session_t, field: str, /) -> None:
    """"""
    if (file := session.get(field)) is not None:
        _DeleteFile(file.server_path)
