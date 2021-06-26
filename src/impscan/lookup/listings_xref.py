from .conda_util import conda_search_reqs
from .pypi_util import pypi_search_reqs

__all__ = ["lookup_requirements"]


def lookup_requirements(requirements):
    conda_reqs = conda_search_reqs(requirements)
    pypi_reqs = pypi_search_reqs(requirements)
    return conda_reqs, pypi_reqs
