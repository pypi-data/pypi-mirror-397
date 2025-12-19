"""CLI entrypoint for repomap."""

import argparse
import fnmatch
import os
import sys
from pathlib import Path

from grep_ast import filename_to_lang

from .core import RepoMap, find_src_files


def main():
    """Run repomap on the specified directories."""
    parser = argparse.ArgumentParser(
        description="Generate a tree-sitter based repository map",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  repomap ./src
  repomap ./src --exclude tests --exclude docs
  repomap ./src --language python
  repomap ./src -o map.md
  repomap ./src --graph graph.png
  repomap ./src --graph graph.svg --focus main
""",
    )
    parser.add_argument(
        "paths",
        nargs="+",
        help="Directories or files to analyze",
    )
    parser.add_argument(
        "--exclude", "-e",
        action="append",
        default=[],
        metavar="PATTERN",
        help="Exclude paths matching pattern (can be used multiple times). "
             "Patterns like 'tests', 'node_modules', '__pycache__'",
    )
    parser.add_argument(
        "--language", "-l",
        action="append",
        default=[],
        metavar="LANG",
        help="Only include files of specified language (can be used multiple times). "
             "Examples: python, javascript, typescript, java, go, rust",
    )
    parser.add_argument(
        "--tokens", "-t",
        type=int,
        default=4096,
        help="Maximum tokens for the repo map (default: 4096)",
    )
    parser.add_argument(
        "--output", "-o",
        metavar="FILE",
        help="Save repo map to a file instead of printing to stdout",
    )
    parser.add_argument(
        "--graph", "-g",
        metavar="FILE",
        help="Generate a call graph (.png, .svg, .pdf, .dot, .json)",
    )
    parser.add_argument(
        "--entry",
        metavar="FILE",
        help="Entry point file - only include files reachable from this file",
    )
    parser.add_argument(
        "--depth",
        type=int,
        metavar="N",
        help="Maximum depth to traverse from entry point (default: unlimited)",
    )
    parser.add_argument(
        "--min-refs",
        type=int,
        default=1,
        metavar="N",
        help="Only include symbols with at least N references (default: 1)",
    )
    parser.add_argument(
        "--focus", "-f",
        metavar="PATTERN",
        help="Focus the graph on files matching this pattern",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output",
    )
    
    args = parser.parse_args()
    
    # Collect all source files
    all_fnames = []
    for path in args.paths:
        if Path(path).is_dir():
            all_fnames += find_src_files(path)
        else:
            all_fnames.append(path)
    
    # Apply exclude patterns
    if args.exclude:
        filtered_fnames = []
        for fname in all_fnames:
            excluded = False
            for pattern in args.exclude:
                # Check if any part of the path matches the pattern
                if fnmatch.fnmatch(fname, f"*{pattern}*") or \
                   fnmatch.fnmatch(fname, f"*/{pattern}/*") or \
                   fnmatch.fnmatch(Path(fname).name, pattern):
                    excluded = True
                    break
            if not excluded:
                filtered_fnames.append(fname)
        all_fnames = filtered_fnames
    
    # Apply language filter
    if args.language:
        lang_set = set(lang.lower() for lang in args.language)
        filtered_fnames = []
        for fname in all_fnames:
            file_lang = filename_to_lang(fname)
            if file_lang and file_lang.lower() in lang_set:
                filtered_fnames.append(fname)
        all_fnames = filtered_fnames
    
    if not all_fnames:
        print("No files found matching the criteria.", file=sys.stderr)
        sys.exit(1)
    
    if args.verbose:
        print(f"Analyzing {len(all_fnames)} files...", file=sys.stderr)
    
    # Determine root directory
    root = os.path.commonpath([os.path.abspath(f) for f in all_fnames]) if all_fnames else "."
    if os.path.isfile(root):
        root = os.path.dirname(root)
    
    rm = RepoMap(root=root, map_tokens=args.tokens, verbose=args.verbose)
    
    # Filter files by entry point if specified (for both graph and repo map)
    if args.entry and not args.graph:
        from .graph import get_reachable_files
        filtered_fnames = get_reachable_files(
            rm, all_fnames, args.entry, args.depth, args.min_refs, args.verbose
        )
        if filtered_fnames is None:
            # Error already printed by get_reachable_files
            sys.exit(1)
        if filtered_fnames:
            all_fnames = filtered_fnames
            if args.verbose:
                print(f"Entry point filter: {len(all_fnames)} files reachable", file=sys.stderr)
    
    # Filter files by focus pattern (for repo map, already handled in graph)
    if args.focus and not args.graph:
        focus_pattern = args.focus.lower()
        filtered = [f for f in all_fnames if focus_pattern in f.lower()]
        if filtered:
            all_fnames = filtered
            if args.verbose:
                print(f"Focus filter: {len(all_fnames)} files match '{args.focus}'", file=sys.stderr)
        else:
            print(f"Warning: No files matching focus pattern '{args.focus}'", file=sys.stderr)
    
    # Generate call graph if requested
    if args.graph:
        from .graph import generate_call_graph
        generate_call_graph(
            rm, all_fnames, args.graph, 
            focus=args.focus,
            entry=args.entry,
            depth=args.depth,
            min_refs=args.min_refs,
            verbose=args.verbose
        )
        print(f"Call graph saved to: {args.graph}", file=sys.stderr)
        if not args.output:
            return  # Exit if only generating graph
    
    # Generate repo map
    repo_map = rm.get_repo_map(
        chat_files=[],
        other_files=all_fnames,
    )
    
    if repo_map:
        output_text = f"\n=== Repo Map ({len(repo_map)} chars) ===\n\n{repo_map}"
        
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(repo_map)
            print(f"Repo map saved to: {args.output}", file=sys.stderr)
        else:
            print(output_text)
    else:
        print("No repo map generated.", file=sys.stderr)


if __name__ == "__main__":
    main()
