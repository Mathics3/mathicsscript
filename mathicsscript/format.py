"""
Format Mathics objects
"""

import random
import networkx as nx


def format_output(obj, expr, format=None):
    if format is None:
        format = obj.format

    if isinstance(format, dict):
        return dict((k, obj.format_output(expr, f)) for k, f in format.items())

    from mathics.core.expression import Expression, BoxError

    expr_type = expr.get_head_name()
    if expr_type == "System`MathMLForm":
        format = "xml"
        leaves = expr.get_leaves()
        if len(leaves) == 1:
            expr = leaves[0]
    elif expr_type == "System`TeXForm":
        format = "tex"
        leaves = expr.get_leaves()
        if len(leaves) == 1:
            expr = leaves[0]
    elif expr_type == "System`Graphics":
        result = Expression("StandardForm", expr).format(obj, "System`MathMLForm")
        ml_str = result.leaves[0].leaves[0]
        # FIXME: not quite right. Need to parse out strings
        display_svg(str(ml_str))

    if format == "text":
        result = expr.format(obj, "System`OutputForm")
    elif format == "xml":
        result = Expression("StandardForm", expr).format(obj, "System`MathMLForm")
    elif format == "tex":
        result = Expression("StandardForm", expr).format(obj, "System`TeXForm")
    elif format == "unformatted":
        if str(expr) == "-Graph-":
            return format_graph(expr.G, expr.options)
        else:
            result = expr.format(obj, "System`OutputForm")
    else:
        raise ValueError

    try:
        boxes = result.boxes_to_text(evaluation=obj)
    except BoxError:
        boxes = None
        if not hasattr(obj, "seen_box_error"):
            obj.seen_box_error = True
            obj.message(
                "General", "notboxes", Expression("FullForm", result).evaluate(obj)
            )
    return boxes


def hierarchy_pos(G, root=None, width=1.0, vert_gap=0.2, vert_loc=0, xcenter=0.5):

    """
    From Joel's answer at https://stackoverflow.com/a/29597209/2966723.
    Licensed under Creative Commons Attribution-Share Alike

    If the graph is a tree this will return the positions to plot this in a
    hierarchical layout.

    G: the graph (must be a tree)

    root: the root node of current branch
    - if the tree is directed and this is not given,
      the root will be found and used
    - if the tree is directed and this is given, then
      the positions will be just for the descendants of this node.
    - if the tree is undirected and not given,
      then a random choice will be used.

    width: horizontal space allocated for this branch - avoids overlap with other branches

    vert_gap: gap between levels of hierarchy

    vert_loc: vertical location of root

    xcenter: horizontal location of root
    """
    if not nx.is_tree(G):
        raise TypeError("cannot use hierarchy_pos on a graph that is not a tree")

    if root is None:
        if isinstance(G, nx.DiGraph):
            root = next(
                iter(nx.topological_sort(G))
            )  # allows back compatibility with nx version 1.11
        else:
            root = random.choice(list(G.nodes))

    def _hierarchy_pos(
        G, root, width=1.0, vert_gap=0.2, vert_loc=0, xcenter=0.5, pos=None, parent=None
    ):
        """
        see hierarchy_pos docstring for most arguments

        pos: a dict saying where all nodes go if they have been assigned
        parent: parent of this branch. - only affects it if non-directed

        """

        if pos is None:
            pos = {root: (xcenter, vert_loc)}
        else:
            pos[root] = (xcenter, vert_loc)
        children = list(G.neighbors(root))
        if not isinstance(G, nx.DiGraph) and parent is not None:
            children.remove(parent)
        if len(children) != 0:
            dx = width / len(children)
            nextx = xcenter - width / 2 - dx / 2
            for child in children:
                nextx += dx
                pos = _hierarchy_pos(
                    G,
                    child,
                    width=dx,
                    vert_gap=vert_gap,
                    vert_loc=vert_loc - vert_gap,
                    xcenter=nextx,
                    pos=pos,
                    parent=root,
                )
        return pos

    return _hierarchy_pos(G, root, width, vert_gap, vert_loc, xcenter)


def tree_layout(G):
    root = G.root if hasattr(G, "root") else None
    return hierarchy_pos(G, root=root)


NETWORKX_LAYOUTS = {
    "circular": nx.circular_layout,
    "multipartite": nx.multipartite_layout,
    "planar": nx.planar_layout,
    "random": nx.random_layout,
    "shell": nx.shell_layout,
    "spectral": nx.spectral_layout,
    "spring": nx.spring_layout,
    "tree": tree_layout,
}


def format_graph(G, options):
    """
    Format a Graph
    """
    # FIXME handle graphviz as well
    import matplotlib.pyplot as plt

    plot_theme = options.get("PlotTheme", None)
    vertex_labeling = options.get("VertexLabeling", None).to_python() or False
    if plot_theme:
        if not isinstance(plot_theme, str):
            plot_theme = plot_theme.get_string_value()
        layout_fn = NETWORKX_LAYOUTS.get(plot_theme, None)
    else:
        layout_fn = None

    if layout_fn:
        nx.draw(G, pos=layout_fn(G), with_labels=vertex_labeling)
    else:
        nx.draw_shell(G, with_labels=vertex_labeling)
    plt.show()
    return None
