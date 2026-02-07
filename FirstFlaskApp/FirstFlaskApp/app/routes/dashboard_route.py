from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required

dashboard_bp = Blueprint('dashboard', __name__,url_prefix="/dashboard")

@dashboard_bp.route("/")
def index():
    return render_template("dashboard/index.html")