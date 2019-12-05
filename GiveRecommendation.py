import pandas as pd
import numpy as np
from keras.models import Model
from keras.models import load_model
import sys
import re

# supress errors in terminal
class DevNull:
    def write(self, msg):
        pass

sys.stderr = DevNull()

# surpress tensorflow messages
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

#read data 
recipes_ids_dinner = pd.read_csv('result_MF_Dinner.csv')
recipes_ids_dessert = pd.read_csv('result_dessertMF.csv')
recipes_ids_breakfast = pd.read_csv('result_breakfastMF.csv')
recipes2 = pd.read_csv('./food-com-recipes-and-user-interactions/RAW_recipes.csv')
recipes = recipes2.rename(columns = {'id':'recipe_id'})
user_df = pd.read_csv('user_df.csv')
done_recc = pd.read_csv('done_recommendations.csv')

# load models
breakfast_model = load_model('Breakfast_MF_U10R10.h5') # nog aan het trainen
dinner_model = load_model('Dinner_MF_R10U10_scale.h5') # nog juiste aantal epochs vinden 
dessert_model = load_model('Dessert_MF_R10U10.h5')

# empty user dictionary for new users 
user_dict = {}

# define functions 
def base_rating(recipes_course_df, all_recipes):
    base_rating = {}
    to_rate = recipes_course_df.sample(5).reset_index()
    for i in range(5): 
        step = 1
        sub_dic = {} 
        id_recipe = to_rate.recipe_id[i]

        recipe = all_recipes[all_recipes.recipe_id == id_recipe]

        # Title
        print('\nTitle:\n', recipe.name.values[0].title())
        # Time 
        print('\nTime to make:', recipe.minutes.values[0], 'minutes\n')
        # Ingredients 
        print('Ingredients:')
        ingredients = recipe.ingredients.values[0]
        ingredient = ingredients.split(',')
        for j in range(len(ingredient)):
            ingredient2 = ingredient[j].lstrip('[')
            ingredient3 = ingredient2.strip('\'')
            ingredient4 = ingredient3.rstrip(']')
            ingredient5 = ingredient4.lstrip(" '")
            ingredient6 = ingredient5.rstrip('\'')
            print('-', ingredient6.capitalize())

        # steps
        print('\nInstructions:')
        steps = recipe.steps.values[0]
        stappen = re.sub('\'', '', steps)
        step2 = stappen.lstrip('[')
        step3 = step2.rstrip(']')
        print(step3)

        while step == 1: 
            rating = int(input('How tasty do you think this recipe will be?\nPlease rate from 0 - 5.\n'))
            if rating == 0 or rating == 1 or rating == 2 or rating == 3 or rating == 4 or rating == 5:
                step += 1
            else:
                print('Oops! That input is not correct. Please choose numbers between 0 and 5.')
                continue

        sub_dic['user_id'] = user_id
        sub_dic['recipe_id'] = id_recipe
        sub_dic['rating'] = rating

        base_rating[i] = sub_dic
    return base_rating

# get recommendations 
def recommendation(ratings, model, user_id):
    recipe_ids = ratings.recipe_id.unique()
    user = np.array([user_id for i in range(len(recipe_ids))])

    predictions = model.predict([user, recipe_ids])
    predictions = np.array([a[0] for a in predictions])
    recommended_recipe_ids = (-predictions).argsort()[:500]
    
    return list(zip(recommended_recipe_ids, predictions[recommended_recipe_ids]))

# change recipe_id and user_id
def change_number(unique_lst):
    unique = pd.DataFrame(unique_lst).reset_index()
    indexes = unique['index']
    ids = unique[0]
    tuple_zip = list(zip(ids, indexes))
    dic = dict((x, y) for x, y in tuple_zip)
    reverse_dic = dict((y, x) for x, y in tuple_zip)
    return dic, reverse_dic

