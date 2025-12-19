"""PageRank-based ranking of code definitions and references."""

import math
import os
from collections import Counter, defaultdict
from pathlib import Path

import networkx as nx
from tqdm import tqdm

from .tags import Tag, get_tags_raw


def get_ranked_tags(
    cache,
    read_text_fn,
    get_rel_fname_fn,
    chat_fnames,
    other_fnames,
    mentioned_fnames=None,
    mentioned_idents=None,
    progress=None,
    verbose=False,
):
    """
    Build a graph of definitions and references, then rank using PageRank.
    
    Args:
        cache: TagsCache instance for caching parsed tags
        read_text_fn: Function to read file contents
        get_rel_fname_fn: Function to convert absolute path to relative
        chat_fnames: Files currently in the chat (higher personalization)
        other_fnames: Other files in the repo
        mentioned_fnames: File names mentioned in conversation
        mentioned_idents: Identifiers mentioned in conversation
        progress: Optional progress callback
        verbose: Enable verbose output
        
    Returns:
        List of ranked Tag tuples
    """
    if not mentioned_fnames:
        mentioned_fnames = set()
    if not mentioned_idents:
        mentioned_idents = set()
    
    defines = defaultdict(set)
    references = defaultdict(list)
    definitions = defaultdict(set)
    personalization = dict()
    
    fnames = set(chat_fnames).union(set(other_fnames))
    chat_rel_fnames = set()
    fnames = sorted(fnames)
    
    # Default personalization for unspecified files is 1/num_nodes
    personalize = 100 / len(fnames) if fnames else 1
    
    cache_size = len(cache)
    if len(fnames) - cache_size > 100:
        print("Initial repo scan can be slow in larger repos, but only happens once.")
        fnames = tqdm(fnames, desc="Scanning repo")
        showing_bar = True
    else:
        showing_bar = False
    
    warned_files = set()
    
    for fname in fnames:
        if verbose:
            print(f"Processing {fname}")
        if progress and not showing_bar:
            progress(f"Updating repo map: {fname}")
        
        try:
            file_ok = Path(fname).is_file()
        except OSError:
            file_ok = False
        
        if not file_ok:
            if fname not in warned_files:
                print(f"Repo-map can't include {fname}")
                warned_files.add(fname)
            continue
        
        rel_fname = get_rel_fname_fn(fname)
        current_pers = 0.0
        
        if fname in chat_fnames:
            current_pers += personalize
            chat_rel_fnames.add(rel_fname)
        
        if rel_fname in mentioned_fnames:
            current_pers = max(current_pers, personalize)
        
        # Check path components against mentioned_idents
        path_obj = Path(rel_fname)
        path_components = set(path_obj.parts)
        basename_with_ext = path_obj.name
        basename_without_ext, _ = os.path.splitext(basename_with_ext)
        components_to_check = path_components.union({basename_with_ext, basename_without_ext})
        
        matched_idents = components_to_check.intersection(mentioned_idents)
        if matched_idents:
            current_pers += personalize
        
        if current_pers > 0:
            personalization[rel_fname] = current_pers
        
        # Get tags with caching
        tags = _get_tags_cached(cache, fname, rel_fname, read_text_fn)
        if tags is None:
            continue
        
        for tag in tags:
            if tag.kind == "def":
                defines[tag.name].add(rel_fname)
                key = (rel_fname, tag.name)
                definitions[key].add(tag)
            elif tag.kind == "ref":
                references[tag.name].append(rel_fname)
    
    if not references:
        references = dict((k, list(v)) for k, v in defines.items())
    
    idents = set(defines.keys()).intersection(set(references.keys()))
    
    G = nx.MultiDiGraph()
    
    # Add a small self-edge for every definition that has no references
    for ident in defines.keys():
        if ident in references:
            continue
        for definer in defines[ident]:
            G.add_edge(definer, definer, weight=0.1, ident=ident)
    
    for ident in idents:
        if progress:
            progress(f"Updating repo map: {ident}")
        
        definers = defines[ident]
        mul = 1.0
        
        is_snake = ("_" in ident) and any(c.isalpha() for c in ident)
        is_kebab = ("-" in ident) and any(c.isalpha() for c in ident)
        is_camel = any(c.isupper() for c in ident) and any(c.islower() for c in ident)
        
        if ident in mentioned_idents:
            mul *= 10
        if (is_snake or is_kebab or is_camel) and len(ident) >= 8:
            mul *= 10
        if ident.startswith("_"):
            mul *= 0.1
        if len(defines[ident]) > 5:
            mul *= 0.1
        
        for referencer, num_refs in Counter(references[ident]).items():
            for definer in definers:
                use_mul = mul
                if referencer in chat_rel_fnames:
                    use_mul *= 50
                
                # scale down so high freq (low value) mentions don't dominate
                num_refs = math.sqrt(num_refs)
                G.add_edge(referencer, definer, weight=use_mul * num_refs, ident=ident)
    
    if personalization:
        pers_args = dict(personalization=personalization, dangling=personalization)
    else:
        pers_args = dict()
    
    try:
        ranked = nx.pagerank(G, weight="weight", **pers_args)
    except ZeroDivisionError:
        try:
            ranked = nx.pagerank(G, weight="weight")
        except ZeroDivisionError:
            return []
    
    # distribute the rank from each source node, across all of its out edges
    ranked_definitions = defaultdict(float)
    for src in G.nodes:
        if progress:
            progress(f"Updating repo map: {src}")
        
        src_rank = ranked[src]
        total_weight = sum(data["weight"] for _src, _dst, data in G.out_edges(src, data=True))
        
        for _src, dst, data in G.out_edges(src, data=True):
            data["rank"] = src_rank * data["weight"] / total_weight
            ident = data["ident"]
            ranked_definitions[(dst, ident)] += data["rank"]
    
    ranked_tags = []
    ranked_definitions = sorted(
        ranked_definitions.items(), reverse=True, key=lambda x: (x[1], x[0])
    )
    
    for (fname, ident), rank in ranked_definitions:
        if fname in chat_rel_fnames:
            continue
        ranked_tags += list(definitions.get((fname, ident), []))
    
    rel_other_fnames_without_tags = set(get_rel_fname_fn(fname) for fname in other_fnames)
    
    fnames_already_included = set(rt[0] for rt in ranked_tags)
    
    top_rank = sorted([(rank, node) for (node, rank) in ranked.items()], reverse=True)
    for rank, fname in top_rank:
        if fname in rel_other_fnames_without_tags:
            rel_other_fnames_without_tags.remove(fname)
        if fname not in fnames_already_included:
            ranked_tags.append((fname,))
    
    for fname in rel_other_fnames_without_tags:
        ranked_tags.append((fname,))
    
    return ranked_tags


def _get_tags_cached(cache, fname, rel_fname, read_text_fn):
    """Get tags for a file, using cache if available."""
    try:
        file_mtime = os.path.getmtime(fname)
    except FileNotFoundError:
        return []
    
    cache_key = fname
    val = cache.get(cache_key)
    
    if val is not None and val.get("mtime") == file_mtime:
        return val["data"]
    
    # Cache miss - parse the file
    code = read_text_fn(fname)
    if not code:
        return []
    
    data = list(get_tags_raw(fname, rel_fname, code))
    
    # Update the cache
    cache.set(cache_key, {"mtime": file_mtime, "data": data})
    
    return data
