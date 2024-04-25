from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from config.views import base_html_view

schema_view = get_schema_view(
	openapi.Info(
		title="Boxproduction",
		default_version='v1',
		description='Box Project',
		terms_of_service='demo.uz',
		contact=openapi.Contact(email='sanjarwer93@gmail.com'),
		license=openapi.License(name="demo license")
	),
	public=True,

)

urlpatterns = [
	# basic urls
	path('admin/', admin.site.urls),
	path('', base_html_view, name='base_html'),
	path('production/', include('apps.production.urls')),
	path('', include('apps.users.urls')),
	path('depo/', include('apps.depo.urls')),
	path('info/', include('apps.info.urls')),

	# swagger
	path('swagger/', schema_view.with_ui(
		'swagger', cache_timeout=0), name='swagger-swagger-ui')

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
