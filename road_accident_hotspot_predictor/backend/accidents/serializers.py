from rest_framework import serializers
from .models import Accident, Hotspot

class AccidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accident
        fields = "__all__"

class HotspotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotspot
        fields = "__all__"
