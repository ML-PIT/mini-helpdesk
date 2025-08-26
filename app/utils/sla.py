from datetime import datetime, timedelta
from flask import current_app
from app.models.ticket import Ticket
from app.models.audit import SystemLog
from app import db

def check_sla_breaches():
    """Check for SLA breaches and mark tickets accordingly"""
    try:
        # Find tickets that are past their SLA due date
        breached_tickets = Ticket.query.filter(
            Ticket.sla_due_date <= datetime.utcnow(),
            Ticket.status.notin_(['resolved', 'closed']),
            Ticket.sla_breached == False
        ).all()
        
        breach_count = 0
        
        for ticket in breached_tickets:
            ticket.sla_breached = True
            breach_count += 1
            
            SystemLog.warning('sla', f'SLA breach detected for ticket {ticket.ticket_number}',
                            details={
                                'ticket_id': ticket.id,
                                'due_date': ticket.sla_due_date.isoformat(),
                                'priority': ticket.priority,
                                'assigned_to': ticket.assignee.full_name if ticket.assignee else 'Unassigned'
                            })
        
        if breach_count > 0:
            db.session.commit()
            SystemLog.info('sla', f'SLA breach check completed: {breach_count} tickets marked as breached')
        
        return breach_count
        
    except Exception as e:
        SystemLog.error('sla', f'Error checking SLA breaches: {str(e)}')
        return 0

