"""Test settings."""

from .base import *  # noqa: F403
from .base import TEMPLATES
from .base import env

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="kIY5cVhdvSGTzb032W4r69zDdZKIDtYAcNQCNM53qaCdJXfThfDSHyyenvX1T7EQ",
)
# https://docs.djangoproject.com/en/dev/ref/settings/#test-runner
TEST_RUNNER = "django.test.runner.DiscoverRunner"

# PASSWORDS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#password-hashers
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# DEBUGGING FOR TEMPLATES
# ------------------------------------------------------------------------------
TEMPLATES[0]["OPTIONS"]["debug"] = True  # type: ignore[index]

# MEDIA
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = "http://media.testserver/"
# DATABASE
# ------------------------------------------------------------------------------
# Use DATABASE_URL if provided (for CI), otherwise fall back to PostgreSQL config
if env("DATABASE_URL", default=None):
    DATABASES = {"default": env.db("DATABASE_URL")}
    DATABASES["default"]["ATOMIC_REQUESTS"] = True
else:
    # Use PostgreSQL for tests when running locally
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "test_nodefinder",
            "USER": env("POSTGRES_USER", default="postgres"),
            "PASSWORD": env("POSTGRES_PASSWORD", default="postgres"),
            "HOST": env("POSTGRES_HOST", default="postgres"),
            "PORT": env("POSTGRES_PORT", default="5432"),
            "ATOMIC_REQUESTS": True,
        },
    }

# Your stuff...
# ------------------------------------------------------------------------------
