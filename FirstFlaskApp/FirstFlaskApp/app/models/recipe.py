from datetime import datetime
from extensions import db

class RecipeTable(db.Model):
    __tablename__ = "tbl_recipes"

    id = db.Column(db.Integer, primary_key=True)
    dish_id = db.Column(db.Integer, db.ForeignKey("tbl_dishes.id"), unique=True, nullable=False)
    recipe_text = db.Column(db.Text, nullable=False)
    tips = db.Column(db.Text, nullable=True)
    warnings = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    dish = db.relationship("DishTable", back_populates="recipe")

    def __repr__(self):
        return f"<Recipe for dish {self.dish_id}>"