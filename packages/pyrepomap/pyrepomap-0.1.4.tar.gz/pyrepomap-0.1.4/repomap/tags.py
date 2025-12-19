"""Tag extraction logic using tree-sitter."""

import warnings
from collections import namedtuple
from importlib import resources
from pathlib import Path

import tree_sitter
from grep_ast import filename_to_lang
from pygments.lexers import guess_lexer_for_filename
from pygments.token import Token

# tree_sitter is throwing a FutureWarning
warnings.simplefilter("ignore", category=FutureWarning)
from grep_ast.tsl import USING_TSL_PACK, get_language, get_parser  # noqa: E402


Tag = namedtuple("Tag", "rel_fname fname line name kind".split())


def get_scm_fname(lang: str) -> Path:
    """Get the path to the tree-sitter query file for a language."""
    if USING_TSL_PACK:
        subdir = "tree-sitter-language-pack"
        try:
            path = resources.files(__package__).joinpath(
                "queries",
                subdir,
                f"{lang}-tags.scm",
            )
            if path.exists():
                return path
        except KeyError:
            pass
    
    return None


def get_tags_raw(fname: str, rel_fname: str, code: str):
    """
    Extract tags (definitions and references) from a source file using tree-sitter.
    """
    lang = filename_to_lang(fname)
    if not lang:
        return
    
    try:
        language = get_language(lang)
        parser = get_parser(lang)
    except Exception as err:
        print(f"Skipping file {fname}: {err}")
        return
    
    query_scm = get_scm_fname(lang)
    if not query_scm or not query_scm.exists():
        return
    query_scm = query_scm.read_text()
    
    if not code:
        return
    tree = parser.parse(bytes(code, "utf-8"))
    
    # Run the tags queries using tree-sitter 0.25.2 API (QueryCursor)
    query = tree_sitter.Query(language, query_scm)
    cursor = tree_sitter.QueryCursor(query)
    captures = cursor.captures(tree.root_node)
    
    saw = set()
    # New API returns dict: {tag_name: [nodes]}
    all_nodes = []
    for tag, nodes in captures.items():
        all_nodes += [(node, tag) for node in nodes]
    
    for node, tag in all_nodes:
        if tag.startswith("name.definition."):
            kind = "def"
        elif tag.startswith("name.reference."):
            kind = "ref"
        else:
            continue
        
        saw.add(kind)
        
        result = Tag(
            rel_fname=rel_fname,
            fname=fname,
            name=node.text.decode("utf-8"),
            kind=kind,
            line=node.start_point[0],
        )
        
        yield result
    
    if "ref" in saw:
        return
    if "def" not in saw:
        return
    
    # Use pygments to backfill refs for languages without ref queries
    try:
        lexer = guess_lexer_for_filename(fname, code)
    except Exception:
        return
    
    tokens = list(lexer.get_tokens(code))
    tokens = [token[1] for token in tokens if token[0] in Token.Name]
    
    for token in tokens:
        yield Tag(
            rel_fname=rel_fname,
            fname=fname,
            name=token,
            kind="ref",
            line=-1,
        )
