from django import forms

from apps.info.models import MaterialType, Material, Warehouse, Firm, Specification, BoxSize, BoxType, MaterialGroup, \
	MaterialSpecialGroup, Brand
from apps.users.models import CustomUser


class MaterialTypeForm(forms.ModelForm):
	class Meta:
		model = MaterialType
		fields = ['name']
		widgets = {
			'name': forms.TextInput(attrs={'class': 'form-control'}),
		}


class MaterialForm(forms.ModelForm):
	class Meta:
		model = Material
		fields = ['name', 'material_group', 'special_group', 'brand', 'material_thickness',
				  'norm', 'unit_of_measurement', 'photo']
		widgets = {
			'code': forms.TextInput(attrs={'class': 'form-control'}),
			'name': forms.TextInput(attrs={'class': 'form-control'}),
			'material_group': forms.Select(attrs={'class': 'form-control'}),
			'special_group': forms.Select(attrs={'class': 'form-control'}),
			'brand': forms.Select(attrs={'class': 'form-control'}),
			'material_thickness': forms.NumberInput(attrs={'class': 'form-control'}),
			'norm': forms.NumberInput(attrs={'class': 'form-control'}),
			'unit_of_measurement': forms.Select(attrs={'class': 'form-control'}),
			'photo': forms.FileInput(attrs={'class': 'form-control'}),
		}


class WarehouseForm(forms.ModelForm):
	can_import = forms.BooleanField(label='Can Import', required=False,
									widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
	can_export = forms.BooleanField(label='Can Export', required=False,
									widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

	class Meta:
		model = Warehouse
		fields = ['code', 'name', 'location', 'can_import', 'can_export', 'managers']
		widgets = {
			'code': forms.TextInput(attrs={'class': 'form-control'}),
			'name': forms.TextInput(attrs={'class': 'form-control'}),
			'location': forms.TextInput(attrs={'class': 'form-control'}),
			'managers': forms.SelectMultiple(attrs={'class': 'form-select'}),
		}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['managers'].queryset = CustomUser.objects.all()


class FirmForm(forms.ModelForm):
	class Meta:
		model = Firm
		fields = ['name', 'type_firm', 'legal_address', 'actual_address', 'phone_number',
				  'license_number', 'mfo']
		widgets = {
			'name': forms.TextInput(attrs={'class': 'form-control'}),
			'type_firm': forms.Select(attrs={'class': 'form-control'}),
			'legal_address': forms.TextInput(attrs={'class': 'form-control'}),
			'actual_address': forms.TextInput(attrs={'class': 'form-control'}),
			'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
			'license_number': forms.TextInput(attrs={'class': 'form-control'}),
			'mfo': forms.TextInput(attrs={'class': 'form-control'}),
		}


class SpecificationForm(forms.ModelForm):
	class Meta:
		model = Specification
		fields = ['year', 'name', 'firm']
		widgets = {
			'year': forms.TextInput(attrs={'class': 'form-control'}),
			'name': forms.TextInput(attrs={'class': 'form-control'}),
			'firm': forms.Select(attrs={'class': 'form-control'}),

		}


class BoxSizesForm(forms.ModelForm):
	class Meta:
		model = BoxSize
		fields = ['length', 'width', 'height', ]
		widgets = {
			'length': forms.NumberInput(attrs={'class': 'form-control'}),
			'width': forms.NumberInput(attrs={'class': 'form-control'}),
			'height': forms.NumberInput(attrs={'class': 'form-control'}),
		}
		labels = {
			'length': 'Длина (в мм)',
			'width': 'Ширина (в мм)',
			'height': 'Высота (в мм)',
		}


class BoxTypesForm(forms.ModelForm):
	class Meta:
		model = BoxType
		fields = ['name', ]
		widgets = {
			'name': forms.TextInput(attrs={'class': 'form-control'}),
		}


class MaterialGroupForm(forms.ModelForm):
	class Meta:
		model = MaterialGroup
		fields = ['name']
		widgets = {
			'name': forms.TextInput(attrs={'class': 'form-control'}),
		}


class MaterialSpecialGroupForm(forms.ModelForm):
	class Meta:
		model = MaterialSpecialGroup
		fields = ['name']
		widgets = {
			'name': forms.TextInput(attrs={'class': 'form-control'}),
		}


class BrandForm(forms.ModelForm):
	class Meta:
		model = Brand
		fields = ['name']
		widgets = {
			'name': forms.TextInput(attrs={'class': 'form-control'}),
		}
