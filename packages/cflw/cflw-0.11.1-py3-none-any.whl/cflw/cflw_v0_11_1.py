# (C) 2025 thpit

__author__ = "thpit"
__date__ = "2025-12-17a"
__version__ = "0.11.1"

__all__ = ['CfCtx', 'TgtNode', 'GraphNode', 'GraphEdge', 'Graph', 
            'CfState', 'GraphRunner', 'RunResult']

import time
from enum import Enum

"""
cflow

A library for synchronously running nodes in a state graph.

Node operation is defined in node functions, which are 
arbitrary (user-implemented) python functions with signature

    func(state, ctx: CfCtx) -> "Target"
    
It is helpful to organize topically-related node functions
into a single class.
"""















###############################################################################

class CfCtx:
    """Object to facilitate keeping references to global resources required
        for node functions or for debugging, e.g. for implementing logging or 
        storage.
        
        Derive from this class, as necessary.
    """
    def __init__(self):
        self._raw_debug = False

class TgtNode:
    _start = None
    _end = None
    _next = None
    _returned = None
    
    def __init__(self, spec, remark: str = ""):
        """If remark is used, it will determine the string value 
            of a corresponding edge label.
        """
        if spec is None:
            raise ValueError("Expecting str or function.")
        self.spec = spec
        self.remark = remark
        
    @staticmethod
    def start():
        """Returns reference to a singleton `TgtNode`."""
        if TgtNode._start is None:
            TgtNode._start = TgtNode(TgtNode.start)
        return TgtNode._start
    @staticmethod
    def end():
        """Returns reference to a singleton `TgtNode`
            signifying the end state of the state graph."""
        if TgtNode._end is None:
            TgtNode._end = TgtNode(TgtNode.end)
        return TgtNode._end
    @staticmethod
    def next():
        """Returns reference to a singleton `TgtNode`
            instructing the runner to proceed along 
            an added edge."""
        if TgtNode._next is None:
            TgtNode._next = TgtNode(TgtNode.next)
        return TgtNode._next
    @staticmethod
    def returned():
        """Returns reference to a singleton `TgtNode` which
            instructs the runner to pass control back to 
            the precedingly running node."""
        if TgtNode._returned is None:
            TgtNode._returned = TgtNode(TgtNode.returned)
        return TgtNode._returned
        
        
###############################################################################

class GraphNode:
    """Internal only.
    
        This class is usually not explicitly instantiated by user code.
        Read access to public members `name`, `func` and `label` is possible.
    """
    def __init__(self, name: str, func, label: str = ""):
        self.name = name
        self.func = func
        self.label = label
        
    def _run(self, state, ctx: CfCtx):
        """Internal only.
        """
        if ctx._raw_debug: print("I: Running " + self.name)
        return self.func(state, ctx)

class GraphEdge:
    """Internal only.
    
        Construct edge object for edge from nd1 to nd2.
    
        This class is usually not explicitly instantiated by user code.
    """
    def __init__(self, nd1: GraphNode, nd2: GraphNode, label: str = ""):
        # Construct edge object for edge from nd1 to nd2.
        self.nd1 = nd1
        self.nd2 = nd2
        self.label = label
        self._traversal_count = 0
        
###############################################################################

