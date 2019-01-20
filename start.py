from flask import render_template, flash, redirect, url_for, request, jsonify, session
from __init__ import app, lm, baza
from flask_login import current_user, login_user, logout_user, login_required
from models import User
from oauth import OAuthSignIn
from flask_oauth import OAuth
import requests
import lastfm
import movie_statistic
import tmdbsimple as tmdb
import movie_recommendation
import urllib.request
import json
import statistic_routes
import pyowm
import random
import omdb

owm = pyowm.OWM('571ac439b33fee0ac1d7f927bd25546b')
omdbc = omdb.OMDBClient(apikey='4909d34')
lastfmc = lastfm.LastFM()

SECRET_KEY = '123'
DEBUG = True
dbName = '\0'
app.debug = DEBUG
SECRET_KEY = "123"
app.secret_key = SECRET_KEY
tmdbKey: str = "b2dd64617f8c64de2a3c3c0ada9f73ec"
tmdb.API_KEY = tmdbKey

GOOGLE_CLIENT_ID = '921408924262-0vsai1m9gru3c3k6qoepn25pe2bepppu.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = 'efb1gFkW041gQD6EtgBa9T9x'

oauth = OAuth()

google = oauth.remote_app('google',
                          base_url='https://www.google.com/accounts/',
                          authorize_url='https://accounts.google.com/o/oauth2/auth',
                          request_token_url=None,
                          request_token_params={'scope': 'https://www.googleapis.com/auth/userinfo.email',
                                                'response_type': 'code'},
                          access_token_url='https://accounts.google.com/o/oauth2/token',
                          access_token_method='POST',
                          access_token_params={'grant_type': 'authorization_code'},
                          consumer_key=GOOGLE_CLIENT_ID,
                          consumer_secret=GOOGLE_CLIENT_SECRET)

REDIRECT_URI = "/google_page"


@app.route('/google')
def log():
    callback = url_for('authorized', _external=True)
    return google.authorize(callback=callback)


@app.route(REDIRECT_URI)
@google.authorized_handler
def authorized(resp):
    access_token = resp['access_token']
    session['access_token'] = access_token, ''
    google_page()
    return redirect(url_for("home"))


@google.tokengetter
def get_access_token():
    return session.get('access_token')


@app.route('/google_page')
def google_page():
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('login'))

    access_token = access_token[0]
    from urllib import request
    from urllib.request import urlopen
    from urllib.error import URLError

    headers = {'Authorization': 'OAuth ' + access_token}
    req = request.Request('https://www.googleapis.com/oauth2/v1/userinfo',
                          None, headers)
    try:
        res = urlopen(req)
    except URLError as e:
        if e.code == 401:
            # Unauthorized - bad token
            session.pop('access_token', None)
            return redirect(url_for('login'))
        return res.read()
    session['logged_in'] = True
    user = res.read()
    jsonuser = json.loads(user)
    id_user = int(jsonuser['id']) % 1000000
    user_id = id_user
    social_id = str(id_user)
    email = jsonuser['email']
    if 'given_name' in jsonuser:
        first_name = jsonuser['given_name']
    else:
        first_name = ""

    if 'family_name' in jsonuser:
        last_name = jsonuser['family_name']
    else:
        last_name = ""

    if 'picture' in jsonuser:
        picture = {"data" : {"url" : jsonuser['picture']}}
    else:
        picture = {"data": {"url": ""}}

    gender = ""
    location = {"name" : ""}
    age_range = {"min" : 0}
    likes = ""

    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('home'))

    user = baza.db.Users.find_one({"social_id": social_id})

    if not user:
        baza.db.Users.insert_one({ "user_id": user_id, "email": email, "social_id": social_id, "first_name": first_name, "last_name": last_name,
                                    "gender": gender, "location": location, "age_range": age_range, "likes": likes, "picture": picture, "movie_likes": [] })
        user = baza.db.Users.find_one({"social_id": social_id})
    login_user(User(user['user_id'], user['email'], user['social_id'], user['first_name'], user['last_name'], user['gender'], user['location'], user['age_range'], user['likes'], user['picture']), remember= True, force= True)

    return jsonuser


@app.route('/')
@app.route('/home')
def home():
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
                                    "gender": gender, "location": location, "age_range": age_range, "likes": likes, "picture": picture, "movie_likes": [] })
        user = baza.db.Users.find_one({"social_id": social_id})

    login_user(User(user['user_id'], user['email'], user['social_id'], user['first_name'], user['last_name'], user['gender'], user['location'], user['age_range'], user['likes'], user['picture']), remember= True, force= True)
    return redirect(url_for('home'))

def fetch_right_user(id):
    if "facebook$" in id:
        user = baza.db.Users.find_one({"social_id": id})
    else:
        user = baza.db.Users.find_one({"user_id": int(id)})
    return user


