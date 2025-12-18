"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import datetime as dttm
import secrets as scrt
import typing as h

from flask import Flask as flask_app_t
from flask_bootstrap import Bootstrap as BootstrapFlask
from flask_session import Session as flask_session_t

from si_fi_o.routes import routes_t
from si_fi_o.session.constants import SESSION_DURATION
from si_fi_o.session.session import file_output_t, session_t

# def FlaskApp(html_folder: str, /) -> flask_app_t:
#     """
#     Just for reference. The app must be created within the specific project in order
#     to set the template folder.
#     """
#     return flask_app_t(__name__, template_folder=html_folder)


def ConfigureApp(
    app: flask_app_t,
    home_page_details: dict[str, h.Any],
    form_type: type,
    session_type: type,
    max_upload_size: int,
    ProcessSession: h.Callable[
        [session_t],
        tuple[
            tuple[h.Any, ...], tuple[file_output_t, ...] | None, str | tuple[str] | None
        ],
    ],
    ini_section: str,
    /,
) -> None:
    """
    max_upload_size: in megabytes
    """
    routes = routes_t(
        home_page_details=home_page_details,
        form_type=form_type,
        session_type=session_type,
        ProcessSession=ProcessSession,
        ini_section=ini_section,
    )
    flask_session_folder = routes.Configure(app)

    app.config.from_mapping(
        PREFERRED_URL_SCHEME="https",
        SESSION_TYPE="filesystem",
        PERMANENT_SESSION_LIFETIME=dttm.timedelta(seconds=SESSION_DURATION),
        SESSION_FILE_DIR=flask_session_folder,
        SECRET_KEY=scrt.token_bytes(),
        MAX_CONTENT_LENGTH=max_upload_size * 1024 * 1024,
    )
    flask_session_t(app)
    BootstrapFlask(app)
