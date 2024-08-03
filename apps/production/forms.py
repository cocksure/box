from django.forms import inlineformset_factory
from django import forms
from apps.info.models import Material, BoxSize, BoxType, Firm
from apps.production.models import BoxModel, ProductionOrder, Process
from .models import BoxOrder, BoxOrderDetail


class BoxModelForm(forms.ModelForm):
	class Meta:
		model = BoxModel
		fields = [
			'name', 'material', 'additional_materials', 'box_size', 'box_type', 'closure_type',
			'additional_properties', 'max_load', 'color', 'grams_per_box', 'format', 'comment', 'photo', 'layers'
		]
		labels = {
			'name': '',
			'closure_type': 'Тип замыкания',
			'additional_properties': 'Дополнительные свойства',
			'max_load': 'Максимальная нагрузка',
			'color': 'Цвет',
			'comment': 'Комментарий',
		}
		widgets = {
			'name': forms.TextInput(attrs={'class': 'form-control mt-3 mb-2', 'placeholder': 'Введите название'}),
			'material': forms.Select(attrs={'class': 'form-select mb-3', 'placeholder': 'Выберите материал'}),
			'box_size': forms.Select(attrs={'class': 'form-select mb-2', 'placeholder': 'Выберите размер'}),
			'box_type': forms.Select(attrs={'class': 'form-select mb-3', 'placeholder': 'Выберите тип коробки'}),
			'color': forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Введите цвет'}),
			'closure_type': forms.Select(attrs={'class': 'form-select mb-2'}),
			'format': forms.Select(attrs={'class': 'form-select mb-2'}),
			'layers': forms.Select(attrs={'class': 'form-select mb-2'}),
			'additional_properties': forms.Select(attrs={'class': 'form-control mb-2'}),

			'max_load': forms.NumberInput(
				attrs={'class': 'form-control mb-3', 'placeholder': 'Введите максимальную нагрузку'}),
			'grams_per_box': forms.NumberInput(
				attrs={'class': 'form-control mb-3', 'placeholder': 'Грамм на одну коробку'}),
			'additional_materials': forms.SelectMultiple(attrs={'class': 'form-control mb-3 custom-select'}),
			'comment': forms.Textarea(
				attrs={'class': 'form-control mb-2', 'rows': 3, 'placeholder': 'Введите комментарий'}),
			'photo': forms.ClearableFileInput(attrs={'class': 'form-control mb-3', 'id': 'photo', 'name': 'photo'}),
		}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['material'].queryset = Material.objects.exclude(material_type=2)  # Готовый продукт
		self.fields['additional_materials'].queryset = Material.objects.exclude(
			material_group=4)  # Группа материала сырьё
		self.fields['box_size'].queryset = BoxSize.objects.all()
		self.fields['box_type'].queryset = BoxType.objects.all()


class BoxOrderForm(forms.ModelForm):
	class Meta:
		model = BoxOrder
		fields = ['customer', 'buyer', 'type_order', 'specification', 'date_of_production']
		widgets = {
			'customer': forms.Select(attrs={'class': 'form-control'}),
			'buyer': forms.Select(attrs={'class': 'form-control'}),
			'type_order': forms.Select(attrs={'class': 'form-control'}),
			'specification': forms.Select(attrs={'class': 'form-control'}),
			'date_of_production': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
		}

	def __init__(self, *args, **kwargs):
		super(BoxOrderForm, self).__init__(*args, **kwargs)
		self.fields['buyer'].queryset = Firm.objects.all()
		self.fields['customer'].queryset = Firm.objects.all()


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


class ProductionOrderForm(forms.ModelForm):
	class Meta:
		model = ProductionOrder
		fields = ['shipping_date', 'type_of_work']
		widgets = {
			'shipping_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', }),
			'type_of_work': forms.Select(attrs={'class': 'form-select'}),
		}


class ProcessLogForm(forms.Form):
	production_order_code = forms.CharField(
		max_length=20,
		label='Код заказа на производство',
		widget=forms.TextInput(attrs={'class': 'form-control'})
	)


class ProductionOrderCodeForm(forms.Form):
	production_order_code = forms.CharField(
		label='Код или ID заказа на производство',
		max_length=20,
		widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите код или ID заказа'})
	)


class PackagingAmountForm(forms.Form):
	packed_amount = forms.DecimalField(
		label='Количество упаковано',
		max_digits=10,
		decimal_places=2,
		widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Введите количество'})
	)


class ProcessLogFilterForm(forms.Form):
	process = forms.ModelChoiceField(queryset=Process.objects.all(), required=False, label='Процесс',
									 widget=forms.Select(attrs={'class': 'form-select'}))
	status = forms.ChoiceField(choices=[('all', 'Все')] + ProductionOrder.ProductionOrderStatus.choices, required=False,
							   label='Статус', widget=forms.Select(attrs={'class': 'form-select'}))
	start_date = forms.DateField(required=False, label='Начало',
								 widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
	end_date = forms.DateField(required=False, label='Окончания',
							   widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
