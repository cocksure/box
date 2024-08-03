from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin
import time
from django.core.cache import cache


class RateLimitMiddleware(MiddlewareMixin):
	def process_request(self, request):
		key = f"rate_limit_{request.META['REMOTE_ADDR']}"
		limit = 6
		period = 2

		current_time = time.time()
		request_count = cache.get(key)
		last_request_time = cache.get(f"{key}_time", current_time)

		if current_time - last_request_time > period:
			# Reset the count and time
			cache.set(key, 1, timeout=period)
			cache.set(f"{key}_time", current_time, timeout=period)
		else:
			if request_count is None:
				request_count = 1
			else:
				request_count += 1

			if request_count > limit:
				return HttpResponse('Слишком много запросов', status=429)
			else:
				cache.set(key, request_count, timeout=period)

		return None
