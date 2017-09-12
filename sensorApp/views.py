from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render
from .models import Terminal, User, Report
from .neo_models import Gateway, Node
from .serializers import TerminalSerializer, ReportSerializer, UserSerializer, TerminalMessageSerializer
from neomodel import db
import json
from datetime import datetime
# from neo4jrestclient.client import GraphDatabase, Node

# gdb = GraphDatabase("http://localhost:7474", username="neo4j", password="123456")
@api_view(['GET'])
def index(request, pk):
    """
    Root page view. Just shows a list of values currently available.
    """
    gw = Gateway.nodes.get_or_none(gatewayEui=pk)
    # try:
    #     if gw is None:
    #         raise ValueError
    # except ValueError:
    #     return Response({'no such gateway': pk}, status=status.HTTP_404_NOT_FOUND)

    return render(request, "client.html")


@api_view(['PATCH'])
def patch_led(request, pk):
    try:
        dev = Terminal.objects.get(pk=pk)
    except Terminal.DoesNotExist:
        return Response("not found", status=status.HTTP_404_NOT_FOUND)

    stamp = datetime.now().timestamp()
    now = int(round(stamp*1000))

    dev.set_led(request.data.get('led'))
    result = Terminal.send_update_led(dev, now)

    if result is not None:
        print('send ws message ok')
    else:
        print('send message failed, None device or gateway!')

    message = {
        'gatewayEui': result,
        'deviceEui': dev.deviceEui,
        'led': dev.led,
        'createAt': now,
    }

    serializer = TerminalMessageSerializer(data=message)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        print("error message format")
        return Response("error message format", status=status.HTTP_400_BAD_REQUEST)

    # data = {
    #     # "deviceEui": dev.deviceEui,
    #     # "status": dev.status,
    #     "led": request.data.get('led'),
    #     # "battery": dev.battery,
    #     # "longitude": dev.longitude,
    #     # "latitude": dev.latitude,
    #     # "userId": dev.userId,
    #
    #
    # }
    # serializer = TerminalSerializer(dev, data=data, partial=True)
    # if serializer.is_valid():
    #     serializer.save()
    #     return Response(serializer.data, status=status.HTTP_200_OK)
    # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET', 'POST'])
def get_post_terminal(request):
    # get all terminal
    if request.method == 'GET':
        terminals = Terminal.objects.all()

        flag = False
        qd = request.GET
        qd_len =len(qd.dict())
        if qd_len !=0:
            if 'deviceEui' in qd and qd_len == 1:
                deveui = qd.get('deviceEui', None)
                if deveui is not None:
                    terminals = terminals.filter(deviceEui=deveui)
                    flag = True
            elif 'terminalId' in qd and qd_len == 1:
                devaddr = qd.get('terminalId', None)
                if devaddr is not None:
                    terminals = terminals.filter(terminalId=devaddr)
                    flag = True
            else:
                return Response({'error in param': qd.dict()}, status=status.HTTP_400_BAD_REQUEST)

        serializer = TerminalSerializer(terminals, many=True)

        if not terminals.count() and flag == True:
            return Response(terminals.all(), status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.data)

    if request.method == 'POST':
        data = {
            'deviceEui': request.data.get('deviceEui'),
            'battery': int(request.data.get('battery')),
            'longitude': request.data.get('longitude'),
            'latitude': request.data.get('latitude'),
            'userId': request.data.get('userId')
        }
        serializer = TerminalSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH'])
