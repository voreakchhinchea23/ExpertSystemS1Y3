from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    abort
)

perm_bp = Blueprint('tbl_perms', __name__,url_prefix="/permissions")

@perm_bp.route('/')
def index():
    return render_template("permissions/index.html")