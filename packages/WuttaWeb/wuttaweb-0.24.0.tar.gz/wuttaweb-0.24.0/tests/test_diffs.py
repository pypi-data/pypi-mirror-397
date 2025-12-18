# -*- coding: utf-8; -*-

from wuttaweb import diffs as mod
from wuttaweb.testing import WebTestCase, VersionWebTestCase


# nb. using WebTestCase here only for mako support in render_html()
class TestDiff(WebTestCase):

    def make_diff(self, *args, **kwargs):
        return mod.Diff(*args, **kwargs)

    def test_constructor(self):
        old_data = {"foo": "bar"}
        new_data = {"foo": "baz"}
        diff = self.make_diff(old_data, new_data, fields=["foo"])
        self.assertEqual(diff.fields, ["foo"])

    def test_make_fields(self):
        old_data = {"foo": "bar"}
        new_data = {"foo": "bar", "baz": "zer"}
        # nb. this calls make_fields()
        diff = self.make_diff(old_data, new_data)
        # TODO: should the fields be cumulative? or just use new_data?
        self.assertEqual(diff.fields, ["baz", "foo"])

    def test_values(self):
        old_data = {"foo": "bar"}
        new_data = {"foo": "baz"}
        diff = self.make_diff(old_data, new_data)
        self.assertEqual(diff.old_value("foo"), "bar")
        self.assertEqual(diff.new_value("foo"), "baz")

    def test_values_differ(self):
        old_data = {"foo": "bar"}
        new_data = {"foo": "baz"}
        diff = self.make_diff(old_data, new_data)
        self.assertTrue(diff.values_differ("foo"))

        old_data = {"foo": "bar"}
        new_data = {"foo": "bar"}
        diff = self.make_diff(old_data, new_data)
        self.assertFalse(diff.values_differ("foo"))

    def test_render_values(self):
        old_data = {"foo": "bar"}
        new_data = {"foo": "baz"}
        diff = self.make_diff(old_data, new_data)
        self.assertEqual(diff.render_old_value("foo"), "'bar'")
        self.assertEqual(diff.render_new_value("foo"), "'baz'")

    def test_get_old_value_attrs(self):

        # no change
        old_data = {"foo": "bar"}
        new_data = {"foo": "bar"}
        diff = self.make_diff(old_data, new_data, nature="update")
        self.assertEqual(diff.get_old_value_attrs(False), {})

        # update
        old_data = {"foo": "bar"}
        new_data = {"foo": "baz"}
        diff = self.make_diff(old_data, new_data, nature="update")
        self.assertEqual(
            diff.get_old_value_attrs(True),
            {"style": f"background-color: {diff.old_color};"},
        )

        # delete
        old_data = {"foo": "bar"}
        new_data = {}
        diff = self.make_diff(old_data, new_data, nature="delete")
        self.assertEqual(
            diff.get_old_value_attrs(True),
            {"style": f"background-color: {diff.old_color};"},
        )

    def test_get_new_value_attrs(self):

        # no change
        old_data = {"foo": "bar"}
        new_data = {"foo": "bar"}
        diff = self.make_diff(old_data, new_data, nature="update")
        self.assertEqual(diff.get_new_value_attrs(False), {})

        # update
        old_data = {"foo": "bar"}
        new_data = {"foo": "baz"}
        diff = self.make_diff(old_data, new_data, nature="update")
        self.assertEqual(
            diff.get_new_value_attrs(True),
            {"style": f"background-color: {diff.new_color};"},
        )

        # create
        old_data = {}
        new_data = {"foo": "bar"}
        diff = self.make_diff(old_data, new_data, nature="create")
        self.assertEqual(
            diff.get_new_value_attrs(True),
            {"style": f"background-color: {diff.new_color};"},
        )

    def test_render_field_row(self):
        old_data = {"foo": "bar"}
        new_data = {"foo": "baz"}
        diff = self.make_diff(old_data, new_data)
        row = diff.render_field_row("foo")
        self.assertIn("<tr>", row)
        self.assertIn("&#39;bar&#39;", row)
        self.assertIn(f'style="background-color: {diff.old_color};"', row)
        self.assertIn("&#39;baz&#39;", row)
        self.assertIn(f'style="background-color: {diff.new_color};"', row)
        self.assertIn("</tr>", row)

    def test_render_html(self):
        old_data = {"foo": "bar"}
        new_data = {"foo": "baz"}
        diff = self.make_diff(old_data, new_data)
        html = diff.render_html()
        self.assertIn("<table", html)
        self.assertIn("<tr>", html)
        self.assertIn("&#39;bar&#39;", html)
        self.assertIn(f'style="background-color: {diff.old_color};"', html)
        self.assertIn("&#39;baz&#39;", html)
        self.assertIn(f'style="background-color: {diff.new_color};"', html)
        self.assertIn("</tr>", html)
        self.assertIn("</table>", html)


