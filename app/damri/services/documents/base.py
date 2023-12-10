from io import BytesIO

from weasyprint import HTML


def html_to_pdf(content: BytesIO) -> bytes:
    return HTML(string=content).write_pdf()
