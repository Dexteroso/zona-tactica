from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings
# from django.contrib.auth.admin import UserAdmin

class UserManager(BaseUserManager):
    def create_user(self, email, nombre, nickname, password=None, **extra_fields):
        if not email:
            raise ValueError("El email es obligatorio")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            nombre=nombre,
            nickname=nickname,
            **extra_fields,
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(
        self,
        email,
        nombre,
        nickname,
        password=None,
        **extra_fields
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(
            email=email,
            nombre=nombre,
            nickname=nickname,
            password=password,
            **extra_fields,
        )

class User(AbstractUser):
    username = None

    email = models.EmailField(unique=True)
    nombre = models.CharField(max_length=100)
    nickname = models.CharField(max_length=50, unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nombre", "nickname"]
    
    objects = UserManager()

    def __str__(self):
        return self.nickname
    
    
# class Usuario(models.Model):
#     id = models.CharField(max_length=10, primary_key=True)
#     nombre = models.CharField(max_length=50)

#     def __str__(self):
#         return self.nombre

class Categoria(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre
    
class Video(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True,blank=True)
    titulo = models.CharField(max_length=100)
    nombre = models.CharField(max_length=100)
    archivo = models.FileField(upload_to='videos/%Y/%m/%d/')
    extension = models.CharField(max_length=5)
    tamanio = models.FloatField()  # en MB
    vistas = models.PositiveIntegerField(default=0)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
    )

    def __str__(self):
        return self.titulo

    class Meta:
        ordering = ["-fecha_subida"]
