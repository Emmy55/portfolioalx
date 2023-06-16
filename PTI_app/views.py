from django.conf import settings
from django.shortcuts import render
import os
import string
import fitz
from django.http import HttpResponse
from .models import PDFFile
from django.http import Http404
import mimetypes
import shutil
import tempfile
from django.http import HttpResponseBadRequest


def sanitize_filename(filename):
    valid_chars = f"-_.() {string.ascii_letters}{string.digits}"
    sanitized_filename = ''.join(c if c in valid_chars else '_' for c in filename)
    return sanitized_filename


def upload_pdf(request):
    if request.method == 'POST' and request.FILES['pdf_file']:
        pdf_file = request.FILES['pdf_file']
        if pdf_file.content_type != 'application/pdf':
           return HttpResponseBadRequest('Only PDF files are allowed.')
            
        # Generate a unique output folder name
        output_folder = sanitize_filename(pdf_file.name)  # Sanitize the filename for folder creation

        # Define the output path
        output_path = os.path.join(settings.MEDIA_ROOT, 'pdf_images', output_folder)
        os.makedirs(output_path, exist_ok=True)  # Create directory if it doesn't exist

        # Save the PDF file
        pdf_path = os.path.join(output_path, f'{output_folder}')
        with open(pdf_path, 'wb') as f:
            for chunk in pdf_file.chunks():
                f.write(chunk)

        # Convert PDF to images
        doc = fitz.open(pdf_path)
        images = []
        for i in range(doc.page_count):
            page = doc.load_page(i)
            pix = page.get_pixmap()
            image_path = os.path.join(output_path, f'page_{i + 1}.jpeg')
            pix.save(image_path)
            images.append(os.path.join(settings.MEDIA_URL, 'pdf_images', output_folder, f'page_{i + 1}.jpeg'))

        # Create a new PDFFile instance
        pdf_file_obj = PDFFile(pdf_file=pdf_file)
        pdf_file_obj.save()

        return render(request, 'PTI_app/image.html', {'output_folder': output_folder, 'image_files': images})

    elif request.method == 'GET':
        return render(request, 'PTI_app/home.html')

