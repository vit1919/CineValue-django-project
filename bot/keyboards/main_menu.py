from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


search_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Search movie')],
    ]
)


def build_movies_keyboard(movies):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=f"{m['title']} ({m['year'] or '—'})",
                callback_data=f"movie:{m['id']}"
            )]
            for m in movies
        ]
    )
