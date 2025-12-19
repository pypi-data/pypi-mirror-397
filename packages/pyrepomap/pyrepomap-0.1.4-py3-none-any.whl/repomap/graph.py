"""Call graph generation and visualization."""

import os
import sys
from collections import defaultdict
from pathlib import Path

import networkx as nx
from tqdm import tqdm

from .tags import get_tags_raw


def get_reachable_files(repomap, fnames, entry, depth=None, min_refs=1, verbose=False):
    """
    Get list of files reachable from an entry point.
    
    Args:
        repomap: RepoMap instance
        fnames: List of all file paths
        entry: Entry point file name/pattern
        depth: Maximum depth to traverse
        min_refs: Minimum references for symbol inclusion
        verbose: Enable verbose output
        
    Returns:
        List of file paths reachable from entry point
    """
    # Build the dependency graph
    defines = defaultdict(set)
    references = defaultdict(list)
    symbol_refs_count = defaultdict(int)
    
    file_iter = tqdm(fnames, desc="Scanning files", leave=False) if len(fnames) > 50 else fnames
    for fname in file_iter:
        rel_fname = repomap.get_rel_fname(fname)
        code = repomap.read_text(fname)
        if not code:
            continue
        
        tags = list(get_tags_raw(fname, rel_fname, code))
        
        for tag in tags:
            if tag.kind == "def":
                defines[tag.name].add(rel_fname)
            elif tag.kind == "ref":
                references[tag.name].append(rel_fname)
                symbol_refs_count[tag.name] += 1
    
    # Filter by min_refs
    if min_refs > 1:
        defines = {k: v for k, v in defines.items() if symbol_refs_count.get(k, 0) >= min_refs}
    
    # Build graph
    G = nx.DiGraph()
    for ident in defines:
        for ref_file in set(references.get(ident, [])):
            for def_file in defines[ident]:
                if ref_file != def_file:
                    G.add_edge(ref_file, def_file)
    
    # Find entry point - prioritize exact path matches
    entry_files = []
    entry_normalized = os.path.normpath(entry)  # Normalize ./main.py -> main.py
    entry_basename = Path(entry).name  # Get just the filename
    
    for node in G.nodes():
        node_normalized = os.path.normpath(node)
        # Check for exact path match first (handles ./main.py matching main.py)
        if node_normalized == entry_normalized:
            entry_files = [node]  # Exact match, use only this
            break
        # Check if entry is a suffix of node path (e.g., "src/main.py" matches "project/src/main.py")
        if node_normalized.endswith("/" + entry_normalized) or node_normalized == entry_normalized:
            entry_files = [node]
            break
    
    # Fall back to basename matching only if no exact match found
    if not entry_files:
        for node in G.nodes():
            node_basename = Path(node).name
            if node_basename == entry_basename:
                entry_files.append(node)
    
    if not entry_files:
        print(f"Error: Entry point '{entry}' not found", file=sys.stderr)
        return None
    
    if len(entry_files) > 1:
        print(f"Error: Multiple files match '{entry}':", file=sys.stderr)
        for f in sorted(entry_files):
            # Show with ./ prefix if at root level for clarity
            display_path = f if "/" in f else f"./{f}"
            print(f"  --entry {display_path}", file=sys.stderr)
        return None
    
    entry_file = entry_files[0]
    
    # BFS from entry point
    reachable = {entry_file}
    frontier = {entry_file}
    current_depth = 0
    
    while frontier and (depth is None or current_depth < depth):
        next_frontier = set()
        for node in frontier:
            next_frontier.update(G.successors(node))
        next_frontier -= reachable
        reachable.update(next_frontier)
        frontier = next_frontier
        current_depth += 1
    
    # Convert back to absolute paths
    result = []
    for fname in fnames:
        rel_fname = repomap.get_rel_fname(fname)
        if rel_fname in reachable:
            result.append(fname)
    
    return result