def get_patch_single_terminal(request, pk):
    try:
        terminal = Terminal.objects.get(pk=pk)
    except Terminal.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = TerminalSerializer(terminal)
        return Response(serializer.data)

    if request.method == 'PATCH':
        serializer = TerminalSerializer(terminal, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
def get_post_report(request):
    if request.method == 'GET':
        reports = Report.objects.all().order_by('-reportAt')
        serializer = ReportSerializer(reports, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == 'POST':
        data = {
            'deviceEui': request.data.get('deviceEui'),
            'reportAt': request.data.get('reportAt'),
            'model': request.data.get('model'),
            'seqno': request.data.get('seqno'),
            'rsrp': request.data.get('rsrp'),
            'sinr': request.data.get('sinr'),
            'temper': request.data.get('temper'),
            'damp': request.data.get('damp'),
            'light': request.data.get('light'),
            'pressure': request.data.get('pressure'),
            'buttery': request.data.get('buttery'),
            'led': request.data.get('led'),
            'longitude': request.data.get('longitude'),
            'latitude': request.data.get('latitude')
        }
        serializer = ReportSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_single_report(request, pk):
    try:
        report = Report.objects.get(pk=pk)
    except Report.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ReportSerializer(report)
        return Response(serializer.data)


@api_view(['GET', 'POST'])
def get_post_user(request):
    if request.method == 'GET':
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        data = {
            'userId': request.data.get('userId'),
            'password': request.data.get('password'),
            'displayName': request.data.get('displayName'),
            'email': request.data.get('email'),
            'mobile': request.data.get('mobile'),
            'role': request.data.get('role')
        }
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH'])
def get_patch_single_user(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)

    if request.method == 'PATCH':
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# transform json data to python object
def json2data(json_str):
    return json.loads(json.dumps(json_str))

# get the nodes link, flag to switch nodes kind
def get_root_nodes(data, flag):
    nodes = []
    for node in data["nodes"]:
        if flag:
            if node["parentEui"] == data["gatewayEui"]:
                nodes.append(node)
        else:
            if node["parentEui"] != data["gatewayEui"]:
                nodes.append(node)
    return nodes

# check the data
def validate_gateway(request):
    gw = request.data.get('gatewayEui')
    nodes = request.data.get('nodes')
    if (gw and nodes) is None:
        return 0
    for i in nodes:
        if (i.get('deviceEui') and i.get('parentEui')) is None:
            return 0
    return 1


"""
# views for neo4j
# get and post gateway info include all nodes
"""


@api_view(['GET', 'POST'])
def get_post_gateway(request):
    if request.method == 'GET':
        results, meta = db.cypher_query("MATCH (g:Gateway) return g")
        arrgw = [Gateway.inflate(row[0]) for row in results]
        gws = []
        for i in arrgw:
            gws.append(i.children())
        return Response(gws, status=status.HTTP_200_OK)

    if request.method == 'POST':
        if not validate_gateway(request):
            return Response("error parameters, check variables!", status=status.HTTP_400_BAD_REQUEST)
        data = json2data(request.data)
        gweui = request.data.get('gatewayEui')
        root_nodes = get_root_nodes(data, True)
        nodes = get_root_nodes(data, False)

        if gweui is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        gw = Gateway.nodes.get_or_none(gatewayEui=gweui)
        if gw is not None:
            return Response({gweui: 'has already exists!'}, status=status.HTTP_400_BAD_REQUEST)

        gw = Gateway.create_or_update({'gatewayEui': gweui}, )[0]
        for i in root_nodes+nodes:
            nd = Node.create_or_update(i)[0]
            flag = nd.update()
            if flag is None:
                return Response({'no such parent': nd.get_parentEui()}, status=status.HTTP_400_BAD_REQUEST)

        # with db.transaction:
        #     if gw is None:
        #         gw = Gateway(gatewayEui=gweui).save()
        #
        #     for node in root_nodes:
        #         n = Node(deviceEui=node["deviceEui"],parentEui=node["parentEui"]).save()
        #         gw.child.connect(n)
        #     for node in nodes:
        #         # get a gateway total info
        #         fnode = Node.nodes.get_or_none(deviceEui=node['parentEui'])
        #         cnode = Node(deviceEui=node["deviceEui"],parentEui=node["parentEui"]).save()
        #         fnode.child.connect(cnode)

        return Response(gw.children(), status=status.HTTP_200_OK)

"""
 get single gateway/{gatewayEui}
"""


@api_view(['GET'])
def get_single_gateway(request, pk):

    gw = Gateway.nodes.get_or_none(gatewayEui=pk)
    if gw is None:
        return Response(status=status.HTTP_404_NOT_FOUND)
    return Response(gw.children(), status=status.HTTP_200_OK)

# reset gateway info  /reset
@api_view(['POST'])
def reset_gateway(request):
    if not validate_gateway(request):
        return Response("error parameters, check variables!", status=status.HTTP_400_BAD_REQUEST)

    data = json2data(request.data)
    gweui = request.data.get('gatewayEui')  # data["gatewayEui"]
    root_nodes = get_root_nodes(data, True)
    nodes = get_root_nodes(data, False)

    gw = Gateway.nodes.get_or_none(gatewayEui=gweui)
    if gw is None:
        return Response({'no such gateway': gw}, status=status.HTTP_404_NOT_FOUND)

    for i in root_nodes+nodes:
        nd = Node.create_or_update(i)[0]
        flag = nd.update()
        if flag is None:
            return Response({'no such parent': nd.get_parentEui()}, status=status.HTTP_400_BAD_REQUEST)
    # with db.transaction:
    #     gw.del_gateway()
    #     if gw is None:
    #         gw = Gateway(gatewayEui=gweui).save()
    #
    #     for node in root_nodes:
    #         #n =
    #         n = Node(deviceEui=node["deviceEui"], parentEui=node["parentEui"],status=node[status]).save()
    #         gw.child.connect(n)
    #     for node in nodes:
    #         # get a gateway total info
    #         fnode = Node.nodes.get_or_none(deviceEui=node['parentEui'])
    #         cnode = Node(deviceEui=node["deviceEui"], parentEui=node["parentEui"]).save()
    #         fnode.child.connect(cnode)
    return Response(gw.children(), status=status.HTTP_200_OK)

# post a node /node
@api_view(['POST'])
def post_node(request, pk):
    deveui = request.data.get('deviceEui')
    pareui = request.data.get('parentEui')
    stat = request.data.get('status')

    if (deveui and pareui) is None:
        return Response("error parameters! please check variables", status=status.HTTP_400_BAD_REQUEST)

    node = Node(deviceEui=deveui, parentEui=pareui, status=stat)
    onode = Node.nodes.get_or_none(deviceEui=deveui)
    if onode is None:
        with db.transaction:
            node.save()
    else:
        return Response({deveui: 'has already exists!'}, status=status.HTTP_400_BAD_REQUEST)

    if pareui == pk:
        gw = Gateway.nodes.get_or_none(gatewayEui=pk)
        with db.transaction:
            gw.child.connect(node)
            return Response(node.get_json(), status=status.HTTP_200_OK)
    else:
        fnode = Node.nodes.get_or_none(deviceEui=pareui)
        if fnode is None:
            return Response({'no such father node': deveui}, status=status.HTTP_404_NOT_FOUND)
        else:
            with db.transaction:
                fnode.child.connect(node)
                return Response(node.get_json(), status=status.HTTP_200_OK)


# operate with single node/{deviceEui}
@api_view(['GET', 'PATCH'])
def get_patch_node(request, pk1, pk2):
    gw = Gateway.nodes.get_or_none(gatewayEui=pk1)
    node = Node.nodes.get_or_none(deviceEui=pk2)

    if gw is None:
        return Response({'no such gateway': pk1}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
#        node = db.cypher_query("MATCH (n:Node) where n.id={pk2} RETURN n")
        if node is not None:
            return Response(node.get_json(), status=status.HTTP_200_OK)
        else:
            return Response({'no such Node': pk2}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PATCH':
        if node is None:
            return Response({'no such Node': pk2}, status=status.HTTP_404_NOT_FOUND)
        pareui = request.data.get('parentEui')
        stat = request.data.get('status')

#        old_pareui = node.get_parentEui()
        if Node.nodes.get_or_none(deviceEui=pareui) is None and Gateway.nodes.get_or_none(gatewayEui=pareui) is None:
            return Response({'no such parentEui': pareui}, status=status.HTTP_404_NOT_FOUND)
        # new = Node(deviceEui=pk2,parentEui=pareui,status=stat)

        new_node = Node.create_or_update({'deviceEui': pk2, 'parentEui': pareui, 'status': stat})[0]
        flag = new_node.update()
        if flag is None:
            return Response({'no parentEui': pareui}, status=status.HTTP_400_BAD_REQUEST)
        # if flag ==0:

        # if old_pareui != pareui:
        #     father = new_node.get_parent()
        #     if father is not None:# or
        # pareui != (father.get_gatewayEui if isinstance(father,Gateway) else father.get_parentEui):
        #         with db.transaction:
        #             new_node.del_rl()
        #             father.child.connect(new_node)
        #     else:
        #         return Response({"patched node has no father!"},status=status.HTTP_200_OK)

        return Response(new_node.get_json(), status=status.HTTP_200_OK)
