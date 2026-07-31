from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import (
    CustomUserChangeForm,
    CustomUserCreationForm,
    VideoUploadForm,
)
from .models import User, Video, Categoria


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = ("email", "nombre", "nickname", "is_staff", "is_active")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("email", "nombre", "nickname")
    ordering = ("email",)
    filter_horizontal = ("groups", "user_permissions")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Información personal", {
            # "fields": ("nombre", "nickname", "first_name", "last_name")
            "fields": ("nombre", "nickname")
        }),
        ("Permisos", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
        ("Fechas importantes", {
            "fields": ("last_login", "date_joined")
        }),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "nombre",
                    "nickname",
                    "password1",
                    "password2",
                ),
            },
        ),
    )


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    form = VideoUploadForm
    list_display = (
        "mostrar_titulo",
        "mostrar_creador",
        "mostrar_categoria",
        "mostrar_formato",
        "mostrar_tamanio",
    )

    @admin.display(description="Título", ordering="titulo")
    def mostrar_titulo(self, obj):
        return obj.titulo

    @admin.display(description="Creador", ordering="creator")
    def mostrar_creador(self, obj):
        return obj.creator

    @admin.display(description="Categoría", ordering="categoria")
    def mostrar_categoria(self, obj):
        return obj.categoria

    @admin.display(description="Formato", ordering="extension")
    def mostrar_formato(self, obj):
        if not obj.extension:
            return "—"
        return obj.extension.upper()

    @admin.display(description="Tamaño", ordering="tamanio")
    def mostrar_tamanio(self, obj):
        if obj.tamanio is None:
            return "—"

        tamanio_mb = float(obj.tamanio)

        if tamanio_mb >= 1:
            valor = tamanio_mb
            unidad = "MB"
        elif tamanio_mb * 1024 >= 1:
            valor = tamanio_mb * 1024
            unidad = "KB"
        else:
            valor = tamanio_mb * 1024 * 1024
            unidad = "B"

        valor_formateado = f"{valor:.2f}".rstrip("0").rstrip(".")
        return f"{valor_formateado} {unidad}"

    def save_model(self, request, obj, form, change):
        if not obj.creator_id:
            obj.creator = request.user
        super().save_model(request, obj, form, change)


admin.site.register(Categoria)

admin.site.site_header = "Plataforma de Videos"
admin.site.site_title = "Plataforma de Videos"
admin.site.index_title = "Panel de Administración"

# Register your models here.
