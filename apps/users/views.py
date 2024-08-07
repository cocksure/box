from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.views import View

from .forms import LoginForm
from django.contrib import messages
import logging


def user_login(request):
	if request.method == "POST":
		form = LoginForm(request.POST)
		if form.is_valid():
			data = form.cleaned_data
			user = authenticate(request, username=data['username'], password=data['password'])

			if user is not None:
				if user.is_active:
					login(request, user)
					return redirect(reverse('base_html'))
				else:
					return render(request, 'users/login.html', {'form': form, 'error': 'Ваш пользователь не активен'})
			else:
				return render(request, 'users/login.html', {'form': form, 'error': 'Неверный логин или пароль'})

	else:
		form = LoginForm()

	return render(request, 'users/login.html', {'form': form})


class LogoutView(LoginRequiredMixin, View):
	def get(self, request):
		logout(request)
		return redirect("login")
