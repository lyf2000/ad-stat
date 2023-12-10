import base64

from django import template
from django.contrib.staticfiles.finders import find as find_static_file

register = template.Library()


def get_file_data(file_path: str) -> bytes:
    """
    @param file_path: Path of the file to get the data
    """
    with open(file_path, "rb") as f:
        data = f.read()
        f.close()
        return data


@register.simple_tag
def encode_static_base_64(path: str) -> str:
    """
    A template tag that returns an encoded string representation of a static file
    Usage::
        {% encode_static_base_64 path [encoding] %}
    Examples::
        <img src="{% encode_static_base_64 'path/to/img.png' %}">
    """
    try:
        file_path = find_static_file(path)
        if file_path is None:
            return ""

        ext = file_path.split(".")[-1]
        file_str = base64.b64encode(get_file_data(file_path)).decode("utf-8")
        return f"data:image/{ext};base64,{file_str}"
    except IOError:
        return ""
