from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from . import views

urlpatterns = [
    path("", views.lista_videos, name="index"),
    path("mis-videos/", views.mis_videos, name="mis_videos"),
    path("upload/", views.upload_video, name="upload_video"),
    path("upload/success/", views.upload_success, name="upload_success"),
    path("register/", views.register, name="register"),
    path(
        "video/<uuid:video_id>/vista/",
        views.registrar_vista_video,
        name="registrar_vista_video",
    ),
    path(
        "video/<uuid:video_id>/editar/",
        views.editar_video,
        name="editar_video",
    ),
    path("video/<uuid:video_id>/eliminar/", views.eliminar_video, name="eliminar_video"),

    path(
        "login/",
        LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
]
