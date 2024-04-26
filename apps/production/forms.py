from django import forms
from django.forms import inlineformset_factory

from apps.info.models import Material, BoxSize, BoxType, Firm
from apps.production.models import BoxModel
from .models import BoxOrder, BoxOrderDetail


class BoxModelForm(forms.ModelForm):
	class Meta:
		model = BoxModel
		fields = ['name', 'material', 'box_size', 'box_type', 'closure_type', 'additional_properties', 'max_load',
				  'color', 'comment', 'photo']
		labels = {
			'name': '',
			'closure_type': 'Тип замыкания',
			'additional_properties': 'Дополнительные свойства',
			'max_load': 'Максимальная нагрузка',
			'color': 'Цвет',
			'comment': 'Комментарий',
		}
		widgets = {
			'name': forms.TextInput(attrs={'class': 'form-control mb-3 mt-3', 'placeholder': 'Введите название'}),
			'material': forms.Select(attrs={'class': 'form-select mb-3', 'placeholder': 'Выберите материал'}),
			'box_size': forms.Select(attrs={'class': 'form-select mb-3', 'placeholder': 'Выберите размер'}),
			'box_type': forms.Select(attrs={'class': 'form-select mb-4', 'placeholder': 'Выберите тип коробки'}),
			'closure_type': forms.Select(attrs={'class': 'form-select mb-3', 'placeholder': 'Выберите тип замыкания'}),
			'additional_properties': forms.TextInput(
				attrs={'class': 'form-control mb-3', 'placeholder': 'Введите дополнительные свойства'}),
			'max_load': forms.TextInput(
				attrs={'class': 'form-control mb-3', 'placeholder': 'Введите максимальную нагрузку'}),
			'color': forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Введите цвет'}),
			'comment': forms.Textarea(
				attrs={'class': 'form-control mb-3', 'rows': 3, 'placeholder': 'Введите комментарий'}),
			'photo': forms.ClearableFileInput(attrs={'class': 'form-control', 'id': 'photo', 'name': 'photo'})
		}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['material'].queryset = Material.objects.all()
		self.fields['box_size'].queryset = BoxSize.objects.all()
		self.fields['box_type'].queryset = BoxType.objects.all()


class BoxOrderForm(forms.ModelForm):
	customer = forms.ModelChoiceField(queryset=Firm.objects.all(), empty_label='Заказчик',
									  widget=forms.Select(attrs={'class': 'form-control'}))
	customer_buyer = forms.ModelChoiceField(queryset=Firm.objects.all(), empty_label='Покупатель',
											widget=forms.Select(
												attrs={'class': 'form-control',
													   'placeholder': 'Введите имя покупателя'}))

	class Meta:
		model = BoxOrder
		fields = ['customer', 'type_order', 'specification', 'date_of_production']
		widgets = {
			'data': forms.DateInput(attrs={'class': 'form-control'}),
			'type_order': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Тип заказа'}),
			'specification': forms.Select(attrs={'class': 'form-control', }),
			'date_of_production': forms.DateInput(
				attrs={'class': 'form-control', 'type': 'date', }),
		}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['specification'].empty_label = 'Cпецификация'


class BoxOrderDetailForm(forms.ModelForm):
	class Meta:
		model = BoxOrderDetail
		fields = ['box_model', 'amount']
		widgets = {
			'box_model': forms.Select(attrs={'class': 'form-control mb-3', 'name': 'box_model', 'id': 'box_model'}),
			'amount': forms.NumberInput(
				attrs={'class': 'form-control', 'name': 'amount', 'id': 'amount', 'placeholder': 'Введите количеству'}),
		}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['box_model'].queryset = BoxModel.objects.all()


BoxOrderDetailFormSet = inlineformset_factory(BoxOrder, BoxOrderDetail, form=BoxOrderDetailForm, extra=1)
