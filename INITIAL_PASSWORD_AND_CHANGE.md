# Initial-Passwort und erzwungene Passwort-Änderung

## Übersicht

Wenn Support-Agenten Kunden telefonisch Tickets erstellen und dabei einen neuen Kundenkonto anlegen, wird:
1. Der neue Kunde mit dem Initial-Passwort `P@ssw0rd123` erstellt
2. Das Flag `force_password_change=True` gesetzt
3. Der Kunde beim ersten Login gezwungen, das Passwort zu ändern

## Workflow

### 1. Agent erstellt Ticket für neuen Kunden

```
1. Agent navigiert zu /tickets/create/
2. Wählt "Ticket für Kunde erstellen"
3. Gibt E-Mail, Vor- und Nachname ein
4. Füllt Ticket-Details aus
5. Klickt "Ticket erstellen"
```

### 2. System erstellt Kunden mit Initial-Passwort

**Was passiert im Hintergrund:**
- Neuer Kundenkonto wird erstellt
- Passwort wird auf `P@ssw0rd123` gesetzt
- `force_password_change` wird auf `True` gesetzt
- Agent sieht Meldung mit dem Passwort

**Meldung für Agent:**
```
Neuer Kunde "Max Mueller" wurde im System erstellt. Initial-Passwort: P@ssw0rd123
```

### 3. Kunde meldet sich an

**Erste Anmeldung:**
- Kunde loggt sich mit E-Mail und `P@ssw0rd123` ein
- Middleware erkennt `force_password_change=True`
- Kunde wird automatisch zur Passwort-Änderungs-Seite weitergeleitet
- Kunde kann nicht auf andere Seiten zugreifen, solange Passwort nicht geändert ist

**Passwort-Änderung:**
- Kunde sieht Warnung: "Sie wurden mit einem temporären Passwort angemeldet. Bitte ändern Sie Ihr Passwort jetzt."
- Kunde gibt aktuelles Passwort (`P@ssw0rd123`) ein
- Kunde gibt neues Passwort zweimal ein
- System setzt `force_password_change=False`
- Kunde wird zum Dashboard weitergeleitet

## Technische Implementierung

### 1. User-Modell (`apps/accounts/models.py`)

**Neues Feld:**
```python
force_password_change = models.BooleanField(
    _('force password change on next login'),
    default=False,
    help_text=_('If True, user must change password on next login')
)
```

### 2. Ticket-View (`apps/tickets/views.py`)

**Neue Kunden werden mit Initial-Passwort erstellt:**
```python
INITIAL_PASSWORD = 'P@ssw0rd123'
customer = User.objects.create_user(
    email=customer_email,
    username=username,
    password=INITIAL_PASSWORD,
    first_name=customer_first_name,
    last_name=customer_last_name,
    role='customer',
    force_password_change=True  # Force password change on first login
)
```

### 3. Middleware (`apps/accounts/middleware.py`)

**ForcePasswordChangeMiddleware:**
- Prüft nach jedem Request, ob Benutzer `force_password_change=True` hat
- Leitet zur Passwort-Änderungs-View weiter (wenn nicht bereits dort)
- Erlaubt Zugriff auf bestimmte Seiten: logout, password_change, static, media, api

**Exempt Paths (Ausnahmen):**
- `/accounts/change_password/` - Passwort-Änderungs-Seite
- `/accounts/logout/` - Logout
- `/static/` - Statische Dateien
- `/media/` - Mediadateien
- `/api/` - API-Endpoints
- `/admin/` - Admin-Panel

### 4. Change Password View (`apps/accounts/views.py`)

```python
@login_required
def change_password(request):
    force_change = request.user.force_password_change

    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()

            # Clear the flag if this was a forced change
            if force_change:
                user.force_password_change = False
                user.save()

            # Keep user logged in
            update_session_auth_hash(request, user)

            messages.success(request, 'Ihr Passwort wurde erfolgreich geändert!')
            return redirect('main:dashboard')
    else:
        form = PasswordChangeForm(request.user)

    context = {
        'form': form,
        'force_change': force_change,
    }
    return render(request, 'accounts/change_password.html', context)
```

