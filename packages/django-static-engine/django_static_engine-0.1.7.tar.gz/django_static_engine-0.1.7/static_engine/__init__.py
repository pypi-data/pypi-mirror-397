from django.conf import settings

STATICSITE_USE_DIR_TEMPLATE = getattr(settings, 'STATICSITE_USE_DIR_TEMPLATE', False)
STATICSITE_DIR = getattr(settings, 'STATICSITE_DIR', settings.BASE_DIR / 'src')
