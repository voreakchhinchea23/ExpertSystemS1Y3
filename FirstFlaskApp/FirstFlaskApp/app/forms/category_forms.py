from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, StopValidation
from app.models import CategoryTable
from extensions import db

class CategoryCreateForm(FlaskForm):
    name = StringField(
        "Name",
        validators=[DataRequired(), Length(min=1, max=50)],
        render_kw={"placeholder": "ត្រី, សាច់..."}
    )
    description = TextAreaField(
        "Description",
        render_kw={"placeholder": "Short description (optional)"}
    )
    submit = SubmitField("Save")
    
    def validate_name(self, field):
        exists = db.session.scalar(
            db.select(CategoryTable).filter(CategoryTable.name == field.data)
        )
        if exists:
            raise ValidationError("This category already exists.")
    
class CategoryEditForm(FlaskForm):
    name = StringField(
        "Name",
        validators=[DataRequired(), Length(min=1, max=50)],
    )
    description = TextAreaField(
        "Description",
    )
    submit = SubmitField("Update")
    
    def __init__(self, original_category=CategoryTable, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_category = original_category
        
    def validate_name(self, field):
        category = getattr(self, 'obj', None)
        query = db.select(CategoryTable).filter(CategoryTable.name == field.data)        
        # If we have the current category, exclude it from the duplicate check
        if category and category.id:
            query = query.filter(CategoryTable.id != category.id)

        exists = db.session.scalar(query)
        if exists:
            raise ValidationError("This category name is already taken by another category.")
        
class CategoryConfirmDeleteForm(FlaskForm):
    submit = SubmitField("Confirm Delete")
    