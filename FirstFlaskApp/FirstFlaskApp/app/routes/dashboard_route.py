# app/routes/dashboard_route.py
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user
from app.models import DishTable, IngredientTable, CategoryTable
from app.services.expert_system import run_inference
from app.common.permissions import Perm
from collections import defaultdict
from app.forms.expert_form import ExpertIngredientForm
from app.forms.dish_forms import get_ingredients_grouped_by_category

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/")

def get_ingredients_grouped_by_category():
    ingredients = IngredientTable.query.join(CategoryTable).order_by(CategoryTable.name, IngredientTable.name).all()
    grouped = defaultdict(list)
    for ing in ingredients:
        cat_name = ing.category.name if ing.category else "Uncategorized"
        grouped[cat_name].append(ing)  # full object
    return dict(sorted(grouped.items()))


@dashboard_bp.route("/", methods=["GET", "POST"])
def index():
    form = ExpertIngredientForm()
    form.ingredients.choices = [(ing.id, ing.name) for ing in IngredientTable.query.all()]
    grouped = get_ingredients_grouped_by_category()
    results = None
    selected_ids = []

    if form.validate_on_submit():
        selected_ids = form.ingredients.data or []
        if not selected_ids:
            flash("Please select at least one ingredient.", "warning")
        elif len(form.ingredients.data) > 20:
            flash("Maximum 20 ingredients allowed.", "warning")
        else:
            results = run_inference(selected_ids, min_confidence=0.3)

    return render_template(
        "dashboard/index.html",
        form=form,
        grouped_ingredients=grouped,
        results=results,
        selected_ids=selected_ids,
        current_user=current_user
    )