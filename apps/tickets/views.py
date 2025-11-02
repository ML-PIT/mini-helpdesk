from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.db import models
from .models import Ticket, TicketComment, Category
from .forms import TicketCreateForm, TicketCommentForm, AgentTicketCreateForm
from .ai_service import ai_service
from apps.accounts.models import User


def notify_agents_new_ticket(ticket):
    """
    Send email notification to Level 1-2 support agents about new ticket.

    IMPORTANT: Level 3+ support agents are NOT notified about new tickets.
    They will only be notified when tickets are explicitly escalated to them.
    This ensures expert agents only handle tickets that require their expertise.
    """
    # Get Level 1-2 agents only (not Level 3+, not admins, not the ticket creator)
    # Level 3 and above agents should only be notified when tickets are escalated to them
    agents = User.objects.filter(
        role='support_agent',
        is_active=True,
        support_level__in=[1, 2]  # Only Level 1 and Level 2 support agents
    ).exclude(id=ticket.created_by.id)

    if not agents.exists():
        return

    # Build ticket URL using SITE_URL setting
    site_url = settings.SITE_URL.rstrip('/')
    ticket_url = f"{site_url}/tickets/{ticket.pk}/"

    subject = f'Neues Ticket: {ticket.ticket_number} - {ticket.title}'

    message = f"""Hallo,

ein neues Support-Ticket wurde erstellt:

Ticket-Nummer: {ticket.ticket_number}
Titel: {ticket.title}
Priorität: {ticket.get_priority_display()}
Kategorie: {ticket.category.name if ticket.category else 'Keine'}
Erstellt von: {ticket.created_by.full_name} ({ticket.created_by.email})
Erstellt am: {ticket.created_at.strftime('%d.%m.%Y %H:%M')}

Beschreibung:
{ticket.description}

Ticket ansehen: {ticket_url}

---
Diese Email wurde automatisch vom ABoro-Soft Helpdesk System gesendet.
"""

    # Send to all agents
    recipient_list = [agent.email for agent in agents]

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=True,  # Don't break ticket creation if email fails
        )
    except Exception as e:
        print(f"Failed to send notification email: {e}")


def notify_agent_ticket_escalation(ticket, escalated_from_agent, escalated_to_agent, reason=''):
    """
    Send email notification to agent when ticket is escalated to them.

    This is the PRIMARY notification method for Level 3+ support agents.
    They receive notifications ONLY when tickets are explicitly escalated to them,
    not for all new tickets in the system.

    Args:
        ticket: Ticket instance being escalated
        escalated_from_agent: User who escalated the ticket (or None if system escalation)
        escalated_to_agent: User who is receiving the escalated ticket
        reason: Optional explanation for the escalation
    """
    if not escalated_to_agent or not escalated_to_agent.email:
        return

    # Build ticket URL using SITE_URL setting
    site_url = settings.SITE_URL.rstrip('/')
    ticket_url = f"{site_url}/tickets/{ticket.pk}/"

    # Get priority display
    priority_display = ticket.get_priority_display()

    # Priority urgency mapping
    urgency_map = {
        'critical': '🔴 KRITISCH - Sofortige Aktion erforderlich',
        'high': '🟠 HOCH - Baldige Bearbeitung erforderlich',
        'medium': '🟡 MITTEL - Normale Priorität',
        'low': '🟢 NIEDRIG - Kann in Ruhe bearbeitet werden'
    }

    urgency_text = urgency_map.get(ticket.priority, priority_display)

    subject = f'ESKALIERT: Ticket {ticket.ticket_number} - {ticket.title} ({priority_display})'

    message = f"""Hallo {escalated_to_agent.first_name},

ein Ticket wurde zu Ihnen eskaliert:

{'=' * 70}
DRINGLICHKEIT: {urgency_text}
{'=' * 70}

Ticket-Nummer: {ticket.ticket_number}
Titel: {ticket.title}
Priorität: {priority_display}
Kategorie: {ticket.category.name if ticket.category else 'Keine'}
Erstellt von: {ticket.created_by.full_name} ({ticket.created_by.email})
Telefonnummer Kunde: {ticket.created_by.phone if ticket.created_by.phone else 'Nicht angegeben'}
Erstellt am: {ticket.created_at.strftime('%d.%m.%Y %H:%M')}
Eskaliert von: {escalated_from_agent.full_name if escalated_from_agent else 'System'}

Beschreibung:
{ticket.description}
"""

    if reason:
        message += f"\nEskalations-Grund:\n{reason}\n"

    message += f"""
Ticket ansehen: {ticket_url}

---
Diese Email wurde automatisch vom ABoro-Soft Helpdesk System gesendet.
"""

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[escalated_to_agent.email],
            fail_silently=True,  # Don't break escalation if email fails
        )
    except Exception as e:
        print(f"Failed to send escalation notification email: {e}")


