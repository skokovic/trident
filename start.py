from flask import Flask, render_template
from app import app, lm, baza
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from app.oauth import OAuthSignIn
import requests

import movie_statistic
SECRET_KEY = '123'
DEBUG = True
dbName = '\0'
app = Flask(__name__)
app.debug = DEBUG
app.secret_key = SECRET_KEY

@app.route('/')
def home():
    upcoming = movie_statistic.get_upcoming_movies()
    return render_template('home.html', upcoming = upcoming )

@app.route('/my_profile.html')
def profile():
    return render_template('my_profile.html')

@app.route('/trending.html')
def trending():
    trending_movies = movie_statistic.get_trending()
    return render_template('trending.html', trending_movies = trending_movies)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

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





def main():
    app.run(host='0.0.0.0')

if __name__ == '__main__':
    main()