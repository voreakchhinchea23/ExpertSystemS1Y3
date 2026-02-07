from extensions import db
from datetime import datetime
from app.models.associations import tbl_dish_ingredients

class DishTable(db.Model):
    __tablename__ = "tbl_dishes"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True) # short description
    image_filename = db.Column(db.String(255), nullable=True)   
    image_mimetype = db.Column(db.String(100), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    recipe = db.relationship("RecipeTable", back_populates="dish", uselist=False, cascade="all, delete-orphan")
    ingredients = db.relationship("IngredientTable", secondary=tbl_dish_ingredients, back_populates="dishes", lazy="dynamic")

    def __repr__(self):
        return f"<Dish {self.name}>"