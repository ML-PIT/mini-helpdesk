# ML Gruppe Helpdesk - API Documentation

## Overview

The ML Gruppe Helpdesk provides a comprehensive REST API for managing tickets, users, and knowledge base content. The API uses JWT authentication and follows RESTful principles.

**Base URL**: `https://helpdesk.mlgruppe.de/api/v1`

## Authentication

### JWT Token Authentication

The API uses JWT (JSON Web Tokens) for authentication. Obtain a token by authenticating with your credentials.

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@mlgruppe.de",
  "password": "your_password"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "user@mlgruppe.de",
    "role": "customer",
    "first_name": "John",
    "last_name": "Doe"
  },
  "expires_in": 3600
}
```

#### Using the Token

Include the token in the Authorization header for all authenticated requests:

```http
Authorization: Bearer <your_token_here>
```

#### Refresh Token
```http
POST /auth/refresh
Authorization: Bearer <refresh_token>
```

#### Get Current User
```http
GET /auth/me
Authorization: Bearer <access_token>
```

## Rate Limiting

The API implements rate limiting to ensure fair usage:

- **API Endpoints**: 10 requests per second
- **Authentication**: 5 requests per minute
- **Customer Users**: 50 requests per hour
- **Agent/Admin Users**: 100 requests per hour

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Request limit per window
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Window reset time (Unix timestamp)

## Error Handling

The API uses conventional HTTP response codes and returns JSON error objects:

```json
{
  "error": "Error message describing what went wrong",
  "code": "ERROR_CODE",
  "details": {
    "field": "Additional error details"
  }
}
```

### HTTP Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `429` - Rate Limited
- `500` - Internal Server Error

## Tickets API

### List Tickets

```http
GET /tickets?page=1&per_page=20&status=open&priority=high&search=query
Authorization: Bearer <token>
```

**Query Parameters:**
- `page` (integer): Page number (default: 1)
- `per_page` (integer): Items per page (max: 100, default: 20)
- `status` (string): Filter by status (`open`, `in_progress`, `pending`, `resolved`, `closed`)
- `priority` (string): Filter by priority (`low`, `medium`, `high`, `critical`)
- `category_id` (integer): Filter by category ID
- `assigned_to` (integer): Filter by assigned agent ID
- `search` (string): Search in title, description, and ticket number
- `sort_by` (string): Sort field (`created_at`, `updated_at`, `priority`, `status`)
- `sort_order` (string): Sort order (`asc`, `desc`)

**Response:**
```json
{
  "tickets": [
    {
      "id": 1,
      "ticket_number": "TK-2024-10001",
      "title": "Cannot access email",
      "status": "open",
      "priority": "high",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z",
      "creator": {
        "id": 2,
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@mlgruppe.de"
      },
      "assignee": null,
      "category": "Technical Support",
      "sla_due_date": "2024-01-16T10:30:00Z",
      "sla_breached": false
    }
  ],
  "pagination": {
    "page": 1,
    "pages": 5,
    "per_page": 20,
    "total": 95,
    "has_next": true,
    "has_prev": false
  }
}
```

### Get Single Ticket

```http
GET /tickets/{ticket_id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "ticket": {
    "id": 1,
    "ticket_number": "TK-2024-10001",
    "title": "Cannot access email",
    "description": "I cannot access my email account since this morning...",
    "status": "open",
    "priority": "high",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "first_response_at": null,
    "resolved_at": null,
    "rating": null,
    "feedback": null,
    "creator": { ... },
    "assignee": null,
    "category": "Technical Support",
    "sla_due_date": "2024-01-16T10:30:00Z",
    "sla_breached": false,
    "comments": [
      {
        "id": 1,
        "content": "We're looking into this issue.",
        "is_internal": false,
        "author": { ... },
        "created_at": "2024-01-15T11:00:00Z"
      }
    ],
    "attachments": [
      {
        "id": 1,
        "filename": "screenshot.png",
        "content_type": "image/png",
        "size": 1024576,
        "uploaded_by": { ... },
        "uploaded_at": "2024-01-15T10:30:00Z"
      }
    ]
  }
}
```

### Create Ticket

```http
POST /tickets
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Cannot access email",
  "description": "Detailed description of the issue...",
  "priority": "high",
  "category_id": 1
}
```

**Response:**
```json
{
  "message": "Ticket created successfully",
  "ticket": { ... }
}
```

### Update Ticket (Agents/Admins only)

```http
PUT /tickets/{ticket_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "status": "in_progress",
  "priority": "medium",
  "assigned_to": 3,
  "category_id": 2
}
```

### Ticket Comments

#### Get Comments

```http
GET /tickets/{ticket_id}/comments
Authorization: Bearer <token>
```

#### Add Comment

```http
POST /tickets/{ticket_id}/comments
Authorization: Bearer <token>
Content-Type: application/json

