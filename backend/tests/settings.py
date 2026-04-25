"""BookStudio 테스트용 Django 설정."""

import os
import sys

SECRET_KEY = "test-secret-key-for-bookstudio"
DEBUG = True

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "rest_framework",
    "bookstudio",
]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "tests.middleware.AutoLoginMiddleware",
]

ALLOWED_HOSTS = ["*"]

_running_tests = "pytest" in sys.modules or "py.test" in sys.argv[0:1]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:" if _running_tests else os.path.join(
            os.path.dirname(__file__), "dev.sqlite3",
        ),
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
USE_TZ = True

ROOT_URLCONF = "tests.urls"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "tests.middleware.NoCsrfSessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}