class Graph:
    def __init__(self, node_name_prefix: str = ""):
        """Instantiate a graph object.

        Parameters
        ----------
        node_name_prefix : str
            The prefix used when resolving `str`-like non-qualified node references.
        """
        self.node_name_prefix = node_name_prefix
        self.entry_point = None

        self.nodes = dict()
        self.edges_added = dict()   # src_nd => GraphEdge(src_nd, tgt_nd)
        self.edges_anncd = dict()   # src_nd => dict(tgt_nd => GraphEdge(src_nd, tgt_nd))
        
        self._nd_end = GraphNode("__end__", None)   
        
    def _resolve_node_spec(self, node_spec):
        """Internal only.
        
            Resolves to (name, ndfunc, nd), where name is the node name, 
            ndfunc is the (user-defined) function,  and nd is a `GraphNode` object.
            node_spec may be a `TgtNode` instance or a `GraphNode` instance.
        """
        if node_spec == TgtNode.end():
            return "__end__", None, self._nd_end
        if node_spec == TgtNode.start():
            return (self.entry_point.name, self.entry_point.func, self.entry_point) \
                        if self.entry_point else (None, None, None)
        if isinstance(node_spec, GraphNode):
            node_name = node_spec.name
            nodefunc = node_spec.func
            nd = node_spec
        elif isinstance(node_spec, str):
            node_name = node_spec
            if node_name.find(".") < 0:
                node_name = self.node_name_prefix + node_name
            raise RunnerException("Using a str as target spec is not fully implemented.")
            nodefunc = eval(node_name)
            nd = None
        elif type(node_spec) == type(TgtNode.end):
            # is function
            node_name = node_spec.__qualname__
            nodefunc = node_spec
            nd = None
        else:
            raise ValueError("Invalid argument to graph building method: "+\
                            "'{}' ".format(node_spec))
        return node_name, nodefunc, nd
                
    def _get_node_for_spec(self, node_spec) -> GraphNode | None:
        """Internal only.
            
            Returns the GraphNode object meant by the provided node spec,
            which can be ndfunc or GraphNode.
        """
        node_name, nodefunc, nd = self._resolve_node_spec(node_spec)
        if nd: return nd
        if not node_name in self.nodes:
            return None
        return self.nodes[node_name]
      
    def set_entry_point(self, entry_point):
        """Declares the entry point into the state graph.
        
        Parameters
        ----------
        entry_point : GraphNode instance or node function
        
        Returns
        -------
        Graph
            the current Graph instance
        """
        if entry_point is None:
            self.entry_point = None
            return self
        if isinstance(entry_point, GraphNode):
            self.entry_point = entry_point
        elif isinstance(entry_point, TgtNode) or (type(entry_point) != type(TgtNode.start)):
            raise ValueError("Graph.set_entry_point(): Expecting either GraphNode instance or node function as parameter.")
        else:
            nd_first = self._get_node_for_spec(entry_point)
            if nd_first is None: 
                self.add_node(entry_point)
                nd_first = self._get_node_fpr_spec(entry_point)
            self.entry_point = nd_first # = a GraphNode instance
        return self
        
    def _get_next_node(self, nd1):
        """ 
        """
        if not nd1 in self.edges_added: return None
        return self.edges_added[nd1].nd2
        
    def exists_added_edge(self, nd1: GraphNode, nd2: GraphNode) -> bool:
        """
        Returns
        -------
        bool
            True if an added edge exists from nd1 to nd2.
        """
        if not nd1 in self.edges_added: return False
        return self.edges_added[nd1] == nd2
        
    def exists_announced_edge(self, nd1: GraphNode, nd2: GraphNode) -> bool:
        """
        Returns
        -------
        bool
            True if an announced edge exists from nd1 to nd2.
        """
        if not nd1 in self.edges_anncd: return False
        if not nd2 in self.edges_anncd[nd1]: return False
        return True
    
    def add_node(self, node_spec, label: str = ""):
        """
        Adds a node to the graph, regarding the provided python function
        as underlying node implementation.
        
        Parameters
        ----------
        node_spec : function
            Must have signature `(state, ctx: CfCtx)` `->` `TgtNode`, where `state`
            is sub-class of `CfState`.
            
        Returns
        -------
        `Graph`
            : the current graph instance. (This may change in future versions.)
            
        Raises
        ------
        `ValueError`
            if the function reference cannot be resolved.
        """
        node_name, nodefunc, nd = self._resolve_node_spec(node_spec)
        if nd:
            raise ValueError("Expecting node_name (str) or node function as node_spec.")
        if node_name in self.nodes:
            raise ValueError("Node name already exists in graph: " + node_name)
        self.nodes[node_name] = GraphNode(node_name, nodefunc, label=label)
        return self
        
    def add_edge(self, node_spec1, node_spec2, label: str = "", replace: bool = False):
        """Adds an edge. State may pass along these edges by using `TgtNode.next()`.
        
        Parameters
        ----------
        node_spec1, node_spec2 : `GraphNode` or node function
            The edge's from- and to-nodes.
        label : str
            Will appear in visualizations
        replace : bool
            If replace is False, an attempt to add an edge from a node for which an
            outgoing already exists in the graph, will raise an exception; if it is
            `True`, the previous edge will be deleted.
            
        Returns
        -------
        `Graph`
            : the current graph instance
            
        Raises
        ------
        `ValueError`
        """
        nd1 = self._get_node_for_spec(node_spec1)
        nd2 = self._get_node_for_spec(node_spec2)
        #self.edges.append((node_name1, node_name2))
        if (nd1 in self.edges_added) and not replace:
            ge0 = self.edges_added[nd1]
            raise ValueError("Refusing to add another regular edge from node "+\
                "'{}' to '{}'. Already existing one to '{}'.".format(nd1.name, nd2.name, ge0.nd2.name))
        self.edges_added[nd1] = GraphEdge(nd1, nd2, label=label)
        return self

    def replace_edge(self, node_spec1, node_spec2, label: str = ""):
        """Short-cut for `add_edge(..., replace=True)`."""
        return self.add_edge(node_spec1, node_spec2, label=label, replace=True)
    
    def announce_edge(self, node_spec1, node_spec2, label: str = ""):
        """Announce an edge to the graph, i.e. declare a possible state
            transition across that edge (from node1 to node 2).
            
            Returns
            -------
            `Graph`
                : the current graph instance.
        """
        nd1 = self._get_node_for_spec(node_spec1)
        nd2 = self._get_node_for_spec(node_spec2)
        if nd1 is None: raise ValueError("Graph.announce_edge(): Expecting non-None parameter node_spec1.")
        if nd2 is None: raise ValueError("Graph.announce_edge(): Expecting non-None parameter node_spec2.")
        if not nd1 in self.edges_anncd:
            self.edges_anncd[nd1] = dict()
        if not nd2 in self.edges_anncd[nd1]:
            self.edges_anncd[nd1][nd2] = GraphEdge(nd1, nd2, label=label)
        return self

    def _record_traversal(self, nd1: GraphNode, nd2: GraphNode, tgtspec: TgtNode) -> None:
        """Internal only.
        
            To be used internally only. Records the traversal into the current graph
            by either announcing the edge if not yet there (with count 1), or 
            incrementing its trav. count. The nodes occuring as parameters need
            not be in the current graph.
        """
        if tgtspec==TgtNode.next():
            # add the edge:
            if not nd1 in self.edges_added:
                ge = GraphEdge(nd1, nd2)
                self.edges_added[nd1] = ge
            else:
                ge = self.edges_added[nd1]
        else:
            if not nd1 in self.edges_anncd:
                self.edges_anncd[nd1] = dict()
            if not nd2 in self.edges_anncd[nd1]:
                ge = GraphEdge(nd1, nd2, label=tgtspec.remark)
                self.edges_anncd[nd1][nd2] = ge
                # Issue: same (nd1, nd2) pair, but different remark? ignored!
            else:
                ge = self.edges_anncd[nd1][nd2]
                if (ge.label != tgtspec.remark):
                    print("W: During edge traversal recording, different edge labels "+\
                            "for same node pair: '{}'".format(tgtspec.remark))
        ge._traversal_count += 1
        
    def edges_from_string(self, edges_spec: str) -> None:
        """Creates edges in the current graph, as specified by the spec 
            provided as string. Format expected is what is returned from
            `Graph.edges_to_string(..., include_counts=False)`.
            
            Warning
            -------
            Input format may change.

            Parameters
            ----------
            edges_spec : str
                A string representation like the output of `Graph.edges_to_string()`.
        """
        for line in edges_spec:
            line = line.strip()
            xx = line.find("[")
            if xx >= 0: 
                line = line[0:xx].rstrip()
                is_announced = line[xx:] == "[announced]"
            else:
                is_announced = False
            nd1name, nd2name = line.split("->")
            nd1name = nd1name.rstrip()
            nd2name = nd2name.lstrip()
            if is_announced:
                self.announce_edge(nd1name, nd2name)
            else:
                self.add_edge(nd1name, nd2name)
                
    def edges_to_string(self, indent: str = "", include_counts=False):
        """Returns a string representation of the edges in the graph.
        
            Warning
            -------
            Output format may change.

            Returns
            -------        
            `str`
                : a (graphviz) dot-format-like description of all edges.
                (If `include_counts` is `True`, also includes traversal count
                information.)
        """
        res = ""
        for nd1 in self.edges_added:
            ge = self.edges_added[nd1]
            buf = "" if not include_counts else " [{}]".format(ge._traversal_count)
            res += indent + "{} -> {}{}\n".format(nd1.name, ge.nd2.name, buf)
        for nd1 in self.edges_anncd:
            d2 = self.edges_anncd[nd1]
            for nd2 in d2:
                buf = "" if not include_counts else " [{}]".format(d2[nd2]._traversal_count)
                res += indent + "{} -> {} [announced]{}\n".format(nd1.name, nd2.name, buf)
        return res
        
    def as_graphviz_obj(self, comment=None):
        """(Requires optional dependency `graphviz`. See pypi.org.)
        
        Returns
        -------
        graphviz.Digraph
            : a graph representation for visualization.
        """
        return GraphVisualization.as_graphviz_obj(self, comment=comment)

    #-----------------------------------------------------------
    # The following are convenience methods; they shall reduce the
    # amount of code to write while using cflw.
    
    def add_as_pipeline(self, node_funcs: list) -> None:
        """
        Setup a pipeline of nodes in the graph.
        
        List must have as elements either node functions,
        or tuples `(node_func, opt_dict: dict)`, where `node_func`
        is a node function, and `opt_dict` contains keyword options
        to pass to `add_node()`. (Both styles can be mixed.)
            
        For every occuring node function, a `GraphNode` 
        instance will be created if not yet existing
        in the graph. Edges are placed from the previous
        to the current node in the list, successively.    
            
        Parameters
        ----------
        node_funcs : `list`
        """
        prev_node = None
        for node_func in node_funcs:
            if isinstance(node_func, tuple):
                node_func, opt_dict = node_func
                if isinstance(opt_dict, str):
                    opt_dict = {'label': opt_dict}  # expect that the str signifies label value
            else:
                opt_dict = {}
            node = self._get_node_for_spec(node_func)
            if not node:
                self.add_node(node_func, **opt_dict)
                node = self._get_node_for_spec(node_func)
                
            if not prev_node:
                prev_node = node
                continue

            self.add_edge(prev_node, node)
            prev_node = node
    
    #---------- end of convenience methods --------------------
    
