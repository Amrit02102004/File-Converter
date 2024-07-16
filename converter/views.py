import os
from pathlib import Path
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from docx import Document
from pptx import Presentation
import fitz  # PyMuPDF
from pdf2docx import Converter
from .forms import UploadFileForm
from .models import UploadedFile

def handle_uploaded_file(f, target_format):
    media_root = settings.MEDIA_ROOT
    if not os.path.exists(media_root):
        os.makedirs(media_root)

    input_path = os.path.join(media_root, f.name)
    output_path = os.path.splitext(input_path)[0] + f'.{target_format}'

    with open(input_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    # Perform conversion here
    if target_format == 'pdf':
        if f.name.endswith(('.docx', '.doc')):
            doc = Document(input_path)
            doc.save(output_path)
        elif f.name.endswith(('.pptx', '.ppt')):
            pres = Presentation(input_path)
            pres.save(output_path)
        else:
            raise ValueError('Unsupported file type for PDF conversion')
    elif target_format == 'docx':
        if f.name.endswith('.pdf'):
            cv = Converter(input_path)
            cv.convert(output_path)
            cv.close()
        elif f.name.endswith(('.pptx', '.ppt')):
            raise NotImplementedError('PPTX to DOCX conversion not implemented')
        else:
            raise ValueError('Unsupported file type for DOCX conversion')
    elif target_format == 'pptx':
        raise NotImplementedError('DOCX or PDF to PPTX conversion not implemented')

    return output_path

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            target_format = form.cleaned_data['target_format']
            try:
                output_file_path = handle_uploaded_file(request.FILES['file'], target_format)
                with open(output_file_path, 'rb') as f:
                    response = HttpResponse(f.read(), content_type=f'application/{target_format}')
                    response['Content-Disposition'] = f'attachment; filename={Path(output_file_path).name}'
                    return response
            except Exception as e:
                return HttpResponse(f"Error: {e}", status=400)
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})
