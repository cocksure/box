from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth import get_user_model
from django import forms

CustomUser = get_user_model()


class CustomUserCreationForm(UserCreationForm):
	class Meta:
		model = CustomUser
		fields = ('username', 'password1', 'password2')


class CustomUserChangeForm(UserChangeForm):
	class Meta:
		model = CustomUser
		fields = (
			'username', 'first_name', 'last_name', 'email', 'is_staff', 'is_superuser', 'groups', 'user_permissions',)


class LoginForm(forms.Form):
	username = forms.CharField(max_length=15, label='',
							   widget=forms.TextInput(attrs={'placeholder': 'Логин', 'class': 'form-control'}),
							   required=True)
	password = forms.CharField(max_length=10, label='', widget=forms.PasswordInput(
		attrs={'placeholder': 'Пароль', 'class': 'form-control', 'autocomplete': 'on'}), required=True)
