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


def notify_agents_new_ticket(ticket):
    """Send email notification to all agents about new ticket"""
    from apps.accounts.models import User

    # Get all agents (not admins, not the ticket creator)
    agents = User.objects.filter(
        role='support_agent',
        is_active=True
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
Diese Email wurde automatisch vom ML Gruppe Helpdesk System gesendet.
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


@login_required
def ticket_list(request):
    """List tickets based on user role"""
    if request.user.role == 'customer':
        # Customers only see their own tickets
        tickets = Ticket.objects.filter(created_by=request.user).order_by('-created_at')
    elif request.user.role == 'support_agent':
        # Agents see assigned tickets or all open unassigned tickets
        tickets = Ticket.objects.filter(
            models.Q(assigned_to=request.user) | models.Q(assigned_to__isnull=True, status='open')
        ).order_by('-created_at')
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
                from apps.accounts.models import User
                customer_email = form.cleaned_data.get('customer_email')

                try:
                    customer = User.objects.get(email=customer_email)
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
                except User.DoesNotExist:
                    messages.error(request, f'Kein Kunde mit der Email {customer_email} gefunden.')
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

    context = {
        'ticket': ticket,
        'comments': comments.order_by('created_at'),
        'form': form,
    }
    return render(request, 'tickets/detail.html', context)


@login_required
def ticket_assign(request, pk):
    """Assign ticket to an agent - only for agents and admins"""
    if request.user.role not in ['support_agent', 'admin']:
        return HttpResponseForbidden('Keine Berechtigung')

    ticket = get_object_or_404(Ticket, pk=pk)

    # Agents can self-assign
    if request.method == 'POST':
        ticket.assigned_to = request.user
        ticket.status = 'in_progress'
        ticket.save()

        # Add system comment
        TicketComment.objects.create(
            ticket=ticket,
            author=request.user,
            content=f'Ticket wurde von {request.user.full_name} übernommen.',
            is_internal=True
        )

        messages.success(request, f'Ticket {ticket.ticket_number} wurde Ihnen zugewiesen.')
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

        from apps.accounts.models import User

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
            messages.success(request, f'Ticket wurde eskaliert an {new_agent.full_name}')

        return redirect('tickets:detail', pk=ticket.pk)

    # Get available agents for escalation (higher support level than current user)
    from apps.accounts.models import User
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
    # Only admins and support agents can view statistics
    if request.user.role not in ['admin', 'support_agent']:
        return HttpResponseForbidden('Sie haben keine Berechtigung, diese Seite zu sehen.')

    from django.db.models import Count, Q, F, Value
    from django.db.models.functions import Concat
    from apps.accounts.models import User
    from .models import MobileClassroom, MobileClassroomLocation

    # Get all closed and resolved tickets for analysis
    all_tickets = Ticket.objects.filter(
        models.Q(status='closed') | models.Q(status='resolved')
    ).select_related('created_by', 'category', 'mobile_classroom')

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

    # Most common issues/categories
    category_stats = (
        all_tickets
        .values('category__id', 'category__name')
        .annotate(count=Count('id'))
        .order_by('-count')
        .exclude(category__isnull=True)[:10]
    )

    # Mobile classroom issues
    classroom_stats = (
        all_tickets
        .filter(mobile_classroom__isnull=False)
        .values('mobile_classroom__id', 'mobile_classroom__name', 'mobile_classroom__location__name')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )

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

    context = {
        'total_tickets': all_tickets.count(),
        'trainer_stats': trainer_stats,
        'category_stats': category_stats,
        'classroom_stats': classroom_stats,
        'priority_stats': priority_stats,
        'top_trainers': top_problematic_trainers,
    }

    return render(request, 'tickets/statistics.html', context)
