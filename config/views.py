from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def base_html_view(request):
	return render(request, 'base.html')
