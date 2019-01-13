from flask import render_template, flash, redirect, url_for, request, jsonify
from __init__ import app, lm, baza
from flask_login import current_user, login_user, logout_user, login_required
from models import User
from oauth import OAuthSignIn
import requests
import lastfm
import movie_statistic
SECRET_KEY = '123'
DEBUG = True
dbName = '\0'
app.debug = DEBUG
app.secret_key = SECRET_KEY



@app.route('/')
@app.route('/home')
def home():

    if not current_user.is_anonymous:
        print(current_user.get_id())
    upcoming = movie_statistic.get_most_popular_movies_today(10)

    return render_template('home.html', upcoming=upcoming)


@app.route('/login_page')
def login():
    return render_template('login_page.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@lm.user_loader   #User Loader Function - Flask needs the application's help in loading a user
def load_user(id):
    user = baza.db.Users.find_one({'user_id': int(id)})
    return User(user['user_id'], user['email'], user['social_id'], user['first_name'], user['last_name'], user['gender'], user['location'], user['age_range'], user['likes'], user['picture'])


@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('home'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('home'))

    oauth = OAuthSignIn.get_provider(provider)
    user_id, social_id, first_name, last_name, email, gender, location, age_range, likes, picture = oauth.callback()

    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('home'))

    user = baza.db.Users.find_one({"social_id": social_id})

    if not user:
        baza.db.Users.insert_one({  "user_id": int(user_id), "email": email, "social_id": social_id, "first_name": first_name, "last_name": last_name, 
                                    "gender": gender, "location": location, "age_range": age_range, "likes": likes, "picture": picture })
        user = baza.db.Users.find_one({"social_id": social_id})

    login_user(User(user['user_id'], user['email'], user['social_id'], user['first_name'], user['last_name'], user['gender'], user['location'], user['age_range'], user['likes'], user['picture']), remember= True, force= True)
    return redirect(url_for('home'))


@app.route('/my_profile.html')
def profile():
    #user = baza.db.Users.find_one({"social_id": current_user.get_id()})
    #my_picture = user['picture']['data']['url']
    my_picture = ""

    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=271d1234d3f497eed5b1d80a07b3fcd1'

    social_id = current_user.get_id()

    #city = baza.db.Users.find_one({"social_id": social_id})['location']['name']
    city = "Zagreb"
    response = requests.get(url.format(city)).json()

    temperature = round((response['main']['temp'] - 32) * 5 / 9, 2)

    weather_info = {
        'city': city,
        'temperature': temperature,
        'description': response['weather'][0]['description'],
        'icon': response['weather'][0]['icon'],
    }


    #print(weather_info['city'], weather_info['temperature'], weather_info['description'], weather_info['icon'])

    return render_template('my_profile.html', my_picture = my_picture, weather_info=weather_info)


@app.route('/trending.html')
def trending():
    trending_movies = movie_statistic.get_trending()
    return render_template('trending.html', trending_movies = trending_movies)

@app.route('/movie', methods=['POST'])
def movie():
    social_id = current_user.get_id()
    data = request.get_json()
    data['social_id'] = social_id
    baza.db.Users.update({'social_id' : social_id}, {'$push' :  {'movie_likes' : {'movie': data['movie'], 'like': data['like']}}}, upsert = True)
    return jsonify(status="success", data=data)


@app.route('/movie_info')
def movie_info():

    url = "http://www.omdbapi.com/?t={}&apikey=4909d34"

    movie_name = "Interstellar"
    movie_info_var = ""
    #movie_info_var = baza.db.MoviesOMDB.find_one({'title': movie_name})
    if not movie_info_var:
        response = requests.get(url.format(movie_name)).json()
        last_request = lastfm.LastFM()
        soundtrack_title = response['Title'] + " soundtrack"
        soundtrack = last_request.get_movie_album("album.search", {"album": soundtrack_title})
        movie_info_var = {
            'title': response["Title"],
            'rated': response["Rated"],
            'released': response["Released"],
            'runtime': response["Runtime"],
            'genre': response["Genre"],
            'director': response["Director"],
            'actors': response["Actors"],
            'plot': response["Plot"],
            'awards': response["Awards"],
            'rating_source': response["Ratings"][0]["Source"],
            'rating_value': response["Ratings"][0]["Value"],
            'image': response['Poster'],
            'soundtrack': soundtrack
        }



     #   baza.db.MoviesOMDB.insert_one({'title': movie_info['title'], 'rated': movie_info["rated"],'released': movie_info['released'],'runtime': movie_info['runtime'],
     #  'genre': movie_info['genre'],'director': movie_info['director'],
     #  'actors': movie_info['actors'],'plot': movie_info['plot'],
     #  'awards': movie_info['awards'],'rating_source': movie_info['rating_source'],
     #  'rating_value': movie_info['rating_value'],'image': movie_info['image'],
     # 'soundtrack': movie_info['soundtrack']})


    return render_template('movie_info.html',  movie_info=movie_info_var)


def main():
    app.run(host='0.0.0.0')


if __name__ == '__main__':
    main()


#    is_authenticated:  a property that is True if the user has valid credentials or False otherwise. User is logged in or not.
#    is_active:         a property that is True if the user's account is active or False otherwise.
#    is_anonymous:      a property that is False for regular users, and True for a special, anonymous user. True only when the user is not logged in.
#    get_id():          a method that returns a unique identifier for the user as a string (unicode, if using Python 2).