from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.clickjacking import xframe_options_exempt
import json
import uuid
import time
import threading
from .models import ChatSession, ChatMessage, ChatSettings
from .ai_service import get_ai_response_for_chat
from apps.admin_panel.models import SystemSettings

User = get_user_model()


def send_ai_response(session_id, message):
    """
    Send AI response after a delay (runs in background thread)
    """
    try:
        system_settings = SystemSettings.get_settings()
        
        # Wait for the configured delay (default to 2 seconds if not set)
        delay = getattr(system_settings, 'ai_response_delay', 2)
        time.sleep(delay)
        
        session = ChatSession.objects.get(session_id=session_id)
        
        # Send AI response if AI is enabled and no agent assigned
        if system_settings.ai_enabled and not session.assigned_agent:
            ai_response = get_ai_response_for_chat(message, session)
            
            if ai_response:
                # Create AI response message
                ChatMessage.objects.create(
                    session=session,
                    message=ai_response,
                    is_from_visitor=False,
                    sender_name="KI-Assistent",
                    message_type='text'
                )
                
                # Update session status to indicate AI is handling it
                if session.status != 'active':
                    session.status = 'active'
                    session.save()
                    
                    # Send system message about AI assistance only once
                    if not session.messages.filter(sender_name="System", message_type='system').exists():
                        ChatMessage.objects.create(
                            session=session,
                            message="🤖 Ein KI-Assistent steht Ihnen zur Verfügung. Bei komplexeren Problemen wird automatisch ein Support-Agent hinzugezogen.",
                            is_from_visitor=False,
                            sender_name="System",
                            message_type='system'
                        )
            else:
                # Fallback if AI doesn't respond
                ChatMessage.objects.create(
                    session=session,
                    message="🤖 Entschuldigung, ich habe momentan technische Probleme. Ein Support-Agent wurde benachrichtigt und wird Ihnen helfen.",
                    is_from_visitor=False,
                    sender_name="KI-Assistent",
                    message_type='text'
                )
    except Exception as e:
        # Log error but don't fail
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"AI response error: {e}")
        
        # Try to send error message to user
        try:
            session = ChatSession.objects.get(session_id=session_id)
            ChatMessage.objects.create(
                session=session,
                message="⚠️ Technisches Problem bei der KI-Antwort. Ein Support-Agent wurde benachrichtigt.",
                is_from_visitor=False,
                sender_name="System",
                message_type='system'
            )
        except:
            pass


def should_send_ai_response(session):
    """
    Determine if AI response should be sent
    """
    system_settings = SystemSettings.get_settings()
    
    # Check if AI is enabled
    if not system_settings.ai_enabled:
        return False
    
    # Always send AI response if no agent is assigned (regardless of status)
    if not session.assigned_agent:
        return True
    
    # Don't send AI response if agent is already assigned
    return False


def should_escalate_to_agent(session):
    """
    Determine if chat should be escalated to human agent based on AI conversation analysis
    """
    # Count total messages in session
    total_messages = session.messages.count()
    user_messages = session.messages.filter(is_from_visitor=True).count()
    
    # Auto-escalate after 4 user messages without resolution
    if user_messages >= 4:
        return True
    
    # Check for escalation keywords in recent user messages
    escalation_keywords = [
        'frustriert', 'frustrated', 'hilft nicht', 'doesn\'t help', 'not working',
        'funktioniert nicht', 'agent', 'mitarbeiter', 'person', 'human',
        'sprechen', 'talk to', 'supervisor', 'manager', 'komplex', 'complex',
        'dringend', 'urgent', 'wichtig', 'important', 'sofort', 'immediately'
    ]
    
    recent_messages = session.messages.filter(
        is_from_visitor=True
    ).order_by('-timestamp')[:2]
    
    for msg in recent_messages:
        if any(keyword in msg.message.lower() for keyword in escalation_keywords):
            return True
    
    # Check if AI has provided multiple solutions without success indicators
    ai_messages = session.messages.filter(is_from_visitor=False, message_type='text').count()
    if ai_messages >= 3 and user_messages >= 3:
        return True
    
    return False


