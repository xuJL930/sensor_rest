# Create your tests here.
from django.test import TestCase
from ..neo_models import Gateway,Node,GatewayEncoder,NodeEncoder
from ..models import TerminalMessage
from ..serializers import CheckMessageSerializer
from channels import Group

from neomodel import config,db

from datetime import datetime
import json
config.DATABASE_URL = 'bolt://neo4j:123456@localhost:7687'

class TestCase(TestCase):
    def test_save(self):
        gw = Gateway(gatewayEui='abcde').save()
        gw.refresh()
        print('id= '+str(gw.id))

    def test_find(self):
#        gw = Gateway.nodes.get(gatewayEui="abcd")
        gw = Gateway.nodes.get_or_none(gatewayEui="abcde")
        print(gw)

    def test_relation(self):
        gw = Gateway.nodes.get(gatewayEui="abcde")
        node = Node(deviceEui='3',parentEui='abcde').save()
        gw.child.connect(node)
        if gw.child.is_connected(node):
            print("gw's child is "+str(node))

    def test_relation_node(self):
        fnode = Node.nodes.get(deviceEui="1")
        cnode = Node(deviceEui='4', parentEui='1').save()
        fnode.child.connect(cnode)

    def test_cypher(self):
        results,meta = db.cypher_query("MATCH (a:Gateway)-[:HAS_CHILD]->(b:Node) RETURN b")
        nodes = [Node.inflate(row[0]) for row in results]
        print(nodes)
        #print(json.dumps(nodes))

    def test_batch_node(self):
        s = '{"gatewayEui":"abcde","nodes":[{"deviceEui":"1","parentEui":"abcde"},' \
            r'{"deviceEui":"2","parentEui":"abcde"}]}'

        data = json.loads(s)
        i = data['nodes'][0]
        fnode = Node.nodes.get_or_none(deviceEui=i['parentEui'])
#        cnode = Node(deviceEui=i['deviceEui'],parentEui=i['parentEui']).save()
        with db.transaction:
            cnode = Node.create(i)
            fnode.child.connect(cnode[0])

    def test_model_child(self):
        gw = Gateway.nodes.get(gatewayEui="abcde")
        children = gw.children()
        node = Node.nodes.get(deviceEui='1')
        #children = node.children()
        #children = node.father.all()
        #data = json.dumps(children)
        #print(data)
        print(children)

    def test_form(self):
        gw = Gateway.nodes.get(gatewayEui="abcde")
#        nd = Node.nodes.get(deviceEui='1')
        lg = gw.children()
        lg1 = lg
        print(type(lg1))
        print(lg1)
     #   print(ln)

    def test_gw(self):
        results1, meta1 = db.cypher_query("MATCH (g) where g.gatewayEui='abcde' MATCH (g:Gateway) RETURN g")
        gws = [Gateway.inflate(row[0]) for row in results1]
        results2, meta2 = db.cypher_query(
            "MATCH (g) where g.gatewayEui='abcde' MATCH (g) -[r:HAS_CHILD]->(b:Node) MATCH (:Node)-[:HAS_CHILD]->(c:Node) RETURN distinct b,c")
        nds = [Node.inflate(row[0]) for row in results2]
        #nds.append([Node.inflate(row[1]) for row in results2])
        print(gws)
        print(nds)

    def test_node(self):
        node = Node.nodes.get_or_none(deviceEui='1')
        node2 = Node(deviceEui='8', parentEui='hijkl', status=False)
        print(node2)

    def test_delete(self):
        gw = Gateway.nodes.get_or_none(gatewayEui='hijkl')
        children = gw.del_gateway()
        print(children)

    def test_update(self):
        node = Node.nodes.get(deviceEui='5')
        f = node.update()
        print(f)

    def test_get_gateway(self):
        node = Node.nodes.get_or_none(deviceEui='7')
        if node is not None:
            father = node.get_gateway()
            print(father)
        else:
            print(node)

    def test_time(self):
        now = datetime.now().timestamp()
        now1 = datetime.timestamp(datetime.now())
        print(now)
        print(now1)

    def test_check_msg(self):
        try:
            message = TerminalMessage.objects.filter(gatewayEui='abcde',status='Pending').order_by('createAt')
            print(message)
        except TerminalMessage.DoesNotExist:
            print("no message to solve!")
            return
        serializer = CheckMessageSerializer(message, many=True)
        print(serializer.data)
        status = serializer.data[0].get('status')
        print(status)
        if status == 'Ok':
            return
        else:
            for msg in serializer.data.reverse():
               print(msg)
               #Group('gateway-abcde').send('text', msg)