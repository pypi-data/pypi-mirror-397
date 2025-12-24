# (C) 2025 thpit

__author__ = "thpit"
__date__ = "2025-12-06b"
__version__ = "0.3.1"

__all__ = ['CfCtx', 'TgtNode', 'GraphNode', 'GraphEdge', 'Graph', 
            'GraphRunnerState', 'GraphRunner']

# 2025-12-06b:
# - Ctx rename
# - TgtNode remark field; new "returned"
# - placing all internal state info into "._internal" field in GraphRunnerState
# ... 
# - edges_from_string() and edges_to_string()   (prelim. impl.) (needs json)
# - We allow that from a node, both a single regular edge, and announced edges, 
#   may originate. This allows handling of exceptional cases at nodes where usually
#   a regular edge is used.

class CfCtx:
    def __init__(self):
        self._raw_debug = False

class TgtNode:
    _start = None
    _end = None
    
    def __init__(self, spec, remark: str = ""):
        if spec is None:
            raise ValueError("Expecting str or function.")
        self.spec = spec
        self.remark = remark
        
    @staticmethod
    def start():
        if TgtNode._start is None:
            TgtNode._start = TgtNode(TgtNode.start)
        return TgtNode._start

    @staticmethod
    def end():
        if TgtNode._end is None:
            TgtNode._end = TgtNode(TgtNode.end)
        return TgtNode._end
        
        
###############################################################################

class GraphNode:
    """This class is usually not explicitly instantiated by the user code.
    """
    def __init__(self, name: str, func, description: str = ""):
        self.name = name
        self.func = func
        self.description = description
        
    def run(self, state, ctx: CfCtx):
        if ctx._raw_debug: print("I: Running " + self.name)
        return self.func(state, ctx)

class GraphEdge:
    """This class is usually not explicitly instantiated by the user code.
    """
    def __init__(self, nd1: GraphNode, nd2: GraphNode, description: str = ""):
        """Construct edge object for edge from nd1 to nd2."""
        self.nd1 = nd1
        self.nd2 = nd2
        self.description = description
        self._traversal_count = 0
        #self._added = _added    # hack to distinguish "added" and "anncd" later
        
class Graph:
    def __init__(self, node_name_prefix: str = ""):
        """Instantiate a graph object.

        :param node_name_prefix: prefix used when resolving non-qualified node references.
        :type str:
        """
        self.node_name_prefix = node_name_prefix

        self.nodes = dict()
        self.edges_added = dict()   # src_nd => GraphEdge(src_nd, tgt_nd)

class GraphRunnerState:
    pass

class GraphRunner:
    pass
    
    
    
##############################################################################

if __name__ == "__main__":

    graph = Graph()
    graph.add_node(MyNodes.node1, "Collect the query")
    graph.add_node(MyNodes.node2, "Solve the query")

    gr1 = GraphRunner()

