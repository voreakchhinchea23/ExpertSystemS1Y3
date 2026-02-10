from typing import List, Optional
from app.models.ingredient import IngredientTable
from extensions import db

class IngredientService:
    @staticmethod
    def get_all_ingredients() -> List[IngredientTable]:
        return IngredientTable.query.order_by(IngredientTable.name.asc()).all()
    
    @staticmethod
    def get_ingredient_by_id(ingredient_id: int) -> Optional[IngredientTable]:
        return IngredientTable.query.get(ingredient_id)
    
    @staticmethod
    def create_ingredient(data: dict) -> IngredientTable:
        ingredient = IngredientTable(
            name=data["name"],
            category_id=data["category_id"]
        )
        db.session.add(ingredient)
        db.session.commit()
        return ingredient
    
    @staticmethod
    def update_ingredient(ingredient: IngredientTable,
                    data: dict) -> IngredientTable:
        
        ingredient.name = data["name"]
        ingredient.category_id = data["category_id"]
        
        db.session.commit()
        return ingredient
    
    @staticmethod
    def delete_ingredient(ingredient: IngredientTable) -> None:
        db.session.delete(ingredient)
        db.session.commit()