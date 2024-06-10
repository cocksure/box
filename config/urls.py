from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from config.views import dashboard_view

urlpatterns = [
	# basic urls
	path('admin/', admin.site.urls),
	path('', dashboard_view, name='base_html'),
	path('production/', include('apps.production.urls')),
	path('', include('apps.users.urls')),
	path('depo/', include('apps.depo.urls')),
	path('info/', include('apps.info.urls')),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
