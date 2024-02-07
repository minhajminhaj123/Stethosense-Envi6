import numpy
import pandas as pd
from pulp import *
import pickle
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer


class Diet:
    def calculate_calorie_requirements(self, gender, age, height_cm, weight_kg):
        # Constants for calorie calculation
        BMR_MALE = 88.362
        BMR_FEMALE = 447.593
        ACTIVITY_MULTIPLIER = 1.375  # Slightly active
        gender = str(gender)
        # Determine BMR based on gender
        if gender.lower() in ('m', 'male'):
            bmr = BMR_MALE
        elif gender.lower() in ('f', 'female'):
            bmr = BMR_FEMALE
        else:
            bmr = (BMR_MALE + BMR_FEMALE)/2

        # Calculate BMR using the Mifflin-St Jeor equation
        bmr += 13.397 * weight_kg + 4.799 * height_cm - 5.677 * age

        return bmr * ACTIVITY_MULTIPLIER

    def __init__(self, height, weight, gender, age):
        self.height = float(height)
        self.weight = float(weight)
        self.gender = str(gender)
        self.age = int(age)
        self.calories = self.calculate_calorie_requirements(
            self.gender, self.age, self.height, self.weight)

    def build_nutritional_values(self):
        protein_calories = self.weight*4
        # res_calories = calories-protein_calories
        carb_calories = self.calories / 2.
        fat_calories = self.calories - carb_calories - protein_calories
        return {
            'Protein Calories': protein_calories,
            'Carbohydrates Calories': carb_calories,
            'Fat Calories': fat_calories
        }

    def extract_gram(self, table):
        protein_grams = table['Protein Calories']/4.
        carbs_grams = table['Carbohydrates Calories']/4.
        fat_grams = table['Fat Calories']/9.
        res = {'Protein Grams': protein_grams,
               'Carbohydrates Grams': carbs_grams, 'Fat Grams': fat_grams}
        return res

    def rec_pattern(self, prob, day):
        with open('./static/days_data.pkl', 'rb') as file:
            days_data = pickle.load(file)

        G = self.extract_gram(self.build_nutritional_values())
        E = G['Carbohydrates Grams']
        F = G['Fat Grams']
        P = G['Protein Grams']
        day_data = days_data[day]
        day_data = day_data[day_data.calories != 0]
        food = day_data.name.tolist()
        c = day_data.calories.tolist()
        x = pulp.LpVariable.dicts(
            "x", indices=food, lowBound=0, upBound=1.5, cat='Continuous', indexStart=[])
        e = day_data.carbohydrate.tolist()
        f = day_data.total_fat.tolist()
        p = day_data.protein.tolist()
        prob = pulp.LpProblem("Diet", LpMinimize)
        prob += pulp.lpSum([x[food[i]]*c[i] for i in range(len(food))])
        prob += pulp.lpSum([x[food[i]]*e[i] for i in range(len(x))]) >= E
        prob += pulp.lpSum([x[food[i]]*f[i] for i in range(len(x))]) >= F
        prob += pulp.lpSum([x[food[i]]*p[i] for i in range(len(x))]) >= P
        prob.solve()
        variables = []
        values = []
        for v in prob.variables():
            variable = v.name
            value = v.varValue
            variables.append(variable)
            values.append(value)
        values = numpy.array(values).round(2).astype(float)
        sol = pd.DataFrame(numpy.array([food, values]).T, columns=[
                           'Food', 'Quantity'])
        sol['Quantity'] = sol.Quantity.astype(float)
        sol = sol[sol['Quantity'] != 0.0]
        sol.Quantity = sol.Quantity*100
        sol = sol.rename(columns={'Quantity': 'Quantity (g)'})
        return sol

    def get_diet_plan(self):
        WEEK_DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        result = []
        for day in WEEK_DAYS:
            prob = pulp.LpProblem("Diet", LpMinimize)
            print('Building a model for day %s \n' % (day))
            result.append(self.rec_pattern(prob, day))
        return dict(zip(WEEK_DAYS, result))

    def get_health_profile(self):
        return {
            'Age': self.age,
            'Weight': self.weight,
            'Height': self.height,
            'Gender': self.gender,
            'Calorie Requirement': round(100 * self.calories) / 100
        }

    def get_todays_recommendation(self):
        nutritional_values = self.extract_gram(self.build_nutritional_values())
        

        dataset = pd.read_csv("recipes.csv")
        COLS = ['RecipeId', 'Name', 'CookTime', 'PrepTime', 'TotalTime', 'RecipeIngredientParts', 'Calories', 'FatContent', 'SaturatedFatContent',
                'CholesterolContent', 'SodiumContent', 'CarbohydrateContent', 'FiberContent', 'SugarContent', 'ProteinContent', 'RecipeInstructions']
        dataset = dataset[COLS]

        max_Calories = 2000
        max_daily_fat = 100
        max_daily_Saturatedfat = 13
        max_daily_Cholesterol = 300
        max_daily_Sodium = 2300
        max_daily_Carbohydrate = 325
        max_daily_Fiber = 40
        max_daily_Sugar = 40
        max_daily_Protein = 200
        max_list = [max_Calories, max_daily_fat, max_daily_Saturatedfat, max_daily_Cholesterol,
            max_daily_Sodium, max_daily_Carbohydrate, max_daily_Fiber, max_daily_Sugar, max_daily_Protein]

        extracted_data = dataset.copy()
        for column, maximum in zip(extracted_data.columns[6:15], max_list):
            extracted_data = extracted_data[extracted_data[column] < maximum]

        extracted_data.RecipeIngredientParts = pd.DataFrame({'RecipeIngredientParts': list(map(
            lambda x: x.lstrip('c(').rstrip(')').replace("\"", ""), extracted_data.RecipeIngredientParts))})
        extracted_data.RecipeInstructions = pd.DataFrame({'RecipeInstructions': list(map(
            lambda x: x.lstrip('c(\"').rstrip('\")').split('", "'), extracted_data.RecipeInstructions))})

        scaler = StandardScaler()
        prep_data = scaler.fit_transform(extracted_data.loc[:, [
                                        'FatContent', 'CarbohydrateContent', 'ProteinContent']].to_numpy())

        neigh = NearestNeighbors(metric='cosine', algorithm='brute')
        neigh.fit(prep_data)

        transformer = FunctionTransformer(neigh.kneighbors, kw_args={
                                        'return_distance': False})
        pipeline = Pipeline([('std_scaler', scaler), ('NN', transformer)])
        pipeline.set_params(
            NN__kw_args={'n_neighbors': 10, 'return_distance': False})

        extracted_data.iloc[pipeline.transform(extracted_data.loc[0:1, [
                                            'FatContent', 'CarbohydrateContent', 'ProteinContent']].to_numpy())[0]]


        

        def scaling(dataframe):
            scaler = StandardScaler()
            prep_data = scaler.fit_transform(
                dataframe.loc[:, ['FatContent', 'CarbohydrateContent', 'ProteinContent']].to_numpy())
            return prep_data, scaler

        def nn_predictor(prep_data):
            neigh = NearestNeighbors(metric='cosine', algorithm='brute')
            neigh.fit(prep_data)
            return neigh

        def build_pipeline(neigh, scaler, params):
            transformer = FunctionTransformer(neigh.kneighbors, kw_args=params)
            pipeline = Pipeline([('std_scaler', scaler), ('NN', transformer)])
            return pipeline

        def extract_data(dataframe, ingredient_filter, max_nutritional_values):
            extracted_data = dataframe.copy()
            for column, maximum in zip(['FatContent', 'CarbohydrateContent', 'ProteinContent'], max_nutritional_values):
                extracted_data = extracted_data[extracted_data[column] < maximum]
            if ingredient_filter != None:
                for ingredient in ingredient_filter:
                    extracted_data = extracted_data[extracted_data['RecipeIngredientParts'].str.contains(
                        ingredient, regex=False)]
            return extracted_data

        def apply_pipeline(pipeline, _input, extracted_data):
            return extracted_data.iloc[pipeline.transform(_input)[0]]

        def recommend(dataframe, _input, max_nutritional_values, ingredient_filter=None, params={'return_distance': False}):
            extracted_data = extract_data(
                dataframe, ingredient_filter, max_nutritional_values)
            prep_data, scaler = scaling(extracted_data)
            neigh = nn_predictor(prep_data)
            pipeline = build_pipeline(neigh, scaler, params)
            return apply_pipeline(pipeline, _input, extracted_data)

        # extracted_data = pickle.load('extracted_data.pkl')
        # max_list = pickle.load('max_list.pkl')

        return dict(recommend(extracted_data, numpy.array(list(nutritional_values.values())[::-1]), max_list))