def get_sla_metrics(days=30):
    """Get SLA performance metrics for the specified period"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get tickets resolved/closed in the period
        resolved_tickets = Ticket.query.filter(
            Ticket.resolved_at >= start_date,
            Ticket.resolved_at <= end_date
        ).all()
        
        if not resolved_tickets:
            return {
                'total_tickets': 0,
                'on_time': 0,
                'breached': 0,
                'sla_compliance_rate': 0,
                'avg_resolution_time': 0,
                'avg_first_response_time': 0
            }
        
        on_time = 0
        breached = 0
        total_resolution_time = 0
        total_first_response_time = 0
        tickets_with_response = 0
        
        for ticket in resolved_tickets:
            # Check if resolved within SLA
            if ticket.resolved_at and ticket.sla_due_date:
                if ticket.resolved_at <= ticket.sla_due_date:
                    on_time += 1
                else:
                    breached += 1
            
            # Calculate resolution time
            if ticket.resolved_at:
                resolution_hours = (ticket.resolved_at - ticket.created_at).total_seconds() / 3600
                total_resolution_time += resolution_hours
            
            # Calculate first response time
            if ticket.first_response_at:
                response_hours = (ticket.first_response_at - ticket.created_at).total_seconds() / 3600
                total_first_response_time += response_hours
                tickets_with_response += 1
        
        total_tickets = len(resolved_tickets)
        compliance_rate = (on_time / (on_time + breached)) * 100 if (on_time + breached) > 0 else 0
        avg_resolution_time = total_resolution_time / total_tickets if total_tickets > 0 else 0
        avg_first_response_time = total_first_response_time / tickets_with_response if tickets_with_response > 0 else 0
        
        return {
            'total_tickets': total_tickets,
            'on_time': on_time,
            'breached': breached,
            'sla_compliance_rate': round(compliance_rate, 2),
            'avg_resolution_time': round(avg_resolution_time, 2),
            'avg_first_response_time': round(avg_first_response_time, 2)
        }
        
    except Exception as e:
        SystemLog.error('sla', f'Error calculating SLA metrics: {str(e)}')
        return None

def get_priority_sla_hours():
    """Get SLA hours for each priority level"""
    return {
        'critical': 4,   # 4 hours
        'high': 24,      # 1 day
        'medium': 72,    # 3 days
        'low': 168       # 1 week
    }

def calculate_sla_due_date(created_at, priority):
    """Calculate SLA due date based on priority"""
    sla_hours = get_priority_sla_hours()
    hours = sla_hours.get(priority, 72)  # Default to medium priority
    
    return created_at + timedelta(hours=hours)

def get_sla_status(ticket):
    """Get SLA status for a ticket"""
    if not ticket.sla_due_date:
        return 'no_sla'
    
    if ticket.status in ['resolved', 'closed']:
        if ticket.resolved_at and ticket.resolved_at <= ticket.sla_due_date:
            return 'met'
        else:
            return 'breached'
    
    now = datetime.utcnow()
    time_remaining = ticket.sla_due_date - now
    
    if time_remaining.total_seconds() <= 0:
        return 'breached'
    elif time_remaining.total_seconds() <= 7200:  # 2 hours
        return 'at_risk'
    else:
        return 'on_track'

def get_sla_time_remaining(ticket):
    """Get time remaining until SLA breach"""
    if not ticket.sla_due_date or ticket.status in ['resolved', 'closed']:
        return None
    
    now = datetime.utcnow()
    time_remaining = ticket.sla_due_date - now
    
    if time_remaining.total_seconds() <= 0:
        return {'breached': True, 'overdue_hours': abs(time_remaining.total_seconds() / 3600)}
    
    hours = time_remaining.total_seconds() / 3600
    
    if hours > 24:
        days = int(hours / 24)
        remaining_hours = int(hours % 24)
        return {'days': days, 'hours': remaining_hours, 'total_hours': hours}
    else:
        return {'hours': int(hours), 'minutes': int((hours % 1) * 60), 'total_hours': hours}

def get_tickets_approaching_sla(hours_threshold=2):
    """Get tickets approaching SLA breach"""
    threshold_time = datetime.utcnow() + timedelta(hours=hours_threshold)
    
    return Ticket.query.filter(
        Ticket.sla_due_date <= threshold_time,
        Ticket.sla_due_date > datetime.utcnow(),
        Ticket.status.notin_(['resolved', 'closed'])
    ).order_by(Ticket.sla_due_date.asc()).all()

def get_breached_tickets():
    """Get all tickets that have breached SLA"""
    return Ticket.query.filter(
        Ticket.sla_breached == True,
        Ticket.status.notin_(['resolved', 'closed'])
    ).order_by(Ticket.sla_due_date.asc()).all()

def update_ticket_sla(ticket, new_priority=None):
    """Update ticket SLA when priority changes"""
    if new_priority:
        ticket.priority = new_priority
    
    # Recalculate SLA due date
    ticket.sla_due_date = calculate_sla_due_date(ticket.created_at, ticket.priority)
    
    # Reset breach status if new SLA is not yet breached
    if ticket.sla_due_date > datetime.utcnow():
        ticket.sla_breached = False
    else:
        ticket.sla_breached = True
    
    return ticket

def get_agent_sla_performance(agent_id, days=30):
    """Get SLA performance metrics for a specific agent"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get tickets resolved by this agent in the period
        resolved_tickets = Ticket.query.filter(
            Ticket.assigned_to == agent_id,
            Ticket.resolved_at >= start_date,
            Ticket.resolved_at <= end_date
        ).all()
        
        if not resolved_tickets:
            return None
        
        on_time = 0
        breached = 0
        total_resolution_time = 0
        total_first_response_time = 0
        tickets_with_response = 0
        
        for ticket in resolved_tickets:
            if ticket.resolved_at and ticket.sla_due_date:
                if ticket.resolved_at <= ticket.sla_due_date:
                    on_time += 1
                else:
                    breached += 1
            
            if ticket.resolved_at:
                resolution_hours = (ticket.resolved_at - ticket.created_at).total_seconds() / 3600
                total_resolution_time += resolution_hours
            
            if ticket.first_response_at:
                response_hours = (ticket.first_response_at - ticket.created_at).total_seconds() / 3600
                total_first_response_time += response_hours
                tickets_with_response += 1
        
        total_tickets = len(resolved_tickets)
        compliance_rate = (on_time / (on_time + breached)) * 100 if (on_time + breached) > 0 else 0
        
        return {
            'agent_id': agent_id,
            'total_tickets': total_tickets,
            'on_time': on_time,
            'breached': breached,
            'sla_compliance_rate': round(compliance_rate, 2),
            'avg_resolution_time': round(total_resolution_time / total_tickets, 2),
            'avg_first_response_time': round(total_first_response_time / tickets_with_response, 2) if tickets_with_response > 0 else 0
        }
        
    except Exception as e:
        SystemLog.error('sla', f'Error calculating agent SLA performance: {str(e)}')
        return None