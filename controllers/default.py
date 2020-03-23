# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# This is a sample controller
# this file is released under public domain and you can use without limitations
# -------------------------------------------------------------------------


import pandas as pd


def load_recommendations():
    item_similarity_df = pd.read_csv("C:/Users/ashish/Desktop/web2py/applications/movies/static/item_similarity_df.csv",
                                     index_col=0)
    print("item_similarity_df cached in memory")
    return item_similarity_df


item_similarity_df = cache.ram('item_similarity_df3', load_recommendations, None)
print(item_similarity_df.head())


# ---- example index page ----
def index():
    response.flash = T("Hello World")
    return locals()
    # return dict(message=T('Welcome to web2py!'))


def login():
    return locals()


# ---- Action for login/register/etc (required for auth) -----
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())


# ---- action to server uploaded static content (required) ---
@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@service.json
def myapi():
    a = 'ashish'
    b = ' kumar'
    print("got: ", a, b)
    # concat two strings
    result = a + b
    return dict(result=result, status="success")


##helper method that doesn't recommend a movie if the user has already seen it
def check_seen(recommended_movie, watched_movies):
    for movie_id, movie in watched_movies.items():
        if recommended_movie == movie["title"]:
            return True
    return False


def get_similar_movies(movie_name, user_rating):
    try:
        similar_score = item_similarity_df[movie_name] * (user_rating - 2.5)
        similar_movies = similar_score.sort_values(ascending=False)
    except:
        print("don't have movie in model")
        similar_movies = pd.Series([])

    return similar_movies


@service.json
def get_recommendations(watched_movies):
    print(watched_movies)
    similar_movies = pd.DataFrame()

    for movie_id, movie in watched_movies.items():
        similar_movies = similar_movies.append(get_similar_movies(movie["title"], movie["rating"]), ignore_index=True)

    all_recommend = similar_movies.sum().sort_values(ascending=False)

    recommended_movies = []
    for movie, score in all_recommend.iteritems():
        if not check_seen(movie, watched_movies):
            recommended_movies.append(movie)

    if len(recommended_movies) > 100:
        recommended_movies = recommended_movies[0:10]

    return recommended_movies