{
  "content": "Thank you for contacting support. We're investigating this issue.",
  "is_internal": false
}
```

### Ticket Attachments

#### Add Attachment

```http
POST /tickets/{ticket_id}/attachments
Authorization: Bearer <token>
Content-Type: application/json

{
  "filename": "error_log.txt",
  "content": "base64_encoded_file_content",
  "content_type": "text/plain"
}
```

## Categories API

### List Categories

```http
GET /categories
Authorization: Bearer <token>
```

**Response:**
```json
{
  "categories": [
    {
      "id": 1,
      "name": "Technical Support",
      "description": "Hardware and software issues",
      "color": "#2fb2bf",
      "is_active": true,
      "auto_assign_to": {
        "id": 3,
        "first_name": "Support",
        "last_name": "Agent"
      }
    }
  ]
}
```

## Knowledge Base API

### List Articles

```http
GET /kb/articles?page=1&search=password&category_id=1
Authorization: Bearer <token>
```

**Query Parameters:**
- `page` (integer): Page number
- `per_page` (integer): Items per page
- `search` (string): Search in title, content, and tags
- `category_id` (integer): Filter by category

**Response:**
```json
{
  "articles": [
    {
      "id": 1,
      "title": "How to Reset Your Password",
      "slug": "how-to-reset-your-password",
      "summary": "Step-by-step guide to reset your account password",
      "is_public": true,
      "is_featured": true,
      "view_count": 150,
      "helpful_votes": 25,
      "not_helpful_votes": 3,
      "helpfulness_ratio": 0.89,
      "tags": ["password", "account", "security"],
      "category": {
        "id": 1,
        "name": "Account Management",
        "slug": "account-management"
      },
      "author": { ... },
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-10T15:30:00Z"
    }
  ],
  "pagination": { ... }
}
```

### Get Single Article

```http
GET /kb/articles/{article_id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "article": {
    "id": 1,
    "title": "How to Reset Your Password",
    "content": "# How to Reset Your Password\n\n1. Go to login page...",
    "slug": "how-to-reset-your-password",
    "summary": "Step-by-step guide...",
    // ... other fields
  }
}
```

## Analytics API (Admin/Team Leader only)

### SLA Metrics

```http
GET /analytics/sla?days=30
Authorization: Bearer <token>
```

**Response:**
```json
{
  "metrics": {
    "total_tickets": 150,
    "on_time": 135,
    "breached": 15,
    "sla_compliance_rate": 90.0,
    "avg_resolution_time": 18.5,
    "avg_first_response_time": 2.3
  }
}
```

### Agent Performance

```http
GET /analytics/agent/{agent_id}/sla?days=30
Authorization: Bearer <token>
```

**Response:**
```json
{
  "performance": {
    "agent_id": 3,
    "total_tickets": 45,
    "on_time": 42,
    "breached": 3,
    "sla_compliance_rate": 93.33,
    "avg_resolution_time": 16.2,
    "avg_first_response_time": 1.8
  }
}
```

## Dashboard API

### Dashboard Statistics

```http
GET /dashboard/stats
Authorization: Bearer <token>
```

**Response (Customer):**
```json
{
  "stats": {
    "my_tickets": 5,
    "open_tickets": 2,
    "resolved_tickets": 3
  }
}
```

**Response (Agent/Admin):**
```json
{
  "stats": {
    "total_tickets": 150,
    "open_tickets": 45,
    "in_progress_tickets": 32,
    "pending_tickets": 8,
    "resolved_today": 12,
    "sla_breached": 5,
    "my_assigned": 15
  }
}
```

## Webhook Integration

### Microsoft Teams Notifications

Configure Teams webhook URL in environment variables. The system automatically sends notifications for:

- New ticket creation
- Ticket status changes
- SLA breaches
- High priority tickets

**Example Teams Card:**
```json
{
  "@type": "MessageCard",
  "@context": "http://schema.org/extensions",
  "summary": "New High Priority Ticket",
  "themeColor": "ff0000",
  "sections": [{
    "activityTitle": "New Ticket: TK-2024-10001",
    "activitySubtitle": "Cannot access email",
    "facts": [
      {"name": "Priority", "value": "High"},
      {"name": "Created By", "value": "John Doe"},
      {"name": "Category", "value": "Technical Support"}
    ]
  }],
  "potentialAction": [{
    "@type": "OpenUri",
    "name": "View Ticket",
    "targets": [{
      "os": "default",
      "uri": "https://helpdesk.mlgruppe.de/tickets/1"
    }]
  }]
}
```

## SDK Examples

### JavaScript/Node.js

```javascript
class HelpdeskAPI {
  constructor(baseUrl, accessToken) {
    this.baseUrl = baseUrl;
    this.accessToken = accessToken;
  }

