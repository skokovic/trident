import tmdbsimple as tmdb
import pandas as pd
import MovieStatistics as ms

tmdbKey: str = "b2dd64617f8c64de2a3c3c0ada9f73ec"
tmdb.API_KEY = tmdbKey


def get_list_of_liked_movies_by_user(user_id):
    #zamijeniti s pravom listom
    if (user_id==0):
        return [24428, 299536, 99861]
    elif (user_id==1):
        return [24428]
    else:
        return [299536, 99861]


def get_list_of_disliked_movies_by_user(user_id):
    #zamijeniti s pravom listom
    if (user_id==0):
        return []
    elif (user_id==1):
        return [99861]
    else:
        return []


def get_similar_movies(movies):
    similar = {}
    for movie in movies:
        tmp = tmdb.Movies(id=movie).similar_movies()['results']
        for film in tmp:
            if film['id'] in similar:
                similar[film['id']] += 1
            else:
                similar[film['id']] = 1
    return similar


def combine_liked_and_disliked_similar(similar_liked, similar_disliked):
    for movie_id in similar_disliked:
        if movie_id in similar_liked:
            similar_liked[movie_id] -= similar_disliked[movie_id]
        else:
            similar_liked[movie_id] = similar_disliked[movie_id]*-1
    similar = {k: v for k, v in similar_liked.items() if v > 0}
    return sorted(similar.items(), key=lambda x: x[1], reverse=True)


def remove_already_watched(liked, disliked, liked_similar, disliked_similar):
    for movie_id in liked:
        if movie_id in liked_similar:
            liked_similar.pop(movie_id)
        if movie_id in disliked_similar:
            disliked_similar.pop(movie_id)
    for movie_id in disliked:
        if movie_id in liked_similar:
            liked_similar.pop(movie_id)
        if movie_id in disliked_similar:
            disliked_similar.pop(movie_id)
    return liked_similar, disliked_similar


def get_similar_movies_with_grades(user_id):
    liked = get_list_of_liked_movies_by_user(user_id)
    liked_similar = get_similar_movies(liked)
    disliked = get_list_of_disliked_movies_by_user(user_id)
    disliked_similar = get_similar_movies(disliked)
    liked_similar, disliked_similar = remove_already_watched(liked, disliked, liked_similar, disliked_similar)
    return combine_liked_and_disliked_similar(liked_similar, disliked_similar)


def get_recommendation(user_id):
    similar_movies_of_user = get_similar_movies_with_grades(user_id)
    return similar_movies_of_user


def get_list_of_all_graded_movies(users):
    movie_ids = []
    for user in users:
        for movie_id in get_list_of_liked_movies_by_user(user):
            if movie_id not in movie_ids:
                movie_ids.append(movie_id)
        for movie_id in get_list_of_disliked_movies_by_user(user):
            if movie_id not in movie_ids:
                movie_ids.append(movie_id)
    return movie_ids


def make_ratings_table():
    users = [0, 1, 2]  # zamijeniti s getanjem liste svih usera
    movie_ids = get_list_of_all_graded_movies(users)
    ratings = pd.DataFrame(index=users, columns=movie_ids, data=0).astype(int)
    for user in users:
        liked_movies = get_list_of_liked_movies_by_user(user)
        disliked_movies = get_list_of_disliked_movies_by_user(user)
        for movie in movie_ids:
            if movie in liked_movies:
                ratings.at[user, movie] = 1
            if movie in disliked_movies:
                ratings.at[user, movie] = -1
    return ratings


def get_similar_users_movie_recommendation(user_id):
    ratings = make_ratings_table()
    similar_users = {}
    users = [0, 1, 2] #zamijeni sa get all users
    movies = get_list_of_all_graded_movies(users)
    users.remove(user_id)
    for user in users:
        up = 0
        down = 0
        for movie in movies:
            if ratings.at[user, movie] != 0 or ratings.at[user_id, movie] != 0:
                down += 1
                if ratings.at[user, movie] == ratings.at[user_id, movie]:
                    up += 1
                elif ratings.at[user, movie] != ratings.at[user_id, movie] and ratings.at[user, movie] != 0 and ratings.at[user_id, movie] != 0:
                    up -= 1
        similar_users[user] = up/down

    similar = {k: v for k, v in similar_users.items() if v >= 0.5}
    similar_users = sorted(similar.items(), key=lambda x: x[1], reverse=True)
    movies_to_recommend = {}
    already_watched = get_list_of_liked_movies_by_user(user_id) + get_list_of_disliked_movies_by_user(user_id)
    for user, grade in similar_users:
        for movie in get_list_of_liked_movies_by_user(user):
            if movie not in already_watched:
                if movie not in movies_to_recommend:
                    movies_to_recommend[movie] = grade*10
                else:
                    movies_to_recommend[movie] += grade*10
    return movies_to_recommend


def get_recommended_movies(user_id):
    if len(get_list_of_liked_movies_by_user(user_id)) == 0 and len(get_list_of_disliked_movies_by_user(user_id)) == 0:
        ids = []
        for movie in ms.get_most_popular_movies_today():
            ids.append(movie['id'])
        return ids
    else:
        ids = []
        similar_movies = dict(get_similar_movies_with_grades(user_id))
        liked_by_similar_users = get_similar_users_movie_recommendation(user_id)
        for movie in liked_by_similar_users:
            if movie in similar_movies:
                similar_movies[movie] += liked_by_similar_users[movie]
            else:
                similar_movies[movie] = liked_by_similar_users[movie]
        sorted_movies = sorted(similar_movies.items(), key=lambda x: x[1], reverse=True)
        for movie in sorted_movies:
            ids.append(movie[0])
        return ids