def generate_call_graph(
    repomap, 
    fnames, 
    output_file, 
    focus=None, 
    entry=None,
    depth=None,
    min_refs=1,
    verbose=False
):
    """
    Generate a call graph visualization from repository files.
    
    Args:
        repomap: RepoMap instance
        fnames: List of file paths to analyze
        output_file: Output file path (.png, .svg, .pdf, .dot)
        focus: Optional symbol name to focus the graph on
        entry: Optional entry point file to start traversal from
        depth: Maximum depth to traverse from entry point
        min_refs: Minimum number of references for a symbol to be included
        verbose: Enable verbose output
    """
    # Build the graph
    G = nx.DiGraph()
    
    defines = defaultdict(set)  # ident -> set of files that define it
    references = defaultdict(list)  # ident -> list of (file, count)
    symbol_refs_count = defaultdict(int)  # ident -> total reference count
    file_to_symbols = defaultdict(set)  # file -> set of symbols defined
    
    file_iter = tqdm(fnames, desc="Scanning files", leave=False) if len(fnames) > 50 else fnames
    for fname in file_iter:
        rel_fname = repomap.get_rel_fname(fname)
        code = repomap.read_text(fname)
        if not code:
            continue
        
        tags = list(get_tags_raw(fname, rel_fname, code))
        
        for tag in tags:
            if tag.kind == "def":
                defines[tag.name].add(rel_fname)
                file_to_symbols[rel_fname].add(tag.name)
            elif tag.kind == "ref":
                references[tag.name].append(rel_fname)
                symbol_refs_count[tag.name] += 1
    
    # Filter symbols by minimum references
    if min_refs > 1:
        filtered_defines = {}
        for ident, files in defines.items():
            if symbol_refs_count.get(ident, 0) >= min_refs:
                filtered_defines[ident] = files
        defines = filtered_defines
    
    # Create file-level edges (file A references symbol defined in file B)
    for ident in defines:
        definers = defines[ident]
        refs = references.get(ident, [])
        
        for ref_file in set(refs):
            for def_file in definers:
                if ref_file != def_file:
                    # Edge from referencer to definer
                    if G.has_edge(ref_file, def_file):
                        # Increment weight
                        G[ref_file][def_file]['weight'] += 1
                        G[ref_file][def_file]['symbols'].add(ident)
                    else:
                        G.add_edge(ref_file, def_file, weight=1, symbols={ident})
    
    # If entry point is specified, extract subgraph from that file
    if entry:
        entry_files = []
        entry_normalized = os.path.normpath(entry)  # Normalize ./main.py -> main.py
        entry_basename = Path(entry).name  # Get just the filename
        
        for node in G.nodes():
            node_normalized = os.path.normpath(node)
            # Check for exact path match first (handles ./main.py matching main.py)
            if node_normalized == entry_normalized:
                entry_files = [node]  # Exact match, use only this
                break
            # Check if entry is a suffix of node path
            if node_normalized.endswith("/" + entry_normalized) or node_normalized == entry_normalized:
                entry_files = [node]
                break
        
        # Fall back to basename matching only if no exact match found
        if not entry_files:
            for node in G.nodes():
                node_basename = Path(node).name
                if node_basename == entry_basename:
                    entry_files.append(node)
        
        if not entry_files:
            print(f"Error: Entry point '{entry}' not found in graph", file=sys.stderr)
            return
        
        if len(entry_files) > 1:
            print(f"Error: Multiple files match '{entry}':", file=sys.stderr)
            for f in sorted(entry_files):
                display_path = f if "/" in f else f"./{f}"
                print(f"  --entry {display_path}", file=sys.stderr)
            return
        
        entry_file = entry_files[0]
        
        # BFS from entry point with optional depth limit
        reachable = {entry_file}
        frontier = {entry_file}
        current_depth = 0
        
        while frontier and (depth is None or current_depth < depth):
            next_frontier = set()
            for node in frontier:
                # Add successors (files this file depends on)
                next_frontier.update(G.successors(node))
            
            next_frontier -= reachable
            reachable.update(next_frontier)
            frontier = next_frontier
            current_depth += 1
        
        G = G.subgraph(reachable).copy()
        if verbose:
            print(f"Entry point '{entry}' -> {len(reachable)} files (depth {current_depth})", 
                  file=sys.stderr)
    
    # If focus is specified, extract subgraph around the focus node
    if focus:
        focus_nodes = set()
        for node in G.nodes():
            if focus.lower() in node.lower():
                focus_nodes.add(node)
                focus_nodes.update(G.predecessors(node))
                focus_nodes.update(G.successors(node))
        
        if focus_nodes:
            G = G.subgraph(focus_nodes).copy()
        else:
            print(f"Warning: No nodes matching '{focus}' found", file=sys.stderr)
    
    if len(G.nodes()) == 0:
        print("No graph data to visualize", file=sys.stderr)
        return
    
    if verbose:
        print(f"Graph: {len(G.nodes())} nodes, {len(G.edges())} edges", file=sys.stderr)
    
    # Simplify node labels (use just filename, not full path)
    mapping = {}
    for node in G.nodes():
        short_name = Path(node).name
        # Handle duplicates by keeping path prefix if needed
        if short_name in mapping.values():
            # Use parent/file format
            short_name = str(Path(node).parent.name) + "/" + short_name
        mapping[node] = short_name
    
    G = nx.relabel_nodes(G, mapping)
    
    # Convert symbols set to comma-separated string for DOT compatibility
    for u, v, data in G.edges(data=True):
        if 'symbols' in data and isinstance(data['symbols'], set):
            # Limit to first 5 symbols to avoid super long labels
            syms = sorted(data['symbols'])[:5]
            if len(data['symbols']) > 5:
                syms.append(f"...+{len(data['symbols']) - 5}")
            data['label'] = ", ".join(syms)
            del data['symbols']  # Remove the set
    
    # Determine output format
    output_path = Path(output_file)
    ext = output_path.suffix.lower()
    base_name = output_path.stem.lower()
    
    if ext == ".json":
        import json
        import time
        
        # Check if FASTEN format requested (filename ends with .fasten.json)
        if base_name.endswith(".fasten"):
            # FASTEN format version 2 - structured call graph
            # Build namespace mapping with unique IDs
            namespace_id = 0
            namespace_map = {}  # node -> id
            internal_modules = {}
            
            for node in sorted(G.nodes()):
                module_uri = f"/{node.replace('.py', '').replace('/', '.')}/"
                namespace_map[node] = str(namespace_id)
                
                internal_modules[module_uri] = {
                    "sourceFile": node,
                    "namespaces": {
                        str(namespace_id): {
                            "namespace": module_uri,
                            "metadata": {}
                        }
                    }
                }
                namespace_id += 1
            
            # Build calls using string IDs per version 2 spec
            internal_calls = []
            for u, v in G.edges():
                src_id = namespace_map.get(u, u)
                dst_id = namespace_map.get(v, v)
                internal_calls.append([src_id, dst_id, {}])
            
            fasten_output = {
                "product": Path(repomap.root).name,
                "forge": "local",
                "nodes": namespace_id,
                "generator": "repomap",
                "depset": [],
                "version": "0.1.0",
                "modules": {
                    "internal": internal_modules,
                    "external": {}
                },
                "graph": {
                    "internalCalls": internal_calls,
                    "externalCalls": [],
                    "resolvedCalls": []
                },
                "timestamp": int(time.time())
            }
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(fasten_output, f, indent=2)
        else:
            # Simple adjacency list format
            adj_list = {}
            for node in G.nodes():
                adj_list[node] = sorted(set(G.successors(node)))
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(adj_list, f, indent=2)
    elif ext == ".dot":
        nx.drawing.nx_pydot.write_dot(G, output_file)
    else:
        try:
            _render_graph(G, output_file, ext)
        except Exception as e:
            dot_file = output_path.with_suffix(".dot")
            nx.drawing.nx_pydot.write_dot(G, dot_file)
            print(f"Could not render {ext} format ({e}). Saved as DOT: {dot_file}", 
                  file=sys.stderr)


