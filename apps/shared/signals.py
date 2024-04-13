from django.http import JsonResponse
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from dj_rest_auth.models import TokenModel


def get_actual_token_value(request):
    token, created = TokenModel.objects.get_or_create(user=request.user)
    return token.key


@receiver(user_logged_in)
def set_cookie_on_login(sender, request, user, **kwargs):
    token_value = get_actual_token_value(request)

    response_data = {
        'token': token_value,
        'user_id': user.pk,
        # Другие данные, которые вы хотите включить в ответ
    }

    response = JsonResponse(response_data)
    response.set_cookie('Admin-Token', value=token_value, samesite='None', secure=True)
    return response