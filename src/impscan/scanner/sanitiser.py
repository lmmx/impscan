from pathlib import Path

__all__ = ["is_ignored_path"]

ignore_part_names = [".eggs", "*.egg-info"]


def is_ignored_path(path: Path):
    """
    Check each part of a path for matches against the list of filters
    given in `ignore_part_names`.
    """
    is_ignored = False
    for ignored_name in ignore_part_names:
        if ignored_name.startswith("*"):
            is_ignored = any(p.endswith(ignored_name.lstrip("*")) for p in path.parts)
        else:
            is_ignored = any(p == ignored_name for p in path.parts)
        if is_ignored:
            break
    return is_ignored
