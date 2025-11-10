import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movie.settings')
django.setup()

import csv
from CineValue.models import IMDb250


def safe_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def safe_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def import_IMDb250(csv_path):
    movies = []
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                movies.append(IMDb250(
                    rank=safe_int(row['Rank']),
                    title=row['Title'],
                    year=safe_int(row['Year']),
                    rating=safe_float(row['Rating']),
                    duration=row['Duration'],
                    certificate=row['Certificate'],
                    genres=row['Genres'],
                    description=row['Description'],
                    image_url=row['Image URL'],
                    movie_url=row['Movie URL'],
                ))
            except Exception as e:
                print(f"Ошибка в строке: {row.get('Title', '')}: {e}")
    IMDb250.objects.bulk_create(movies)
    print(f'Imported {len(movies)} movies')


if __name__ == '__main__':
    import_IMDb250('data/imdb_top_movies.csv')
