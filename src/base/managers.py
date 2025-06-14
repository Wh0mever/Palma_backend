from django.db.models import QuerySet


class FlagsQuerySet(QuerySet):

    def get_available(self):
        return self.filter(is_deleted=False)
