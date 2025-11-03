# 💻 Entwickler Handbuch
## Aboro-IT Helpdesk System - Technische Dokumentation

![Aboro-IT Logo](https://via.placeholder.com/400x150/FF4444/FFFFFF?text=ABORO-IT)

---

## 📋 Inhaltsverzeichnis

1. [Architektur-Übersicht](#architektur-übersicht)
2. [Installation & Setup](#installation--setup)
3. [Projektstruktur](#projektstruktur)
4. [Live-Chat System](#live-chat-system)
5. [KI-Integration](#ki-integration)
6. [User Management System](#user-management-system)
7. [Ticket System](#ticket-system)
8. [API Dokumentation](#api-dokumentation)
9. [Frontend-Komponenten](#frontend-komponenten)
10. [Deployment](#deployment)
11. [Testing](#testing)
12. [Troubleshooting](#troubleshooting)

---

## 🏗️ Architektur-Übersicht

### Technology Stack
```python
Backend:
- Django 5.0+ 
- Python 3.13+
- SQLite (Development) / PostgreSQL (Production)
- Django REST Framework (API)

Frontend:
- Bootstrap 5.3
- Vanilla JavaScript (ES6+)
- WebSocket (Chat)
- Fetch API (AJAX)

AI Integration:
- Anthropic Claude API
- OpenAI ChatGPT API
- Fallback System

Infrastructure:
- Docker (Optional)
- Nginx (Production)
- Gunicorn (WSGI)
- Systemd (Service Management)
```

### System Components
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │────│   Django App    │────│   Database      │
│   (Browser)     │    │   (Backend)     │    │   (SQLite/PG)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └──────────────│   AI Services   │──────────────┘
                        │  Claude/ChatGPT │
                        └─────────────────┘
```

---

## 🚀 Installation & Setup

### Development Environment

#### 1. Repository klonen
```bash
git clone https://github.com/aboro-it/mini-helpdesk.git
cd mini-helpdesk
```

#### 2. Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

#### 3. Dependencies installieren
```bash
pip install -r requirements.txt
```

#### 4. Environment Variables
```bash
# .env Datei erstellen
cp .env.example .env

# Wichtige Settings:
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///db.sqlite3

# AI API Keys (Optional für Development)
ANTHROPIC_API_KEY=sk-ant-api03-...
OPENAI_API_KEY=sk-...
```

#### 5. Database Setup
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
```

#### 6. Development Server
```bash
python manage.py runserver
# Server läuft auf http://127.0.0.1:8000/
```

### Production Deployment
Siehe [Deployment Section](#deployment)

---

## 📁 Projektstruktur

```
mini-helpdesk/
├── apps/                       # Django Apps
│   ├── accounts/              # Benutzerverwaltung
│   │   ├── models.py         # User Model + Permissions
│   │   ├── views.py          # Auth Views
│   │   ├── forms.py          # Login/Register Forms
│   │   ├── user_management_views.py  # User CRUD
│   │   └── urls.py           # URL Routing
│   ├── admin_panel/          # Admin Funktionen
│   │   ├── models.py         # SystemSettings
│   │   ├── views.py          # Admin Views
│   │   └── license_views.py  # Lizenz Management
│   ├── chat/                 # Live-Chat System
│   │   ├── models.py         # ChatSession, ChatMessage, ChatSettings
│   │   ├── views.py          # Chat API Endpoints
│   │   ├── ai_service.py     # KI-Integration
│   │   └── urls.py           # Chat URLs
│   ├── tickets/              # Ticket System
│   │   ├── models.py         # Ticket, Comment, Category
│   │   ├── views.py          # Ticket CRUD
│   │   └── forms.py          # Ticket Forms
│   ├── knowledge/            # FAQ/Knowledge Base
│   │   ├── models.py         # Article, Category
│   │   ├── views.py          # Article CRUD
│   │   └── search.py         # Search Functionality
│   └── main/                 # Dashboard & Core
│       ├── views.py          # Dashboard Views
│       └── context_processors.py  # Global Context
├── templates/                 # Django Templates
│   ├── base.html            # Base Template mit Chat Widget
│   ├── accounts/            # User Templates
│   ├── chat/                # Chat Templates
│   ├── tickets/             # Ticket Templates
│   └── knowledge/           # FAQ Templates
├── static/                   # Static Files
│   ├── css/                 # Custom CSS
│   ├── js/                  # Custom JavaScript
│   └── images/              # Images
├── tools/                    # Deployment Tools
│   ├── license_generator.py      # Lizenz Generator
│   ├── license_generator_gui.py  # GUI Generator
│   └── requirements.txt      # Tool Dependencies
├── websites/                 # Marketing Websites
│   ├── aboro-it.net/        # Aboro-IT Website
│   └── sleibo.com/          # Sleibo Website
├── helpdesk/                # Django Project Settings
│   ├── settings.py          # Main Settings
│   ├── urls.py              # URL Configuration
│   └── wsgi.py              # WSGI Application
└── manage.py                # Django Management
```

---

## 💬 Live-Chat System

### Models (apps/chat/models.py)

#### ChatSession
```python
class ChatSession(models.Model):
    # Visitor Information
    visitor_name = models.CharField(max_length=100)
    visitor_email = models.EmailField()
    visitor_ip = models.GenericIPAddressField()
    
    # Session details
    session_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    # Assignment
    assigned_agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Status: waiting, active, escalated, ended
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
    
    # Additional info
    initial_message = models.TextField()
    visitor_page_url = models.URLField(null=True, blank=True)
```

#### ChatMessage
```python
class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    
    # Sender information
    is_from_visitor = models.BooleanField(default=True)
    sender_name = models.CharField(max_length=100)
    agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Message type: text, system, file
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text')
```

### API Endpoints (apps/chat/views.py)

#### Widget Integration
```python
# Widget-Daten abrufen
GET /chat/widget-data/
{
  "success": true,
  "widget_data": {
    "session_id": "uuid",
    "available_agents": 0,
    "ai_available": true,
    "is_available": true,
    "widget_color": "#667eea"
  }
}

# Chat starten
POST /chat/api/start/
{
  "session_id": "uuid",
  "name": "Customer Name",
  "email": "customer@example.com", 
  "message": "Initial message",
  "page_url": "https://website.com/page"
}

# Nachricht senden
POST /chat/api/send/
{
  "session_id": "uuid",
  "message": "Customer message"
}

# Nachrichten abrufen
GET /chat/api/messages/{session_id}/
{
  "success": true,
  "messages": [...],
  "session_status": "active"
}
```

#### Agent Endpoints
```python
# Agent Dashboard
GET /chat/dashboard/

# Chat übernehmen
POST /chat/api/take/{session_id}/

# Agent Nachricht
POST /chat/api/agent/send/{session_id}/
{
  "message": "Agent response"
}

# Chat beenden
POST /chat/api/end/{session_id}/
```

### Frontend Integration (templates/base.html)

#### Chat Widget Embedding
```javascript
// Automatisches Widget für eingeloggte Kunden
document.addEventListener('DOMContentLoaded', function() {
    fetch('/chat/widget-data/?customer=true&user_name={{ user.full_name|urlencode }}&user_email={{ user.email|urlencode }}')
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            renderChatWidget(data.widget_data);
        }
    });
});

// Widget rendern
function renderChatWidget(data) {
    // Chat Button + Window HTML generieren
    // Event Handlers binden
    // Polling für neue Nachrichten starten
}
```

---

## 🤖 KI-Integration

### AI Service (apps/chat/ai_service.py)

#### Klassen-Struktur
```python
class AIService:
    def __init__(self):
        self.system_settings = SystemSettings.get_settings()
    
    def is_ai_enabled(self):
        return self.system_settings.ai_enabled
    
    def get_ai_response(self, message, chat_history=None):
        # Fallback-Kette:
        # 1. Primary Provider (Claude/ChatGPT)
        # 2. Secondary Provider (ChatGPT/Claude)  
        # 3. Free AI Response
        # 4. Emergency Response
        
    def _get_claude_response(self, message, chat_history=None):
        # Claude API Integration
        
    def _get_chatgpt_response(self, message, chat_history=None):
        # OpenAI API Integration
        
    def _get_claude_free_response(self, message, chat_history=None):
        # Intelligente Offline-Antworten
        
    def _analyze_conversation_context(self, chat_history):
        # Conversation Memory & Analysis
```

#### Intelligente Features
```python
# Problem-Kategorisierung
problem_keywords = {
    'login': ['passwort', 'password', 'anmelden', 'login'],
    'email': ['email', 'e-mail', 'mail', 'outlook'],
    'performance': ['langsam', 'slow', 'performance', 'hängt'],
    'connection': ['verbindung', 'internet', 'network', 'wifi'],
    'software': ['software', 'programm', 'application'],
    'hardware': ['hardware', 'computer', 'laptop', 'monitor']
}

# User Expertise Detection
technical_terms = ['api', 'server', 'database', 'log', 'cache', 'cookie']
if technical_score >= 3:
    context['user_expertise_level'] = 'advanced'
elif technical_score >= 1:
    context['user_expertise_level'] = 'intermediate'

# Auto-Escalation Triggers
escalation_keywords = [
    'frustriert', 'frustrated', 'hilft nicht', 'doesn\'t help',
    'agent', 'mitarbeiter', 'person', 'human', 'dringend', 'urgent'
]
```

#### API Configuration
```python
# System Settings Model
class SystemSettings(models.Model):
    # AI Configuration
    ai_enabled = models.BooleanField(default=True)
    ai_provider = models.CharField(max_length=50, choices=[
        ('claude', 'Anthropic Claude'),
        ('chatgpt', 'OpenAI ChatGPT')
    ], default='claude')
    ai_response_delay = models.IntegerField(default=3)  # Sekunden
    ai_max_tokens = models.IntegerField(default=1000)
    
    # API Keys
    anthropic_api_key = models.CharField(max_length=200, blank=True)
    openai_api_key = models.CharField(max_length=200, blank=True)
```

### Auto-Escalation System (apps/chat/views.py)

#### Escalation Logic
```python
def should_escalate_to_agent(session):
    # Count user messages
    user_messages = session.messages.filter(is_from_visitor=True).count()
    
    # Auto-escalate after 4+ user messages
    if user_messages >= 4:
        return True
    
    # Check for escalation keywords
    escalation_keywords = [
        'frustriert', 'frustrated', 'hilft nicht', 'agent', 'person'
    ]
    
    recent_messages = session.messages.filter(
        is_from_visitor=True
    ).order_by('-timestamp')[:2]
    
    for msg in recent_messages:
        if any(keyword in msg.message.lower() for keyword in escalation_keywords):
            return True
    
    return False

# Integration in message sending
if should_escalate_to_agent(session):
    session.status = 'escalated'
    session.save()
    # Create escalation message
    ChatMessage.objects.create(...)
```

---

## 👥 User Management System

### Extended User Model (apps/accounts/models.py)

```python
class User(AbstractUser):
    # Basic Info
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    
    # Role System
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('support_agent', 'Support Agent'),
        ('customer', 'Customer'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    
    # Support Agent Levels
    SUPPORT_LEVEL_CHOICES = [
        (1, 'Level 1 - Basic Support'),
        (2, 'Level 2 - Technical Support'),
        (3, 'Level 3 - Expert Support'),
        (4, 'Level 4 - Senior Expert / Team Lead'),
    ]
    support_level = models.IntegerField(choices=SUPPORT_LEVEL_CHOICES, null=True, blank=True)
    
    # Contact Information
    phone = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=100, blank=True)
    
    # Address
    street_address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(null=True, blank=True)
    
    # Permissions
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def can_manage_users(self, target_role=None):
        # Permission logic für User Management
        if self.role == 'admin':
            return True
        if self.role == 'support_agent':
            if self.support_level == 4:
                return target_role in ['customer', 'support_agent'] if target_role else True
            else:
                return target_role == 'customer' if target_role else True
        return False
```

### User Management Views (apps/accounts/user_management_views.py)

#### CRUD Operations
```python
@login_required
def user_list(request):
    # Role-based filtering
    if request.user.role == 'admin':
        users = User.objects.all()
    elif request.user.role == 'support_agent' and request.user.support_level == 4:
        users = User.objects.exclude(role='admin')
    else:
        users = User.objects.filter(role='customer')
    
    # Search & Filter
    search = request.GET.get('search')
    if search:
        users = users.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search)
        )
    
    return render(request, 'accounts/user_management/user_list.html', {
        'users': users
    })

@login_required
def user_create(request):
    if request.method == 'POST':
        form = UserCreateForm(request.POST, current_user=request.user)
        if form.is_valid():
            user = form.save()
            # Auto-generate password
            password = User.objects.make_random_password()
            user.set_password(password)
            user.save()
            
            # Send welcome email with password
            send_welcome_email(user, password)
            
            messages.success(request, f'Benutzer {user.full_name} erfolgreich erstellt.')
            return redirect('accounts:user_detail', pk=user.pk)
    else:
        form = UserCreateForm(current_user=request.user)
    
    return render(request, 'accounts/user_management/user_form.html', {
        'form': form,
        'title': 'Neuen Benutzer erstellen'
    })
```

### Permission System

#### Role-based Access Control
```python
# Decorator für View-Protection
def requires_user_management_permission(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.can_manage_users():
            return HttpResponseForbidden("Sie haben keine Berechtigung für Benutzerverwaltung.")
        return view_func(request, *args, **kwargs)
    return wrapper

# Template Tag für UI-Elemente
@register.filter
def can_edit_user(current_user, target_user):
    return current_user.can_edit_user(target_user)

# Usage in Templates
{% if user|can_edit_user:target_user %}
    <a href="{% url 'accounts:user_edit' pk=target_user.pk %}">Bearbeiten</a>
{% endif %}
```

---

## 🎫 Ticket System

### Models (apps/tickets/models.py)

#### Core Ticket Model
```python
class Ticket(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Relations
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_tickets')
    assigned_agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Status & Priority
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('pending', 'Pending Customer'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_by_agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_tickets')
    escalated_from_level = models.IntegerField(null=True, blank=True)
    escalated_to_level = models.IntegerField(null=True, blank=True)
    escalation_reason = models.TextField(blank=True)
```

#### Comment System
```python
class Comment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    is_internal = models.BooleanField(default=False, help_text="Internal comments are only visible to support agents")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Business Logic (apps/tickets/views.py)

#### Auto-Assignment System
```python
def auto_assign_ticket(ticket):
    # Find available agents based on category and level
    suitable_agents = User.objects.filter(
        role='support_agent',
        is_active=True
    )
    
    # Priority-based assignment
    if ticket.priority == 'critical':
        suitable_agents = suitable_agents.filter(support_level__gte=3)
    elif ticket.priority == 'high':
        suitable_agents = suitable_agents.filter(support_level__gte=2)
    
    # Load balancing - assign to agent with least active tickets
    agent = suitable_agents.annotate(
        active_tickets=Count('assigned_tickets', filter=Q(assigned_tickets__status='in_progress'))
    ).order_by('active_tickets').first()
    
    if agent:
        ticket.assigned_agent = agent
        ticket.status = 'in_progress'
        ticket.save()
        
        # Send notification
        send_assignment_notification(ticket, agent)
        
        return True
    return False
```

---

## 🔌 API Dokumentation

### REST Endpoints

#### Chat API
```python
# Base URL: /chat/api/

# Widget Data
GET /widget-data/
Query Parameters:
- customer: boolean
- user_name: string
- user_email: string

# Chat Session Management
POST /start/              # Start new chat
POST /send/               # Send message
GET /messages/{session_id}/  # Get messages
POST /take/{session_id}/  # Agent take chat
POST /end/{session_id}/   # End chat
```

#### User Management API
```python
# Base URL: /accounts/api/

# User CRUD
GET /users/               # List users (filtered by permissions)
POST /users/              # Create user
GET /users/{id}/          # Get user details
PUT /users/{id}/          # Update user
DELETE /users/{id}/       # Deactivate user

# User Actions
POST /users/{id}/reset-password/    # Reset password
POST /users/{id}/toggle-status/     # Toggle active status
POST /users/{id}/send-welcome/      # Send welcome email
```

#### Ticket API
```python
# Base URL: /tickets/api/

# Ticket CRUD
GET /tickets/             # List tickets (filtered by permissions)
POST /tickets/            # Create ticket
GET /tickets/{id}/        # Get ticket details
PUT /tickets/{id}/        # Update ticket
POST /tickets/{id}/close/ # Close ticket

# Comments
GET /tickets/{id}/comments/      # Get comments
POST /tickets/{id}/comments/     # Add comment

# Actions
POST /tickets/{id}/assign/       # Assign to agent
POST /tickets/{id}/escalate/     # Escalate ticket
```

### Authentication
```python
# Session-based Authentication (Default)
# JWT kann implementiert werden für API-only Clients

# Permission Decorators
@login_required
@permission_required('tickets.view_ticket')
@role_required(['admin', 'support_agent'])
```

---

## 🎨 Frontend-Komponenten

### Base Template (templates/base.html)

#### CSS Framework
```html
<!-- Bootstrap 5.3 + Custom CSS -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="{% static 'css/custom.css' %}" rel="stylesheet">

<!-- Custom CSS Variables -->
<style>
:root {
    --primary-color: #667eea;
    --success-color: #51cf66;
    --danger-color: #ff6b6b;
    --warning-color: #ffd43b;
    --info-color: #74c0fc;
}
</style>
```

#### Navigation System
```html
<nav class="navbar">
    <div class="navbar-container">
        <div class="navbar-brand">
            {% if logo_url %}
            <img src="{{ logo_url }}" alt="{{ app_name }}" class="navbar-brand-logo">
            {% endif %}
            <span>{{ app_name }}</span>
        </div>
        <div class="navbar-menu">
            {% if user.is_authenticated %}
            <a href="{% url 'main:dashboard' %}">Dashboard</a>
            <a href="{% url 'tickets:list' %}">Tickets</a>
            <a href="{% url 'knowledge:list' %}">FAQ</a>
            {% if user.role in 'support_agent,admin' %}
            <a href="{% url 'chat:agent_dashboard' %}">💬 Live Support</a>
            {% endif %}
            {% if user.can_manage_users %}
            <a href="{% url 'accounts:user_list' %}">Benutzerverwaltung</a>
            {% endif %}
            {% endif %}
        </div>
    </div>
</nav>
```

### JavaScript Components

#### Chat Widget (templates/base.html)
```javascript
// Global Chat Variables
let chatOpen = false;
let chatSession = null;
let sessionId = null;
let messagePolling = null;

// Chat Widget Functions
function toggleChat() { /* ... */ }
function startChat() { /* ... */ }
function sendMessage() { /* ... */ }
function loadMessages() { /* ... */ }
function displayMessages(messages) { /* ... */ }
function startMessagePolling() { /* ... */ }

// Real-time Message Polling (2-second interval)
setInterval(loadMessages, 2000);
```

#### AJAX Form Handling
```javascript
// Generic AJAX Form Handler
function submitAjaxForm(formId, successCallback) {
    const form = document.getElementById(formId);
    const formData = new FormData(form);
    
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            successCallback(data);
        } else {
            showError(data.error);
        }
    })
    .catch(error => {
        showError('Ein Fehler ist aufgetreten.');
    });
}
```

### Responsive Design
```css
/* Mobile-First Approach */
@media (max-width: 768px) {
    .navbar-menu {
        flex-direction: column;
        gap: 10px;
    }
    
    .card {
        margin: 10px;
        padding: 15px;
    }
    
    .table-responsive {
        font-size: 14px;
    }
}

@media (max-width: 480px) {
    .container {
        padding: 0 15px;
    }
    
    #chat-widget {
        width: 100vw !important;
        height: 100vh !important;
        bottom: 0 !important;
        right: 0 !important;
        border-radius: 0 !important;
    }
}
```

---

## 🚀 Deployment

### Production Setup

#### 1. Server Preparation (Ubuntu 22.04)
```bash
# System Updates
sudo apt update && sudo apt upgrade -y

# Python & Dependencies
sudo apt install python3 python3-pip python3-venv nginx postgresql postgresql-contrib redis-server -y

# User erstellen
sudo useradd -m -s /bin/bash helpdesk
sudo usermod -aG sudo helpdesk
```

#### 2. Application Deployment
```bash
# Als helpdesk user
sudo su - helpdesk

# Repository klonen
git clone https://github.com/aboro-it/mini-helpdesk.git
cd mini-helpdesk

# Virtual Environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Production Settings
cp .env.example .env.production
# Edit .env.production with production values
```

#### 3. Database Setup (PostgreSQL)
```bash
# PostgreSQL Setup
sudo -u postgres psql
CREATE DATABASE helpdesk_db;
CREATE USER helpdesk_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE helpdesk_db TO helpdesk_user;
\q

# Django Setup
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

#### 4. Gunicorn Configuration
```bash
# /etc/systemd/system/helpdesk.service
[Unit]
Description=Helpdesk Gunicorn daemon
After=network.target

[Service]
User=helpdesk
Group=helpdesk
WorkingDirectory=/home/helpdesk/mini-helpdesk
ExecStart=/home/helpdesk/mini-helpdesk/.venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/home/helpdesk/mini-helpdesk/helpdesk.sock helpdesk.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target

# Service aktivieren
sudo systemctl enable helpdesk
sudo systemctl start helpdesk
```

#### 5. Nginx Configuration
```nginx
# /etc/nginx/sites-available/helpdesk
server {
    listen 80;
    server_name your-domain.com;
    
    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /home/helpdesk/mini-helpdesk;
    }
    
    location /media/ {
        root /home/helpdesk/mini-helpdesk;
    }
    
    location / {
        include proxy_params;
        proxy_pass http://unix:/home/helpdesk/mini-helpdesk/helpdesk.sock;
    }
}

# Site aktivieren
sudo ln -s /etc/nginx/sites-available/helpdesk /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

#### 6. SSL Setup (Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

### Docker Deployment (Alternative)

#### Dockerfile
```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "helpdesk.wsgi:application"]
```

#### docker-compose.yml
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - DATABASE_URL=postgresql://user:pass@db:5432/helpdesk
    depends_on:
      - db
      - redis
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: helpdesk
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - static_volume:/var/www/staticfiles
      - media_volume:/var/www/media

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

---

## 🧪 Testing

### Test Structure
```
tests/
├── test_models.py          # Model Tests
├── test_views.py           # View Tests  
├── test_api.py             # API Tests
├── test_ai_service.py      # AI Integration Tests
├── test_chat.py            # Chat System Tests
├── test_permissions.py     # Permission Tests
└── test_integration.py     # End-to-End Tests
```

### Model Tests (tests/test_models.py)
```python
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.chat.models import ChatSession, ChatMessage

User = get_user_model()

class UserModelTest(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            role='admin'
        )
        self.agent_l4 = User.objects.create_user(
            username='agent_l4',
            email='agent@test.com',
            role='support_agent',
            support_level=4
        )
        self.customer = User.objects.create_user(
            username='customer',
            email='customer@test.com',
            role='customer'
        )
    
    def test_user_permissions(self):
        # Admin kann alle verwalten
        self.assertTrue(self.admin.can_manage_users())
        
        # Level 4 Agent kann Agents und Kunden verwalten
        self.assertTrue(self.agent_l4.can_manage_users('support_agent'))
        self.assertTrue(self.agent_l4.can_manage_users('customer'))
        
        # Kunde kann niemanden verwalten
        self.assertFalse(self.customer.can_manage_users())
```

### View Tests (tests/test_views.py)
```python
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.agent = User.objects.create_user(
            username='agent',
            email='agent@test.com',
            role='support_agent',
            support_level=2
        )
    
    def test_chat_widget_data(self):
        response = self.client.get('/chat/widget-data/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('widget_data', data)
    
    def test_agent_dashboard_access(self):
        self.client.force_login(self.agent)
        response = self.client.get(reverse('chat:agent_dashboard'))
        self.assertEqual(response.status_code, 200)
    
    def test_customer_cannot_access_agent_dashboard(self):
        customer = User.objects.create_user(
            username='customer',
            email='customer@test.com',
            role='customer'
        )
        self.client.force_login(customer)
        response = self.client.get(reverse('chat:agent_dashboard'))
        self.assertEqual(response.status_code, 200)  # Should render access_denied.html
```

### AI Service Tests (tests/test_ai_service.py)
```python
from django.test import TestCase
from unittest.mock import patch, MagicMock
from apps.chat.ai_service import AIService
from apps.chat.models import ChatSession, ChatMessage

class AIServiceTest(TestCase):
    def setUp(self):
        self.ai_service = AIService()
    
    def test_conversation_context_analysis(self):
        # Create mock chat history
        session = ChatSession.objects.create(
            visitor_name='Test User',
            visitor_email='test@example.com',
            visitor_ip='127.0.0.1',
            session_id='test-session',
            initial_message='Ich habe ein Login-Problem'
        )
        
        # Add messages
        ChatMessage.objects.create(
            session=session,
            message='Ich kann mich nicht anmelden',
            is_from_visitor=True,
            sender_name='Test User'
        )
        
        ChatMessage.objects.create(
            session=session,
            message='Welchen Browser verwenden Sie?',
            is_from_visitor=False,
            sender_name='KI-Assistent'
        )
        
        # Test context analysis
        context = self.ai_service._analyze_conversation_context(session.messages.all())
        
        self.assertEqual(context['problem_type'], 'login')
        self.assertEqual(context['user_expertise_level'], 'beginner')
        self.assertTrue(context['asked_browser'])
    
    @patch('apps.chat.ai_service.requests.post')
    def test_claude_api_fallback(self, mock_post):
        # Mock failed Claude API call
        mock_post.side_effect = Exception("API Error")
        
        # Should fallback to free response
        response = self.ai_service._get_claude_response("Test message")
        self.assertIsNone(response)  # API call failed
        
        # Test free response fallback
        free_response = self.ai_service._get_claude_free_response("Hallo")
        self.assertIsNotNone(free_response)
        self.assertIn("👋", free_response)  # Should contain greeting
```

### Running Tests
```bash
# All Tests
python manage.py test

# Specific App
python manage.py test apps.chat

# Specific Test
python manage.py test tests.test_ai_service.AIServiceTest.test_conversation_context_analysis

# Coverage Report
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # HTML Report in htmlcov/
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Chat Widget not loading
```python
# Problem: Widget shows "Loading..." but never loads

# Debug Steps:
1. Check browser console for JavaScript errors
2. Verify CORS settings in settings.py
3. Check if /chat/widget-data/ endpoint returns valid JSON
4. Verify CSP headers allow iframe embedding

# Browser Console Debug:
fetch('/chat/widget-data/')
.then(r => r.json())
.then(console.log)
.catch(console.error)

# Django Debug:
python manage.py shell
>>> from apps.chat.views import widget_data
>>> # Test widget_data function
```

#### 2. AI not responding
```python
# Problem: KI sendet keine Antworten

# Debug Steps:
1. Check AI settings in admin panel
2. Verify API keys are correct
3. Check logs for AI service errors
4. Test AI service manually

# Manual AI Test:
python manage.py shell
>>> from apps.chat.ai_service import AIService
>>> ai = AIService()
>>> ai.is_ai_enabled()
>>> response = ai.get_ai_response("Test message")
>>> print(response)

# Log Analysis:
tail -f /var/log/helpdesk/django.log | grep -i "ai"
```

#### 3. Permission Errors
```python
# Problem: Users can't access certain features

# Debug Steps:
1. Check user role and support_level
2. Verify permission functions
3. Check template conditionals

# User Debug:
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.get(email='user@example.com')
>>> user.role
>>> user.support_level
>>> user.can_manage_users()
>>> user.can_edit_user(target_user)
```

#### 4. Database Migration Issues
```python
# Problem: Migration conflicts or errors

# Solutions:
1. Check migration dependencies
python manage.py showmigrations

2. Fake problematic migration
python manage.py migrate --fake apps.chat 0001

3. Reset migrations (CAUTION: Data loss!)
python manage.py migrate apps.chat zero
rm apps/chat/migrations/0*.py
python manage.py makemigrations chat
python manage.py migrate

4. Manual SQL fixes (if needed)
python manage.py dbshell
```

### Performance Optimization

#### Database Queries
```python
# Use select_related for ForeignKey relationships
tickets = Ticket.objects.select_related('customer', 'assigned_agent', 'category')

# Use prefetch_related for Many-to-Many or reverse ForeignKey
sessions = ChatSession.objects.prefetch_related('messages')

# Add database indexes
class Meta:
    indexes = [
        models.Index(fields=['status', 'created_at']),
        models.Index(fields=['assigned_agent', 'status']),
    ]
```

#### Caching
```python
# Cache expensive operations
from django.core.cache import cache

def get_dashboard_stats(user):
    cache_key = f'dashboard_stats_{user.id}'
    stats = cache.get(cache_key)
    
    if stats is None:
        stats = calculate_dashboard_stats(user)
        cache.set(cache_key, stats, 300)  # 5 minutes
    
    return stats
```

#### Static Files Optimization
```python
# settings.py
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# Compress CSS/JS in production
COMPRESS_ENABLED = True
COMPRESS_CSS_FILTERS = ['compressor.filters.css_default.CssAbsoluteFilter']
```

### Monitoring & Logging

#### Structured Logging
```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/helpdesk/django.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'ai_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/helpdesk/ai.log',
            'maxBytes': 1024*1024*5,  # 5MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'apps.chat.ai_service': {
            'handlers': ['ai_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

#### Health Check Endpoint
```python
# apps/main/views.py
def health_check(request):
    health_status = {
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'services': {}
    }
    
    # Database check
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status['services']['database'] = 'ok'
    except Exception as e:
        health_status['services']['database'] = f'error: {str(e)}'
        health_status['status'] = 'unhealthy'
    
    # AI service check
    try:
        from apps.chat.ai_service import AIService
        ai = AIService()
        if ai.is_ai_enabled():
            health_status['services']['ai_service'] = 'ok'
        else:
            health_status['services']['ai_service'] = 'disabled'
    except Exception as e:
        health_status['services']['ai_service'] = f'error: {str(e)}'
    
    status_code = 200 if health_status['status'] == 'healthy' else 503
    return JsonResponse(health_status, status=status_code)
```

---

## 📚 Additional Resources

### Development Tools
- **Django Debug Toolbar**: Profiling & Debug Information
- **django-extensions**: Useful management commands
- **pytest-django**: Advanced testing framework
- **black**: Code formatting
- **flake8**: Code linting

### Useful Commands
```bash
# Development
python manage.py runserver_plus  # Enhanced development server
python manage.py shell_plus      # Enhanced Django shell
python manage.py graph_models    # Generate model diagrams

# Database
python manage.py dbbackup        # Backup database
python manage.py dbrestore       # Restore database
python manage.py reset_db        # Reset database (dev only)

# Static Files
python manage.py collectstatic   # Collect static files
python manage.py compress        # Compress CSS/JS

# Custom Commands
python manage.py create_test_data    # Generate test data
python manage.py cleanup_old_sessions # Clean old chat sessions
python manage.py send_digest_emails  # Send daily digest emails
```

### External APIs Documentation
- **Anthropic Claude API**: https://docs.anthropic.com/en/api/
- **OpenAI ChatGPT API**: https://platform.openai.com/docs/api-reference
- **Bootstrap 5**: https://getbootstrap.com/docs/5.3/
- **Django**: https://docs.djangoproject.com/

---

## 📞 Support & Contribution

### Getting Help
- **Email**: dev@aboro-it.net
- **Issues**: https://github.com/aboro-it/mini-helpdesk/issues
- **Documentation**: https://docs.aboro-it.net/helpdesk/

### Contributing
1. Fork Repository
2. Create Feature Branch
3. Write Tests
4. Follow Code Style (black + flake8)
5. Submit Pull Request

### Code Style
```bash
# Install dev dependencies
pip install black flake8 isort

# Format code
black .
isort .

# Check style
flake8 .

# Pre-commit hook
echo "black . && isort . && flake8 ." > .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

---

---

**© 2025 Aboro-IT - Entwickler Dokumentation**  
*Version 2.0 - November 2025*  
*Professionelle IT-Lösungen für Ihr Unternehmen*  
*https://aboro-it.net*