###############################################################################

class Foo:
    pass
    
class CfState:
    """Base class from which the user's state class must be derived.
    """
    def __init__(self):
        self._internal = Foo()
        self._internal.ttl = None

class RunnerException(Exception):
    """Raised upon runner-internal exceptions that are
        caused by a graph misspecification.
        
        Runner exceptions are always passed to user code.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
class RunResult:
    """Returned from `GraphRunner.run()`. Member `rc`
        contains the return code after finishing the state graph 
        run; member `exc` contains a user-code originating
        exception if that was reason for stop.
    """
    class RC(Enum):
        """Enumeration covering possible return codes.
            Possible values: `END` (normal end by jumping to the 
            state graph's end state), `TTL_CAP`, and `EXCEPTION`.
        """
        END = 0
        TTL_CAP = -2
        EXCEPTION = -1

    def __init__(self, rc, exc=None):
        self.rc = rc
        self.exc = exc
        
class GraphRunner:
    """The object running the `Graph`.
    
    """

    def __init__(self, *, 
                    enforce_structure: bool = False,
                    tracking_graph: Graph | None = None,
                    default_ttl: int | None = None, 
                    step_delay_secs: float | None = None,
                    pre_run_clbk = None,
                    post_run_clbk = None,
                    propagate_node_exceptions: bool = False):
        """
        Parameters
        ----------
        
        enforce_structure : bool
            If True, all attempts to hop the control flow across
            edges that are neither added nor announced will fail 
            with exception. (This holds for 'start' and 'returned' 
            and 'end' targets also.)

        tracking_graph : `Graph`
            If set to a Graph instance (say `g2`), all edges traversed 
            during running of the current graph instance (provided 
            to `GraphRunner.run()`) are recorded into `g2`. This can be used to 
            automatically collect missing edges, when building the 
            graph structure.
                        
        default_ttl : int | None
            The default ttl value set in `state` instances communicated to 
            `run(...)` which have no ttl value set.
                        
        pre_run_clbk : `function(state, ctx, nd) -> None`
            If not None, the provided function will be run immediately
            before running the specified node.
            (An exception raised within the callback will propagate to
            user top-level code.)
                        
        post_run_clbk : `function(state, ctx, nd, exc=None) -> None`
            Analogous.
            (An exception raised within the callback will propagate to
            user top-level code.)
            Note: `post_run_clbk` will still be run after an exception 
            occured in the respective node. (Then with `exc` not None.)
                        
        propagate_node_exceptions : bool
            If True, exceptions occuring during running
            within the node functions are left propagating to the
            top-level. (This may help debugging.) If False, such exceptions
            <s>stop only the node execution but not the runner from
            running</s> will be caught and the graph finishes indicating
            the exception in `RunResult`.
            (<i>This behaviour is subject to revision and welcomes user feedback.</i>)
        """
        self.enforce_structure = enforce_structure
        self.tracking_graph = tracking_graph
        self.default_ttl = default_ttl      # None = no cap
        self.step_delay_secs = step_delay_secs
        self.pre_run_clbk = pre_run_clbk
        self.post_run_clbk = post_run_clbk
        self.propagate_node_exceptions = propagate_node_exceptions
        
    def run(self, graph, state: CfState, ctx: CfCtx, entry_point = None):
        """Run the given graph, starting from entry_point, passing around a state object.
        
        Run the given graph, starting from the node as specified by entry_point
        (or, if that is None, from the node previously set with set_entry_point())
        and proceeding through a sequence of nodes as defined either by added 
        edges in the graph or directions generated in the node functions. 
        The given state is passed by reference to the nodes, in turn.

        :param graph: The Graph instance to run.
        :type Graph:

        :param state: The state upon which nodes act.
        :type CfState: or sub class thereof; user-defined

        :param entry_point: a GraphNode instance, a node function, or None.

        :raises RunnerException: upon structural errors
        :raises Exception: any other exception as arising from user code.

        :return: A RunResult instance, containing information about the cause of completion.
        :rtype: RunResult
        """
        if not (entry_point is None):
            if isinstance(entry_point, TgtNode):
                raise ValueError("GraphRunner.run(): Expecting entry_point to be either GraphNode instance or node function, or None.")
            if not isinstance(entry_point, GraphNode):
                entry_point = graph._get_node_for_spec(entry_point)
                if entry_point is None:
                    raise ValueError("Provided node function is not associated with a GraphNode instance. Add it first? Typo?")
            # here, entry_point is a GraphNode instance
                        
        orig_first_nd = entry_point if entry_point else graph.entry_point
            
        if state._internal.ttl is None:
            state._internal.ttl = self.default_ttl
        next_spec = orig_first_nd # This may be None; but then results a trivial end.
        prev_nd = None
        while next_spec:
            nd = graph._get_node_for_spec(next_spec)    # next_spec may be a GraphNode instance
            if 1:
                if ctx._raw_debug: print("I: About to run " + nd.name + " ...")
                if self.pre_run_clbk: self.pre_run_clbk(state, ctx, nd)
                try:
                    tgt_node = nd._run(state, ctx)
                except Exception as ex:
                    if self.post_run_clbk: 
                        self.post_run_clbk(state, ctx, nd, ex)
                    else:
                        print("E: While running node {}:".format(nd.name))
                        print("E:", str(ex))
                    if self.propagate_node_exceptions: raise ex  # re-raise
                    return RunResult(RunResult.RC.EXCEPTION, ex)
                if self.post_run_clbk: self.post_run_clbk(state, ctx, nd)
                if not state._internal.ttl is None: state._internal.ttl -= 1
                if not isinstance(tgt_node, TgtNode):
                    raise RunnerException("Expecting TgtNode instance as return value of node's "+\
                                    "run(). (node '{}')".format(nd.name))
                if not tgt_node.spec:
                    raise ValueError("Expecting non-None spec value in TgtNode instance returned from node "+\
                                    "'{}'".format(nd.name))
                if self.step_delay_secs: time.sleep(self.step_delay_secs)
                if tgt_node == TgtNode.end():
                    if self.enforce_structure:
                        if not graph.exists_announced_edge(nd, graph._nd_end):
                            raise RunnerException("Attempt to follow undeclared edge: "+\
                                                "'{}' -> '{}'".format(nd.name, graph._nd_end))
                    if self.tracking_graph: self.tracking_graph._record_traversal(nd, graph._nd_end, tgt_node)
                    return RunResult(RunResult.RC.END)
                if not (state._internal.ttl is None) and (state._internal.ttl <= 0):
                    return RunResult(RunResult.RC.TTL_CAP)
                if tgt_node == TgtNode.returned():
                    if not prev_nd:
                        raise RunnerException("No previous node defined to return to; "+\
                                                "occuring at '{}'".format(nd.name))
                    if self.enforce_structure:
                        if not graph.exists_announced_edge(nd, prev_nd):
                            raise RunnerException("Attempt to follow undeclared edge: "+\
                                                "'{}' -> '{}'".format(nd.name, prev_nd.name))
                    if self.tracking_graph: self.tracking_graph._record_traversal(nd, prev_nd, tgt_node)
                    next_spec = prev_nd
                    prev_nd = None 
                    continue
                prev_nd = nd
                if tgt_node == TgtNode.start(): 
                    if self.enforce_structure:
                        if not graph.exists_announced_edge(nd, orig_first_nd):
                            raise RunnerException("Attempt to follow undeclared edge: "+\
                                                "'{}' -> '{}'".format(nd.name, orig_first_nd.name))
                    if self.tracking_graph: self.tracking_graph._record_traversal(nd, orig_first_nd, tgt_node)
                    next_spec = orig_first_nd
                    continue
                if tgt_node == TgtNode.next():
                    next_spec = graph._get_next_node(nd)    # returns a GraphNode
                    if not next_spec:
                        raise RunnerException("No regular edge to follow defined, from node "+\
                                                "'{}'".format(nd.name))
                    if self.tracking_graph: self.tracking_graph._record_traversal(nd, next_spec, tgt_node)
                    if next_spec == graph._nd_end:
                        return RunResult(RunResult.RC.END)
                    continue
                if True:
                    next_spec = graph._get_node_for_spec(tgt_node.spec)
                    if not next_spec:
                        raise RunnerException("No node corresponding to this target spec defined: "+\
                                                "'{}'".format(tgt_node.spec))
                    if self.enforce_structure:
                        if not graph.exists_announced_edge(nd, next_spec):
                            raise RunnerException("Attempt to follow undeclared edge: "+\
                                                "'{}' -> '{}'".format(nd.name, next_spec.name))                
                    if self.tracking_graph: self.tracking_graph._record_traversal(nd, next_spec, tgt_node)
                continue
        return RunResult(RunResult.RC.END)
        
class GraphVisualization:
    
    @staticmethod
    def as_graphviz_obj(graph: Graph, comment=None):
        """Returns a graphviz object representing the provided graph.
        """
        import graphviz                 # optional dependency
        import datetime as dt

        comment = comment if comment else 'cflw graph ' \
                    + dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        dot = graphviz.Digraph(comment=comment, engine='dot', graph_attr={'splines': 'true'})
        dot.attr('node', foHntname="Arial", fontsize="13")

        def place_node(id, name, fillcolor):
            dot.node(id, name, shape=None if name in ['__start__', '__end__'] else "box", 
                                color="#cccccc", style="rounded,filled", fillcolor=fillcolor)
        
        # start and end node:
        if graph.entry_point: 
            # graph.entry_point here is ensured GraphNode instance
            place_node("__start__", "__start__", "#ffffff")
            dot.edge("__start__", graph.entry_point.name, style=None, 
                        color="#555555")
        
        # other nodes:
        for name in graph.nodes:
            nd = graph.nodes[name]
            fillcolor = "#e6dafa"
            place_node(nd.name, nd.label if nd.label else nd.name, fillcolor)

        place_node("__end__",   "__end__",   "#baadcd")
        
        # added edges:
        for nd1 in graph.edges_added:
            ed = graph.edges_added[nd1]
            nd2 = ed.nd2
            cond = False
            dot.edge(nd1.name, nd2.name, style='dashed' if cond else None, 
                        color="#444444" if cond else "#555555", label=ed.label)
            
        for nd1 in graph.edges_anncd:
            d2 = graph.edges_anncd[nd1]
            for nd2 in d2:
                ed = d2[nd2]
                cond = True
                dot.edge(nd1.name, nd2.name, style='dashed' if cond else None, 
                            color="#444444" if cond else "#555555", label=ed.label)
            
        return dot
    
                            
###############################################################################
###############################################################################

if __name__ == "__main__":

    import sys
    
    class ChatHistory(CfState):
        def __init__(self):
            super().__init__()
            self.messages = []
            self.node1_run_counter = 0
        def append_msg(self, msg):
            self.messages.append(msg)
        def get_last_msg(self):
            if len(self.messages) == 0: return ""
            return self.messages[-1]
        
    class MyNodes:

        def node1(state: ChatHistory, ctx: CfCtx) -> TgtNode: 
            state.node1_run_counter += 1
            
            # recommended:
            return TgtNode(MyNodes.node2)   
                        
        def node2(state: ChatHistory, ctx: CfCtx) -> TgtNode:
            print(state.get_last_msg())
            if state.node1_run_counter >= 5:            
                return TgtNode.end()
            else:
                #return TgtNode.next()
                return TgtNode.start()      # here, this and below variant yield equivalent behavior
                #return TgtNode.returned()

        def node3(state: ChatHistory, ctx: CfCtx) -> TgtNode:
            print("The end.")
            return TgtNode.end()

    graph = Graph(node_name_prefix="MyNodes.")
    graph.add_node(MyNodes.node1, "Collect the query")
    graph.add_node(MyNodes.node2, "Solve the query")
    #graph.add_node(MyNodes.node3, "The end")
    #graph.add_edge(MyNodes.node2, MyNodes.node3)
    graph.announce_edge(MyNodes.node1, MyNodes.node2)
    graph.announce_edge(MyNodes.node2, MyNodes.node1)
    graph.announce_edge(MyNodes.node2, TgtNode.end())

    print(graph.nodes)

    state = ChatHistory()
    state.append_msg({'role': 'user', 'content': 'What is the weather in San Francisco now?'})

    ctx = CfCtx()
    ctx._raw_debug = True
    
    gr1 = GraphRunner(step_delay_secs=0.5, enforce_structure=True)
    rres = gr1.run(graph, state, ctx, MyNodes.node1)

    print(rres.rc, repr(rres.exc))
    
    print(graph.edges_to_string())

    graph.set_entry_point(MyNodes.node1)
    
    #dot1 = graph.as_graphviz_obj()
    #print(dot1)
    


