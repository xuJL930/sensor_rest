# -*- coding:utf8 -*-
#from channels.generic.websockets import WebsocketDemultiplexer, JsonWebsocketConsumer
#from .models import TerminalBinding

from channels import Group
from channels.sessions import channel_session
from channels.generic.websockets import JsonWebsocketConsumer
from .models import Terminal, TerminalMessage
from .serializers import TerminalSerializer, TerminalMessageSerializer
from .neo_models import Gateway
# from .global_val import gl_gateways, gl_duplicate
from .tasks import check_terminal_message

class GatewayConsumer(JsonWebsocketConsumer):
    # channel_session = True

    # def connection_groups(self, **kwargs):
    #     label = kwargs.get('gatewayEui')
    #     return ["gateway-{0}".format(label)]

    def connect(self, message, **kwargs):
        # print(message['path'])
        label = kwargs.get('gatewayEui')
        if label is None:
            print('invalid ws path=%s', message['path'])
            self.message.reply_channel.send({"accept": False})
            return
        else:
            gw = Gateway.nodes.get_or_none(gatewayEui=label)
            if gw is not None:
                self.message.reply_channel.send({"accept": True})
            else:
                # self.message.reply_channel.send({"accept": False})
                self.message.reply_channel.send({"close": True})
                return

        # self.groups.append("gateway-{0}".format(label))
        Group("gateway-{0}".format(label)).add(message.reply_channel)
        print(label+' === accepted')
        # message.channel_session['gw'] = label

        # check is there any message not
        # solved when gateway offline
        check_terminal_message.delay(label)

    def receive(self, content, **kwargs):
        payload = content['text']
        print(content)
        if payload is None:
            return
        try:
            termMsg = TerminalMessage.objects.get(deviceEui=payload['deviceEui'], createAt=payload['createAt'])
            terminal = Terminal.objects.get(deviceEui=payload['deviceEui'])
        except TerminalMessage.DoesNotExist:
            print("no such TerminalMessage")
            return
        except Terminal.DoesNotExist:
            print("no such Terminal")
            return

        data = {
            'led': payload['led']
        }

        serializer = TerminalSerializer(terminal, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            print('terminal led saved ok')
            serializerMsg = TerminalMessageSerializer(termMsg, data={'status': 'Ok'}, partial=True)
            if serializerMsg.is_valid():
                serializerMsg.save()
                print('terminal message pending => ok')
            else:
                print(serializerMsg.errors)
        else:
            print(serializer.errors)


    def disconnect(self, message, **kwargs):
        label = kwargs.get('gatewayEui')
        if label is not None:
            print(kwargs['gatewayEui']+" === closed")
            Group('gateway-'+kwargs['gatewayEui']).discard(message.reply_channel)
            # self.groups.remove('gateway-'+kwargs['gatewayEui'])
            self.message.reply_channel.send({"close": True})
        # if kwargs['gatewayEui'] in gl_gateways and not gl_duplicate:
        #     gl_gateways.remove(kwargs['gatewayEui'])




