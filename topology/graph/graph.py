from threading import Lock

class Node():
    def __init__(self, ip):
        self.ip = ip
        self.running = {"scanned": "false"}

    def __eq__(self, other):
        """Override the default Equals behavior"""
        if isinstance(other, self.__class__):
            return self.ip == other.ip
        return False

    def __ne__(self, other):
        """Define a non-equality test"""
        return not self.__eq__(other)

    def __str__(self):
        if self.running == {"scanned": "false"}:
            return str(self.ip)
        return str((self.ip, self.running))

    def __hash__(self):
        numbers = [int(x) for x in self.ip.split(".")]
        return numbers[0] * 256 ** 3 + numbers[1] * 256 ** 2 + numbers[2] * 256 + numbers[3]

class Graph():
    def __init__(self):
        self.edges = set()
        self.nodes = set()
        self.lock = Lock()

        self.unpopulated = set()
        self.populated = set()

    def add_edge(self, n1, n2):
        self.nodes.add(n1)
        self.nodes.add(n2)

        if n1 not in self.populated:
            self.unpopulated.add(n1)
        if n2 not in self.populated:
            self.unpopulated.add(n2)

        if n1 == n2:
            return

        self.edges.add((n1, n2))

    def merge(self, graph):
        graph1 = self.graph
        graph2 = graph

        self.graph.lock.acquire()

        graph1.edges.union(graph2.edges)
        graph1.nodes.union(graph2.nodes)
        graph1.populated.union(graph2.populated)

        # (U1 + U2) - (P1 + P2)
        graph1.unpopulated.union(graph2.unpopulated)
        graph1.unpopulated.difference(graph1.populated)

        self.graph.lock.release()

    def to_json(self):
        return {
            "hosts" : [{
                "ip" : node.ip,
                "running" : node.running
            } for node in self.nodes],
            "links" : [{
                "source" : n1.ip,
                "target" : n2.ip,
                "value"  : 1,
            } for n1, n2 in self.edges]
        }

    @staticmethod
    def from_json(json_input):
        res = Graph()

        for link in json_input["links"]:
            n1 = Node(link["source"])
            n2 = Node(link["target"])
            res.add_edge(n1, n2)

        for host in json_input["hosts"]:
            n1 = Node(host["ip"])
            running = host["running"]
            for node in res.nodes:
                if node == n1:
                    node.running = running

        return res

    def __str__(self):
         return str([(str(n1), str(n2)) for (n1, n2) in self.edges])