  async request(method, endpoint, data = null) {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = {
      'Authorization': `Bearer ${this.accessToken}`,
      'Content-Type': 'application/json'
    };

    const response = await fetch(url, {
      method,
      headers,
      body: data ? JSON.stringify(data) : null
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    return response.json();
  }

  // Authenticate user
  static async login(baseUrl, email, password) {
    const response = await fetch(`${baseUrl}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    
    return response.json();
  }

  // Get tickets
  async getTickets(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request('GET', `/tickets?${query}`);
  }

  // Create ticket
  async createTicket(ticketData) {
    return this.request('POST', '/tickets', ticketData);
  }

  // Add comment
  async addComment(ticketId, content, isInternal = false) {
    return this.request('POST', `/tickets/${ticketId}/comments`, {
      content,
      is_internal: isInternal
    });
  }
}

// Usage
const api = new HelpdeskAPI('https://helpdesk.mlgruppe.de/api/v1', 'your_token');
const tickets = await api.getTickets({ status: 'open', page: 1 });
```

### Python

```python
import requests
from typing import Dict, Any, Optional

class HelpdeskAPI:
    def __init__(self, base_url: str, access_token: str):
        self.base_url = base_url
        self.access_token = access_token
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        })

    @classmethod
    def login(cls, base_url: str, email: str, password: str) -> Dict[str, Any]:
        """Authenticate and get tokens"""
        response = requests.post(
            f'{base_url}/auth/login',
            json={'email': email, 'password': password}
        )
        response.raise_for_status()
        return response.json()

    def get_tickets(self, **params) -> Dict[str, Any]:
        """Get tickets with optional filters"""
        response = self.session.get(f'{self.base_url}/tickets', params=params)
        response.raise_for_status()
        return response.json()

    def create_ticket(self, title: str, description: str, 
                     priority: str = 'medium', category_id: Optional[int] = None) -> Dict[str, Any]:
        """Create a new ticket"""
        data = {
            'title': title,
            'description': description,
            'priority': priority
        }
        if category_id:
            data['category_id'] = category_id
            
        response = self.session.post(f'{self.base_url}/tickets', json=data)
        response.raise_for_status()
        return response.json()

    def add_comment(self, ticket_id: int, content: str, is_internal: bool = False) -> Dict[str, Any]:
        """Add comment to ticket"""
        data = {
            'content': content,
            'is_internal': is_internal
        }
        response = self.session.post(f'{self.base_url}/tickets/{ticket_id}/comments', json=data)
        response.raise_for_status()
        return response.json()

# Usage
api = HelpdeskAPI('https://helpdesk.mlgruppe.de/api/v1', 'your_token')
tickets = api.get_tickets(status='open', priority='high')
```

## Postman Collection

A Postman collection is available for testing the API. Import the collection using this URL:

```
https://helpdesk.mlgruppe.de/api/docs/postman.json
```

The collection includes:
- Pre-configured authentication
- All API endpoints
- Example requests and responses
- Test scripts for validation

## OpenAPI/Swagger Documentation

Interactive API documentation is available at:

```
https://helpdesk.mlgruppe.de/api/docs
```

The OpenAPI specification can be downloaded at:

```
https://helpdesk.mlgruppe.de/api/openapi.json
```

## Mobile App Integration

The API is designed to support mobile applications with:

- JWT token-based authentication
- Optimized endpoints for mobile data usage
- Push notification support (via webhooks)
- Offline-first data synchronization patterns

### Recommended Mobile Architecture

1. **Authentication**: Store JWT tokens securely
2. **Caching**: Cache frequently accessed data locally
3. **Sync**: Implement background sync for tickets and comments
4. **Push Notifications**: Use Teams webhooks or custom notification service
5. **Offline Support**: Queue actions when offline, sync when online

## Troubleshooting

### Common Issues

1. **401 Unauthorized**
   - Check if token is expired
   - Verify token format in Authorization header
   - Ensure user account is active

2. **403 Forbidden**
   - Check user role permissions
   - Verify access to specific ticket/resource
   - Review role-based access controls

3. **429 Rate Limited**
   - Implement exponential backoff
   - Check rate limit headers
   - Consider upgrading user role for higher limits

4. **422 Validation Error**
   - Check required fields
   - Verify data types and formats
   - Review field length limits

### Rate Limiting Best Practices

1. **Respect Limits**: Check rate limit headers in responses
2. **Implement Backoff**: Use exponential backoff when rate limited
3. **Cache Data**: Cache frequently accessed data locally
4. **Batch Operations**: Group multiple operations when possible

### Support

For API support and questions:
- Email: api-support@mlgruppe.de
- Documentation: https://docs.mlgruppe.de/helpdesk/api
- Issues: https://github.com/mlgruppe/helpdesk/issues