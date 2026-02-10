# app/services/expert_system.py
from typing import List, Tuple
from app.models import DishTable
from extensions import db


def calculate_combined_cf(match_ratio: float, dish_confidence: float) -> float:
    """
    Combine match ratio with dish confidence using simple multiplication.
    
    Formula: match_ratio × dish_confidence
    
    Examples:
    - 2/12 ingredients (16.7%) × 0.8 = 13.4% ✓ (realistic!)
    - 6/12 ingredients (50%) × 0.8 = 40% ✓
    - 12/12 ingredients (100%) × 0.8 = 80% ✓ (perfect match!)
    """
    return match_ratio * dish_confidence


def run_inference(selected_ingredient_ids: List[int], min_confidence: float = 0.3) -> List[Tuple[DishTable, float, int, int]]:
    """
    Inference engine: finds and ranks matching dishes using selected ingredients and per-dish confidence.
    Returns: [(dish, percentage, matched_count, total_ingredients), ...]
    Sorted by confidence descending
    
    Note: min_confidence lowered to 0.3 (30%) because new formula is more realistic
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

        # Skip if ZERO ingredients match
        if matched == 0:
            continue

        match_ratio = matched / total
        combined_cf = calculate_combined_cf(match_ratio, dish.confidence)
        percentage = round(combined_cf * 100, 1)

        if combined_cf >= min_confidence:
            results.append((dish, percentage, matched, total))

    results.sort(key=lambda x: x[1], reverse=True)
    return results
