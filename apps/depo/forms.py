from django.forms import inlineformset_factory

from apps.depo.models.incoming import Incoming, IncomingMaterial
from django import forms

from apps.depo.models.outgoing import Outgoing, OutgoingMaterial
from apps.info.models import Warehouse, Material


class IncomingForm(forms.ModelForm):
	class Meta:
		model = Incoming
		fields = ['invoice', 'note', 'warehouse', 'contract_number', 'data']

		widgets = {
			'invoice': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите инвойс'}),
			'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 1, 'placeholder': 'Примечания'}),
			'warehouse': forms.Select(attrs={'class': 'form-control'}),
			'contract_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '№ Контракта'}),
			'data': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', }),
		}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['warehouse'].empty_label = 'Выберите склад'


class IncomingMaterialForm(forms.ModelForm):
	class Meta:
		model = IncomingMaterial
		fields = ['material', 'amount', 'comment']
		widgets = {
			'material': forms.Select(attrs={'class': 'form-select mb-3 incoming_material', 'id': 'incoming_material',
											'name': 'incoming_material'}),
			'amount': forms.NumberInput(
				attrs={'class': 'form-control mb-3 incoming_amount', 'id': 'incoming_amount',
					   'placeholder': 'Введите количество'}),
			'comment': forms.Textarea(
				attrs={'class': 'form-control incoming_comment', 'id': 'incoming_comment', 'rows': 2,
					   'placeholder': 'Комментарий'}),
		}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['material'].queryset = Material.objects.exclude(material_type=2)


class OutgoingForm(forms.ModelForm):
	class Meta:
		model = Outgoing
		fields = ['outgoing_type', 'data', 'warehouse', 'to_warehouse', 'note']
		widgets = {
			'outgoing_type': forms.Select(attrs={'class': 'form-control'}),
			'data': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
			'warehouse': forms.Select(attrs={'class': 'form-control', 'name': 'warehouse'}),
			'to_warehouse': forms.Select(attrs={'class': 'form-control'}),
			'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
		}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['warehouse'].empty_label = 'Из склада'
		self.fields['to_warehouse'].empty_label = 'В склад'


class OutgoingMaterialForm(forms.ModelForm):
	class Meta:
		model = OutgoingMaterial
		fields = ['material', 'amount', 'material_party', 'comment']
		widgets = {
			'material': forms.Select(attrs={'class': 'form-control outgoing_material mb-3', 'id': 'outgoing_material',
											'name': 'outgoing_material'}),
			'amount': forms.NumberInput(
				attrs={'class': 'form-control outgoing_amount mb-3', 'id': 'outgoing_amount',
					   'name': 'outgoing_amount', 'placeholder': 'Введите количеству'}),
			'material_party': forms.TextInput(
				attrs={'class': 'form-control outgoing_material_party mb-3', 'id': 'outgoing_material_party',
					   'name': 'outgoing_material_party'}),
			'comment': forms.Textarea(
				attrs={'class': 'form-control outgoing_comment', 'rows': 2, 'id': 'outgoing_comment',
					   'name': 'outgoing_comment', 'placeholder': 'Примечание'}),
		}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['material'].queryset = Material.objects.exclude(material_type=2)


OutgoingMaterialFormSet = inlineformset_factory(Outgoing, OutgoingMaterial, form=OutgoingMaterialForm, extra=1)
IncomingMaterialFormSet = inlineformset_factory(Incoming, IncomingMaterial, form=IncomingMaterialForm, extra=1)


class MaterialCodeForm(forms.Form):
	material_code = forms.CharField(
		label='Код материала',
		max_length=100,
		widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите код материала'})
	)


class SaleForm(forms.Form):
	quantity = forms.IntegerField(
		label='Количество',
		min_value=1,
		widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Введите количество'})
	)
