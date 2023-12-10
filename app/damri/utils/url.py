from django.core.validators import URLValidator


def is_url(text: str):
    val = URLValidator()
    try:
        val(text)
        return True
    except:
        return False