### 5. URLs (`apps/accounts/urls.py`)

```python
path('change_password/', views.change_password, name='change_password'),
```

### 6. Settings (`helpdesk/settings.py`)

**Middleware registriert:**
```python
MIDDLEWARE = [
    # ... andere middleware ...
    'apps.accounts.middleware.ForcePasswordChangeMiddleware',
]
```

### 7. Template (`templates/accounts/change_password.html`)

**Zeigt Warnung für erzwungene Passwort-Änderung:**
```html
{% if force_change %}
<div style="background: #fff3cd; border-left: 4px solid #ffc107; ...">
    <strong>⚠️ Passwort-Änderung erforderlich</strong><br>
    Sie wurden mit einem temporären Passwort angemeldet. Bitte ändern Sie Ihr Passwort jetzt.
</div>
{% endif %}
```

## Sicherheitsfeatures

1. **Middleware-Schutz**: Benutzer können nicht auf andere Seiten zugreifen
2. **Session-Erhaltung**: Benutzer bleibt eingeloggt nach Passwort-Änderung
3. **Klare Fehlermeldungen**: Informiert Benutzer über Anforderung
4. **Admin-Kontrolle**: Admin kann über Django Admin manuell `force_password_change` setzen

## Standort (Location) - Bereits Optional

Das Feld `MobileClassroom.location` ist bereits optional konfiguriert:
```python
location = models.ForeignKey(
    MobileClassroomLocation,
    on_delete=models.SET_NULL,
    null=True,  # Kann NULL sein
    blank=True, # Optional im Admin/Form
    ...
)
```

## Database-Migrationen

**Angewendete Migration:**
```
apps/accounts/migrations/0003_user_force_password_change_alter_user_support_level.py
```

Diese Migration:
- Fügt `force_password_change` Feld hinzu (Standard: False)
- Ändert `support_level` Feld-Eigenschaften

## Testing-Szenarien

### Test 1: Neuer Kunde via Telefon-Ticket
```
1. Agent erstellt Ticket für neuen Kunden
2. System zeigt: "Initial-Passwort: P@ssw0rd123"
3. Kunde loggt sich ein mit P@ssw0rd123
4. Middleware leitet zur Passwort-Änderung weiter
5. Kunde ändert Passwort zu "MeinNeuesPasswort123"
6. Flag wird gelöscht, Kunde kann Dashboard sehen
```

### Test 2: Existierender Kunde
```
1. Agent erstellt Ticket für existierenden Kunden
2. Keine neuen Passwörter nötig
3. Kunde kann sich normal anmelden
```

### Test 3: Admin setzt force_password_change manuell
```
1. Admin geht zu Django Admin
2. Findet Benutzer
3. Setzt `force_password_change = True`
4. Speichert
5. Nächster Login: Benutzer wird zur Passwort-Änderung geleitet
```

## URLs

- **Change Password (Custom)**: `/accounts/change_password/`
- **Django Default Password Change**: `/accounts/password_change/`
- **Django Default Password Change Done**: `/accounts/password_change/done/`

## Admin-Integration

Die neuen Felder sind im Django Admin verfügbar:
- `force_password_change` ist editierbar im Admin
- Wird in der User-Changelist angezeigt (wenn in UserAdmin.list_display eingestellt)

Zum Anzeigen in Admin, bearbeiten Sie `apps/accounts/admin.py`:
```python
class UserAdmin(admin.ModelAdmin):
    list_display = [..., 'force_password_change']
    # oder im fieldset
    fieldsets = (
        ...
        ('Passwort', {'fields': ('force_password_change',)}),
    )
```

## Validierung

✅ Django System Check: Keine Fehler
✅ Template Syntax: Valid
✅ Migrations: Erfolgreich angewendet
✅ Form Validation: Funktioniert korrekt
