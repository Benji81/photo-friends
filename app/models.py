from datetime import datetime, timezone
from io import BytesIO
import os
import uuid

from PIL import Image
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

def get_utc_now() -> datetime:
    """Return the current UTC time when called."""
    return datetime.now(timezone.utc)


class Album(models.Model):
    """Class to define an uniq Album to upload photos"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(
        max_length=64,
        verbose_name=_("Album name"),
        # help_text="Album name",
    )
    creator = models.CharField(
        max_length=64,
        verbose_name=_("Creator"),
        # help_text="Your name",
    )
    created_at = models.DateTimeField(
        default=get_utc_now,
        help_text="Date in format ISO8601. Example: 2020-03-03T18:31:01.915000Z.",
    )
    enabled = models.BooleanField(verbose_name="Album enabled", default=True)

    def __str__(self):
        return self.name


def get_upload_path(instance, filename):
    """generate a path for photo which contains the album UID"""
    return os.path.join("photos", str(instance.album.id), filename)

def get_thumbnail_path(instance, filename):
    """generate a path for thumbnail which contains the album UID"""
    return os.path.join("thumbnails", str(instance.album.id), filename)


class Upload(models.Model):
    """Model for uploaded file for non-logged used"""

    album = models.ForeignKey(
        Album,
        on_delete=models.PROTECT,
        help_text="Related Album",
    )
    photo = models.ImageField(
        verbose_name="Image to upload",
        help_text="Select one or more images to upload",
        upload_to=get_upload_path,
    )
    thumbnail = models.ImageField(
        editable=False,
        upload_to=get_thumbnail_path,
    )

    created_at = models.DateTimeField(
        blank=True,
        null=True,
        db_index=True,
        help_text="Date in format ISO8601. Example: 2020-03-03T18:31:01.915000Z.",
    )

    uploaded_at = models.DateTimeField(
        default=get_utc_now,
        help_text="Date in format ISO8601. Example: 2020-03-03T18:31:01.915000Z.",
    )

    uploader = models.CharField(
        max_length=64,
        verbose_name=_("Name"),
    )

    def save(self, *args, **kwargs):

        if not self.make_thumbnail():
            # set to a default thumbnail
            raise Exception("Could not create thumbnail - is the file type valid?")

        super().save(*args, **kwargs)

    def make_thumbnail(self):
        """At save time, create a thumbnail of a photo"""

        thumb_name, thumb_extension = os.path.splitext(self.photo.name)
        thumb_extension = thumb_extension.lower()

        thumb_filename = thumb_name + "_thumb" + thumb_extension

        if thumb_extension in [".jpg", ".jpeg"]:
            file_type = "JPEG"
        elif thumb_extension == ".gif":
            file_type = "GIF"
        elif thumb_extension == ".png":
            file_type = "PNG"
        elif thumb_extension in {".avi", ".mp4", ".mov"}:
            return True  # need to generate special thumbnail for movie
        else:
            return False  # Unrecognized file type

        # Save thumbnail to in-memory file as StringIO
        temp_thumb = BytesIO()
        image = Image.open(self.photo)
        image.thumbnail(settings.THUMB_SIZE, Image.ANTIALIAS)
        image.save(temp_thumb, file_type)
        temp_thumb.seek(0)

        # set save=False, otherwise it will run in an infinite loop
        self.thumbnail.save(thumb_filename, ContentFile(temp_thumb.read()), save=False)
        temp_thumb.close()

        return True


@receiver(models.signals.post_delete, sender=Upload)
# pylint: disable=unused-argument
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.photo:
        if os.path.isfile(instance.photo.path):
            os.remove(instance.photo.path)
    if instance.thumb:
        if os.path.isfile(instance.thumb.path):
            os.remove(instance.thumb.path)
