"""Core RepoMap class for generating repository maps."""

import os
import time
from pathlib import Path

from .cache import TagsCache
from .ranking import get_ranked_tags
from .tree import to_tree


# List of important root files to prioritize
ROOT_IMPORTANT_FILES = [
    "README", "README.md", "README.txt", "README.rst",
    "requirements.txt", "pyproject.toml", "setup.py", "setup.cfg",
    "package.json", "Cargo.toml", "go.mod", "Gemfile",
    ".gitignore",
]

NORMALIZED_ROOT_IMPORTANT_FILES = set(os.path.normpath(path) for path in ROOT_IMPORTANT_FILES)

# Default directories to exclude when scanning for source files
DEFAULT_EXCLUDES = {
    '.venv', 'venv', '.env', 'env',
    'node_modules',
    '__pycache__', '.pytest_cache', '.mypy_cache',
    '.git', '.hg', '.svn',
    'dist', 'build', '.eggs', '*.egg-info',
    '.tox', '.nox',
    'target',  # Rust
    'vendor',  # Go
    '.idea', '.vscode',
    'tests', 'test', 'testing',  # Test directories
}

def is_important(file_path):
    """Check if a file is commonly important in codebases."""
    normalized_path = os.path.normpath(file_path)
    return normalized_path in NORMALIZED_ROOT_IMPORTANT_FILES


def filter_important_files(file_paths):
    """Filter a list of file paths to return only important ones."""
    return list(filter(is_important, file_paths))


