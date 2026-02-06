from flask import Flask, redirect, url_for
from config import Config
from extensions import db, csrf, login_manager
from flask_login import LoginManager
from app.models import UserTable
from app.common.permissions import Perm

def create_app(config_class: type[Config] = Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    @app.context_processor
    def inject_permissions():
        return {'perm': Perm}
    
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    
    #optional settings
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "warning"
    
    # this function tells flask-login how to load a user form session
    @login_manager.user_loader
    def load_user(user_id):
        return UserTable.query.get(int(user_id))
    
    # register blueprints
    from app.routes.user_routes import user_bp
    from app.routes.auth_routes import auth_bp
    from app.routes.roles_route import role_bp
    from app.routes.permission_route import perm_bp
    from app.routes.category_route import cate_bp
    from app.routes.home_route import home_bp
    
    app.register_blueprint(user_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(role_bp)
    app.register_blueprint(perm_bp)
    app.register_blueprint(cate_bp)
    app.register_blueprint(home_bp)
    
    # add this block so "/" goes to the users list
    @app.route("/")
    def home():
        return redirect(url_for('home.index'))
    
    # create tables
    with app.app_context():
        from app.models import UserTable, RoleTable, PermissionTable, CategoryTable # noqa: F401
        db.create_all()
        
    return app