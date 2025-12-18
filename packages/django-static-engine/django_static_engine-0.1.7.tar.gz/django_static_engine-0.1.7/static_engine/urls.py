from django.urls import path
from . import STATICSITE_DIR
from .views import view_constructor


def url_constructor(base_dir: str):
    view = view_constructor(base_dir)
    return [
        path('', lambda request: view(request, ''), name='src_root'),
        path('<path:path>', view, name='src'),
    ]


urlpatterns = url_constructor(STATICSITE_DIR)

