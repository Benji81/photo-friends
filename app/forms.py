from django import forms


class UploadFileForm(forms.Form):
    """Main app form: upload one or more files"""

    uploader = forms.TextInput()
    files = forms.FileField(
        widget=forms.ClearableFileInput(attrs={"allow_multiple_selected": True})
    )
