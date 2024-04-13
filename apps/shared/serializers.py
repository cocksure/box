from rest_framework import serializers


class BaseNameCodeSerializer(serializers.ModelSerializer):
    class Meta:
        abstract = True

    def validate(self, data):
        code = data.get('code')
        name = data.get('name')

        if code and name and code == name:
            raise serializers.ValidationError('Код и имя не должны быть одинаковыми.')

        if name.isnumeric():
            raise serializers.ValidationError("Имя не должно содержать только цифры.")

        return data