class RepoMap:
    """
    Generate a markdown-formatted map of a code repository.
    
    Uses tree-sitter to parse source files, extracts definitions and references,
    builds a call graph, and uses PageRank to rank the most relevant code.
    """
    
    CACHE_VERSION = 4
    
    def __init__(
        self,
        root=None,
        map_tokens=1024,
        verbose=False,
        refresh="auto",
    ):
        """Initialize RepoMap."""
        self.verbose = verbose
        self.refresh = refresh
        
        if not root:
            root = os.getcwd()
        self.root = root
        
        self.cache = TagsCache(root, cache_version=self.CACHE_VERSION, verbose=verbose)
        
        self.max_map_tokens = map_tokens
        
        self.tree_cache = {}
        self.tree_context_cache = {}
        self.map_cache = {}
        self.map_processing_time = 0
        self.last_map = None
    
    def token_count(self, text):
        """Estimate token count (simple character-based estimation)."""
        return len(text) / 4
    
    def get_repo_map(
        self,
        chat_files,
        other_files,
        mentioned_fnames=None,
        mentioned_idents=None,
        force_refresh=False,
    ):
        """Generate a repo map for the given files."""
        if self.max_map_tokens <= 0:
            return
        if not other_files:
            return
        if not mentioned_fnames:
            mentioned_fnames = set()
        if not mentioned_idents:
            mentioned_idents = set()
        
        max_map_tokens = self.max_map_tokens
        
        try:
            files_listing = self.get_ranked_tags_map(
                chat_files,
                other_files,
                max_map_tokens,
                mentioned_fnames,
                mentioned_idents,
                force_refresh,
            )
        except RecursionError:
            print("Disabling repo map, git repo too large?")
            self.max_map_tokens = 0
            return
        
        if not files_listing:
            return
        
        if self.verbose:
            num_tokens = self.token_count(files_listing)
            print(f"Repo-map: {num_tokens / 1024:.1f} k-tokens")
        
        return files_listing
    
    def get_rel_fname(self, fname):
        """Get relative filename from absolute path."""
        try:
            return os.path.relpath(fname, self.root)
        except ValueError:
            return fname
    
    def get_abs_fname(self, rel_fname):
        """Get absolute filename from relative path."""
        return os.path.join(self.root, rel_fname)
    
    def get_mtime(self, fname):
        """Get file modification time."""
        try:
            return os.path.getmtime(fname)
        except FileNotFoundError:
            return None
    
    def read_text(self, fname):
        """Read file contents."""
        try:
            with open(fname, "r", encoding="utf-8", errors="replace") as f:
                return f.read()
        except (OSError, FileNotFoundError):
            return None
    
    def get_ranked_tags_map(
        self,
        chat_fnames,
        other_fnames=None,
        max_map_tokens=None,
        mentioned_fnames=None,
        mentioned_idents=None,
        force_refresh=False,
    ):
        """Generate ranked tags map with caching."""
        cache_key = [
            tuple(sorted(chat_fnames)) if chat_fnames else None,
            tuple(sorted(other_fnames)) if other_fnames else None,
            max_map_tokens,
        ]
        
        if self.refresh == "auto":
            cache_key += [
                tuple(sorted(mentioned_fnames)) if mentioned_fnames else None,
                tuple(sorted(mentioned_idents)) if mentioned_idents else None,
            ]
        cache_key = tuple(cache_key)
        
        use_cache = False
        if not force_refresh:
            if self.refresh == "manual" and self.last_map:
                return self.last_map
            
            if self.refresh == "always":
                use_cache = False
            elif self.refresh == "files":
                use_cache = True
            elif self.refresh == "auto":
                use_cache = self.map_processing_time > 1.0
            
            if use_cache and cache_key in self.map_cache:
                return self.map_cache[cache_key]
        
        start_time = time.time()
        result = self._get_ranked_tags_map_uncached(
            chat_fnames, other_fnames, max_map_tokens, mentioned_fnames, mentioned_idents
        )
        end_time = time.time()
        self.map_processing_time = end_time - start_time
        
        self.map_cache[cache_key] = result
        self.last_map = result
        
        return result
    
    def _get_ranked_tags_map_uncached(
        self,
        chat_fnames,
        other_fnames=None,
        max_map_tokens=None,
        mentioned_fnames=None,
        mentioned_idents=None,
    ):
        """Generate ranked tags map without caching."""
        if not other_fnames:
            other_fnames = list()
        if not max_map_tokens:
            max_map_tokens = self.max_map_tokens
        if not mentioned_fnames:
            mentioned_fnames = set()
        if not mentioned_idents:
            mentioned_idents = set()
        
        ranked_tags = get_ranked_tags(
            cache=self.cache,
            read_text_fn=self.read_text,
            get_rel_fname_fn=self.get_rel_fname,
            chat_fnames=chat_fnames,
            other_fnames=other_fnames,
            mentioned_fnames=mentioned_fnames,
            mentioned_idents=mentioned_idents,
            verbose=self.verbose,
        )
        
        other_rel_fnames = sorted(set(self.get_rel_fname(fname) for fname in other_fnames))
        special_fnames = filter_important_files(other_rel_fnames)
        ranked_tags_fnames = set(tag[0] for tag in ranked_tags)
        special_fnames = [fn for fn in special_fnames if fn not in ranked_tags_fnames]
        special_fnames = [(fn,) for fn in special_fnames]
        
        ranked_tags = special_fnames + ranked_tags
        
        num_tags = len(ranked_tags)
        lower_bound = 0
        upper_bound = num_tags
        best_tree = None
        best_tree_tokens = 0
        
        chat_rel_fnames = set(self.get_rel_fname(fname) for fname in chat_fnames)
        
        self.tree_cache = dict()
        
        middle = min(int(max_map_tokens // 25), num_tags)
        while lower_bound <= upper_bound:
            tree = to_tree(
                ranked_tags[:middle],
                chat_rel_fnames,
                self.read_text,
                self.tree_cache,
                self.tree_context_cache,
                self.get_mtime,
                self.get_abs_fname,
            )
            num_tokens = self.token_count(tree)
            
            pct_err = abs(num_tokens - max_map_tokens) / max_map_tokens if max_map_tokens else 0
            ok_err = 0.15
            if (num_tokens <= max_map_tokens and num_tokens > best_tree_tokens) or pct_err < ok_err:
                best_tree = tree
                best_tree_tokens = num_tokens
                
                if pct_err < ok_err:
                    break
            
            if num_tokens < max_map_tokens:
                lower_bound = middle + 1
            else:
                upper_bound = middle - 1
            
            middle = int((lower_bound + upper_bound) // 2)
        
        return best_tree


def find_src_files(directory, exclude_patterns=None):
    """Find all source files in a directory, excluding common non-source dirs."""
    if not os.path.isdir(directory):
        return [directory]
    
    excludes = DEFAULT_EXCLUDES.copy()
    if exclude_patterns:
        excludes.update(exclude_patterns)
    
    src_files = []
    for root, dirs, files in os.walk(directory):
        # Filter out excluded directories in-place to prevent os.walk from descending
        dirs[:] = [d for d in dirs if d not in excludes and not d.endswith('.egg-info')]
        
        for file in files:
            src_files.append(os.path.join(root, file))
    return src_files
