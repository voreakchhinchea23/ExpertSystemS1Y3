from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    abort
)
from flask_login import login_required
from app.common.permissions import Perm
from app.services.ingredient_service import IngredientService
from app.forms.ingredient_forms import *;
from app.utils.decorators import permission_required

ingredient_bp = Blueprint('tbl_ingredient', __name__,url_prefix="/ingredient")

@ingredient_bp.route('/')
@login_required
@permission_required(Perm.INGREDIENT_READ)
def index():
    ingredients = IngredientService.get_all_ingredients()
    return render_template('ingredients/index.html', ingredients=ingredients)

@ingredient_bp.route('/<int:ingredient_id>')
@login_required
@permission_required(Perm.INGREDIENT_READ)
def detail(ingredient_id: int):
    ingredient = IngredientService.get_ingredient_by_id(ingredient_id)
    return render_template('ingredients/detail.html', ingredient=ingredient)

@ingredient_bp.route('/create', methods=["GET","POST"])
@login_required
@permission_required(Perm.INGREDIENT_CREATE)
def create():
    form = IngredientCreateForm()
    if form.validate_on_submit():
        data = {
           "name": form.name.data,
           "category_id": form.category_id.data 
        }
        ingredient = IngredientService.create_ingredient(data)
        flash(f"Ingredient '{ingredient.name}' was created successfully.", "success")
        return redirect(url_for("tbl_ingredient.index"))
    return render_template('ingredients/create.html', form=form)

@ingredient_bp.route('/<int:ingredient_id>/edit', methods=["GET","POST"])
@login_required
@permission_required(Perm.INGREDIENT_UPDATE)
def edit(ingredient_id: int):
    ingredient = IngredientService.get_ingredient_by_id(ingredient_id)
    if ingredient is None:
        abort(404)
        
    form = IngredientEditForm(ingredient=ingredient)
    if form.validate_on_submit():
        data ={
            "name":form.name.data,
            "category_id":form.category_id.data
        }
        IngredientService.update_ingredient(ingredient,data)
        flash(f"Ingredient '{ingredient.name}' was updated successfully.", "success")
        return redirect(url_for("tbl_ingredient.detail", ingredient_id=ingredient.id))
    
    return render_template("ingredients/edit.html", form=form, ingredient=ingredient)

@ingredient_bp.route("/<int:ingredient_id>/delete", methods=["GET"])
@login_required
@permission_required(Perm.INGREDIENT_DELETE)
def delete_confirm(ingredient_id: int):
    ingredient = IngredientService.get_ingredient_by_id(ingredient_id)
    if ingredient is None:
        abort(404)
    
    form = IngredientConfirmDeleteForm()
    return render_template("ingredients/delete_confirm.html", ingredient=ingredient, form=form)

@ingredient_bp.route("/<int:ingredient_id>/delete", methods=["POST"])
@login_required
@permission_required(Perm.INGREDIENT_DELETE)
def delete(ingredient_id: int):
    ingredient = IngredientService.get_ingredient_by_id(ingredient_id)
    if ingredient is None:
        abort(404)
        
    IngredientService.delete_ingredient(ingredient)
    flash("Ingredient was deleted successfully.", "success")
    return redirect(url_for("tbl_ingredient.index"))