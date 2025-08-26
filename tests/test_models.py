import pytest
from datetime import datetime, timedelta
from app import db
from app.models.user import User
from app.models.ticket import Ticket, TicketComment, Category
from app.models.knowledge import KnowledgeArticle
from app.models.audit import AuditLog

class TestUserModel:
    def test_create_user(self, app):
        """Test user creation"""
        with app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                first_name='Test',
                last_name='User',
                role='customer'
            )
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            assert user.id is not None
            assert user.username == 'testuser'
            assert user.check_password('password123')
            assert not user.check_password('wrongpassword')

    def test_user_roles_and_permissions(self, app):
        """Test user role-based permissions"""
        with app.app_context():
            admin = User(username='admin', email='admin@test.com', role='admin')
            agent = User(username='agent', email='agent@test.com', role='support_agent')
            customer = User(username='customer', email='customer@test.com', role='customer')
            
            # Admin permissions
            assert admin.has_permission('all')
            assert admin.has_permission('manage_users')
            
            # Agent permissions
            assert agent.has_permission('view_assigned_tickets')
            assert agent.has_permission('update_tickets')
            assert not agent.has_permission('all')
            
            # Customer permissions
            assert customer.has_permission('view_own_tickets')
            assert customer.has_permission('create_tickets')
            assert not customer.has_permission('view_assigned_tickets')

    def test_user_full_name_property(self, app, customer_user):
        """Test full name property"""
        with app.app_context():
            assert customer_user.full_name == 'Test Customer'

class TestTicketModel:
    def test_create_ticket(self, app, customer_user, test_category):
        """Test ticket creation"""
        with app.app_context():
            ticket = Ticket(
                title='Test Ticket',
                description='Test description',
                priority='high',
                created_by=customer_user.id,
                category_id=test_category.id
            )
            
            db.session.add(ticket)
            db.session.commit()
            
            assert ticket.id is not None
            assert ticket.ticket_number is not None
            assert ticket.ticket_number.startswith('TK-')
            assert ticket.status == 'open'
            assert ticket.creator == customer_user
            assert ticket.category == test_category

    def test_ticket_sla_calculation(self, app, test_ticket):
        """Test SLA due date calculation"""
        with app.app_context():
            # Medium priority should have 72 hours SLA
            expected_sla = test_ticket.created_at + timedelta(hours=72)
            assert abs((test_ticket.sla_due_date - expected_sla).total_seconds()) < 60
            
            # Test SLA breach detection
            test_ticket.sla_due_date = datetime.utcnow() - timedelta(hours=1)
            assert test_ticket.check_sla_breach() == True
            assert test_ticket.sla_breached == True

    def test_ticket_comments(self, app, test_ticket, agent_user):
        """Test ticket comment system"""
        with app.app_context():
            comment = test_ticket.add_comment(
                author_id=agent_user.id,
                content='This is a test comment',
                is_internal=False
            )
            
            db.session.commit()
            
            assert comment.id is not None
            assert comment.content == 'This is a test comment'
            assert comment.author == agent_user
            assert test_ticket.comments.count() == 1

    def test_ticket_response_time(self, app, test_ticket, agent_user):
        """Test first response time tracking"""
        with app.app_context():
            # Initially no first response
            assert test_ticket.first_response_at is None
            assert test_ticket.get_response_time() is None
            
            # Add agent comment (should set first response time)
            test_ticket.add_comment(
                author_id=agent_user.id,
                content='Agent response',
                is_internal=False
            )
            
            db.session.commit()
            
            assert test_ticket.first_response_at is not None
            assert test_ticket.get_response_time() is not None
            assert test_ticket.get_response_time() > 0

    def test_ticket_to_dict(self, app, test_ticket):
        """Test ticket serialization"""
        with app.app_context():
            ticket_dict = test_ticket.to_dict()
            
            assert 'id' in ticket_dict
            assert 'ticket_number' in ticket_dict
            assert 'title' in ticket_dict
            assert 'status' in ticket_dict
            assert 'priority' in ticket_dict
            assert 'creator' in ticket_dict
            assert ticket_dict['title'] == test_ticket.title
            
            # Test detailed version
            detailed_dict = test_ticket.to_dict(include_details=True)
            assert 'description' in detailed_dict
            assert 'comments' in detailed_dict

