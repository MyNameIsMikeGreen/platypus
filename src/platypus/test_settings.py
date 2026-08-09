from .settings import *

MIDDLEWARE = [
    middleware
    for middleware in MIDDLEWARE
    if middleware != "whitenoise.middleware.WhiteNoiseMiddleware"
]

STORAGES = {
    **STORAGES,
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
