# pylint: disable=missing-module-docstring
from django.contrib import admin

from app.models import Album, Upload


class AlbumAdmin(admin.ModelAdmin):
    """Better admin page for Albums"""

    list_display = ["name", "creator", "created_at", "id"]


class UploadAdmin(admin.ModelAdmin):
    """Better admin page for Uploads"""

    list_display = ["album", "uploaded_at", "created_at", "uploader"]
    list_filter = ["album", "uploaded_at", "created_at", "uploader"]


admin.site.register(Upload, UploadAdmin)
admin.site.register(Album, AlbumAdmin)
