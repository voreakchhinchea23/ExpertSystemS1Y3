from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required
from app.forms.dish_forms import DishCreateForm, DishEditForm, DishDeleteConfirmForm, get_ingredient_choices, get_ingredients_grouped_by_category
from app.services.dish_service import DishService
from app.utils.decorators import permission_required 
from app.common.permissions import Perm

dish_bp = Blueprint("tbl_dish", __name__, url_prefix="/dishes")

@dish_bp.route("/")
@login_required
@permission_required(Perm.DISH_READ)
def index():
    dishes = DishService.get_all_dishes()
    return render_template("dishes/index.html", dishes=dishes)


@dish_bp.route("/create", methods=["GET", "POST"])
@login_required
@permission_required(Perm.DISH_CREATE)  
def create():
    form = DishCreateForm()
    
    # Populate choices for the select multiple / multi checkbox
    form.ingredients.choices = get_ingredient_choices()
    
    # Get grouped ingredients for template display
    grouped_ingredients = get_ingredients_grouped_by_category()

    if form.validate_on_submit():
        data = {
            "name": form.name.data,
            "description": form.description.data,
            "recipe_text": form.recipe_text.data,
            "tips": form.tips.data,
            "warnings": form.warnings.data,
            "notes": form.notes.data,
            "image_file": form.image.data if form.image.data else None
        }
        ingredient_ids = form.ingredients.data or []

        dish = DishService.create_dish(data, ingredient_ids)
        flash(f"Dish '{dish.name}' created successfully!", "success")
        return redirect(url_for("tbl_dish.detail", dish_id=dish.id))

    return render_template(
        "dishes/create.html",
        form=form,
        grouped_ingredients=grouped_ingredients
    )


@dish_bp.route("/<int:dish_id>/edit", methods=["GET", "POST"])
@login_required
@permission_required(Perm.DISH_UPDATE)
def edit(dish_id: int):
    dish = DishService.get_dish_by_id(dish_id)
    if not dish:
        abort(404)

    form = DishEditForm(dish=dish)
    
    # Populate choices
    form.ingredients.choices = get_ingredient_choices()
    
    # Grouped for display
    grouped_ingredients = get_ingredients_grouped_by_category()

    if form.validate_on_submit():
        data = {
            "name": form.name.data,
            "description": form.description.data,
            "recipe_text": form.recipe_text.data,
            "tips": form.tips.data,
            "warnings": form.warnings.data,
            "notes": form.notes.data,
            "image_file": form.image.data if form.image.data else None
        }
        ingredient_ids = form.ingredients.data or []

        DishService.update_dish(dish, data, ingredient_ids)
        flash(f"Dish '{dish.name}' updated successfully!", "success")
        return redirect(url_for("tbl_dish.detail", dish_id=dish.id))

    return render_template(
        "dishes/edit.html",
        form=form,
        dish=dish,
        grouped_ingredients=grouped_ingredients
    )


@dish_bp.route("/<int:dish_id>")
@login_required
@permission_required(Perm.DISH_READ)
def detail(dish_id: int):
    dish = DishService.get_dish_by_id(dish_id)
    if not dish:
        abort(404)
    return render_template("dishes/detail.html", dish=dish)


@dish_bp.route("/<int:dish_id>/delete", methods=["GET"])
@login_required
@permission_required(Perm.DISH_DELETE)
def delete_confirm(dish_id: int):
    dish = DishService.get_dish_by_id(dish_id)
    if not dish:
        abort(404)
    
    form = DishDeleteConfirmForm()
    return render_template("dishes/delete_confirm.html", dish=dish, form=form)


@dish_bp.route("/<int:dish_id>/delete", methods=["POST"])
@login_required
@permission_required(Perm.DISH_DELETE)  
def delete(dish_id: int):
    dish = DishService.get_dish_by_id(dish_id)
    if not dish:
        abort(404)
    
    DishService.delete_dish(dish)
    flash("Dish was deleted successfully.", "success")
    return redirect(url_for("tbl_dish.index"))