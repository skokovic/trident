from flask import render_template, flash, redirect, url_for, request, jsonify
from __init__ import app, lm, baza
from flask_login import current_user, login_user, logout_user, login_required
from models import User
from oauth import OAuthSignIn
import requests
import lastfm
import movie_statistic
import tmdbsimple as tmdb
import movie_reccommendation
import urllib.request
import json
SECRET_KEY = '123'
DEBUG = True
dbName = '\0'
app.debug = DEBUG
app.secret_key = SECRET_KEY
tmdbKey: str = "b2dd64617f8c64de2a3c3c0ada9f73ec"
tmdb.API_KEY = tmdbKey



@app.route('/')
@app.route('/home')
def home():

    if not current_user.is_anonymous:
        print(current_user.get_id())
    upcoming = movie_statistic.get_most_popular_movies_today(10)
    print(upcoming)
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


@app.route('/my_profile')
def profile():

    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=271d1234d3f497eed5b1d80a07b3fcd1'

    #social_id = current_user.get_id()
    social_id = "facebook$10215343795441714"

    #user = baza.db.Users.find_one({"social_id": current_user.get_id()})
    user = baza.db.Users.find_one({"social_id": social_id})
    email = user['email']
    name = user['first_name']
    lastname = " " + user['last_name']
    gender = user['gender']
    age = user['age_range']['min']
    location = user['location']['name']
    if 'picture' in user:
        my_picture = user['picture']['data']['url']
    else:
        my_picture = "https://fignow.com/public_html/fignow.com/wp-content/uploads/2016/12/Unknown.jpg"

    recommendation = movie_reccommendation.get_recommended_movies(1)

    list_of_movie_info = []
    for movie_id in recommendation:
        id_new = urllib.request.urlopen("https://api.themoviedb.org/3/movie/"+ str(movie_id)+"?api_key=b2dd64617f8c64de2a3c3c0ada9f73ec").read()
        id_new = id_new.decode("utf-8")
        json_data = json.loads(id_new)
        list_of_movie_info.append(movie_data(json_data['imdb_id']))

    recommendation = list_of_movie_info
    city = baza.db.Users.find_one({"social_id": social_id})['location']['name']
    response = requests.get(url.format(city)).json()

    temperature = round((response['main']['temp'] - 32) * 5 / 9, 2)

    weather_info = {
        'city': city,
        'temperature': str(temperature)+ " " + u'\N{DEGREE SIGN}'+"C" ,
        'description': response['weather'][0]['description'] + " at " + (city.split(","))[0],
        'icon': response['weather'][0]['icon'],
    }

    print(recommendation)

    return render_template('my_profile.html', reccomendation = recommendation, my_picture = my_picture, weather_info= weather_info, email = email, name = name, lastname = lastname, gender = gender, age = age, location = location)


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


def movie_data(imdbid):
    url = "http://www.omdbapi.com/?i={}&apikey=4909d34"
    movie_info_var = baza.db.MoviesOMDB.find_one({'imdbID': imdbid})


    if not movie_info_var:
        response = requests.get(url.format(imdbid)).json()
        last_request = lastfm.LastFM()
        print(imdbid)
        trailer = "www.youtube.com/watch?v=" + tmdb.Movies(id=imdbid).videos()['results'][0]['key']
        print(trailer)
        soundtrack_title = response['Title'] + " soundtrack"
        soundtrack = last_request.get_movie_album("album.search", {"album": soundtrack_title})
        soundtrack = soundtrack[:-1]

        movie_info_var = {
            'imdbID': response['imdbID'],
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
            'soundtrack': soundtrack,
            'trailer' : trailer
        }

        baza.db.MoviesOMDB.insert_one(
            {'imdbID': movie_info_var['imdbID'], 'title': movie_info_var['title'], 'rated': movie_info_var["rated"],
             'released': movie_info_var['released'], 'runtime': movie_info_var['runtime'],
             'genre': movie_info_var['genre'], 'director': movie_info_var['director'],
             'actors': movie_info_var['actors'], 'plot': movie_info_var['plot'],
             'awards': movie_info_var['awards'], 'rating_source': movie_info_var['rating_source'],
             'rating_value': movie_info_var['rating_value'], 'image': movie_info_var['image'],
             'soundtrack': movie_info_var['soundtrack'], 'trailer': trailer})

    return movie_info_var


@app.route('/movie_info<imdbID>')
def movie_info(imdbID):

    imdbID = imdbID[1:-1]
    if "tt" not in imdbID:
        id_new = urllib.request.urlopen(
            "https://api.themoviedb.org/3/movie/" + str(imdbID) + "?api_key=b2dd64617f8c64de2a3c3c0ada9f73ec").read()
        id_new = id_new.decode("utf-8")
        json_data = json.loads(id_new)

        imdbID = json_data['imdb_id']

    print(imdbID)
    movie_info_var = movie_data(imdbID)

    return render_template('movie_info.html', movie_info=movie_info_var)


def main():
    app.run(host='0.0.0.0')


if __name__ == '__main__':
    main()


#    is_authenticated:  a property that is True if the user has valid credentials or False otherwise. User is logged in or not.
#    is_active:         a property that is True if the user's account is active or False otherwise.
#    is_anonymous:      a property that is False for regular users, and True for a special, anonymous user. True only when the user is not logged in.
#    get_id():          a method that returns a unique identifier for the user as a string (unicode, if using Python 2).