"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import dominate.tags as html
import flask as flsk
from si_fi_o.path.html import URLOfPath
from si_fi_o.path.server import file_t
from si_fi_o.session.form import form_t
from si_fi_o.session.session import session_t


def SessionInputsAsHTML(
    session: session_t | None,
    session_id: str,
    /,
    *,
    save_fname: str = "SaveSession",
    load_fname: str = "LoadSession",
) -> html.html_tag:
    """"""
    output = html.div()

    empty_form = form_t()
    file_fields = empty_form.file_fields
    field_names_to_labels = empty_form.fields_to_labels

    if (is_none := (session is None)) or session.is_empty:
        if is_none:
            session = {}
        save = None
    else:
        save = html.a(
            html.button(
                "Save Session",
                type="button",
                style="margin-right:24pt; margin-top: 12pt; margin-bottom: 24pt",
            ),
            href=flsk.url_for("." + save_fname, session_id=session_id),
        )
    load = _SessionLoadingForm(session_id, load_fname)

    row = None
    for idx, (name, label) in enumerate(field_names_to_labels.items()):
        value = session.get(name, "")
        if isinstance(value, file_t):
            value = value.client_name
        elif isinstance(value, str) and (value.__len__() > 0) and (name in file_fields):
            # The value has been assigned by a session loading, which does not produce valid form file fields
            value = html.span(
                f"{value} (must be re-uploaded)",
                style="color:Crimson; font-weight:bold",
            )

        if idx % 2 == 0:
            if row is not None:
                output.add(row)
            row = html.div()
        row.add(html.div(f"{label}: ", value))

    if row is not None:
        output.add(row)

    table = html.table()
    with table:
        with html.tr():
            if save is not None:
                html.td(save)
            html.td(load)
    output.add(table)

    return output


def SessionOutputsAsHTML(session: session_t, /) -> html.html_tag | None:
    """
    Dummy version. Actual version is specific to the project.
    Needs to be kept in sync with the processing function since it assigns the outputs.
    """
    if session.outputs is None:
        return None

    return None


def SessionManagementAsHTML(
    session: session_t, session_id: str, /, *, delete_fname: str = "DeleteSession"
) -> html.html_tag | None:
    """"""
    if session is None:
        return None

    if (path := session.outputs_path) is None:
        output_url = None
    else:
        output_url = URLOfPath(path)

    output = html.div()
    with output:
        if output_url is not None:
            html.a(
                html.button(
                    "Download Result",
                    type="button",
                    style="margin-top: 8pt; margin-bottom: 12pt",
                ),
                href=output_url,
                download="",
            )
            html.span(style="margin-right:48pt")
        html.a(
            html.button(
                html.b("Clear All Data"),
                type="button",
                style="margin-top: 8pt; margin-bottom: 12pt",
            ),
            href=flsk.url_for("." + delete_fname, session_id=session_id),
        )

    return output


def _SessionLoadingForm(session_id: str, load_fname: str, /) -> html.form:
    """"""
    output = html.form(
        role="form",
        method="post",
        enctype="multipart/form-data",
        action=flsk.url_for("." + load_fname, session_id=session_id),
        style="margin-bottom: 12pt",
    )

    with output:
        html.label("Load Session")
        html.input_(
            type="file",
            name="session",
            required=True,
            style="margin-top: 12pt; margin-bottom: 12pt",
        )
        html.input_(
            type="submit",
            name="submit",
            value="Validate",
            style="margin-top: 12pt; margin-bottom: 12pt",
        )

    return output
