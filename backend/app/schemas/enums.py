"""
Enum types for recipe preferences
"""
from enum import Enum


class CuisineType(str, Enum):
    NORTH_INDIAN = "North Indian"
    SOUTH_INDIAN = "South Indian"
    EAST_INDIAN = "East Indian"
    WEST_INDIAN = "West Indian"
    ANY = "Any"


class MealType(str, Enum):
    BREAKFAST = "Breakfast"
    LUNCH = "Lunch"
    DINNER = "Dinner"
    SNACK = "Snack"


class DietaryType(str, Enum):
    VEGETARIAN = "Vegetarian"
    NON_VEGETARIAN = "Non-Vegetarian"
    VEGAN = "Vegan"
    JAIN = "Jain"


class SpiceLevel(str, Enum):
    MILD = "Mild"
    MEDIUM = "Medium"
    SPICY = "Spicy"
