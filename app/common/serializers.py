from rest_framework import serializers


class BaseModelSerializer(serializers.ModelSerializer):
    def save(self, **kwargs):
        # TODO add ModelService.create
        return super().save(**kwargs)

    def update(self, instance, validated_data):
        # TODO add ModelService.update
        return super().update(instance, validated_data)
