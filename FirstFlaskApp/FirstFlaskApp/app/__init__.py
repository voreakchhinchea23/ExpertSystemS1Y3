from flask import Flask, redirect, url_for
from config import Config
from extensions import db, csrf, login_manager
from flask_login import LoginManager
from app.models import UserTable
from app.common.permissions import Perm
from app.forms.dish_forms import get_ingredients_grouped_by_category
import os

def create_app(config_class: type[Config] = Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Create upload folder if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    @app.context_processor
    def inject_permissions():
        return {'perm': Perm}
    
    # @app.context_processor
    # def utility_processor():
    #     return dict(
    #         get_ingredients_grouped_by_category=get_ingredients_grouped_by_category
    #     )
    
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
    from app.routes.dashboard_route import dashboard_bp
    from app.routes.ingredient_route import ingredient_bp
    from app.routes.dish_route import dish_bp
    
    app.register_blueprint(user_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(role_bp)
    app.register_blueprint(perm_bp)
    app.register_blueprint(cate_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(ingredient_bp)
    app.register_blueprint(dish_bp)
    
    # add this block so "/" goes to the users list
    @app.route("/")
    def home():
        return redirect(url_for('dashboard.index'))
    
    # create tables
    with app.app_context():
        from app.models import UserTable, RoleTable, PermissionTable, CategoryTable, IngredientTable, DishTable, RecipeTable # noqa: F401
        db.create_all()
        
    return app