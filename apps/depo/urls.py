from django.urls import path

from apps.depo.views import IncomingListView, IncomingCreate, OutgoingCreate, OutgoingListView

app_name = 'depo'

urlpatterns = [
	path('incoming/', IncomingListView.as_view(), name='incoming-list'),
	path('incoming/create/', IncomingCreate.as_view(), name='incoming-create'),

	path('outgoing/', OutgoingListView.as_view(), name='outgoing-list'),
	path('outgoing/create/', OutgoingCreate.as_view(), name='outgoing-create'),
]
