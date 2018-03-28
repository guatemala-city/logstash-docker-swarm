from pathlib import Path
from re import match
from .constants import pipeline_config_path_workspace
import pytest

path_list = [pipeline_config_path_workspace]

@pytest.mark.parametrize("path", path_list, ids=["pipeline_config"])
def test_file_exist(path):
    file = Path(path)
    assert(file.is_file())

@pytest.fixture(params=path_list)
def open_file(request):
    with open(request.param,"r") as file:
        text = file.read()
    yield text

def test_null_file(open_file):
    # validate that the file is not empty
    assert(len(open_file) is not 0)

def test_all_parameters_injected(open_file):
    # validate that everything injected -> the pattern {{ foo }} not found..
    assert(match(r'{{.*}}',open_file) is None)
