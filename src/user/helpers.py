from django.db import ProgrammingError
from django.urls import URLResolver, URLPattern

from .models import ViewPermission


def reg_urls_to_rule(urlpatterns):
    try:
        for url in urlpatterns:
            if isinstance(url, URLResolver):
                if url.namespace == 'admin' or url.namespace == 'accounts':
                    continue
                reg_urls_to_rule(url.url_patterns)
            elif isinstance(url, URLPattern):
                ViewPermission.objects.get_or_create(
                    view_name=url.lookup_str,
                    path_name=url.name,
                )
    except ProgrammingError:
        pass