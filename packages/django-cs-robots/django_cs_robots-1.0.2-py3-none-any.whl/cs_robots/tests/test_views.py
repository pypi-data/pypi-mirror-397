from unittest import mock

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.http import Http404
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import Client
from cs_robots.forms import RobotsTxtForm
from cs_robots.views import edit_robots_txt, serve_robots_txt

User = get_user_model()


@override_settings(ROBOTS_TXT_PATH="/tmp/test_robots.txt")
class EditRobotsTxtViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.staff_user = User.objects.create_user(
            username="staffuser",
            email="staff@example.com",
            password="password",
            is_staff=True,
        )
        self.normal_user = User.objects.create_user(
            username="normaluser", email="normal@example.com", password="password"
        )
        self.edit_url = reverse("edit_robots_txt")

        self.client = Client()

    def _get_request_with_user(self, user, method="GET", data=None):
        if method == "POST":
            request = self.factory.post(self.edit_url, data=data)
        else:
            request = self.factory.get(self.edit_url)
        request.user = user
        middleware = SessionMiddleware(lambda r: None)
        middleware.process_request(request)
        request.session.save()
        # Attach messages storage to the request
        setattr(request, "_messages", FallbackStorage(request))
        return request

    # @mock.patch("builtins.open", new_callable=mock.mock_open)
    # def test_get_request_file_not_found(self, mock_open):
    #     mock_open.reset_mock()
    #     mock_open.side_effect = FileNotFoundError
    #     request = self._get_request_with_user(self.staff_user)
    #     response = edit_robots_txt(request)

    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn(
    #         b"El fichero robots.txt no exist", response.content
    #     )  # Check for warning message
    #     # self.assertIsInstance(response.context["form"], RobotsTxtForm)
    #     # self.assertEqual(response.context["form"].initial["content"], "")
    #     mock_open.assert_any_call(settings.ROBOTS_TXT_PATH, "r", encoding="utf-8")
    #     self.assertIn(
    #         "El fichero robots.txt no existía y será creado.",
    #         [m.message for m in messages.get_messages(request)],
    #     )

    # @mock.patch("builtins.open", new_callable=mock.mock_open)
    # def test_get_request_file_read_error(self, mock_open):
    #     mock_open.reset_mock()
    #     mock_open.side_effect = IOError("Permission denied")
    #     request = self._get_request_with_user(self.staff_user)
    #     response = edit_robots_txt(request)

    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn(
    #         b"Error al leer el fichero", response.content
    #     )  # Check for error message
    #     # self.assertIsInstance(response.context["form"], RobotsTxtForm)
    #     # self.assertEqual(response.context["form"].initial["content"], "")
    #     mock_open.assert_any_call(settings.ROBOTS_TXT_PATH, "r", encoding="utf-8")
    #     self.assertIn(
    #         "Error al leer el fichero: Permission denied",
    #         [m.message for m in messages.get_messages(request)],
    #     )

    # @mock.patch("builtins.open", new_callable=mock.mock_open)
    # def test_get_request_file_exists(self, mock_open):
    #     mock_open.return_value.read.return_value = "User-agent: *\nDisallow: /admin/"
    #     request = self._get_request_with_user(self.staff_user)
    #     response = edit_robots_txt(request)

    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn(b"User-agent: *", response.content)
    #     # self.assertIsInstance(response.context["form"], RobotsTxtForm)
    #     # self.assertEqual(
    #     #     response.context["form"].initial["content"],
    #     #     "User-agent: *\nDisallow: /admin/",
    #     # )
    #     mock_open.assert_any_call(settings.ROBOTS_TXT_PATH, "r", encoding="utf-8")
    #     self.assertFalse(list(messages.get_messages(request)))  # No messages expected

    @mock.patch("builtins.open", new_callable=mock.mock_open)
    def test_post_request_valid_form_success(self, mock_open):
        new_content = "User-agent: Googlebot\nDisallow: /private/"
        self.client.force_login(self.staff_user)
        response = self.client.post(self.edit_url, data={"content": new_content})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.edit_url)
        mock_open.assert_any_call(settings.ROBOTS_TXT_PATH, "w", encoding="utf-8")
        mock_open.return_value.write.assert_called_once_with(new_content)

    # @mock.patch("builtins.open", new_callable=mock.mock_open)
    # def test_post_request_valid_form_write_error(self, mock_open):
    #     mock_open.return_value.__enter__.return_value.write.side_effect = IOError(
    #         "Disk full"
    #     )
    #     new_content = "User-agent: Googlebot\nDisallow: /private/"
    #     request = self._get_request_with_user(
    #         self.staff_user, method="POST", data={"content": new_content}
    #     )
    #     response = edit_robots_txt(request)

    #     self.assertEqual(response.status_code, 200)  # Form re-rendered with error
    #     self.assertIn(b"Error al guardar el fichero", response.content)
    #     mock_open.assert_any_call(settings.ROBOTS_TXT_PATH, "w", encoding="utf-8")
    #     mock_open.return_value.write.assert_called_once_with(new_content)
    #     self.assertIn(
    #         "Error al guardar el fichero: Disk full",
    #         [m.message for m in messages.get_messages(request)],
    #     )

    def test_post_request_invalid_form(self):
        # Assuming RobotsTxtForm requires content, an empty string would be invalid
        self.client.force_login(self.staff_user)
        response = self.client.post(self.edit_url, data={"content": ""})

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b"The robots.txt file did not exist and will be created.",
            response.content,
        )

    def test_non_staff_user_access(self):
        self.client.force_login(self.normal_user)
        response = self.client.get(self.edit_url)

        # staff_member_required redirects to login for non-staff users
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("admin:login"), response.url)


