from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from app import views


urlpatterns = [
    path(r"", views.AlbumCreateView.as_view(), name="index"),
    path(r"album/<str:id>/", views.AlbumDetailView.as_view(), name="album"),
    path(r"download/<str:album_id>/", views.download, name="download"),
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
