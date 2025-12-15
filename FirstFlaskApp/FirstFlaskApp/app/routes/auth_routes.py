from flask import Blueprint, render_template, request, flash, redirect, url_for


auth_bp = Blueprint('auth', __name__,url_prefix="/auth")


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    return render_template("auth/login.html")