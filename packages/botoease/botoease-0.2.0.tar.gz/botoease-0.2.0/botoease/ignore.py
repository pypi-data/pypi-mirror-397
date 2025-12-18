import os
import fnmatch

DEFAULT_IGNORE_FILE = ".botoeaseignore"


def load_ignore_patterns(base_path, ignore_file=DEFAULT_IGNORE_FILE, extra_patterns=None):
    patterns = set(extra_patterns or [])

    ignore_path = os.path.join(base_path, ignore_file)
    if os.path.exists(ignore_path):
        with open(ignore_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    patterns.add(line)

    return patterns


def is_ignored(path, patterns):
    """
    path must be POSIX-style relative path (a/b/c.txt)
    """
    for pattern in patterns:
        # Exact / wildcard match
        if fnmatch.fnmatch(path, pattern):
            return True

        # Directory-style ignore (e.g. __pycache__/)
        if pattern.endswith("/") and path.startswith(pattern):
            return True

    return False