@xframe_options_exempt
def chat_widget(request):
    """Render the chat widget for embedding in websites"""
    settings = ChatSettings.get_settings()
    
    # Check if chat is available or AI is enabled
    from datetime import timedelta
    online_threshold = timezone.now() - timedelta(minutes=5)
    
    # Check for available agents (simplified - just check if they're active)
    available_agents = User.objects.filter(
        role__in=['support_agent', 'admin'],
        is_active=True
    ).count()
    
    # For more accurate online detection, check last_activity if field exists
    try:
        available_agents_with_activity = User.objects.filter(
            role__in=['support_agent', 'admin'],
            is_active=True,
            last_activity__gte=online_threshold
        ).count()
        # Use the activity-based count if it's available
        available_agents = available_agents_with_activity
    except:
        # If last_activity field doesn't exist, assume no agents online for proper AI fallback
        available_agents = 0
    
    # Check AI availability
    system_settings = SystemSettings.get_settings()
    ai_available = system_settings.ai_enabled
    
    # Check if loaded in iframe
    is_iframe = request.GET.get('iframe', 'false').lower() == 'true' or \
               request.headers.get('Sec-Fetch-Dest') == 'iframe'
    
    # Check if customer is logged in (from URL parameters)
    is_customer = request.GET.get('customer', 'false').lower() == 'true'
    user_name = request.GET.get('user_name', '')
    user_email = request.GET.get('user_email', '')
    
    context = {
        'settings': settings,
        'is_available': settings.is_enabled and (available_agents > 0 or ai_available),
        'available_agents': available_agents,
        'ai_available': ai_available,
        'session_id': str(uuid.uuid4()),
        'is_iframe': is_iframe,
        'is_customer': is_customer,
        'user_name': user_name,
        'user_email': user_email,
    }
    
    return render(request, 'chat/widget.html', context)


def widget_data(request):
    """Return widget data as JSON for direct embedding"""
    settings = ChatSettings.get_settings()
    
    # Check if chat is available or AI is enabled
    from datetime import timedelta
    online_threshold = timezone.now() - timedelta(minutes=5)
    
    # Check for available agents (simplified - just check if they're active)
    available_agents = User.objects.filter(
        role__in=['support_agent', 'admin'],
        is_active=True
    ).count()
    
    # For more accurate online detection, check last_activity if field exists
    try:
        available_agents_with_activity = User.objects.filter(
            role__in=['support_agent', 'admin'],
            is_active=True,
            last_activity__gte=online_threshold
        ).count()
        # Use the activity-based count if it's available
        available_agents = available_agents_with_activity
    except:
        # If last_activity field doesn't exist, assume no agents online for proper AI fallback
        available_agents = 0
    
    # Check AI availability
    system_settings = SystemSettings.get_settings()
    ai_available = system_settings.ai_enabled
    
    # Check if customer is logged in (from URL parameters)
    is_customer = request.GET.get('customer', 'false').lower() == 'true'
    user_name = request.GET.get('user_name', '')
    user_email = request.GET.get('user_email', '')
    
    widget_data = {
        'session_id': str(uuid.uuid4()),
        'available_agents': available_agents,
        'ai_available': ai_available,
        'is_available': settings.is_enabled and (available_agents > 0 or ai_available),
        'widget_color': settings.widget_color,
        'is_customer': is_customer,
        'user_name': user_name,
        'user_email': user_email,
        'welcome_message': settings.welcome_message,
        'offline_message': settings.offline_message,
    }
    
    return JsonResponse({
        'success': True,
        'widget_data': widget_data
    })


