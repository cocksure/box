from django.urls import path
from apps.api.views.production import ProcessListCreate, BoxModelListCreate, BoxModelDetail, BoxOrderListCreate, \
	BoxOrderDetailView, \
	ProductionOrderCreate

app_name = 'api'

urlpatterns = [
	path('processes/', ProcessListCreate.as_view(), name='process-list'),
	path('boxmodels/', BoxModelListCreate.as_view(), name='boxmodel-list'),
	path('boxmodels/<int:pk>/', BoxModelDetail.as_view(), name='boxmodel-detail'),
	path('boxorders/', BoxOrderListCreate.as_view(), name='boxorder-list'),
	path('boxorders/<int:pk>/', BoxOrderDetailView.as_view(), name='boxorder-detail'),
	path('boxorderdetails/<int:pk>/production-order/', ProductionOrderCreate.as_view(), name='production-order-create'),
]
