# app/services/expert_system.py
from typing import List, Tuple
from app.models import DishTable
from extensions import db


def calculate_combined_cf(match_ratio: float, dish_confidence: float) -> float:
    """
    Combine match ratio with dish confidence using teacher's style:
    combined = match_ratio + dish_confidence × (1 - match_ratio)
    Caps at 1.0 (never 100%)
    """
    combined = match_ratio + dish_confidence * (1 - match_ratio)
    return min(combined, 1.0)


def find_matching_dishes(selected_ingredient_ids: List[int], min_confidence: float = 0.7) -> List[Tuple[DishTable, float, int, int]]:
    """
    Find matching dishes and calculate confidence.
    Only include dishes with at least 1 matched ingredient.
    """
    if not selected_ingredient_ids:
        return []

    selected_set = set(selected_ingredient_ids)
    dishes = db.session.query(DishTable).all()
    results = []

    for dish in dishes:
        if not dish.ingredients:
            continue

        total = dish.ingredients.count()
        if total == 0:
            continue

        matched = sum(1 for ing in dish.ingredients if ing.id in selected_set)

        # IMPORTANT: Skip if ZERO ingredients match
        if matched == 0:
            continue

        match_ratio = matched / total
        combined_cf = calculate_combined_cf(match_ratio, dish.confidence)
        percentage = round(combined_cf * 100, 1)

        if combined_cf >= min_confidence:
            results.append((dish, percentage, matched, total))

    results.sort(key=lambda x: x[1], reverse=True)
    return results