# give recommendation 
def recommendation_recipe(recommendation):
    dic_rated = {}
    print('\nTitle:\n', recommendation.name.values[0].title())
    
    print('\nTime to make:', recommendation.minutes.values[0], 'minutes\n')

    # Ingredients 
    print('Ingredients:')

    ingredients = recommendation.ingredients.values[0]
    ingredient = ingredients.split(',')
    for i in range(len(ingredient)):
        ingredient2 = ingredient[i].lstrip('[')
        ingredient3 = ingredient2.strip('\'')
        ingredient4 = ingredient3.rstrip(']')
        ingredient5 = ingredient4.lstrip(" '")
        ingredient6 = ingredient5.rstrip('\'')
        print('-', ingredient6.capitalize())

    # steps
    print('\nInstructions:')
    steps = recommendation.steps.values[0]
    stappen = re.sub('\'', '', steps)
    step2 = stappen.lstrip('[')
    step3 = step2.rstrip(']')
    print(step3)
    
    dic_rated['user_id'] = user_id
    dic_rated['recipe_id'] = recommendation.recipe_id
    
    return dic_rated

# start for new user 
step = 1
while step == 1:
    name = input('Welcome to Cookly! \nPlease type your username in the field below. \nIf you are new, please type "new".\n')
    if name in user_df.name.values:
        user_id = user_df[user_df.name == name]['user_id'].values[0]
        step += 2
    else:
        step += 1
while step == 2:
    if name.lower() == 'new':
        name_new = input('Please choose a user name:\n')
        if name_new not in user_df.name.values:
            user_dict = {}
            user_dict[name_new] = len(user_df.name)
            user_id = len(user_df.name)
            print('Your new username is: ', name_new)
            print('To be able to give you the best possible recipe reccomendations, rate the following 15 recipes from 0 to 5.')
            print('\nFirst you will rate 5 breakfast recipes, then 5 lunch and dinner recipes and finally 5 desserts.\n')
            
            # user_id and name to user_id_df for later
            new_user_df = pd.DataFrame(list(user_dict.items()), columns=['name', 'user_id'])
            user_df = pd.concat([user_df, new_user_df])
            user_df.to_csv('user_df.csv', index=False)
            step += 1
        elif name_new in user_df.name.values:
            print('Sorry! That username already exists, please choose a new username\n')
    else:
        name = input('Oops! That is not a known username, if you want to make an account please type "new".\n')
        continue

# filenames for user interactions 
filename_breakfast = 'breakfast_input' + str(user_id) + '.csv'
filename_dinner = 'dinner_input' + str(user_id) + '.csv'
filename_dessert = 'dessert_input' + str(user_id) + '.csv'

try: 
    name_new
    # print recipes for input 
    base_rating_breakfast = base_rating(recipes_ids_breakfast, recipes)
    base_rating_dinner = base_rating(recipes_ids_dinner, recipes)
    base_rating_dessert = base_rating(recipes_ids_dessert, recipes)
    # make ratings to df
    breakfast_df_user = pd.DataFrame(base_rating_breakfast).T
    dinner_df_user = pd.DataFrame(base_rating_dinner).T
    dessert_df_user = pd.DataFrame(base_rating_dessert).T
    print('Thank you for rating these recipes, now you can start getting your own personilized recipes\n')
    # save ratings as csv
    breakfast_df_user.to_csv(filename_breakfast, index = False)
    dinner_df_user.to_csv(filename_dinner, index = False)
    dessert_df_user.to_csv(filename_dessert, index = False)
except:
    print('Welcome back!')
    breakfast_df_user = pd.read_csv(filename_breakfast)
    dinner_df_user = pd.read_csv(filename_dinner)
    dessert_df_user = pd.read_csv(filename_dessert)
    
    # vraag om input van het vorige gerecht!!!!\

# ask what they want breakfast dinner dessert
step = 1 
while step == 1:
    requested = input('Would you like a breakfast, dinner or a dessert recommendation?\n').lower()
    if requested == 'breakfast' or requested == 'dinner' or requested == 'dessert':
        step += 1
    else:
        print('Oops that is not a valid input! Please choose breakfast, dinner or dessert.\n')

# ask exclusions 
exclusion_list = ['']
exclusion_step = 1
exclusion_yn = input('Are there any food items you want to exclude from your recommendations?\n').lower()
while exclusion_step == 1:
    if exclusion_yn == 'yes':
        exclusion = input('What food item do you want to exclude?\n').lower()
        exclusion_list.append(exclusion)
        more = input('Do you want to exclude more ingredients?\n').lower()
        if more == 'yes':
            exclusion = input('What food item do you want to exclude?\n').lower()
            exclusion_list.append(exclusion)
            more = input('Do you want to exclude more ingredients?\n').lower()
        elif more == 'no':
            exclusion_yn = 'no'
        
    else:
        exclusion_step += 1

