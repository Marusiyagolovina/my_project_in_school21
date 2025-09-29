#!/usr/bin/env python3

import argparse
import pandas as pd
import numpy as np
import sys
from recipes import RecipeProcessor


def build_recipe_vector(ingredients, ingredient_columns):
    """
    Построение бинарного вектора для рецепта
    """
    vector = np.zeros(len(ingredient_columns))
    for ingredient in ingredients:
        for i, col in enumerate(ingredient_columns):
            if "/" in col:
                if ingredient in col.split("/"):
                    vector[i] = 1
                    break
            else:
                if ingredient == col:
                    vector[i] = 1
                    break
        else:
            raise ValueError(f"{ingredient} - ingredient not found in database")
    return vector


def print_forecast(recipe_vector, recipe_processor):
    forecast = recipe_processor.predict_rating(recipe_vector)
    print("I. OUR FORECAST")
    print(
        f"You might find it tasty, but in our opinion, it is a {forecast} idea "
        "to have a dish with that list of ingredients.\n"
    )


def print_nutrition_facts(ingredients_list, recipe_processor):
    print("II. NUTRITION FACTS")
    for ingredient in ingredients_list:
        nutrition_info = recipe_processor.get_nutrition(ingredient)
        if nutrition_info is not None:
            print(f"{ingredient.capitalize()}")
            for nutrient, value in nutrition_info.fillna(0).items():
                if value:
                    print(f"{nutrient} - {value}% of Daily Value")
        else:
            print(f"{ingredient.capitalize()} - No nutrition data available.")
        print("")


def print_similar_recipes(recipe_vector, recipe_processor, recipe_data, title_column):
    print("III. TOP-3 SIMILAR RECIPES:")
    similar_recipes = recipe_processor.find_similar_recipes(
        recipe_vector, recipe_data, title_column
    )
    for _, row in similar_recipes.iterrows():
        print(f"- {row['title']}, rating: {row['rating']}, URL: {row['url']}")

def print_daily_menu(menu):
    for item in menu:
        print(item["meal"].upper())
        print("-" * 30)
        print(f"{item['title']} (rating: {item['rating']})")
        print("Ingredients:")
        for ingr in item["ingredients"]:
            print(f"- {ingr.strip()}")
        print("Nutrients:")
        for nut, val in item["nutrients"].items():
            print(f"- {nut}: {val}%")
        print(f"URL: {item['url']}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Find similar recipes and provide insights."
    )
    parser.add_argument(
        "ingredients", nargs="+", help="List of ingredients to use in the recipe."
    )
    args = parser.parse_args()

    # Приводим ингредиенты к единому виду
    user_ingredients = [
        ingredient.replace(",", "").strip().lower() for ingredient in args.ingredients
    ]

    # Загружаем основной датафрейм с рецептами
    data = pd.read_csv("data/epi_r.csv")

    # Загружаем все ингредиенты из файла
    ingredient_columns_raw = (
        pd.read_csv("data/ingredients.csv", header=None).iloc[:, 0].str.strip().tolist()
    )

    # Оставляем только те ингредиенты, которые реально есть в столбцах датафрейма
    ingredient_columns = [col for col in ingredient_columns_raw if col in data.columns]

    if not ingredient_columns:
        raise ValueError("Нет совпадений между ingredients.csv и столбцами в epi_r.csv")

    recipe_data = data[ingredient_columns]

    print(f"Используемые столбцы ингредиентов ({len(ingredient_columns)}): {ingredient_columns}")

    try:
        recipe_vector = build_recipe_vector(user_ingredients, ingredient_columns)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    processor = RecipeProcessor()

    # Последовательный вывод
    print_forecast(recipe_vector, processor)
    print_nutrition_facts(user_ingredients, processor)
    print_similar_recipes(recipe_vector, processor, recipe_data, data["title"])
    daily_menu = processor.generate_daily_menu(user_ingredients, recipe_data, data)
    print_daily_menu(daily_menu)


if __name__ == "__main__":
    main()