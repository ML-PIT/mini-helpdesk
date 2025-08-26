import pytest
import json
from app import db
from app.models.user import User

class TestAPIAuth:
    def test_api_login_success(self, client, customer_user):
        """Test successful API login"""
        response = client.post('/api/v1/auth/login', 
                              json={
                                  'email': 'customer@test.com',
                                  'password': 'customer123'
                              })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert 'user' in data
        assert data['user']['email'] == 'customer@test.com'

    def test_api_login_failure(self, client):
        """Test failed API login"""
        response = client.post('/api/v1/auth/login',
                              json={
                                  'email': 'nonexistent@test.com',
                                  'password': 'wrongpassword'
                              })
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data

    def test_api_login_missing_fields(self, client):
        """Test API login with missing fields"""
        response = client.post('/api/v1/auth/login',
                              json={'email': 'test@test.com'})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_protected_endpoint_without_token(self, client):
        """Test accessing protected endpoint without token"""
        response = client.get('/api/v1/tickets')
        
        assert response.status_code == 401

    def test_protected_endpoint_with_token(self, client, customer_user):
        """Test accessing protected endpoint with valid token"""
        # Get token
        login_response = client.post('/api/v1/auth/login',
                                   json={
                                       'email': 'customer@test.com',
                                       'password': 'customer123'
                                   })
        
        token = json.loads(login_response.data)['access_token']
        
        # Use token to access protected endpoint
        response = client.get('/api/v1/tickets',
                             headers={'Authorization': f'Bearer {token}'})
        
        assert response.status_code == 200

