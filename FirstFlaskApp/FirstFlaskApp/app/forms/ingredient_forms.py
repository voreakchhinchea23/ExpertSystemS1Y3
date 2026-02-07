from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from extensions import db
from app.models import IngredientTable, CategoryTable

# helper
def _category_choices():
    """Return list of (id, name) tuples for all category, order by id."""
    return [
        (category.id, category.name)
        for category in db.session.scalars(
            db.select(CategoryTable).order_by(CategoryTable.id)
        )
    ]

class IngredientCreateForm(FlaskForm):
    name = StringField(
        "Name", validators=[DataRequired(), Length(min=1, max=100)],
        render_kw={"placeholder": "បញ្ចូលឈ្មោះគ្រឿងផ្សំ"})
    
    category_id = SelectField(
        "Category",
        coerce=int,
        validators=[DataRequired()],
        choices=[] ,
    )
    submit = SubmitField("Save")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category_id.choices =  _category_choices()
    
    def validate_name(self, field):
        if IngredientTable.query.filter_by(name=field.data).first():
            raise ValidationError("This ingredient name already exists.")

class IngredientEditForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=1, max=100)])
    
    category_id = SelectField(
        "Category",
        coerce=int,
        validators=[DataRequired()],
        choices=[]
    )
    submit = SubmitField("Update")
    
    def __init__(self, ingredient=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ingredient = ingredient
        self.category_id.choices = _category_choices()
        
        if ingredient and not self.is_submitted():
            self.name.data = ingredient.name
            self.category_id.data = ingredient.category_id

    def validate_name(self, field):
        """
        Allow the same name if it's the current ingredient being edited,
        but block duplicates from other ingredients
        """
        if not self.ingredient:
            return

        query = db.select(IngredientTable).filter(IngredientTable.name == field.data)
        
        if self.ingredient.id:
            query = query.filter(IngredientTable.id != self.ingredient.id)

        exists = db.session.scalar(query)
        if exists:
            raise ValidationError("This ingredient name is already taken by another ingredient.")
        
class IngredientConfirmDeleteForm(FlaskForm):
    submit = SubmitField("Confirm Delete")