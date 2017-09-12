# -*- coding:utf8 -*-
from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import Terminal, Report, User, TerminalMessage
# from django.forms import ModelForm
# from .neo_models import Gateway,Node
# from neomodel import IntegerProperty

class TerminalSerializer(serializers.ModelSerializer):

    terminalId = serializers.PrimaryKeyRelatedField(read_only=True, pk_field=serializers.UUIDField(format='hex'))
    deviceEui = serializers.CharField(max_length=20, allow_null= False, validators=[UniqueValidator(queryset=Terminal.objects.all())])
    #userId = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Terminal
#        fields = ('deviceEui','battery','longitude','latitude','userId')
        fields = '__all__'

    def validated_userid(self, userid):
        try:
            data = User.objects.get(userId=userid)
        except User.DoesNotExist:
            raise ValidationError(userid+'not exist!')
        return data


class ReportSerializer(serializers.ModelSerializer):

    reportId = serializers.PrimaryKeyRelatedField(read_only=True, pk_field=serializers.UUIDField(format='hex'))

    class Meta:
        model = Report
        fields = '__all__'
    #    ordering = ('reportAt')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('password',)


class TerminalMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TerminalMessage
        fields = '__all__'

class CheckMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TerminalMessage
        fields = ('deviceEui', 'led', 'createAt', 'status')
# class GatewayForm(serializers.ModelSerializer):
#     deviceEui = serializers.ListField(style=serializers.CharField(max_length=30))
#     class Meta:
#         model = Gateway
#         fields = ['id','gatewayEui']

#
# class NodeForm(ModelForm):
#     id = IntegerProperty()
#     class Meta:
#         model = Node
#         fields = ['deviceEui','parentEui','status']
