from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.forms.role_forms import RoleCreateForm, RoleEditForm, RoleConfirmDeleteForm
from app.services.role_service import RoleService

role_bp = Blueprint('tbl_roles', __name__,url_prefix="/roles")


@role_bp.route('/')
def index():
    roles = RoleService.get_all_roles()
    return render_template("roles/index.html", roles=roles)

@role_bp.route('/create', methods=['GET', 'POST'])
def create():
    form = RoleCreateForm()
    if form.validate_on_submit():
        data = {
            "name" : form.name.data,
            "description" : form.description.data
        }
        
    return render_template("roles/create.html")

@role_bp.route('/edit', methods=['GET', 'POST'])
def edit():
    return render_template("roles/edit.html")

@role_bp.route('/detail', methods=['GET'])
def detail():
    return render_template("roles/detail.html")

@role_bp.route('/delete', methods=['GET', 'POST'])
def delete():
    return render_template("roles/delete.html")