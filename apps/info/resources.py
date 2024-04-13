from import_export import resources

from apps.info import models


class MaterialResource(resources.ModelResource):
    class Meta:
        model = models.Material
        fields = ('id', 'code', 'name', 'material_type', 'material_thickness')