# ask time 
time_question = 1
while time_question == 1:
    time_yn = input('Are you crunched for time?\n').lower()
    if time_yn == 'yes':
        max_time = int(input('How much time do you want to spend on cooking today?\nPlease give your anwser in minutes.\n'))
        time_question += 1
    elif time_yn == 'no':
        max_time = 864050
        print('Please wait while your personal recipe is being fetched.')
        time_question += 1
    else:
        print('Oops that is not a valid input. Please try again.')

# make predictions 
if requested == 'breakfast':
    breakfast_ratings = pd.concat([breakfast_df_user, recipes_ids_breakfast], sort = True).sort_values(by='user_id')
    unique_recipe_breakfast = breakfast_ratings['recipe_id'].unique()
    unique_users_breakfast = breakfast_ratings['user_id'].unique()
    # get dict to get indreasing numbers 
    recipe_dict, Rrecipe_dict = change_number(unique_recipe_breakfast)
    user_dict, Ruser_dict = change_number(unique_users_breakfast)
    # map dict 
    breakfast_ratings['recipe_id'] = breakfast_ratings['recipe_id'].replace(recipe_dict)
    breakfast_ratings['user_id'] = breakfast_ratings['user_id'].replace(user_dict)
    # get recommendations 
    breakfast_recommendation = recommendation(breakfast_ratings, breakfast_model, 0)
    breakfast_df = pd.DataFrame(breakfast_recommendation, columns=['recipe_id', 'rating'])
    # normal recipe ids 
    breakfast_df['recipe_id'] = breakfast_df['recipe_id'].replace(Rrecipe_dict)
    # merge recommendations
    merged_breakfast = pd.merge(breakfast_df, recipes, on = 'recipe_id', how = 'inner').sort_values(by = 'rating', ascending=False)

    # filter time constraint
    df_timeselect2 = merged_breakfast[merged_breakfast.minutes < max_time]
    df_timeselect = df_timeselect2.reset_index()
    # filter ingredients
    index_list = [0]
    for i in range(len(df_timeselect['ingredients'])):
        for item in exclusion_list:
            if item not in df_timeselect['ingredients'][i]:
                index_list.append(i)
    del df_timeselect['index']
    number = 1
    while number == 1:
        i = 0
        index = index_list[i]
        df_timeselect = df_timeselect.reset_index()
        recommendation_breakfast = df_timeselect[df_timeselect.index == index]
        done_user = done_recc[done_recc.user_id == user_id]
        if len(done_user) == 0:
            breakfast_dict = recommendation_recipe(recommendation_breakfast)
            number += 1
        elif len(done_user) != 0:
            if recommendation_breakfast.recipe_id.values[0] == done_user.recipe_id.values[0]:
                i += 1
            else:
                breakfast_dict = recommendation_recipe(recommendation_breakfast)
                number += 1

        breakfast_done_df = pd.DataFrame(list(breakfast_dict.items()), columns = ['user_id', 'recipe_id'])
        done = pd.concat([breakfast_done_df, done_recc])
        done2 = done[done.user_id != 'user_id']
        done3 = done2[done2.recipe_id != 'recipe_id']
        done3['user_id'] = done3['user_id'].astype('int')
        done3['recipe_id'] = done3['recipe_id'].astype('int')
        done3.to_csv('done_recommendations.csv', index = False)
 

