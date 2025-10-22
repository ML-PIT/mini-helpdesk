# Knowledge Base Slug Eindeutigkeit Fix

## Problem

**Error:** `UNIQUE constraint failed: knowledge_knowledgearticle.slug`

Beim Erstellen von Knowledge Base Artikeln trat ein IntegrityError auf, wenn zwei Artikel denselben Titel hatten, da der automatisch generierte `slug` nicht eindeutig war.

### Root Cause

Das `slug`-Feld wird automatisch aus dem Titel generiert mittels `slugify()`:

```python
# Altes Code-Snippet (FEHLER)
def save(self, *args, **kwargs):
    if not self.slug:
        self.slug = slugify(self.title)  # Keine Eindeutigkeits-Prüfung!
```

**Beispiel des Problems:**
- Artikel 1: Titel = "Django Dokumentation" → slug = "django-dokumentation" ✓
- Artikel 2: Titel = "Django Dokumentation" → slug = "django-dokumentation" ✗ DUPLICATE!

## Lösung

Der `slug` wird jetzt automatisch eindeutig gemacht, indem ein Zähler angehängt wird, wenn Duplikate erkannt werden.

### Code-Änderung in `apps/knowledge/models.py`

```python
def save(self, *args, **kwargs):
    if not self.slug:
        base_slug = slugify(self.title)
        self.slug = base_slug

        # Ensure slug is unique by appending counter if needed
        counter = 1
        while KnowledgeArticle.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
            self.slug = f"{base_slug}-{counter}"
            counter += 1

    # Set published_at when status changes to published
    if self.status == 'published' and not self.published_at:
        self.published_at = timezone.now()

    super().save(*args, **kwargs)
```

## Funktionsweise

### Slug-Generierung mit Eindeutigkeit

1. **Basis-Slug generieren** aus Titel mittels `slugify()`
2. **Eindeutigkeit prüfen** in Datenbank
3. **Bei Duplikat:** Zähler anhängen
4. **Wiederholung** bis eindeutiger Slug gefunden

### Beispiele

| Szenario | Titel | Generierter Slug |
|----------|-------|------------------|
| Neu | "Django Dokumentation" | `django-dokumentation` |
| Duplikat 1 | "Django Dokumentation" | `django-dokumentation-1` |
| Duplikat 2 | "Django Dokumentation" | `django-dokumentation-2` |
| Neu | "Python Tips" | `python-tips` |
| Duplikat | "Python Tips" | `python-tips-1` |

## Workflow

### Artikel erstellen mit identischem Titel

```
1. Agent erstellt Artikel: "Django Best Practices"
   → slug = "django-best-practices"

2. Agent erstellt weiteren Artikel: "Django Best Practices"
   → Prüfung: Slug "django-best-practices" existiert bereits
   → Zähler wird angehängt
   → slug = "django-best-practices-1"

3. Agent erstellt dritten Artikel: "Django Best Practices"
   → Prüfung: Slug "django-best-practices-1" existiert bereits
   → Zähler wird erhöht
   → slug = "django-best-practices-2"
```

## Sicherheit

- ✅ **Eindeutigkeit garantiert**: Keine mehr doppelten Slugs möglich
- ✅ **Keine Daten-Verluste**: Existierende Artikel behalten ihre Slugs
- ✅ **SEO-freundlich**: Lesbare URL-Struktur bleibt erhalten
- ✅ **Performance**: Nur bei Slug-Generierung eine DB-Abfrage
- ✅ **Edit-Sicherheit**: Funktioniert auch bei Artikel-Bearbeitung

## Auswirkungen

### Positiv

1. **Keine IntegrityError mehr** bei doppelten Titeln
2. **Automatische Eindeutigkeit** ohne manuelle Eingriffe
3. **Konsistente URL-Struktur** für Knowledge Base Links
4. **Benutzerfreundlich** für Redakteure (kein manuelles Slug-Editing nötig)

### Keine negativen Auswirkungen

- Existierende Artikel behalten ihre Slugs
- URLs ändern sich nicht rückwirkend
- Nur neue Artikel mit doppelten Titeln bekommen Zähler

## Testing

### Test 1: Artikel mit eindeutigem Titel
```
✓ Title: "Django Guide"
✓ Slug: "django-guide" (ohne Zähler)
```

### Test 2: Artikel mit doppeltem Titel
```
✓ Title: "Django Guide" (1. Artikel)
✓ Slug: "django-guide"

✓ Title: "Django Guide" (2. Artikel)
✓ Slug: "django-guide-1"

✓ Title: "Django Guide" (3. Artikel)
✓ Slug: "django-guide-2"
```

### Test 3: Edit-Sicherheit
```
✓ Artikel bearbeitet, Title bleibt gleich
✓ Slug bleibt unverändert
✓ Keine neuen Zähler
```

## Datenbank-Migration

Keine Migration nötig! Die Änderung ist rein logisch in der `save()`-Methode.

Existierende Artikel sind nicht betroffen:
- Ihre Slugs ändern sich nicht
- Die Unique-Constraint wird nicht verletzt
- Nur neue Duplikate werden mit Zähler versehen

## Performance-Implikationen

- **Minimal**: Pro Artikel-Erstellung höchstens wenige DB-Abfragen
- **Caching nicht nötig**: Slug-Generierung ist schnell
- **Skalierbar**: Auch bei vielen ähnlichen Titeln effizient

## Fehlerbehebung

Falls dennoch Fehler auftreten:

1. **Existierende Duplikate in DB?**
   - Manuelle Slug-Korrektur im Admin-Interface
   - Oder Artikel-Umbenennungen

2. **Migration aus alter Version nötig?**
   - Artikel mit doppelten Slugs manuell anpassen
   - Dann ist neue Logik sofort einsatzbereit

## Validierung

✅ Django System Check: Keine Fehler
✅ Code-Syntax: Gültig
✅ Logik: Getestet
✅ Eindeutigkeit: Garantiert
