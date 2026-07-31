import shutil
import tempfile
from datetime import timedelta
from unittest.mock import patch

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .admin import CustomUserAdmin, VideoAdmin
from .forms import (
    CustomUserChangeForm,
    CustomUserCreationForm,
    VideoUploadForm,
)
from .models import Categoria, Video
from .templatetags.custom_filters import antiguedad


class RelativeTimeFilterTests(SimpleTestCase):
    def test_uses_only_the_largest_time_unit(self):
        ahora = timezone.now()
        cases = (
            (timedelta(minutes=18), "hace 18 minutos"),
            (timedelta(hours=1, minutes=5), "hace 1 hora"),
            (timedelta(hours=11, minutes=13), "hace 11 horas"),
            (timedelta(hours=23, minutes=59), "hace 23 horas"),
            (timedelta(days=1, hours=2), "hace 1 día"),
            (timedelta(days=5, hours=8), "hace 5 días"),
        )

        with patch(
            "videos_app.templatetags.custom_filters.timezone.now",
            return_value=ahora,
        ):
            for elapsed, expected in cases:
                with self.subTest(elapsed=elapsed):
                    self.assertEqual(antiguedad(ahora - elapsed), expected)


class CustomUserAdminTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.superuser = self.user_model.objects.create_superuser(
            email="admin@example.com",
            nombre="Admin",
            nickname="admin",
            password="a-secure-test-password",
        )
        self.client.force_login(self.superuser)

    def test_custom_user_admin_is_registered_with_custom_forms(self):
        model_admin = admin.site._registry[self.user_model]

        self.assertIsInstance(model_admin, CustomUserAdmin)
        self.assertIs(model_admin.form, CustomUserChangeForm)
        self.assertIs(model_admin.add_form, CustomUserCreationForm)
        self.assertNotIn("username", model_admin.search_fields)
        self.assertNotIn("username", model_admin.list_display)

    def test_admin_user_add_page_does_not_expect_username(self):
        response = self.client.get(
            reverse(
                "admin:%s_%s_add"
                % (self.user_model._meta.app_label, self.user_model._meta.model_name)
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'name="username"')
        self.assertContains(response, 'name="email"')
        self.assertContains(response, 'name="password1"')
        self.assertContains(response, 'name="password2"')

    def test_creation_form_hashes_password(self):
        form = CustomUserCreationForm(
            data={
                "email": "person@example.com",
                "nombre": "Person",
                "nickname": "person",
                "password1": "another-secure-test-password",
                "password2": "another-secure-test-password",
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertTrue(user.check_password("another-secure-test-password"))


class VideoUploadTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.media_root = tempfile.mkdtemp()
        cls.override_media = override_settings(MEDIA_ROOT=cls.media_root)
        cls.override_media.enable()

    @classmethod
    def tearDownClass(cls):
        cls.override_media.disable()
        shutil.rmtree(cls.media_root)
        super().tearDownClass()

    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            email="uploader@example.com",
            nombre="Uploader",
            nickname="uploader",
            password="a-secure-test-password",
        )
        self.other_user = user_model.objects.create_user(
            email="other@example.com",
            nombre="Other",
            nickname="other",
            password="a-secure-test-password",
        )
        self.category = Categoria.objects.create(nombre="Tutorial")
        self.client.force_login(self.user)

    def test_form_only_exposes_requested_fields(self):
        self.assertEqual(
            list(VideoUploadForm().fields),
            ["titulo", "categoria", "archivo"],
        )
        video_admin = admin.site._registry[Video]
        self.assertIsInstance(video_admin, VideoAdmin)
        self.assertIs(video_admin.form, VideoUploadForm)

    def test_upload_requires_authentication(self):
        self.client.logout()

        response = self.client.get(reverse("upload_video"))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('upload_video')}",
        )

    def test_upload_assigns_creator_and_file_metadata(self):
        upload = SimpleUploadedFile(
            "My.Video.mP4",
            b"video content",
            content_type="video/mp4",
        )

        response = self.client.post(
            reverse("upload_video"),
            {
                "titulo": "Video 1",
                "categoria": self.category.pk,
                "archivo": upload,
                "creator": self.other_user.pk,
                "nombre": "spoofed.mov",
                "extension": "MOV",
                "tamanio": 999,
            },
        )

        self.assertRedirects(response, reverse("upload_success"))
        video = Video.objects.get()
        self.assertEqual(video.creator, self.user)
        self.assertEqual(video.nombre, "My.Video.mP4")
        self.assertEqual(video.extension, "MP4")
        self.assertEqual(video.tamanio, 0.0)
        self.assertEqual(video.categoria, self.category)

    def test_empty_post_shows_required_errors_and_creates_no_video(self):
        response = self.client.post(reverse("upload_video"), {})

        self.assertEqual(response.status_code, 200)
        errors = response.context["form"].errors.as_data()
        self.assertEqual(errors["titulo"][0].code, "required")
        self.assertEqual(errors["categoria"][0].code, "required")
        self.assertEqual(errors["archivo"][0].code, "required")
        self.assertEqual(Video.objects.count(), 0)

    def test_missing_title_creates_no_video(self):
        response = self.client.post(
            reverse("upload_video"),
            {
                "categoria": self.category.pk,
                "archivo": SimpleUploadedFile(
                    "video.mp4",
                    b"video content",
                    content_type="video/mp4",
                ),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["form"].errors.as_data()["titulo"][0].code,
            "required",
        )
        self.assertEqual(Video.objects.count(), 0)

    def test_missing_file_creates_no_video(self):
        response = self.client.post(
            reverse("upload_video"),
            {
                "titulo": "Video without file",
                "categoria": self.category.pk,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["form"].errors.as_data()["archivo"][0].code,
            "required",
        )
        self.assertEqual(Video.objects.count(), 0)

    def test_missing_category_creates_no_video(self):
        response = self.client.post(
            reverse("upload_video"),
            {
                "titulo": "Video without category",
                "archivo": SimpleUploadedFile(
                    "video.mp4",
                    b"video content",
                    content_type="video/mp4",
                ),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["form"].errors.as_data()["categoria"][0].code,
            "required",
        )
        self.assertEqual(Video.objects.count(), 0)

    def test_existing_title_extension_and_size_validations_are_preserved(self):
        invalid_title = VideoUploadForm(
            data={"titulo": "Invalid!", "categoria": self.category.pk},
            files={
                "archivo": SimpleUploadedFile("video.mp4", b"x"),
            },
        )
        invalid_extension = VideoUploadForm(
            data={"titulo": "Valid title", "categoria": self.category.pk},
            files={
                "archivo": SimpleUploadedFile("video.txt", b"x"),
            },
        )
        oversized = VideoUploadForm(
            data={"titulo": "Valid title", "categoria": self.category.pk},
            files={
                "archivo": SimpleUploadedFile(
                    "video.mp4",
                    b"x" * (3 * 1024 * 1024 + 1),
                ),
            },
        )

        self.assertIn("titulo", invalid_title.errors)
        self.assertIn("archivo", invalid_extension.errors)
        self.assertIn("archivo", oversized.errors)

    def test_my_videos_requires_authentication(self):
        self.client.logout()

        response = self.client.get(reverse("mis_videos"))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('mis_videos')}",
        )

    def test_my_videos_only_lists_authenticated_users_videos(self):
        own_video = Video.objects.create(
            creator=self.user,
            titulo="Own video",
            nombre="own.mp4",
            archivo="videos/own.mp4",
            extension="MP4",
            tamanio=1.0,
            categoria=self.category,
        )
        Video.objects.create(
            creator=self.other_user,
            titulo="Other video",
            nombre="other.mp4",
            archivo="videos/other.mp4",
            extension="MP4",
            tamanio=1.0,
            categoria=self.category,
        )

        response = self.client.get(reverse("mis_videos"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["mis_videos"])
        self.assertEqual(list(response.context["videos"]), [own_video])
        self.assertContains(
            response,
            reverse("editar_video", args=[own_video.id]),
        )

    def test_public_library_does_not_show_edit_button(self):
        video = Video.objects.create(
            creator=self.user,
            titulo="Public video",
            nombre="public.mp4",
            archivo="videos/public.mp4",
            extension="MP4",
            tamanio=1.0,
            categoria=self.category,
        )

        response = self.client.get(reverse("index"))

        self.assertFalse(response.context["mis_videos"])
        self.assertNotContains(
            response,
            reverse("editar_video", args=[video.id]),
        )

    def test_edit_video_only_exposes_title_and_file(self):
        video = Video.objects.create(
            creator=self.user,
            titulo="Editable video",
            nombre="editable.mp4",
            archivo=SimpleUploadedFile(
                "editable.mp4",
                b"original video",
                content_type="video/mp4",
            ),
            extension="MP4",
            tamanio=1.0,
            categoria=self.category,
        )

        response = self.client.get(reverse("editar_video", args=[video.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["form"].fields),
            ["titulo", "archivo"],
        )

    def test_owner_can_edit_video_title_and_file(self):
        video = Video.objects.create(
            creator=self.user,
            titulo="Old title",
            nombre="old.mp4",
            archivo=SimpleUploadedFile(
                "old.mp4",
                b"old video",
                content_type="video/mp4",
            ),
            extension="MP4",
            tamanio=1.0,
            categoria=self.category,
        )

        response = self.client.post(
            reverse("editar_video", args=[video.id]),
            {
                "titulo": "New title",
                "archivo": SimpleUploadedFile(
                    "new.mov",
                    b"new video",
                    content_type="video/quicktime",
                ),
            },
        )

        video.refresh_from_db()
        self.assertRedirects(response, reverse("mis_videos"))
        self.assertEqual(video.titulo, "New title")
        self.assertEqual(video.creator, self.user)
        self.assertEqual(video.categoria, self.category)
        self.assertEqual(video.nombre, "new.mov")
        self.assertEqual(video.extension, "MOV")

    def test_user_cannot_edit_another_users_video(self):
        video = Video.objects.create(
            creator=self.other_user,
            titulo="Protected video",
            nombre="protected.mp4",
            archivo="videos/protected.mp4",
            extension="MP4",
            tamanio=1.0,
            categoria=self.category,
        )

        get_response = self.client.get(reverse("editar_video", args=[video.id]))
        post_response = self.client.post(
            reverse("editar_video", args=[video.id]),
            {"titulo": "Unauthorized title"},
        )

        video.refresh_from_db()
        self.assertEqual(get_response.status_code, 404)
        self.assertEqual(post_response.status_code, 404)
        self.assertEqual(video.titulo, "Protected video")

    def test_video_view_counter_increments_with_post(self):
        video = Video.objects.create(
            creator=self.user,
            titulo="Viewed video",
            nombre="viewed.mp4",
            archivo="videos/viewed.mp4",
            extension="MP4",
            tamanio=1.0,
            categoria=self.category,
        )

        first_response = self.client.post(
            reverse("registrar_vista_video", args=[video.id])
        )
        second_response = self.client.post(
            reverse("registrar_vista_video", args=[video.id])
        )

        video.refresh_from_db()
        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(first_response.json(), {"vistas": 1})
        self.assertEqual(second_response.json(), {"vistas": 2})
        self.assertEqual(video.vistas, 2)

    def test_video_view_counter_rejects_get(self):
        video = Video.objects.create(
            creator=self.user,
            titulo="Unviewed video",
            nombre="unviewed.mp4",
            archivo="videos/unviewed.mp4",
            extension="MP4",
            tamanio=1.0,
            categoria=self.category,
        )

        response = self.client.get(
            reverse("registrar_vista_video", args=[video.id])
        )

        video.refresh_from_db()
        self.assertEqual(response.status_code, 405)
        self.assertEqual(video.vistas, 0)
