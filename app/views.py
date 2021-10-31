from os.path import basename
import tempfile
import zipfile

import PIL
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.generic import CreateView, DetailView, FormView

from app.forms import UploadFileForm
from app.models import Album, Upload


class AlbumCreateView(CreateView):
    """View to create a album a auto generate an UUID"""

    model = Album
    fields = ["name", "creator"]

    def form_valid(self, form):
        album = form.save(commit=False)
        album.created_by = self.request.user
        album.save()
        return HttpResponseRedirect(reverse("album", kwargs={"id": album.id}))


class AlbumDetailView(DetailView, FormView):
    model = Album
    pk_url_kwarg = "id"
    queryset = Album.objects.all()
    form_class = UploadFileForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        album = Album.objects.get(id=self.kwargs[self.pk_url_kwarg])
        context["uploads"] = Upload.objects.filter(album=album)
        return context

    def form_valid(self, form):
        files = self.request.FILES.getlist("files")
        album = self.get_object()

        for uploaded_file in files:
            try:
                Upload.objects.create(
                    photo=uploaded_file, album=album, uploader=form.data["id_uploader"]
                )
            except PIL.UnidentifiedImageError:
                pass
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse("album", kwargs={"id": self.kwargs[self.pk_url_kwarg]})


def download(request, id):
    album = Album.objects.get(id=id)
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