@login_required
def ticket_list(request):
    """List tickets based on user role"""
    if request.user.role == 'customer':
        # Customers only see their own tickets (including closed)
        tickets = Ticket.objects.filter(created_by=request.user).order_by('-created_at')
    elif request.user.role == 'support_agent':
        # Agents see all tickets (assigned, unassigned, and closed)
        tickets = Ticket.objects.all().order_by('-created_at')
    else:  # admin
        # Admins see all tickets
        tickets = Ticket.objects.all().order_by('-created_at')

    context = {
        'tickets': tickets,
        'user': request.user,
    }
    return render(request, 'tickets/list.html', context)


@login_required
def ticket_create(request):
    """Create a new ticket - customers create for themselves, agents can create for customers"""
    if request.user.role not in ['customer', 'support_agent', 'admin']:
        messages.error(request, 'Sie haben keine Berechtigung, Tickets zu erstellen.')
        return redirect('main:dashboard')

    # Agents use a different form to specify customer
    if request.user.role in ['support_agent', 'admin']:
        if request.method == 'POST':
            form = AgentTicketCreateForm(request.POST, request.FILES)
            if form.is_valid():
                customer_email = form.cleaned_data.get('customer_email', '').strip()
                customer_first_name = form.cleaned_data.get('customer_first_name', '').strip()
                customer_last_name = form.cleaned_data.get('customer_last_name', '').strip()
                customer_phone = form.cleaned_data.get('customer_phone', '').strip()

                customer = None

                # First, try to find customer by email if provided
                if customer_email:
                    try:
                        customer = User.objects.get(email=customer_email)

                        # Update phone if provided
                        if customer_phone and not customer.phone:
                            customer.phone = customer_phone
                            customer.save()
                    except User.DoesNotExist:
                        # Email provided but customer doesn't exist
                        if not customer_first_name or not customer_last_name:
                            messages.error(
                                request,
                                f'Kunde mit Email {customer_email} existiert nicht. '
                                'Bitte geben Sie Vor- und Nachname ein, um einen neuen Kunden zu erstellen.'
                            )
                            return render(request, 'tickets/create_agent.html', {'form': form})

                        # Create new customer with the provided email and name
                        customer = None  # Will be created below

                # If no customer found yet, try to create new one from name
                if not customer:
                    if not customer_first_name or not customer_last_name:
                        messages.error(
                            request,
                            'Bitte geben Sie entweder die Email eines existierenden Kunden ein '
                            'oder Vor- und Nachname eines neuen Kunden.'
                        )
                        return render(request, 'tickets/create_agent.html', {'form': form})

                    # Generate email from name if not provided
                    if not customer_email:
                        customer_email = f"{customer_first_name.lower()}.{customer_last_name.lower()}@example.com"
                        # Ensure email is unique by appending counter if needed
                        base_email = customer_email
                        counter = 1
                        while User.objects.filter(email=customer_email).exists():
                            customer_email = f"{customer_first_name.lower()}.{customer_last_name.lower()}{counter}@example.com"
                            counter += 1

                    # Generate username from email (remove domain part)
                    username = customer_email.split('@')[0]

                    # Ensure username is unique by appending counter if needed
                    base_username = username
                    counter = 1
                    while User.objects.filter(username=username).exists():
                        username = f"{base_username}{counter}"
                        counter += 1

                    try:
                        # Create new customer user with initial password
                        INITIAL_PASSWORD = 'P@ssw0rd123'
                        customer = User.objects.create_user(
                            email=customer_email,
                            username=username,
                            password=INITIAL_PASSWORD,
                            first_name=customer_first_name,
                            last_name=customer_last_name,
                            phone=customer_phone,  # Add phone number
                            role='customer',
                            force_password_change=True  # Force password change on first login
                        )
                        messages.info(
                            request,
                            f'Neuer Kunde "{customer.full_name}" wurde im System erstellt. '
                            f'Initial-Passwort: {INITIAL_PASSWORD}'
                        )
                    except Exception as e:
                        messages.error(request, f'Fehler beim Erstellen des Kunden: {str(e)}')
                        return render(request, 'tickets/create_agent.html', {'form': form})

                # Create ticket for customer
                ticket = form.save(commit=False)
                ticket.created_by = customer
                ticket.save()

                # Set SLA based on priority
                ticket.set_priority_based_sla()
                ticket.save()

                # Add internal note that agent created this
                TicketComment.objects.create(
                    ticket=ticket,
                    author=request.user,
                    content=f'Ticket wurde von {request.user.full_name} für Kunde {customer.full_name} erstellt (telefonische Anfrage).',
                    is_internal=True
                )

                # Send notification emails to other agents
                notify_agents_new_ticket(ticket)

                messages.success(request, f'Ticket {ticket.ticket_number} wurde für {customer.full_name} erstellt!')
                return redirect('tickets:detail', pk=ticket.pk)
        else:
            form = AgentTicketCreateForm()

        return render(request, 'tickets/create_agent.html', {'form': form})

    # Customers create tickets for themselves
    else:
        if request.method == 'POST':
            form = TicketCreateForm(request.POST, request.FILES)
            if form.is_valid():
                ticket = form.save(commit=False)
                ticket.created_by = request.user
                ticket.save()

                # Set SLA based on priority
                ticket.set_priority_based_sla()
                ticket.save()

                # Send notification emails to all agents
                notify_agents_new_ticket(ticket)

                # Try to auto-respond with Claude AI
                if ai_service.is_available():
                    try:
                        ai_comment = ai_service.create_auto_comment(ticket)
                        if ai_comment:
                            messages.success(request, f'Ticket {ticket.ticket_number} wurde erstellt! Unsere KI hat bereits eine erste Antwort generiert.')
                        else:
                            messages.success(request, f'Ticket {ticket.ticket_number} wurde erfolgreich erstellt!')
                    except Exception as e:
                        messages.success(request, f'Ticket {ticket.ticket_number} wurde erfolgreich erstellt!')
                else:
                    messages.success(request, f'Ticket {ticket.ticket_number} wurde erfolgreich erstellt!')

                return redirect('tickets:detail', pk=ticket.pk)
        else:
            form = TicketCreateForm()

        return render(request, 'tickets/create.html', {'form': form})