@csrf_exempt
@require_http_methods(["POST"])
def start_chat(request):
    """Start a new chat session"""
    try:
        data = json.loads(request.body)
        
        # Get visitor IP
        visitor_ip = request.META.get('HTTP_X_FORWARDED_FOR')
        if visitor_ip:
            visitor_ip = visitor_ip.split(',')[0]
        else:
            visitor_ip = request.META.get('REMOTE_ADDR')
        
        # Create chat session
        session = ChatSession.objects.create(
            session_id=data.get('session_id'),
            visitor_name=data.get('name'),
            visitor_email=data.get('email'),
            visitor_ip=visitor_ip,
            initial_message=data.get('message'),
            visitor_page_url=data.get('page_url'),
            status='waiting'
        )
        
        # Create initial message
        ChatMessage.objects.create(
            session=session,
            message=data.get('message'),
            is_from_visitor=True,
            sender_name=data.get('name'),
            message_type='text'
        )
        
        # Auto-assign if enabled AND agents are actually online
        settings = ChatSettings.get_settings()
        if settings.auto_assign:
            # Check for truly online agents (with recent activity)
            from datetime import timedelta
            online_threshold = timezone.now() - timedelta(minutes=5)
            
            try:
                available_agent = User.objects.filter(
                    role__in=['support_agent', 'admin'],
                    is_active=True,
                    last_activity__gte=online_threshold
                ).first()
            except:
                # If last_activity field doesn't exist, don't auto-assign
                available_agent = None
            
            if available_agent:
                session.assigned_agent = available_agent
                session.status = 'active'
                session.save()
                
                # Send system message
                ChatMessage.objects.create(
                    session=session,
                    message=f"👋 {available_agent.full_name} hat den Chat übernommen.",
                    is_from_visitor=False,
                    sender_name="System",
                    message_type='system'
                )
        
        # If no agent assigned and AI is enabled, trigger AI response
        if should_send_ai_response(session):
            # Start AI response in background thread
            ai_thread = threading.Thread(
                target=send_ai_response,
                args=(session.session_id, data.get('message'))
            )
            ai_thread.daemon = True
            ai_thread.start()
        
        return JsonResponse({
            'success': True,
            'session_id': session.session_id,
            'status': session.status,
            'assigned_agent': session.assigned_agent.full_name if session.assigned_agent else None
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def send_message(request):
    """Send a message in an existing chat session"""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        message = data.get('message')
        
        session = get_object_or_404(ChatSession, session_id=session_id)
        
        # Create message
        ChatMessage.objects.create(
            session=session,
            message=message,
            is_from_visitor=True,
            sender_name=session.visitor_name,
            message_type='text'
        )
        
        # Check if AI should respond
        if should_send_ai_response(session):
            # Check for auto-escalation before AI response
            if should_escalate_to_agent(session):
                # Create escalation message
                ChatMessage.objects.create(
                    session=session,
                    message="🚀 **Automatische Weiterleitung an Support-Agent**\n\nIch erkenne, dass Ihr Problem komplexere Unterstützung benötigt. Ein erfahrener Support-Agent wurde benachrichtigt und übernimmt in Kürze.\n\n✅ Alle bisherigen Informationen wurden übertragen\n✅ Prioritäre Bearbeitung\n✅ Direkter menschlicher Kontakt",
                    is_from_visitor=False,
                    sender_name="KI-Assistent",
                    message_type='system'
                )
                
                # Notify available agents (this could trigger email/push notifications)
                # For now, we'll just update the session status to indicate escalation needed
                session.status = 'escalated'
                session.save()
            else:
                # Start AI response in background thread
                ai_thread = threading.Thread(
                    target=send_ai_response,
                    args=(session_id, message)
                )
                ai_thread.daemon = True
                ai_thread.start()
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_http_methods(["GET"])
def get_messages(request, session_id):
    """Get messages for a chat session"""
    try:
        session = get_object_or_404(ChatSession, session_id=session_id)
        messages = session.messages.all()
        
        message_data = []
        for msg in messages:
            message_data.append({
                'id': msg.id,
                'message': msg.message,
                'timestamp': msg.timestamp.isoformat(),
                'is_from_visitor': msg.is_from_visitor,
                'sender_name': msg.sender_name,
                'message_type': msg.message_type
            })
        
        return JsonResponse({
            'success': True,
            'messages': message_data,
            'session_status': session.status
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def agent_dashboard(request):
    """Dashboard for agents to manage chats"""
    if request.user.role not in ['support_agent', 'admin']:
        return render(request, 'chat/access_denied.html')
    
    # Get active and waiting chats
    waiting_chats = ChatSession.objects.filter(status='waiting')
    escalated_chats = ChatSession.objects.filter(status='escalated')
    active_chats = ChatSession.objects.filter(
        status='active',
        assigned_agent=request.user
    )
    
    # Get AI-handled chats (active but no assigned agent)
    ai_handled_chats = ChatSession.objects.filter(
        status='active',
        assigned_agent__isnull=True
    )
    
    context = {
        'waiting_chats': waiting_chats,
        'escalated_chats': escalated_chats,
        'active_chats': active_chats,
        'ai_handled_chats': ai_handled_chats,
    }
    
    return render(request, 'chat/agent_dashboard.html', context)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def agent_take_chat(request, session_id):
    """Agent takes a waiting chat or takes over from AI"""
    if request.user.role not in ['support_agent', 'admin']:
        return JsonResponse({'success': False, 'error': 'Access denied'})
    
    try:
        # Allow taking over from waiting, escalated, and AI-handled active chats
        session = get_object_or_404(
            ChatSession, 
            session_id=session_id, 
            status__in=['waiting', 'active', 'escalated']
        )
        
        # Check if chat is AI-handled (active but no assigned agent) or escalated
        is_ai_takeover = session.status == 'active' and not session.assigned_agent
        is_escalated = session.status == 'escalated'
        
        session.assigned_agent = request.user
        session.status = 'active'
        session.save()
        
        # Send appropriate system message
        if is_escalated:
            message_text = f"🚀 {request.user.full_name} hat Ihren eskalierten Chat übernommen und steht Ihnen jetzt persönlich zur Verfügung."
        elif is_ai_takeover:
            message_text = f"👨‍💻 {request.user.full_name} hat den Chat vom KI-Assistenten übernommen."
        else:
            message_text = f"👋 {request.user.full_name} hat den Chat übernommen."
            
        ChatMessage.objects.create(
            session=session,
            message=message_text,
            is_from_visitor=False,
            sender_name="System",
            message_type='system'
        )
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def agent_send_message(request, session_id):
    """Agent sends a message"""
    if request.user.role not in ['support_agent', 'admin']:
        return JsonResponse({'success': False, 'error': 'Access denied'})
    
    try:
        data = json.loads(request.body)
        message = data.get('message')
        
        session = get_object_or_404(
            ChatSession, 
            session_id=session_id, 
            assigned_agent=request.user
        )
        
        # Create message
        ChatMessage.objects.create(
            session=session,
            message=message,
            is_from_visitor=False,
            sender_name=request.user.full_name,
            agent=request.user,
            message_type='text'
        )
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def end_chat(request, session_id):
    """End a chat session"""
    if request.user.role not in ['support_agent', 'admin']:
        return JsonResponse({'success': False, 'error': 'Access denied'})
    
    try:
        session = get_object_or_404(
            ChatSession, 
            session_id=session_id, 
            assigned_agent=request.user
        )
        
        session.status = 'ended'
        session.ended_at = timezone.now()
        session.save()
        
        # Send system message
        ChatMessage.objects.create(
            session=session,
            message="Chat wurde beendet.",
            is_from_visitor=False,
            sender_name="System",
            message_type='system'
        )
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def chat_detail(request, session_id):
    """Detailed view of a chat session for agents"""
    if request.user.role not in ['support_agent', 'admin']:
        return render(request, 'chat/access_denied.html')
    
    session = get_object_or_404(ChatSession, session_id=session_id)
    messages = session.messages.all()
    
    context = {
        'session': session,
        'messages': messages,
        'can_respond': session.assigned_agent == request.user and session.status == 'active'
    }
    
    return render(request, 'chat/chat_detail.html', context)