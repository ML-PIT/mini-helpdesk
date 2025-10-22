from django import forms
from .models import KnowledgeArticle


class KnowledgeArticleForm(forms.ModelForm):
    """Form for creating and editing knowledge articles with CKEditor"""

    class Meta:
        model = KnowledgeArticle
        fields = ['title', 'excerpt', 'content', 'category', 'keywords', 'is_public', 'is_featured', 'status']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Titel des Artikels...'
            }),
            'excerpt': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Kurze Zusammenfassung des Artikels...'
            }),
            # CKEditor widget is automatically used for RichTextUploadingField
            'category': forms.Select(attrs={
                'class': 'form-control',
            }),
            'keywords': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'z.B. passwort, zurücksetzen, login'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'status': forms.Select(attrs={
                'class': 'form-control',
            }),
        }
