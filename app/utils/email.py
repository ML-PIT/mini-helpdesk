import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from flask import current_app, render_template
from app.models.ticket import Ticket, TicketComment
from app.models.user import User
from app.models.audit import SystemLog
from app import db
import threading
import time
import re

class EmailManager:
    """Manages email integration for tickets"""
    
    def __init__(self):
        self.imap_server = None
        self.smtp_server = None
    
    def connect_imap(self):
        """Connect to IMAP server"""
        try:
            self.imap_server = imaplib.IMAP4_SSL(
                current_app.config['EMAIL_HOST'],
                current_app.config['EMAIL_PORT']
            )
            self.imap_server.login(
                current_app.config['EMAIL_USERNAME'],
                current_app.config['EMAIL_PASSWORD']
            )
            return True
        except Exception as e:
            SystemLog.error('email', f'IMAP connection failed: {str(e)}')
            return False
    
    def connect_smtp(self):
        """Connect to SMTP server"""
        try:
            self.smtp_server = smtplib.SMTP(
                current_app.config['SMTP_HOST'],
                current_app.config['SMTP_PORT']
            )
            self.smtp_server.starttls()
            self.smtp_server.login(
                current_app.config['EMAIL_USERNAME'],
                current_app.config['EMAIL_PASSWORD']
            )
            return True
        except Exception as e:
            SystemLog.error('email', f'SMTP connection failed: {str(e)}')
            return False
    
    def send_email(self, to_email, subject, body, attachments=None, ticket_number=None):
        """Send email via SMTP"""
        try:
            if not self.connect_smtp():
                return False
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = current_app.config['EMAIL_USERNAME']
            msg['To'] = to_email
            
            # Add ticket number to subject for threading
            if ticket_number:
                subject = f"[{ticket_number}] {subject}"
            
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(body, 'html'))
            
            # Add attachments
            if attachments:
                for attachment in attachments:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment['content'])
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {attachment["filename"]}'
                    )
                    msg.attach(part)
            
            # Send email
            self.smtp_server.send_message(msg)
            self.smtp_server.quit()
            
            SystemLog.info('email', f'Email sent to {to_email}', 
                          details={'subject': subject, 'ticket_number': ticket_number})
            
            return True
            
        except Exception as e:
            SystemLog.error('email', f'Failed to send email to {to_email}: {str(e)}',
                           details={'subject': subject, 'error': str(e)})
            return False
    
    def process_incoming_emails(self):
        """Process incoming emails and create tickets"""
        try:
            if not self.connect_imap():
                return
            
            self.imap_server.select('INBOX')
            
            # Search for unread emails
            status, messages = self.imap_server.search(None, 'UNSEEN')
            
            if status == 'OK':
                for msg_id in messages[0].split():
                    try:
                        # Fetch email
                        status, msg_data = self.imap_server.fetch(msg_id, '(RFC822)')
                        
                        if status == 'OK':
                            email_body = msg_data[0][1]
                            email_message = email.message_from_bytes(email_body)
                            
                            # Process the email
                            self._process_email_message(email_message)
                            
                            # Mark as read
                            self.imap_server.store(msg_id, '+FLAGS', '\\Seen')
                            
                    except Exception as e:
                        SystemLog.error('email', f'Error processing email {msg_id}: {str(e)}')
                        continue
            
            self.imap_server.close()
            self.imap_server.logout()
            
        except Exception as e:
            SystemLog.error('email', f'Error processing incoming emails: {str(e)}')
    
    def _process_email_message(self, email_message):
        """Process individual email message"""
        try:
            # Extract email details
            sender_email = email.utils.parseaddr(email_message['From'])[1]
            subject = email_message['Subject']
            message_id = email_message['Message-ID']
            
            # Get or create user
            user = User.query.filter_by(email=sender_email).first()
            if not user:
                # Create new customer user
                user = User(
                    username=sender_email.split('@')[0],
                    email=sender_email,
                    first_name=email.utils.parseaddr(email_message['From'])[0] or 'Unknown',
                    last_name='',
                    role='customer',
                    is_active=True,
                    email_verified=True
                )
                db.session.add(user)
                db.session.commit()
            
            # Check if this is a reply to existing ticket
            ticket = self._find_ticket_by_subject(subject)
            
            # Extract email body
            body = self._extract_email_body(email_message)
            
            if ticket:
                # Add as comment to existing ticket
                comment = ticket.add_comment(
                    author_id=user.id,
                    content=body,
                    is_internal=False,
                    email_message_id=message_id
                )
                
                # Update ticket status if closed
                if ticket.status == 'closed':
                    ticket.status = 'open'
                
                db.session.commit()
                
                SystemLog.info('email', f'Email added as comment to ticket {ticket.ticket_number}',
                              details={'sender': sender_email, 'ticket_id': ticket.id})
                
                # Send auto-reply
                self._send_auto_reply(sender_email, ticket, 'updated')
                
            else:
                # Create new ticket
                ticket = Ticket(
                    title=subject[:200] if subject else 'Email Support Request',
                    description=body,
                    priority='medium',
                    created_by=user.id,
                    email_thread_id=message_id
                )
                
                ticket.set_priority_based_sla()
                db.session.add(ticket)
                db.session.commit()
                
                SystemLog.info('email', f'New ticket created from email: {ticket.ticket_number}',
                              details={'sender': sender_email, 'ticket_id': ticket.id})
                
                # Send auto-reply
                self._send_auto_reply(sender_email, ticket, 'created')
            
            # Process attachments
            self._process_email_attachments(email_message, ticket, user.id)
            
        except Exception as e:
            SystemLog.error('email', f'Error processing email message: {str(e)}',
                           details={'error': str(e)})
    
    def _find_ticket_by_subject(self, subject):
        """Find existing ticket by subject line"""
        if not subject:
            return None
        
        # Look for ticket number in subject [TK-YYYY-XXXXX]
        match = re.search(r'\[TK-\d{4}-\d{5}\]', subject)
        if match:
            ticket_number = match.group().strip('[]')
            return Ticket.query.filter_by(ticket_number=ticket_number).first()
        
        return None
    
    def _extract_email_body(self, email_message):
        """Extract plain text body from email"""
        body = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    break
                elif part.get_content_type() == "text/html" and not body:
                    # Fallback to HTML if no plain text
                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    # Basic HTML to text conversion
                    body = re.sub(r'<[^>]+>', '', body)
        else:
            body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
        
        return body.strip()
    
    def _process_email_attachments(self, email_message, ticket, user_id):
        """Process email attachments"""
        if not email_message.is_multipart():
            return
        
        for part in email_message.walk():
            if part.get_content_disposition() == 'attachment':
                filename = part.get_filename()
                if filename:
                    content = part.get_payload(decode=True)
                    content_type = part.get_content_type()
                    
                    # Check file size and type
                    if len(content) <= 16 * 1024 * 1024:  # 16MB limit
                        ticket.add_attachment(
                            filename=filename,
                            content=content,
                            content_type=content_type,
                            author_id=user_id
                        )
    
    def _send_auto_reply(self, to_email, ticket, action):
        """Send automatic reply to customer"""
        try:
            if action == 'created':
                subject = f"Ticket Created: {ticket.title}"
                template = 'emails/ticket_created.html'
            else:
                subject = f"Ticket Updated: {ticket.title}"
                template = 'emails/ticket_updated.html'
            
            body = render_template(template, ticket=ticket)
            
            self.send_email(
                to_email=to_email,
                subject=subject,
                body=body,
                ticket_number=ticket.ticket_number
            )
            
        except Exception as e:
            SystemLog.error('email', f'Failed to send auto-reply: {str(e)}')

