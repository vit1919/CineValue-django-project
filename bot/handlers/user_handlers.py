import asyncio
import logging

from aiogram import Router, types, F
from aiogram.filters import Command, CommandStart
from asgiref.sync import sync_to_async
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from CineValue.models.movie import Movie
from CineValue.api_services import get_kinopoisk_data_async, get_whatson_data_async
from CineValue.utils.movie_utils import count_avg_rating
from bot.keyboards.main_menu import build_movies_keyboard

logger = logging.getLogger(__name__)
router = Router()

class SearchStates(StatesGroup):
    waiting_for_query = State()

def _search_movies(query: str):
    return list(
        Movie.objects.filter(title__icontains=query)
        .order_by("-popularity", "title")[:10]
        .values("id", "title", "year", "tmdb_id", "vote_average", "genres", "overview")
    )

def _get_movie_by_id(movie_id: int):
    return Movie.objects.filter(id=movie_id).values(
        "id", "title", "year", "tmdb_id", "vote_average",
        "genres", "overview", "original_title",
    ).first()

def _format_ratings(kp, whatson) -> str:
    lines = []
    if kp and isinstance(kp, dict) and "error" not in kp:
        kp_rating = (kp.get("rating") or {}).get("kp")
        if kp_rating:
            lines.append(f"  Kinopoisk: {kp_rating}/10")

    if whatson and isinstance(whatson, dict) and "error" not in whatson:
        imdb_rating = (whatson.get("imdb") or {}).get("users_rating")
        if imdb_rating:
            lines.append(f"  IMDb: {imdb_rating}/10")

        rt_rating = (whatson.get("rotten_tomatoes") or {}).get("critics_rating")
        if rt_rating:
            lines.append(f"  Rotten Tomatoes: {rt_rating}/100")

        meta_rating = (whatson.get("metacritic") or {}).get("critics_rating")
        if meta_rating:
            lines.append(f"  Metacritic: {meta_rating}/100")

        lb_rating = (whatson.get("letterboxd") or {}).get("users_rating")
        if lb_rating:
            lines.append(f"  Letterboxd: {lb_rating}/5")

    if not lines:
        lines.append("  Нет данных по рейтингам")

    return "\n".join(lines)


@router.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        "CineValue — рейтинги фильмов\n\n"
        "Введите /search и название фильма,\n"
        "чтобы увидеть рейтинги из разных сервисов."
    )

@router.message(Command("search"))
async def start_search(message: types.Message, state: FSMContext):
    await message.answer("Введите название фильма:")
    await state.set_state(SearchStates.waiting_for_query)

@router.message(SearchStates.waiting_for_query)
async def process_search(message: types.Message, state: FSMContext):
    user_query = message.text.strip()
    if len(user_query) < 2:
        await message.answer("Введите минимум 2 символа.")
        return

    await message.answer(f"Ищу: <b>{user_query}</b>...", parse_mode="HTML")

    movies = await sync_to_async(_search_movies)(user_query)

    if not movies:
        await message.answer("Ничего не найдено. Попробуйте другой запрос.")
        await state.clear()
        return

    await message.answer(
        f"Найдено: {len(movies)}",
        reply_markup=build_movies_keyboard(movies),
    )
    await state.clear()


@router.callback_query(F.data.startswith("movie:"))
async def movie_details(callback: types.CallbackQuery):
    movie_id = int(callback.data.split(":", 1)[1])
    movie = await sync_to_async(_get_movie_by_id)(movie_id)

    if not movie:
        await callback.message.answer("Фильм не найден.")
        await callback.answer()
        return

    await callback.answer()

    await callback.message.answer("Загружаю рейтинги...")

    tmdb_id = movie.get("tmdb_id")
    tmdb_id_int = int(tmdb_id) if tmdb_id and str(tmdb_id).isdigit() else None

    if tmdb_id_int:
        kp, whatson = await asyncio.gather(
            get_kinopoisk_data_async(tmdb_id_int),
            get_whatson_data_async(tmdb_id_int),
        )
    else:
        kp, whatson = None, None

    ratings_text = _format_ratings(kp, whatson)
    avg = count_avg_rating(kp, whatson)

    genres = movie.get("genres") or ""
    genres_str = ", ".join(g.strip() for g in genres.split(",") if g.strip()) or "—"

    overview = movie.get("overview") or "Без описания"
    if len(overview) > 300:
        overview = overview[:300] + "..."

    year = f" ({movie['year']})" if movie.get("year") else ""
    text = f"🎬 {movie['title']}{year}\n"

    if movie.get("original_title") and movie["original_title"] != movie["title"]:
        text += f"({movie['original_title']})\n"

    text += f"\n🎭 {genres_str}\n"

    if avg and avg != "–":
        text += f"\n⭐ CineValue: {avg}/10\n"

    text += f"\n📊 Рейтинги:\n{ratings_text}\n"
    text += f"\n📝 {overview}\n"

    await callback.message.answer(text)
