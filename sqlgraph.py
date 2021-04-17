from sqldoc_mariadb import Sqldoc, mariadb


class StillConnected(Exception):
    pass


class SqlGraph(Sqldoc):
    pass

    # outgoing
    # incoming
    #

    def create_edge(self, source, target, **kwargs):
        if type(source) is not str:
            source = source['_docid']
        if type(target) is not str:
            target = target['_docid']

        edge = dict(_source=source, _target=target)
        edge.update(**kwargs)
        return Edge(self, **self.create_doc(edge))

    def create_node(self, **kwargs):
        return Node(self, **self.create_doc(kwargs))

    def incoming_edgeids(self, node):
        if type(node) != str:
            node = node['_docid']
        fragment = f"a1.name='_target' and a1.str='{node}'"
        return self.query_docids(fragment)

    def outgoing_edgeids(self, node):
        if type(node) != str:
            node = node['_docid']
        fragment = f"a1.name='_source' and a1.str='{node}'"
        return self.query_docids(fragment)

    def edges(self, edgeids):
        for edgeid in edgeids:
            yield Edge(self, **self.read_doc(edgeid))

    def del_node(self, node, del_connected=False):
        if type(node) != str:
            node = node['_docid']
        incoming = self.incoming_edgeids(node)
        outgoing = self.outgoing_edgeids(node)
        alledges = set(incoming) | set(outgoing)

        if alledges:
            if del_connected:
                for edgeid in alledges:
                    self.del_doc(edgeid)
            else:
                raise StillConnected(f'node {node} is still connected')

        self.del_doc(node)


class Node(dict):

    def __init__(self, sg: SqlGraph, **kwargs):
        self.sg = sg
        dict.__init__(self, **kwargs)

    def incoming(self):
        return self.sg.incoming_edgeids(self)

    def outgoing(self):
        return self.sg.outgoing_edgeids(self)

    def incoming_edges(self):
        return self.edges(self.sg.incoming_edgeids(self))

    def outgoing_edges(self):
        return self.edges(self.sg.outgoing_edgeids(self))

    def edges(self, edgeids):
        return self.sg.edges(edgeids)


class Edge(dict):

    def __init__(self, sg: SqlGraph, **kwargs):
        self.sg = sg
        dict.__init__(self, **kwargs)

    def source(self):
        return Node(self.sg, **self.sg.read_doc(self['_source']))

    def target(self):
        return Node(self.sg, **self.sg.read_doc(self['_target']))


def test():
    conn = mariadb.connect(
            user="sqldoc",
            password="sqldoc",
            database='sqldoc',
            host="127.0.0.1",

            port=3306)

    sg = SqlGraph(conn, True, False)

    alice = sg.create_node(name='Alice')
    bob = sg.create_node(name='Bob')
    charlie = sg.create_node(name='Charlie')

    edge1 = sg.create_edge(alice, bob, relation='likes')
    edge2 = sg.create_edge(bob, charlie, relation='likes')
    print(list(bob.incoming_edges()))
    print(list(alice.outgoing_edges()))

    print(edge1.source())

    try:
        sg.del_node(charlie)
    except StillConnected as e:
        print(e)

    sg.del_node(charlie, True)

    sg.commit()


if __name__ == '__main__':
    test()
