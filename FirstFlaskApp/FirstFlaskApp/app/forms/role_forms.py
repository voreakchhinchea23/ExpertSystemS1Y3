from collections import defaultdict
from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, StopValidation
from .multi_checkbox_field import MultiCheckboxField
from app.models import RoleTable, PermissionTable
from extensions import db

def _permission_choices():
    """Flat (id, label) list, used for field binding only"""
    return [
        (perm.id, f"{perm.code} - {perm.name}")
        for perm in db.session.scalars(
            db.select(PermissionTable).order_by(PermissionTable.code)
        )
    ]

def _permissions_grouped_by_module():
    """
    return permissions grouped by module:
    {
        "Users": [Permission, ...],
        "Roles": [Permission,....],
        ...
    }
    """
    perms = list(
        db.session.scalars(
            db.select(PermissionTable).order_by(
                PermissionTable.module, PermissionTable.code
            )
        )
    )
    grouped = defaultdict(list)
    for perm in perms:
        module = perm.module or "General"
        grouped[module].append(perm)
    return dict(grouped)
    

class RoleCreateForm(FlaskForm):
    name = StringField(
        "Name",
        validators=[DataRequired(), Length(min=1, max=80)],
        render_kw={"placeholder": "Enter role name"}
    )
    description = StringField(
        "Description",
        render_kw={"placeholder": "Short description (optional)"}
    )
    permission_ids = MultiCheckboxField(
        "Permissions",
        coerce=int,
        render_kw={"placeholder": "Permissions granted to this role"}
    )
    
    submit = SubmitField("Save")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.permission_ids.choices = _permission_choices()
        self.permissions_by_module = _permissions_grouped_by_module()
        
    def validate_name(self, field):
        exists = db.session.scalar(
            db.select(RoleTable).filter(RoleTable.name == field.data)
        )
        if exists:
            raise ValidationError("This role name is already taken.")

class RoleEditForm(FlaskForm):
    name = StringField(
        "Name",
        validators=[DataRequired(), Length(min=1, max=80)],

    )
    description = StringField(
        "Description",
    )
    permission_ids = MultiCheckboxField(
        "Permissions",
        coerce=int,
    )
    
    submit = SubmitField("Update")
    
    def __init__(self,origial_role: RoleTable, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_role = origial_role
        self.permission_ids.choices = _permission_choices()
        self.permissions_by_module = _permissions_grouped_by_module()
        
        if not self.is_submitted():
            self.permission_ids.data = [p.id for p in origial_role.permissions]
            
    def validate_name(self, field):
        q = db.select(RoleTable).filter(
            RoleTable.name == field.data,
            RoleTable.id != self.original_role.id,
        )
        exists = db.session.scalar(q)
        if exists:
            raise ValidationError("This role name is already taken.")

class RoleConfirmDeleteForm(FlaskForm):
   submit = SubmitField("Confirm Delete")