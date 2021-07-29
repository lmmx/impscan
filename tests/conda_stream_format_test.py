from pytest import fixture, mark, raises

from impscan.conda_meta.streaming_formats import CondaArchiveStream

EXAMPLE_CONDA_URL = (
    "https://repo.anaconda.com/pkgs/main/linux-64/tqdm-4.19.5-py27_0.conda"
)


@fixture(scope="session")
def example_conda_archive():
    return CondaArchiveStream(source_url=EXAMPLE_CONDA_URL, defer_pull=True)


def test_conda_archive(example_conda_archive):
    example_conda_archive
