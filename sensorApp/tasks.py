# -*- coding:utf8 -*-
from __future__ import absolute_import
#from celery import shared_task
from celery.task import task, periodic_task
from channels import Group
from .models import TerminalMessage
from .serializers import TerminalMessageSerializer, CheckMessageSerializer
import json

@task
def check_terminal_message(gateway):
    try:
        print(gateway)
        message = TerminalMessage.objects.filter(gatewayEui=gateway).latest('createAt')# order_by('-createAt')[:1]
    except TerminalMessage.DoesNotExist:
        print("no message to solve!")
        return
    ser = CheckMessageSerializer(message)
    if ser.data.get('status') == 'Ok':
        print("the latest message has solved!")
        return
    else:
        message = TerminalMessage.objects.filter(gatewayEui=gateway, status='Pending').order_by('-createAt')[:5]
        # message = message.reverse()
        serializer = CheckMessageSerializer(message, many=True)
        # msglist = list(serializer.data)
        # msglist.reverse()
        for msg in serializer.data:
            print(dict(msg))
            Group('gateway-{0}'.format(gateway)).send({'text': json.dumps(dict(msg))})


