"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import dataclasses as d
import secrets as scrt
import typing as h
from pathlib import Path as path_t

import flask as flsk

from si_fi_o.html.home_page import HomePage
from si_fi_o.path.server import NAME_FIELD_SEPARATOR, TIME_STAMP_SEPARATOR
from si_fi_o.session.form import InputFileContents
from si_fi_o.session.session import file_output_t, session_t


@d.dataclass(repr=False, eq=False)
class routes_t:
    home_page_details: dict[str, h.Any]
    form_type: type
    session_type: type
    ProcessSession: h.Callable[
        [session_t],
        tuple[
            tuple[h.Any, ...], tuple[file_output_t, ...] | None, str | tuple[str] | None
        ],
    ]
    ini_section: str
    runtime_folder: path_t = d.field(init=False, default=None)

    def Configure(self, app: flsk.app, /) -> path_t:
        """"""
        _ = app.route("/")(self.LaunchNewSession)
        _ = app.route("/<session_id>", methods=("GET", "POST"))(self.UpdateHomePage)
        _ = app.route("/load/<session_id>", methods=("POST",))(LoadSession)
        _ = app.route("/save/<session_id>")(SaveSession)
        _ = app.route("/delete/<session_id>")(DeleteSession)

        # app.static_folder is an absolute path
        relative_static_folder = path_t(path_t(app.static_folder).name)
        self.runtime_folder = relative_static_folder / "runtime"

        flask_session_folder = self.runtime_folder / "session"
        flask_session_folder.mkdir(parents=True, exist_ok=True)

        return flask_session_folder

    def LaunchNewSession(self) -> flsk.Response:
        """"""
        session_id = scrt.token_urlsafe().replace(
            NAME_FIELD_SEPARATOR, TIME_STAMP_SEPARATOR
        )
        flsk.session[session_id] = self.session_type(
            self.runtime_folder, session_id, self.ini_section
        )

        return flsk.redirect(f"/{session_id}")

    def UpdateHomePage(self, *, session_id: str = None) -> str:
        """"""
        session = flsk.session[session_id]
        form = self.form_type()  # Do not pass flask.request.form

        session.DeleteObsoleteFiles()

        if flsk.request.method == "GET":
            form.Update(session.AsDictionary())
        elif form.validate_on_submit():
            form_data = form.Data()
            session.UpdateInputs(form_data, form.file_fields)

            if session.IsComplete(form=form):
                outputs = self.ProcessSession(session)
                session.UpdateOutputs(*outputs)

        return HomePage(
            session_id, session=session, form=form, **self.home_page_details
        )


def LoadSession(*, session_id: str = None) -> flsk.Response:
    """"""
    session = flsk.session[session_id]

    contents = InputFileContents().decode("ascii")
    session.UpdateFromINIContents(contents)

    return flsk.redirect(f"/{session_id}")


def SaveSession(*, session_id: str = None) -> flsk.Response:
    """"""
    session = flsk.session[session_id]

    name, path = session.SaveForDownload()

    return flsk.send_file(
        path, mimetype="text/plain", as_attachment=True, download_name=name
    )


def DeleteSession(*, session_id: str = None) -> flsk.Response:
    """"""
    session = flsk.session[session_id]

    session.DeleteInputFiles()
    session.DeleteOutputFiles()
    session.DeleteFileForDownload()

    flsk.session.pop(session_id, None)

    return flsk.redirect("/")
