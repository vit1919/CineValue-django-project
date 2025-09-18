import os
import django
import csv
from datetime import datetime

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movie.settings')
django.setup()

from CineValue.models import Movie

def clean_value(value):
    """Очистить значение от null/пустых"""
    if value in ['', 'None', '[null]', None, 'null']:
        return None
    return value

def safe_int(value):
    """Безопасное преобразование в int"""
    if not value or value in ['', '[null]', 'null']:
        return None
    try:
        return int(float(value))
    except:
        return None

def safe_float(value):
    """Безопасное преобразование в float"""
    if not value or value in ['', '[null]', 'null']:
        return None
    try:
        return float(value)
    except:
        return None

def safe_bool(value):
    """Безопасное преобразование в bool"""
    if value in ['True', 'true', '1', 1, True]:
        return True
    return False

def safe_date(date_str):
    """Безопасное преобразование даты"""
    if not date_str or date_str in ['', '[null]', 'null']:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except:
        return None

def should_skip_movie(row):
    """Проверить нужно ли пропустить фильм"""
    
    # 1. Пропускаем если нет IMDB ID
    imdb_id = clean_value(row.get('imdb_id'))
    if not imdb_id:
        return True, "Нет IMDB ID"
    
    # 2. Пропускаем короткие фильмы (менее 60 минут)
    runtime = safe_int(row.get('runtime'))
    if runtime and runtime < 60:
        return True, f"Короткий фильм ({runtime} мин)"
    
    # 3. Пропускаем взрослые фильмы
    adult = safe_bool(row.get('adult'))
    if adult:
        return True, "Взрослый контент"
    
    # 4. Пропускаем фильмы без названия
    title = row.get('title', '').strip()
    if not title:
        return True, "Нет названия"
    
    # 5. Пропускаем фильмы с низким рейтингом (менее 4.0)
    vote_average = safe_float(row.get('vote_average'))
    if vote_average and vote_average <= 4.0:
        return True, f"Низкий рейтинг ({vote_average})"
    
    # 6. Пропускаем фильмы с малым количеством голосов (менее 100)
    vote_count = safe_int(row.get('vote_count'))
    if vote_count and vote_count <= 100:
        return True, f"Мало голосов ({vote_count})"
    
    return False, None

def import_filtered_movies(csv_path):
    print(f"Начинаем фильтрованный импорт из {csv_path}")
    print("Фильтры:")
    print("- Только с IMDB ID")
    print("- Только полнометражные (60+ минут)")
    print("- Исключаем взрослый контент")
    print("- Только с названием")
    print("- Рейтинг > 5.0")
    print("- Количество голосов > 300")
    print()
    
    if not os.path.exists(csv_path):
        print(f"Файл {csv_path} не найден!")
        return
    
    count_imported = 0
    count_skipped = 0
    count_errors = 0
    skip_reasons = {}
    
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        print("Доступные колонки в CSV:")
        for i, col in enumerate(reader.fieldnames):
            print(f"{i+1}. {col}")
        print()
        
        for row_num, row in enumerate(reader, 1):
            try:
                # Проверяем нужно ли пропустить
                should_skip, skip_reason = should_skip_movie(row)
                
                if should_skip:
                    count_skipped += 1
                    skip_reasons[skip_reason] = skip_reasons.get(skip_reason, 0) + 1
                    continue
                
                # Проверяем дубликаты
                tmdb_id = clean_value(row.get('id'))
                imdb_id = clean_value(row.get('imdb_id'))
                
                if Movie.objects.filter(tmdb_id=tmdb_id).exists() or \
                   Movie.objects.filter(imdb_id=imdb_id).exists():
                    count_skipped += 1
                    skip_reasons["Дубликат"] = skip_reasons.get("Дубликат", 0) + 1
                    continue
                
                # Создаем фильм со всеми полями
                movie = Movie.objects.create(
                    # Основные поля
                    title=row.get('title', '').strip(),
                    original_title=clean_value(row.get('original_title')),
                    original_language=clean_value(row.get('original_language')),
                    year=safe_int(row.get('release_date', '')[:4] if row.get('release_date') else None),
                    overview=clean_value(row.get('overview')),
                    
                    # ID поля
                    tmdb_id=tmdb_id,
                    imdb_id=imdb_id,
                    
                    # Статус и даты
                    status=clean_value(row.get('status')),
                    release_date=safe_date(row.get('release_date')),
                    
                    # Флаги и числа
                    adult=safe_bool(row.get('adult')),
                    budget=safe_int(row.get('budget')),
                    revenue=safe_int(row.get('revenue')),
                    
                    # Контент
                    genres=row.get('genres', '').strip()[:500],
                    
                    # Рейтинги
                    vote_average=safe_float(row.get('vote_average')),
                    vote_count=safe_int(row.get('vote_count')),
                    popularity=safe_float(row.get('popularity')),
                    
                    # Изображения
                    poster_path=clean_value(row.get('poster_path')),
                    backdrop_path=clean_value(row.get('backdrop_path')),
                    
                    # Дополнительные поля
                    production_countries=clean_value(row.get('production_countries', ''))[:200] if row.get('production_countries') else None,
                )
                
                count_imported += 1
                
                # Показываем прогресс
                if count_imported % 100 == 0:
                    print(f"Импортировано: {count_imported} | Пропущено: {count_skipped} | Строка: {row_num}")
                    
            except Exception as e:
                count_errors += 1
                if count_errors <= 10:
                    print(f"Ошибка в строке {row_num}: {e}")
                continue
    
    print(f"\n{'='*50}")
    print(f"ИМПОРТ ЗАВЕРШЕН!")
    print(f"{'='*50}")
    print(f"Успешно импортировано: {count_imported} фильмов")
    print(f"Всего пропущено: {count_skipped}")
    print(f"Ошибок: {count_errors}")
    
    print(f"\nПричины пропуска:")
    for reason, count in sorted(skip_reasons.items(), key=lambda x: x[1], reverse=True):
        print(f"- {reason}: {count}")

if __name__ == "__main__":
    csv_file_path = 'data/movies.csv'  # путь к вашему CSV
    import_filtered_movies(csv_file_path)
