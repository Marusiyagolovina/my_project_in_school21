import joblib
import numpy as np
import pandas as pd
import random
from sklearn.metrics import pairwise_distances


class RecipeProcessor:
    def __init__(self, 
                 model_path="best_classification_model.pkl",
                 recipes_path="data/similar_recipes.csv",
                 nutrition_path="data/nutrition_facts.csv"):

        # Загружаем модель
        self.model = joblib.load(model_path)

        # Загружаем рецепты
        self.similar_recipes = pd.read_csv(recipes_path)

        # Загружаем нутриенты (один раз)
        self.nutrition_data = pd.read_csv(nutrition_path, index_col=0)

        # Словарь классов (можно расширять при необходимости)
        self.class_labels = {
            0: "bad",
            1: "so-so",
            2: "great"
        }

    def predict_rating(self, ingredient_vector):
        """Предсказание рейтинга рецепта по вектору ингредиентов"""
        ingredient_vector = np.array(ingredient_vector).reshape(1, -1)
        predicted_class = self.model.predict(ingredient_vector)[0]
        return self.class_labels.get(predicted_class, "unknown")

    def get_nutrition(self, ingredient):
        """Получение информации о нутриентах по названию ингредиента"""
        return self.nutrition_data.loc[ingredient] if ingredient in self.nutrition_data.index else None

    def find_similar_recipes(self, recipe_vector, recipe_data, title_column, top_n=3):
        """
        Поиск похожих рецептов на основе Jaccard similarity
        recipe_vector: бинарный вектор текущего рецепта
        recipe_data: DataFrame с бинарными векторами других рецептов
        title_column: Series с названиями рецептов
        top_n: сколько вернуть рецептов
        """

        # Вычисляем расстояния (Jaccard) и превращаем в схожесть
        similarity = 1 - pairwise_distances(
            [recipe_vector], recipe_data.values, metric="jaccard"
        )[0]

        # Формируем DataFrame с результатами
        df = pd.DataFrame({
            "title": title_column.values,
            "similarity": similarity
        })

        # Сортируем и берём top_n
        top_recipes = df.sort_values(by="similarity", ascending=False).head(top_n)

        # Подтягиваем дополнительную инфу из similar_recipes (если есть совпадения по title)
        merged = pd.merge(top_recipes, self.similar_recipes, on="title", how="left")

        return merged
    
    def generate_daily_menu(self, recipes_df, nutrition_df, daily_values):
        """
        Генерирует меню на день: завтрак, обед, ужин.
        Если нет столбца 'meal_type', он создаётся автоматически по названию рецепта.
        """

        # --- если нет meal_type, создаём ---
        if "meal_type" not in recipes_df.columns:
            def assign_meal_type(title):
                title = str(title).lower()
                if any(word in title for word in ["omelette", "pancake", "muffin", "oatmeal", "toast"]):
                    return "breakfast"
                elif any(word in title for word in ["salad", "sandwich", "soup", "wrap", "bowl"]):
                    return "lunch"
                else:
                    return "dinner"  # всё остальное считаем ужином

            recipes_df["meal_type"] = recipes_df["title"].apply(assign_meal_type)

        menu = []
        meal_types = ["breakfast", "lunch", "dinner"]
        used_nutrients = {nutrient: 0 for nutrient in daily_values.keys()}

        for meal in meal_types:
            # кандидаты для этого приёма пищи
            candidates = recipes_df[recipes_df["meal_type"] == meal]

            if candidates.empty:
                continue

            # сортируем по рейтингу и берём топ-3
            top_candidates = candidates.sort_values(by="rating", ascending=False).head(3)

            chosen_recipe = None
            tries = 0
            while tries < len(top_candidates) and chosen_recipe is None:
                # случайный выбор из топ-3
                candidate = top_candidates.sample(1).iloc[0]
                recipe_nutrients = nutrition_df.loc[candidate["title"]]

                # проверяем нутриенты (чтобы не превысить 100%)
                valid = True
                for nutrient, value in recipe_nutrients.items():
                    if used_nutrients[nutrient] + value > daily_values[nutrient]:
                        valid = False
                        break

                if valid:
                    chosen_recipe = candidate
                tries += 1

            if chosen_recipe is not None:
                # обновляем использованные нутриенты
                recipe_nutrients = nutrition_df.loc[chosen_recipe["title"]]
                for nutrient, value in recipe_nutrients.items():
                    used_nutrients[nutrient] += value

                menu.append({
                    "meal": meal,
                    "title": chosen_recipe["title"],
                    "rating": chosen_recipe["rating"],
                    "ingredients": chosen_recipe["ingredients"].split(","),
                    "nutrients": recipe_nutrients.to_dict(),
                    "url": chosen_recipe["url"]
                })

        return menu