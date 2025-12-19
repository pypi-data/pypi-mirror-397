from pathlib import Path
import sys, re, os 

# Default configuration lists - accessible for manual configuration and extended via environment variables
DEFAULT_ADD_DIR_NAMES = ['src', 'app', 'main', 'test', 'tests', 'mcp']
DEFAULT_SKIP_DIR_PATTERNS = ['setup', 'venv.*', '.*\.egg.*', 'old.*', 'bkup|backup']
shortest_path = []  # will be set later if autorun occurs

# Environment variables: FUPI_ADD_DIR_NAMES and FUPI_SKIP_DIR_PATTERNS can extend the defaults
# when creating a ManualFupi instance. This allows configuration without code changes.


class ManualFupi:
    """Manual configuration class for fupi path management.
    
    Usage:
        mf = ManualFupi()
        mf.add_dir_names = ['src', 'test']
        mf.skip_dir_patterns = ['venv*', 'build']
        
        # Preview paths before running
        paths = mf.get_paths()
        print(f"Will add {len(paths)} paths to sys.path")
        
        # Execute configuration
        mf.run()
        
        # Or in one call with parameters:
        mf.run(add_dir_names=['src'], skip_dir_patterns=['venv*'])
    """
    add_dir_names: list = []
    skip_dir_patterns: list = []
    sys_path_history: list = []
    
    def __init__(self, add_dir_names=[], skip_dir_patterns=[], autorun: bool = False):
        """Initialize ManualFupi with default configuration.
        
        Configuration can be extended via environment variables:
        - FUPI_ADD_DIR_NAMES: Comma-separated directory names to append to defaults
        - FUPI_SKIP_DIR_PATTERNS: Comma-separated patterns to append to defaults
        
        Environment variables support optional wrapping with quotes/brackets:
        e.g., FUPI_ADD_DIR_NAMES="src,test" or FUPI_ADD_DIR_NAMES=['src','test']
        """
        # Start with copies of defaults (ensures instance independence)
        self.add_dir_names     = add_dir_names     if add_dir_names     else DEFAULT_ADD_DIR_NAMES.copy()
        self.skip_dir_patterns = skip_dir_patterns if skip_dir_patterns else DEFAULT_SKIP_DIR_PATTERNS.copy()

        def unwrap(env_var: str) -> str:
            """Remove wrapping quotes and brackets from environment variable value."""
            fw = ['"', "'", '[', '(', '{']
            bw = ['"', "'", ']', ')', '}']
            val = env_var.strip()
            if val[-1:]=='/': val=val[:-1] # remove trailing slashes
            # Unwrap outer layer while both sides match
            while val and val[:1] in fw and val[-1:] in bw:
                val = val[1:-1].strip()
            return val

        # Extend defaults with environment variables if set
        env_add_dirs_str = os.getenv('FUPI_ADD_DIR_NAMES', '').strip()
        env_skip_dirs_str = os.getenv('FUPI_SKIP_DIR_PATTERNS', '').strip()
        
        if env_add_dirs_str:
            # Unwrap the entire value first, then split on commas and unwrap each
            unwrapped = unwrap(env_add_dirs_str)
            env_add_dirs = [unwrap(v.strip()) for v in unwrapped.split(',') if v.strip()]
            self.add_dir_names.extend(env_add_dirs)
        
        if env_skip_dirs_str:
            # Unwrap the entire value first, then split on commas and unwrap each
            unwrapped = unwrap(env_skip_dirs_str)
            env_skip_dirs = [unwrap(v.strip()) for v in unwrapped.split(',') if v.strip()]
            self.skip_dir_patterns.extend(env_skip_dirs)
        
        if autorun: self.run() 
        else: self.sys_path_history = self.__inspthhist__(sys.path.copy())  
        

    def shortest_path(self, paths:list = None) -> Path:
        """Returns the shortest path found in the current sys.path.
        If there are no candidate paths, set to None. Tie-break 
        lexicographically on path string for deterministic selection.

        Args:
            paths: Optional list of paths to evaluate. If None, uses path list ADDED at last .run() executed (a subset of sys.path).

        Returns:
            list: The shortest Path object found, by parts count with lexicographic tie-breaker.
        """
        if not paths and not self.sys_path_history: return []
        if not paths: 
            curpaths = [Path(p) for p in self.sys_path_history[-1] # current path list
                     if p not in self.sys_path_history[0]]  
        else: 
            curpaths = [Path(p) for p in paths]       # not in original path list
        shortest_path = min(curpaths, key=lambda p: (len(p.parts), p.as_posix())) if curpaths else None
        return shortest_path


    def get_paths(self, add_dir_names=None, skip_dir_patterns=None) -> list:
        """Get the list of paths that will be added to sys.path.
        
        This allows previewing what paths will be added without modifying sys.path.
        
        Args:
            add_dir_names: List of dir names to add. If None, uses self.add_dir_names
            skip_dir_patterns: List of patterns to skip. If None, uses self.skip_dir_patterns
            
        Returns:
            list: Paths that would be added to sys.path
        """
        # Use provided params or fall back to instance variables
        add_dirs = list(set(add_dir_names if add_dir_names is not None else self.add_dir_names))
        if not add_dirs: return [] 
        skip_dirs = list(set(skip_dir_patterns if skip_dir_patterns is not None else self.skip_dir_patterns))
    
        # make sure there are no residual quotes around anything:
        quotes = ['"',"'"]
        add_dirs = [d[1:-1] if d[:1] in quotes and d[-1:] in quotes else d for d in add_dirs]
        skip_dirs = [d[1:-1] if d[:1] in quotes and d[-1:] in quotes else d for d in skip_dirs]
        
        skip_dirs.extend([r'\..*'])  # always skip paths that begin with a period (e.g., `.git`)
        skip_dirs.extend([r'_.*'])  # always skip paths that begin with an underscore (e.g., `__pycache__`)

        # ADD all paths that contain one of our add_dirs (as direct matched strings)
        allpaths = []
        for dirname in add_dirs: 
            tdir = Path.cwd().resolve()
            found_paths = [pth for pth in tdir.rglob('*/') if dirname in pth.parts]
            allpaths.extend(found_paths)

        # REMOVE any paths that matches one of our skip_dirs patterns (as regex patterns)
        # Use a list comprehension (safe vs mutating the list while iterating).
        skip_dirs_re = [re.compile(skipre) for skipre in skip_dirs]
        allpaths = [pth for pth in allpaths
                    if not any(s.match(part) for part in pth.parts[1:] for s in skip_dirs_re)]
                     
        return allpaths
    

    def run(self, add_dir_names=None, skip_dir_patterns=None) -> list:
        """Execute path configuration with given or preset directories.
        
        This gets the qualifying paths and adds them to sys.path.
        
        Args:
            add_dir_names: List of dir names to add. If None, uses self.add_dir_names
            skip_dir_patterns: List of patterns to skip. If None, uses self.skip_dir_patterns
            
        Returns:
            list: Paths that were added to sys.path
        """
        # add current (soon to be history) state to our backup history, if not already present
        self.__inspthhist__(sys.path.copy())
        
        # Use provided params or fall back to instance variables
        if add_dir_names is not None:
            self.add_dir_names = list(add_dir_names)
        if skip_dir_patterns is not None:
            self.skip_dir_patterns = list(skip_dir_patterns)
        
        # Get the paths to add
        allpaths = self.get_paths(self.add_dir_names, self.skip_dir_patterns)
        
        # add allpaths to the sys.path for the current process
        sys.path.extend([str(pth) for pth in allpaths if str(pth) not in sys.path])

        # record the new sys.path state in our history
        self.__inspthhist__(sys.path.copy())

        global shortest_path
        shortest_path = self.shortest_path()

        return allpaths


    def __inspthhist__(self, paths: list) -> None:
        """Ensure `paths` appears in the global `sys_path_history` exactly once.

        Behavior:
        - Normalize the supplied `paths` to a sorted list of strings.
        - Normalize (sort) each existing entry in `sys_path_history` for comparison.
        - If a matching entry already exists, do nothing.
        - Otherwise append the normalized `paths` to `sys_path_history`.

        This helper is defensive about input types: Path objects and strings are
        both accepted and compared as their string form.
        """
        # Operate on the instance history (`self._sys_path_history`). Normalize
        # the incoming list to a sorted list of strings for deterministic
        # comparison.
        target = sorted([str(p) for p in paths])
        if not self.sys_path_history: self.sys_path_history = []

        # Normalize each existing history entry (in-place) and check for equality
        for idx, hist in enumerate(self.sys_path_history):
            normalized = sorted([str(p) for p in hist])
            self.sys_path_history[idx] = normalized
            if normalized == target:
                return

        # No match found; append the normalized target
        self.sys_path_history.append(target)

