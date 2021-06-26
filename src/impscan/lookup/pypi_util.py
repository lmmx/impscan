__all__ = ["pypi_search_reqs"]

def pypi_search_reqs(requirements) -> set:
    pypi_reqs = set()
    for req in requirements.registered_imports:
        pass
    return pypi_reqs