class TestCategoryModel:
    def test_create_category(self, app):
        """Test category creation"""
        with app.app_context():
            category = Category(
                name='Bug Reports',
                description='Software bugs and issues',
                color='#ff0000'
            )
            
            db.session.add(category)
            db.session.commit()
            
            assert category.id is not None
            assert category.name == 'Bug Reports'
            assert category.is_active == True

    def test_category_auto_assignment(self, app, agent_user):
        """Test category auto-assignment"""
        with app.app_context():
            category = Category(
                name='VIP Support',
                auto_assign_to=agent_user.id
            )
            
            db.session.add(category)
            db.session.commit()
            
            assert category.assignee == agent_user

class TestKnowledgeModel:
    def test_create_article(self, app, admin_user, kb_category):
        """Test knowledge article creation"""
        with app.app_context():
            article = KnowledgeArticle(
                title='Test Article',
                content='# Test Content\n\nThis is test content',
                summary='Test summary',
                author_id=admin_user.id,
                category_id=kb_category.id
            )
            
            db.session.add(article)
            db.session.commit()
            
            assert article.id is not None
            assert article.slug is not None
            assert 'test-article' in article.slug
            assert article.author == admin_user

    def test_article_view_tracking(self, app, kb_article):
        """Test article view count tracking"""
        with app.app_context():
            initial_count = kb_article.view_count
            
            kb_article.increment_view()
            
            assert kb_article.view_count == initial_count + 1

    def test_article_helpfulness_voting(self, app, kb_article):
        """Test article helpfulness voting"""
        with app.app_context():
            assert kb_article.helpful_votes == 0
            assert kb_article.not_helpful_votes == 0
            assert kb_article.helpfulness_ratio == 0
            
            kb_article.vote_helpful(True)
            kb_article.vote_helpful(True)
            kb_article.vote_helpful(False)
            
            assert kb_article.helpful_votes == 2
            assert kb_article.not_helpful_votes == 1
            assert kb_article.helpfulness_ratio == 2/3

    def test_article_visibility(self, app, kb_article, customer_user, admin_user):
        """Test article visibility rules"""
        with app.app_context():
            # Public published article - everyone can view
            assert kb_article.can_view(customer_user) == True
            assert kb_article.can_view(admin_user) == True
            
            # Private article - only staff can view
            kb_article.is_public = False
            db.session.commit()
            
            assert kb_article.can_view(customer_user) == False
            assert kb_article.can_view(admin_user) == True
            
            # Unpublished article - only staff can view
            kb_article.is_public = True
            kb_article.is_published = False
            db.session.commit()
            
            assert kb_article.can_view(customer_user) == False
            assert kb_article.can_view(admin_user) == True

class TestAuditModel:
    def test_create_audit_log(self, app, admin_user, test_ticket):
        """Test audit log creation"""
        with app.app_context():
            audit_log = AuditLog.log_ticket_action(
                user_id=admin_user.id,
                ticket=test_ticket,
                action='update',
                old_values={'status': 'open'},
                new_values={'status': 'in_progress'},
                description='Status changed'
            )
            
            db.session.commit()
            
            assert audit_log.id is not None
            assert audit_log.user == admin_user
            assert audit_log.ticket == test_ticket
            assert audit_log.action == 'update'
            assert audit_log.entity_type == 'ticket'

    def test_audit_log_changes_tracking(self, app, admin_user, test_ticket):
        """Test changes tracking in audit logs"""
        with app.app_context():
            old_values = {'status': 'open', 'priority': 'medium'}
            new_values = {'status': 'in_progress', 'priority': 'high'}
            
            audit_log = AuditLog.log_ticket_action(
                user_id=admin_user.id,
                ticket=test_ticket,
                action='update',
                old_values=old_values,
                new_values=new_values
            )
            
            db.session.commit()
            
            changes = audit_log.get_changes()
            assert 'status' in changes
            assert 'priority' in changes
            assert changes['status']['from'] == 'open'
            assert changes['status']['to'] == 'in_progress'
            assert changes['priority']['from'] == 'medium'
            assert changes['priority']['to'] == 'high'