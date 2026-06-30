CATEGORY_MULTIPLIERS = {
    "study": 1.08,
    "coding": 1.12,
    "backend": 1.03,
    "analytics": 1.0,
    "qa": 0.95,
    "admin": 0.9,
}


def category_multiplier(category: str) -> float:
    return CATEGORY_MULTIPLIERS.get(category.strip().lower(), 1.0)