class TestVersionDiff(VersionWebTestCase):

    def make_diff(self, *args, **kwargs):
        return mod.VersionDiff(*args, **kwargs)

    def test_constructor(self):
        import sqlalchemy_continuum as continuum

        model = self.app.model
        user = model.User(username="fred")
        self.session.add(user)
        self.session.commit()
        user.username = "freddie"
        self.session.commit()
        self.session.delete(user)
        self.session.commit()

        txncls = continuum.transaction_class(model.User)
        vercls = continuum.version_class(model.User)
        versions = self.session.query(vercls).order_by(vercls.transaction_id).all()
        self.assertEqual(len(versions), 3)

        version = versions[0]
        diff = self.make_diff(version)
        self.assertEqual(diff.nature, "create")
        self.assertEqual(
            diff.fields,
            ["active", "person_uuid", "prevent_edit", "username", "uuid"],
        )

        version = versions[1]
        diff = self.make_diff(version)
        self.assertEqual(diff.nature, "update")
        self.assertEqual(
            diff.fields,
            ["active", "person_uuid", "prevent_edit", "username", "uuid"],
        )

        version = versions[2]
        diff = self.make_diff(version)
        self.assertEqual(diff.nature, "delete")
        self.assertEqual(
            diff.fields,
            ["active", "person_uuid", "prevent_edit", "username", "uuid"],
        )

    def test_render_values(self):
        import sqlalchemy_continuum as continuum

        model = self.app.model
        user = model.User(username="fred")
        self.session.add(user)
        self.session.commit()
        user.username = "freddie"
        self.session.commit()
        self.session.delete(user)
        self.session.commit()

        txncls = continuum.transaction_class(model.User)
        vercls = continuum.version_class(model.User)
        versions = self.session.query(vercls).order_by(vercls.transaction_id).all()
        self.assertEqual(len(versions), 3)

        version = versions[0]
        diff = self.make_diff(version)
        self.assertEqual(diff.nature, "create")
        self.assertEqual(diff.render_old_value("username"), "")
        self.assertEqual(
            diff.render_new_value("username"),
            '<span style="font-family: monospace;">&#39;fred&#39;</span>',
        )

        version = versions[1]
        diff = self.make_diff(version)
        self.assertEqual(diff.nature, "update")
        self.assertEqual(
            diff.render_old_value("username"),
            '<span style="font-family: monospace;">&#39;fred&#39;</span>',
        )
        self.assertEqual(
            diff.render_new_value("username"),
            '<span style="font-family: monospace;">&#39;freddie&#39;</span>',
        )

        version = versions[2]
        diff = self.make_diff(version)
        self.assertEqual(diff.nature, "delete")
        self.assertEqual(
            diff.render_old_value("username"),
            '<span style="font-family: monospace;">&#39;freddie&#39;</span>',
        )
        self.assertEqual(diff.render_new_value("username"), "")
