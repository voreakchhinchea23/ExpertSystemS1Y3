from typing import List, Optional
from app.models.category import CategoryTable
from extensions import db

class CategoryService:
    @staticmethod
    def get_all_categories() -> List[CategoryTable]:
        return CategoryTable.query.order_by(CategoryTable.id.asc()).all()
    
    @staticmethod
    def get_category_by_id(cate_id: int) -> Optional[CategoryTable]:
        return CategoryTable.query.get(cate_id)
    
    @staticmethod
    def create_category(data: dict) -> CategoryTable:
        cate = CategoryTable(
            name=data["name"],
            description=data.get("description") or ""
        )
        db.session.add(cate)
        db.session.commit()
        return cate
    
    @staticmethod
    def update_category(cate: CategoryTable,
                    data: dict) -> CategoryTable:
        
        cate.name = data["name"]
        cate.description = data.get("description") or ""
        
        db.session.commit()
        return cate
    
    @staticmethod
    def delete_category(cate: CategoryTable) -> None:
        db.session.delete(cate)
        db.session.commit()