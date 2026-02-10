from typing import List, Optional
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app
from extensions import db
from app.models import DishTable, RecipeTable, IngredientTable

class DishService:
    @staticmethod
    def get_all_dishes() -> List[DishTable]:
        """Return all dishes, ordered by ID ascending."""
        return DishTable.query.order_by(DishTable.name.asc()).all()

    @staticmethod
    def get_dish_by_id(dish_id: int) -> Optional[DishTable]:
        """Get a single dish by ID."""
        return DishTable.query.get(dish_id)

    @staticmethod
    def create_dish(data: dict, ingredient_ids: Optional[List[int]] = None) -> DishTable:
        """
        Create a new dish with recipe and ingredients.
        data should contain: name, description, recipe_text, tips, warnings, notes, image_file (optional)
        """
        dish = DishTable(
            name=data["name"],
            description=data.get("description") or ""
        )
        db.session.add(dish)
        db.session.flush()  # Get dish.id

        # Create linked recipe
        recipe = RecipeTable(
            dish_id=dish.id,
            recipe_text=data["recipe_text"],
            tips=data.get("tips"),
            warnings=data.get("warnings"),
            notes=data.get("notes")
        )
        db.session.add(recipe)

        # Assign ingredients
        if ingredient_ids:
            ingredients = db.session.scalars(
                db.select(IngredientTable).filter(IngredientTable.id.in_(ingredient_ids))
            ).all()
            dish.ingredients = list(ingredients)

        # Handle image upload
        image_file = data.get("image_file")
        if image_file:
            filename = secure_filename(image_file.filename)
            unique_name = f"{dish.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{filename}"
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
            image_file.save(save_path)
            dish.image_filename = unique_name
            dish.image_mimetype = image_file.mimetype

        db.session.commit()
        return dish

    @staticmethod
    def update_dish(dish: DishTable, data: dict, ingredient_ids: Optional[List[int]] = None) -> DishTable:
        """
        Update an existing dish, its recipe, ingredients, and image.
        ingredient_ids=None means "remove all", empty list means "keep current".
        """
        dish.name = data["name"]
        dish.description = data.get("description") or ""

        # Update recipe
        if dish.recipe:
            dish.recipe.recipe_text = data["recipe_text"]
            dish.recipe.tips = data.get("tips")
            dish.recipe.warnings = data.get("warnings")
            dish.recipe.notes = data.get("notes")
        else:
            # Rare case: recipe missing
            recipe = RecipeTable(
                dish_id=dish.id,
                recipe_text=data["recipe_text"],
                tips=data.get("tips"),
                warnings=data.get("warnings"),
                notes=data.get("notes")
            )
            db.session.add(recipe)

        # Update ingredients
        if ingredient_ids is not None:
            dish.ingredients = []
            if ingredient_ids:
                ingredients = db.session.scalars(
                    db.select(IngredientTable).filter(IngredientTable.id.in_(ingredient_ids))
                ).all()
                dish.ingredients = list(ingredients)

        # Handle image replacement
        image_file = data.get("image_file")
        if image_file:
            # Delete old image if exists
            if dish.image_filename:
                old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], dish.image_filename)
                if os.path.exists(old_path):
                    os.remove(old_path)

            filename = secure_filename(image_file.filename)
            unique_name = f"{dish.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{filename}"
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
            image_file.save(save_path)
            dish.image_filename = unique_name
            dish.image_mimetype = image_file.mimetype

        db.session.commit()
        return dish

    @staticmethod
    def delete_dish(dish: DishTable) -> None:
        """Delete dish, its recipe, image file, and associations."""
        # Delete image file
        if dish.image_filename:
            path = os.path.join(current_app.config['UPLOAD_FOLDER'], dish.image_filename)
            if os.path.exists(path):
                os.remove(path)

        # Delete dish (cascade will delete recipe and associations)
        db.session.delete(dish)
        db.session.commit()