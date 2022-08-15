"""
CODE FROM emekadavid
https://emekadavid-solvingit.blogspot.com/2020/08/classes-for-graphs-and-directed-graphs.html
"""
class Node(object):

    def __init__(self, name):
        ''' assumes name a string '''
        self.name = name

    def get_name(self):
        return self.name

    def __str__(self):
        return self.name

"""
CODE FROM emekadavid
https://emekadavid-solvingit.blogspot.com/2020/08/classes-for-graphs-and-directed-graphs.html
"""
class Edge(object):

    def __init__(self, src, dest):
        '''assume src and dest are nodes '''
        self.src = src
        self.dest = dest

    def get_source(self):
        return self.src

    def get_destination(self):
        return self.dest

    def __str__(self):
        return self.src.get_name() + '-->' + \
            self.dest.get_name()

"""
CODE FROM emekadavid
https://emekadavid-solvingit.blogspot.com/2020/08/classes-for-graphs-and-directed-graphs.html
"""
class Digraph(object):
    # node is a list of the nodes in the graph
    # edges is a dict mapping each node to 
    # a list of its children
    def __init__(self):
        self.nodes = []
        self.edges = {}

    def add_node(self, node):
        if node in self.nodes:
            raise ValueError('Duplicate Node')
        else:
            self.nodes.append(node)
            self.edges[node] = []

    def add_edge(self, edge):
        src = edge.get_source()
        dest = edge.get_destination()
        if not (src in self.nodes and dest in self.nodes):
            raise ValueError('Node not in graph')
        self.edges[src].append(dest)

    def children_of(self, node):
        return self.edges[node]

    def has_node(self, node):
        return node in self.nodes

    def find_node_by_name(self, name):
        for node in self.nodes:
            if node.get_name() == name:
                return node
        return None

    def parents_of(self, f_node):
        parent_list = []
        for key in self.edges:
            nodes = self.edges[key]
            if f_node in nodes:
                parent_list.append(key)
        return parent_list

    def __str__(self):
        result = ''
        for src in self.nodes:
            for dest in self.edges[src]:
                result = result + src.get_name() + \
                    '-->' + dest.get_name() + '\n'
        return result[:-1] # remove last newline
