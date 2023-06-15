from django.conf import settings
from django.shortcuts import render
import os
import string
import zipfile
import fitz
from django.http import HttpResponse
from .models import PDFFile
from django.http import Http404

def sanitize_filename(filename):
    valid_chars = f"-_.() {string.ascii_letters}{string.digits}"
    sanitized_filename = ''.join(c if c in valid_chars else '_' for c in filename)
    return sanitized_filename


def upload_pdf(request):
    if request.method == 'POST':
        pdf_file = request.FILES['pdf_file']

        # Generate a unique output folder name
        output_folder = sanitize_filename(pdf_file.name)  # Sanitize the filename for folder creation

        # Define the output path
        output_path = os.path.join(settings.MEDIA_ROOT, 'pdf_images', output_folder)
        os.makedirs(output_path, exist_ok=True)  # Create directory if it doesn't exist

        # Save the PDF file
        pdf_path = os.path.join(output_path, f'{output_folder}.pdf')
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
from django.http import HttpResponse
from django.conf import settings
import os
import zipfile
import mimetypes


def download_images(request, output_folder):
    # Define the directory path where the images are stored
    image_dir = os.path.join(settings.MEDIA_ROOT, 'pdf_images', output_folder)

    # Get the first image file in the directory
    image_file = next(iter(os.listdir(image_dir)), None)

    if image_file:
        # Construct the path of the image file
        image_path = os.path.join(image_dir, image_file)

        # Open the image file in binary mode
        with open(image_path, 'rb') as f:
            # Read the image data
            image_data = f.read()

        # Guess the MIME type of the image file
        mime_type, _ = mimetypes.guess_type(image_file)
        if mime_type is None:
            mime_type = 'application/octet-stream'

        # Create a response with the image data
        response = HttpResponse(image_data, content_type=mime_type)

        # Set the Content-Disposition header to specify the filename
        response['Content-Disposition'] = f'attachment; filename="{image_file}"'

        return response

    # If no image file is found, raise a 404 error
    raise Http404("Image not found.")