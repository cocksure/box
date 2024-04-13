from django import forms

from apps.info.models import MaterialType, Material, Warehouse, Firm, Specification, BoxSize, BoxType
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
		fields = ['code', 'name', 'material_type', 'material_thickness']
		widgets = {
			'code': forms.TextInput(attrs={'class': 'form-control'}),
			'name': forms.TextInput(attrs={'class': 'form-control'}),
			'material_type': forms.Select(attrs={'class': 'form-control'}),
			'material_thickness': forms.TextInput(attrs={'class': 'form-control'}),
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
		fields = ['code', 'name', 'legal_address', 'actual_address', 'phone_number', 'license_number']
		widgets = {
			'code': forms.TextInput(attrs={'class': 'form-control'}),
			'name': forms.TextInput(attrs={'class': 'form-control'}),
			'legal_address': forms.TextInput(attrs={'class': 'form-control'}),
			'actual_address': forms.TextInput(attrs={'class': 'form-control'}),
			'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
			'license_number': forms.TextInput(attrs={'class': 'form-control'}),
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
		fields = ['name', ]
		widgets = {
			'name': forms.TextInput(attrs={'class': 'form-control'}),
		}


class BoxTypesForm(forms.ModelForm):
	class Meta:
		model = BoxType
		fields = ['name', ]
		widgets = {
			'name': forms.TextInput(attrs={'class': 'form-control'}),
		}
