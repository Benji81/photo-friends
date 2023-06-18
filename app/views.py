from collections import defaultdict
import datetime
import os
from os.path import basename
import zipfile

from django.conf import settings
from django.db.models import Count
from django.http import FileResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import CreateView, DetailView, FormView

import PIL
from PIL import Image

from app.forms import UploadFileForm
from app.models import Album, Upload


class AlbumCreateView(CreateView):
    """View to create an album a auto generate an UUID"""

    model = Album
    fields = ["name", "creator"]

    def form_valid(self, form):
        album = form.save(commit=False)
        album.created_by = self.request.user
        album.save()
        return HttpResponseRedirect(reverse("album", kwargs={"id": album.id}))


class AlbumDetailView(DetailView, FormView):
    """View to get an album information and actions on it"""

    model = Album
    pk_url_kwarg = "id"
    queryset = Album.objects.all()
    form_class = UploadFileForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        album = Album.objects.get(id=self.kwargs[self.pk_url_kwarg])
        uploads = Upload.objects.filter(album=album).order_by("created_at")
        # context["uploads"] = uploads
        uploads_by_date = defaultdict(list)
        for upload in uploads:
            uploads_by_date[
                upload.created_at.date() if upload.created_at else None
            ].append(upload)
        context["uploads"] = dict(
            uploads_by_date
        )  # Django template cannot iter on defaultdict
        context["uploaders"] = (
            Upload.objects.filter(album=album)
            .values("uploader")
            .annotate(total=Count("uploader"))
        )
        return context

    def form_valid(self, form):
        files = self.request.FILES.getlist("files")
        album = self.get_object()

        for uploaded_file in files:
            parse_date = None
            try:
                exif = Image.open(uploaded_file).getexif()
                exif_date = exif.get(306) or exif.get(36867) or exif.get(36868)
                # we could get timezone with exif_offset = exif.get(36880)
                # or exif.get(36881) or exif.get(36882)
                parse_date = (
                    datetime.datetime.strptime(exif_date, "%Y:%m:%d %H:%M:%S").replace(
                        tzinfo=timezone.get_current_timezone()
                    )
                    if exif_date
                    else None
                )
            except PIL.UnidentifiedImageError:
                pass
            Upload.objects.create(
                photo=uploaded_file,
                album=album,
                uploader=form.data["id_uploader"],
                created_at=parse_date,
            )
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse("album", kwargs={"id": self.kwargs[self.pk_url_kwarg]})


def get_last_album_update(album):
    """Last modification date for a given album"""
    return Upload.objects.filter(album=album).latest("uploaded_at").uploaded_at


def create_zip(zip_path, album):
    """Create a zip archive with all medias inside"""
    uploads = Upload.objects.filter(album=album)
    with open(zip_path, "wb") as zip_file:
        with zipfile.ZipFile(
            zip_file, "w", compression=zipfile.ZIP_STORED, allowZip64=True
        ) as archive:
            for upload in uploads:
                archive.write(
                    upload.photo.path, f"{album.name}/{basename(upload.photo.path)}"
                )


def download(request, album_id):
    """Function to download a given album as a big zip"""
    album = Album.objects.get(id=album_id)

    zip_dir = os.path.join(settings.MEDIA_ROOT, "zip")
    os.makedirs(zip_dir, exist_ok=True)
    zip_path = os.path.join(zip_dir, album_id + ".zip")
    last_update = get_last_album_update(album)
    if os.path.exists(zip_path):
        zip_date = datetime.datetime.fromtimestamp(
            os.stat(zip_path).st_mtime, tz=timezone.utc
        )
        if zip_date < last_update:
            create_zip(zip_path, album)
    else:
        create_zip(zip_path, album)
    return FileResponse(
        open(zip_path, "rb"),
        filename=f"{album.name}.zip",
        headers={
            "Content-Type": "application/x-zip-compressed",
            "Content-Disposition": f'attachment; filename="{album.name}.zip"',
        },
    )