# Global email manager instance
email_manager = EmailManager()

def send_ticket_notification(ticket, action, comment=None):
    """Send ticket notification emails"""
    try:
        # Determine recipients based on action
        recipients = set()
        
        # Always notify ticket creator (if not the same as actor)
        from flask_login import current_user
        if ticket.creator and ticket.creator.email and ticket.creator.id != current_user.id:
            recipients.add(ticket.creator.email)
        
        # Notify assigned agent
        if ticket.assignee and ticket.assignee.email and ticket.assignee.id != current_user.id:
            recipients.add(ticket.assignee.email)
        
        # For certain actions, notify team leaders
        if action in ['created', 'escalated'] and current_user.role == 'customer':
            team_leaders = User.query.filter_by(role='team_leader', is_active=True).all()
            for leader in team_leaders:
                recipients.add(leader.email)
        
        # Send notifications
        for recipient_email in recipients:
            _send_notification_email(recipient_email, ticket, action, comment)
        
        # Send Teams notification if configured
        if current_app.config.get('TEAMS_WEBHOOK_URL'):
            _send_teams_notification(ticket, action, comment)
            
    except Exception as e:
        SystemLog.error('email', f'Error sending ticket notifications: {str(e)}')

def _send_notification_email(recipient_email, ticket, action, comment=None):
    """Send individual notification email"""
    try:
        # Determine template and subject based on action
        template_map = {
            'created': ('emails/ticket_created.html', f'New Ticket: {ticket.title}'),
            'commented': ('emails/ticket_commented.html', f'Comment Added: {ticket.title}'),
            'assigned': ('emails/ticket_assigned.html', f'Ticket Assigned: {ticket.title}'),
            'status_changed': ('emails/ticket_status_changed.html', f'Status Changed: {ticket.title}'),
            'priority_changed': ('emails/ticket_priority_changed.html', f'Priority Changed: {ticket.title}')
        }
        
        template, subject = template_map.get(action, ('emails/ticket_updated.html', f'Ticket Updated: {ticket.title}'))
        
        body = render_template(template, ticket=ticket, comment=comment)
        
        email_manager.send_email(
            to_email=recipient_email,
            subject=subject,
            body=body,
            ticket_number=ticket.ticket_number
        )
        
    except Exception as e:
        SystemLog.error('email', f'Failed to send notification to {recipient_email}: {str(e)}')