def _render_graph(G, output_file, ext):
    """Render graph to image file using matplotlib or graphviz."""
    try:
        import pydot
        
        pydot_graph = nx.drawing.nx_pydot.to_pydot(G)
        pydot_graph.set_rankdir("LR")
        pydot_graph.set_nodesep(0.5)
        pydot_graph.set_ranksep(1.0)
        
        # Style nodes
        for node in pydot_graph.get_nodes():
            node.set_shape("box")
            node.set_style("rounded,filled")
            node.set_fillcolor("#e8f4f8")
            node.set_fontname("Helvetica")
            node.set_fontsize(10)
        
        # Style edges with weight as thickness
        for edge in pydot_graph.get_edges():
            edge.set_fontsize(8)
            edge.set_fontcolor("#666666")
            edge.set_color("#666666")
        
        if ext == ".png":
            pydot_graph.write_png(output_file)
        elif ext == ".svg":
            pydot_graph.write_svg(output_file)
        elif ext == ".pdf":
            pydot_graph.write_pdf(output_file)
        else:
            pydot_graph.write_png(output_file)
            
    except ImportError:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        
        plt.figure(figsize=(16, 12))
        pos = nx.spring_layout(G, k=2, iterations=50)
        
        nx.draw(G, pos, 
                with_labels=True,
                node_color='lightblue',
                node_size=2000,
                font_size=8,
                font_weight='bold',
                arrows=True,
                edge_color='gray',
                arrowsize=20)
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()
