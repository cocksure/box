from django.urls import path

from apps.depo import utils
from apps.depo.views import IncomingListView, IncomingCreate, OutgoingCreate, OutgoingListView, UnacceptedOutgoingsView, \
	OutgoingDetailView, IncomingDetailView, StockListView

app_name = 'depo'

urlpatterns = [
	path('incoming/', IncomingListView.as_view(), name='incoming-list'),
	path('incoming/create/', IncomingCreate.as_view(), name='incoming-create'),
	path('incoming/<int:pk>/', IncomingDetailView.as_view(), name='incoming-detail'),

	path('outgoing/', OutgoingListView.as_view(), name='outgoing-list'),
	path('outgoing/create/', OutgoingCreate.as_view(), name='outgoing-create'),
	path('outgoing/<int:pk>/', OutgoingDetailView.as_view(), name='outgoing-detail'),

	path('stock/', StockListView.as_view(), name='stock-list'),

	path('unaccepted/', UnacceptedOutgoingsView.as_view(), name='unaccepted-list'),

	path('check_material_availability/', utils.check_material_availability, name='check_material_availability'),

]
