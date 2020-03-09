from django.conf import settings
from django.contrib import admin
from django.views.static import serve
from django.urls import re_path, include

from rest_framework.documentation import include_docs_urls


API_TITLE = 'API Documents'
API_DESCRIPTION = 'API Information'

urlpatterns = [
    re_path(r'^htgl/', admin.site.urls),
    re_path(r'^api/', include('app.urls_api', namespace='api')),
    re_path(r'^page/', include('app.urls', namespace='page')),
    re_path(r'^api-auth/', include('rest_framework.urls')),
    re_path(r'^docs/', include_docs_urls(title=API_TITLE, description=API_DESCRIPTION)),
]


urlpatterns += [
    re_path(
        r'^{0}(?P<path>.*)$'.format(settings.STATIC_URL[1:]),
        serve, {'document_root': settings.STATIC_ROOT}, name='static'),
    re_path(
        r'^{0}(?P<path>.*)$'.format(settings.MEDIA_URL[1:]),
        serve, {'document_root': settings.MEDIA_ROOT}, name='media'),
]
