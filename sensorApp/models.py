# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models
from channels import Group
from .neo_models import Gateway, Node
import uuid
import json


class Report(models.Model):
    reportId = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    deviceEui = models.ForeignKey('Terminal',models.DO_NOTHING,to_field='deviceEui',db_column='deviceEui',null=True)
    reportAt = models.IntegerField(blank=True,null=True)
    model = models.CharField(max_length=5, blank=True, null=True)
    seqno = models.IntegerField(blank=True, null=True)
    rsrp = models.FloatField(blank=True, null=True)
    sinr = models.FloatField(blank=True, null=True)
    temper = models.FloatField(blank=True, null=True)
    damp = models.FloatField(blank=True, null=True)
    light = models.FloatField(blank=True, null=True)
    pressure = models.FloatField(blank=True, null=True)
    buttery = models.IntegerField(blank=True, null=True)
    led = models.CharField(max_length=5, blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = 'report'


class Terminal(models.Model):
    terminalId = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    deviceEui = models.CharField(max_length=20,unique=True,db_index=True)
    status = models.BooleanField(default=True)
    led = models.CharField(max_length=5, blank=True, null=True)
    battery = models.IntegerField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    userId = models.ForeignKey('User', models.DO_NOTHING)

    class Meta:
        db_table = 'terminal'

    def set_led(self, led):
        self.led = led

    @staticmethod
    def send_update_led(terminal, time):
        print(terminal.deviceEui)
        node = Node.nodes.get_or_none(deviceEui=terminal.deviceEui)
        print(node)
        if node is not None:
            gateway = node.get_gateway()
            if gateway is not None:
                data = {
                    'deviceEui': terminal.deviceEui,
                    'led': terminal.led,
                    'createAt': time
                }
                print('gateway-{0}'.format(gateway.gatewayEui))
                Group('gateway-{0}'.format(gateway.gatewayEui)).send({'text': json.dumps(data)})
                return gateway.gatewayEui
            else:
                return None
        else:
            return None


class TerminalMessage(models.Model):
    STATUS = (
        ('Pending', 'Pending'),
        ('Ok', 'Ok')
    )
    gatewayEui = models.CharField(max_length=20)
    deviceEui = models.CharField(max_length=20)
    led = models.CharField(max_length=5)
    createAt = models.BigIntegerField()
    status = models.CharField(choices=STATUS, max_length=10, default='Pending')

    class Meta:
        db_table = 'terminal_message'
        unique_together = ('deviceEui', 'createAt')

    @classmethod
    def get_status(self):
        return self.status
# class TerminalBinding(WebsocketBinding):
#     model = Terminal
#     stream = "devLed"
#     fields = ["deviceEui", "led"]
#
#     @classmethod
#     def group_names(cls, instance):
#         return ["devLed-updates"]
#
#     def has_permission(self, user, action, pk):
#         return True


class User(models.Model):
    userId = models.CharField(primary_key=True, max_length=20)
    password = models.CharField(max_length=100)
    displayName = models.CharField(max_length=45, blank=True, null=True)
    email = models.CharField(max_length=40, blank=True, null=True)
    mobile = models.CharField(max_length=11, blank=True, null=True)
    role = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        db_table = 'user'
