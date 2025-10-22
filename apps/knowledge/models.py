from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify


class KnowledgeArticle(models.Model):
    """Knowledge base articles"""

    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('published', _('Published')),
        ('archived', _('Archived')),
    ]

    title = models.CharField(_('title'), max_length=200, db_index=True)
    slug = models.SlugField(_('slug'), max_length=220, unique=True, blank=True)
    content = models.TextField(_('content'))
    excerpt = models.TextField(_('excerpt'), blank=True,
                              help_text='Short summary of the article')

    # Organization
    category = models.ForeignKey('tickets.Category',
                                on_delete=models.SET_NULL,
                                null=True, blank=True,
                                related_name='knowledge_articles',
                                verbose_name=_('category'))

    # Metadata
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES,
                            default='draft', db_index=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.PROTECT,
                              related_name='knowledge_articles',
                              verbose_name=_('author'))

    # SEO
    meta_description = models.CharField(_('meta description'), max_length=160, blank=True)
    keywords = models.CharField(_('keywords'), max_length=255, blank=True,
                               help_text='Comma-separated keywords')

    # Statistics
    views = models.IntegerField(_('views'), default=0)
    helpful_count = models.IntegerField(_('helpful votes'), default=0)
    not_helpful_count = models.IntegerField(_('not helpful votes'), default=0)

    # Timestamps
    created_at = models.DateTimeField(_('created at'), default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    published_at = models.DateTimeField(_('published at'), null=True, blank=True)

    # Access control
    is_public = models.BooleanField(_('public'), default=True,
                                   help_text='Visible to all users including customers')
    is_featured = models.BooleanField(_('featured'), default=False)

    class Meta:
        verbose_name = _('knowledge article')
        verbose_name_plural = _('knowledge articles')
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

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

    @property
    def helpfulness_ratio(self):
        """Calculate helpfulness ratio"""
        total = self.helpful_count + self.not_helpful_count
        if total == 0:
            return 0
        return (self.helpful_count / total) * 100

    def increment_views(self):
        """Increment view counter"""
        self.views += 1
        self.save(update_fields=['views'])

    def vote_helpful(self, helpful=True):
        """Record a helpfulness vote"""
        if helpful:
            self.helpful_count += 1
        else:
            self.not_helpful_count += 1
        self.save(update_fields=['helpful_count', 'not_helpful_count'])

    def to_dict(self, include_content=False):
        """Convert article to dictionary"""
        data = {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'excerpt': self.excerpt,
            'status': self.status,
            'author': self.author.to_dict(),
            'category': self.category.name if self.category else None,
            'views': self.views,
            'helpfulness_ratio': self.helpfulness_ratio,
            'is_public': self.is_public,
            'is_featured': self.is_featured,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }

        if include_content:
            data['content'] = self.content
            data['meta_description'] = self.meta_description
            data['keywords'] = self.keywords

        return data
