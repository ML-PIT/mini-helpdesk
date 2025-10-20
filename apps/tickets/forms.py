from django import forms
from .models import Ticket, TicketComment


class TicketCreateForm(forms.ModelForm):
    """Form for creating tickets"""

    class Meta:
        model = Ticket
        fields = ['title', 'description', 'category', 'priority']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Kurze Beschreibung des Problems'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Detaillierte Beschreibung des Problems...'
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': 'Titel',
            'description': 'Beschreibung',
            'category': 'Kategorie',
            'priority': 'Priorität',
        }


class TicketCommentForm(forms.ModelForm):
    """Form for adding comments to tickets"""

    is_internal = forms.BooleanField(
        required=False,
        label='Interner Kommentar (nur für Support-Team sichtbar)',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = TicketComment
        fields = ['content', 'is_internal']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Ihre Nachricht...'
            }),
        }
        labels = {
            'content': 'Kommentar',
        }
