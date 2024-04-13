from django.urls import path

from apps.api.views.incoming import IncomingMaterialListView
from apps.depo.views import IncomingListView, IncomingDetailView

app_name = 'depo'

urlpatterns = [
	path('incoming/', IncomingListView.as_view(), name='incoming-list'),
	path('incoming-materials/', IncomingMaterialListView.as_view(), name='incoming-materials-list'),
	path('incoming/<int:pk>/', IncomingDetailView.as_view(), name='incoming-detail'),
]