elif requested == 'dinner':
    dinner_ratings = pd.concat([dinner_df_user, recipes_ids_dinner], sort = True).sort_values(by='user_id')
    unique_recipe_dinner = dinner_ratings['recipe_id'].unique()
    unique_users_dinner = dinner_ratings['user_id'].unique()
    # get dict to get increasing numbers 
    recipe_dict, Rrecipe_dict = change_number(unique_recipe_dinner)
    user_dict, Ruser_dict = change_number(unique_users_dinner)
    # map dict 
    dinner_ratings['recipe_id'] = dinner_ratings['recipe_id'].replace(recipe_dict)
    dinner_ratings['user_id'] = dinner_ratings['user_id'].replace(user_dict)
    # get recommendations 
    dinner_recommendation = recommendation(dinner_ratings, dinner_model, 0)
    dinner_df = pd.DataFrame(dinner_recommendation, columns=['recipe_id', 'rating'])
    # normal recipe ids 
    dinner_df['recipe_id'] = dinner_df['recipe_id'].replace(Rrecipe_dict)
    # merge recommendations
    merged_dinner = pd.merge(dinner_df, recipes, on = 'recipe_id', how = 'inner').sort_values(by = 'rating', ascending=False)
    # filter time constraint
    df_timeselect = merged_dinner[merged_dinner.minutes < max_time].reset_index()
    # filter ingredients 
    index_list = [0]
    for i in range(len(df_timeselect['ingredients'])):
        for item in exclusion_list:
            if item not in df_timeselect['ingredients'][i]:
                index_list.append(i)
    del df_timeselect['index']
    number = 1
    while number == 1:
        i = 0
        index = index_list[i]
        df_timeselect = df_timeselect.reset_index()
        recommendation_dinner = df_timeselect[df_timeselect.index == index]
        done_user = done_recc[done_recc.user_id == user_id]
        if len(done_user) == 0:
            dinner_dict = recommendation_recipe(recommendation_dinner)
            number += 1
        elif len(done_user) != 0:
            if recommendation_dinner.recipe_id.values[0] == done_user.recipe_id.values[0]:
                i += 1
            else:
                dinner_dict = recommendation_recipe(recommendation_dinner)
                number += 1

        dinner_done_df = pd.DataFrame(list(dinner_dict.items()), columns = ['user_id', 'recipe_id'])
        done = pd.concat([dinner_done_df, done_recc])
        done2 = done[done.user_id != 'user_id']
        done3 = done2[done2.recipe_id != 'recipe_id']
        done3['user_id'] = done3['user_id'].astype('int')
        done3['recipe_id'] = done3['recipe_id'].astype('int')
        done3.to_csv('done_recommendations.csv', index = False)

elif requested == 'dessert':
    dessert_ratings = pd.concat([dessert_df_user, recipes_ids_dessert], sort = True).sort_values(by='user_id') 
    unique_recipe_dessert = dessert_ratings['recipe_id'].unique()
    unique_users_dessert = dessert_ratings['user_id'].unique()
    # get dict to get indreasing numbers 
    recipe_dict, Rrecipe_dict = change_number(unique_recipe_dessert)
    user_dict, Ruser_dict = change_number(unique_users_dessert)
    # map dict 
    dessert_ratings['recipe_id'] = dessert_ratings['recipe_id'].replace(recipe_dict)
    dessert_ratings['user_id'] = dessert_ratings['user_id'].replace(user_dict)
    # get recommendations 
    dessert_recommendation = recommendation(dessert_ratings, dessert_model, 0)
    dessert_df = pd.DataFrame(dessert_recommendation, columns=['recipe_id', 'rating'])
    # normal recipe ids 
    dessert_df['recipe_id'] = dessert_df['recipe_id'].replace(Rrecipe_dict)
    # merge recommendations
    merged_dessert = pd.merge(dessert_df, recipes, on = 'recipe_id', how = 'inner').sort_values(by = 'rating', ascending=False)
    # filter time constraint
    df_timeselect = merged_dessert[merged_dessert.minutes < max_time].reset_index()
    # filter ingredients
    index_list = [0]
    for i in range(len(df_timeselect['ingredients'])):
        for item in exclusion_list:
            if item not in df_timeselect['ingredients'][i]:
                index_list.append(i)
    del df_timeselect['index']
    number = 1
    while number == 1:
        i = 0
        index = index_list[i]
        df_timeselect = df_timeselect.reset_index()
        recommendation_dessert = df_timeselect[df_timeselect.index == index]
        done_user = done_recc[done_recc.user_id == user_id]
        if len(done_user) == 0:
            dessert_dict = recommendation_recipe(recommendation_dessert)
            number += 1
        elif len(done_user) != 0:
            if recommendation_dessert.recipe_id.values[0] == done_user.recipe_id.values[0]:
                i += 1
            else:
                dessert_dict = recommendation_recipe(recommendation_dessert)
                number += 1

        dessert_done_df = pd.DataFrame(list(dessert_dict.items()), columns = ['user_id', 'recipe_id'])
        done = pd.concat([dessert_done_df, done_recc])
        done2 = done[done.user_id != 'user_id']
        done3 = done2[done2.recipe_id != 'recipe_id']
        done3['user_id'] = done3['user_id'].astype('int')
        done3['recipe_id'] = done3['recipe_id'].astype('int')
        done3.to_csv('done_recommendations.csv', index = False)