@app.route('/my_profile')
def profile():
    user_id = current_user.get_id()
    #social_id = "facebook$10215343795441714"
    user = fetch_right_user(user_id)

    # TODO add checks for these fields if they are null or not!
    email = user['email']
    name = user['first_name']
    lastname = " " + user['last_name']
    gender = user['gender']

    age_range = user['age_range']
    if age_range is not None:
        age = age_range['min']
    else:
        age = 'Not defined'

    location_out = user['location']
    if location_out is not None:
        location = location_out['name']
    else:
        location = None

    if 'picture' in user:
        my_picture = user['picture']['data']['url']
    else:
        my_picture = "https://fignow.com/public_html/fignow.com/wp-content/uploads/2016/12/Unknown.jpg"

    recommendation = user['movie_likes']

    list_of_movie_info = []
    for movie_id in recommendation:
        json_data = tmdb_movie_data(movie_id['movie'])
        # TODO append if db.user.movie_likes.search(json_data['id']) is not None
        list_of_movie_info.append(movie_data(json_data['imdb_id']))

    # quick fix for duplicate movies in 
    list_of_movie_info = list(set(list_of_movie_info))

    random_cities = ['London', 'Rio de Janeiro', 'Los Angeles', 'Tokyo', 'Sidney']
    recommendation = list_of_movie_info
    if location is not None:
        city = location
        try:
            observation = owm.weather_at_place(city)
        except:
            try:
                observation = owm.weather_at_place(city.split(',')[0])
            except:
                observation = owm.weather_at_place(random.choice(random_cities))

        w = observation.get_weather()
        temperature = w.get_temperature('celsius')['temp']

        weather_info = {
            'city': city,
            'temperature': str(temperature)+ " " + u'\N{DEGREE SIGN}'+"C" ,
            'description': w.get_detailed_status() + " at " + (city.split(","))[0],
            'icon': w.get_weather_icon_url(),
        }
    else:
        city = random.choice(random_cities)
        observation = owm.weather_at_place(city)
        w = observation.get_weather()
        temperature = w.get_temperature('celsius')['temp']

        weather_info = {
            'city': city,
            'temperature': str(temperature)+ " " + u'\N{DEGREE SIGN}'+"C" ,
            'description': w.get_detailed_status() + " at " + (city.split(","))[0],
            'icon': w.get_weather_icon_url(),
        }

    return render_template('my_profile.html', reccomendation = recommendation, my_picture = my_picture, weather_info= weather_info, email = email, name = name, lastname = lastname, gender = gender, age = age, location = location)


@app.route('/trending.html')
def trending():
    trending_movies = movie_statistic.get_trending()
    return render_template('trending.html', trending_movies = trending_movies)

@app.route('/recommendations.html')
def recommendations():
    user_id = current_user.get_id()
    user_id = ''.join(filter(str.isdigit, str(user_id)))
    recommended_movies = movie_recommendation.get_recommended_movies(user_id)
    #recommended_movies = movie_recommendation.get_recommended_movies(10218039196831139)
    movies = []
    for movie_id in recommended_movies:
        movie = tmdb_movie_data(movie_id)
        movies.append(movie)

    return render_template('recommendations.html', movies = movies)


@app.route('/search_movies', methods=['POST'])
def search_movies():
    keyword = request.form['movie_keyword']
    search = tmdb.Search()
    response = search.movie(query=keyword)
    movies = search.results
    for movie in movies:
        tmdb_movie_data(movie['id'])


    return render_template('search.html', movies = movies)


@app.route('/movie', methods=['POST'])
def movie():
    user_id = current_user.get_id()
    data = request.get_json()
    data['social_id'] = user_id
    if "facebook$" in user_id:
        baza.db.Users.update({'social_id' : user_id}, {'$set' :  {'movie_likes' : {'movie': int(data['movie']), 'like': data['like']}}}, upsert = True)
    else:
        baza.db.Users.update({'user_id' : int(user_id)}, {'$set' :  {'movie_likes' : {'movie': int(data['movie']), 'like': data['like']}}}, upsert = True)
    return jsonify(status="success", data=data)


def tmdb_movie_data(tmdb_id):
    movie = baza.db.MoviesTMDB.find_one({'id': tmdb_id})
    if movie is None:
        movie = tmdb.Movies(id=tmdb_id)
        info = movie.info()
        #omdb = omdb_movie_data(info['imdb_id'])
        baza.db.MoviesTMDB.insert_one(info)
    return movie

def omdb_movie_data(omdb_id):
    movie = baza.db.MoviesOMDB.find_one({'imdbID': id})
    if movie is None:
        movie = omdbc.imdbid(omdb_id)
        baza.db.MoviesOMDB.insert_one(movie)
    return movie

def movie_data(imdbid):
    url = "http://www.omdbapi.com/?i={}&apikey=4909d34"
    movie_info_var = baza.db.MoviesOMDB.find_one({'imdbID': imdbid})


    if not movie_info_var:
        response = requests.get(url.format(imdbid)).json()
        #last_request = lastfm.LastFM()
        print(imdbid)
        trailer = "www.youtube.com/watch?v=" + tmdb.Movies(id=imdbid).videos()['results'][0]['key']
        print(trailer)
        soundtrack_title = response['Title'] + " soundtrack"
        soundtrack = lastfmc.get_movie_album("album.search", {"album": soundtrack_title})
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
