"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import typing as h

import dominate.tags as html
from flask import render_template as RenderHTML
from si_fi_o.html.session import SessionInputsAsHTML as SessionInputsAsHTMLDefault
from si_fi_o.html.session import SessionManagementAsHTML
from si_fi_o.html.session import SessionOutputsAsHTML as SessionOutputsAsHTMLDefault
from si_fi_o.session.form import form_t
from si_fi_o.session.session import session_t


def HomePage(
    session_id: str,
    /,
    *,
    session: session_t = None,
    form: form_t = None,
    html_template: str = "main.html",
    name: str = "<Missing Name>",
    name_meaning: str = "<Missing Name Meaning>",
    about: html.html_tag = None,
    SessionInputsAsHTML: h.Callable[
        [session_t, str], html.html_tag
    ] = SessionInputsAsHTMLDefault,
    max_file_size: int = 1,
    SessionOutputsAsHTML: h.Callable[
        [session_t], html.html_tag
    ] = SessionOutputsAsHTMLDefault,
) -> str:
    """"""
    return RenderHTML(
        html_template,
        name=name,
        name_meaning=name_meaning,
        about=about,
        session=SessionInputsAsHTML(session, session_id),
        form=form,
        max_file_size=max_file_size,
        outputs=SessionOutputsAsHTML(session),
        data_management=SessionManagementAsHTML(session, session_id),
    )
