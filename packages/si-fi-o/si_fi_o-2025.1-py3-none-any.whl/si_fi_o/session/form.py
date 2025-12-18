"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import typing as h

import flask as flsk
import wtforms as wtfm
from flask_wtf import FlaskForm as flask_form_t
from si_fi_o.path.server import file_t

validators_t = wtfm.validators


class form_t(flask_form_t):
    submit = wtfm.SubmitField(label="Launch Processing")

    @property
    def fields_to_labels(self) -> dict[str, str]:
        """"""
        output = {}

        for name in self.__dict__:
            attribute = getattr(self, name)
            if _ElementIsInputField(attribute):  # Not all elements are fields
                # Fields might not have a label (at least it does not cost much to check)
                if hasattr(attribute, "label"):
                    output[name] = attribute.label.text
                else:
                    output[name] = name

        return output

    @property
    def file_fields(self) -> tuple[str, ...]:
        """"""
        output = []

        for name in self.__dict__:
            if isinstance(getattr(self, name), wtfm.FileField):
                output.append(name)

        return tuple(output)

    def Data(self) -> dict[str, h.Any]:
        """"""
        output = {}

        for name in self.__dict__:
            attribute = getattr(self, name)

            if _ElementIsInputField(attribute):
                data = attribute.data
                if isinstance(attribute, wtfm.FileField):
                    if data.filename == "":
                        output[name] = None  # Only place where output value can be None
                    else:
                        output[name] = data
                else:
                    output[name] = data

        return output

    def Update(self, session: dict[str, h.Any], /) -> None:
        """"""
        for field, value in session.items():
            if not isinstance(value, file_t):
                getattr(self, field).process_formdata((value,))


def InputFileContents() -> bytes:
    """"""
    client_file = tuple(flsk.request.files.values())[0]

    return client_file.read()


def _ElementIsInputField(element: h.Any, /) -> bool:
    """"""
    return isinstance(element, wtfm.Field) and not isinstance(
        element, (wtfm.HiddenField, wtfm.SubmitField)
    )
