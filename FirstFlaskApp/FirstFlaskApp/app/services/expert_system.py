# app/services/expert_system.py
from typing import List, Tuple
from app.models import DishTable
from extensions import db


class RecipeRule:
    """
    Wraps a DishTable object for inference.
    """
    def __init__(self, dish: DishTable):
        self.dish = dish
        self.rule_id = dish.id
        self.title = dish.name
        self.description = dish.description or ""
        self.ingredients = list(dish.ingredients) 
        self.solution = dish.recipe.recipe_text if dish.recipe else ""
        self.confidence = dish.confidence  # default 0.8 

    def match_count(self, selected_ingredient_ids: set) -> int:
        return sum(1 for ing in self.ingredients if ing.id in selected_ingredient_ids)


class InferenceEngine:
    def __init__(self):
        self.rules: List[RecipeRule] = []
        self.load_rules()

    def load_rules(self):
        """Load all dishes from database as RecipeRule objects"""
        dishes = db.session.query(DishTable).all()
        self.rules = [RecipeRule(dish) for dish in dishes if dish.ingredients]

    def diagnose(self, selected_ingredient_ids: List[int], min_confidence: float = 0.45) -> List[Tuple[DishTable, float, int, int]]:

        if not selected_ingredient_ids:
            return []

        selected_set = set(selected_ingredient_ids)
        matches = []

        for rule in self.rules:
            total = len(rule.ingredients)
            if total == 0:
                continue

            matched = rule.match_count(selected_set)
            if matched == 0:
                continue

            match_ratio = matched / total
            confidence = rule.confidence * match_ratio
            percentage = round(confidence * 100, 1)

            if confidence >= min_confidence:
                matches.append((rule.dish, percentage, matched, total))

        # Sort by confidence descending
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches