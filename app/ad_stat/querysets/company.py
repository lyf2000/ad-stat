from common.utils import user_admin
from django.db.models import QuerySet


class CompanyQuerySet(QuerySet):
    def of_user(self, user_id: int | None = None, user=None) -> QuerySet["Company"]:
        if user_admin(user, user_id):  # admin users have full access
            return self

        user_id = user_id or user.id

        return self.filter(company_groups__users__id__in=[user_id])
