from flask import Blueprint, render_template, request, flash, redirect, url_for


role_bp = Blueprint('roles', __name__,url_prefix="/roles")


@role_bp.route('/')
def index():
    return render_template("roles/index.html")

@role_bp.route('/create', methods=['GET', 'POST'])
def create():
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