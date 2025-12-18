from typing import List, Optional
from app.models.user import UserTable
from app.models.role import RoleTable
from extensions import db

class UserService:
    @staticmethod
    def get_all_users() -> List[UserTable]:
        return UserTable.query.order_by(UserTable.id.asc()).all()
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[UserTable]:
        return UserTable.query.get(user_id)
    
    @staticmethod
    def create_user(data: dict,
                    password: str, 
                    role_id: Optional[int] = None) -> UserTable:
        user = UserTable(
            username=data["username"],
            email=data["email"],
            fullname=data["fullname"],
            is_active=data.get("is_active", True)
        )
        user.set_password(password)
        
        if role_id:
            role = db.session.get(RoleTable, role_id)
            if role:
                user.roles= [role]
        
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def update_user(user: UserTable,
                    data: dict, 
                    password: Optional[str] = None,
                    role_id : Optional[int] = None) -> UserTable:
        
        user.username = data["username"]
        user.email = data["email"]
        user.fullname = data["fullname"]
        user.is_active = data.get("is_active", True)
        
        if password:
            user.set_password(password)
        
        if role_id:
            role = db.session.get(RoleTable, role_id)
            if role:
                user.roles = [role]
        
        db.session.commit()
        return user
    
    @staticmethod
    def delete_user(user: UserTable) -> None:
        db.session.delete(user)
        db.session.commit()