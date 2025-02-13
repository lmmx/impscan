from pytest import fixture

from impscan.conda_meta.formats import CondaArchive

EXAMPLE_CONDA_URL = (
    "https://repo.anaconda.com/pkgs/main/linux-64/tqdm-4.19.5-py27_0.conda"
)


@fixture(scope="session")
def example_conda_archive():
    return CondaArchive(source_url=EXAMPLE_CONDA_URL, defer_pull=True)


def test_conda_archive(example_conda_archive):
    example_conda_archive
