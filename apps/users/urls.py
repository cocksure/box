from django.urls import path

from .views import user_login, LogoutView

urlpatterns = [
	path('login/', user_login, name='login'),
	path('logut/', LogoutView.as_view(), name='logout'),

]
