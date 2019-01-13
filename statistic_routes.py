from flask import request
import movie_statistic as stats


@app.route('/movies_in_theatre', methods=['POST'])
def movies_in_theatre():
    return stats.get_movies_in_theatre()

@app.route('/upcoming_movies', methods=['POST'])
def upcoming_movies():
    return stats.get_upcoming_movies()

@app.route('/most_popular_movies_today', methods=['POST'])
def most_popular_movies_today():
    return stats.get_most_popular_movies_today(11)

@app.route('/top_rated_movies_ever', methods=['POST'])
def top_rate_movies_ever():
    return stats.get_top_rated_movies_ever(11)

@app.route('/most_highest_grossing_movies', methods=['POST'])
def most_highest_grossing_movies():
    data = request.get_json()
    return stats.get_highest_grossing_movies(data['year'])


@app.route('/movies_with_most_vote_count', methods=['POST'])
def get_movies_with_most_vote_count():
    return stats.get_movies_with_most_vote_count(11)

@app.route('/trending', methods=['POST'])
def get_trending():
    data = request.get_json()
    return stats.get_trending(11, data['daily'], data['media_type'])

@app.route('/most_popular_movies_by_genre', methods=['POST'])
def get_most_popular_movies_by_genre():
    data = request.get_json()
    return stats.get_most_popular_movies_by_genre(11, data['genre_id'])

@app.route('/movies_with_highest_revenue_by_genre', methods=['POST'])
def get_movies_with_highest_revenue_by_genre():
    data = request.get_json()
    return stats.get_movies_with_highest_revenue_by_genre(11, data['genre_id'])

@app.route('/most_successful_companies', methods=['POST'])
def get_the_most_successful_companies():
    return stats.get_the_most_successful_companies()

@app.route('/most_successful_actors', methods=['POST'])
def get_the_most_successful_actors():
    return stats.get_the_most_successful_actors()


