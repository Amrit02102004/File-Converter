from django import forms

class UploadFileForm(forms.Form):
    file = forms.FileField()
    target_format = forms.ChoiceField(choices=[('pdf', 'PDF'), ('docx', 'DOCX'), ('pptx', 'PPTX')])
from django.core.exceptions import ValidationError

def validate_file_size(value):
    if value.size > 5 * 1024 * 1024:  # 5 MB
        raise ValidationError('File size exceeds 5 MB!')