@login_required
def ticket_detail(request, pk):
    """View ticket details and add comments"""
    ticket = get_object_or_404(Ticket, pk=pk)

    # Check permissions
    if not request.user.can_access_ticket(ticket):
        return HttpResponseForbidden('Sie haben keine Berechtigung, dieses Ticket zu sehen.')

    if request.method == 'POST':
        form = TicketCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.ticket = ticket
            comment.author = request.user

            # Only agents and admins can create internal comments
            if request.user.role in ['support_agent', 'admin']:
                comment.is_internal = form.cleaned_data.get('is_internal', False)
            else:
                comment.is_internal = False

            comment.save()
            messages.success(request, 'Kommentar hinzugefügt!')
            return redirect('tickets:detail', pk=ticket.pk)
    else:
        form = TicketCommentForm()

    # Get comments (hide internal from customers)
    if request.user.role == 'customer':
        comments = ticket.comments.filter(is_internal=False)
    else:
        comments = ticket.comments.all()

    # Get available agents for team lead assignment
    team_agents = User.objects.filter(
        role='support_agent',
        is_active=True
    ).exclude(id=request.user.id).order_by('first_name', 'last_name')

    context = {
        'ticket': ticket,
        'comments': comments.order_by('created_at'),
        'form': form,
        'team_agents': team_agents,
    }
    return render(request, 'tickets/detail.html', context)


