from pathlib import Path
import re

from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import User, Video


ALLOWED_VIDEO_EXTENSIONS = {
    "AVI",
    "FLV",
    "MKV",
    "MOV",
    "MP4",
    "MPEG",
    "MPG",
    "WEBM",
    "WMV",
}
MAX_VIDEO_SIZE = 3 * 1024 * 1024


class CustomUserCreationForm(UserCreationForm):
    """Form used by the admin to create an email-based user."""

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email", "nombre", "nickname")

class CreatorRegistrationForm(UserCreationForm):
    """Formulario público para registrar nuevos creators."""

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email", "nombre", "nickname")
        
class CustomUserChangeForm(UserChangeForm):
    """Form used by the admin to edit an email-based user."""

    class Meta(UserChangeForm.Meta):
        model = User
        fields = "__all__"


class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ("titulo", "categoria", "archivo")
        widgets = {
            "archivo": forms.ClearableFileInput(attrs={"accept": "video/*"}),
        }

    def clean_titulo(self):
        titulo = self.cleaned_data["titulo"]
        if not re.fullmatch(r"[A-Za-z0-9\s]+", titulo):
            raise forms.ValidationError(
                "Titulo del video en formato incorrecto. "
                "Debe capturar solo numeros y letras."
            )
        return titulo

    def clean_archivo(self):
        archivo = self.cleaned_data["archivo"]
        filename = Path(archivo.name).name
        extension = Path(filename).suffix.removeprefix(".").upper()

        if extension not in ALLOWED_VIDEO_EXTENSIONS:
            raise forms.ValidationError(
                "Extension del video en formato incorrecto. Debe ser mp4, avi, "
                "mov, mkv, flv, wmv, webm, mpg o mpeg."
            )
        if archivo.size > MAX_VIDEO_SIZE:
            raise forms.ValidationError("El archivo no debe pesar mas de 3 MB.")
        if len(filename) > Video._meta.get_field("nombre").max_length:
            raise forms.ValidationError("El nombre del archivo es demasiado largo.")

        return archivo

    def save(self, commit=True):
        archivo = self.cleaned_data["archivo"]
        filename = Path(archivo.name).name

        self.instance.nombre = filename
        self.instance.extension = Path(filename).suffix.removeprefix(".").upper()
        self.instance.tamanio = round(archivo.size / (1024 * 1024), 2)

        return super().save(commit=commit)


class VideoEditForm(VideoUploadForm):
    class Meta(VideoUploadForm.Meta):
        fields = ("titulo", "archivo")
