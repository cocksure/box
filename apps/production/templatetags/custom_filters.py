from django import template
import base64

register = template.Library()


@register.filter
def get_item(dictionary, key):
	return dictionary.get(key)


@register.filter(name='b64encode')
def b64encode(value):
	return base64.b64encode(value).decode('utf-8')
