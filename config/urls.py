from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions


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
    permission_classes=[permissions.AllowAny],

)


urlpatterns = [
    # basic urls
    path('admin/', admin.site.urls),
    path('', include('apps.production.urls')),
    path('', include('apps.users.urls')),
    path('depo/', include('apps.depo.urls')),
    path('info/', include('apps.info.urls')),


    # api urls
    path('api/production', include('apps.api.urls.production')),
    path('api/info/', include('apps.api.urls.info')),
    path('api/depo/', include('apps.api.urls.depo')),

    # dj-rest-auth
    path('api-auth/', include('rest_framework.urls')),
    path('api/rest-auth/', include('dj_rest_auth.urls')),
    path('api/rest-auth/registration', include('dj_rest_auth.registration.urls')),

    # swagger
    path('swagger/', schema_view.with_ui(
        'swagger', cache_timeout=0), name='swagger-swagger-ui')

]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
