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


import mimetypes
import shutil
import tempfile

def download_images(request, output_folder):
    # Sanitize the output folder name
    output_folder = sanitize_filename(output_folder)

    # Define the directory path where the images are stored
    image_dir = os.path.join(settings.MEDIA_ROOT, 'pdf_images', output_folder)

    # If the request specifies downloading as a folder
    if request.GET.get('download_type') == 'folder':
        # Create a temporary directory to hold the images

        temp_dir = tempfile.mkdtemp(dir=settings.MEDIA_ROOT)
    
    # Create a temporary folder to hold the images
        temp_folder = os.path.join(temp_dir, output_folder)
        os.makedirs(temp_folder, exist_ok=True)

       

        # Copy the images to the temporary folder
        for image_file in os.listdir(image_dir):
            image_path = os.path.join(image_dir, image_file)
            if os.path.isfile(image_path):
                shutil.copy(image_path, temp_folder)

        # Get the MIME type of the first image file
        first_image_file = os.listdir(temp_folder)[0]
        first_image_path = os.path.join(temp_folder, first_image_file)
        mime_type, _ = mimetypes.guess_type(first_image_path)

        # Open the temporary folder as a file-like object
        temp_folder_file = open(temp_folder, 'rb')

        # Create a response to serve the temporary folder as a download
        response = HttpResponse(temp_folder_file, content_type=mime_type)

        # Set the Content-Disposition header to specify the filename
        response['Content-Disposition'] = f'attachment; filename="{output_folder}"'

        # Clean up the temporary directory
        shutil.rmtree(temp_dir)

        return response

    # If the request specifies downloading individual files
    elif request.GET.get('download_type') == 'files':
        # Create a response to serve the image files
        response = HttpResponse(content_type='image/jpeg')

        # Iterate over the image files in the directory
        for image_file in os.listdir(image_dir):
            image_path = os.path.join(image_dir, image_file)
            if os.path.isfile(image_path):
                # Open the image file in binary mode
                with open(image_path, 'rb') as f:
                    # Read the image data
                    image_data = f.read()

                # Set the Content-Disposition header to specify the filename
                response['Content-Disposition'] = f'attachment; filename="{image_file}"'

                # Write the image data to the response
                response.write(image_data)

        # If no image file is found, raise a 404 error
        if response.content == b'':
            raise Http404("No images found.")

        return response

    # If the request does not specify a download type, return an error
    else:
        return HttpResponse("Invalid download type.")
