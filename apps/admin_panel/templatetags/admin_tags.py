"""
Template tags for admin panel
"""
from django import template
from django.utils.safestring import mark_safe
from apps.admin_panel.models import SystemSettings

register = template.Library()


@register.filter
def get_editor_class(editor_choice=None):
    """
    Return the CSS class for the chosen text editor
    Usage: {{ text_editor|get_editor_class }}
    """
    if not editor_choice:
        settings = SystemSettings.get_settings()
        editor_choice = settings.text_editor

    if editor_choice == 'tinymce':
        return 'tinymce-editor'
    elif editor_choice == 'ckeditor':
        return 'ckeditor-editor'
    return 'tinymce-editor'  # default


@register.simple_tag
def render_editor(field_name, content='', editor_choice=None, css_class=''):
    """
    Render a rich text editor textarea
    Usage: {% render_editor 'description' my_content %}
    """
    if not editor_choice:
        settings = SystemSettings.get_settings()
        editor_choice = settings.text_editor

    editor_class = get_editor_class(editor_choice)
    full_class = f'{editor_class} form-control {css_class}'.strip()

    html = f'''
    <textarea
        name="{field_name}"
        class="{full_class}"
        style="width: 100%; min-height: 300px;">
{content}</textarea>
    '''
    return mark_safe(html)


@register.simple_tag
def ckeditor_script():
    """
    Render CKEditor initialization script
    Usage: {% ckeditor_script %}
    """
    from django.utils.translation import get_language

    current_lang = get_language() or 'de'

    script = f'''
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            const editorElements = document.querySelectorAll('textarea.ckeditor-editor');
            editorElements.forEach(element => {{
                ClassicEditor
                    .create(element, {{
                        language: '{current_lang}',
                        toolbar: {{
                            items: [
                                'bold', 'italic', '|',
                                'heading', '|',
                                'bulletedList', 'numberedList', '|',
                                'blockQuote', 'codeBlock', '|',
                                'undo', 'redo'
                            ]
                        }}
                    }})
                    .catch(error => console.error(error));
            }});
        }});
    </script>
    '''
    return mark_safe(script)


@register.simple_tag
def tinymce_script():
    """
    Render TinyMCE initialization script
    Usage: {% tinymce_script %}
    """
    from django.utils.translation import get_language

    current_lang = get_language() or 'de'

    script = f'''
    <script>
        tinymce.init({{
            selector: 'textarea.tinymce-editor',
            plugins: 'link image code table lists autoresize',
            toolbar: 'undo redo | formatselect | bold italic | alignleft aligncenter alignright | bullist numlist | link image code',
            height: 300,
            language: '{current_lang}',
            menubar: false,
            images_upload_url: '/admin-panel/api/upload-image/',
        }});
    </script>
    '''
    return mark_safe(script)


@register.simple_tag
def get_editor_type():
    """
    Get the current editor type configured in settings
    Usage: {{ get_editor_type }}
    """
    try:
        settings = SystemSettings.get_settings()
        return settings.text_editor
    except:
        return 'tinymce'
