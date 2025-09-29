import pandas as pd
import joblib

#Класс для работы с ингредиентами
class Ingredients:
    #Конструктор, который определяет все ингредиенты
    def __init__(self, main_df, ingredients_path):
        df = pd.read_csv(ingredients_path)
        all_ingredients = df['ingredient'].to_list()
        self.ingredients_path = ingredients_path
        self.all_ingredients = [column for column in main_df.columns if column in all_ingredients]

    #Возвращает все ингредиенты
    def get_all_ingredients(self):
        return self.all_ingredients

    #Создаёт вектор с данными, если переданные ингредиенты существуют
    def create_vector(self, new_ingredients):
        self.new_ingredients = new_ingredients
        false_ingredients = []
        for ingredient in new_ingredients:
            if ingredient not in self.all_ingredients:
                false_ingredients.append(ingredient)
        if len(false_ingredients) > 0:
            print('the following ingredients are missing in our database:', ', '.join(false_ingredients))
            return pd.DataFrame()
        vector = [1 if column in new_ingredients else 0 for column in self.all_ingredients]
        return pd.DataFrame([vector], columns=self.all_ingredients)

    def create_list_nutritions(self):
        df = pd.read_csv(self.ingredients_path)
        return df[df['ingredient'].isin(self.new_ingredients)]

#Класс для работы с рецептами
class Recipes:
    def __init__(self, recipes_path):
        df = pd.read_csv(recipes_path)
        for column in df.columns:
            if '/' in column:
                new_name_column = column.split('/')[0]
                df.rename(columns={column: new_name_column}, inplace=True)
            if ' or ' in column:
                new_name_column = column.split(' or ')[0]
                df.rename(columns={column: new_name_column}, inplace=True)
        self.all_data = df

    #Возвращает DataFrame с нашими первоначальными данными
    def get_all(self):
        return self.all_data

    #Предсказывает результат на основе модели и ингредиентов
    def predict(self, model_path, X):
        self.X = X
        model = joblib.load(model_path)
        y = model.predict(X)
        if y[0] not in ['bad', 'so-so', 'great']:
            if y[0] < 1.5:
                y[0] = 'bad'
            elif y[0] < 3.5:
                y[0] = 'so-so'
            else:
                y[0] = 'great'
        return y[0]

    #Создаёт список самых лучших блюд по данным ингредиентам
    def create_best_recipes(self, similar_recipes):
        df = pd.read_csv(similar_recipes)
        main_df = self.all_data.copy()
        for column in self.X.columns:
            if column == 'avocado' or column == 'garlic':
                continue
            try:
                if self.X[column].loc[0] == 1:
                    main_df = main_df[main_df[column] == 1]
            except:
                pass
        main_df = main_df.sort_values(by=['rating', 'title'], ascending=[False, True])
        best_recipes = []
        for title in main_df['title']:
            if title in df['title'].values:
                row = df.loc[df['title'] == title]
                best_recipes.append((row['title'].values[0], row['rating'].values[0], row['url'].values[0]))
            if len(best_recipes) == 3:
                break
        return best_recipes

#Класс для вывода на экран
class Information:
    def __init__(self, ingredients, y, best_recipes):
        self.ingredients = ingredients
        self.y = y
        self.best_recipes = best_recipes

    #Вывод на экран первой части
    def one_part(self):
        print('I. OUR FORECAST')
        print(f'You might find it tasty, but in our opinion, it is a {self.y} idea to have a dish with that list of ingredients.')

     # Вывод на экран второй части
    def two_part(self):
        print('II. NUTRITION FACTS')
        df_nutritions = self.ingredients.create_list_nutritions()
        for ingredient in self.ingredients.new_ingredients:
            print(ingredient)
            row = df_nutritions[df_nutritions['ingredient'] == ingredient]
            for col in df_nutritions.columns[1:]:
                value = row[col].iloc[0]
                if value > 0:
                    print(f'{col} - {value}% of Daily Value')

    # Вывод на экран третий части
    def three_part(self):
        if len(self.best_recipes) == 0:
            print('III. THERE ARE NO SIMILAR RECIPES')
        else:
            print(f'III. TOP-{len(self.best_recipes)} SIMILAR RECIPES:')
            for recipe in self.best_recipes:
                print(f'- {recipe[0]}, rating: {recipe[1]}, URL: {recipe[2]}')

    #Вывод всего на экран
    def print_on_terminal(self):
        self.one_part()
        self.two_part()
        self.three_part()