@login_required
def ticket_assign(request, pk):
    """Assign ticket to an agent - for self-assignment and team leads"""
    if request.user.role not in ['support_agent', 'admin']:
        return HttpResponseForbidden('Keine Berechtigung')

    ticket = get_object_or_404(Ticket, pk=pk)

    if request.method == 'POST':
        # Check if user is Level 4 (Team Lead) or Admin
        is_team_lead = request.user.role == 'support_agent' and request.user.support_level == 4
        is_admin = request.user.role == 'admin'

        # Team leads can assign to other agents, others can only self-assign
        if is_team_lead or is_admin:
            # Get agent_id from POST data if provided (team lead assigning to someone else)
            agent_id = request.POST.get('agent_id')

            if agent_id:
                try:
                    assigned_agent = User.objects.get(id=agent_id, role='support_agent', is_active=True)
                    ticket.assigned_to = assigned_agent
                    action_text = f'Ticket wurde von {request.user.full_name} (Team Lead) an {assigned_agent.full_name} zugewiesen.'
                    success_msg = f'Ticket {ticket.ticket_number} wurde {assigned_agent.full_name} zugewiesen.'
                except User.DoesNotExist:
                    messages.error(request, 'Agent nicht gefunden.')
                    return redirect('tickets:detail', pk=ticket.pk)
            else:
                # Self-assign for team lead
                ticket.assigned_to = request.user
                action_text = f'Ticket wurde von {request.user.full_name} übernommen.'
                success_msg = f'Ticket {ticket.ticket_number} wurde Ihnen zugewiesen.'
        else:
            # Regular agents can only self-assign
            ticket.assigned_to = request.user
            action_text = f'Ticket wurde von {request.user.full_name} übernommen.'
            success_msg = f'Ticket {ticket.ticket_number} wurde Ihnen zugewiesen.'

        ticket.status = 'in_progress'
        ticket.save()

        # Add system comment
        TicketComment.objects.create(
            ticket=ticket,
            author=request.user,
            content=action_text,
            is_internal=True
        )

        messages.success(request, success_msg)
        return redirect('tickets:detail', pk=ticket.pk)

    return redirect('tickets:detail', pk=ticket.pk)


@login_required
def ticket_escalate(request, pk):
    """Escalate ticket to another agent or higher level"""
    if request.user.role not in ['support_agent', 'admin']:
        return HttpResponseForbidden('Keine Berechtigung')

    ticket = get_object_or_404(Ticket, pk=pk)

    if request.method == 'POST':
        new_agent_id = request.POST.get('agent_id')
        new_level = request.POST.get('support_level')
        reason = request.POST.get('reason', '')

        # Change assigned agent and/or support level
        if new_agent_id:
            new_agent = get_object_or_404(User, pk=new_agent_id)
            old_agent = ticket.assigned_to
            ticket.assigned_to = new_agent

            # Add system comment
            comment_text = f'Ticket eskaliert von {request.user.full_name}'
            if old_agent:
                comment_text += f' (war: {old_agent.full_name})'
            comment_text += f' an {new_agent.full_name}'

            if new_level:
                ticket.support_level = new_level
                comment_text += f' - {dict(Ticket.SUPPORT_LEVEL_CHOICES)[new_level]}'

            if reason:
                comment_text += f'\n\nGrund: {reason}'

            TicketComment.objects.create(
                ticket=ticket,
                author=request.user,
                content=comment_text,
                is_internal=True
            )

            ticket.save()

            # Send email notification to escalated agent with urgency
            notify_agent_ticket_escalation(ticket, old_agent, new_agent, reason)

            messages.success(request, f'Ticket wurde eskaliert an {new_agent.full_name} und Email wurde versendet')

        return redirect('tickets:detail', pk=ticket.pk)

    # Get available agents for escalation (higher support level than current user)
    if request.user.role == 'admin':
        # Admins can escalate to anyone
        agents = User.objects.filter(
            role='support_agent',
            is_active=True
        ).exclude(id=request.user.id)
    else:
        # Agents can only escalate to higher level agents
        current_level = request.user.support_level or 1
        agents = User.objects.filter(
            role='support_agent',
            support_level__gt=current_level,
            is_active=True
        )

    context = {
        'ticket': ticket,
        'agents': agents,
        'support_levels': Ticket.SUPPORT_LEVEL_CHOICES,
        'current_user_level': request.user.support_level if request.user.role == 'support_agent' else 3,
    }
    return render(request, 'tickets/escalate.html', context)


