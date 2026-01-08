from django import forms

class URLForm(forms.Form):
    original_url = forms.URLField(
        label='Enter URL',
        widget=forms.URLInput(attrs={
            'placeholder': 'https://example.com',
            'class': 'form-control'
        })
    )