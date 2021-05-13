from sqldoc_mariadb import mariadb, Sqldoc

class StillConnected(Exception):
    pass


class SqlGraph:

    def __init__(self, storage: Sqldoc):
        self.storage = storage

    def __getattr__(self, item):
        return getattr(self.storage,item)

    def create_edge(self, _source, _target, **kwargs):
        _source = self._docid(_source)
        _target = self._docid(_target)

        edge = dict(_source=_source, _target=_target)
        edge.update(**kwargs)
        return Edge(self, **self.create_doc(edge))

    def create_node(self, **kwargs):
        return Node(self, **self.create_doc(kwargs))

    def incoming_edgeids(self, node):
        node = self._docid(node)
        fragment = f"attr.name='_target' and attr.str='{node}'"
        return self.querydocids(fragment)

    def outgoing_edgeids(self, node):
        node = self._docid(node)
        fragment = f"attr.name='_source' and attr.str='{node}'"
        return self.querydocids(fragment)

    def edges(self, edgeids):
        for edgeid in edgeids:
            yield Edge(self, **self.read_doc(edgeid))

    def del_node(self, node, del_connected=False):
        node = self._docid(node)
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

    def _source(self):
        return Node(self.sg, **self.sg.read_doc(self['_source']))

    def _target(self):
        return Node(self.sg, **self.sg.read_doc(self['_target']))


def test():
    from config import conn
    storage = Sqldoc(conn, True, False)

    sg = SqlGraph(storage)

    alice = sg.create_node(name='Alice')
    bob = sg.create_node(name='Bob')
    charlie = sg.create_node(name='Charlie')

    edge1 = sg.create_edge(alice, bob, relation='likes')
    edge2 = sg.create_edge(bob, charlie, relation='likes')
    print(list(bob.incoming_edges()))
    print(list(alice.outgoing_edges()))

    print(edge1._source())

    try:
        sg.del_node(charlie)
    except StillConnected as e:
        print(e)

    sg.del_node(charlie, True)

    sg.commit()


if __name__ == '__main__':
    test()
