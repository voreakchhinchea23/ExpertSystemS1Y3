from datetime import datetime
from extensions import db

class CategoryTable(db.Model):
    __tablename__ = "tbl_categories"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)  
    description = db.Column(db.Text, nullable=True)
    
    # Relationship to ingredients
    #ingredients = db.relationship("IngredientTable", back_populates="category", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Category {self.name}>"