from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.utils import timezone
from .models import Ticket, TicketComment, Category
from .forms import TicketCreateForm, TicketCommentForm


@login_required
def ticket_list(request):
    """List tickets based on user role"""
    if request.user.role == 'customer':
        # Customers only see their own tickets
        tickets = Ticket.objects.filter(created_by=request.user).order_by('-created_at')
    elif request.user.role in ['support_agent', 'team_leader']:
        # Agents see assigned tickets or all open tickets
        tickets = Ticket.objects.filter(
            models.Q(assigned_to=request.user) | models.Q(assigned_to__isnull=True)
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
    """Create a new ticket - only for customers and agents"""
    if request.user.role not in ['customer', 'support_agent', 'team_leader']:
        messages.error(request, 'Sie haben keine Berechtigung, Tickets zu erstellen.')
        return redirect('main:dashboard')

    if request.method == 'POST':
        form = TicketCreateForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = request.user
            ticket.save()

            # Set SLA based on priority
            ticket.set_priority_based_sla()
            ticket.save()

            messages.success(request, f'Ticket {ticket.ticket_number} wurde erstellt!')
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

            # Only agents can create internal comments
            if request.user.role in ['support_agent', 'team_leader', 'admin']:
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
    if request.user.role not in ['support_agent', 'team_leader', 'admin']:
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
    if request.user.role not in ['support_agent', 'team_leader', 'admin']:
        return HttpResponseForbidden('Keine Berechtigung')

    ticket = get_object_or_404(Ticket, pk=pk)

    if request.method == 'POST':
        new_agent_id = request.POST.get('agent_id')
        new_level = request.POST.get('support_level')
        reason = request.POST.get('reason', '')

        from apps.accounts.models import User

        # Change assigned agent
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

    # Get available agents for escalation
    from apps.accounts.models import User
    agents = User.objects.filter(
        role__in=['support_agent', 'team_leader'],
        is_active=True
    ).exclude(id=request.user.id)

    context = {
        'ticket': ticket,
        'agents': agents,
        'support_levels': Ticket.SUPPORT_LEVEL_CHOICES,
    }
    return render(request, 'tickets/escalate.html', context)


@login_required
def ticket_close(request, pk):
    """Close a ticket"""
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

            messages.success(request, f'Ticket {ticket.ticket_number} wurde geschlossen.')
            return redirect('tickets:detail', pk=ticket.pk)

    return HttpResponseForbidden('Keine Berechtigung')
