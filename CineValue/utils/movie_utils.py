from ..models import IMDb250, Liked, Movie, Rating, WatchList

def count_avg_rating(kp, data_whatson):

    service_count=0
    rating_count=0

    if kp is not None:
        kp_rating = kp.get('rating', {}).get('kp', '–')
        if kp_rating != '–' and kp_rating != 0:
            service_count += 1
            rating_count += kp_rating
        

    if data_whatson:

        imdb_rating = (data_whatson.get('imdb') or {}).get('users_rating', '–')
        if imdb_rating != '–':
            service_count += 1
            rating_count += imdb_rating

        rt_rating_critics = (data_whatson.get('rotten_tomatoes') or {}).get('critics_rating', '–')
        if rt_rating_critics != '–':
            service_count += 1
            rating_count += rt_rating_critics / 10

        metacritic_rating = (data_whatson.get('metacritic') or {}).get('critics_rating', '–')
        if metacritic_rating != '–':
            service_count += 1
            rating_count += metacritic_rating / 10

        letterboxd_rating = (data_whatson.get('letterboxd') or {}).get('users_rating', '–')
        if letterboxd_rating != '–':
            service_count += 1
            rating_count += letterboxd_rating * 2

        average_rating = round(rating_count / service_count, 1) if service_count > 0 else '–'
    else:
        average_rating = None

    return average_rating


def round_to_M(amount):
    round(amount / 1_000_000) if amount else 0
    return amount


def check_user_movie_status(user, movie):

    if not user.is_authenticated:
        return {
            'is_in_watchlist': False,
            'is_in_liked': False,
            'is_rated': False,
        }
    
    return {
        'is_in_watchlist': WatchList.objects.filter(user=user, movie=movie).exists(),
        'is_in_liked': Liked.objects.filter(user=user, movie=movie).exists(),
        'is_rated': Rating.objects.filter(user=user, movie=movie).exists(),
    }

def get_backdrop_url(movie, data_whatson):
    if movie.backdrop_path:
        return f'https://image.tmdb.org/t/p/original{movie.backdrop_path}'
    elif data_whatson and data_whatson.get('image'):
        return data_whatson.get('image')
    return ''