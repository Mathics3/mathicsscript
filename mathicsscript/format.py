"""
Format Mathics objects
"""


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
            return format_graph_matplotlib(expr.G)
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


def format_graph_matplotlib(G):
    """
    Format a Graph
    """
    import matplotlib.pyplot as plt
    import networkx as nx

    nx.draw_shell(G)
    plt.show()
    return None