@login_required
def ticket_close(request, pk):
    """Close a ticket and send history via email"""
    ticket = get_object_or_404(Ticket, pk=pk)

    # Only assigned agent or admin can close
    if request.user.role == 'admin' or ticket.assigned_to == request.user:
        if request.method == 'POST':
            ticket.status = 'closed'
            ticket.closed_at = timezone.now()
            ticket.save()

            TicketComment.objects.create(
                ticket=ticket,
                author=request.user,
                content='Ticket wurde geschlossen.',
                is_internal=False
            )

            # Send ticket history to customer via email
            try:
                history_text = ticket.get_history_as_text()
                send_mail(
                    subject=f'Ticket {ticket.ticket_number} wurde geschlossen - Zusammenfassung',
                    message=history_text,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[ticket.created_by.email],
                    fail_silently=False,
                )
                messages.success(request, f'Ticket {ticket.ticket_number} wurde geschlossen und die Zusammenfassung wurde per Email versendet.')
            except Exception as e:
                # If email fails, still close the ticket but warn user
                messages.warning(request, f'Ticket {ticket.ticket_number} wurde geschlossen, aber die Email konnte nicht versendet werden: {str(e)}')

            return redirect('tickets:detail', pk=ticket.pk)

    return HttpResponseForbidden('Keine Berechtigung')


