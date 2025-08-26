from datetime import datetime
from app import db
from sqlalchemy import Text

class KnowledgeArticle(db.Model):
    __tablename__ = 'knowledge_articles'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(Text, nullable=False)
    summary = db.Column(db.String(500))
    slug = db.Column(db.String(250), unique=True, nullable=False, index=True)
    
    # Categorization
    category_id = db.Column(db.Integer, db.ForeignKey('kb_categories.id'), nullable=True)
    tags = db.Column(db.String(500))  # Comma-separated tags
    
    # Access control
    is_public = db.Column(db.Boolean, default=True)  # Public or internal only
    is_featured = db.Column(db.Boolean, default=False)
    is_published = db.Column(db.Boolean, default=True)
    
    # Authoring
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Metrics
    view_count = db.Column(db.Integer, default=0)
    helpful_votes = db.Column(db.Integer, default=0)
    not_helpful_votes = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime, nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    author = db.relationship('User', foreign_keys=[author_id], backref='authored_articles')
    reviewer = db.relationship('User', foreign_keys=[reviewer_id], backref='reviewed_articles')
    category = db.relationship('KnowledgeCategory', backref='articles')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.slug and self.title:
            self.slug = self.generate_slug(self.title)
    
    def __repr__(self):
        return f'<KnowledgeArticle {self.title}>'
    
    @staticmethod
    def generate_slug(title):
        """Generate URL-friendly slug from title"""
        import re
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')
    
    def increment_view(self):
        """Increment view counter"""
        self.view_count += 1
        db.session.commit()
    
    def vote_helpful(self, helpful=True):
        """Record a helpful/not helpful vote"""
        if helpful:
            self.helpful_votes += 1
        else:
            self.not_helpful_votes += 1
        db.session.commit()
    
    @property
    def helpfulness_ratio(self):
        """Calculate helpfulness ratio (0-1)"""
        total_votes = self.helpful_votes + self.not_helpful_votes
        if total_votes == 0:
            return 0
        return self.helpful_votes / total_votes
    
    @property
    def tag_list(self):
        """Get tags as a list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []
    
    def set_tags(self, tag_list):
        """Set tags from a list"""
        self.tags = ', '.join(tag_list) if tag_list else None
    
    def can_view(self, user):
        """Check if user can view this article"""
        if not self.is_published:
            return user and user.role in ['admin', 'team_leader', 'support_agent']
        
        if not self.is_public:
            return user and user.role in ['admin', 'team_leader', 'support_agent']
        
        return True
    
    def to_dict(self, include_content=False):
        """Convert article to dictionary"""
        data = {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'summary': self.summary,
            'is_public': self.is_public,
            'is_featured': self.is_featured,
            'is_published': self.is_published,
            'view_count': self.view_count,
            'helpful_votes': self.helpful_votes,
            'not_helpful_votes': self.not_helpful_votes,
            'helpfulness_ratio': self.helpfulness_ratio,
            'tags': self.tag_list,
            'category': self.category.to_dict() if self.category else None,
            'author': self.author.to_dict(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'published_at': self.published_at.isoformat() if self.published_at else None
        }
        
        if include_content:
            data['content'] = self.content
            
        return data

class KnowledgeCategory(db.Model):
    __tablename__ = 'kb_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('kb_categories.id'), nullable=True)
    
    # Display options
    color = db.Column(db.String(7), default='#2fb2bf')
    icon = db.Column(db.String(50))  # Font Awesome icon class
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Self-referential relationship for subcategories
    parent = db.relationship('KnowledgeCategory', remote_side=[id], backref='subcategories')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.slug and self.name:
            self.slug = KnowledgeArticle.generate_slug(self.name)
    
    def __repr__(self):
        return f'<KnowledgeCategory {self.name}>'
    
    @property
    def article_count(self):
        """Get count of published articles in this category"""
        return self.articles.filter_by(is_published=True).count()
    
    def to_dict(self, include_articles=False):
        data = {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'color': self.color,
            'icon': self.icon,
            'sort_order': self.sort_order,
            'is_active': self.is_active,
            'article_count': self.article_count,
            'parent_id': self.parent_id
        }
        
        if include_articles:
            data['articles'] = [article.to_dict() for article in self.articles.filter_by(is_published=True)]
            
        return data

class FAQ(db.Model):
    __tablename__ = 'faqs'
    
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False)
    answer = db.Column(Text, nullable=False)
    
    # Categorization
    category_id = db.Column(db.Integer, db.ForeignKey('kb_categories.id'), nullable=True)
    
    # Display and access
    is_featured = db.Column(db.Boolean, default=False)
    is_published = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    
    # Metrics
    view_count = db.Column(db.Integer, default=0)
    helpful_votes = db.Column(db.Integer, default=0)
    not_helpful_votes = db.Column(db.Integer, default=0)
    
    # Authoring
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    author = db.relationship('User', backref='authored_faqs')
    category = db.relationship('KnowledgeCategory', backref='faqs')
    
    def __repr__(self):
        return f'<FAQ {self.question[:50]}...>'
    
    def increment_view(self):
        """Increment view counter"""
        self.view_count += 1
        db.session.commit()
    
    def vote_helpful(self, helpful=True):
        """Record a helpful/not helpful vote"""
        if helpful:
            self.helpful_votes += 1
        else:
            self.not_helpful_votes += 1
        db.session.commit()
    
    @property
    def helpfulness_ratio(self):
        """Calculate helpfulness ratio (0-1)"""
        total_votes = self.helpful_votes + self.not_helpful_votes
        if total_votes == 0:
            return 0
        return self.helpful_votes / total_votes
    
    def to_dict(self):
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'is_featured': self.is_featured,
            'is_published': self.is_published,
            'sort_order': self.sort_order,
            'view_count': self.view_count,
            'helpful_votes': self.helpful_votes,
            'not_helpful_votes': self.not_helpful_votes,
            'helpfulness_ratio': self.helpfulness_ratio,
            'category': self.category.to_dict() if self.category else None,
            'author': self.author.to_dict(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }