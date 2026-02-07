from .user_forms import UserCreateForm, UserEditForm, UserConfirmDeleteForm
from .role_forms import RoleCreateForm, RoleEditForm, RoleConfirmDeleteForm
from .permission_forms import PermissionCreateForm, PermissionEditForm, PermissionConfirmDeleteForm
from .category_forms import CategoryCreateForm, CategoryEditForm, CategoryConfirmDeleteForm
from .ingredient_forms import IngredientCreateForm, IngredientEditForm, IngredientConfirmDeleteForm
from .dish_forms import  DishCreateForm, DishEditForm, DishDeleteConfirmForm

__all__ = [
    "UserCreateForm",
    "UserEditForm",
    "UserConfirmDeleteForm",
    "RoleCreateForm",
    "RoleEditForm",
    "RoleConfirmDeleteForm",
    "PermissionCreateForm",
    "PermissionEditForm",
    "PermissionConfirmDeleteForm",
    "CategoryCreateForm",
    "CategoryEditForm",
    "CategoryConfirmDeleteForm",
    "IngredientCreateForm",
    "IngredientEditForm",
    "IngredientConfirmDeleteForm",
    "DishCreateForm",
    "DishEditForm",
    "DishDeleteConfirmForm"
]