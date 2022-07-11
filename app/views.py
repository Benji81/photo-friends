from collections import defaultdict
import datetime
from os.path import basename
import tempfile
import zipfile

import PIL
from PIL import Image
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import CreateView, DetailView, FormView

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
        context["uploaders"] = Upload.objects.all().values('uploader').annotate(total=Count('uploader'))
        return context

    def form_valid(self, form):
        files = self.request.FILES.getlist("files")
        album = self.get_object()

        for uploaded_file in files:
            parse_date = None
            try:
                exif = Image.open(uploaded_file).getexif()
                exif_date = exif.get(306) or exif.get(36867) or exif.get(36868)
                # we could get timezone with exif_offset = exif.get(36880) or exif.get(36881) or exif.get(36882)
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


def download(request, album_id):
    """Function to download a given album as a big zip"""
    album = Album.objects.get(id=album_id)
    uploads = Upload.objects.filter(album=album)

    with tempfile.SpooledTemporaryFile() as tmp:
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as archive:
            for upload in uploads:
                archive.write(
                    upload.photo.path, f"{album.name}/{basename(upload.photo.path)}"
                )
        tmp.seek(0)
        return HttpResponse(
            tmp.read(),
            headers={
                "Content-Type": "application/x-zip-compressed",
                "Content-Disposition": f'attachment; filename="{album.name}.zip"',
            },
        )
