# -*- coding:utf8 -*-
from channels import route_class, route
from sensorApp.consumers import GatewayConsumer

channel_routing = [
    # route_class(GatewayConsumer, path="^/gateway/$"),
    route_class(GatewayConsumer, path="^/gateway/(?P<gatewayEui>\w+)/$"),
]