"""
Format Mathics objects
"""

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


NETWORKX_LAYOUTS = {
    "circular": nx.circular_layout,
    "multipartite": nx.multipartite_layout,
    "planar": nx.planar_layout,
    "random": nx.random_layout,
    "shell": nx.shell_layout,
    "spectral": nx.spectral_layout,
    "spring": nx.spring_layout,
    "tree": nx.planar_layout,
}


def format_graph(G, options):
    """
    Format a Graph
    """
    # FIXME handle graphviz as well
    import matplotlib.pyplot as plt

    plot_theme = options.get("PlotTheme", None)
    if plot_theme:
        if not isinstance(plot_theme, str):
            plot_theme = plot_theme.get_string_value()
        layout_fn = NETWORKX_LAYOUTS.get(plot_theme, None)

    if layout_fn:
        nx.draw(G, pos=layout_fn(G))
    else:
        nx.draw_shell(G)
    plt.show()
    return None
