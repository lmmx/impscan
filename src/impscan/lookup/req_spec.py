# Python 3.7+ enable list[str] see https://stackoverflow.com/a/65777001/
from __future__ import annotations

__all__ = ["ReqSpec", "CondaReqSpec", "PyPIReqSpec"]


class Repository(Enum):
    Conda = "conda"
    PyPI = "pypi"


class ReqSpec:
    def __init__(
        self, package: str, repository: Repository, channel: list, constraints: list
    ):
        self.package = package
        self.repository = repository
        self.channel = channel
        self.constraints = constraints


class CondaReqSpec(ReqSpec):
    def __init__(self, package: str, channel: list[str], constraints: list):
        super().__init__(
            package=package,
            repository=Repository.Conda,
            channel=channel,
            constraints=constraints,
        )


class PyPIReqSpec(ReqSpec):
    def __init__(self, package: str, channel: list[str], constraints: list):
        super().__init__(
            package=package,
            repository=Repository.PyPI,
            channel=None,
            constraints=constraints,
        )
