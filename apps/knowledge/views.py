from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Q
from .models import KnowledgeArticle
from apps.tickets.models import Category


@login_required
def kb_list(request):
    """List all published knowledge base articles"""
    search_query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')

    # Base query - only published articles
    articles = KnowledgeArticle.objects.filter(status='published')

    # Customers only see public articles
    if request.user.role == 'customer':
        articles = articles.filter(is_public=True)

    # Search functionality
    if search_query:
        articles = articles.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(excerpt__icontains=search_query) |
            Q(keywords__icontains=search_query)
        )

    # Filter by category
    if category_id:
        articles = articles.filter(category_id=category_id)

    # Get featured articles
    featured = articles.filter(is_featured=True)[:3]

    # Get categories
    categories = Category.objects.filter(is_active=True)

    context = {
        'articles': articles.order_by('-published_at'),
        'featured': featured,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_id,
    }
    return render(request, 'knowledge/list.html', context)


@login_required
def kb_detail(request, slug):
    """View a single knowledge base article"""
    article = get_object_or_404(KnowledgeArticle, slug=slug, status='published')

    # Check if customer can access
    if request.user.role == 'customer' and not article.is_public:
        return HttpResponseForbidden('Sie haben keine Berechtigung, diesen Artikel zu sehen.')

    # Increment view counter
    article.increment_views()

    # Handle helpfulness votes
    if request.method == 'POST':
        vote = request.POST.get('vote')
        if vote == 'helpful':
            article.vote_helpful(helpful=True)
            messages.success(request, 'Vielen Dank für Ihr Feedback!')
        elif vote == 'not_helpful':
            article.vote_helpful(helpful=False)
            messages.success(request, 'Vielen Dank für Ihr Feedback!')
        return redirect('knowledge:detail', slug=slug)

    # Get related articles
    related = KnowledgeArticle.objects.filter(
        status='published',
        category=article.category
    ).exclude(id=article.id)[:3]

    if request.user.role == 'customer':
        related = related.filter(is_public=True)

    context = {
        'article': article,
        'related': related,
    }
    return render(request, 'knowledge/detail.html', context)


@login_required
def kb_create(request):
    """Create a new knowledge article - only for Level 2+ agents and admins"""
    if request.user.role == 'customer':
        return HttpResponseForbidden('Keine Berechtigung')

    if request.user.role == 'support_agent' and (not request.user.support_level or request.user.support_level < 2):
        messages.error(request, 'Nur Support Agents Level 2 und höher können Artikel erstellen.')
        return redirect('knowledge:list')

    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        excerpt = request.POST.get('excerpt', '')
        category_id = request.POST.get('category')
        keywords = request.POST.get('keywords', '')
        is_public = request.POST.get('is_public') == 'on'
        is_featured = request.POST.get('is_featured') == 'on'
        status = request.POST.get('status', 'draft')

        article = KnowledgeArticle.objects.create(
            title=title,
            content=content,
            excerpt=excerpt,
            category_id=category_id if category_id else None,
            keywords=keywords,
            is_public=is_public,
            is_featured=is_featured,
            status=status,
            author=request.user
        )

        messages.success(request, f'Artikel "{article.title}" wurde erstellt!')
        return redirect('knowledge:detail', slug=article.slug)

    categories = Category.objects.filter(is_active=True)
    context = {'categories': categories}
    return render(request, 'knowledge/create.html', context)


@login_required
def kb_edit(request, slug):
    """Edit a knowledge article - only for author, Level 2+ agents, and admins"""
    article = get_object_or_404(KnowledgeArticle, slug=slug)

    # Check permissions
    if request.user.role == 'customer':
        return HttpResponseForbidden('Keine Berechtigung')

    if request.user.role == 'support_agent':
        # Must be author or Level 2+
        if article.author != request.user and (not request.user.support_level or request.user.support_level < 2):
            messages.error(request, 'Sie können nur Ihre eigenen Artikel bearbeiten oder benötigen Level 2+.')
            return redirect('knowledge:detail', slug=slug)

    if request.method == 'POST':
        article.title = request.POST.get('title')
        article.content = request.POST.get('content')
        article.excerpt = request.POST.get('excerpt', '')
        article.keywords = request.POST.get('keywords', '')
        article.is_public = request.POST.get('is_public') == 'on'
        article.is_featured = request.POST.get('is_featured') == 'on'
        article.status = request.POST.get('status', 'draft')

        category_id = request.POST.get('category')
        article.category_id = category_id if category_id else None

        article.save()

        messages.success(request, f'Artikel "{article.title}" wurde aktualisiert!')
        return redirect('knowledge:detail', slug=article.slug)

    categories = Category.objects.filter(is_active=True)
    context = {
        'article': article,
        'categories': categories
    }
    return render(request, 'knowledge/edit.html', context)
