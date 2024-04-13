from django import forms
from django.forms import formset_factory, inlineformset_factory

from .models import UploadImage, BoxOrder, BoxOrderDetail
from apps.info.models import Material, BoxSize, BoxType
from apps.production.models import BoxModel, Process


class BoxModelForm(forms.ModelForm):
	class Meta:
		model = BoxModel
		fields = ['name', 'material', 'type_of_work', 'box_size', 'box_type', 'photos']
		labels = {
			'name': '',
		}
		widgets = {
			'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название'}),
			'material': forms.Select(attrs={'class': 'form-select', 'placeholder': 'Выберите материал'}),
			'type_of_work': forms.SelectMultiple(
				attrs={'class': 'form-select', 'placeholder': 'Выберите тип работ', 'style': 'height: 180px;'}),
			'box_size': forms.Select(attrs={'class': 'form-select', 'placeholder': 'Выберите размер'}),
			'box_type': forms.Select(attrs={'class': 'form-select', 'placeholder': 'Выберите тип коробки'}),
			'photos': forms.Select(attrs={'class': 'form-select', 'placeholder': 'Выберите фото'}),
		}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['material'].queryset = Material.objects.all()
		self.fields['type_of_work'].queryset = Process.objects.all()
		self.fields['box_size'].queryset = BoxSize.objects.all()
		self.fields['box_type'].queryset = BoxType.objects.all()
		self.fields['photos'].queryset = UploadImage.objects.all()


class BoxOrderForm(forms.ModelForm):
	class Meta:
		model = BoxOrder
		fields = ['customer', 'type_order', 'specification', 'date_of_production']
		widgets = {
			'data': forms.DateInput(attrs={'class': 'form-control', }),
			'customer': forms.TextInput(attrs={'class': 'form-control'}),
			'type_order': forms.TextInput(attrs={'class': 'form-control'}),
			'specification': forms.TextInput(attrs={'class': 'form-control'}),
			'date_of_production': forms.DateInput(attrs={'class': 'form-control'}),
		}


class BoxOrderDetailForm(forms.ModelForm):
	class Meta:
		model = BoxOrderDetail
		fields = ['box_model', 'amount']
		widgets = {
			'box_model': forms.Select(attrs={'class': 'form-control', 'name': 'box_model', 'id': 'box_model'}),
			'amount': forms.NumberInput(attrs={'class': 'form-control', 'name': 'amount', 'id': 'amount'}),
		}


BoxOrderDetailFormSet = inlineformset_factory(BoxOrder, BoxOrderDetail, form=BoxOrderDetailForm, extra=1)