class TestAPITickets:
    def get_auth_headers(self, client, user_email, password):
        """Helper to get authorization headers"""
        response = client.post('/api/v1/auth/login',
                              json={'email': user_email, 'password': password})
        token = json.loads(response.data)['access_token']
        return {'Authorization': f'Bearer {token}'}

    def test_get_tickets_customer(self, client, customer_user, test_ticket):
        """Test customer can only see their own tickets"""
        headers = self.get_auth_headers(client, 'customer@test.com', 'customer123')
        
        response = client.get('/api/v1/tickets', headers=headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'tickets' in data
        assert len(data['tickets']) == 1
        assert data['tickets'][0]['creator']['id'] == customer_user.id

    def test_get_tickets_agent(self, client, agent_user, test_ticket):
        """Test agent can see all tickets"""
        headers = self.get_auth_headers(client, 'agent@test.com', 'agent123')
        
        response = client.get('/api/v1/tickets', headers=headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'tickets' in data

    def test_create_ticket_success(self, client, customer_user, test_category):
        """Test successful ticket creation"""
        headers = self.get_auth_headers(client, 'customer@test.com', 'customer123')
        
        ticket_data = {
            'title': 'API Test Ticket',
            'description': 'This ticket was created via API for testing',
            'priority': 'high',
            'category_id': test_category.id
        }
        
        response = client.post('/api/v1/tickets', 
                              json=ticket_data, 
                              headers=headers)
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'ticket' in data
        assert data['ticket']['title'] == 'API Test Ticket'
        assert data['ticket']['priority'] == 'high'

    def test_create_ticket_missing_fields(self, client, customer_user):
        """Test ticket creation with missing required fields"""
        headers = self.get_auth_headers(client, 'customer@test.com', 'customer123')
        
        response = client.post('/api/v1/tickets',
                              json={'title': 'Incomplete Ticket'},
                              headers=headers)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_get_single_ticket_success(self, client, customer_user, test_ticket):
        """Test getting single ticket details"""
        headers = self.get_auth_headers(client, 'customer@test.com', 'customer123')
        
        response = client.get(f'/api/v1/tickets/{test_ticket.id}', headers=headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'ticket' in data
        assert data['ticket']['id'] == test_ticket.id
        assert 'description' in data['ticket']  # Should include details

    def test_get_single_ticket_access_denied(self, client, customer_user, agent_user, test_ticket):
        """Test access denied for ticket not owned by customer"""
        # Create another user
        with client.application.app_context():
            other_user = User(
                username='other',
                email='other@test.com',
                first_name='Other',
                last_name='User',
                role='customer'
            )
            other_user.set_password('other123')
            db.session.add(other_user)
            db.session.commit()
        
        headers = self.get_auth_headers(client, 'other@test.com', 'other123')
        
        response = client.get(f'/api/v1/tickets/{test_ticket.id}', headers=headers)
        
        assert response.status_code == 403

    def test_update_ticket_agent(self, client, agent_user, test_ticket):
        """Test agent can update tickets"""
        headers = self.get_auth_headers(client, 'agent@test.com', 'agent123')
        
        update_data = {
            'status': 'in_progress',
            'priority': 'high'
        }
        
        response = client.put(f'/api/v1/tickets/{test_ticket.id}',
                             json=update_data,
                             headers=headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['ticket']['status'] == 'in_progress'
        assert data['ticket']['priority'] == 'high'

    def test_update_ticket_customer_denied(self, client, customer_user, test_ticket):
        """Test customers cannot update ticket status"""
        headers = self.get_auth_headers(client, 'customer@test.com', 'customer123')
        
        response = client.put(f'/api/v1/tickets/{test_ticket.id}',
                             json={'status': 'resolved'},
                             headers=headers)
        
        assert response.status_code == 403

class TestAPIComments:
    def get_auth_headers(self, client, user_email, password):
        """Helper to get authorization headers"""
        response = client.post('/api/v1/auth/login',
                              json={'email': user_email, 'password': password})
        token = json.loads(response.data)['access_token']
        return {'Authorization': f'Bearer {token}'}

    def test_add_comment_customer(self, client, customer_user, test_ticket):
        """Test customer can add comments to their tickets"""
        headers = self.get_auth_headers(client, 'customer@test.com', 'customer123')
        
        comment_data = {
            'content': 'This is a customer comment via API'
        }
        
        response = client.post(f'/api/v1/tickets/{test_ticket.id}/comments',
                              json=comment_data,
                              headers=headers)
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'comment' in data
        assert data['comment']['content'] == 'This is a customer comment via API'
        assert data['comment']['is_internal'] == False

    def test_add_internal_comment_agent(self, client, agent_user, test_ticket):
        """Test agent can add internal comments"""
        headers = self.get_auth_headers(client, 'agent@test.com', 'agent123')
        
        comment_data = {
            'content': 'This is an internal agent comment',
            'is_internal': True
        }
        
        response = client.post(f'/api/v1/tickets/{test_ticket.id}/comments',
                              json=comment_data,
                              headers=headers)
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['comment']['is_internal'] == True

    def test_get_comments_filters_internal_for_customers(self, client, customer_user, agent_user, test_ticket):
        """Test that customers don't see internal comments"""
        # Add internal comment as agent
        agent_headers = self.get_auth_headers(client, 'agent@test.com', 'agent123')
        client.post(f'/api/v1/tickets/{test_ticket.id}/comments',
                   json={'content': 'Internal comment', 'is_internal': True},
                   headers=agent_headers)
        
        # Add public comment as customer
        customer_headers = self.get_auth_headers(client, 'customer@test.com', 'customer123')
        client.post(f'/api/v1/tickets/{test_ticket.id}/comments',
                   json={'content': 'Customer comment'},
                   headers=customer_headers)
        
        # Get comments as customer
        response = client.get(f'/api/v1/tickets/{test_ticket.id}/comments',
                             headers=customer_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Should only see non-internal comments
        visible_comments = [c for c in data['comments'] if not c['is_internal']]
        internal_comments = [c for c in data['comments'] if c['is_internal']]
        
        assert len(visible_comments) == 1
        assert len(internal_comments) == 0

class TestAPICategories:
    def get_auth_headers(self, client, user_email, password):
        """Helper to get authorization headers"""
        response = client.post('/api/v1/auth/login',
                              json={'email': user_email, 'password': password})
        token = json.loads(response.data)['access_token']
        return {'Authorization': f'Bearer {token}'}

    def test_get_categories(self, client, customer_user, test_category):
        """Test getting categories list"""
        headers = self.get_auth_headers(client, 'customer@test.com', 'customer123')
        
        response = client.get('/api/v1/categories', headers=headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'categories' in data
        assert len(data['categories']) == 1
        assert data['categories'][0]['name'] == 'Technical Support'

class TestAPIKnowledgeBase:
    def get_auth_headers(self, client, user_email, password):
        """Helper to get authorization headers"""
        response = client.post('/api/v1/auth/login',
                              json={'email': user_email, 'password': password})
        token = json.loads(response.data)['access_token']
        return {'Authorization': f'Bearer {token}'}

    def test_get_public_articles(self, client, customer_user, kb_article):
        """Test getting public knowledge base articles"""
        headers = self.get_auth_headers(client, 'customer@test.com', 'customer123')
        
        response = client.get('/api/v1/kb/articles', headers=headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'articles' in data
        assert len(data['articles']) == 1

    def test_get_single_article(self, client, customer_user, kb_article):
        """Test getting single knowledge article"""
        headers = self.get_auth_headers(client, 'customer@test.com', 'customer123')
        
        response = client.get(f'/api/v1/kb/articles/{kb_article.id}', headers=headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'article' in data
        assert 'content' in data['article']  # Should include full content
        assert data['article']['view_count'] > 0  # Should increment view count

class TestAPIDashboard:
    def get_auth_headers(self, client, user_email, password):
        """Helper to get authorization headers"""
        response = client.post('/api/v1/auth/login',
                              json={'email': user_email, 'password': password})
        token = json.loads(response.data)['access_token']
        return {'Authorization': f'Bearer {token}'}

    def test_dashboard_stats_customer(self, client, customer_user, test_ticket):
        """Test customer dashboard stats"""
        headers = self.get_auth_headers(client, 'customer@test.com', 'customer123')
        
        response = client.get('/api/v1/dashboard/stats', headers=headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'stats' in data
        assert 'my_tickets' in data['stats']
        assert data['stats']['my_tickets'] == 1

    def test_dashboard_stats_agent(self, client, agent_user):
        """Test agent dashboard stats"""
        headers = self.get_auth_headers(client, 'agent@test.com', 'agent123')
        
        response = client.get('/api/v1/dashboard/stats', headers=headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'stats' in data
        assert 'total_tickets' in data['stats']