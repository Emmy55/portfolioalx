from django.urls import path
from . import views

urlpatterns = [
    path("", views.upload_pdf, name="convert_pdf"),
    path('download_images/<path:output_folder>/', views.download_images, name='download_images'),
]