class ContextMixin:
    def __init__(self, context: dict|None = None):
        self._context = context or {}
