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
            # mobile_classroom field removed
        }
        labels = {
            'title': 'Titel',
            'description': 'Beschreibung',
            'category': 'Kategorie',
            'priority': 'Priorität',
            # mobile_classroom label removed
        }


class AgentTicketCreateForm(forms.ModelForm):
    """Form for agents to create tickets on behalf of customers"""

    customer_search = forms.CharField(
        label='Kunde suchen (Name oder Email)',
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Kundenname (z.B. "Max Mustermann") oder Email eingeben...',
            'id': 'customer-search-field',
            'autocomplete': 'off',
            'data-url': '/tickets/api/search-customers/'
        }),
        help_text='Geben Sie den Namen oder die Email eines Kunden ein, um diesen zu suchen'
    )

    customer_email = forms.EmailField(
        label='Kunden-Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'kunde@example.com',
            'id': 'customer-email-field'
        }),
        help_text='Email-Adresse des Kunden',
        required=False
    )

    customer_first_name = forms.CharField(
        label='Vorname des Kunden',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Vorname (optional, falls noch nicht registriert)',
            'id': 'customer-first-name-field'
        }),
        help_text='Nur erforderlich, wenn der Kunde noch nicht im System existiert'
    )

    customer_last_name = forms.CharField(
        label='Nachname des Kunden',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nachname (optional, falls noch nicht registriert)',
            'id': 'customer-last-name-field'
        }),
        help_text='Nur erforderlich, wenn der Kunde noch nicht im System existiert'
    )

    customer_phone = forms.CharField(
        label='Telefonnummer des Kunden',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'z.B. +49 30 12345678 oder 030/12345678',
            'id': 'customer-phone-field'
        }),
        help_text='Telefonnummer des Kunden (optional, aber empfohlen)'
    )

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
            # mobile_classroom field removed
        }
        labels = {
            'title': 'Titel',
            'description': 'Beschreibung',
            'category': 'Kategorie',
            'priority': 'Priorität',
            # mobile_classroom label removed
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
