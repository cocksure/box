from rest_framework import serializers
from apps.production.models import Process, BoxModel, BoxOrder, BoxOrderDetail, ProductionOrder, UploadImage


class ProcessSerializer(serializers.ModelSerializer):
	class Meta:
		model = Process
		fields = '__all__'


class UploadImageSerializer(serializers.ModelSerializer):
	class Meta:
		model = UploadImage
		fields = ('id', 'photo')


class BoxModelSerializer(serializers.ModelSerializer):
	material_name = serializers.CharField(source='material.name', read_only=True)
	type_of_work_names = serializers.SerializerMethodField()
	box_size_name = serializers.CharField(source='box_size.name', read_only=True)
	box_type_name = serializers.CharField(source='box_type.name', read_only=True)
	image_url = serializers.SerializerMethodField()

	class Meta:
		model = BoxModel
		fields = (
			'id', 'name', 'material', 'material_name', 'type_of_work', 'type_of_work_names', 'box_size', 'box_size_name',
			'box_type', 'box_type_name', 'photos', 'image_url')

	def get_type_of_work_names(self, obj):
		return [process.name for process in obj.type_of_work.all()] if obj.type_of_work.exists() else []

	def get_image_url(self, obj):
		if obj.photos and obj.photos.photo:
			return obj.photos.photo.url
		return None


class BoxOrderDetailSerializer(serializers.ModelSerializer):
	class Meta:
		model = BoxOrderDetail
		fields = ['box_model', 'amount']


class BoxOrderSerializer(serializers.ModelSerializer):
	order_detail = BoxOrderDetailSerializer(many=True, source='boxorderdetail_set')

	class Meta:
		model = BoxOrder
		fields = ['data', 'customer', 'status', 'type_order', 'specification', 'manager',
				  'date_of_production', 'order_detail']

	def create(self, validated_data):
		order_detail_data = validated_data.pop('boxorderdetail_set')
		box_order = BoxOrder.objects.create(**validated_data)
		for detail_data in order_detail_data:
			BoxOrderDetail.objects.create(box_order=box_order, **detail_data)
		return box_order


class ProductionOrderSerializer(serializers.ModelSerializer):
	box_order_detail = BoxOrderDetailSerializer()

	type_of_work = serializers.SerializerMethodField()
	material_thickness = serializers.SerializerMethodField()

	class Meta:
		model = ProductionOrder
		fields = ['box_order_detail', 'shipping_date', 'amount', 'material_thickness', 'type_of_work', ]

	def get_type_of_work(self, obj):
		box_model = obj.box_order_detail.box_model if obj.box_order_detail else None
		type_of_work = box_model.type_of_work.all() if box_model else []
		return [process.name for process in type_of_work]

	def get_material_thickness(self, obj):
		box_model = obj.box_order_detail.box_model if obj.box_order_detail else None
		material_thickness = box_model.material.material_thickness if box_model and box_model.material else None
		return material_thickness
