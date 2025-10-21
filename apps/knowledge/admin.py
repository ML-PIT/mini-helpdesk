from django.contrib import admin
from .models import KnowledgeArticle


@admin.register(KnowledgeArticle)
class KnowledgeArticleAdmin(admin.ModelAdmin):
    """Knowledge article admin"""
    list_display = ['title', 'status', 'author', 'category', 'is_public',
                   'is_featured', 'views', 'published_at']
    list_filter = ['status', 'is_public', 'is_featured', 'category', 'published_at']
    search_fields = ['title', 'content', 'keywords']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'

    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'excerpt', 'content')
        }),
        ('Organization', {
            'fields': ('category', 'author', 'status')
        }),
        ('SEO', {
            'fields': ('meta_description', 'keywords'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('is_public', 'is_featured')
        }),
        ('Statistics', {
            'fields': ('views', 'helpful_count', 'not_helpful_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('published_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['views', 'helpful_count', 'not_helpful_count',
                      'created_at', 'updated_at']

    def has_module_permission(self, request):
        """Only admins can access knowledge management in admin"""
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or (hasattr(request.user, 'role') and request.user.role == 'admin')
