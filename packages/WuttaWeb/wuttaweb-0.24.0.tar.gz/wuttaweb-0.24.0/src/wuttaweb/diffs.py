# -*- coding: utf-8; -*-
################################################################################
#
#  wuttaweb -- Web App for Wutta Framework
#  Copyright © 2024-2025 Lance Edgar
#
#  This file is part of Wutta Framework.
#
#  Wutta Framework is free software: you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option) any
#  later version.
#
#  Wutta Framework is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
#  more details.
#
#  You should have received a copy of the GNU General Public License along with
#  Wutta Framework.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Tools for displaying simple data diffs
"""

import sqlalchemy as sa

from pyramid.renderers import render
from webhelpers2.html import HTML


class Diff:
    """
    Represent / display a basic "diff" between two data records.

    You must provide both the "old" and "new" data records, when
    constructing an instance of this class.  Then call
    :meth:`render_html()` to display the diff table.

    :param old_data: Dict of "old" data record.

    :param new_data: Dict of "new" data record.

    :param fields: Optional list of field names.  If not specified,
       will be derived from the data records.

    :param nature: What sort of diff is being represented; must be one
       of: ``("create", "update", "delete")``

    :param old_color: Background color to display for "old/deleted"
       field data, when applicable.

    :param new_color: Background color to display for "new/created"
       field data, when applicable.
    """

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        old_data: dict,
        new_data: dict,
        fields: list = None,
        nature="update",
        old_color="#ffebe9",
        new_color="#dafbe1",
    ):
        self.old_data = old_data
        self.new_data = new_data
        self.columns = ["field name", "old value", "new value"]
        self.fields = fields or self.make_fields()
        self.nature = nature
        self.old_color = old_color
        self.new_color = new_color

    def make_fields(self):  # pylint: disable=missing-function-docstring
        return sorted(set(self.old_data) | set(self.new_data), key=lambda x: x.lower())

    def old_value(self, field):  # pylint: disable=missing-function-docstring
        return self.old_data.get(field)

    def new_value(self, field):  # pylint: disable=missing-function-docstring
        return self.new_data.get(field)

    def values_differ(self, field):  # pylint: disable=missing-function-docstring
        return self.new_value(field) != self.old_value(field)

    def render_html(self, template="/diff.mako", **kwargs):
        """
        Render the diff as HTML table.

        :param template: Name of template to render, if you need to
           override the default.

        :param \\**kwargs: Remaining kwargs are passed as context to
           the template renderer.

        :returns: HTML literal string
        """
        context = kwargs
        context["diff"] = self
        return HTML.literal(render(template, context))

    def render_field_row(self, field):  # pylint: disable=missing-function-docstring
        is_diff = self.values_differ(field)

        td_field = HTML.tag("td", class_="field", c=field)

        td_old_value = HTML.tag(
            "td",
            c=self.render_old_value(field),
            **self.get_old_value_attrs(is_diff),
        )

        td_new_value = HTML.tag(
            "td",
            c=self.render_new_value(field),
            **self.get_new_value_attrs(is_diff),
        )

        return HTML.tag("tr", c=[td_field, td_old_value, td_new_value])

    def render_old_value(self, field):  # pylint: disable=missing-function-docstring
        value = self.old_value(field)
        return repr(value)

    def render_new_value(self, field):  # pylint: disable=missing-function-docstring
        value = self.new_value(field)
        return repr(value)

    def get_old_value_attrs(  # pylint: disable=missing-function-docstring
        self, is_diff
    ):
        attrs = {}
        if self.nature == "update" and is_diff:
            attrs["style"] = f"background-color: {self.old_color};"
        elif self.nature == "delete":
            attrs["style"] = f"background-color: {self.old_color};"
        return attrs

    def get_new_value_attrs(  # pylint: disable=missing-function-docstring
        self, is_diff
    ):
        attrs = {}
        if self.nature == "create":
            attrs["style"] = f"background-color: {self.new_color};"
        elif self.nature == "update" and is_diff:
            attrs["style"] = f"background-color: {self.new_color};"
        return attrs


class VersionDiff(Diff):
    """
    Special diff class, for use with version history views.  Note that
    while based on :class:`Diff`, this class uses a different
    signature for the constructor.

    :param version: Reference to a Continuum version record (object).

    :param \\**kwargs: Remaining kwargs are passed as-is to the
       :class:`Diff` constructor.
    """

    def __init__(self, version, **kwargs):
        import sqlalchemy_continuum as continuum  # pylint: disable=import-outside-toplevel
        from wutta_continuum.util import (  # pylint: disable=import-outside-toplevel
            render_operation_type,
        )

        self.version = version
        self.model_class = continuum.parent_class(type(self.version))
        self.mapper = sa.inspect(self.model_class)
        self.version_mapper = sa.inspect(type(self.version))
        self.title = kwargs.pop("title", self.model_class.__name__)

        self.operation_title = render_operation_type(self.version.operation_type)

        if "nature" not in kwargs:
            if (
                version.previous
                and version.operation_type == continuum.Operation.DELETE
            ):
                kwargs["nature"] = "delete"
            elif version.previous:
                kwargs["nature"] = "update"
            else:
                kwargs["nature"] = "create"

        if "fields" not in kwargs:
            kwargs["fields"] = self.get_default_fields()

        old_data = {}
        new_data = {}
        for field in kwargs["fields"]:
            if version.previous:
                old_data[field] = getattr(version.previous, field)
            new_data[field] = getattr(version, field)

        super().__init__(old_data, new_data, **kwargs)

    def get_default_fields(self):  # pylint: disable=missing-function-docstring
        fields = sorted(self.version_mapper.columns.keys())

        unwanted = [
            "transaction_id",
            "end_transaction_id",
            "operation_type",
        ]

        return [field for field in fields if field not in unwanted]

    def render_version_value(self, value):  # pylint: disable=missing-function-docstring
        return HTML.tag("span", c=[repr(value)], style="font-family: monospace;")

    def render_old_value(self, field):
        if self.nature == "create":
            return ""
        value = self.old_value(field)
        return self.render_version_value(value)

    def render_new_value(self, field):
        if self.nature == "delete":
            return ""
        value = self.new_value(field)
        return self.render_version_value(value)