def _send_teams_notification(ticket, action, comment=None):
    """Send Microsoft Teams notification"""
    try:
        import requests
        
        webhook_url = current_app.config.get('TEAMS_WEBHOOK_URL')
        if not webhook_url:
            return
        
        # Create Teams card
        card = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "summary": f"Ticket {action}: {ticket.ticket_number}",
            "themeColor": "2fb2bf",
            "sections": [{
                "activityTitle": f"Ticket {action.title()}: {ticket.ticket_number}",
                "activitySubtitle": ticket.title,
                "activityImage": "https://example.com/icon.png",
                "facts": [
                    {"name": "Ticket", "value": ticket.ticket_number},
                    {"name": "Status", "value": ticket.status.title()},
                    {"name": "Priority", "value": ticket.priority.title()},
                    {"name": "Created By", "value": ticket.creator.full_name if ticket.creator else "Unknown"},
                    {"name": "Assigned To", "value": ticket.assignee.full_name if ticket.assignee else "Unassigned"}
                ],
                "markdown": True
            }],
            "potentialAction": [{
                "@type": "OpenUri",
                "name": "View Ticket",
                "targets": [{
                    "os": "default",
                    "uri": f"{current_app.config.get('SITE_URL', '')}/tickets/{ticket.id}"
                }]
            }]
        }
        
        if comment:
            card["sections"][0]["text"] = f"**Comment:** {comment.content[:200]}{'...' if len(comment.content) > 200 else ''}"
        
        response = requests.post(webhook_url, json=card, timeout=10)
        response.raise_for_status()
        
        SystemLog.info('teams', f'Teams notification sent for ticket {ticket.ticket_number}')
        
    except Exception as e:
        SystemLog.error('teams', f'Failed to send Teams notification: {str(e)}')

def start_email_monitoring():
    """Start email monitoring in background thread"""
    def monitor_emails():
        while True:
            try:
                email_manager.process_incoming_emails()
                time.sleep(60)  # Check every minute
            except Exception as e:
                SystemLog.error('email', f'Email monitoring error: {str(e)}')
                time.sleep(300)  # Wait 5 minutes on error
    
    if current_app.config.get('EMAIL_USERNAME'):
        thread = threading.Thread(target=monitor_emails, daemon=True)
        thread.start()
        SystemLog.info('email', 'Email monitoring started')