from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileSize
from wtforms import StringField, TextAreaField, SelectField, BooleanField, SubmitField, MultipleFileField, HiddenField
from wtforms.validators import DataRequired, Length, Optional, ValidationError
from wtforms.widgets import TextArea
from app.models.ticket import Category
from app.models.user import User

class TicketForm(FlaskForm):
    title = StringField('Title', validators=[
        DataRequired(message='Title is required'),
        Length(min=5, max=200, message='Title must be between 5 and 200 characters')
    ], render_kw={'placeholder': 'Brief description of the issue'})
    
    description = TextAreaField('Description', validators=[
        DataRequired(message='Description is required'),
        Length(min=20, max=5000, message='Description must be between 20 and 5000 characters')
    ], render_kw={
        'placeholder': 'Please provide detailed information about the issue, including:\n- What you were trying to do\n- What happened instead\n- Error messages (if any)\n- Steps to reproduce the issue',
        'rows': 8
    })
    
    priority = SelectField('Priority', choices=[
        ('low', 'Low - General question or minor issue'),
        ('medium', 'Medium - Standard support request'),
        ('high', 'High - Business impact, needs urgent attention'),
        ('critical', 'Critical - System down, major business impact')
    ], default='medium', validators=[DataRequired()])
    
    category_id = SelectField('Category', coerce=int, validators=[Optional()])
    
    attachments = MultipleFileField('Attachments', validators=[
        FileAllowed(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'zip'], 
                   'Only specific file types are allowed'),
        FileSize(max_size=16*1024*1024, message='File size must be less than 16MB')
    ])
    
    submit = SubmitField('Create Ticket')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate category choices dynamically
        self.category_id.choices = [(0, 'Select Category')] + [
            (c.id, c.name) for c in Category.query.filter_by(is_active=True).order_by(Category.name).all()
        ]

class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[
        DataRequired(message='Comment cannot be empty'),
        Length(min=5, max=2000, message='Comment must be between 5 and 2000 characters')
    ], render_kw={
        'placeholder': 'Add your comment or response here...',
        'rows': 4
    })
    
    is_internal = BooleanField('Internal Note', 
                              description='Check this box to make this comment visible only to support staff')
    
    attachments = MultipleFileField('Attachments', validators=[
        FileAllowed(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'zip']),
        FileSize(max_size=16*1024*1024)
    ])
    
    submit = SubmitField('Add Comment')

class AssignTicketForm(FlaskForm):
    assigned_to = SelectField('Assign To', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Assign')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate with agents and team leaders
        agents = User.query.filter(
            User.role.in_(['support_agent', 'team_leader']),
            User.is_active == True
        ).order_by(User.first_name, User.last_name).all()
        
        self.assigned_to.choices = [(0, 'Unassigned')] + [
            (u.id, f"{u.full_name} ({u.role.replace('_', ' ').title()})") for u in agents
        ]

class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[
        DataRequired(message='Category name is required'),
        Length(min=2, max=100, message='Category name must be between 2 and 100 characters')
    ], render_kw={'placeholder': 'e.g., Technical Support, Billing, General'})
    
    description = TextAreaField('Description', validators=[
        Optional(),
        Length(max=500, message='Description must be less than 500 characters')
    ], render_kw={
        'placeholder': 'Brief description of what tickets belong in this category',
        'rows': 3
    })
    
    color = StringField('Color', validators=[
        DataRequired(message='Color is required'),
        Length(min=7, max=7, message='Color must be a valid hex code')
    ], default='#2fb2bf', render_kw={
        'type': 'color',
        'title': 'Choose a color for this category'
    })
    
    auto_assign_to = SelectField('Auto-Assign To', coerce=int, validators=[Optional()],
                                description='Automatically assign new tickets in this category to a specific agent')
    
    submit = SubmitField('Create Category')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate auto-assignment choices
        agents = User.query.filter(
            User.role.in_(['support_agent', 'team_leader']),
            User.is_active == True
        ).order_by(User.first_name, User.last_name).all()
        
        self.auto_assign_to.choices = [(0, 'No Auto-Assignment')] + [
            (u.id, u.full_name) for u in agents
        ]
    
    def validate_name(self, name):
        category = Category.query.filter_by(name=name.data).first()
        if category:
            raise ValidationError('A category with this name already exists.')
    
    def validate_color(self, color):
        import re
        if not re.match(r'^#[0-9a-fA-F]{6}$', color.data):
            raise ValidationError('Color must be a valid hex code (e.g., #2fb2bf).')

