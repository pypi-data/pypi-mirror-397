"""Tree rendering for repo map output."""

from grep_ast import TreeContext

from .tags import Tag


def render_tree(abs_fname, rel_fname, lois, read_text_fn, tree_cache, tree_context_cache, get_mtime_fn):
    """
    Render a file's code tree with lines of interest highlighted.
    """
    mtime = get_mtime_fn(abs_fname)
    key = (rel_fname, tuple(sorted(lois)), mtime)
    
    if key in tree_cache:
        return tree_cache[key]
    
    if (
        rel_fname not in tree_context_cache
        or tree_context_cache[rel_fname]["mtime"] != mtime
    ):
        code = read_text_fn(abs_fname) or ""
        if not code.endswith("\n"):
            code += "\n"
        
        context = TreeContext(
            rel_fname,
            code,
            color=False,
            line_number=False,
            child_context=False,
            last_line=False,
            margin=0,
            mark_lois=False,
            loi_pad=0,
            show_top_of_file_parent_scope=False,
        )
        tree_context_cache[rel_fname] = {"context": context, "mtime": mtime}
    
    context = tree_context_cache[rel_fname]["context"]
    context.lines_of_interest = set()
    context.add_lines_of_interest(lois)
    context.add_context()
    res = context.format()
    tree_cache[key] = res
    return res


def to_tree(tags, chat_rel_fnames, read_text_fn, tree_cache, tree_context_cache, get_mtime_fn, get_abs_fname_fn):
    """
    Convert ranked tags to a tree-formatted markdown string.
    """
    if not tags:
        return ""
    
    cur_fname = None
    cur_abs_fname = None
    lois = None
    output = ""
    
    # add a bogus tag at the end so we trip the this_fname != cur_fname...
    dummy_tag = (None,)
    for tag in sorted(tags) + [dummy_tag]:
        this_rel_fname = tag[0]
        if this_rel_fname in chat_rel_fnames:
            continue
        
        # ... here ... to output the final real entry in the list
        if this_rel_fname != cur_fname:
            if lois is not None:
                output += "\n"
                output += cur_fname + ":\n"
                output += render_tree(
                    cur_abs_fname, cur_fname, lois, read_text_fn,
                    tree_cache, tree_context_cache, get_mtime_fn
                )
                lois = None
            elif cur_fname:
                output += "\n" + cur_fname + "\n"
            if type(tag) is Tag:
                lois = []
                cur_abs_fname = tag.fname
            cur_fname = this_rel_fname
        
        if lois is not None:
            lois.append(tag.line)
    
    # truncate long lines, in case we get minified js or something else crazy
    output = "\n".join([line[:100] for line in output.splitlines()]) + "\n"
    
    return output
