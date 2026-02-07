# app/forms/dish_forms.py
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, ValidationError
from app.models import IngredientTable, DishTable, CategoryTable
from extensions import db
from collections import defaultdict

# Custom multi-checkbox (keep this)
from wtforms import SelectMultipleField
from wtforms.widgets import ListWidget, CheckboxInput

class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()


def get_ingredient_choices():
    """Flat list for field binding"""
    return [
        (ing.id, ing.name)
        for ing in db.session.scalars(
            db.select(IngredientTable).order_by(IngredientTable.name)
        )
    ]


def get_ingredients_grouped_by_category():
    """Grouped for template display"""
    ingredients = db.session.scalars(
        db.select(IngredientTable)
          .join(CategoryTable)
          .order_by(CategoryTable.name, IngredientTable.name)
    ).all()
    grouped = defaultdict(list)
    for ing in ingredients:
        cat_name = ing.category.name if ing.category else "Uncategorized"
        grouped[cat_name].append(ing)
    return dict(sorted(grouped.items()))


class DishCreateForm(FlaskForm):
    name = StringField(
        "Dish Name",
        validators=[DataRequired(), Length(min=2, max=150)],
        render_kw={"placeholder": "Enter dish name"}
    )
    description = TextAreaField(
        "Description",
        render_kw={"placeholder": "Short description (optional)"}
    )
    ingredients = MultiCheckboxField(
        "Ingredients",
        coerce=int,
        render_kw={"placeholder": "Select ingredients"}
    )
    recipe_text = TextAreaField(
        "Recipe Instructions",
        validators=[DataRequired(), Length(min=30)],
        render_kw={"rows": 10}
    )
    tips = TextAreaField("Tips", render_kw={"rows": 4})
    warnings = TextAreaField("Warnings", render_kw={"rows": 4})
    notes = TextAreaField("Notes", render_kw={"rows": 4})
    image = FileField(
        "Dish Image (optional)",
        validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'])]
    )
    submit = SubmitField("Save")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ingredients.choices = get_ingredient_choices()
        self.grouped_ingredients = get_ingredients_grouped_by_category()

    def validate_name(self, field):
        if DishTable.query.filter_by(name=field.data).first():
            raise ValidationError("This dish name is already taken.")


class DishEditForm(FlaskForm):
    name = StringField(
        "Dish Name",
        validators=[DataRequired(), Length(min=2, max=150)]
    )
    description = TextAreaField("Description")
    ingredients = MultiCheckboxField("Ingredients", coerce=int)
    recipe_text = TextAreaField("Recipe Instructions", validators=[DataRequired(), Length(min=30)], render_kw={"rows": 10})
    tips = TextAreaField("Tips", render_kw={"rows": 4})
    warnings = TextAreaField("Warnings", render_kw={"rows": 4})
    notes = TextAreaField("Notes", render_kw={"rows": 4})
    image = FileField("Dish Image (optional)", validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'])])
    submit = SubmitField("Update")

    def __init__(self, dish=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dish = dish
        self.ingredients.choices = get_ingredient_choices()
        self.grouped_ingredients = get_ingredients_grouped_by_category()

        if dish and not self.is_submitted():
            self.name.data = dish.name
            self.description.data = dish.description
            self.ingredients.data = [ing.id for ing in dish.ingredients]
            if dish.recipe:
                self.recipe_text.data = dish.recipe.recipe_text
                self.tips.data = dish.recipe.tips
                self.warnings.data = dish.recipe.warnings
                self.notes.data = dish.recipe.notes

    def validate_name(self, field):
        if not self.dish:
            return
        query = db.select(DishTable).filter(DishTable.name == field.data)
        if self.dish.id:
            query = query.filter(DishTable.id != self.dish.id)
        if db.session.scalar(query):
            raise ValidationError("This dish name is already taken by another dish.")


class DishDeleteConfirmForm(FlaskForm):
    submit = SubmitField("Yes, Delete", render_kw={"class": "btn btn-danger"})