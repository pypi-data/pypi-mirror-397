from django.test import TestCase
from django import forms
from cs_robots.forms import RobotsTxtForm


class RobotsTxtFormTest(TestCase):

    def test_form_valid_data(self):
        """
        Test that the form is valid with typical robots.txt content.
        """
        form_data = {"content": "User-agent: *\nDisallow: /admin/\nAllow: /"}
        form = RobotsTxtForm(data=form_data)
        self.assertTrue(
            form.is_valid(), f"Form should be valid, but got errors: {form.errors}"
        )

    def test_form_empty_content(self):
        """
        Test that the form is valid even with empty content, as an empty robots.txt is valid.
        """
        form_data = {"content": ""}
        form = RobotsTxtForm(data=form_data)
        self.assertFalse(
            form.is_valid(),
            "Form shouldn't be empty",
        )

    def test_form_widget_attributes(self):
        """
        Test that the 'content' field uses a Textarea widget with correct attributes.
        """
        form = RobotsTxtForm()
        self.assertIsInstance(form.fields["content"].widget, forms.Textarea)
        self.assertEqual(form.fields["content"].widget.attrs["rows"], 20)
        self.assertEqual(form.fields["content"].widget.attrs["cols"], 80)

    def test_form_field_labels_and_help_text(self):
        """
        Test that the 'content' field has the correct label and help text.
        """
        form = RobotsTxtForm()
        self.assertEqual(
            form.fields["content"].label, "Contenido del fichero robots.txt"
        )
        self.assertEqual(
            form.fields["content"].help_text,
            "Guarda los cambios para sobreescribir el fichero físico.",
        )
