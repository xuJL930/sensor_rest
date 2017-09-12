import sensorDemo
from neomodel import config,db
from neomodel import  StructuredNode,StringProperty,Relationship,IntegerProperty,\
                        RelationshipTo,RelationshipFrom,UniqueIdProperty,BooleanProperty

#config.DATABASE_URL = 'bolt://neo4j:123456@localhost:7687'
from neomodel import install_all_labels
from django.forms.models import model_to_dict
#install_all_labels()
import json



class Gateway(StructuredNode):
#    id = IntegerProperty()
    gatewayEui = StringProperty(unique_index=True)
    child  = RelationshipTo('Node','HAS_CHILD')

    def get_eui(self):
        return self.gatewayEui

    def __repr__(self):
        return str(self)

    # def children(self):
    #     results1, meta1 = self.cypher("MATCH (g) where id(g)={self} MATCH (g:Gateway) RETURN g")
    #     gws = [Gateway.inflate(row[0]) for row in results1]
    #     results2, meta2 = self.cypher("MATCH (g) where id(g)={self} MATCH (g)-[:HAS_CHILD]->(b:Node) MATCH (:Node)-[:HAS_CHILD]->(c:Node) RETURN b,c")
    #     nds = [Node.inflate(row[0]) for row in results2]
    #     dt = {}
    #     dt['gateway'] = json.loads(json.dumps(gws[0],cls=GatewayEncoder))
    #     dt['nodes'] = json.loads(json.dumps(nds,cls=NodeEncoder))
    #     return dt

    def del_gateway(self):
#        self.cypher("MATCH (g) where id(g)={self} MATCH (g)-[r:HAS_CHILD]->() DELETE r,g")
        nodes=[]
        children = self.get_children(self,nodes)
        with db.transaction:
            for child in children:
                child.del_node()
            self.cypher("MATCH (g) where id(g)={self} MATCH (g)-[r:HAS_CHILD]->() DELETE r,g")
            return children



    def get_gatewayEui(self):
        return self.gatewayEui

    def children(self):
       nodes =[self,]
       l = self.get_children(self,nodes)
       dt = {}
       dt['gateway'] = json.loads(json.dumps(l[0],cls=GatewayEncoder))
       dt['nodes'] = json.loads(json.dumps(l[1:],cls=NodeEncoder))
       return dt
 #       #results,meta = self.cypher("MATCH (a) where id(a)={self} MATCH (a)-[:HAS_CHILD]->(b:Node) MATCH (:Node)-[:HAS_CHILD]->(c:Node) RETURN b,c")
 #       #return [Node.inflate(row[0]) for row in results]

   # get a gateway all children
    def get_children(self,root,nodes):
        n = root.child.all()
        if len(n):
            for i in n:
                nodes.append(i)
                self.get_children(i,nodes)
        return nodes

#    def to_json(self,list):

class GatewayEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o,Gateway):
            return eval(o.__repr__())
        return json.JSONEncoder.default(self,o)


class Node(StructuredNode):
#    id = IntegerProperty()
    deviceEui = StringProperty(unique_index=True)
    parentEui = StringProperty()
    status  = BooleanProperty(default=True)
    child = RelationshipTo('Node','HAS_CHILD')
    # father = RelationshipTo('Node','HAS_FATHER')
    # father_gw = RelationshipTo('Gateway','HAS_FATHER')

    def get_gateway(self):
        father = self.get_node_father()
        while not isinstance(father, Gateway):
            father = father.get_node_father()
        return father

    def update(self):
        father = self.get_connect_father()
        new_father = self.get_node_father()
        if father is None:
            return None

        if new_father is None:
            return None

        if isinstance(father,Gateway):
            if self.parentEui != father.gatewayEui:
                with db.transaction:
                    self.del_rl()
                    new_father.child.connect(self)
                    return 1
            else: return 0
        if isinstance(father,Node):
            if self.parentEui != father.deviceEui:
                with db.transaction:
                    self.del_rl()
                    new_father.child.connect(self)
                    return 1
            else: return 0

    def get_node_father(self):
         pareui = self.get_parentEui()
         father_gw = Gateway.nodes.get_or_none(gatewayEui=pareui)
         father_nd = Node.nodes.get_or_none(deviceEui=pareui)
         if father_gw is None and father_nd is None:
             return None
         elif father_gw is not None:
             return father_gw
         else:
             return father_nd

    def get_connect_father(self):
        query1= "MATCH (a) where id(a)={self} MATCH (f:Gateway)-[r:HAS_CHILD]->(a) RETURN f"
        query2= "MATCH (a) where id(a)={self} MATCH (f:Node)-[r:HAS_CHILD]->(a) RETURN f"

        results1,meta = self.cypher(query1)
        father_gw = [Gateway.inflate(row[0]) for row in results1]
        if not father_gw:
            results2, meta = self.cypher(query2)
            father_nd = [self.inflate(row[0]) for row in results2]
            if father_nd:
                return father_nd[0]
            else: return None
        return father_gw[0]


    def del_node(self):
        self.cypher(
            "MATCH (a) where id(a)={self} MATCH ()-[r:HAS_CHILD]->(a) DELETE r,a")

    def del_rl(self):
        self.cypher("MATCH (a) where id(a)={self} MATCH ()-[r:HAS_CHILD]->(a) DELETE r")


    def get_json(self):
        return json.loads(json.dumps(self,cls=NodeEncoder))

    def get_parentEui(self):
        return self.parentEui

    def __repr__(self):
        return str(self)

    def children(self):
        nodes = []
        l = self.child.all()
        #return json.dumps(l,cls=NodeEncoder)
        return l

        # results, columns = self.cypher("MATCH (a) WHERE id(a)={self} MATCH (a)-[:HAS_CHILD]->(b:Node) RETURN b")
        # results, columns = self.cypher("MATCH (a)-[:HAS_CHILD]->(b:Node) RETURN b")
        # return [self.inflate(row[0]) for row in results]

class NodeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o,Node):
            return eval(o.__repr__())
        return json.JSONEncoder.default(self,o)