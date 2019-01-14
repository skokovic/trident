import datetime
import tmdbsimple as tmdb
import omdb
import math
import requests # to make TMDB API calls
import locale # to format currency as USD
locale.setlocale( locale.LC_ALL, '' )

tmdbKey: str = "b2dd64617f8c64de2a3c3c0ada9f73ec"
tmdb.API_KEY = tmdbKey
omdb.set_default('apikey', "4909d34")


def get_movies_in_theatre():
    now_playing = tmdb.Movies().now_playing()['results']
    return now_playing


def get_upcoming_movies():
    upcoming = []
    now = str(datetime.datetime.now())[:10]
    response = tmdb.Movies().upcoming()['results']
    for movie in response:
        if movie['release_date'] > now:
            upcoming.append(movie)
    return upcoming


def get_most_popular_movies_today(number_of_listed=10):
    n = math.ceil(number_of_listed/20)
    response = []
    j = 1
    for i in range(1, n+1):
        movies = tmdb.Movies().popular(page=i)['results']
        for movie in movies:
            response.append(movie)
            if j > number_of_listed:
                break
            j += 1
    return response


def get_top_rated_movies_ever(number_of_listed=10):
    n = math.ceil(number_of_listed/20)
    response = []
    j = 1
    for i in range(1, n+1):
        movies = tmdb.Movies().top_rated(page=i)['results']
        for movie in movies:
            response.append(movie)
            if j > number_of_listed:
                break
            j += 1
    return response


def get_most_popular_keywords(number_of_movies_taken=100):
    #SPEED IT UP!
    movie_ids = []
    keywords = {}
    for movie in get_most_popular_movies_today(number_of_listed=number_of_movies_taken):
        movie_ids.append(movie['id'])
    for movie_id in movie_ids:
        for keyword in tmdb.Movies(id=movie_id).keywords()['keywords']:
            if keyword['name'] in keywords:
                keywords[str(keyword['name'])] += 1
            else:
                keywords[keyword['name']] = 1
    keywords2 = {k: v for k, v in keywords.items() if v > 1}
    return sorted(keywords2.items(), key=lambda x: x[1], reverse=True)


def get_highest_grossing_movies(number_of_movies_taken=11, year=None):
    n = math.ceil(number_of_movies_taken / 20)
    response = []
    j = 1
    for i in range(1, n + 1):
        movies = requests.get(
            'https://api.themoviedb.org/3/discover/movie?api_key=' + tmdbKey + '&primary_release_year='
            + str(year) + '&sort_by=revenue.desc&page=' + str(i))
        highest_revenue = movies.json()
        highest_revenue_movies = highest_revenue['results']
        for movie in highest_revenue_movies:
            response.append(movie)
            if j >= number_of_movies_taken:
                break
            j += 1
    """for movie in response:
        lol = requests.get('https://api.themoviedb.org/3/movie/' + str(movie['id']) + 
        '?api_key=' + tmdbKey + '&language=en-US')
        movie_revenue = lol.json()
        print(movie['title'] + ", " + str(movie_revenue['revenue']))"""
    return response


def get_movies_with_most_vote_count(number_of_movies_taken=10):
    n = math.ceil(number_of_movies_taken / 20)
    response = []
    j = 1
    for i in range(1, n + 1):
        movies = requests.get(
            'https://api.themoviedb.org/3/discover/movie?api_key=' + tmdbKey + '&sort_by=vote_count.desc&page='
            + str(i))
        highest_revenue = movies.json()
        highest_revenue_movies = highest_revenue['results']
        for movie in highest_revenue_movies:
            response.append(movie)
            if j > number_of_movies_taken:
                break
            j += 1
    return response


def get_trending(number_of_listed=10, daily=False, media_type="all"):
    #media_type = all, movie, tv, person
    if daily:
        time_window = "day"
    else:
        time_window = "week"
    n = math.ceil(number_of_listed / 20)
    response = []
    j = 1
    for i in range(1, n + 1):
        trending = requests.get(
            'https://api.themoviedb.org/3/trending/'+media_type+'/'+time_window+'?api_key=' + tmdbKey)
        trending_topics = trending.json()
        trending_topics_list = trending_topics['results']
        for movie in trending_topics_list:
            response.append(movie)
            if j > number_of_listed:
                break
            j += 1
    return response


