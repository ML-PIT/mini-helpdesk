from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length, Optional
from app.models.knowledge import KnowledgeCategory

class ArticleForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=5, max=200)])
    summary = StringField('Summary', validators=[Optional(), Length(max=500)])
    content = TextAreaField('Content', validators=[DataRequired(), Length(min=50)])
    category_id = SelectField('Category', coerce=int, validators=[Optional()])
    tags = StringField('Tags', validators=[Optional()], 
                      description='Comma-separated tags')
    is_public = BooleanField('Public Article', default=True)
    is_featured = BooleanField('Featured Article', default=False)
    submit = SubmitField('Create Article')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = KnowledgeCategory.query.filter_by(is_active=True).all()
        self.category_id.choices = [(0, 'No Category')] + [
            (c.id, c.name) for c in categories
        ]

class CategoryForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    submit = SubmitField('Create Category')

class FAQForm(FlaskForm):
    question = StringField('Question', validators=[DataRequired(), Length(max=500)])
    answer = TextAreaField('Answer', validators=[DataRequired()])
    category_id = SelectField('Category', coerce=int, validators=[Optional()])
    is_featured = BooleanField('Featured FAQ', default=False)
    sort_order = IntegerField('Sort Order', default=0)
    submit = SubmitField('Create FAQ')