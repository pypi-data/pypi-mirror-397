"""
Chedito URL configuration.

Include these URLs in your project's urls.py:

    from django.urls import path, include

    urlpatterns = [
        ...
        path('chedito/', include('chedito.urls')),
    ]
"""

from django.urls import path

from chedito.views import ImageUploadView, VideoUploadView, FileUploadView

app_name = "chedito"

urlpatterns = [
    path("upload/image/", ImageUploadView.as_view(), name="upload_image"),
    path("upload/video/", VideoUploadView.as_view(), name="upload_video"),
    path("upload/file/", FileUploadView.as_view(), name="upload_file"),
]
