# type: ignore
__all__ = ["conda_search_reqs"]


def conda_search_reqs(requirements) -> set:
    conda_reqs = set()

    for req in requirements.registered_imports:
        # look up req (imported module name) in database compiled in advance
        pass
    return conda_reqs
