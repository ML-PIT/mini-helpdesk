import pytest
import os
import tempfile
from app import create_app, db
from app.models.user import User
from app.models.ticket import Ticket, Category
from app.models.knowledge import KnowledgeArticle, KnowledgeCategory

@pytest.fixture
def app():
    """Create application for testing"""
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app('testing')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        yield app
        
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create CLI test runner"""
    return app.test_cli_runner()

@pytest.fixture
def admin_user(app):
    """Create admin user for testing"""
    with app.app_context():
        user = User(
            username='admin',
            email='admin@test.com',
            first_name='Admin',
            last_name='User',
            role='admin',
            is_active=True
        )
        user.set_password('admin123')
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def agent_user(app):
    """Create support agent for testing"""
    with app.app_context():
        user = User(
            username='agent',
            email='agent@test.com',
            first_name='Support',
            last_name='Agent',
            role='support_agent',
            is_active=True
        )
        user.set_password('agent123')
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def customer_user(app):
    """Create customer user for testing"""
    with app.app_context():
        user = User(
            username='customer',
            email='customer@test.com',
            first_name='Test',
            last_name='Customer',
            role='customer',
            is_active=True
        )
        user.set_password('customer123')
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def test_category(app):
    """Create test category"""
    with app.app_context():
        category = Category(
            name='Technical Support',
            description='Technical issues and questions',
            color='#2fb2bf'
        )
        db.session.add(category)
        db.session.commit()
        return category

@pytest.fixture
def test_ticket(app, customer_user, test_category):
    """Create test ticket"""
    with app.app_context():
        ticket = Ticket(
            title='Test Ticket',
            description='This is a test ticket for automated testing',
            priority='medium',
            created_by=customer_user.id,
            category_id=test_category.id
        )
        ticket.set_priority_based_sla()
        db.session.add(ticket)
        db.session.commit()
        return ticket

@pytest.fixture
def kb_category(app):
    """Create knowledge base category"""
    with app.app_context():
        category = KnowledgeCategory(
            name='Getting Started',
            description='Basic guides for new users',
            slug='getting-started'
        )
        db.session.add(category)
        db.session.commit()
        return category

@pytest.fixture
def kb_article(app, admin_user, kb_category):
    """Create knowledge base article"""
    with app.app_context():
        article = KnowledgeArticle(
            title='How to Create a Ticket',
            content='# How to Create a Ticket\n\n1. Click on "New Ticket"\n2. Fill out the form\n3. Submit',
            summary='Learn how to create a support ticket',
            author_id=admin_user.id,
            category_id=kb_category.id,
            is_published=True,
            is_public=True
        )
        db.session.add(article)
        db.session.commit()
        return article