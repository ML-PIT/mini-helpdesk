"""
API endpoints for file uploads
"""
import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from .file_handler import FileUploadHandler


@login_required
@require_http_methods(["POST"])
def upload_file(request):
    """
    Upload a file and return JSON response

    Request should be multipart/form-data with:
    - file: File to upload
    - upload_type: Type of upload (ticket_attachment, knowledge_attachment, etc.)
    """
    try:
        if 'file' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'No file provided'
            }, status=400)

        file_obj = request.FILES['file']
        upload_type = request.POST.get('upload_type', 'ticket_attachment')

        # Validate file
        handler = FileUploadHandler()
        is_valid, error_msg = handler.validate_file(file_obj)

        if not is_valid:
            return JsonResponse({
                'success': False,
                'error': error_msg
            }, status=400)

        # Save file
        upload_path = handler.get_upload_path(upload_type)
        file_name = default_storage.save(
            f'{upload_path}{file_obj.name}',
            file_obj
        )

        # Return response
        return JsonResponse({
            'success': True,
            'file_name': file_name,
            'file_url': f'/media/{file_name}',
            'file_size': handler.format_file_size(file_obj.size),
            'message': 'File uploaded successfully'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def upload_image_for_editor(request):
    """
    Upload image for rich text editor (CKEditor/TinyMCE)

    Returns JSON with image URL for editor integration
    """
    try:
        if 'upload' not in request.FILES:
            return JsonResponse({
                'error': {'message': 'No image provided'},
                'uploaded': False
            }, status=400)

        image_file = request.FILES['upload']

        # Validate image
        handler = FileUploadHandler()
        is_valid, error_msg = handler.validate_file(image_file)

        if not is_valid:
            return JsonResponse({
                'error': {'message': error_msg},
                'uploaded': False
            }, status=400)

        # Save image
        upload_path = 'editor_images/'
        file_name = default_storage.save(
            f'{upload_path}{image_file.name}',
            image_file
        )

        # Return CKEditor compatible response
        return JsonResponse({
            'uploaded': True,
            'url': f'/media/{file_name}'
        })

    except Exception as e:
        return JsonResponse({
            'error': {'message': str(e)},
            'uploaded': False
        }, status=500)
