from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_required
from app.knowledge import bp
from app.models.knowledge import KnowledgeArticle, KnowledgeCategory, FAQ
from app.models.user import User
from app.models.audit import AuditLog
from app import db
from app.utils.decorators import role_required, agent_or_admin_required
from app.knowledge.forms import ArticleForm, CategoryForm, FAQForm

@bp.route('/')
def public_knowledge():
    """Public knowledge base"""
    search = request.args.get('search')
    category_id = request.args.get('category_id', type=int)
    
    query = KnowledgeArticle.query.filter_by(is_published=True, is_public=True)
    
    if search:
        query = query.filter(
            db.or_(
                KnowledgeArticle.title.contains(search),
                KnowledgeArticle.content.contains(search),
                KnowledgeArticle.tags.contains(search)
            )
        )
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    articles = query.order_by(
        KnowledgeArticle.is_featured.desc(),
        KnowledgeArticle.view_count.desc()
    ).limit(50).all()
    
    categories = KnowledgeCategory.query.filter_by(is_active=True).all()
    featured_faqs = FAQ.query.filter_by(is_published=True, is_featured=True).limit(10).all()
    
    return render_template('knowledge/public.html',
                         articles=articles,
                         categories=categories,
                         featured_faqs=featured_faqs)

@bp.route('/article/<slug>')
def view_article(slug):
    """View knowledge article"""
    article = KnowledgeArticle.query.filter_by(slug=slug).first_or_404()
    
    if not article.can_view(current_user):
        flash('Access denied.', 'error')
        return redirect(url_for('knowledge.public_knowledge'))
    
    # Increment view count
    article.increment_view()
    
    # Get related articles
    related_articles = KnowledgeArticle.query.filter(
        KnowledgeArticle.category_id == article.category_id,
        KnowledgeArticle.id != article.id,
        KnowledgeArticle.is_published == True
    ).limit(5).all()
    
    return render_template('knowledge/article.html',
                         article=article,
                         related_articles=related_articles)

@bp.route('/faq')
def faq():
    """FAQ page"""
    category_id = request.args.get('category_id', type=int)
    
    query = FAQ.query.filter_by(is_published=True)
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    faqs = query.order_by(FAQ.is_featured.desc(), FAQ.sort_order.asc()).all()
    categories = KnowledgeCategory.query.filter_by(is_active=True).all()
    
    return render_template('knowledge/faq.html', faqs=faqs, categories=categories)

@bp.route('/manage')
@login_required
@agent_or_admin_required
def manage_articles():
    """Manage knowledge articles"""
    articles = KnowledgeArticle.query.order_by(
        KnowledgeArticle.updated_at.desc()
    ).limit(50).all()
    
    return render_template('knowledge/manage.html', articles=articles)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
@agent_or_admin_required
def create_article():
    """Create new knowledge article"""
    form = ArticleForm()
    
    if form.validate_on_submit():
        article = KnowledgeArticle(
            title=form.title.data,
            content=form.content.data,
            summary=form.summary.data,
            category_id=form.category_id.data if form.category_id.data != 0 else None,
            is_public=form.is_public.data,
            is_featured=form.is_featured.data,
            author_id=current_user.id
        )
        
        if form.tags.data:
            article.set_tags([tag.strip() for tag in form.tags.data.split(',')])
        
        db.session.add(article)
        db.session.commit()
        
        AuditLog.log_action(
            user_id=current_user.id,
            entity_type='knowledge_article',
            entity_id=article.id,
            action='create',
            description=f'Knowledge article "{article.title}" created',
            ip_address=request.remote_addr
        )
        
        flash('Article created successfully!', 'success')
        return redirect(url_for('knowledge.view_article', slug=article.slug))
    
    return render_template('knowledge/create_article.html', form=form)

@bp.route('/article/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@agent_or_admin_required
def edit_article(id):
    """Edit knowledge article"""
    article = KnowledgeArticle.query.get_or_404(id)
    form = ArticleForm(obj=article)
    
    if form.validate_on_submit():
        article.title = form.title.data
        article.content = form.content.data
        article.summary = form.summary.data
        article.category_id = form.category_id.data if form.category_id.data != 0 else None
        article.is_public = form.is_public.data
        article.is_featured = form.is_featured.data
        
        if form.tags.data:
            article.set_tags([tag.strip() for tag in form.tags.data.split(',')])
        
        db.session.commit()
        
        AuditLog.log_action(
            user_id=current_user.id,
            entity_type='knowledge_article',
            entity_id=article.id,
            action='update',
            description=f'Knowledge article "{article.title}" updated',
            ip_address=request.remote_addr
        )
        
        flash('Article updated successfully!', 'success')
        return redirect(url_for('knowledge.view_article', slug=article.slug))
    
    return render_template('knowledge/edit_article.html', form=form, article=article)

@bp.route('/categories')
@login_required
@agent_or_admin_required
def manage_categories():
    """Manage knowledge categories"""
    from app.models.knowledge import KnowledgeCategory
    categories = KnowledgeCategory.query.order_by(KnowledgeCategory.sort_order, KnowledgeCategory.name).all()
    return render_template('knowledge/manage_categories.html', categories=categories)

@bp.route('/faqs')
@login_required
@agent_or_admin_required
def manage_faqs():
    """Manage FAQs"""
    faqs = FAQ.query.order_by(FAQ.sort_order, FAQ.created_at.desc()).all()
    categories = KnowledgeCategory.query.filter_by(is_active=True).all()
    return render_template('knowledge/manage_faqs.html', faqs=faqs, categories=categories)