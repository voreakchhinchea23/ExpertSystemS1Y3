from flask import Blueprint, abort, render_template, request, flash, redirect, url_for
from flask_login import login_required
from app.forms.role_forms import RoleCreateForm, RoleEditForm, RoleConfirmDeleteForm
from app.services.role_service import RoleService
from app.utils.decorators import permission_required
from app.common.permissions import Perm

role_bp = Blueprint('tbl_roles', __name__,url_prefix="/roles")


@role_bp.route('/')
@login_required
@permission_required(Perm.ROLE_READ)
def index():
    roles = RoleService.get_all_roles()
    return render_template("roles/index.html", roles=roles)

@role_bp.route('/create', methods=['GET', 'POST'])
@login_required
@permission_required(Perm.ROLE_CREATE)
def create():
    form = RoleCreateForm()
    if form.validate_on_submit():
        data = {
            "name" : form.name.data,
            "description" : form.description.data,
        }
        permission_ids = form.permission_ids.data or []
        
        role = RoleService.create_role(data, permission_ids)
        flash(f"Role '{role.name}' was created successfully.", "success")
        return redirect(url_for("tbl_roles.index"))
    return render_template("roles/create.html", form=form)

@role_bp.route('/edit/<int:role_id>', methods=['GET', 'POST'])
@login_required
@permission_required(Perm.ROLE_UPDATE)
def edit(role_id: int):
    role = RoleService.get_role_by_id(role_id)
    if role is None:
        abort(404)

    form = RoleEditForm(origial_role=role, obj=role)
    
    if form.validate_on_submit():
        data = {
            "name": form.name.data,
            "description": form.description.data
        }
        permission_ids = form.permission_ids.data or []
        
        RoleService.update_role(role, data, permission_ids)
        flash(f"Role '{role.name}' was updated successfully.", "success")
        return redirect(url_for("tbl_roles.detail", role_id=role.id))
    
    return render_template("roles/edit.html", form=form, role=role)

@role_bp.route('/detail/<int:role_id>', methods=['GET'])
@login_required
@permission_required(Perm.ROLE_READ)
def detail(role_id: int):
    role = RoleService.get_role_by_id(role_id)
    if role is None:
        abort(404)
    return render_template("roles/detail.html", role=role)

@role_bp.route("/<int:role_id>/delete", methods=["GET"])
@login_required
@permission_required(Perm.ROLE_DELETE)
def delete_confirm(role_id:int):
    role = RoleService.get_role_by_id(role_id)
    if role is None:
        abort(404)
        
    form = RoleConfirmDeleteForm()
    return render_template("roles/delete_confirm.html", role=role,form=form)

@role_bp.route("/<int:role_id>/delete", methods=["POST"])
@login_required
@permission_required(Perm.ROLE_DELETE)
def delete(role_id: int):
    role = RoleService.get_role_by_id(role_id)
    if role is None:
        abort(404)
        
    RoleService.delete_role(role)
    flash("Role was deleted successfully.", "success")
    return redirect(url_for("tbl_roles.index"))
