from rest_framework import routers

from apps.api.views.info import MaterialViewSetView, MaterialTypeViewSetView, WarehouseViewSetView, BoxTypeViewSet, \
	BoxSizeViewSet

app_name = 'api'
router = routers.DefaultRouter()

router.register(r'material/type', MaterialTypeViewSetView)
router.register(r'material', MaterialViewSetView)

router.register(r'warehouse', WarehouseViewSetView)
router.register(r'boxsize', BoxSizeViewSet)
router.register(r'boxtype', BoxTypeViewSet)

urlpatterns = []

urlpatterns += router.urls
