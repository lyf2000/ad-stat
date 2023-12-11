MAX_MESSAGE_LENGTH = 4096


def split_text(text: str, length: int = MAX_MESSAGE_LENGTH) -> list[str]:
    """
    Split long text

    :param text:
    :param length:
    :return: list of parts
    :rtype: :obj:`typing.List[str]`
    """
    return [text[i : i + length] for i in range(0, len(text), length)]
