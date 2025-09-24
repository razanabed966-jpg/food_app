import flask
import secrets

import tensorflow as tf
from tensorflow import keras
import numpy as np
from PIL import Image, ImageOps
import io
import linecache
import base64

import matplotlib.pyplot as plt
import matplotlib
import seaborn as sn
matplotlib.use('Agg')


print("Starting flask server")

app = flask.Flask(__name__)

app.config["SECRET_KEY"] = secrets.token_bytes()

INGREDIENTS = sorted([
    'egg', 'chicken', 'rice', 'tomato', 'cheese', 'potato', 'onion', 'garlic', 'butter', 'corn',
    'lemon', 'cucumber', 'fish', 'pasta', 'spinach', 'ginger', 'parsley', 'carrot', 'cinnamon', 'olives',
    'eggplant', 'mushroom', 'bread', 'beef', 'chocolate', 'apple', 'banana', 'orange', 'broccoli', 'peas'
])

# AI models
ingredients_classifier_path = 'saved_models/ingredients_classifier.keras'
ingredients_classifier = tf.keras.models.load_model(ingredients_classifier_path)

meals_classifier_path = 'saved_models/meals_classifier.keras'
meals_classifier = tf.keras.models.load_model(meals_classifier_path)

personal_recommender_path = 'saved_models/personal_recommender.keras'
personal_recommender = tf.keras.models.load_model(personal_recommender_path)


@app.route('/ingredients-classifier', methods=['POST'])
def classify_ingredients():
    images = flask.request.files.getlist('images')
    print(images)

    ingredients = []
    for img_data in images:
        print(img_data)

        img = Image.open(io.BytesIO(img_data.read()))

        img = ImageOps.fit(img, (224, 224))

        img_array = keras.utils.img_to_array(img)

        img_array = tf.expand_dims(img_array, 0)
        predictions = ingredients_classifier.predict(img_array)

        ingredients.append(INGREDIENTS[np.argmax(predictions[0])])

    return flask.make_response(flask.jsonify({'ingredients': ingredients}))




def __get_meal_ingredients(id: int):
    return linecache.getline("data/ingredients.txt", id).split(',')


def __get_meal_name(id: int):
    return linecache.getline("data/classes.txt", id).replace('_', ' ')


@app.route('/meal-classifier', methods=['POST'])
def classify_meal():
    img_data = flask.request.files['meal_image']

    img = Image.open(io.BytesIO(img_data.read()))
    img = ImageOps.fit(img, (256, 256))

    img_array = keras.utils.img_to_array(img)

    img_array = tf.expand_dims(img_array, 0)

    predictions = meals_classifier.predict(img_array)

    meal_id = np.argmax(predictions[0]) + 1

    print(f'recognized meal: {meal_id}')

    ingredients = __get_meal_ingredients(meal_id)
    meal_name = __get_meal_name(meal_id)

    return flask.make_response(flask.jsonify({'recognized_meal': meal_name, 'ingredients': ingredients}))


@app.route('/personal-recommender', methods=['POST'])
def personal_recommendation():
    features = flask.request.json.get('features')
    scores = personal_recommender.predict([features])[0].tolist()
    scores = zip(scores, range(len(scores)))

    top30 = [item[1] for item in sorted(scores, reverse=True)][:30]

    return flask.make_response(flask.jsonify({'top30': top30}))


def cleanup():
    sn.reset_orig()
    plt.clf()
    plt.close()


@app.route('/data-analysis', methods=['POST'])
def data_analysis():
    def encode_plot(plot):
        buf = io.BytesIO()
        fig = plot.get_figure()
        fig.tight_layout()

        fig.savefig(buf, format='png')
        data = base64.b64encode(buf.getvalue()).decode("utf-8")

        return data
    
    def get_hist_plot(data, x, label):
        plot = sn.histplot(data=data, x=x)

        for item in plot.get_xticklabels():
            item.set_rotation(70)
        
        plt.xlabel(label)

        return plot
    
    data = flask.request.json
    age_data = data['age']
    gender_data = data['gender']
    orders = sorted(data['orders'])

    orders_data = {
        "ingredients": [order[0] for order in orders],
        "age": [order[1] for order in orders],
        "gender": [order[2] for order in orders],
        "male-orders": [order[0] for order in orders if order[2] == 'male'],
        "female-orders": [order[0] for order in orders if order[2] == 'female'],
    }

    plots = dict()

    plot = sn.histplot(data=data, x='age', color="#ADD8E6")
    plots['age-hist'] = encode_plot(plot)
    cleanup()

    labels = 'young', 'adult', 'elder'
    sizes = [
        len([1 for age in age_data if age < 30]) / len(age_data),
        len([1 for age in age_data if 30 <= age < 50]) / len(age_data),
        len([1 for age in age_data if age >= 50]) / len(age_data)
    ]

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%')
    plots['age-pie'] = encode_plot(ax)
    cleanup()

    plot = sn.countplot(x='gender', data=data)
    plots['gender-bar'] = encode_plot(plot)
    cleanup()

    labels = 'male', 'female'
    sizes = [
        len([1 for gender in gender_data if gender=='male']) / len(gender_data),
        len([1 for gender in gender_data if gender=='female']) / len(gender_data)
    ]

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%')
    plots['gender-pie'] = encode_plot(ax)
    cleanup()

    fig, ax = plt.subplots()
    plt.scatter('gender', 'age', data=data)
    plt.xlabel('gender')
    plt.ylabel('age')

    plots['gender-age-scatter'] = encode_plot(ax)
    cleanup()

    plot = get_hist_plot(data, 'ingredients', 'ingredients')
    plots['ingredients-hist'] = encode_plot(plot)
    cleanup()

    plot = get_hist_plot(orders_data, 'ingredients', 'ingredients')
    plots['ingredients-orders-hist'] = encode_plot(plot)
    cleanup()

    fig, ax = plt.subplots()
    plt.scatter('ingredients', 'age', data=orders_data)
    plt.xlabel('ingredients')
    plt.ylabel('age')
    plt.xticks(rotation=75)
    plots['ingredients-age-scatter'] = encode_plot(ax)
    cleanup()

    fig, ax = plt.subplots()
    plt.scatter('ingredients', 'gender', data=orders_data)
    plt.xlabel('ingredients')
    plt.ylabel('gender')
    plt.xticks(rotation=75)
    plots['ingredients-gender-scatter'] = encode_plot(ax)
    cleanup()

    plot = get_hist_plot(orders_data, 'male-orders', 'ingredients')
    plots['ingredients-male-hist'] = encode_plot(plot)
    cleanup()

    plot = get_hist_plot(orders_data, 'female-orders', 'ingredients')
    plots['ingredients-female-hist'] = encode_plot(plot)
    cleanup()

    response = flask.make_response(flask.jsonify(plots))

    return response
