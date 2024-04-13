from apps.depo.models.incoming import Incoming, IncomingMaterial
from django import forms
from apps.info.models import Warehouse, Material


class IncomingForm(forms.ModelForm):
	class Meta:
		model = Incoming
		fields = ['invoice', 'note', 'warehouse', 'data']
		labels = {
			'invoice': '',
			'note': '',
			'data': '',
		}
		widgets = {
			'invoice': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите инвойс'}),
			'warehouse': forms.Select(attrs={'class': 'form-select', 'placeholder': 'Выберите склад', 'required': True}),
			'data': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'placeholder': 'Дата', 'required': True}),
			'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 1, 'placeholder': 'Примечания'}),
		}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['warehouse'].queryset = Warehouse.objects.all()


class IncomingMaterialForm(forms.ModelForm):
	class Meta:
		model = IncomingMaterial
		fields = ['material', 'amount', 'comment']
		widgets = {
			'material': forms.Select(attrs={'class': 'form-select'}),
			'amount': forms.NumberInput(attrs={'class': 'form-control'}),
			'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
		}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['material'].queryset = Material.objects.all()
