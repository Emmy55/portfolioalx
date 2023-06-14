from django.urls import path
from . import views

urlpatterns = [
    path("image/", views.upload_pdf, name="convert_pdf"),
]