#Класс для бонусной части
class Bonus:
    def __init__(self, main_df, all_ingredients, ingredients_path):
        self.main_df = main_df.copy()
        self.all_ingredients = all_ingredients
        self.ingredients_path = ingredients_path

    def breakfast(self):
        df_breakfast = self.main_df.copy()
        df_breakfast = df_breakfast[df_breakfast['breakfast'] == 1]
        df_nutritions = pd.read_csv(self.ingredients_path)
        df_nutritions = df_nutritions.fillna(0)
        result = []
        for i in range(len(df_breakfast)):
            if df_breakfast.iloc[i]['rating'] < 4.8:
                continue
            row = dict()
            row['title'] = df_breakfast.iloc[i]['title']
            row['rating'] = df_breakfast.iloc[i]['rating']
            for column in df_nutritions.columns:
                if column != 'ingredient':
                    row[column] = 0
            for ingredient in self.all_ingredients:
                try:
                    if df_breakfast.iloc[i][ingredient] == 1:
                        row_tmp = df_nutritions[df_nutritions['ingredient'] == ingredient].iloc[0]
                        for column in df_nutritions.columns:
                            if column != 'ingredient':
                                row[column] += row_tmp[column]
                except:
                    pass
            flag = True
            for column in df_nutritions.columns:
                if column != 'ingredient':
                    if row[column] > 100:
                        flag = False
            if flag:
                result.append(row)
        self.my_breakfast = pd.DataFrame(result)

    def lunch(self):
        df_lunch = self.main_df.copy()
        df_lunch = df_lunch[df_lunch['lunch'] == 1]
        df_nutritions = pd.read_csv(self.ingredients_path)
        df_nutritions = df_nutritions.fillna(0)
        result = []
        for i in range(len(df_lunch)):
            if df_lunch.iloc[i]['rating'] < 4.8:
                continue
            row = dict()
            row['title'] = df_lunch.iloc[i]['title']
            row['rating'] = df_lunch.iloc[i]['rating']
            for column in df_nutritions.columns:
                if column != 'ingredient':
                    row[column] = 0
            for ingredient in self.all_ingredients:
                try:
                    if df_lunch.iloc[i][ingredient] == 1:
                        row_tmp = df_nutritions[df_nutritions['ingredient'] == ingredient].iloc[0]
                        for column in df_nutritions.columns:
                            if column != 'ingredient':
                                row[column] += row_tmp[column]
                except:
                    pass
            flag = True
            for column in df_nutritions.columns:
                if column != 'ingredient':
                    if row[column] > 100:
                        flag = False
            if flag:
                result.append(row)
        self.my_lunch = pd.DataFrame(result)

    def dinner(self):
        df_dinner = self.main_df.copy()
        df_dinner = df_dinner[df_dinner['dinner'] == 1]
        df_nutritions = pd.read_csv(self.ingredients_path)
        df_nutritions = df_nutritions.fillna(0)
        result = []
        for i in range(len(df_dinner)):
            if df_dinner.iloc[i]['rating'] < 5:
                continue
            row = dict()
            row['title'] = df_dinner.iloc[i]['title']
            row['rating'] = df_dinner.iloc[i]['rating']
            for column in df_nutritions.columns:
                if column != 'ingredient':
                    row[column] = 0
            for ingredient in self.all_ingredients:
                try:
                    if df_dinner.iloc[i][ingredient] == 1:
                        row_tmp = df_nutritions[df_nutritions['ingredient'] == ingredient].iloc[0]
                        for column in df_nutritions.columns:
                            if column != 'ingredient':
                                row[column] += row_tmp[column]
                except:
                    pass
            flag = True
            for column in df_nutritions.columns:
                if column != 'ingredient':
                    if row[column] > 100:
                        flag = False
            if flag:
                result.append(row)
        self.my_dinner = pd.DataFrame(result)

    def create_menu(self, bonus_path):
        result = []
        for i in range(len(self.my_breakfast)):
            for j in range(len(self.my_lunch)):
                for k in range(len(self.my_dinner)):
                    df_tmp = pd.concat([self.my_breakfast.iloc[[i]], self.my_lunch.iloc[[j]], self.my_dinner.iloc[[k]]], ignore_index=True)
                    summed = df_tmp.sum(numeric_only=True)
                    if (summed <= 100).all():
                        result.append({
                            "breakfast": df_tmp.iloc[0]['title'],
                            "lunch": df_tmp.iloc[1]['title'],
                            "dinner": df_tmp.iloc[2]['title']})
        menu_df = pd.DataFrame(result)
        menu_df.to_csv(bonus_path)

    def print_menu(self, bonus_path, similar_recipes):
        df = pd.read_csv(bonus_path)
        row = df.sample(n=1)
        my_breakfast = row.iloc[0]['breakfast']
        my_breakfast_rating = self.main_df[self.main_df['title'] == my_breakfast]['rating'].values[0]
        my_lunch = row.iloc[0]['lunch']
        my_lunch_rating = self.main_df[self.main_df['title'] == my_lunch]['rating'].values[0]
        my_dinner = row.iloc[0]['dinner']
        my_dinner_rating = self.main_df[self.main_df['title'] == my_dinner]['rating'].values[0]
        df_nutritions = pd.read_csv(self.ingredients_path)
        df_nutritions = df_nutritions.fillna(0)
        df_sim = pd.read_csv(similar_recipes)

        row = dict()
        for column in df_nutritions.columns:
            if column != 'ingredient':
                row[column] = 0
        print('BREAKFAST')
        print('---------------------')
        print(f'{my_breakfast} (rating: {my_breakfast_rating})')
        print('Ingredients:')
        for column in self.all_ingredients:
            if column != 'ingredient':
                try:
                    if self.main_df[self.main_df['title'] == my_breakfast][column].values[0] == 1:
                        print(f'- {column}')
                        row_tmp = df_nutritions[df_nutritions['ingredient'] == column].iloc[0]
                        for column2 in df_nutritions.columns:
                            if column2 != 'ingredient':
                                row[column2] += row_tmp[column2]
                except:
                    pass
        print('Nutrients:')
        for key, value in row.items():
            if value > 0:
                print(f'- {key}: {value}%')
        print(f"URL: {df_sim[df_sim['title'] == my_breakfast]['url'].values[0]}")

        row = dict()
        for column in df_nutritions.columns:
            if column != 'ingredient':
                row[column] = 0
        print('LUNCH')
        print('---------------------')
        print(f'{my_lunch} (rating: {my_lunch_rating})')
        print('Ingredients:')
        for column in self.all_ingredients:
            if column != 'ingredient':
                try:
                    if self.main_df[self.main_df['title'] == my_lunch][column].values[0] == 1:
                        print(f'- {column}')
                        row_tmp = df_nutritions[df_nutritions['ingredient'] == column].iloc[0]
                        for column2 in df_nutritions.columns:
                            if column2 != 'ingredient':
                                row[column2] += row_tmp[column2]
                except:
                    pass
        print('Nutrients:')
        for key, value in row.items():
            if value > 0:
                print(f'- {key}: {value}%')
        print(f"URL: {df_sim[df_sim['title'] == my_lunch]['url'].values[0]}")

        row = dict()
        for column in df_nutritions.columns:
            if column != 'ingredient':
                row[column] = 0
        print('DINNER')
        print('---------------------')
        print(f'{my_dinner} (rating: {my_dinner_rating})')
        print('Ingredients:')
        for column in self.all_ingredients:
            if column != 'ingredient':
                try:
                    if self.main_df[self.main_df['title'] == my_dinner][column].values[0] == 1:
                        print(f'- {column}')
                        row_tmp = df_nutritions[df_nutritions['ingredient'] == column].iloc[0]
                        for column2 in df_nutritions.columns:
                            if column2 != 'ingredient':
                                row[column2] += row_tmp[column2]
                except:
                    pass
        print('Nutrients:')
        for key, value in row.items():
            if value > 0:
                print(f'- {key}: {value}%')
        print(f"URL: {df_sim[df_sim['title'] == my_dinner]['url'].values[0]}")
