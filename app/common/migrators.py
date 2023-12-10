"""Migrate raw data to DB services"""


# TODO: add celery caller
class BaseMigrator:
    def __call__(self):
        self.migrate()

    def migrate(self):
        raise NotImplementedError
