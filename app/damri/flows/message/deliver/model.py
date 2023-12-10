class MessageModelMixin:
    @classmethod
    def init(cls, *args, **kwargs):
        return cls.objects.create(*args, **kwargs)

    def ok(self, *args, **kwargs):
        self._ok(*args, **kwargs)
        self.save()

    def fail(self, *args, **kwargs):
        self._fail(*args, **kwargs)
        self.save()

    def empty(self):
        self._empty()
        self.save()

    def _empty(self, *args, **kwargs):
        pass

    def _fail(self, *args, **kwargs):
        pass

    def _ok(self, *args, **kwargs):
        pass