@override_settings(ROBOTS_TXT_PATH="/tmp/test_robots.txt")
class ServeRobotsTxtViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.serve_url = reverse("robots_txt")

    def test_robots_txt_path_not_defined(self):
        # Temporarily remove ROBOTS_TXT_PATH from settings
        with self.assertRaises(ImproperlyConfigured) as cm:
            with override_settings(ROBOTS_TXT_PATH="/tmp/test_robots.txt_to_delete"):
                delattr(settings, "ROBOTS_TXT_PATH")

                request = self.factory.get(self.serve_url)
                serve_robots_txt(request)

        self.assertIn("ROBOTS_TXT_PATH is not defined", str(cm.exception))

    @mock.patch("builtins.open", new_callable=mock.mock_open)
    def test_serve_robots_txt_file_exists(self, mock_open):
        mock_content = "User-agent: *\nDisallow: /"
        mock_open.return_value.read.return_value = mock_content

        request = self.factory.get(self.serve_url)
        response = serve_robots_txt(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/plain")
        self.assertEqual(response.content.decode("utf-8"), mock_content)
        mock_open.assert_any_call(settings.ROBOTS_TXT_PATH, "r", encoding="utf-8")

    @mock.patch("builtins.open", new_callable=mock.mock_open)
    def test_serve_robots_txt_file_not_found(self, mock_open):
        mock_open.side_effect = FileNotFoundError

        request = self.factory.get(self.serve_url)
        with self.assertRaises(Http404) as cm:
            serve_robots_txt(request)

        self.assertIn("robots.txt not found.", str(cm.exception))
        mock_open.assert_any_call(settings.ROBOTS_TXT_PATH, "r", encoding="utf-8")

    @mock.patch("builtins.open", new_callable=mock.mock_open)
    def test_serve_robots_txt_file_read_error(self, mock_open):
        # Test that other exceptions during file read are not caught by Http404
        # but propagate as regular exceptions.
        mock_open.side_effect = IOError("Disk error")

        request = self.factory.get(self.serve_url)
        with self.assertRaises(IOError) as cm:
            serve_robots_txt(request)

        self.assertIn("Disk error", str(cm.exception))
        mock_open.assert_any_call(settings.ROBOTS_TXT_PATH, "r", encoding="utf-8")
