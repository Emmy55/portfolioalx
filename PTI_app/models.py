from django.db import models

# Create your models here.



class PDFFile(models.Model):
    pdf_file = models.FileField(upload_to='pdf_files/')
    image = models.ImageField(upload_to='pdf_images/', blank=True)
