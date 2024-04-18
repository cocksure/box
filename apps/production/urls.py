from django.urls import path
from .views import base_html_view, BoxModelListCreate, BoxModelEdit, BoxOrderListView, BoxOrderListCreate

urlpatterns = [
	path('', base_html_view, name='base_html'),
	path('boxmodel/', BoxModelListCreate.as_view(), name='box-model-list'),
	path('boxmodel/edit/<int:pk>/', BoxModelEdit.as_view(), name='box-model-edit'),
	path('boxorders/', BoxOrderListView.as_view(), name='box-order-list'),
	path('boxorders/create/', BoxOrderListCreate.as_view(), name='box-order-create'),
]