def get_most_popular_movies_by_genre(number_of_listed=10, genre_id=28):
    # 28 Action, 12 Adventure, 16 Animation, 35 Comedy, 80 Crime, 99 Documentary, 18 Drama,
    # 10751 Family, 14 Fantasy, 36 History, 27 Horror, 10402 Music, 9648 Mystery, 10749 Romance,
    # 878 SF, 10770 Tv Movie, 53 Thriller, 10752 War
    n = math.ceil(number_of_listed / 20)
    response = []
    j = 1
    for i in range(1, n + 1):
        movies = requests.get(
            'https://api.themoviedb.org/3/discover/movie?api_key=' + tmdbKey + '&with_genres=' + str(genre_id) +
            '&sort_by=popularity.desc&page=' + str(i))
        popular = movies.json()
        popular_movies = popular['results']
        for movie in popular_movies:
            response.append(movie)
            if j > number_of_listed:
                break
            j += 1
    return response


def get_movies_with_highest_revenue_by_genre(number_of_listed=10, genre_id=28):
    n = math.ceil(number_of_listed / 20)
    response = []
    j = 1
    for i in range(1, n + 1):
        movies = requests.get(
            'https://api.themoviedb.org/3/discover/movie?api_key=' + tmdbKey + '&with_genres=' + str(genre_id) +
            '&sort_by=revenue.desc&page=' + str(i))
        popular = movies.json()
        popular_movies = popular['results']
        for movie in popular_movies:
            response.append(movie)
            if j > number_of_listed:
                break
            j += 1
    for movie in response:
        print(movie['title'])
    return response


def get_the_most_successful_companies(p=0.8):
    companies_ratings = {}
    companies_revenue = {}
    companies_grade = {}
    revenue, ratings = get_the_most_successful()
    i = 0
    for movie_id in revenue:
        for company in tmdb.Movies(id=movie_id).info()['production_companies']:
            if company['name'] in companies_revenue:
                companies_revenue[company['name']] += (50-i)
            else:
                companies_revenue[company['name']] = (50 - i)
        i += 1
    i = 0
    for movie_id in ratings:
        for company in tmdb.Movies(id=movie_id).info()['production_companies']:
            if company['name'] in companies_ratings:
                companies_ratings[company['name']] += (50-i)
            else:
                companies_ratings[company['name']] = (50 - i)
        i += 1
    for company in companies_revenue:
        companies_grade[company] = companies_revenue[company] * p
    for company in companies_ratings:
        if company in companies_grade:
            companies_grade[company] += companies_ratings[company] * (1-p)
        else:
            companies_grade[company] = companies_ratings[company] * (1-p)
    companies = {k: v for k, v in companies_grade.items() if v > 50}
    return sorted(companies.items(), key=lambda x: x[1], reverse=True)


def get_the_most_successful_actors(p=0.3):
    actors_ratings = {}
    actors_revenue = {}
    actors_grade = {}
    revenue, ratings = get_the_most_successful()
    i = 0
    for movie_id in revenue:
        cast = tmdb.Movies(id=movie_id).credits()['cast']
        cast_size = len(cast)
        for j in range(0, cast_size):
            if str(cast[j]['name']) in actors_revenue:
                actors_revenue[str(cast[j]['name'])] += ((50 - i)*(cast_size-j)/cast_size)
            else:
                actors_revenue[str(cast[j]['name'])] = ((50 - i)*(cast_size-j)/cast_size)
        i += 1
    i = 0
    for movie_id in ratings:
        cast = tmdb.Movies(id=movie_id).credits()['cast']
        cast_size = len(cast)
        for j in range(0, cast_size):
            if str(cast[j]['name']) in actors_ratings:
                actors_ratings[str(cast[j]['name'])] += ((50 - i)*(cast_size-j)/cast_size)
            else:
                actors_ratings[str(cast[j]['name'])] = ((50 - i)*(cast_size-j)/cast_size)
        i += 1
    for actor in actors_revenue:
        actors_grade[actor] = actors_revenue[actor] * p
    for actor in actors_ratings:
        if actor in actors_grade:
            actors_grade[actor] += actors_ratings[actor] * (1-p)
        else:
            actors_grade[actor] = actors_ratings[actor] * (1-p)
    actors = {k: v for k, v in actors_grade.items() if v > 50}
    return sorted(actors.items(), key=lambda x: x[1], reverse=True)


def get_the_most_successful():
    # movie_ids
    highest_revenue_id = []
    top_rated_id = []
    #get movie ids
    highest_grossing_movies = get_highest_grossing_movies(number_of_movies_taken=50)
    for movie in highest_grossing_movies:
        highest_revenue_id.append(movie['id'])
    top_rated_movies = get_top_rated_movies_ever(number_of_listed=50)
    for movie in top_rated_movies:
        top_rated_id.append(movie['id'])
    return highest_revenue_id, top_rated_id

"""
def test():
    print(tmdb.Movies(id=808).keywords())
    return"""


def main():
    """for movie in get_top_rated_movies_ever():
        print(movie['title'])"""
    print(get_the_most_successful_companies())
    print(get_the_most_successful_actors())
    #lista = get_upcoming_movies()
    #print(get_trending())

if __name__ == '__main__':
    main()
