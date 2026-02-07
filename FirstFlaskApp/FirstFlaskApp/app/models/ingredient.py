from extensions import db
from datetime import datetime
from app.models.associations import tbl_dish_ingredients

class IngredientTable(db.Model):
    __tablename__ = "tbl_ingredients"
    
    id = db.Column(db.Integer, primary_key=True) 
    name = db.Column(db.String(100), unique=True, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("tbl_categories.id"), nullable=False) # one-to-many relationship
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,onupdate=datetime.utcnow, nullable=False)
    
    category = db.relationship("CategoryTable", back_populates="ingredients")
    dishes = db.relationship("DishTable",secondary=tbl_dish_ingredients, back_populates="ingredients")
    
    def __repr__(self):
        return f"<Ingredient {self.name} (id={self.id})>"