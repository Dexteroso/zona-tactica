# Zona Táctica ⚽

Zona Táctica es una aplicación web desarrollada con **Django** para compartir, organizar y consultar videos de análisis táctico de fútbol.

Este proyecto fue desarrollado como proyecto final del **Bootcamp Full Stack Developer** y demuestra la implementación de autenticación de usuarios, autorización por roles, carga y reproducción de videos, panel de administración personalizado y despliegue en producción utilizando PostgreSQL, Gunicorn y Nginx.

---

## 🚀 Demo

**Aplicación en producción:**

https://zonatactica.dexforge.app

---

## ✨ Funcionalidades

- Registro e inicio de sesión de usuarios mediante correo electrónico.
- Gestión de usuarios con roles y permisos.
- Publicación y administración de videos.
- Organización de videos por categorías.
- Lista general de videos.
- Sección **Mis Videos** para cada creador.
- Búsqueda por título o creador.
- Edición de videos propios.
- Contador automático de reproducciones.
- Panel de administración de Django.
- Diseño responsive para computadoras, tablets y dispositivos móviles.

---

## 🛠 Tecnologías utilizadas

- Python 3
- Django 6
- PostgreSQL
- Gunicorn
- Nginx
- HTML5
- CSS3
- JavaScript
- Git
- GitHub

---

## ⚙️ Instalación local

```bash
git clone https://github.com/Dexteroso/zona-tactica.git

cd zona-tactica

python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt

python manage.py migrate

python manage.py runserver
```

La aplicación estará disponible en:

```
http://127.0.0.1:8000
```

---

## 🌐 Producción

La aplicación se encuentra desplegada en un servidor Ubuntu utilizando la siguiente arquitectura:

- Django
- PostgreSQL
- Gunicorn
- Nginx
- Let's Encrypt (HTTPS)
- Dominio personalizado

---

## 📂 Estructura del proyecto

```
mis_videos/
videos_app/
media/
manage.py
requirements.txt
README.md
```

---

## 📌 Mejoras futuras

- Generación automática de miniaturas (thumbnails) para los videos.
- Estadísticas avanzadas de visualizaciones.
- Sistema de comentarios.
- Sistema de "Me gusta".
- Filtros avanzados por categoría y creador.

---

## 👨‍💻 Autor

**Angel Solano**

Proyecto desarrollado como parte del Bootcamp **Full Stack Developer**.