@login_required
def statistics_dashboard(request):
    """Statistics dashboard for trainers/customers and classroom issues"""
    # Only support agents can view statistics
    if request.user.role != 'support_agent':
        return HttpResponseForbidden('Sie haben keine Berechtigung, diese Seite zu sehen.')

    from django.db.models import Count, Q, F, Value
    from django.db.models.functions import Concat
    # MobileClassroom imports removed - not needed

    # Get filter from request
    category_filter = request.GET.get('category')

    # Get all closed and resolved tickets for analysis
    all_tickets = Ticket.objects.filter(
        models.Q(status='closed') | models.Q(status='resolved')
    ).select_related('created_by', 'assigned_to', 'category')

    # Apply category filter if provided
    if category_filter:
        all_tickets = all_tickets.filter(category_id=category_filter)

    # Calculate overall average processing time
    total_processing_time = 0
    tickets_with_time = 0
    for ticket in all_tickets:
        processing_hours = ticket.get_processing_time_hours()
        if processing_hours is not None:
            total_processing_time += processing_hours
            tickets_with_time += 1

    avg_processing_hours = (total_processing_time / tickets_with_time) if tickets_with_time > 0 else 0
    avg_processing_days = avg_processing_hours / 24

    # Statistics per trainer/customer - use Concat for full_name
    trainer_stats = (
        all_tickets
        .values('created_by__id', 'created_by__email', 'created_by__first_name', 'created_by__last_name')
        .annotate(
            total_tickets=Count('id'),
            high_priority=Count('id', filter=models.Q(priority__in=['high', 'critical'])),
            avg_resolution_days=models.Avg(
                models.F('resolved_at') - models.F('created_at'),
                output_field=models.DurationField(),
                filter=models.Q(resolved_at__isnull=False)
            )
        )
        .order_by('-total_tickets')
    )

    # Convert duration to days and create full_name display
    for stat in trainer_stats:
        if stat.get('avg_resolution_days'):
            stat['avg_resolution_days_display'] = stat['avg_resolution_days'].days
        else:
            stat['avg_resolution_days_display'] = 'N/A'
        # Create full_name from first_name and last_name
        stat['full_name'] = f"{stat['created_by__first_name']} {stat['created_by__last_name']}"

    # Statistics per assigned agent (support staff handling time)
    agent_tickets = all_tickets.filter(assigned_to__isnull=False)
    agent_stats = {}
    for ticket in agent_tickets:
        agent_id = ticket.assigned_to.id
        if agent_id not in agent_stats:
            agent_stats[agent_id] = {
                'id': agent_id,
                'name': ticket.assigned_to.full_name,
                'email': ticket.assigned_to.email,
                'total_handled': 0,
                'high_priority_handled': 0,
                'total_hours': 0,
                'tickets': []
            }

        agent_stats[agent_id]['total_handled'] += 1
        if ticket.priority in ['high', 'critical']:
            agent_stats[agent_id]['high_priority_handled'] += 1

        processing_hours = ticket.get_processing_time_hours()
        if processing_hours is not None:
            agent_stats[agent_id]['total_hours'] += processing_hours

        agent_stats[agent_id]['tickets'].append({
            'number': ticket.ticket_number,
            'title': ticket.title,
            'priority': ticket.priority,
            'processing_time': ticket.get_processing_time_display(),
            'created_at': ticket.created_at
        })

    # Calculate average time per agent and convert to sorted list
    # IMPORTANT: Only Level 4 support agents can see all agents' performance data
    # Other support agents can only see their own performance
    agent_stats_list = []
    user_support_level = request.user.support_level if hasattr(request.user, 'support_level') else None

    for agent_id, stats in agent_stats.items():
        # Permission check: Only show agent data if:
        # 1. User is Level 4 (can see all agents), OR
        # 2. User is viewing their own performance data
        if user_support_level != 4 and agent_id != request.user.id:
            continue  # Skip this agent's data - user doesn't have permission to view it

        avg_hours = stats['total_hours'] / stats['total_handled'] if stats['total_handled'] > 0 else 0
        avg_days = avg_hours / 24

        # Format average processing time
        if avg_days > 0:
            days_int = int(avg_days)
            hours_int = int((avg_days % 1) * 24)
            if days_int > 0:
                avg_time_display = f"{days_int} Tage"
            else:
                avg_time_display = f"{hours_int} Stunden"
        else:
            avg_time_display = "N/A"

        agent_stats_list.append({
            **stats,
            'avg_hours': avg_hours,
            'avg_days': avg_days,
            'avg_time_display': avg_time_display
        })

    # Sort by total handled tickets descending
    agent_stats_list.sort(key=lambda x: x['total_handled'], reverse=True)

    # Most common issues/categories
    category_stats = (
        all_tickets
        .values('category__id', 'category__name')
        .annotate(count=Count('id'))
        .order_by('-count')
        .exclude(category__isnull=True)[:10]
    )

    # Mobile classroom stats removed - not needed
    classroom_stats = []

    # Priority distribution
    priority_stats = (
        all_tickets
        .values('priority')
        .annotate(count=Count('id'))
        .order_by('priority')
    )

    # Get top problematic trainers (those with most issues)
    top_problematic_trainers = [
        {
            'id': stat['created_by__id'],
            'name': stat['full_name'],
            'email': stat['created_by__email'],
            'tickets': stat['total_tickets'],
            'high_priority': stat['high_priority'],
            'avg_days': stat['avg_resolution_days_display']
        }
        for stat in trainer_stats[:10]
    ]

    # Get all categories for filter dropdown
    all_categories = Category.objects.filter(is_active=True).order_by('name')

    # Format average processing time for display
    if avg_processing_days > 0:
        days_int = int(avg_processing_days)
        hours_int = int((avg_processing_days % 1) * 24)
        if days_int > 0:
            avg_processing_display = f"{days_int} {'Tag' if days_int == 1 else 'Tage'}"
            if hours_int > 0:
                avg_processing_display += f", {hours_int} {'Stunde' if hours_int == 1 else 'Stunden'}"
        else:
            avg_processing_display = f"{hours_int} {'Stunde' if hours_int == 1 else 'Stunden'}"
    else:
        avg_processing_display = "N/A"

    # Add information about whether user can view all agent stats
    can_view_all_agent_stats = (request.user.role == 'support_agent' and user_support_level == 4) or request.user.role == 'admin'

    context = {
        'total_tickets': all_tickets.count(),
        'avg_processing_time': avg_processing_display,
        'avg_processing_hours': round(avg_processing_hours, 1),
        'trainer_stats': trainer_stats,
        'agent_stats': agent_stats_list,
        'can_view_all_agent_stats': can_view_all_agent_stats,
        'user_support_level': user_support_level,
        'category_stats': category_stats,
        'classroom_stats': classroom_stats,
        'priority_stats': priority_stats,
        'top_trainers': top_problematic_trainers,
        'all_categories': all_categories,
        'selected_category': category_filter,
    }

    return render(request, 'tickets/statistics.html', context)


# API Endpoints for AJAX requests

@login_required
def search_customers_api(request):
    """
    API endpoint to search customers by name or email.
    Returns JSON list of matching customers.
    """
    from django.http import JsonResponse
    from django.db.models import Q
    
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    # Search by first name, last name, or email
    customers = User.objects.filter(
        role='customer',
        is_active=True
    ).filter(
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(email__icontains=query)
    ).values('id', 'first_name', 'last_name', 'email', 'phone')[:10]
    
    results = []
    for customer in customers:
        full_name = f"{customer['first_name']} {customer['last_name']}".strip()
        results.append({
            'id': customer['id'],
            'name': full_name,
            'first_name': customer['first_name'],
            'last_name': customer['last_name'],
            'email': customer['email'],
            'phone': customer['phone'] or '',
            'display': f"{full_name} ({customer['email']})"
        })

    return JsonResponse({'results': results})
