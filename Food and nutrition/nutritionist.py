#!/usr/bin/env python3

import sys
from recipes import Ingredients, Recipes, Information, Bonus

def main():
    ingredients_path = 'nutrition_facts.csv'
    recipes_path = 'epi_r.csv'
    best_model = 'best_model.joblib'
    similar_recipes = 'similar_recipes.csv'
    bonus_path = 'bonus.csv'

    joined_params = " ".join(sys.argv[1:])
    params = [p.strip() for p in joined_params.split(",")]
    if len(sys.argv) == 1:
        print('Вы не передали ингредиенты в запросе!')
        return

    my_recipes = Recipes(recipes_path)
    my_ingredients = Ingredients(my_recipes.get_all(), ingredients_path)
    if len(sys.argv) == 2:
        if sys.argv[1] == 'create_bonus':
            my_bonus = Bonus(my_recipes.get_all(), my_ingredients.get_all_ingredients(), ingredients_path)
            my_bonus.breakfast()
            my_bonus.lunch()
            my_bonus.dinner()
            my_bonus.create_menu(bonus_path)
            return
        if sys.argv[1] == 'bonus':
            my_bonus = Bonus(my_recipes.get_all(), my_ingredients.get_all_ingredients(), ingredients_path)
            my_bonus.print_menu(bonus_path, similar_recipes)
            return

    X = my_ingredients.create_vector(params)
    if len(X) == 0:
        return
    y = my_recipes.predict(best_model, X)
    best_recipes = my_recipes.create_best_recipes(similar_recipes)

    my_information = Information(my_ingredients, y, best_recipes)
    my_information.print_on_terminal()

if __name__ == "__main__":
    main()
