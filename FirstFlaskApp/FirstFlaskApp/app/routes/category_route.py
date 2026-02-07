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
from app.services.category_service import CategoryService
from app.forms.category_forms import *;
from app.utils.decorators import permission_required

cate_bp = Blueprint('tbl_cate', __name__,url_prefix="/categories")

@cate_bp.route('/')
@login_required
@permission_required(Perm.CATE_READ)
def index():
    categories = CategoryService.get_all_categories()
    return render_template("categories/index.html", categories=categories)

@cate_bp.route('/create', methods=["GET", "POST"])
@login_required
@permission_required(Perm.CATE_CREATE)
def create():
    form = CategoryCreateForm()
    if form.validate_on_submit():
        data = {
            "name" : form.name.data,
            "description" : form.description.data,
        }
        cate = CategoryService.create_category(data)
        flash(f"Category '{cate.name}' was created successfully.", "success")
        return redirect(url_for("tbl_cate.index"))
    return render_template("categories/create.html", form=form)

@cate_bp.route("/<int:cate_id>")
@login_required
@permission_required(Perm.CATE_READ)
def detail(cate_id: int):
    category = CategoryService.get_category_by_id(cate_id)
    if category is None:
        abort(404)
    return render_template("categories/detail.html", category=category)

@cate_bp.route('/edit/<int:cate_id>', methods=['GET', 'POST'])
@login_required
@permission_required(Perm.CATE_UPDATE)
def edit(cate_id: int):
    category = CategoryService.get_category_by_id(cate_id)
    if category is None:
        abort(404)
    
    form = CategoryEditForm(original_category=category, obj = category)
    if form.validate_on_submit():
        data = {
            "name": form.name.data,
            "description":form.description.data
        }
        
        CategoryService.update_category(category, data)
        flash(f"Category '{category.name}' was updated successfully.", "success")
        return redirect(url_for("tbl_cate.detail", cate_id=category.id))
    
    return render_template("categories/edit.html", form=form, category=category)

@cate_bp.route("/<int:cate_id>/delete", methods=["GET"])
@login_required
@permission_required(Perm.CATE_DELETE)
def delete_confirm(cate_id: int):
    category = CategoryService.get_category_by_id(cate_id)
    if category is None:
        abort(404)
    
    form = CategoryConfirmDeleteForm()
    return render_template("categories/delete_confirm.html", category=category, form=form)

@cate_bp.route("/<int:cate_id>/delete", methods=["POST"])
@login_required
@permission_required(Perm.CATE_DELETE)
def delete(cate_id: int):
    category = CategoryService.get_category_by_id(cate_id)
    if category is None:
        abort(404)
        
    CategoryService.delete_category(category)
    flash("Category was deleted successfully.", "success")
    return redirect(url_for("tbl_cate.index"))