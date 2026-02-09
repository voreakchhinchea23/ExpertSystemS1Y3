from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, SubmitField
from wtforms.validators import Optional, ValidationError

class ExpertIngredientForm(FlaskForm):
    ingredients = SelectMultipleField(
        "Ingredients",
        coerce=int,
        validators=[Optional()]  
    )
    
    submit = SubmitField("Find Matching Dishes")
    
    def validate_ingredients(self, field):
        if len(field.data) > 20:
            raise ValidationError("You can select a maximum of 20 ingredients.")