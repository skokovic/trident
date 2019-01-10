from flask import Flask, render_template
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

def main():
    app.run(host='0.0.0.0')

if __name__ == '__main__':
    main()