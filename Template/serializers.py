from rest_framework import serializers
from Template.models import Template

class TemplateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Template
        fields = '__all__'
