from py2neo import Graph
import pandas as pd 

class App:
    def __init__(self, uri : str, username : str, password : str, verbose : bool = False, ):
        self.driver   = Graph(uri, auth = (username, password))
        self.verbose  = verbose 
        
        if self.verbose:
            print('Started the neo4j driver ...')
        
    def prop_dict_to_str(self, properties : dict):
        prop_list = [f"{k}: '{v}'" for k,v in properties.items()]
        prop_str  = '{' + ', '.join(prop_list) + '}'
        return prop_str

    def create_node(self, label : str, properties : dict):
        ## query syntax :==> CREATE (n:label {properties})
        properties = self.prop_dict_to_str(properties)
        query = f"CREATE (n:{label} {properties})"
        node  = self.driver.query(query)
        
    def create_relationship(self, label : list, reltype : str, node1_name : str = None, node2_name : str = None, where_cond : bool = True):
        ## query syntax :==> MATCH (n1:label[0]), (n2:label[1]) WHERE n1.name = name AND n2.name = name CREATE (n1)-[r:reltype]->(n2)
        if where_cond:
            assert node1_name is not None, "node1_name value is none"
            assert node2_name is not None, "node2_name value is none"
            
            query = f"MATCH (a:{label[0]}), (b:{label[1]}) WHERE a.name = '{node1_name}' AND b.name = '{node2_name}' CREATE (a)-[r:{reltype}]->(b)"
        else:
            query = f"MATCH (a:{label[0]}), (b:{label[1]}) CREATE (a)-[r:{reltype}]->(b)"
            
        rel = self.driver.query(query)
        
    def delete_node(self, label : str, name : str):
        ## query syntax :==> MATCH (n:label {name : name}) DELETE n
        query = f"MATCH (n:{label} {{name : '{name}'}}) DELETE n"
        node  = self.driver.query(query)
        
    def delete_relationship(self, label : list, reltype : str):
        ## query syntax :==> MATCH (a)-[r:reltype]->(b) DELETE r
        query = f"MATCH (a:{label[0]})-[r:{reltype}]->(b:{label[1]}) DELETE r"
        rel   = self.driver.query(query)
        
    def empty_graph(self):
        ## query syntax :==> MATCH (n) DETACH DELETE n
        query = 'MATCH (n) DETACH DELETE n'
        self.driver.query(query)
        print('Deleted all nodes and relationships ...')
        return 
        
    def find_return_node(self, label : str, name : str = None):
        ## query syntax :==> MATCH (n:label {name : 'name'}) RETURN n
        if name:
            query = f"MATCH (n:{label} {{name: '{name}'}}) RETURN *"
        else:
            query = f"MATCH (n:{label}) RETURN *"
            
        nodes = self.driver.query(query).to_data_frame()
        return nodes
    
    def custom_query(self, query):
        return self.driver.query(query).to_data_frame()
    
    @staticmethod
    def merge_relations(relations):
        ## Start, End, Relationship
        rl = {}
        for _, rdf in relations.iterrows():
            d = list(map(str, sorted([rdf['st'], rdf['ed']])))
            m = '_'.join(d)

            if m in rl.keys():
                rl[m].append(rdf['r'])
            else:
                rl[m] = [rdf['r']]

        return pd.DataFrame(pd.Series(list(rl.values())), columns = ['Relations'])
    
    def return_nodes_relations(self):
        ## query syntax :==> MATCH (n) RETURN *
        query     = 'MATCH (a)-[r]-(b) RETURN ID(startNode(r)) as Start_id, ID(endNode(r)) as End_id, properties(startNode(r)).name as Start_node, properties(endNode(r)).name as End_node, type(r) as Relation'
        relations = self.driver.query(query).to_data_frame()
        query     = 'MATCH (n) RETURN ID(n) as Node_id, n as Nodes, labels(n) as Label'
        nodes     = self.driver.query(query).to_data_frame()    
        # graph     = pd.concat([nodes, relations], axis = 1)
        
        return nodes, relations
    
    def test_query(self):
        query = "match (n), (a)-[r]-(b) return distinct n.name as Node, labels(n) as Label, type(r) as Relations"
        nodes = self.driver.query(query)
        return nodes