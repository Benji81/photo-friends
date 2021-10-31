# pylint: disable=missing-module-docstring
from django.contrib import admin

from app.models import Album, Upload


admin.site.register(Upload)
admin.site.register(Album)
