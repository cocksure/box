from django.urls import path

from apps.api.views.incoming import IncomingListApiApiView, IncomingCreateApiView, IncomingDetailView
from apps.api.views.outgoing import OutgoingListApiView, OutgoingCreateView, OutgoingDetailView
from apps.api.views.stock import StockDetailView, UnacceptedMaterialsListView, UnacceptedMaterialsDetailView, \
	StockListApiView

app_name = 'api'

urlpatterns = [
	path('incoming/', IncomingListApiApiView.as_view(), name='incoming-list'),
	path('incoming/create/', IncomingCreateApiView.as_view(), name='incoming-create'),
	path('incoming/detail/<int:pk>/', IncomingDetailView.as_view(), name='incoming-detail'),

	path('outgoing/', OutgoingListApiView.as_view(), name='outgoing-list'),
	path('outgoing/create/', OutgoingCreateView.as_view(), name='outgoing-create'),
	path('outgoing/detail/<int:pk>/', OutgoingDetailView.as_view(), name='outgoing-detail'),

	path('stock/', StockListApiView.as_view(), name='stock-list'),
	path('stock-detail/<int:pk>/', StockDetailView.as_view(), name='stock-detail'),

	path('unaccepted-materials/', UnacceptedMaterialsListView.as_view(), name='unaccepted-materials-list'),
	path('unaccepted-materials/<int:outgoing_id>/', UnacceptedMaterialsDetailView.as_view(),
		 name='unaccepted-material-detail'),
]
