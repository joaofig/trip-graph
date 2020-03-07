

class OSMNode(object):

    def __init__(self, nid, lat, lon):
        self.nid = nid
        self.lat = lat
        self.lon = lon

    def __repr__(self):
        return "OSMNode(nid={0}, lat={1}, lon={2}".format(self.nid,
                                                          self.lat,
                                                          self.lon)


class OSMWay(object):

    def __init__(self, wid, nodes, tags):
        self.wid = wid
        self.nodes = set(nodes)
        self.tags = tags

    def has_node(self, nid):
        return nid in self.nodes

    def is_highway(self):
        return "highway" in self.tags

    def has_name(self):
        return "name" in self.tags

    def __repr__(self):
        if self.has_name() and self.is_highway():
            return "OSMWay(wid={0}, name={1})"\
                .format(self.wid, self.tags['name'])
        else:
            return "OSMWay(wid={0})".format(self.wid)


class OSMNet(object):

    def __init__(self):
        self.node_idx = dict()
        self.way_nodes = dict()
        self.ways = []

    def add_node(self, node: OSMNode):
        self.node_idx[node.nid] = node

    def add_nodes(self, nodes):
        for node in nodes:
            self.add_node(node)

    def add_way(self, way: OSMWay):
        self.ways.append(way)
        self.way_nodes[way.wid] = [self.node_idx[nid] for nid in way.nodes]
