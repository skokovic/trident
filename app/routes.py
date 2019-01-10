from flask import render_template, flash, redirect, url_for, request
from app import app, lm, baza
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from app.oauth import OAuthSignIn
import requests

@app.route('/')
@app.route('/index')
def index():
    if not current_user.is_anonymous:
        print(current_user.get_id())
    return render_template('index.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/weather', methods=['GET', 'POST'])
def weather():

    social_id = current_user.get_id()
    social_id = "facebook$" + social_id

    not_found = 2

    if request.method == 'POST':
        new_city = request.form.get('city')
        delete_city = request.form.get('deleteCity')

        if new_city:
            grad = baza.db.Users.update({'social_id' : social_id}, {'$push' :  {'gradovi' : new_city}}, upsert = True)
            not_found = 0
        if delete_city:
            if delete_city in baza.db.Users.find_one({'social_id': social_id})['gradovi']:
                grad = baza.db.Users.update({'social_id': social_id}, {'$pull' : {'gradovi' : delete_city}}, upsert=True)
                not_found = 0
            else:
                not_found = 1

    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=271d1234d3f497eed5b1d80a07b3fcd1'

    cities = baza.db.Users.find_one({"social_id" : social_id})['gradovi']
    weather_data = []

    for city in cities:
        response = requests.get(url.format(city)).json()

        weather = {
            'city': city,
            'temperature': response['main']['temp'],
            'description': response['weather'][0]['description'],
            'icon': response['weather'][0]['icon'],
        }

        weather_data.append(weather)

    return render_template('weather.html', weather_data=weather_data, not_found = not_found)


@lm.user_loader   #User Loader Function - Flask needs the application's help in loading a user
def load_user(id):
    user = baza.db.Users.find_one({'user_id': int(id)})
    return User(user['user_id'], user['email'], user['social_id'], user['first_name'], user['last_name'])

@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()

@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))

    oauth = OAuthSignIn.get_provider(provider)
    user_id, social_id, first_name, last_name, email = oauth.callback()

    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))

    user = baza.db.Users.find_one({"social_id": social_id})

    if not user:
        baza.db.Users.insert_one({"user_id": int(user_id), "email": email, "social_id": social_id, "first_name": first_name, "last_name": last_name, "gradovi": ['Zagreb'], "filmovi" : [], 'favoriti': []})
        user = baza.db.Users.find_one({"social_id": social_id})

    login_user(User(user['user_id'], user['email'], user['social_id'], user['first_name'], user['last_name']), remember= True, force= True)
    return redirect(url_for('index'))



#    is_authenticated:  a property that is True if the user has valid credentials or False otherwise. User is logged in or not.
#    is_active:         a property that is True if the user's account is active or False otherwise.
#    is_anonymous:      a property that is False for regular users, and True for a special, anonymous user. True only when the user is not logged in.
#    get_id():          a method that returns a unique identifier for the user as a string (unicode, if using Python 2).