class EditCategoryForm(CategoryForm):
    def __init__(self, original_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_name = original_name
        self.submit.label.text = 'Update Category'
    
    def validate_name(self, name):
        if name.data != self.original_name:
            category = Category.query.filter_by(name=name.data).first()
            if category:
                raise ValidationError('A category with this name already exists.')

class BulkActionForm(FlaskForm):
    ticket_ids = HiddenField('Ticket IDs')
    action = SelectField('Action', choices=[
        ('', 'Select Action'),
        ('assign', 'Assign to Agent'),
        ('change_status', 'Change Status'),
        ('change_priority', 'Change Priority'),
        ('add_category', 'Set Category')
    ], validators=[DataRequired()])
    
    # Action-specific fields (populated dynamically via JavaScript)
    assigned_to = SelectField('Assign To', coerce=int, validators=[Optional()])
    status = SelectField('Status', choices=[
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('pending', 'Pending'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed')
    ], validators=[Optional()])
    priority = SelectField('Priority', choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ], validators=[Optional()])
    category_id = SelectField('Category', coerce=int, validators=[Optional()])
    
    submit = SubmitField('Apply Action')

class TicketSearchForm(FlaskForm):
    search = StringField('Search', render_kw={
        'placeholder': 'Search tickets by title, description, or ticket number...'
    })
    
    status = SelectField('Status', choices=[
        ('', 'All Statuses'),
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('pending', 'Pending'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed')
    ])
    
    priority = SelectField('Priority', choices=[
        ('', 'All Priorities'),
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ])
    
    category_id = SelectField('Category', coerce=int)
    assigned_to = SelectField('Assigned To', coerce=int)
    
    date_from = StringField('From Date', render_kw={'type': 'date'})
    date_to = StringField('To Date', render_kw={'type': 'date'})
    
    sort_by = SelectField('Sort By', choices=[
        ('updated_at', 'Last Updated'),
        ('created_at', 'Created Date'),
        ('priority', 'Priority'),
        ('status', 'Status'),
        ('sla_due_date', 'SLA Due Date')
    ], default='updated_at')
    
    sort_order = SelectField('Order', choices=[
        ('desc', 'Descending'),
        ('asc', 'Ascending')
    ], default='desc')
    
    submit = SubmitField('Search')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Populate category choices
        categories = Category.query.filter_by(is_active=True).order_by(Category.name).all()
        self.category_id.choices = [(0, 'All Categories')] + [(c.id, c.name) for c in categories]
        
        # Populate agent choices
        agents = User.query.filter(
            User.role.in_(['support_agent', 'team_leader']),
            User.is_active == True
        ).order_by(User.first_name, User.last_name).all()
        self.assigned_to.choices = [(0, 'All Agents'), (-1, 'Unassigned')] + [
            (u.id, u.full_name) for u in agents
        ]

class TicketRatingForm(FlaskForm):
    rating = SelectField('Rating', choices=[
        ('1', '1 Star - Very Unsatisfied'),
        ('2', '2 Stars - Unsatisfied'),
        ('3', '3 Stars - Neutral'),
        ('4', '4 Stars - Satisfied'),
        ('5', '5 Stars - Very Satisfied')
    ], validators=[DataRequired()], coerce=int)
    
    feedback = TextAreaField('Feedback', validators=[Optional(), Length(max=1000)], 
                           render_kw={
                               'placeholder': 'Please share your experience with our support (optional)',
                               'rows': 4
                           })
    
    submit = SubmitField('Submit Rating')

class QuickResponseForm(FlaskForm):
    """Form for quick response templates"""
    response_type = SelectField('Quick Response', choices=[
        ('', 'Select a template...'),
        ('acknowledge', 'Acknowledge receipt'),
        ('more_info', 'Request more information'),
        ('working_on_it', 'Working on the issue'),
        ('resolved', 'Issue resolved'),
        ('escalated', 'Escalated to specialist'),
        ('custom', 'Custom response')
    ])
    
    custom_content = TextAreaField('Custom Response', validators=[Optional()],
                                 render_kw={'rows': 4, 'style': 'display: none;'})
    
    is_internal = BooleanField('Internal Note')
    
    submit = SubmitField('Send Response')

class MergeTicketsForm(FlaskForm):
    """Form for merging tickets"""
    primary_ticket_id = HiddenField('Primary Ticket ID', validators=[DataRequired()])
    secondary_ticket_ids = HiddenField('Secondary Ticket IDs', validators=[DataRequired()])
    merge_reason = TextAreaField('Merge Reason', validators=[
        DataRequired(),
        Length(min=10, max=500)
    ], render_kw={
        'placeholder': 'Explain why these tickets should be merged...',
        'rows': 3
    })
    
    submit = SubmitField('Merge Tickets')