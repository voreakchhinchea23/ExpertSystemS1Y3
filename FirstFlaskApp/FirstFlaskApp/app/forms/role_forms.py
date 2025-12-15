import re
from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, StopValidation

from app.models import Role
from extensions import db

class RoleCreateForm(FlaskForm):
    name = StringField(
        "Name",
        validators=[DataRequired(), Length(min=1, max=80)],
        render_kw={"placeholder": "Enter role name"}
    )
    description = StringField(
        "Description",
        render_kw={"placeholder": "Short description (optional)"}
    )
    