def validate_rating(rating_str):
    if not rating_str:
        raise ValueError("Rating is required")
    try:
        rating = int(rating_str)
        if not 1 <= rating <= 10:
            raise ValueError()
        return rating
    except (TypeError, ValueError):
        raise ValueError("Rating must be a number between 1 and 10")
